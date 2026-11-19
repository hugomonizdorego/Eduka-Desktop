#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""The window manager of the session, and Compiz (0.11 Pre-Stable).

Eduka-Settings → Windows → Window manager chooses among the window managers
that are installed: xfwm4 (the default), Openbox, KWin, Marco and Compiz.
The choice is LXQt's own setting (~/.config/lxqt/session.conf, window_manager)
and is used from the next login.

Compiz (3D effects: wobbly windows, the cube, all windows side by side) is
installed separately. It runs through /usr/lib/edukasaun-desktop/eduka-compiz,
which checks 3D graphics and a window decorator first and falls back to
xfwm4 or Openbox when Compiz cannot run, so a session always has window
borders. Before its first start Eduka switches off the Compiz keys that
Eduka-Desktop and LXQt use themselves (Super+S, Ctrl+Super+arrows, Alt+F1,
Alt+F2, Ctrl+Alt+T, Alt+Print), and Eduka does not start its own compositor
(picom) beside it. Only the standard library is used.
"""
import json, os, re, shutil, subprocess
from pathlib import Path

CONFIG_HOME = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')
SESSION_CONF = CONFIG_HOME/'lxqt'/'session.conf'
STATE = CONFIG_HOME/'eduka-desktop'/'desktop'/'compiz.json'
WRAPPER = '/usr/lib/edukasaun-desktop/eduka-compiz'
PROFILE = os.environ.get('COMPIZ_CONFIG_PROFILE') or 'Default'
DEFAULTS_VERSION = 1
WINDOW_MANAGERS = (
    ('xfwm4', 'xfwm4', 'Light, with its own compositor (recommended)'),
    ('openbox', 'Openbox', 'The lightest, for very old computers'),
    ('kwin_x11', 'KWin', 'The window manager of KDE Plasma'),
    ('marco', 'Marco', 'The window manager of MATE'),
    ('compiz', 'Compiz', '3D effects: wobbly windows, the cube, all windows side by side (needs 3D graphics)'),
)
DECORATORS = ('gtk-window-decorator', 'emerald', 'kde4-window-decorator', 'compiz-decorator')
PLUGINS = ['core', 'composite', 'opengl', 'compiztoolbox', 'decor', 'vpswitch', 'snap', 'mousepoll', 'resize', 'place',
           'move', 'wall', 'grid', 'regex', 'imgpng', 'session', 'animation', 'fade', 'workarounds', 'scale', 'expo',
           'ezoom', 'switcher']
# Keys of Compiz that Eduka-Desktop or LXQt use themselves: switched off.
FREE_KEYS = (
    ('expo', 'expo-key', ''),                       # Super+S is search
    ('grid', 'left-maximize', ''), ('grid', 'right-maximize', ''),   # Ctrl+Super+arrows: workspaces
    ('gnomecompat', 'main-menu-key', ''), ('gnomecompat', 'run-key', ''),
    ('gnomecompat', 'run-command-window-screenshot-key', ''), ('gnomecompat', 'run-command-terminal-key', ''),
)


def _run(cmd, timeout=6):
    if not shutil.which(cmd[0]):
        return None
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def installed():
    return [(cmd, name, hint) for cmd, name, hint in WINDOW_MANAGERS if shutil.which(cmd)]


def configured():
    """The window manager LXQt starts (its command name)."""
    try:
        text = SESSION_CONF.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return ''
    m = re.search(r'^\s*window_manager\s*=\s*(\S+)', text, re.M)
    if not m:
        return ''
    wm = os.path.basename(m.group(1))
    return 'compiz' if wm in ('eduka-compiz', 'compiz') else wm


def compiz_configured():
    return configured() == 'compiz'


def set_window_manager(cmd):
    """Write LXQt's window_manager= (Compiz through Eduka's wrapper)."""
    value = WRAPPER if cmd == 'compiz' else cmd
    try:
        text = SESSION_CONF.read_text(encoding='utf-8', errors='ignore') if SESSION_CONF.exists() else '[General]\n'
    except OSError:
        return False
    if re.search(r'^\s*window_manager\s*=', text, re.M):
        text = re.sub(r'^\s*window_manager\s*=.*$', f'window_manager={value}', text, count=1, flags=re.M)
    elif '[General]' in text:
        text = text.replace('[General]', f'[General]\nwindow_manager={value}', 1)
    else:
        text = f'[General]\nwindow_manager={value}\n\n' + text
    try:
        SESSION_CONF.parent.mkdir(parents=True, exist_ok=True)
        tmp = SESSION_CONF.with_name('.session.conf.eduka-tmp')
        tmp.write_text(text, encoding='utf-8'); os.replace(tmp, SESSION_CONF)
        return True
    except OSError:
        return False


def _renderer():
    out = _run(['glxinfo', '-B'], timeout=8) or ''
    m = re.search(r'OpenGL renderer string:\s*(.+)', out)
    return m.group(1).strip() if m else ''


def _virtual():
    out = _run(['systemd-detect-virt'], timeout=3)
    return bool(out and out.strip() not in ('none', ''))


def can_run():
    """(ok, reason): Compiz, a window decorator and 3D graphics."""
    if not shutil.which('compiz'):
        return False, 'Compiz is not installed.'
    if not any(shutil.which(d) for d in DECORATORS):
        return False, 'Compiz has no window decorator (install compiz-gnome or emerald).'
    if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
        return False, 'Compiz works in the X11 session only.'
    renderer = _renderer().lower()
    if any(x in renderer for x in ('llvmpipe', 'softpipe', 'swrast', 'svga3d')) or (_virtual() and not renderer):
        return False, 'Compiz needs 3D graphics, which this computer (or virtual machine) does not have.'
    return True, ''


def _gsettings(plugin, key, value):
    return _run(['gsettings', 'set', f'org.compiz.{plugin}:/org/compiz/profiles/{PROFILE}/plugins/{plugin}/', key, value]) is not None


def _gsettings_get(plugin, key):
    return (_run(['gsettings', 'get', f'org.compiz.{plugin}:/org/compiz/profiles/{PROFILE}/plugins/{plugin}/', key]) or '').strip()


def prepare():
    """Once per account (and when Eduka's defaults change): the plugins of a
    usable desktop when only "core" is on, and no keys that clash with
    Eduka-Desktop. Settings changed later in CompizConfig stay."""
    try:
        done = json.loads(STATE.read_text(encoding='utf-8')).get('defaults', 0)
    except (OSError, ValueError, AttributeError):
        done = 0
    if done >= DEFAULTS_VERSION or not shutil.which('gsettings'):
        return False
    schemas = Path('/usr/share/glib-2.0/schemas')
    if not (schemas/'org.compiz.core.gschema.xml').exists():
        return False
    active = _gsettings_get('core', 'active-plugins')
    if active in ("['core']", '@as []', ''):
        present = [p for p in PLUGINS if p == 'core' or any(Path(d, f'lib{p}.so').exists() for d in _plugin_dirs())]
        _gsettings('core', 'active-plugins', '[' + ', '.join(f"'{p}'" for p in present) + ']')
    for plugin, key, value in FREE_KEYS:
        if (schemas/f'org.compiz.{plugin}.gschema.xml').exists():
            _gsettings(plugin, key, f"'{value}'")
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps({'defaults': DEFAULTS_VERSION}) + '\n', encoding='utf-8')
    except OSError:
        pass
    return True


def _plugin_dirs():
    out = []
    for base in ('/usr/lib/x86_64-linux-gnu/compiz', '/usr/lib/aarch64-linux-gnu/compiz', '/usr/lib/i386-linux-gnu/compiz',
                 '/usr/lib/compiz', '/usr/local/lib/compiz', str(Path.home()/'.compiz-1'/'plugins')):
        if os.path.isdir(base):
            out.append(base)
    return out


def install_command():
    return ['sh', '-c', 'echo "Installing Compiz (3D window effects) ..."; echo; '
                        'sudo apt-get install compiz compiz-plugins compizconfig-settings-manager; echo; '
                        'printf "Press Enter to close this window. "; read _answer']


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['prepare']:
        prepare(); sys.exit(0)
    if sys.argv[1:] == ['check']:
        ok, why = can_run()
        if why:
            print(why, file=sys.stderr)
        sys.exit(0 if ok else 1)
    print('configured:', configured() or '?', '| installed:', [c for c, _n, _h in installed()])
    print('compiz:', can_run())
