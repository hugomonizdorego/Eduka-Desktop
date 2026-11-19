#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Windows, workspaces and the pointer (0.11 Pre-Stable).

Eduka-Settings → Windows & Workspaces:

* Virtual workspaces: how many (1 to 8), a switcher on Eduka-Panel, and the
  taskbar showing the windows of the current workspace. The number is set
  at once (EWMH) and kept by the window manager (xfwm4, Openbox, KWin).
* Hot corners: pushing the pointer into a corner of the screen opens
  Eduka-Desktop, shows the desktop, opens the Action Center…
* Focus follows the mouse (the window under the pointer gets the keyboard)
  or click to focus, for xfwm4, Openbox, KWin, Compiz and (Wayland) labwc.
* Middle-click paste (Linux): the selected text is pasted with the middle
  button or a three-finger tap. It can be switched off for GTK programs.
* Clipboard history (Super+V, as on Windows), kept in memory only.
* Force Close: a program that has not answered for two minutes is offered
  to be closed (Eduka-Panel watches the windows; see eduka_hang).
"""
import json, os, re, shutil, subprocess
from pathlib import Path

CONFIG_HOME = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')
PREFS = CONFIG_HOME/'eduka-desktop'/'desktop'/'windows.json'
CORNERS = ('top-left', 'top-right', 'bottom-left', 'bottom-right')
CORNER_ACTIONS = (
    ('', 'Nothing'),
    ('menu', 'Open Eduka-Desktop'),
    ('show-desktop', 'Show the desktop'),
    ('action-center', 'Open the Action Center'),
    ('quick', 'Open Eduka-Quick'),
    ('desktop-next', 'Next workspace'),
    ('desktop-prev', 'Previous workspace'),
    ('notifications', 'Show notifications'),
    ('lock', 'Lock the screen'),
)
DEFAULTS = {'corners': {c: '' for c in CORNERS}, 'corner_delay': 180, 'workspace_switcher': True,
            'tasks_current_workspace': True, 'clipboard_history': True, 'force_close': True, 'hang_seconds': 120}


def read_prefs():
    prefs = json.loads(json.dumps(DEFAULTS))
    try:
        data = json.loads(PREFS.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return prefs
    if not isinstance(data, dict):
        return prefs
    corners = data.get('corners')
    if isinstance(corners, dict):
        valid = {k for k, _l in CORNER_ACTIONS}
        for c in CORNERS:
            if corners.get(c) in valid:
                prefs['corners'][c] = corners[c]
    for k in ('workspace_switcher', 'tasks_current_workspace', 'clipboard_history', 'force_close'):
        if k in data:
            prefs[k] = bool(data[k])
    try:
        prefs['corner_delay'] = max(0, min(1000, int(data.get('corner_delay', 180))))
        prefs['hang_seconds'] = max(30, min(600, int(data.get('hang_seconds', 120))))
    except (TypeError, ValueError):
        pass
    return prefs


def save_prefs(prefs):
    import eduka_ipc
    clean = read_prefs()
    clean.update({k: v for k, v in prefs.items() if k in DEFAULTS})
    eduka_ipc.write_json_atomic(PREFS, clean, indent=2)


def _run(cmd, timeout=4):
    if not shutil.which(cmd[0]):
        return None
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def window_manager():
    """The window manager of this session: xfwm4, openbox, kwin_x11, compiz,
    marco, … ('' when none is known)."""
    uid = os.getuid()
    known = ('xfwm4', 'openbox', 'kwin_x11', 'compiz', 'marco', 'fluxbox', 'icewm', 'labwc', 'kwin_wayland')
    for d in Path('/proc').iterdir():
        if not d.name.isdigit():
            continue
        try:
            if d.stat().st_uid != uid:
                continue
            comm = (d/'comm').read_text().strip()
        except OSError:
            continue
        if comm in known:
            return comm
    try:
        import eduka_wayland
        comp = eduka_wayland.compositor()
        if comp in known:
            return comp
    except ImportError:
        pass
    return ''


# ---------------------------------------------------------------- workspaces
def _root_cardinal(prop):
    out = _run(['xprop', '-root', prop]) or ''
    m = re.search(r'=\s*(\d+)', out)
    return int(m.group(1)) if m else None


def workspace_count():
    return _root_cardinal('_NET_NUMBER_OF_DESKTOPS') or 1


def current_workspace():
    return _root_cardinal('_NET_CURRENT_DESKTOP') or 0


def set_workspace_count(n):
    """Set at once (EWMH) and keep it in the window manager's settings."""
    n = max(1, min(8, int(n)))
    if shutil.which('wmctrl'):
        _run(['wmctrl', '-n', str(n)])
    wm = window_manager()
    try:
        import eduka_common as ec
        if wm == 'xfwm4':
            ec._xfwm4_set('/general/workspace_count', 'int', n)
        elif wm == 'openbox':
            for path in ec._openbox_rc_files(create=True):
                text = path.read_text(encoding='utf-8', errors='ignore')
                if re.search(r'<desktops>.*?<number>\d+</number>', text, re.S):
                    new = re.sub(r'(<desktops>.*?<number>)\d+(</number>)', lambda m: f'{m.group(1)}{n}{m.group(2)}', text, count=1, flags=re.S)
                elif '<desktops>' in text:
                    new = text.replace('<desktops>', f'<desktops>\n    <number>{n}</number>', 1)
                else:
                    new = text.replace('</openbox_config>', f'  <desktops>\n    <number>{n}</number>\n  </desktops>\n</openbox_config>', 1)
                if new != text:
                    path.write_text(new, encoding='utf-8')
            ec.safe_popen(['openbox', '--reconfigure'])
        elif wm in ('kwin_x11', 'kwin_wayland'):
            import eduka_wayland as wl
            wl.kwin_write('Desktops', 'Number', n); wl.kwin_reconfigure()
        elif wm == 'labwc':
            import eduka_wayland as wl
            wl.labwc_desktops(n)
    except Exception:
        pass
    return True


def configured_workspace_count():
    """The number of workspaces the window manager keeps: EWMH in X11, the
    compositor's own setting in a Wayland session (labwc, KWin)."""
    n = _root_cardinal('_NET_NUMBER_OF_DESKTOPS')
    if n:
        return n
    try:
        import eduka_wayland as wl
        comp = wl.compositor()
        if comp == 'labwc':
            return max(1, min(8, int(wl.labwc_desktop_count() or 1)))
        if comp == 'kwin_wayland':
            return max(1, min(8, int(wl.kwin_read('Desktops', 'Number') or 1)))
    except (ImportError, ValueError):
        pass
    return 1


def switch_workspace(index):
    if shutil.which('wmctrl'):
        return _run(['wmctrl', '-s', str(int(index))]) is not None
    return False


# ---------------------------------------------------------------- focus
def focus_mode():
    """'mouse' (focus follows the mouse) or 'click'."""
    wm = window_manager()
    try:
        import eduka_common as ec
        if wm == 'xfwm4':
            return 'click' if (ec._xfwm4_get('/general/click_to_focus') or 'true').lower() == 'true' else 'mouse'
        if wm == 'openbox':
            for path in ec._openbox_rc_files():
                m = re.search(r'<focus>.*?<followMouse>(\w+)</followMouse>', path.read_text(encoding='utf-8', errors='ignore'), re.S)
                if m:
                    return 'mouse' if m.group(1).lower() in ('yes', 'true', 'on') else 'click'
        if wm in ('kwin_x11', 'kwin_wayland'):
            import eduka_wayland as wl
            return 'mouse' if 'Mouse' in wl.kwin_read('Windows', 'FocusPolicy') else 'click'
        if wm == 'labwc':
            import eduka_wayland as wl
            return 'mouse' if (wl.labwc_read('focus/followMouse') or 'no').lower() in ('yes', 'true', 'on') else 'click'
        if wm == 'compiz':
            out = _run(['gsettings', 'get', 'org.compiz.core:/org/compiz/profiles/Default/plugins/core/', 'click-to-focus']) or 'true'
            return 'click' if 'true' in out else 'mouse'
    except Exception:
        pass
    return 'click'


def set_focus_mode(mode, delay=250):
    """Focus follows the mouse (mode 'mouse') after `delay` ms, without
    raising the window (it stays where it is), or click to focus."""
    mouse = mode == 'mouse'
    delay = max(0, min(2000, int(delay)))
    wm = window_manager()
    try:
        import eduka_common as ec
        if wm == 'xfwm4':
            ec._xfwm4_set('/general/click_to_focus', 'bool', 'false' if mouse else 'true')
            ec._xfwm4_set('/general/focus_delay', 'int', delay)
            ec._xfwm4_set('/general/raise_on_click', 'bool', 'true')
            return True
        if wm == 'openbox':
            for path in ec._openbox_rc_files(create=True):
                text = path.read_text(encoding='utf-8', errors='ignore')
                new = text
                for tag, value in (('followMouse', 'yes' if mouse else 'no'), ('focusDelay', str(delay)), ('raiseOnFocus', 'no'),
                                   ('underMouse', 'no')):
                    if re.search(rf'<focus>.*?<{tag}>[^<]*</{tag}>', new, re.S):
                        new = re.sub(rf'(<focus>.*?<{tag}>)[^<]*(</{tag}>)', lambda m, v=value: m.group(1) + v + m.group(2), new, count=1, flags=re.S)
                    elif '<focus>' in new:
                        new = new.replace('<focus>', f'<focus>\n    <{tag}>{value}</{tag}>', 1)
                if new != text:
                    path.write_text(new, encoding='utf-8')
            ec.safe_popen(['openbox', '--reconfigure'])
            return True
        if wm in ('kwin_x11', 'kwin_wayland'):
            import eduka_wayland as wl
            ok = wl.kwin_write('Windows', 'FocusPolicy', 'FocusFollowsMouse' if mouse else 'ClickToFocus')
            wl.kwin_write('Windows', 'DelayFocusInterval', delay); wl.kwin_reconfigure()
            return ok
        if wm == 'labwc':
            import eduka_wayland as wl
            return bool(wl.labwc_focus(mouse, delay))
        if wm == 'compiz' and shutil.which('gsettings'):
            _run(['gsettings', 'set', 'org.compiz.core:/org/compiz/profiles/Default/plugins/core/', 'click-to-focus',
                  'false' if mouse else 'true'])
            return True
    except Exception:
        return False
    return False


# ---------------------------------------------------------------- middle-click paste
def middle_paste():
    try:
        import eduka_common as ec
        v = ec._get_ini_value(CONFIG_HOME/'gtk-3.0'/'settings.ini', 'Settings', 'gtk-enable-primary-paste')
        return str(v or 'true').strip().lower() not in ('false', '0', 'no')
    except Exception:
        return True


def set_middle_paste(on):
    """GTK 3 and 4 programs (Qt programs always paste with the middle button
    in X11). In a Wayland session the compositor switches it for every
    program: labwc's primarySelection, KWin's EnablePrimarySelection."""
    try:
        import eduka_common as ec
        for g in ('gtk-3.0', 'gtk-4.0'):
            ec._set_ini_value(CONFIG_HOME/g/'settings.ini', 'Settings', 'gtk-enable-primary-paste', 'true' if on else 'false')
    except Exception:
        return False
    try:
        import eduka_wayland as wl
        comp = wl.compositor()
        if comp == 'labwc':
            wl.labwc_primary_selection(on)
        elif comp == 'kwin_wayland':
            wl.kwin_write('Wayland', 'EnablePrimarySelection', 'true' if on else 'false'); wl.kwin_reconfigure()
    except Exception:
        pass
    return True


if __name__ == '__main__':
    print('window manager:', window_manager() or '?')
    print('workspaces:', workspace_count(), 'current:', current_workspace())
    print('focus:', focus_mode(), 'middle paste:', middle_paste())
    print(json.dumps(read_prefs(), indent=1))
