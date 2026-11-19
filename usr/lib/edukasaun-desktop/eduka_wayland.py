#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Settings of the LXQt Wayland session and of KWin (0.11 Pre-Stable).

In a Wayland session the compositor, not X11, owns the keyboard, the mouse,
the touchpad and the windows: xinput, setxkbmap and EWMH only reach
XWayland there. Eduka-Settings therefore writes the same choices into the
compositor's own configuration and asks it to reload:

* labwc (LXQt's default Wayland compositor): ~/.config/labwc/rc.xml, the
  file LXQt copies there at the first Wayland login: <libinput> (touchpad
  and mouse), <focus> (focus follows the mouse), <core><primarySelection>
  (middle-click paste) and <desktops number="N"> (workspaces); then labwc
  reloads it (SIGHUP to $LABWC_PID, or labwc --reconfigure).
* KWin (kwin_wayland and kwin_x11, KDE 5 and 6): kwinrc through
  kwriteconfig6/kwriteconfig5, then KWin's reconfigure over D-Bus.

Other compositors (niri, Wayfire, sway, Hyprland) keep their own files and
are left alone. A file that cannot be read as XML is never written. Only the
standard library is used.
"""
import os, re, shutil, signal, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

CONFIG_HOME = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')
LABWC_RC = CONFIG_HOME/'labwc'/'rc.xml'
COMPOSITORS = ('labwc', 'kwin_wayland', 'niri', 'wayfire', 'sway', 'hyprland', 'river')


def is_wayland():
    return os.environ.get('XDG_SESSION_TYPE') == 'wayland' or bool(os.environ.get('WAYLAND_DISPLAY'))


def compositor():
    """The Wayland compositor of this session ('labwc', 'kwin_wayland', ...)
    or '' in an X11 session."""
    if not is_wayland():
        return ''
    for part in (os.environ.get('XDG_CURRENT_DESKTOP') or '').split(':'):
        if part.lower() in COMPOSITORS:
            return part.lower()
    if os.environ.get('LABWC_PID'):
        return 'labwc'
    try:
        text = (CONFIG_HOME/'lxqt'/'session.conf').read_text(encoding='utf-8', errors='ignore')
        m = re.search(r'^\s*compositor\s*=\s*(\S+)', text, re.M)
        if m:
            return os.path.basename(m.group(1)).lower()
    except OSError:
        pass
    return ''


# ---------------------------------------------------------------- labwc
def _labwc_load():
    """(prolog, root) of ~/.config/labwc/rc.xml, comments kept; None when
    the file is missing or is not valid XML (it is then never written)."""
    try:
        text = LABWC_RC.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None
    m = re.search(r'<labwc_config\b', text)
    if not m:
        return None
    try:
        root = ET.fromstring(text, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    except ET.ParseError:
        return None
    if root.tag != 'labwc_config':
        return None
    return text[:m.start()], root


def _labwc_save(prolog, root, created):
    if created and hasattr(ET, 'indent'):
        ET.indent(root, space='  ')
    text = (prolog or '<?xml version="1.0"?>\n') + ET.tostring(root, encoding='unicode') + '\n'
    tmp = LABWC_RC.with_name('.rc.xml.eduka-tmp')
    try:
        backup = LABWC_RC.with_name('rc.xml.eduka-backup')
        if not backup.exists():
            shutil.copy2(LABWC_RC, backup)
        tmp.write_text(text, encoding='utf-8')
        os.replace(tmp, LABWC_RC)
    except OSError:
        return False
    return True


def _child(parent, tag, created, **attrs):
    for el in parent.findall(tag):
        if all(el.get(k) == v for k, v in attrs.items()):
            return el
    created.append(tag)
    return ET.SubElement(parent, tag, attrs)


def _value(parent, tag, value, created):
    el = parent.find(tag)
    if el is None:
        el = ET.SubElement(parent, tag); created.append(tag)
    el.text = str(value)


def labwc_reconfigure():
    """labwc reads rc.xml again (it keeps running)."""
    pid = os.environ.get('LABWC_PID', '')
    if pid.isdigit():
        try:
            os.kill(int(pid), signal.SIGHUP)
            return True
        except OSError:
            pass
    if shutil.which('labwc'):
        try:
            subprocess.run(['labwc', '--reconfigure'], capture_output=True, timeout=5)
            return True
        except (OSError, subprocess.SubprocessError):
            pass
    return False


def labwc_update(change, reload=True):
    """Run change(root, created) on rc.xml, save it and reload labwc.
    'changed' or 'same'; False when rc.xml is missing or not valid XML."""
    loaded = _labwc_load()
    if loaded is None:
        return False
    prolog, root = loaded
    before = ET.tostring(root, encoding='unicode')
    created = []
    change(root, created)
    if ET.tostring(root, encoding='unicode') == before:
        return 'same'
    if not _labwc_save(prolog, root, created):
        return False
    if reload:
        labwc_reconfigure()
    return 'changed'


def _yes(on):
    return 'yes' if on else 'no'


def labwc_input(cfg):
    """Touchpad and mouse of eduka_input's settings, as labwc's <libinput>."""
    def change(root, created):
        lib = _child(root, 'libinput', created)
        tp = _child(lib, 'device', created, category='touchpad')
        _value(tp, 'sendEventsMode', _yes(cfg.get('tp_enabled', True)), created)
        _value(tp, 'tap', _yes(cfg.get('tp_tap', True)), created)
        _value(tp, 'tapAndDrag', _yes(cfg.get('tp_drag', True)), created)
        _value(tp, 'dragLock', _yes(cfg.get('tp_drag_lock', False)), created)
        _value(tp, 'naturalScroll', _yes(cfg.get('tp_natural', True)), created)
        _value(tp, 'disableWhileTyping', _yes(cfg.get('tp_dwt', True)), created)
        _value(tp, 'leftHanded', _yes(cfg.get('left_handed', False)), created)
        _value(tp, 'pointerSpeed', f"{max(-1.0, min(1.0, float(cfg.get('tp_speed', 0.0)))):.2f}", created)
        _value(tp, 'scrollMethod', {'two-finger': 'twofinger', 'edge': 'edge', 'none': 'none'}.get(cfg.get('tp_scroll'), 'twofinger'),
               created)
        mouse = _child(lib, 'device', created, category='non-touch')
        _value(mouse, 'pointerSpeed', f"{max(-1.0, min(1.0, float(cfg.get('mouse_speed', 0.0)))):.2f}", created)
        _value(mouse, 'naturalScroll', _yes(cfg.get('mouse_natural', False)), created)
        _value(mouse, 'leftHanded', _yes(cfg.get('left_handed', False)), created)
        _value(mouse, 'middleEmulation', _yes(cfg.get('middle_emulation', False)), created)
    return labwc_update(change)


def labwc_focus(mouse, delay=250):
    def change(root, created):
        focus = _child(root, 'focus', created)
        _value(focus, 'followMouse', _yes(mouse), created)
        _value(focus, 'raiseOnFocus', 'no', created)
    return labwc_update(change)


def labwc_primary_selection(on):
    def change(root, created):
        _value(_child(root, 'core', created), 'primarySelection', _yes(on), created)
    return labwc_update(change)


def labwc_desktops(n):
    """N workspaces: <desktops><number>. Named workspaces (<names>) keep
    their names; names beyond N are removed, missing ones get numbers."""
    n = max(1, min(8, int(n)))

    def change(root, created):
        d = _child(root, 'desktops', created)
        d.attrib.pop('number', None)
        _value(d, 'number', n, created)
        names = d.find('names')
        if names is not None:
            for extra in names.findall('name')[n:]:
                names.remove(extra)
    return labwc_update(change)


def labwc_desktop_count():
    loaded = _labwc_load()
    if loaded is None:
        return None
    d = loaded[1].find('desktops')
    if d is None:
        return 1
    try:
        n = int(d.get('number') or (d.findtext('number') or '0').strip() or 0)
    except ValueError:
        n = 0
    return max(1, n, len(d.findall('names/name')))


def labwc_keyboard(cfg):
    """Keyboard layouts, the layout switch key, key repeat and Num Lock of
    eduka_input's settings for labwc: XKB_DEFAULT_LAYOUT and
    XKB_DEFAULT_OPTIONS in ~/.config/labwc/environment, <keyboard> in rc.xml."""
    if _labwc_load() is None:
        return False
    env = LABWC_RC.with_name('environment')
    layouts = [re.sub(r'[^A-Za-z0-9_()-]', '', x) for x in cfg.get('layouts') or [] if x][:4]
    switch = cfg.get('switch') or ''
    try:
        lines = env.read_text(encoding='utf-8', errors='ignore').splitlines() if env.exists() else []
    except OSError:
        lines = []
    keep = [ln for ln in lines if not re.match(r'\s*XKB_DEFAULT_(LAYOUT|OPTIONS)\s*=', ln)]
    if layouts:
        keep.append('XKB_DEFAULT_LAYOUT=' + ','.join(layouts))
        if switch and len(layouts) > 1 and re.fullmatch(r'grp:[a-z_]+', switch):
            keep.append('XKB_DEFAULT_OPTIONS=' + switch)
    elif any(re.match(r'\s*XKB_DEFAULT_LAYOUT\s*=', ln) for ln in lines):
        keep += [ln for ln in lines if re.match(r'\s*XKB_DEFAULT_LAYOUT\s*=', ln)]   # the system's layout stays
    env_changed = keep != lines
    if env_changed:
        try:
            tmp = env.with_name('.environment.eduka-tmp')
            tmp.write_text('\n'.join(keep) + '\n', encoding='utf-8'); os.replace(tmp, env)
        except OSError:
            return False

    def change(root, created):
        kb = _child(root, 'keyboard', created)
        delay = max(150, min(1000, int(cfg.get('repeat_delay', 500))))
        rate = max(5, min(60, int(cfg.get('repeat_rate', 30))))
        _value(kb, 'repeatRate', rate, created)
        _value(kb, 'repeatDelay', delay, created)
        _value(kb, 'numlock', 'on' if cfg.get('numlock') else 'off', created)
    result = labwc_update(change, reload=False)
    if result == 'changed' or env_changed:
        labwc_reconfigure()
    return bool(result)


def labwc_read(path, attr=None):
    """A value of rc.xml ('focus/followMouse', or 'desktops' with attr)."""
    loaded = _labwc_load()
    if loaded is None:
        return None
    el = loaded[1].find(path)
    if el is None:
        return None
    return el.get(attr) if attr else (el.text or '').strip()


# ---------------------------------------------------------------- KWin
def _kwrite_tool():
    return shutil.which('kwriteconfig6') or shutil.which('kwriteconfig5')


def kwin_write(group, key, value, file='kwinrc'):
    tool = _kwrite_tool()
    if not tool:
        return False
    try:
        return subprocess.run([tool, '--file', file, '--group', group, '--key', key, str(value)],
                              capture_output=True, timeout=5).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def kwin_read(group, key, file='kwinrc'):
    tool = shutil.which('kreadconfig6') or shutil.which('kreadconfig5')
    if not tool:
        return ''
    try:
        return subprocess.run([tool, '--file', file, '--group', group, '--key', key],
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ''


def kwin_reconfigure():
    if not shutil.which('dbus-send'):
        return False
    try:
        subprocess.run(['dbus-send', '--session', '--type=method_call', '--dest=org.kde.KWin', '/KWin', 'org.kde.KWin.reconfigure'],
                       capture_output=True, timeout=5)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def kwin_available():
    return _kwrite_tool() is not None


if __name__ == '__main__':
    print('wayland:', is_wayland(), '| compositor:', compositor() or '-', '| labwc rc.xml:', LABWC_RC.exists())
    if LABWC_RC.exists():
        print('focus follows mouse:', labwc_read('focus/followMouse'), '| workspaces:', labwc_desktop_count())
