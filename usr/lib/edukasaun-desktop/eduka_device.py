#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""What kind of computer Eduka-Desktop runs on (0.11 RC3).

Eduka-Desktop sets itself up a little differently on a laptop, a desktop
computer, a tablet or a virtual machine:

* the kind of computer: the DMI chassis type of the firmware, else a
  battery or a lid switch (laptop); a touch screen with a tablet-mode switch
  makes a convertible; systemd-detect-virt finds virtual machines;
* the keyboards: built in (i8042, I2C), USB or Bluetooth, from
  /proc/bus/input/devices. Num Lock is on at login on desktop computers and
  off on laptops (many laptops type numbers instead of letters with it), on
  again when a USB or Bluetooth keyboard is plugged in;
* the screens: size and sharpness (xrandr), for the display scale
  Eduka-Settings → Display recommends (75 to 200 %).

Only files of /sys and /proc are read and xrandr is asked; nothing here
needs administrator rights.
"""
import json, math, os, re, shutil, subprocess
from pathlib import Path

SYS = Path('/sys')
PROC = Path('/proc')

# DMI chassis types (SMBIOS 3.x, section 7.4.1).
CHASSIS = {3: 'desktop', 4: 'desktop', 5: 'desktop', 6: 'desktop', 7: 'desktop', 15: 'desktop', 16: 'desktop',
           24: 'desktop', 34: 'desktop', 35: 'desktop', 36: 'desktop', 13: 'all-in-one',
           8: 'laptop', 9: 'laptop', 10: 'laptop', 14: 'laptop', 11: 'tablet', 30: 'tablet',
           31: 'convertible', 32: 'detachable', 17: 'server', 23: 'server', 25: 'server', 28: 'server', 29: 'server'}
KIND_NAMES = {'desktop': 'Desktop computer', 'laptop': 'Laptop', 'tablet': 'Tablet',
              'convertible': 'Convertible laptop (turns into a tablet)', 'detachable': 'Tablet with a detachable keyboard',
              'all-in-one': 'All-in-one computer', 'server': 'Server', 'vm': 'Virtual machine'}
KIND_ICONS = {'desktop': 'computer', 'laptop': 'computer-laptop', 'tablet': 'tablet', 'convertible': 'computer-laptop',
              'detachable': 'tablet', 'all-in-one': 'video-display', 'server': 'network-server', 'vm': 'computer'}
PORTABLE = ('laptop', 'tablet', 'convertible', 'detachable')

BUS = {0x03: 'usb', 0x05: 'bluetooth', 0x11: 'built-in', 0x18: 'built-in', 0x19: 'built-in', 0x1c: 'built-in'}
NOT_KEYBOARD = re.compile(r'power button|sleep button|lid switch|video bus|consumer control|system control|'
                          r'wmi hotkeys|hid events|extra buttons|pc speaker|hdmi|headphone|mic|virtual|uinput|'
                          r'xtest|ydotool|xdotool|webcam|camera|tablet mode|accel|intel hid|asus wmi|dell wmi|'
                          r'hp wmi|ideapad|thinkpad extra', re.I)
VM_NAMES = re.compile(r'qemu|kvm|virtualbox|vmware|bochs|hyper-v|virtual machine|xen|parallels|bhyve', re.I)

SCALES = (0.75, 1.0, 1.25, 1.5, 1.75, 2.0)


def _read(path):
    try:
        return Path(path).read_text(encoding='utf-8', errors='ignore').strip()
    except OSError:
        return ''


def dmi(key):
    return _read(SYS/'class'/'dmi'/'id'/key)


def chassis_type():
    value = dmi('chassis_type')
    return int(value) if value.isdigit() else 0


def virtual_machine():
    """The name of the virtual machine ('' on real hardware)."""
    if shutil.which('systemd-detect-virt'):
        try:
            out = subprocess.run(['systemd-detect-virt', '--vm'], capture_output=True, text=True, timeout=2).stdout.strip()
            if out and out != 'none':
                return out
            if out == 'none':
                return ''
        except (OSError, subprocess.SubprocessError):
            pass
    text = ' '.join((dmi('sys_vendor'), dmi('product_name'), dmi('board_vendor')))
    m = VM_NAMES.search(text)
    return m.group(0) if m else ''


def batteries():
    """Batteries that power the computer (not those of a mouse or game pad)."""
    out = []
    for b in sorted((SYS/'class'/'power_supply').glob('*')):
        if _read(b/'type') == 'Battery' and _read(b/'scope').lower() != 'device':
            out.append(b.name)
    return out


def _bits(hexwords):
    """Bitmap of /proc/bus/input/devices (hex words, highest first) → int."""
    value = 0
    for word in hexwords.split():
        value = (value << 64) | int(word, 16)
    return value


def input_devices():
    """[{name, bus, phys, handlers, ev, key, abs, prop, sw}] from the kernel."""
    devices, cur = [], {}
    try:
        text = (PROC/'bus'/'input'/'devices').read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return []
    for line in text.splitlines() + ['']:
        if not line.strip():
            if cur:
                devices.append(cur)
            cur = {}
            continue
        kind, _sep, rest = line.partition(': ')
        if kind == 'I':
            m = re.search(r'Bus=([0-9a-fA-F]+)', rest)
            cur['bus'] = int(m.group(1), 16) if m else 0
        elif kind == 'N':
            cur['name'] = rest.split('=', 1)[1].strip().strip('"') if '=' in rest else rest
        elif kind == 'P':
            cur['phys'] = rest.split('=', 1)[1].strip() if '=' in rest else ''
        elif kind == 'H':
            cur['handlers'] = rest.split('=', 1)[1].split() if '=' in rest else []
        elif kind == 'B' and '=' in rest:
            name, value = rest.split('=', 1)
            try:
                cur[name.strip().lower()] = _bits(value)
            except ValueError:
                pass
    return devices


KEY_Q, KEY_A, KEY_Z, KEY_SPACE = 16, 30, 44, 57
BTN_TOOL_FINGER, BTN_TOUCH = 0x145, 0x14a
ABS_MT_POSITION_X = 0x35
INPUT_PROP_POINTER, INPUT_PROP_DIRECT, INPUT_PROP_BUTTONPAD = 0, 1, 2
SW_LID, SW_TABLET_MODE = 0, 1


def keyboards(devices=None):
    """[{name, connection}] of the real keyboards (with letter keys)."""
    out = []
    for d in devices if devices is not None else input_devices():
        key = d.get('key', 0); name = d.get('name', '')
        if 'kbd' not in d.get('handlers', []) or NOT_KEYBOARD.search(name):
            continue
        if not all(key >> k & 1 for k in (KEY_Q, KEY_A, KEY_Z, KEY_SPACE)):
            continue
        out.append({'name': name, 'connection': BUS.get(d.get('bus', 0), 'other')})
    return out


def _has_prop(d, bit):
    return bool(d.get('prop', 0) >> bit & 1)


def touchscreens(devices=None):
    return [d.get('name', '') for d in (devices if devices is not None else input_devices())
            if _has_prop(d, INPUT_PROP_DIRECT) and d.get('abs', 0) and not re.search(r'pen|stylus', d.get('name', ''), re.I)]


def touchpads(devices=None):
    out = []
    for d in devices if devices is not None else input_devices():
        name = d.get('name', '')
        pad = (_has_prop(d, INPUT_PROP_POINTER) or _has_prop(d, INPUT_PROP_BUTTONPAD)) and d.get('key', 0) >> BTN_TOOL_FINGER & 1
        if pad or re.search(r'touch\s*pad|trackpad|glidepoint', name, re.I):
            out.append(name)
    return out


def switches(devices=None):
    sw = 0
    for d in devices if devices is not None else input_devices():
        sw |= d.get('sw', 0)
    return {'lid': bool(sw >> SW_LID & 1), 'tablet': bool(sw >> SW_TABLET_MODE & 1)}


def kind(devices=None):
    """desktop, laptop, tablet, convertible, detachable, all-in-one, server or vm."""
    if virtual_machine():
        return 'vm'
    devices = devices if devices is not None else input_devices()
    k = CHASSIS.get(chassis_type(), '')
    sw = switches(devices)
    if not k:
        k = 'laptop' if batteries() or sw['lid'] else 'desktop'
    if k == 'laptop' and sw['tablet'] and touchscreens(devices):
        k = 'convertible'
    return k


def is_portable():
    return kind() in PORTABLE


# ---------------------------------------------------------------- screens
def screens():
    """[{name, width, height, mm_width, mm_height, primary, built_in}] of the
    connected screens (xrandr; [] without X)."""
    if not shutil.which('xrandr') or not os.environ.get('DISPLAY'):
        return []
    try:
        out = subprocess.run(['xrandr', '--query'], capture_output=True, text=True, timeout=3).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    found = []
    for line in out.splitlines():
        m = re.match(r'^(\S+)\s+connected(\s+primary)?\s+(\d+)x(\d+)\+\d+\+\d+.*?(?:(\d+)mm x (\d+)mm)?\s*$', line)
        if m:
            found.append({'name': m.group(1), 'primary': bool(m.group(2)), 'width': int(m.group(3)), 'height': int(m.group(4)),
                          'mm_width': int(m.group(5) or 0), 'mm_height': int(m.group(6) or 0),
                          'built_in': bool(re.match(r'^(eDP|LVDS|DSI)', m.group(1), re.I))})
    return found


def screen_facts(s):
    """(inches, dpi) of a screen, or (0, 0) when its size is not believable
    (virtual machines and many projectors report none or a made-up one)."""
    mw, mh = s.get('mm_width', 0), s.get('mm_height', 0)
    if mw < 120 or mh < 70:
        return 0.0, 0.0
    inches = math.hypot(mw, mh) / 25.4
    px_ratio = s['width'] / max(1, s['height']); mm_ratio = mw / max(1, mh)
    if not 7 <= inches <= 60 or abs(px_ratio - mm_ratio) / px_ratio > 0.12:
        return 0.0, 0.0
    return round(inches, 1), round(s['width'] / (mw / 25.4))


def main_screen(found=None):
    found = screens() if found is None else found
    for pick in (lambda s: s['built_in'], lambda s: s['primary'], lambda s: True):
        for s in found:
            if pick(s):
                return s
    return None


def recommended_scale(found=None):
    """The scale that makes things as big as on a 96 DPI screen, never
    leaving less than 1280 x 720 pixels of room (small school laptops with
    1366 x 768 stay at 100 %)."""
    s = main_screen(found)
    if not s:
        return 1.0
    _inches, dpi = screen_facts(s)
    if not dpi:
        return 1.0
    scale = 1.0 if dpi < 120 else 1.25 if dpi < 144 else 1.5 if dpi < 168 else 1.75 if dpi < 192 else 2.0
    while scale > 1.0 and (s['width'] / scale < 1280 or s['height'] / scale < 720):
        scale -= 0.25
    return scale


# ---------------------------------------------------------------- the whole picture
def profile():
    devices = input_devices()
    k = kind(devices)
    found = screens()
    return {
        'kind': k, 'kind_name': KIND_NAMES.get(k, k), 'icon': KIND_ICONS.get(k, 'computer'),
        'vendor': dmi('sys_vendor'), 'model': dmi('product_name') or dmi('board_name'),
        'vm': virtual_machine(), 'batteries': batteries(), 'keyboards': keyboards(devices),
        'touchpads': touchpads(devices), 'touchscreens': touchscreens(devices), 'switches': switches(devices),
        'screens': found, 'recommended_scale': recommended_scale(found),
    }


def numlock_default(p=None):
    """Num Lock at login when the user left it on Automatic: on for desktop
    computers; on a laptop or tablet only while a USB or Bluetooth keyboard
    is connected; off in a virtual machine (the host keeps it)."""
    p = p or profile()
    if p['kind'] == 'vm':
        return False
    if p['kind'] in PORTABLE:
        return any(kb['connection'] in ('usb', 'bluetooth') for kb in p['keyboards'])
    return True


def keyboard_text(p):
    names = {'built-in': 'Built-in keyboard', 'usb': 'USB keyboard', 'bluetooth': 'Bluetooth keyboard', 'other': 'Keyboard'}
    return [f"{names.get(kb['connection'], 'Keyboard')}: {kb['name']}" for kb in p['keyboards']]


# ---------------------------------------------------------------- display scale
def config_home():
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')


def display_file(cfg=None):
    return Path(cfg or config_home())/'eduka-desktop'/'desktop'/'display.json'


def read_display(cfg=None):
    try:
        data = json.loads(display_file(cfg).read_text(encoding='utf-8'))
        if isinstance(data, dict):
            scale = float(data.get('scale', 1.0))
            return {'scale': scale if scale in SCALES else 1.0, 'auto': bool(data.get('auto', False))}
    except (OSError, ValueError, TypeError):
        pass
    return None


def scale_environment(scale):
    """Qt programs (Eduka, LXQt) scale everything; GTK programs scale whole
    pixels (GDK_SCALE) and the rest of the way with their text."""
    gdk = 2 if scale >= 2 else 1
    env = {'QT_SCALE_FACTOR': f'{scale:g}', 'GDK_SCALE': str(gdk), 'GDK_DPI_SCALE': f'{scale / gdk:g}'}
    return env


def _set_environment(conf, values):
    """Set keys of the [Environment] section of LXQt's session.conf (a key
    with the value None is removed); every other line stays."""
    try:
        lines = conf.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError:
        lines = ['[General]']
    out, inside, done = [], False, set()
    for line in lines:
        st = line.strip()
        if st.startswith('[') and st.endswith(']'):
            if inside:
                out += [f'{k}={v}' for k, v in values.items() if k not in done and v is not None]
                done.update(values)
            inside = st == '[Environment]'
            out.append(line); continue
        if inside and '=' in st:
            key = st.split('=', 1)[0].strip()
            if key in values:
                done.add(key)
                if values[key] is not None:
                    out.append(f'{key}={values[key]}')
                continue
        out.append(line)
    if inside:
        out += [f'{k}={v}' for k, v in values.items() if k not in done and v is not None]
        done.update(values)
    missing = {k: v for k, v in values.items() if k not in done and v is not None}
    if missing:
        if out and out[-1].strip():
            out.append('')
        out.append('[Environment]')
        out += [f'{k}={v}' for k, v in missing.items()]
    conf.parent.mkdir(parents=True, exist_ok=True)
    tmp = conf.with_name(conf.name + '.eduka-tmp')
    tmp.write_text('\n'.join(out) + '\n', encoding='utf-8')
    os.replace(tmp, conf)


def apply_scale(scale, auto=False, cfg=None):
    """Save the display scale for the next login of Eduka-Desktop (and LXQt):
    the [Environment] of ~/.config/lxqt/session.conf, which lxqt-session
    gives to every program of the session."""
    if scale not in SCALES:
        raise ValueError('scale must be one of 75, 100, 125, 150, 175 or 200 %')
    cfg = Path(cfg or config_home())
    env = scale_environment(scale) if scale != 1.0 else {k: None for k in scale_environment(1.5)}
    _set_environment(cfg/'lxqt'/'session.conf', env)
    path = display_file(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'scale': scale, 'auto': bool(auto)}) + '\n', encoding='utf-8')
    return True


def first_login_scale(cfg=None):
    """At the first login of an account on a sharp screen: the recommended
    scale, once (the user's choice is never changed afterwards)."""
    if read_display(cfg) is not None:
        return None
    cfg = Path(cfg or config_home())
    # A scale set before with LXQt's own settings stays.
    try:
        text = (cfg/'lxqt'/'session.conf').read_text(encoding='utf-8', errors='ignore')
        m = re.search(r'^\s*QT_SCALE_FACTOR\s*=\s*([0-9.]+)', text, re.M)
    except OSError:
        m = None
    if m:
        try:
            have = min(SCALES, key=lambda v: abs(v - float(m.group(1))))
        except ValueError:
            have = 1.0
        path = display_file(cfg); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'scale': have, 'auto': False}) + '\n', encoding='utf-8')
        return None
    rec = recommended_scale()
    apply_scale(rec, auto=True, cfg=cfg)
    return rec


if __name__ == '__main__':
    print(json.dumps(profile(), indent=1, default=str))
