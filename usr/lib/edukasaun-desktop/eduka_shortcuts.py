#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Keyboard shortcuts of Eduka-Desktop (0.11 RC3).

The LXQt shortcuts (Ctrl+Alt+T terminal, Ctrl+Alt+E files, Ctrl+Alt+L lock,
Print, the brightness keys, …) stay as LXQt ships them. Eduka adds the
Windows shortcuts people already know (Super+E, Super+D, Super+L,
Super+arrows, Super+Shift+S, Ctrl+Shift+Esc, …) and the sound and media keys
(the volume of LXQt lived in lxqt-panel, which Eduka-Panel replaces).

No two shortcuts share a key: a key that LXQt, the user or the window
manager (xfwm4, Openbox, KWin) already uses is left to it, and Eduka-Settings
→ Keyboard → Shortcuts says so. The shortcuts live in LXQt's own file
(~/.config/lxqt/globalkeyshortcuts.conf, read by lxqt-globalkeysd); Eduka's
entries run `eduka-shortcut ACTION` and are recognized by that command, so a
key the user changed with LXQt's shortcut editor is kept.

Choices: ~/.config/eduka-desktop/desktop/shortcuts.json
  {"enabled": true, "off": ["media-play", …]}
"""
import json, os, re, shutil, subprocess, tempfile, time, xml.etree.ElementTree as ET
from pathlib import Path

EXEC = 'eduka-shortcut'
LXQT_FILE = ('lxqt', 'globalkeyshortcuts.conf')
FIRST_ID = 1200

# (action, keys, label, group). Keys are written as lxqt-globalkeys writes
# them: modifiers Shift, Control, Alt, Meta (= Super / Windows key) and the
# X key name.
SHORTCUTS = (
    ('search', ('Meta+S',), 'Search apps and files', 'Start'),
    ('run', ('Meta+R', 'Alt+F2'), 'Run a command', 'Start'),
    ('menu', ('Alt+F1',), 'Open Eduka-Desktop (start menu)', 'Start'),
    ('show-desktop', ('Meta+D',), 'Show the desktop; again brings the windows back', 'Windows'),
    ('minimize-all', ('Meta+M',), 'Minimize all windows', 'Windows'),
    ('restore-all', ('Shift+Meta+M',), 'Bring the minimized windows back', 'Windows'),
    ('maximize', ('Meta+Up',), 'Maximize the window', 'Windows'),
    ('restore', ('Meta+Down',), 'Restore the window, then minimize it', 'Windows'),
    ('snap-left', ('Meta+Left',), 'Window on the left half of the screen', 'Windows'),
    ('snap-right', ('Meta+Right',), 'Window on the right half of the screen', 'Windows'),
    ('monitor-left', ('Shift+Meta+Left',), 'Window to the screen on the left', 'Windows'),
    ('monitor-right', ('Shift+Meta+Right',), 'Window to the screen on the right', 'Windows'),
    ('desktop-prev', ('Control+Meta+Left',), 'Previous workspace', 'Windows'),
    ('desktop-next', ('Control+Meta+Right',), 'Next workspace', 'Windows'),
    ('files', ('Meta+E',), 'File manager', 'Programs'),
    ('settings', ('Meta+I',), 'Eduka-Settings', 'Programs'),
    ('action-center', ('Meta+A',), 'Action Center (quick settings)', 'Programs'),
    ('notifications', ('Meta+N',), 'Notifications', 'Programs'),
    ('emoji', ('Meta+period',), 'Emoji and symbols', 'Programs'),
    ('task-manager', ('Shift+Control+Escape',), 'Task manager', 'Programs'),
    ('leave', ('Control+Alt+Delete',), 'Lock, log out, sleep, restart or shut down', 'Programs'),
    ('lock', ('Meta+L',), 'Lock the screen', 'Programs'),
    ('display', ('Meta+P',), 'Screens and projector', 'Programs'),
    ('calculator', ('XF86Calculator',), 'Calculator', 'Programs'),
    ('files', ('XF86Explorer', 'XF86MyComputer'), 'File manager', 'Programs'),
    ('browser', ('XF86WWW', 'XF86HomePage'), 'Web browser', 'Programs'),
    ('mail', ('XF86Mail',), 'E-mail', 'Programs'),
    ('screenshot-region', ('Shift+Meta+S',), 'Screenshot of an area', 'Screenshots'),
    ('screenshot-window', ('Alt+Print',), 'Screenshot of the window', 'Screenshots'),
    ('screenshot-save', ('Meta+Print',), 'Screenshot saved to Pictures at once', 'Screenshots'),
    ('accessibility', ('Meta+U',), 'Accessibility settings', 'Accessibility'),
    ('screen-reader', ('Control+Meta+Return',), 'Screen reader on or off', 'Accessibility'),
    ('osk', ('Control+Meta+O',), 'On-screen keyboard on or off', 'Accessibility'),
    ('magnifier', ('Meta+equal', 'Meta+KP_Add'), 'Magnifier', 'Accessibility'),
    ('volume-up', ('XF86AudioRaiseVolume',), 'Volume up', 'Sound and media'),
    ('volume-down', ('XF86AudioLowerVolume',), 'Volume down', 'Sound and media'),
    ('volume-mute', ('XF86AudioMute',), 'Sound off or on', 'Sound and media'),
    ('mic-mute', ('XF86AudioMicMute',), 'Microphone off or on', 'Sound and media'),
    ('media-play', ('XF86AudioPlay', 'XF86AudioPause'), 'Play or pause', 'Sound and media'),
    ('media-next', ('XF86AudioNext',), 'Next track', 'Sound and media'),
    ('media-prev', ('XF86AudioPrev',), 'Previous track', 'Sound and media'),
    ('media-stop', ('XF86AudioStop',), 'Stop playing', 'Sound and media'),
    ('touchpad-toggle', ('XF86TouchpadToggle',), 'Touchpad on or off', 'Laptop'),
)
ACTIONS = {a for a, *_r in SHORTCUTS}
GROUPS = ('Start', 'Windows', 'Programs', 'Screenshots', 'Accessibility', 'Sound and media', 'Laptop')

# Shortcuts of Eduka, LXQt and the window manager that Eduka does not write
# (shown on the Shortcuts page so everything is in one list).
BUILT_IN = (
    ('Super', 'Open Eduka-Desktop (start menu)', 'Start'),
    ('Super+Q', 'Eduka-Quick (when it is on)', 'Start'),
    ('Super+Space', 'Next keyboard layout (when chosen on the Keyboard page)', 'Start'),
    ('Alt+Tab', 'Switch between windows (window manager)', 'Windows'),
    ('Alt+F4', 'Close the window (window manager)', 'Windows'),
    ('Ctrl+Alt+T', 'Terminal (LXQt)', 'Programs'),
    ('Ctrl+Alt+E', 'File manager (LXQt)', 'Programs'),
    ('Ctrl+Alt+I', 'Web browser (LXQt)', 'Programs'),
    ('Ctrl+Alt+L', 'Lock the screen (LXQt)', 'Programs'),
    ('Print', 'Screenshot (LXQt)', 'Screenshots'),
    ('Brightness keys', 'Screen brightness (LXQt)', 'Laptop'),
)


def config_home():
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')


def lxqt_file(cfg=None):
    return Path(cfg or config_home()).joinpath(*LXQT_FILE)


def prefs_file(cfg=None):
    return Path(cfg or config_home())/'eduka-desktop'/'desktop'/'shortcuts.json'


def read_prefs(cfg=None):
    try:
        data = json.loads(prefs_file(cfg).read_text(encoding='utf-8'))
        if isinstance(data, dict):
            off = [a for a in data.get('off', []) if a in ACTIONS]
            return {'enabled': bool(data.get('enabled', True)), 'off': off}
    except (OSError, ValueError):
        pass
    return {'enabled': True, 'off': []}


def save_prefs(prefs, cfg=None):
    path = prefs_file(cfg)
    data = {'enabled': bool(prefs.get('enabled', True)), 'off': sorted(a for a in prefs.get('off', []) if a in ACTIONS)}
    _write_atomic(path, json.dumps(data, indent=1) + '\n')


def _write_atomic(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.eduka-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(text)
        mask = os.umask(0o022); os.umask(mask)
        os.chmod(tmp, 0o644 & ~mask)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------- key names
_MODS = {'shift': 'shift', 's': 'shift', 'control': 'control', 'ctrl': 'control', 'primary': 'control', 'c': 'control',
         'alt': 'alt', 'a': 'alt', 'mod1': 'alt', 'm': 'alt', 'meta': 'super', 'super': 'super', 'w': 'super',
         'mod4': 'super', 'win': 'super', 'hyper': 'hyper', 'h': 'hyper'}


def normalize(mods, key):
    """(frozenset of modifiers, key name in lower case): one spelling for the
    keys of LXQt, xfwm4, Openbox and KWin."""
    key = key.strip()
    k = key.lower()
    k = {'kp_enter': 'kp_enter', 'enter': 'return', 'esc': 'escape', 'del': 'delete', 'ins': 'insert',
         'pgup': 'page_up', 'prior': 'page_up', 'pgdown': 'page_down', 'next': 'page_down',
         '.': 'period', ',': 'comma', '=': 'equal', '+': 'plus', '-': 'minus', 'sysreq': 'print', 'sys_req': 'print'}.get(k, k)
    return frozenset(_MODS.get(m.lower(), m.lower()) for m in mods if m), k


def parse_lxqt(shortcut):
    parts = shortcut.split('+')
    # "Meta++" or a key that is itself "+": keep the last part as the key.
    if shortcut.endswith('++'):
        parts = shortcut[:-2].split('+') + ['+']
    return normalize(parts[:-1], parts[-1]) if parts else None


def parse_xfwm(text):
    mods = re.findall(r'<([^>]+)>', text)
    key = re.sub(r'<[^>]+>', '', text)
    return normalize(mods, key) if key else None


def parse_openbox(text):
    parts = text.split('-')
    if text.endswith('--'):
        parts = text[:-2].split('-') + ['-']
    return normalize(parts[:-1], parts[-1]) if parts else None


def parse_kde(text):
    parts = text.split('+')
    return normalize(parts[:-1], parts[-1]) if parts and parts[-1] else None


def human(shortcut):
    """Meta+Shift+S → Super+Shift+S (as the Shortcuts page shows it)."""
    names = {'Meta': 'Super', 'Control': 'Ctrl', 'period': '.', 'equal': '=', 'Return': 'Enter', 'Escape': 'Esc',
             'KP_Add': 'Num +', 'Print': 'PrtScn', 'Delete': 'Del'}
    out = []
    for part in shortcut.split('+'):
        if part.startswith('XF86'):
            part = {'XF86AudioRaiseVolume': 'Volume up key', 'XF86AudioLowerVolume': 'Volume down key',
                    'XF86AudioMute': 'Mute key', 'XF86AudioMicMute': 'Microphone mute key', 'XF86AudioPlay': 'Play key',
                    'XF86AudioPause': 'Pause key', 'XF86AudioNext': 'Next key', 'XF86AudioPrev': 'Previous key',
                    'XF86AudioStop': 'Stop key', 'XF86Calculator': 'Calculator key', 'XF86Explorer': 'Explorer key',
                    'XF86MyComputer': 'My Computer key', 'XF86WWW': 'Browser key', 'XF86HomePage': 'Home page key',
                    'XF86Mail': 'Mail key', 'XF86TouchpadToggle': 'Touchpad key'}.get(part, part[4:] + ' key')
        out.append(names.get(part, part))
    # Windows order: Ctrl, Super, Shift, Alt as people read them.
    order = {'Ctrl': 0, 'Super': 1, 'Shift': 2, 'Alt': 3}
    keys = out[-1:]; mods = sorted(out[:-1], key=lambda m: order.get(m, 9))
    return '+'.join(mods + keys)


# ---------------------------------------------------------------- the window manager
def running_wm():
    for name in ('xfwm4', 'openbox', 'kwin_x11', 'kwin_wayland', 'marco', 'fluxbox', 'icewm'):
        try:
            if subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', name], capture_output=True, timeout=2).returncode == 0:
                return name
        except (OSError, subprocess.SubprocessError):
            break
    return ''


def _xfwm_keys(cfg):
    """Keys of xfwm4 (xfconf channel xfce4-keyboard-shortcuts, custom when
    there, else the defaults)."""
    keys = set()
    for path in (Path(cfg)/'xfce4'/'xfconf'/'xfce-perchannel-xml'/'xfce4-keyboard-shortcuts.xml',
                 Path('/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml')):
        try:
            root = ET.parse(str(path)).getroot()
        except (OSError, ET.ParseError):
            continue
        for chan in root.findall("./property[@name='xfwm4']"):
            custom = chan.find("./property[@name='custom']")
            for group in ([custom] if custom is not None and len(custom) else chan.findall('./property')):
                for prop in group.findall('./property'):
                    if prop.get('value') and prop.get('value') != 'empty':
                        k = parse_xfwm(prop.get('name', ''))
                        if k:
                            keys.add(k)
        if keys:
            break
    return keys


def _openbox_keys(cfg):
    keys = set()
    for path in (Path(cfg)/'openbox'/'rc.xml', Path(cfg)/'openbox'/'lxqt-rc.xml', Path('/etc/xdg/openbox/rc.xml')):
        try:
            root = ET.parse(str(path)).getroot()
        except (OSError, ET.ParseError):
            continue
        for kb in root.iter():
            if kb.tag.endswith('keybind') and kb.get('key'):
                k = parse_openbox(kb.get('key'))
                if k:
                    keys.add(k)
        if keys:
            break
    return keys


def _kwin_keys(cfg):
    keys = set()
    try:
        text = (Path(cfg)/'kglobalshortcutsrc').read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return keys
    inside = False
    for line in text.splitlines():
        if line.startswith('['):
            inside = line.strip() == '[kwin]'
        elif inside and '=' in line:
            fields = line.split('=', 1)[1].split(',')
            for spec in fields[:1]:
                for one in spec.split('\t'):
                    if one and one != 'none':
                        k = parse_kde(one)
                        if k:
                            keys.add(k)
    return keys


def wm_keys(cfg=None, wm=None):
    cfg = cfg or config_home()
    wm = running_wm() if wm is None else wm
    if wm == 'xfwm4':
        return _xfwm_keys(cfg)
    if wm == 'openbox':
        return _openbox_keys(cfg)
    if wm.startswith('kwin'):
        return _kwin_keys(cfg)
    return set()


# ---------------------------------------------------------------- what this computer has
def first_installed(names):
    return next((n for n in names if shutil.which(n)), '')


EMOJI_PICKERS = ('emote', 'gnome-characters', 'kcharselect', 'gucharmap')
CALCULATORS = ('galculator', 'qalculate-gtk', 'qalculate-qt', 'kcalc', 'gnome-calculator', 'mate-calc', 'speedcrunch')
TASK_MANAGERS = ('qps', 'lxtask', 'xfce4-taskmanager', 'gnome-system-monitor', 'mate-system-monitor', 'plasma-systemmonitor')
SCREENSHOTERS = ('screengrab', 'flameshot', 'spectacle', 'xfce4-screenshooter', 'gnome-screenshot', 'scrot', 'maim', 'import')
MAIL = ('thunderbird', 'evolution', 'claws-mail', 'kmail', 'geary', 'sylpheed')
RUNNERS = ('lxqt-runner',)


def is_laptop():
    try:
        import eduka_device
        return eduka_device.is_portable()
    except Exception:
        return any(Path('/sys/class/power_supply').glob('BAT*'))


def available(action):
    """False when nothing on this computer can do it (the key stays free)."""
    if action == 'emoji':
        return bool(first_installed(EMOJI_PICKERS))
    if action == 'calculator':
        return bool(first_installed(CALCULATORS))
    if action == 'mail':
        return bool(first_installed(MAIL))
    if action.startswith('screenshot'):
        return bool(first_installed(SCREENSHOTERS))
    if action == 'screen-reader':
        return bool(shutil.which('orca'))
    if action == 'osk':
        return bool(shutil.which('onboard'))
    if action == 'magnifier':
        return bool(first_installed(('magnus', 'kmag', 'xzoom')))
    if action == 'touchpad-toggle':
        return is_laptop() and bool(shutil.which('xinput'))
    if action in ('maximize', 'restore', 'snap-left', 'snap-right', 'monitor-left', 'monitor-right',
                  'show-desktop', 'minimize-all', 'restore-all', 'desktop-prev', 'desktop-next'):
        return bool(shutil.which('wmctrl') and shutil.which('xdotool'))
    if action in ('volume-up', 'volume-down', 'volume-mute', 'mic-mute'):
        return bool(first_installed(('pactl', 'wpctl', 'amixer')))
    return True


# ---------------------------------------------------------------- LXQt's file
def _sections(text):
    """[(header or None, [lines])] in the order of the file."""
    blocks, cur = [], (None, [])
    for line in text.splitlines():
        st = line.strip()
        if st.startswith('[') and st.endswith(']'):
            blocks.append(cur)
            cur = (st[1:-1], [line])
        else:
            cur[1].append(line)
    blocks.append(cur)
    return blocks


def _values(lines):
    out = {}
    for line in lines[1:]:
        if '=' in line and not line.lstrip().startswith(('#', ';')):
            k, v = line.split('=', 1)
            out[k.strip()] = v.strip()
    return out


def eduka_action(values):
    """The action of an entry Eduka wrote (Exec=eduka-shortcut, ACTION)."""
    parts = [p.strip() for p in values.get('Exec', '').split(',')]
    if len(parts) >= 2 and os.path.basename(parts[0]) == EXEC and parts[1] in ACTIONS:
        return parts[1]
    return ''


def section_key(header):
    name = header.rsplit('.', 1)[0] if '.' in header else header
    return name.replace('%2B', '+').replace('%2b', '+')


def dead_in_eduka(values):
    """An action of a program that never runs in Eduka-Desktop: lxqt-panel
    (replaced by Eduka-Panel; its menu and volume keys did nothing) or a
    missing lxqt-runner. Eduka may take such a key; the entry is turned off."""
    path = values.get('path', '')
    if not path or values.get('service'):
        return False
    return path.startswith('/panel/') or (path.startswith('/runner/') and not shutil.which('lxqt-runner'))


# Keys that LXQt programs of the session register themselves after they
# start (lxqt-globalkeysd adds them to the file then): taken when installed.
RUNTIME_KEYS = (('lxqt-runner', 'Alt+F2', 'LXQt runner'),)


def plan(cfg=None, prefs=None, wm=None, text=None):
    """What Eduka's shortcuts are on this computer: a list of
    (action, keys, label, group, state, detail) with state one of
    'on', 'custom' (the user moved the key), 'off' (turned off),
    'taken' (detail: what uses the key), 'wm' (the window manager uses it)
    and 'missing' (no program for it)."""
    cfg = cfg or config_home()
    prefs = prefs or read_prefs(cfg)
    if text is None:
        try:
            text = lxqt_file(cfg).read_text(encoding='utf-8', errors='ignore')
        except OSError:
            text = ''
    others, mine, mine_off = {}, {}, set()
    for header, lines in _sections(text):
        if not header or header == 'General':
            continue
        values = _values(lines)
        action = eduka_action(values)
        key = section_key(header)
        enabled = values.get('Enabled', 'true').lower() == 'true'
        if action:
            mine.setdefault(action, []).append(key)
            if not enabled:
                mine_off.add(key)
        elif enabled and not dead_in_eduka(values):
            k = parse_lxqt(key)
            if k:
                others[k] = values.get('Comment', '') or values.get('Exec', '') or values.get('path', '')
    for program, key, what in RUNTIME_KEYS:
        if shutil.which(program):
            others.setdefault(parse_lxqt(key), what)
    taken_wm = wm_keys(cfg, wm)
    defaults = {}
    for action, keys, *_r in SHORTCUTS:
        defaults.setdefault(action, []).extend(keys)
    rows, used, seen_custom = [], set(), set()
    for action, keys, label, group in SHORTCUTS:
        custom = [k for k in mine.get(action, []) if k not in defaults[action]]
        if custom and action not in seen_custom:
            seen_custom.add(action)
            rows.append((action, tuple(custom), label, group, 'custom', ''))
            used.update(parse_lxqt(k) for k in custom)
            continue
        for key in keys:
            k = parse_lxqt(key)
            if not prefs.get('enabled', True) or action in prefs.get('off', []):
                state, detail = 'off', ''
            elif key in mine_off:
                state, detail = 'off', 'LXQt'
            elif not available(action):
                state, detail = 'missing', ''
            elif k in others:
                state, detail = 'taken', others[k]
            elif k in taken_wm:
                state, detail = 'wm', ''
            elif k in used:
                state, detail = 'taken', 'Eduka-Desktop'
            else:
                state, detail = 'on', ''
                used.add(k)
            rows.append((action, (key,), label, group, state, detail))
    return rows


def render(cfg=None, prefs=None, wm=None):
    """The new text of LXQt's file, or None when nothing changes."""
    cfg = cfg or config_home()
    path = lxqt_file(cfg)
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        text = ''
    rows = plan(cfg, prefs, wm, text)
    wanted = {}
    for action, keys, label, _g, state, _d in rows:
        if state in ('on', 'custom') or (state == 'off' and _d == 'LXQt'):
            for key in keys:
                wanted[key] = (action, label)
    taken = {parse_lxqt(k) for k in wanted}
    kept = []
    for header, lines in _sections(text):
        values = _values(lines) if header else {}
        action = eduka_action(values) if header else ''
        if action:
            key = section_key(header)
            if wanted.get(key, ('',))[0] == action:
                kept.append((header, lines)); wanted.pop(key)
            continue                              # an Eduka key that is off now
        if header and dead_in_eduka(values) and parse_lxqt(section_key(header)) in taken \
                and values.get('Enabled', 'true').lower() == 'true':
            lines = [('Enabled=false' if l.strip().startswith('Enabled=') else l) for l in lines]
        if header or any(l.strip() for l in lines):
            kept.append((header, lines))
    ids = []
    for header, _lines in kept:
        if header and '.' in header and header.rsplit('.', 1)[1].isdigit():
            ids.append(int(header.rsplit('.', 1)[1]))
    nxt = max([FIRST_ID - 1] + ids) + 1
    out = []
    for header, lines in kept:
        block = '\n'.join(lines).rstrip('\n')
        if block:
            out.append(block)
    for key, (action, label) in wanted.items():
        out.append(f'[{key.replace("+", "%2B")}.{nxt}]\nComment=Eduka: {label}\nEnabled=true\nExec={EXEC}, {action}')
        nxt += 1
    new = '\n\n'.join(out) + '\n'
    return None if new == text else new


def apply(cfg=None, prefs=None, wm=None):
    """Write Eduka's shortcuts into LXQt's file (at login, before
    lxqt-globalkeysd starts). True when the file changed."""
    new = render(cfg, prefs, wm)
    if new is None:
        return False
    _write_atomic(lxqt_file(cfg), new)
    return True


def daemon_running():
    try:
        return subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'lxqt-globalkeysd'],
                              capture_output=True, timeout=2).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def apply_now(cfg=None, prefs=None):
    """From Eduka-Settings while the session runs: lxqt-globalkeysd saves its
    own list when it stops, so it is stopped first, the file is written,
    and it is started again."""
    was_running = daemon_running()
    if was_running:
        subprocess.run(['pkill', '-TERM', '-u', str(os.getuid()), '-x', 'lxqt-globalkeysd'], capture_output=True, timeout=3)
        for _i in range(30):
            if not daemon_running():
                break
            time.sleep(0.1)
    changed = apply(cfg, prefs)
    if was_running and shutil.which('lxqt-globalkeysd'):
        try:
            subprocess.Popen(['lxqt-globalkeysd'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        except OSError:
            pass
    return changed


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['--plan']:
        for row in plan():
            print('%-18s %-28s %-8s %s' % (row[0], '+'.join(row[1]), row[4], row[5]))
    else:
        print('changed' if apply() else 'unchanged')
