#!/usr/bin/env python3
import os, sys, json, glob, configparser, subprocess, shlex, time, re, html, shutil
from pathlib import Path
from PyQt5.QtGui import QIcon, QPainterPath, QRegion
from PyQt5.QtCore import QSize, Qt, QObject, QEvent, QRectF
from PyQt5.QtWidgets import QMenu

VERSION = "0.9.19"
SETTINGS_REVISION = "0.9.6-transparency"
MAX_FAVORITES = 5
APP_ID = "eduka-desktop"
THEME_DEFAULT = "Eduka-Default-Theme"
THEME_LIQUID = "Liquid Glass"
THEME_DARK = "Edukasaun-Dark"
THEME_LOW = "Eduka-Low-Theme"          # after Yaru-remix: flat, opaque, no effects
THEME_TRANSPARENT = "Eduka-Transparan" # after Transparent-Shell-Theme: dark glass
THEMES = [THEME_DEFAULT, THEME_LOW, THEME_LIQUID, THEME_DARK, THEME_TRANSPARENT]
DARK_THEMES = (THEME_DARK, THEME_TRANSPARENT)
# Themes whose look needs a compositor, and what they fall back to without one.
GLASS_FALLBACK = {THEME_LIQUID: THEME_DEFAULT, THEME_TRANSPARENT: THEME_DARK}

# Edukasaun-Dark: colors from the Orchis dark theme by vinceliuice
# (github.com/vinceliuice/Orchis-theme, GPL-3.0): grey 900/800 surfaces,
# white text at 87 %/60 % and the Orchis teal-300/400 accent.
DARK = {
    'base': (33, 33, 33),        # Orchis grey-900 #212121
    'surface': (44, 44, 44),     # Orchis dark window background
    'card': (56, 56, 56),
    'raised': (66, 66, 66),      # Orchis grey-800 #424242
    'border': 'rgba(255,255,255,30)',
    'text': 'rgba(255,255,255,222)',
    'text2': 'rgba(255,255,255,153)',
    'accent': '#4DB6AC',         # Orchis teal-300
    'accent_dark': '#26A69A',    # Orchis teal-400
}
# Internal registry/build name is Eduka-Desktop. The visible OS name stays "Edukasaun Desktop".
BASE_CONFIG = Path.home()/".config"/"eduka-desktop"
LEGACY_BASE_CONFIG = Path.home()/".config"/"edukasaun-desktop"
PANEL_CONFIG_DIR = BASE_CONFIG/"panel"
MENU_CONFIG_DIR = BASE_CONFIG/"menu"
DESKTOP_CONFIG_DIR = BASE_CONFIG/"desktop"
RUNTIME_DIR = Path(os.environ.get('XDG_RUNTIME_DIR','/tmp'))/"eduka-desktop"
LEGACY_RUNTIME_DIR = Path(os.environ.get('XDG_RUNTIME_DIR','/tmp'))/"edukasaun-desktop"
CACHE_DIR = Path.home()/'.cache'/'eduka-desktop'
LEGACY_CACHE_DIR = Path.home()/'.cache'/'edukasaun-desktop'
APP_REGISTRY_PATH = CACHE_DIR/'app-registry.json'
STATE_REGISTRY_PATH = RUNTIME_DIR/'state-registry.json'
MENU_COMMAND_PATH = RUNTIME_DIR/'menu-command.json'
MENU_DAEMON_PID = RUNTIME_DIR/'menu-daemon.pid'
MENU_DAEMON_LOCK = RUNTIME_DIR/'menu-daemon.lock'
SETTINGS_LOCK = RUNTIME_DIR/'menu-settings.lock'
EUS_RUNTIME_DIR = Path(os.environ.get('XDG_RUNTIME_DIR','/tmp'))/'eduka-update-system'
EUS_PANEL_STATUS_PATH = EUS_RUNTIME_DIR/'panel-status.json'
EUS_ICON_DIR = Path('/usr/lib/EUS-ICONS')
ASSET_DIR = Path('/usr/share/edukasaun-desktop/assets')
START_ICON = str(ASSET_DIR/'StartMenu.png')
GENERIC_ICON = str(ASSET_DIR/'app-generic.png')

# --- X11 / Wayland session handling -------------------------------------
# Eduka-Panel and Eduka-Desktop manage windows through EWMH (wmctrl, xprop,
# xdotool). On a Wayland session those only see XWayland, so the Eduka
# components themselves run through XWayland. Applications they launch get
# the user's original platform back through child_env().
_ORIGINAL_QT_QPA = os.environ.get('QT_QPA_PLATFORM')

def session_type():
    """Return 'wayland' or 'x11' for the current login session."""
    value=(os.environ.get('XDG_SESSION_TYPE') or '').strip().lower()
    if value in ('x11', 'wayland'):
        return value
    return 'wayland' if os.environ.get('WAYLAND_DISPLAY') else 'x11'

if session_type() == 'wayland' and os.environ.get('DISPLAY') and not os.environ.get('EDUKA_NATIVE_WAYLAND'):
    os.environ['QT_QPA_PLATFORM']='xcb'

def child_env():
    """Environment for programs started by Eduka components."""
    env=os.environ.copy()
    if _ORIGINAL_QT_QPA is None:
        env.pop('QT_QPA_PLATFORM', None)
    else:
        env['QT_QPA_PLATFORM']=_ORIGINAL_QT_QPA
    return env

# --- Rounded context menus -------------------------------------------------
# A QMenu is a rectangular native window, so a border-radius in a stylesheet
# alone leaves sharp corners. With a translucent, frameless, shadowless
# window only the rounded stylesheet background is painted.
ACCENT = '#00a879'
MENU_QSS = """
QMenu{background:#fbfefc;color:#1f2d2a;border:1px solid rgba(0,120,90,70);border-radius:14px;padding:6px 5px;}
QMenu::item{background:transparent;padding:7px 28px 7px 10px;margin:1px 2px;border-radius:9px;color:#1f2d2a;}
QMenu::item:selected{background:#00a879;color:#ffffff;}
QMenu::item:disabled{color:#8a9b96;background:transparent;}
QMenu::icon{padding-left:6px;}
QMenu::separator{height:1px;background:#e1ece8;margin:5px 12px;}
QMenu::indicator{width:14px;height:14px;padding-left:6px;}
QMenu::right-arrow{width:8px;height:8px;margin-right:8px;}
"""

_COMPOSITOR = {'checked': 0.0, 'value': True}

def compositor_running(force=False):
    """True when a compositing manager runs (needed for translucent windows).

    Without one, X11 paints the transparent corners of rounded windows black.
    Checks the EWMH _NET_WM_CM_Sn selection owner through libX11; cached for
    30 seconds. Wayland always composites.
    """
    now=time.monotonic()
    if not force and _COMPOSITOR['checked'] and now - _COMPOSITOR['checked'] < 30:
        return _COMPOSITOR['value']
    value=True
    if session_type() != 'wayland' and os.environ.get('DISPLAY'):
        try:
            import ctypes, ctypes.util
            x11=ctypes.cdll.LoadLibrary(ctypes.util.find_library('X11') or 'libX11.so.6')
            x11.XOpenDisplay.restype=ctypes.c_void_p; x11.XOpenDisplay.argtypes=[ctypes.c_char_p]
            x11.XDefaultScreen.argtypes=[ctypes.c_void_p]
            x11.XInternAtom.restype=ctypes.c_ulong; x11.XInternAtom.argtypes=[ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
            x11.XGetSelectionOwner.restype=ctypes.c_ulong; x11.XGetSelectionOwner.argtypes=[ctypes.c_void_p, ctypes.c_ulong]
            x11.XCloseDisplay.argtypes=[ctypes.c_void_p]
            display=x11.XOpenDisplay(None)
            if display:
                atom=x11.XInternAtom(display, ('_NET_WM_CM_S%d' % x11.XDefaultScreen(display)).encode(), 0)
                value=x11.XGetSelectionOwner(display, atom) != 0
                x11.XCloseDisplay(display)
        except Exception:
            value=True
    _COMPOSITOR['checked']=now; _COMPOSITOR['value']=value
    return value

def ensure_compositor():
    """Start picom when no compositor runs (e.g. Openbox) in an Eduka session.

    Transparent Eduka windows need a compositor; without one X11 paints their
    transparent parts black. xfwm4 and KWin composite themselves, so picom is
    only started when nothing composites. xrender backend, no shadows, no
    fading: light and stable, also in VirtualBox.
    """
    if not in_eduka_session() or session_type() == 'wayland' or shutil.which('picom') is None:
        return False
    mode, args = _picom_mode()
    own=_own_picom()
    if mode == 'none':
        # Eduka-Low-Theme: no compositor at all (saves memory and CPU).
        if own:
            try: os.kill(own[0], 15)
            except Exception: pass
        return False
    if own and own[1] == mode:
        return True
    if own:
        # Theme or blur setting changed: restart the picom Eduka started.
        try: os.kill(own[0], 15)
        except Exception: pass
        for _ in range(20):
            if not compositor_running(force=True): break
            time.sleep(0.05)
    elif compositor_running(force=True):
        return False        # xfwm4, KWin or a user-started compositor
    ok=_start_picom(mode, args)
    if not ok and mode != 'xrender':
        # No working OpenGL (e.g. VirtualBox without 3D): glass without blur.
        fallback_mode, fallback_args = 'xrender', _PICOM_XRENDER
        ok=_start_picom(fallback_mode, fallback_args)
    return ok

PICOM_STATE = RUNTIME_DIR/'picom.json'
_PICOM_XRENDER = ['picom','--backend','xrender','--config','/dev/null']

def _picom_mode():
    """xrender (light, works everywhere) or glx with blur behind the glass of
    Eduka-Panel and Eduka-Desktop when Liquid Glass blur is switched on."""
    try:
        cfg=read_desktop_config()
        theme=normalize_theme_style(cfg.get('theme_style'))
        blur=theme in (THEME_LIQUID, THEME_TRANSPARENT) and bool(cfg.get('glass_blur', False))
    except Exception:
        theme=THEME_DEFAULT; blur=False
    if theme == THEME_LOW:
        return 'none', []
    if blur:
        return 'glx-blur', ['picom','--backend','glx','--config','/dev/null',
                            '--blur-method','dual_kawase','--blur-strength','4',
                            '--blur-background-exclude',"class_g != 'eduka-panel' && class_g != 'eduka-menu'"]
    return 'xrender', list(_PICOM_XRENDER)

def _own_picom():
    """(pid, mode) of the picom this session's Eduka started, if it runs."""
    try:
        data=json.loads(PICOM_STATE.read_text(encoding='utf-8'))
        pid=int(data.get('pid', 0))
        cmdline=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')[0]
        if pid > 0 and os.path.basename(cmdline.decode('utf-8', 'ignore')) == 'picom':
            return pid, data.get('mode', 'xrender')
    except Exception:
        pass
    return None

def _start_picom(mode, args):
    try:
        proc=subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, env=child_env())
    except Exception:
        return False
    for _ in range(30):
        time.sleep(0.05)
        if proc.poll() is not None:
            return False
        if compositor_running(force=True):
            break
    if proc.poll() is not None:
        return False
    try:
        write_json(PICOM_STATE, {'pid': proc.pid, 'mode': mode})
    except Exception:
        pass
    return True

def wait_for_compositor(timeout=2.5):
    """Before creating windows: start picom if needed and give the
    compositor (picom, or xfwm4/KWin still starting) a moment to appear, so
    the first window is already created transparent."""
    if session_type() == 'wayland' or not os.environ.get('DISPLAY'):
        return True
    if compositor_running(force=True):
        return True
    ensure_compositor()
    deadline=time.monotonic()+timeout
    while time.monotonic() < deadline:
        time.sleep(0.1)
        if compositor_running(force=True):
            return True
    return False

def watch_compositor(parent, before_restart=None, interval=4000, initial=None):
    """Restart this Eduka program when a compositor starts or stops.

    Whether a window may be transparent is fixed when it is created, so the
    cleanest switch between the transparent and the opaque look is a fresh
    start of the program (same PID, a fraction of a second).
    """
    from PyQt5.QtCore import QTimer
    # `initial` must be the value the window was created with; reading it
    # again here could already see a compositor that started meanwhile.
    state={'value': compositor_running(force=True) if initial is None else bool(initial)}
    def check():
        now=compositor_running(force=True)
        if now == state['value']:
            return
        if before_restart:
            try: before_restart()
            except Exception: pass
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
            state['value']=now
    timer=QTimer(parent); timer.timeout.connect(check); timer.start(interval)
    return timer

def effective_theme(value):
    """Liquid Glass only when a compositor can show it; otherwise the
    default theme, so the desktop never turns black."""
    theme=normalize_theme_style(value)
    if theme in GLASS_FALLBACK and not compositor_running():
        return GLASS_FALLBACK[theme]
    return theme

def liquid_glass_surface(alpha_scale=1.0, radius=18, rim=1):
    """Liquid Glass surface (0.9.16): soft milky glass, a gentle highlight
    along the top edge, an even body and a slightly brighter foot, with a
    thin light rim. After github.com/ryohsuke1231/liquid-glass, drawn with
    Qt stylesheets (blur comes from picom when enabled)."""
    k=max(0.4, min(1.6, float(alpha_scale)))
    a=lambda v: max(0, min(255, int(v*k)))
    return (f'background:qlineargradient(x1:0,y1:0,x2:0,y2:1,'
            f'stop:0 rgba(255,255,255,{a(150)}),stop:0.04 rgba(255,255,255,{a(118)}),'
            f'stop:0.5 rgba(246,250,252,{a(96)}),stop:0.96 rgba(240,247,250,{a(108)}),stop:1 rgba(255,255,255,{a(140)}));'
            f'border:{rim}px solid rgba(255,255,255,{a(150)});border-top:{rim}px solid rgba(255,255,255,{a(215)});'
            f'border-radius:{radius}px;')

def _old_liquid_glass_surface(alpha_scale=1.0, radius=18, rim=1):
    """Liquid Glass surface: clear glass with a bright specular band at the
    top, a soft base and a light rim (after the Liquid Glass look of
    github.com/ryohsuke1231/liquid-glass, rendered with Qt stylesheets)."""
    k=max(0.4, min(1.6, float(alpha_scale)))
    a=lambda v: max(0, min(255, int(v*k)))
    return (f'background:qlineargradient(x1:0,y1:0,x2:0,y2:1,'
            f'stop:0 rgba(255,255,255,{a(175)}),stop:0.07 rgba(255,255,255,{a(120)}),'
            f'stop:0.45 rgba(240,248,252,{a(92)}),stop:1 rgba(226,240,246,{a(122)}));'
            f'border:{rim}px solid rgba(255,255,255,{a(200)});border-bottom:{rim}px solid rgba(255,255,255,{a(110)});'
            f'border-radius:{radius}px;')

TOOLTIP_QSS = 'QToolTip{background:#fbfefc;color:#1f2d2a;border:1px solid rgba(0,120,90,70);padding:5px 8px;border-radius:8px;}'
TOOLTIP_QSS_DARK = 'QToolTip{background:#383838;color:#ffffff;border:1px solid rgba(255,255,255,40);padding:5px 8px;border-radius:8px;}'

def tooltip_qss():
    return TOOLTIP_QSS_DARK if is_dark_theme() else TOOLTIP_QSS

MENU_QSS_DARK = """
QMenu{background:#2c2c2c;color:#ffffff;border:1px solid rgba(255,255,255,40);border-radius:14px;padding:6px 5px;}
QMenu::item{background:transparent;padding:7px 28px 7px 10px;margin:1px 2px;border-radius:9px;color:rgba(255,255,255,222);}
QMenu::item:selected{background:#26A69A;color:#ffffff;}
QMenu::item:disabled{color:rgba(255,255,255,90);background:transparent;}
QMenu::icon{padding-left:6px;}
QMenu::separator{height:1px;background:rgba(255,255,255,30);margin:5px 12px;}
QMenu::indicator{width:14px;height:14px;padding-left:6px;}
QMenu::right-arrow{width:8px;height:8px;margin-right:8px;}
"""

# --- Arrows for spin boxes and combo boxes --------------------------------
# A stylesheet on QSpinBox/QComboBox replaces the native arrows; without an
# image they disappear. Small SVG chevrons are written once to the cache.
_ARROW_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12">'
              '<path d="{d}" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')
_ARROW_PATHS = {'up': 'M2.5 7.8 6 4.2 9.5 7.8', 'down': 'M2.5 4.2 6 7.8 9.5 4.2',
                'left': 'M7.8 2.5 4.2 6 7.8 9.5', 'right': 'M4.2 2.5 7.8 6 4.2 9.5'}

def arrow_icon_path(direction, color='#2d4a43'):
    folder=CACHE_DIR/'ui'
    path=folder/f"arrow-{direction}-{color.strip('#')}.svg"
    if not path.exists():
        try:
            folder.mkdir(parents=True, exist_ok=True)
            path.write_text(_ARROW_SVG.format(d=_ARROW_PATHS[direction], c=color), encoding='utf-8')
        except Exception:
            pass
    return str(path)

def arrow_qss(dark=None):
    """Up/down arrows for spin boxes and the drop-down arrow for combo boxes."""
    dark=is_dark_theme() if dark is None else dark
    color='#e0e0e0' if dark else '#2d4a43'
    hover='rgba(255,255,255,30)' if dark else 'rgba(0,168,121,40)'
    up=arrow_icon_path('up', color); down=arrow_icon_path('down', color)
    return (
        'QSpinBox,QDoubleSpinBox{padding-right:28px;}'
        'QSpinBox::up-button,QDoubleSpinBox::up-button{subcontrol-origin:border;subcontrol-position:top right;width:24px;border:0;border-top-right-radius:9px;background:transparent;}'
        'QSpinBox::down-button,QDoubleSpinBox::down-button{subcontrol-origin:border;subcontrol-position:bottom right;width:24px;border:0;border-bottom-right-radius:9px;background:transparent;}'
        f'QSpinBox::up-button:hover,QDoubleSpinBox::up-button:hover,QSpinBox::down-button:hover,QDoubleSpinBox::down-button:hover{{background:{hover};}}'
        f'QSpinBox::up-arrow,QDoubleSpinBox::up-arrow{{image:url("{up}");width:12px;height:12px;}}'
        f'QSpinBox::down-arrow,QDoubleSpinBox::down-arrow{{image:url("{down}");width:12px;height:12px;}}'
        'QComboBox{padding-right:28px;}'
        'QComboBox::drop-down{subcontrol-origin:padding;subcontrol-position:center right;width:26px;border:0;background:transparent;}'
        f'QComboBox::down-arrow{{image:url("{down}");width:12px;height:12px;}}'
        f'QComboBox::down-arrow:on{{image:url("{up}");}}'
    )

# --- Icon themes -------------------------------------------------------------
def list_icon_themes():
    """Installed icon themes that contain icons (cursor-only themes skipped)."""
    names={}
    for root in [Path.home()/'.local/share/icons', Path.home()/'.icons', Path('/usr/local/share/icons'), Path('/usr/share/icons')]:
        try:
            entries=list(root.iterdir())
        except Exception:
            continue
        for d in entries:
            index=d/'index.theme'
            if d.name in names or d.name.casefold() == 'default' or not index.is_file():
                continue
            try:
                text=index.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            if re.search(r'^\s*Directories\s*=\s*\S', text, re.M) is None:
                continue
            if re.search(r'^\s*Hidden\s*=\s*true', text, re.M | re.I):
                continue
            label=re.search(r'^\s*Name\s*=\s*(.+)$', text, re.M)
            names[d.name]=(label.group(1).strip() if label else d.name)
    return sorted(names.items(), key=lambda item: item[1].casefold())

def _set_ini_value(path, section, key, value):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    lines=path.read_text(encoding='utf-8', errors='ignore').splitlines() if path.exists() else []
    out=[]; in_section=False; done=False; seen_section=False
    for line in lines:
        stripped=line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            if in_section and not done:
                out.append(f'{key}={value}'); done=True
            in_section = stripped == f'[{section}]'
            seen_section = seen_section or in_section
        elif in_section and re.match(r'\s*%s\s*=' % re.escape(key), line):
            if not done:
                out.append(f'{key}={value}'); done=True
            continue
        out.append(line)
    if not done:
        if not seen_section:
            if out and out[-1].strip():
                out.append('')
            out.append(f'[{section}]')
        out.append(f'{key}={value}')
    tmp=path.with_suffix(path.suffix+'.eduka-tmp')
    tmp.write_text('\n'.join(out)+'\n', encoding='utf-8'); os.replace(tmp, path)

def _get_ini_value(path, section, key, default=None):
    try:
        lines=Path(path).read_text(encoding='utf-8', errors='ignore').splitlines()
    except Exception:
        return default
    in_section=False
    for line in lines:
        stripped=line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            in_section = stripped == f'[{section}]'
        elif in_section:
            m=re.match(r'\s*%s\s*=\s*(.*)$' % re.escape(key), line)
            if m:
                return m.group(1).strip()
    return default

def _remove_ini_value(path, section, key):
    path=Path(path)
    if not path.exists():
        return
    out=[]; in_section=False
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        stripped=line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            in_section = stripped == f'[{section}]'
        elif in_section and re.match(r'\s*%s\s*=' % re.escape(key), line):
            continue
        out.append(line)
    path.write_text('\n'.join(out)+'\n', encoding='utf-8')

DARK_PALETTE = {
    # LXQt's Qt platform plugin reads these from lxqt.conf [Palette].
    'window_color': '#2c2c2c', 'base_color': '#212121', 'highlight_color': '#26a69a',
    'window_text_color': '#ffffff', 'text_color': '#ffffff', 'highlighted_text_color': '#ffffff',
    'link_color': '#4db6ac', 'link_visited_color': '#80cbc4',
}
LOW_PALETTE = {
    # Yaru-remix colors: porcelain surfaces, jet text, blue accent.
    'window_color': '#f7f7f7', 'base_color': '#ffffff', 'highlight_color': '#315bef',
    'window_text_color': '#3d3d3d', 'text_color': '#3d3d3d', 'highlighted_text_color': '#ffffff',
    'link_color': '#315bef', 'link_visited_color': '#5d5d5d',
}
THEME_BACKUP = BASE_CONFIG/'desktop-theme-backup.json'
DESKTOP_DARK_THEME = 'Edukasaun-Dark'
# Eduka theme -> (GTK theme, prefer dark, Qt palette, window border theme)
SYSTEM_THEMES = {
    THEME_DARK: ('Edukasaun-Dark', True, DARK_PALETTE, 'Edukasaun-Dark'),
    THEME_TRANSPARENT: ('Edukasaun-Dark', True, DARK_PALETTE, 'Eduka-Transparan'),
    THEME_LOW: ('Eduka-Low', False, LOW_PALETTE, 'Eduka-Low'),
}

def _home(*parts):
    return Path.home().joinpath(*parts)

def _openbox_rc():
    for name in ('lxqt-rc.xml', 'rc.xml'):
        path=_home('.config','openbox',name)
        if path.exists():
            return path
    return None

def _openbox_theme(path):
    try:
        m=re.search(r'<theme>.*?<name>([^<]*)</name>', path.read_text(encoding='utf-8', errors='ignore'), re.S)
        return m.group(1).strip() if m else None
    except Exception:
        return None

def _set_openbox_theme(path, name):
    try:
        text=path.read_text(encoding='utf-8', errors='ignore')
        new=re.sub(r'(<theme>.*?<name>)[^<]*(</name>)', lambda m: m.group(1)+name+m.group(2), text, count=1, flags=re.S)
        if new != text:
            path.write_text(new, encoding='utf-8')
        if shutil.which('openbox'):
            safe_popen(['openbox','--reconfigure'])
    except Exception:
        pass

def _xfwm4_theme():
    if shutil.which('xfconf-query') is None:
        return None
    try:
        out=subprocess.run(['xfconf-query','-c','xfwm4','-p','/general/theme'], capture_output=True, text=True, timeout=2)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except Exception:
        return None

def _xfwm4_get(prop):
    if shutil.which('xfconf-query') is None:
        return None
    try:
        out=subprocess.run(['xfconf-query','-c','xfwm4','-p',prop], capture_output=True, text=True, timeout=2)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except Exception:
        return None

def _xfwm4_set(prop, kind, value):
    if shutil.which('xfconf-query'):
        safe_popen(['xfconf-query','-c','xfwm4','-p',prop,'-n','-t',kind,'-s',str(value)])

def _set_xfwm4_theme(name):
    if shutil.which('xfconf-query'):
        safe_popen(['xfconf-query','-c','xfwm4','-p','/general/theme','-s',name])

def apply_desktop_theme(theme=None):
    """Make the whole desktop follow the Eduka theme.

    Edukasaun-Dark switches GTK applications (GTK 2/3/4), Qt applications
    (LXQt palette) and the window borders (xfwm4 or Openbox) to the bundled
    Edukasaun-Dark theme (Orchis dark). The user's previous choices are saved
    first and restored when another Eduka theme is chosen.
    """
    theme=normalize_theme_style(theme if theme is not None else read_desktop_config().get('theme_style'))
    lxqt=_home('.config','lxqt','lxqt.conf')
    gtk3=_home('.config','gtk-3.0','settings.ini'); gtk4=_home('.config','gtk-4.0','settings.ini')
    gtk2=_home('.gtkrc-2.0')
    if theme in SYSTEM_THEMES:
        gtk_name, prefer_dark, palette, wm_name = SYSTEM_THEMES[theme]
        if not THEME_BACKUP.exists():
            ob=_openbox_rc()
            backup={
                'gtk3_theme': _get_ini_value(gtk3, 'Settings', 'gtk-theme-name'),
                'gtk3_dark': _get_ini_value(gtk3, 'Settings', 'gtk-application-prefer-dark-theme'),
                'gtk4_theme': _get_ini_value(gtk4, 'Settings', 'gtk-theme-name'),
                'gtk4_dark': _get_ini_value(gtk4, 'Settings', 'gtk-application-prefer-dark-theme'),
                'gtk2': gtk2.read_text(encoding='utf-8', errors='ignore') if gtk2.exists() else None,
                'palette': {k: _get_ini_value(lxqt, 'Palette', k) for k in DARK_PALETTE},
                'openbox': _openbox_theme(ob) if ob else None,
                'xfwm4': _xfwm4_theme(),
                'xfwm4_compositing': _xfwm4_get('/general/use_compositing'),
            }
            write_json(THEME_BACKUP, backup)
        for path in (gtk3, gtk4):
            _set_ini_value(path, 'Settings', 'gtk-theme-name', gtk_name)
            _set_ini_value(path, 'Settings', 'gtk-application-prefer-dark-theme', 'true' if prefer_dark else 'false')
        lines=[l for l in (gtk2.read_text(encoding='utf-8', errors='ignore').splitlines() if gtk2.exists() else []) if not l.strip().startswith('gtk-theme-name')]
        lines.append(f'gtk-theme-name="{gtk_name}"')
        gtk2.write_text('\n'.join(lines)+'\n', encoding='utf-8')
        for key, value in palette.items():
            _set_ini_value(lxqt, 'Palette', key, value)
        ob=_openbox_rc()
        if ob: _set_openbox_theme(ob, wm_name)
        if shutil.which('xfwm4') and _xfwm4_theme() is not None:
            _set_xfwm4_theme(wm_name)
            # The low theme also switches xfwm4's compositor off.
            _xfwm4_set('/general/use_compositing', 'bool', 'false' if theme == THEME_LOW else 'true')
        return True
    if not THEME_BACKUP.exists():
        return False
    try:
        backup=json.loads(THEME_BACKUP.read_text(encoding='utf-8'))
    except Exception:
        backup={}
    for path, tkey, dkey in ((gtk3, 'gtk3_theme', 'gtk3_dark'), (gtk4, 'gtk4_theme', 'gtk4_dark')):
        if backup.get(tkey): _set_ini_value(path, 'Settings', 'gtk-theme-name', backup[tkey])
        else: _remove_ini_value(path, 'Settings', 'gtk-theme-name')
        if backup.get(dkey): _set_ini_value(path, 'Settings', 'gtk-application-prefer-dark-theme', backup[dkey])
        else: _remove_ini_value(path, 'Settings', 'gtk-application-prefer-dark-theme')
    if backup.get('gtk2') is not None:
        gtk2.write_text(backup['gtk2'], encoding='utf-8')
    elif gtk2.exists():
        lines=[l for l in gtk2.read_text(encoding='utf-8', errors='ignore').splitlines() if not l.strip().startswith('gtk-theme-name')]
        gtk2.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    for key in DARK_PALETTE:
        old=(backup.get('palette') or {}).get(key)
        if old: _set_ini_value(lxqt, 'Palette', key, old)
        else: _remove_ini_value(lxqt, 'Palette', key)
    ob=_openbox_rc()
    if ob and backup.get('openbox'): _set_openbox_theme(ob, backup['openbox'])
    if backup.get('xfwm4'): _set_xfwm4_theme(backup['xfwm4'])
    if backup.get('xfwm4_compositing'): _xfwm4_set('/general/use_compositing', 'bool', backup['xfwm4_compositing'])
    try: THEME_BACKUP.unlink()
    except Exception: pass
    return True

# ---------------------------------------------------------------------------
# Languages. Eduka follows the system language chosen at boot (live) or by
# the installer (locales, LANG). Tetun has no system language pack yet, so
# Eduka carries its own Tetun translation; it can be chosen in Eduka-Settings.
# Catalogs: /usr/share/edukasaun-desktop/i18n/<lang>.json {"English": "..."}.
# ---------------------------------------------------------------------------
LANGUAGES = [('system', 'System language'), ('tet', 'Tetun (Tetum)')]
I18N_DIRS = [Path('/usr/share/edukasaun-desktop/i18n'),
             Path(__file__).resolve().parents[2]/'share'/'edukasaun-desktop'/'i18n']
CTX = '\x04'      # 'context\x04English' for words that need two translations

STRINGS = {
    'morning': 'Good morning', 'midday': 'midday\x04Good afternoon', 'afternoon': 'Good afternoon',
    'evening': 'Good evening', 'net_off': 'Network not connected', 'net_wifi': 'Connected to Wi-Fi',
    'net_lan': 'Connected by cable (Ethernet)', 'offline': 'Offline', 'lock': 'Lock', 'logout': 'Log Out',
    'restart': 'Restart', 'shutdown': 'Shut Down', 'dnd': 'Do Not Disturb', 'no_notif': 'No new notifications',
}

def system_language():
    """Language of the session: 'pt_BR', 'pt', 'id', 'zh_CN', ... or 'en'."""
    for var in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
        value=os.environ.get(var, '')
        for part in value.split(':'):
            first=part.split('.')[0].split('@')[0]
            # 'tet' in LANGUAGE comes from the Tetun choice itself, not the system.
            if first and first not in ('C', 'POSIX', 'tet'):
                return first
    return 'en'

_LANG_CACHE={'stamp': None, 'lang': 'en'}

def ui_language():
    """'tet' when Tetun is chosen in Eduka-Settings, otherwise the system language."""
    try:
        st=menu_config_path().stat().st_mtime_ns
    except Exception:
        st=None
    if _LANG_CACHE['stamp'] != st or _LANG_CACHE['stamp'] is None:
        try:
            choice=str(read_menu_config().get('language', 'system') or 'system')
        except Exception:
            choice='system'
        # Tetun is chosen in Eduka-Settings or on the login screen.
        login_tet=os.environ.get('EDUKA_LOGIN_LANGUAGE') == 'tet'
        _LANG_CACHE['lang']='tet' if choice == 'tet' or login_tet else system_language()
        _LANG_CACHE['stamp']=st if st is not None else time.time()
    return _LANG_CACHE['lang']

_CATALOGS={}

def _catalog(lang=None):
    lang=lang or ui_language()
    if lang in _CATALOGS:
        return _CATALOGS[lang]
    data={}; patterns=[]
    names=[]
    base=lang.split('_')[0]
    if base != lang: names.append(base)
    names.append(lang)
    if lang == 'tet': names=['tet']
    for name in names:
        for d in I18N_DIRS:
            path=d/f'{name}.json'
            if path.is_file():
                try:
                    data.update(json.loads(path.read_text(encoding='utf-8')))
                except Exception:
                    pass
                break
    for key, value in data.items():
        if '{' in key:
            rx='^'+re.sub(r'\\\{(\w+)\\\}', lambda m: f'(?P<{m.group(1)}>.+?)', re.escape(key))+'$'
            try: patterns.append((re.compile(rx, re.S), value))
            except re.error: pass
    _CATALOGS[lang]=(data, patterns)
    return _CATALOGS[lang]

_RECORD=os.environ.get('EDUKA_I18N_RECORD')

def _(text, lang=None):
    """Translate an English interface text into the interface language.
    Spaces around the text, a trailing ':' and '&&' are kept as they are."""
    if not isinstance(text, str) or not text.strip():
        return text
    lang=lang or ui_language()
    m=re.match(r'^(\s*)(.*?)(:?)(\s*)$', text, re.S)
    lead, core, colon, trail=m.groups()
    core_key=core.replace('&&', '&')
    if lang.startswith('en') and not _RECORD:
        return text.split(CTX, 1)[-1]
    data, patterns=_catalog(lang)
    out=data.get(core_key)
    if out is None and colon:
        out=data.get(core_key+':')
        if out is not None: colon=''
    if out is None:
        for rx, value in patterns:
            mm=rx.match(core_key)
            if mm:
                try: out=value.format(**{k: _(v, lang) for k, v in mm.groupdict().items()})
                except Exception: out=None
                break
    if out is None:
        if _RECORD and core_key.strip() and not core_key.startswith(('/', 'http')):
            try:
                with open(_RECORD, 'a', encoding='utf-8') as f: f.write(json.dumps(core_key)+'\n')
            except Exception:
                pass
        return text.split(CTX, 1)[-1] if CTX in text else text
    if '&' in core and '&&' in core: out=out.replace('&', '&&')
    return lead+out+colon+trail

def tr(key, lang=None):
    return _(STRINGS.get(key, key), lang)

def greeting_text(hour=None, lang=None):
    """Selamat pagi / siang / sore / malam, Bondia / Botarde / Bonoite, ..."""
    import datetime
    hour=datetime.datetime.now().hour if hour is None else int(hour)
    if 4 <= hour < 11: key='morning'
    elif 11 <= hour < 15: key='midday'
    elif 15 <= hour < 18: key='afternoon'
    else: key='evening'
    return tr(key, lang)

def translate_tree(root):
    """Translate texts set in constructors (QLabel('...'), QPushButton('...'))
    of a window and its children. Later setText() calls are translated by
    install_translations()."""
    if ui_language().startswith('en') and not _RECORD:
        return root
    from PyQt5.QtWidgets import QWidget, QLabel, QAbstractButton, QLineEdit
    widgets=[root]+root.findChildren(QWidget)
    for w in widgets:
        try:
            if isinstance(w, (QLabel, QAbstractButton)) and not w.property('eduka_tr'):
                t=w.text()
                if t: _ORIG['label'](w, _(t)) if isinstance(w, QLabel) else _ORIG['button'](w, _(t))
                w.setProperty('eduka_tr', True)
            if isinstance(w, QLineEdit) and w.placeholderText():
                _ORIG['placeholder'](w, _(w.placeholderText()))
            if w.toolTip(): _ORIG['tooltip'](w, _(w.toolTip()))
            if w.isWindow() and w.windowTitle(): _ORIG['title'](w, _(w.windowTitle()))
        except Exception:
            pass
    return root

_ORIG={}

def install_translations(app=None):
    """Translate texts the Eduka programs set at run time. Only exact
    interface texts from the catalogs change; names, titles and paths stay."""
    from PyQt5.QtWidgets import QLabel, QAbstractButton, QWidget, QLineEdit, QMenu, QMessageBox, QAction
    round_tooltips(app)
    if _ORIG:
        return
    _ORIG.update(label=QLabel.setText, button=QAbstractButton.setText, tooltip=QWidget.setToolTip,
                 title=QWidget.setWindowTitle, placeholder=QLineEdit.setPlaceholderText,
                 add_action=QMenu.addAction, add_menu=QMenu.addMenu, action_text=QAction.setText)
    if ui_language().startswith('en') and not _RECORD:
        return
    if ui_language() == 'tet':
        # Dates in Timor-Leste are written with the Portuguese month names.
        from PyQt5.QtCore import QLocale
        QLocale.setDefault(QLocale(QLocale.Portuguese, QLocale.Portugal))
    QLabel.setText=lambda self, t: _ORIG['label'](self, _(t))
    QAbstractButton.setText=lambda self, t: _ORIG['button'](self, _(t))
    QWidget.setToolTip=lambda self, t: _ORIG['tooltip'](self, _(t))
    QWidget.setWindowTitle=lambda self, t: _ORIG['title'](self, _(t))
    QLineEdit.setPlaceholderText=lambda self, t: _ORIG['placeholder'](self, _(t))
    QAction.setText=lambda self, t: _ORIG['action_text'](self, _(t))
    def _first_str(args):
        args=list(args)
        for i, a in enumerate(args):
            if isinstance(a, str):
                args[i]=_(a); break
        return args
    # Widgets made later with a text, e.g. QLabel('No applications found').
    from PyQt5.QtWidgets import QPushButton, QCheckBox, QRadioButton, QGroupBox
    for cls in (QLabel, QPushButton, QCheckBox, QRadioButton, QGroupBox, QMenu):
        def init(self, *a, _o=cls.__init__, **k):
            _o(self, *_first_str(a), **k)
        cls.__init__=init
    QMenu.addAction=lambda self, *a: _ORIG['add_action'](self, *_first_str(a))
    QMenu.addMenu=lambda self, *a: _ORIG['add_menu'](self, *_first_str(a))
    for name in ('question', 'warning', 'information', 'critical'):
        orig=getattr(QMessageBox, name)
        def wrapped(parent, title, text, *rest, _o=orig):
            return _o(parent, _(title), _(text), *rest)
        setattr(QMessageBox, name, staticmethod(wrapped))
    try:
        from PyQt5.QtCore import QTranslator, QLibraryInfo, QLocale
        if app is not None and not ui_language().startswith('tet'):
            t=QTranslator(app)
            if t.load(QLocale(system_language()), 'qtbase', '_', QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
                app.installTranslator(t)
    except Exception:
        pass

def user_display_name():
    try:
        import pwd
        entry=pwd.getpwuid(os.getuid())
        name=(entry.pw_gecos.split(',')[0] or entry.pw_name).strip()
    except Exception:
        name=os.environ.get('USER', '')
    return name.split()[0].capitalize() if name else ''

CLOCK_STYLES = ('digital', 'analog', 'led')
LED_COLORS = [('#ff3b30', 'Red'), ('#00e676', 'Green'), ('#2196f3', 'Blue'), ('#ffb300', 'Amber'),
              ('#00e5ff', 'Cyan'), ('#e040fb', 'Purple'), ('#ffffff', 'White')]

def clock_settings():
    cfg=read_panel_config()
    style=cfg.get('clock_style', 'digital'); fmt=cfg.get('clock_format', '24h')
    return (style if style in CLOCK_STYLES else 'digital'), (fmt if fmt in ('24h', '12h') else '24h')

def clock_options():
    """Every clock option: style, format, seconds, blinking colon, LED color."""
    cfg=read_panel_config(); style, fmt=clock_settings()
    # One color for every clock face; '' = the theme's own text color
    # (the LED face then uses green).
    color=str(cfg.get('clock_color', '') or '')
    if color and not re.fullmatch(r'#[0-9a-fA-F]{6}', color): color=''
    return {'style': style, 'format': fmt, 'seconds': bool(cfg.get('clock_seconds', False)),
            'blink': bool(cfg.get('clock_blink', False)), 'color': color, 'led_color': color or '#00e676'}

def format_clock(qtime, fmt=None, seconds=False, colon=':'):
    """'14:05' (24 hours) or '2:05 PM' (12 hours); colon=' ' hides the
    separators for a blinking clock (same width with a monospace font)."""
    fmt=fmt or clock_settings()[1]
    if fmt == '12h':
        text=qtime.toString('h:mm:ss AP' if seconds else 'h:mm AP')
    else:
        text=qtime.toString('HH:mm:ss' if seconds else 'HH:mm')
    return text.replace(':', colon) if colon != ':' else text

# ---------------------------------------------------------------- effects
EFFECT_HOVER = [('none', 'None'), ('wave', 'Wave (icon lifts)'), ('glow', 'Glow pulse'), ('slide', 'Slide in')]
EFFECT_LAUNCH = [('none', 'None'), ('bubble', 'Bubbles'), ('zoom-in', 'Zoom in'), ('zoom-out', 'Zoom out'),
                 ('ripple', 'Ripple'), ('bounce', 'Bounce'), ('confetti', 'Confetti'), ('fade', 'Fade')]

def system_memory_gib():
    try:
        for line in Path('/proc/meminfo').read_text(encoding='utf-8').splitlines():
            if line.startswith('MemTotal:'):
                return float(line.split()[1])/(1024*1024)
    except Exception:
        pass
    return 0.0

def effects_capability():
    """(memory GiB, CPU threads, allowed). Animated effects need 4 GB of
    memory and four CPU threads (shown as ~3.6 GiB by the kernel)."""
    mem=system_memory_gib(); threads=max(1, int(os.cpu_count() or 1))
    return mem, threads, mem >= 3.5 and threads >= 4

def effects_settings():
    """Effects in force: off unless the user enabled them, the computer is
    strong enough and the theme is not Eduka-Low-Theme."""
    cfg=read_desktop_config()
    on=bool(cfg.get('effects_enabled', False)) and effects_capability()[2] and current_theme() != THEME_LOW \
        and not cfg.get('visual_accessibility', False)
    hover=cfg.get('effect_hover', 'wave'); launch=cfg.get('effect_launch', 'bubble')
    return {'enabled': on, 'hover': hover if on else 'none', 'launch': launch if on else 'none'}

# ---------------------------------------------------------------- panel position
PANEL_POSITIONS = ('Bottom', 'Top', 'Left', 'Right')

def panel_position(cfg=None):
    value=str((cfg or read_panel_config()).get('position', 'Bottom')).capitalize()
    return value if value in PANEL_POSITIONS else 'Bottom'

# ---------------------------------------------------------------- cursor themes
def list_cursor_themes():
    """Installed mouse cursor themes (folders with a cursors/ directory)."""
    names={}
    for root in [Path.home()/'.local/share/icons', Path.home()/'.icons', Path('/usr/local/share/icons'), Path('/usr/share/icons')]:
        try:
            entries=list(root.iterdir())
        except Exception:
            continue
        for d in entries:
            if d.name in names or d.name == 'default' or not (d/'cursors').is_dir():
                continue
            label=d.name
            try:
                m=re.search(r'^\s*Name\s*=\s*(.+)$', (d/'index.theme').read_text(encoding='utf-8', errors='ignore'), re.M)
                if m: label=m.group(1).strip()
            except Exception:
                pass
            names[d.name]=label
    return sorted(names.items(), key=lambda item: item[1].casefold())

def current_cursor_theme():
    for value in (_get_ini_value(Path.home()/'.config/lxqt/session.conf', 'Mouse', 'cursor_theme'),
                  _get_ini_value(Path.home()/'.config/gtk-3.0/settings.ini', 'Settings', 'gtk-cursor-theme-name'),
                  _get_ini_value(Path.home()/'.icons/default/index.theme', 'Icon Theme', 'Inherits')):
        if value:
            return value
    return os.environ.get('XCURSOR_THEME', '')

def current_cursor_size():
    try:
        return int(_get_ini_value(Path.home()/'.config/lxqt/session.conf', 'Mouse', 'cursor_size') or 24)
    except ValueError:
        return 24

def set_cursor_theme(name, size=24):
    """Use a cursor theme everywhere: LXQt, GTK, X resources and the X
    default theme. New windows use it at once; the rest after logging in."""
    name=str(name or '').strip(); size=int(size or 24)
    if not name:
        return False
    try:
        _set_ini_value(Path.home()/'.config/lxqt/session.conf', 'Mouse', 'cursor_theme', name)
        _set_ini_value(Path.home()/'.config/lxqt/session.conf', 'Mouse', 'cursor_size', str(size))
        for gtk in ('gtk-3.0', 'gtk-4.0'):
            _set_ini_value(Path.home()/'.config'/gtk/'settings.ini', 'Settings', 'gtk-cursor-theme-name', name)
            _set_ini_value(Path.home()/'.config'/gtk/'settings.ini', 'Settings', 'gtk-cursor-theme-size', str(size))
        gtk2=Path.home()/'.gtkrc-2.0'
        lines=[l for l in (gtk2.read_text(encoding='utf-8', errors='ignore').splitlines() if gtk2.exists() else []) if not l.strip().startswith(('gtk-cursor-theme-name', 'gtk-cursor-theme-size'))]
        lines+= [f'gtk-cursor-theme-name="{name}"', f'gtk-cursor-theme-size={size}']
        gtk2.write_text('\n'.join(lines)+'\n', encoding='utf-8')
        default=Path.home()/'.icons/default/index.theme'
        default.parent.mkdir(parents=True, exist_ok=True)
        default.write_text(f'[Icon Theme]\nName=Default\nComment=Default cursor theme (Eduka-Settings)\nInherits={name}\n', encoding='utf-8')
        xres=Path.home()/'.Xresources'
        lines=[l for l in (xres.read_text(encoding='utf-8', errors='ignore').splitlines() if xres.exists() else []) if not l.strip().startswith(('Xcursor.theme', 'Xcursor.size'))]
        lines+= [f'Xcursor.theme: {name}', f'Xcursor.size: {size}']
        xres.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    except Exception:
        return False
    if os.environ.get('DISPLAY'):
        if shutil.which('xrdb'):
            try:
                subprocess.run(['xrdb', '-merge', str(Path.home()/'.Xresources')], timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        if shutil.which('xsetroot'):
            env=dict(child_env(), XCURSOR_THEME=name, XCURSOR_SIZE=str(size))
            try:
                subprocess.Popen(['xsetroot', '-cursor_name', 'left_ptr'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
    return True

def set_icon_theme(name):
    """Use an icon theme for the whole desktop: LXQt (file manager, dialogs),
    GTK applications and the Eduka components."""
    name=str(name or '').strip()
    if not name:
        return False
    try:
        _set_ini_value(Path.home()/'.config/lxqt/lxqt.conf', 'General', 'icon_theme', name)
        for gtk in ('gtk-3.0', 'gtk-4.0'):
            _set_ini_value(Path.home()/'.config'/gtk/'settings.ini', 'Settings', 'gtk-icon-theme-name', name)
    except Exception:
        return False
    icon_theme_setup(force=True); touch_reload()
    return True

THEME_ACCENTS = {THEME_DEFAULT: '#00a879', THEME_LOW: '#315bef', THEME_LIQUID: '#1e9bd7', THEME_DARK: '#26a69a', THEME_TRANSPARENT: '#6c6c6c'}

def theme_accent():
    return THEME_ACCENTS.get(current_theme(), '#00a879')

def round_combo(combo, radius=10):
    """Rounded drop-down list for a QComboBox (needs a compositor; without
    one the list stays square so no black corners appear)."""
    try:
        view=combo.view(); box=view.parentWidget()
        if box is None or not compositor_running():
            return combo
        box.setWindowFlags(box.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        box.setAttribute(Qt.WA_TranslucentBackground, True)
        box.setStyleSheet(f'background:transparent;border:0;')
        dark=is_dark_theme()
        view.setStyleSheet(f'QAbstractItemView{{border-radius:{radius}px;padding:4px;outline:0;'
                           f'background:{"#2f2f2f" if dark else "#ffffff"};color:{"#ffffff" if dark else "#1f2d2a"};'
                           f'border:1px solid {"rgba(255,255,255,40)" if dark else "rgba(0,120,90,60)"};}}'
                           f'QAbstractItemView::item{{min-height:26px;padding:2px 8px;border-radius:7px;}}'
                           f'QAbstractItemView::item:selected{{background:{theme_accent()};color:#ffffff;}}')
    except Exception:
        pass
    return combo

class _RoundMask(QObject):
    """Rounded window shape without a compositor: the corners are cut off
    with a mask, so no square corner shows behind a rounded style."""
    def __init__(self, radius, parent=None):
        super().__init__(parent); self.radius=radius
    def eventFilter(self, w, e):
        if e.type() in (QEvent.Resize, QEvent.Show) and w.isWindow():
            path=QPainterPath(); path.addRoundedRect(QRectF(w.rect()), self.radius, self.radius)
            w.setMask(QRegion(path.toFillPolygon().toPolygon()))
        return False

def round_window_shape(widget, radius=12):
    """Keep a frameless popup rounded on computers without a compositor."""
    f=_RoundMask(radius, widget); widget.installEventFilter(f)
    return widget

class _TooltipRounder(QObject):
    """Tooltips are separate windows (QTipLabel) with square corners."""
    def eventFilter(self, w, e):
        # A translucent QTipLabel loses its painted background, so the
        # corners are cut with a mask (QTipLabel gets no Polish event).
        if e.type() in (QEvent.Show, QEvent.Resize) and w.metaObject().className() == 'QTipLabel':
            path=QPainterPath(); path.addRoundedRect(QRectF(w.rect()), 8, 8)
            w.setMask(QRegion(path.toFillPolygon().toPolygon()))
        return False

def round_tooltips(app):
    if app is not None and not getattr(app, '_eduka_tooltips', None):
        app._eduka_tooltips=_TooltipRounder(app); app.installEventFilter(app._eduka_tooltips)

def fade_in(widget, ms=150):
    """Fade a window in. Timer steps instead of QPropertyAnimation: in
    Eduka-Panel the animation clock can stall while the status thread runs,
    which left popups at opacity 0 (invisible). Always ends fully opaque."""
    from PyQt5.QtCore import QTimer, QElapsedTimer
    old=getattr(widget, '_eduka_fade', None)
    if old is not None:
        old.stop()
    clock=QElapsedTimer(); clock.start()
    timer=QTimer(widget); timer.setInterval(16)
    def step():
        t=min(1.0, clock.elapsed()/float(max(1, ms)))
        widget.setWindowOpacity(1-(1-t)**3)
        if t >= 1.0:
            timer.stop(); widget.setWindowOpacity(1.0)
    timer.timeout.connect(step)
    widget._eduka_fade=timer
    widget.setWindowOpacity(0.0); timer.start()
    QTimer.singleShot(ms+120, lambda: (timer.stop(), widget.setWindowOpacity(1.0)))
    return timer

def round_menu(menu):
    """Give any QMenu (also Qt's built-in ones) smooth rounded corners.

    Without a compositor the menu stays an opaque window with a small radius,
    so no black corners appear.
    """
    qss=MENU_QSS_DARK if is_dark_theme() else MENU_QSS
    if compositor_running():
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground, True)
        menu.setStyleSheet(qss)
    else:
        menu.setStyleSheet(qss.replace('border-radius:14px', 'border-radius:10px'))
        if not menu.property('eduka_mask'):
            menu.setProperty('eduka_mask', True); round_window_shape(menu, 10)
    return menu

class RoundedMenu(QMenu):
    """QMenu whose submenus are rounded as well."""
    def __init__(self, *args):
        super().__init__(*args)
        round_menu(self)

    def addMenu(self, *args):
        if len(args) == 1 and isinstance(args[0], QMenu):
            round_menu(args[0])
            return super().addMenu(args[0])
        if len(args) == 1:
            icon, title = None, args[0]
        else:
            icon, title = args[0], args[1]
        sub=RoundedMenu(title, self)
        if icon is not None:
            sub.setIcon(icon)
        super().addMenu(sub)
        return sub

def rounded_text_context_menu(edit):
    """Replace a QLineEdit's square Cut/Copy/Paste menu with a rounded one."""
    edit.setContextMenuPolicy(Qt.CustomContextMenu)
    def show(pos, e=edit):
        menu=round_menu(e.createStandardContextMenu())
        menu.exec_(e.mapToGlobal(pos))
        menu.deleteLater()
    edit.customContextMenuRequested.connect(show)

DEFAULT_PANEL = {
    "height": 42,
    "width_percent": 96,
    "position": "Bottom",
    "transparency": 0.54,
    "icon_size": 24,
    "menu_label": "Edukasaun",
    "menu_icon": START_ICON,
    "menu_icon_size": 26,
    "menu_icon_keep_aspect": True,
    "show_menu_text": True,
    "taskbar_style": "Icon and Text",
    "taskbar_icon_size": 22,
    "autohide": False,
    "locked": True,
    "enable_shadows": False,
    "low_resource_mode": True,
    "theme_style": THEME_DEFAULT,
    "clock_style": "digital",
    "clock_format": "24h",
    "clock_seconds": False,
    "clock_blink": False,
    "clock_color": "",
    "notify_seconds": 7,
    "notify_history": True,
    "reserve_workarea": True,
    "force_window_above_panel": True,
    "taskbar_max_button_width": 175,
    "taskbar_min_button_width": 46
}
DEFAULT_MENU = {"mode": "Eduka-Desktop", "language": "system", "sddm_follow": True}
DEFAULT_DESKTOP = {"last_category": "Edukasaun", "layout": "Grid", "width_percent": 98, "height_percent": 92, "transparency": 0.51, "enable_shadows": False, "low_resource_mode": True, "theme_style": THEME_DEFAULT, "show_right_panel": True, "smooth_animations": False, "corner_radius": 24, "visual_accessibility": False, "hearing_accessibility": False, "orca_enabled": False, "glass_blur": False, "effects_enabled": False, "effect_hover": "wave", "effect_launch": "bubble"}

CATEGORY_ORDER = [
    ("All", "view-app-grid", []),
    ("Edukasaun", "applications-education", ["education", "science", "game"]),
    ("Accessories", "applications-accessories", ["utility", "accessory", "accessories"]),
    ("Graphics", "applications-graphics", ["graphics", "2dgraphics", "photography"]),
    ("Internet", "applications-internet", ["network", "webbrowser", "email", "chat", "instantmessaging", "browser"]),
    ("Office", "applications-office", ["office", "wordprocessor", "spreadsheet", "presentation"]),
    ("Programming", "applications-development", ["development", "programming", "ide"]),
    ("Sound & Video", "applications-multimedia", ["audio", "video", "audiovideo", "multimedia", "player"]),
    ("System Tools", "applications-system", ["system", "monitor", "emulator", "filesystem"]),
    ("Universal Access", "preferences-desktop-accessibility", ["accessibility", "universalaccess"]),
    ("Preferences", "preferences-system", ["settings", "desktopsettings", "hardwareSettings".lower()]),
]

# Strong category overrides for common Edukasaun OS apps. This prevents apps
# such as VLC/Audacious from appearing under Programming only because their
# desktop file includes broad or vendor-specific categories.
CATEGORY_NAME_OVERRIDES = {
    # Education / learning
    'gcompris': 'Edukasaun', 'kde education': 'Edukasaun', 'tux paint': 'Edukasaun',
    'kturtle': 'Edukasaun', 'kwordquiz': 'Edukasaun', 'marble': 'Edukasaun',
    'geogebra': 'Edukasaun', 'kstars': 'Edukasaun', 'kgeography': 'Edukasaun',
    'kalzium': 'Edukasaun', 'kbruch': 'Edukasaun', 'klettres': 'Edukasaun',
    'kblocks': 'Edukasaun', 'khangman': 'Edukasaun', 'knetwalk': 'Edukasaun',
    'ktuberling': 'Edukasaun', 'childsplay': 'Edukasaun', 'scratch': 'Edukasaun',
    'turbowarp': 'Edukasaun', 'abacus': 'Edukasaun', '2048': 'Edukasaun',
    'blinken': 'Edukasaun', 'fretboard': 'Edukasaun', 'goldendict': 'Edukasaun',
    'duolingo': 'Edukasaun', 'bovo': 'Edukasaun', 'kanagram': 'Edukasaun',
    # Multimedia
    'vlc': 'Sound & Video', 'audacious': 'Sound & Video', 'mpv': 'Sound & Video',
    'celluloid': 'Sound & Video', 'rhythmbox': 'Sound & Video', 'parole': 'Sound & Video',
    'sound': 'Sound & Video', 'pulse': 'Sound & Video', 'volume': 'Sound & Video',
    # Internet
    'firefox': 'Internet', 'chromium': 'Internet', 'google chrome': 'Internet',
    'thunderbird': 'Internet', 'telegram': 'Internet', 'whatsapp': 'Internet',
    # Graphics
    'gimp': 'Graphics', 'inkscape': 'Graphics', 'krita': 'Graphics', 'ristretto': 'Graphics',
    'shotwell': 'Graphics', 'kolourpaint': 'Graphics', 'colorflow': 'Graphics',
    # Office
    'libreoffice': 'Office', 'writer': 'Office', 'calc': 'Office', 'impress': 'Office',
    'feathernotes': 'Office', 'featherpad': 'Accessories',
    # Preferences/System
    'appearance': 'Preferences', 'brightness': 'Preferences', 'date and time': 'Preferences',
    'dimensions': 'Preferences', 'desktop': 'Preferences', 'qt5 configuration': 'Preferences',
    'fcitx': 'Preferences', 'printer': 'System Tools', 'monitor': 'System Tools',
}
CATEGORY_EXEC_OVERRIDES = {
    'vlc': 'Sound & Video', 'audacious': 'Sound & Video', 'mpv': 'Sound & Video',
    'celluloid': 'Sound & Video', 'parole': 'Sound & Video', 'pavucontrol-qt': 'Sound & Video',
    'firefox': 'Internet', 'chromium': 'Internet', 'google-chrome': 'Internet',
    'thunderbird': 'Internet', 'telegram-desktop': 'Internet', 'whatsapp-linux-app': 'Internet',
    'gimp': 'Graphics', 'inkscape': 'Graphics', 'krita': 'Graphics', 'kolourpaint': 'Graphics',
    'libreoffice': 'Office', 'featherpad': 'Accessories', 'feathernotes': 'Office',
    'qterminal': 'System Tools', 'pcmanfm-qt': 'System Tools', 'lxqt-config': 'Preferences',
    'nm-connection-editor': 'Preferences', 'blueman-manager': 'Preferences',
    'gcompris-qt': 'Edukasaun', 'tuxpaint': 'Edukasaun', 'turbowarp': 'Edukasaun',
    'pcmanfm-qt': 'System Tools', 'pcmanfm': 'System Tools',
    'org.pwmt.zathura': 'Office', 'evince': 'Office', 'atril': 'Office',
    'brasero': 'Sound & Video', 'k3b': 'Sound & Video',
}

DESKTOP_DIRS = [
    '/usr/share/applications', '/usr/local/share/applications',
    str(Path.home()/'.local/share/applications'),
    '/var/lib/snapd/desktop/applications',
    '/var/lib/flatpak/exports/share/applications',
    str(Path.home()/'.local/share/flatpak/exports/share/applications'),
]
HIDE_IDS = {
    'edukasaun-desktop.desktop','eduka-menu-settings.desktop','eduka-settings.desktop',
    'eduka-menu.desktop','eduka-panel.desktop','eduka-about.desktop',
    'edukasaun-desktop-menu-open.desktop','eduka-app-registry.desktop','eduka-app-cache.desktop',
    # LXQt pieces that Eduka-Desktop already provides (footer buttons, About,
    # Eduka-Panel). Eduka-Desktop only shows the LXQt tools it really needs.
    'lxqt-leave.desktop','lxqt-logout.desktop','lxqt-lockscreen.desktop','lxqt-reboot.desktop',
    'lxqt-shutdown.desktop','lxqt-suspend.desktop','lxqt-hibernate.desktop','lxqt-about.desktop',
    'lxqt-panel.desktop',
}
INTERNAL_EXEC_MARKERS = (
    'eduka-menu', 'eduka-panel', 'eduka-about', 'eduka-app-registry', 'eduka-app-cache',
    'edukasaun-desktop-menu-open', 'eduka-session-action'
)
INTERNAL_APP_NAMES = {'edukasaun desktop','eduka desktop','eduka-desktop','eduka menu','eduka-menu','eduka panel','eduka-panel'}

def ensure_dirs():
    # 0.8.0 alpha migration: keep user settings from old Edukasaun Desktop settings
    # but store all new runtime/config/cache data under the internal Eduka-Desktop name.
    try:
        if LEGACY_BASE_CONFIG.exists() and not BASE_CONFIG.exists():
            shutil.copytree(LEGACY_BASE_CONFIG, BASE_CONFIG)
    except Exception:
        pass
    try:
        if LEGACY_CACHE_DIR.exists() and not CACHE_DIR.exists():
            shutil.copytree(LEGACY_CACHE_DIR, CACHE_DIR)
    except Exception:
        pass
    for d in [BASE_CONFIG, PANEL_CONFIG_DIR, MENU_CONFIG_DIR, DESKTOP_CONFIG_DIR, RUNTIME_DIR, CACHE_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def read_json(path, default):
    ensure_dirs(); path=Path(path)
    if not path.exists(): write_json(path, default); return dict(default)
    try:
        with path.open(encoding='utf-8') as f: data=json.load(f)
        if not isinstance(data, dict): raise ValueError('bad json')
    except Exception:
        data=dict(default); write_json(path,data)
    merged=dict(default); merged.update(data); return merged

def write_json(path, data):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w',encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(tmp, path)

def panel_config_path(): return PANEL_CONFIG_DIR/'settings.json'
def menu_config_path(): return MENU_CONFIG_DIR/'settings.json'
def desktop_config_path(): return DESKTOP_CONFIG_DIR/'settings.json'
def normalize_theme_style(value):
    """Map stored or retired theme names to Eduka-Default-Theme, Liquid Glass or Edukasaun-Dark."""
    text=str(value or '').strip().casefold()
    for theme in THEMES:
        if text == theme.casefold():
            return theme
    return THEME_DEFAULT

def current_theme():
    """Theme in effect for Eduka components right now."""
    try:
        return effective_theme(read_desktop_config().get('theme_style'))
    except Exception:
        return THEME_DEFAULT

def is_dark_theme():
    return current_theme() in DARK_THEMES

def is_low_theme():
    return current_theme() == THEME_LOW
def read_panel_config():
    data=read_json(panel_config_path(), DEFAULT_PANEL)
    changed=False
    if data.get('_settings_revision') != SETTINGS_REVISION:
        data['transparency']=0.54
        data['_settings_revision']=SETTINGS_REVISION
        changed=True
    theme=normalize_theme_style(data.get('theme_style'))
    if data.get('theme_style') != theme:
        data['theme_style']=theme
        changed=True
    if changed:
        write_json(panel_config_path(), data)
    return data
def read_menu_config(): return read_json(menu_config_path(), DEFAULT_MENU)
def read_desktop_config():
    data=read_json(desktop_config_path(), DEFAULT_DESKTOP)
    changed=False
    if data.get('_settings_revision') != SETTINGS_REVISION:
        data['transparency']=0.51
        data['_settings_revision']=SETTINGS_REVISION
        changed=True
    theme=normalize_theme_style(data.get('theme_style'))
    if data.get('theme_style') != theme:
        data['theme_style']=theme
        changed=True
    if changed:
        write_json(desktop_config_path(), data)
    return data
def save_panel_config(c):
    current=read_panel_config(); current.update(c); current['theme_style']=normalize_theme_style(current.get('theme_style')); write_json(panel_config_path(), current); touch_reload()
def save_menu_config(c):
    current=read_menu_config(); current.update(c); write_json(menu_config_path(), current); touch_reload()
def save_desktop_config(c):
    current=read_desktop_config(); current.update(c); current['theme_style']=normalize_theme_style(current.get('theme_style')); write_json(desktop_config_path(), current); touch_reload()
def touch_reload(): ensure_dirs(); (RUNTIME_DIR/'reload').write_text(str(time.time()))

def in_eduka_session():
    """True inside an Eduka-Desktop login session (set by eduka-desktop-session)."""
    return bool(os.environ.get('EDUKA_DESKTOP_SESSION'))

def stop_lxqt_module_in_eduka_session(module, process):
    """Ask lxqt-session to stop one of its modules (Eduka-Desktop sessions only)."""
    if not in_eduka_session() or shutil.which('pgrep') is None:
        return False
    try:
        if subprocess.run(['pgrep','-x',process], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2).returncode != 0:
            return False
    except Exception:
        return False
    if shutil.which('dbus-send'):
        return safe_popen(['dbus-send','--session','--type=method_call','--dest=org.lxqt.session','/LXQtSession','org.lxqt.session.stopModule',f'string:{module}'])
    if shutil.which('qdbus'):
        return safe_popen(['qdbus','org.lxqt.session','/LXQtSession','org.lxqt.session.stopModule',module])
    return False

LXQT_NOTIFY_OVERRIDE = '[Desktop Entry]\nType=Application\nName=LXQt Notification Daemon\nExec=lxqt-notificationd\n' \
    'Hidden=true\nComment=Disabled by Edukasaun Desktop: Eduka-Panel shows notifications.\n'

def stop_lxqt_notifications_in_eduka_session():
    """Eduka-Panel shows all notifications itself in Eduka-Desktop sessions:
    lxqt-session stops its daemon, it is hidden from future logins (user
    autostart override) and, if it still runs, it is ended."""
    if not in_eduka_session():
        return False
    try:
        override=Path.home()/'.config/autostart/lxqt-notifications.desktop'
        if not override.exists():
            override.parent.mkdir(parents=True, exist_ok=True); override.write_text(LXQT_NOTIFY_OVERRIDE, encoding='utf-8')
    except Exception:
        pass
    stop_lxqt_module_in_eduka_session('lxqt-notifications.desktop', 'lxqt-notificationd')
    if shutil.which('pkill'):
        try:
            subprocess.run(['pkill','-u',str(os.getuid()),'-x','lxqt-notificationd'], timeout=2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    return True

def stop_lxqt_panel_in_eduka_session():
    """Stop lxqt-panel through lxqt-session, only in Eduka-Desktop sessions.

    Eduka-Panel replaces lxqt-panel. Asking lxqt-session (instead of killing
    the process) keeps it from restarting the panel, and a plain LXQt session
    is never touched.
    """
    if not in_eduka_session() or shutil.which('pgrep') is None:
        return False
    try:
        running=subprocess.run(['pgrep','-x','lxqt-panel'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2).returncode == 0
    except Exception:
        return False
    if not running:
        return False
    if shutil.which('dbus-send'):
        cmd=['dbus-send','--session','--type=method_call','--dest=org.lxqt.session','/LXQtSession','org.lxqt.session.stopModule','string:lxqt-panel.desktop']
    elif shutil.which('qdbus'):
        cmd=['qdbus','org.lxqt.session','/LXQtSession','org.lxqt.session.stopModule','lxqt-panel.desktop']
    else:
        return False
    return safe_popen(cmd)

def orca_available():
    """Return True when the Orca executable is available for this session."""
    return shutil.which('orca') is not None

def orca_autostart_path():
    return Path.home()/'.config'/'autostart'/'eduka-orca.desktop'

def configure_orca(enabled):
    """Enable or disable Orca for the current user and future LXQt sessions.

    Orca is launched with its documented replacement and speech options.  The
    autostart entry is user-scoped, so system-wide desktop settings and other
    users are never changed.
    """
    enabled=bool(enabled)
    entry=orca_autostart_path()
    if enabled:
        if not orca_available():
            return False, 'Orca is not installed. Install the orca and speech-dispatcher-espeak-ng packages.'
        try:
            entry.parent.mkdir(parents=True, exist_ok=True)
            tmp=entry.with_suffix('.desktop.tmp')
            tmp.write_text(
                '[Desktop Entry]\n'
                'Type=Application\n'
                'Name=Orca Screen Reader for Eduka-Desktop\n'
                'Comment=Spoken navigation for Eduka-Desktop and LXQt\n'
                'TryExec=orca\n'
                'Exec=orca --replace --enable=speech\n'
                'OnlyShowIn=LXQt;LXDE;\n'
                'X-GNOME-Autostart-enabled=true\n'
                'NoDisplay=true\n',
                encoding='utf-8'
            )
            os.replace(tmp, entry)
        except Exception as exc:
            return False, f'Could not create Orca session autostart: {exc}'
        if shutil.which('gsettings'):
            safe_popen(['gsettings','set','org.gnome.desktop.a11y.applications','screen-reader-enabled','true'])
        if not safe_popen(['orca','--replace','--enable=speech']):
            try:
                entry.unlink(missing_ok=True)
            except Exception:
                pass
            if shutil.which('gsettings'):
                safe_popen(['gsettings','set','org.gnome.desktop.a11y.applications','screen-reader-enabled','false'])
            return False, 'Orca is installed but could not be started in this desktop session.'
        registry_update('accessibility', {'orca_enabled': True, 'version': VERSION})
        return True, 'Orca screen reader is enabled now and at the next LXQt login.'

    try:
        entry.unlink(missing_ok=True)
    except Exception:
        pass
    if shutil.which('gsettings'):
        safe_popen(['gsettings','set','org.gnome.desktop.a11y.applications','screen-reader-enabled','false'])
    if shutil.which('pkill'):
        safe_popen(['pkill','-TERM','-x','orca'])
    registry_update('accessibility', {'orca_enabled': False, 'version': VERSION})
    return True, 'Orca screen reader is disabled for Eduka-Desktop sessions.'


def menu_daemon_autostart_path():
    return Path.home()/'.config'/'autostart'/'eduka-menu-daemon.desktop'

def menu_daemon_autostart_enabled():
    """False only when the user placed a Hidden=true override for the daemon."""
    try:
        text=menu_daemon_autostart_path().read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return True
    return not re.search(r'^\s*Hidden\s*=\s*true\s*$', text, re.M | re.I)

def set_menu_daemon_autostart(enabled):
    """Enable or disable the Eduka-Desktop daemon for this user only.

    The system entry in /etc/xdg/autostart stays untouched; XDG autostart lets a
    same-named file in ~/.config/autostart override it.
    """
    entry=menu_daemon_autostart_path()
    try:
        if enabled:
            entry.unlink(missing_ok=True)
        else:
            entry.parent.mkdir(parents=True, exist_ok=True)
            entry.write_text(
                '[Desktop Entry]\n'
                'Type=Application\n'
                'Name=Eduka Menu Fast Daemon\n'
                'Exec=eduka-menu --daemon\n'
                'Hidden=true\n',
                encoding='utf-8'
            )
        return True
    except OSError:
        return False


def registry_read():
    """Compatibility state reader.
    Lightweight runtime state/cache map under XDG_RUNTIME_DIR. It is not a
    Windows-style registry or plugin system; it only lets Eduka-Desktop,
    Eduka-Menu and Eduka-Panel exchange safe runtime status.
    """
    ensure_dirs()
    try:
        data=json.loads(STATE_REGISTRY_PATH.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def registry_update(section, values):
    ensure_dirs(); data=registry_read()
    sec=data.get(section, {}) if isinstance(data.get(section, {}), dict) else {}
    values=dict(values or {})
    # Eduka-Panel and Eduka-Desktop report state on short timers. Skip the disk
    # write when nothing changed so old laptops are not woken every second.
    if values and all(sec.get(k) == v for k, v in values.items() if k != 'updated_at'):
        return data
    sec.update(values); sec['updated_at']=time.time(); data[section]=sec
    try: write_json(STATE_REGISTRY_PATH, data)
    except Exception: pass
    return data

def send_menu_command(action='toggle'):
    ensure_dirs()
    payload={'action': action, 'time': time.time(), 'id': int(time.time()*1000)}
    try: write_json(MENU_COMMAND_PATH, payload); return True
    except Exception: return False

def _pid_alive(pid):
    try:
        os.kill(int(pid), 0); return True
    except Exception:
        return False

def menu_daemon_alive():
    ensure_dirs()
    try: return _pid_alive(MENU_DAEMON_PID.read_text().strip())
    except Exception: return False

def ensure_menu_daemon(show=False):
    ensure_dirs()
    if not menu_daemon_alive():
        safe_popen(['eduka-menu','--daemon'] + (['--show'] if show else []))
        return False
    return True

def _clean_theme_name(value):
    value = str(value or '').strip().strip('"').strip("'")
    if not value or value.lower() in ('true','false','1','0','theme'):
        return ''
    # LXQt/GTK files sometimes store comments after the value.
    value = value.split('#', 1)[0].strip().strip('"').strip("'")
    return value


def lxqt_appearance_files():
    """Files changed by LXQt Appearance Configuration and GTK icon settings.
    Eduka-Desktop and Eduka-Panel watch/read these so icon theme changes in
    LXQt Appearance are applied without using Eduka-specific blue fallback icons.
    """
    home = Path.home()
    return [
        home/'.config/lxqt/lxqt.conf',
        home/'.config/lxqt/session.conf',
        home/'.config/pcmanfm-qt/lxqt/settings.conf',
        home/'.config/gtk-3.0/settings.ini',
        home/'.config/gtk-4.0/settings.ini',
        home/'.gtkrc-2.0',
        Path('/etc/xdg/lxqt/lxqt.conf'),
    ]


def _read_theme_names_from_file(path):
    names=[]
    try:
        txt=Path(path).read_text(errors='ignore')
    except Exception:
        return names
    # LXQt keys seen in the wild: icon_theme, iconTheme, icon_theme_name.
    # GTK keys: gtk-icon-theme-name.
    keys=['icon_theme','iconTheme','icon_theme_name','IconThemeName','gtk-icon-theme-name','gtk_icon_theme_name']
    for key in keys:
        for m in re.finditer(r'^\s*%s\s*=\s*(.+?)\s*$' % re.escape(key), txt, re.M|re.I):
            n=_clean_theme_name(m.group(1))
            if n: names.append(n)
    # ~/.gtkrc-2.0 often uses: gtk-icon-theme-name="Papirus"
    for m in re.finditer(r'gtk-icon-theme-name\s*=\s*["\']?([^"\'\n]+)', txt, re.I):
        n=_clean_theme_name(m.group(1))
        if n: names.append(n)
    return names


def _theme_exists(name):
    if not name:
        return False
    for root in [Path('/usr/share/icons'), Path('/usr/local/share/icons'), Path.home()/'.icons', Path.home()/'.local/share/icons']:
        if (root/name).exists():
            return True
    return False


def _theme_candidates():
    names=[]
    # 1) LXQt Appearance Configuration has priority.
    for pth in lxqt_appearance_files():
        for n in _read_theme_names_from_file(pth):
            if n and n not in names:
                names.append(n)
    # 2) Environment and current Qt theme.
    for env in ['QT_ICON_THEME','GTK_ICON_THEME','XDG_CURRENT_DESKTOP']:
        n=_clean_theme_name(os.environ.get(env,''))
        if n and _theme_exists(n) and n not in names:
            names.append(n)
    current=QIcon.themeName()
    if current and current not in names:
        names.append(current)
    # 3) Defaults. Papirus is preferred when present, then common fallbacks.
    for n in ['Papirus', 'Papirus-Dark', 'Papirus-Light', 'breeze', 'Adwaita', 'Humanity', 'hicolor']:
        if n not in names:
            names.append(n)
    out=[]
    for n in names:
        n=_clean_theme_name(n)
        if n and n not in out:
            out.append(n)
    return out


def current_icon_theme_name():
    for n in _theme_candidates():
        if _theme_exists(n) or n == 'hicolor':
            return n
    return QIcon.themeName() or 'hicolor'


_ICON_THEME_LAST_CHECK = 0.0
_ICON_THEME_LAST_SELECTED = ''

def icon_theme_setup(force=False):
    global _ICON_THEME_LAST_CHECK, _ICON_THEME_LAST_SELECTED
    now=time.monotonic()
    # get_icon() is called for every application tile. Re-reading every LXQt/
    # GTK theme file for every tile made opening and refreshing the launcher
    # feel delayed. A short cache keeps theme changes responsive without doing
    # repeated filesystem work while one menu frame is being built.
    if not force and _ICON_THEME_LAST_CHECK and now - _ICON_THEME_LAST_CHECK < 2.0:
        return _ICON_THEME_LAST_SELECTED or QIcon.themeName()
    paths=QIcon.themeSearchPaths()+['/usr/share/icons','/usr/local/share/icons',str(Path.home()/'.icons'),str(Path.home()/'.local/share/icons'),'/usr/share/pixmaps']
    QIcon.setThemeSearchPaths(list(dict.fromkeys(paths)))
    selected=current_icon_theme_name()
    old=QIcon.themeName()
    _ICON_THEME_LAST_CHECK=now
    _ICON_THEME_LAST_SELECTED=selected or old
    if selected and selected != old:
        QIcon.setThemeName(selected)
        try:
            _ICON_OBJECT_CACHE.clear()
        except Exception:
            pass
        registry_update('appearance', {'icon_theme': selected, 'previous_icon_theme': old, 'updated_at': time.time()})
    return selected or old


_ICON_INDEX = {'roots': None, 'files': {}}

def _icon_index(roots):
    """{name: [(root number, path)]} of every icon file below the roots.
    Built once per set of icon themes (a recursive glob per lookup took
    seconds and froze Eduka-Panel when the Action Center opened)."""
    key=tuple(str(r) for r in roots)
    if _ICON_INDEX['roots'] != key:
        files={}
        for i, root in enumerate(roots):
            for dirpath, _dirs, names in os.walk(str(root), followlinks=True):
                for fname in names:
                    stem, ext=os.path.splitext(fname)
                    if ext in ('.svg', '.png', '.xpm'):
                        files.setdefault(stem, []).append((i, os.path.join(dirpath, fname)))
        _ICON_INDEX.update(roots=key, files=files)
    return _ICON_INDEX['files']

def _find_icon_file(name):
    if not name: return None
    name=str(name).strip()
    if os.path.exists(name): return name
    base=os.path.splitext(os.path.basename(name))[0]
    roots=[]
    for theme in _theme_candidates():
        for root in [Path('/usr/share/icons')/theme, Path('/usr/local/share/icons')/theme, Path.home()/'.icons'/theme, Path.home()/'.local/share/icons'/theme]:
            if root.exists(): roots.append(root)
    for root in [Path('/usr/share/pixmaps'), ASSET_DIR]:
        if root.exists(): roots.append(root)
    found=_icon_index(roots).get(base)
    if not found:
        return None
    ext_rank={'.svg': 0, '.png': 1, '.xpm': 2}
    preferred=['scalable','128x128','96x96','64x64','48x48','32x32','24x24','22x22','16x16']
    for pref in preferred:
        hits=[(i, ext_rank.get(os.path.splitext(path)[1], 3), path) for i, path in found if f'/{pref}/' in path]
        if hits:
            return min(hits)[2]
    return min((i, ext_rank.get(os.path.splitext(path)[1], 3), path) for i, path in found)[2]

ICON_ALIASES = {
    'view-app-grid': ['view-app-grid','applications-all','application-menu','start-here'],
    'applications-education': ['applications-education','education','applications-science','accessories-dictionary'],
    'applications-accessories': ['applications-accessories','applications-utilities','preferences-desktop-accessibility'],
    'applications-graphics': ['applications-graphics','graphics','image-x-generic'],
    'applications-internet': ['applications-internet','internet-web-browser','network-wireless','web-browser'],
    'applications-office': ['applications-office','x-office-document','libreoffice-startcenter'],
    'applications-development': ['applications-development','development','text-x-script'],
    'applications-multimedia': ['applications-multimedia','multimedia-volume-control','audio-x-generic'],
    'applications-system': ['applications-system','preferences-system','system-run'],
    'preferences-desktop-accessibility': ['preferences-desktop-accessibility','preferences-desktop','accessibility'],
    'preferences-system': ['preferences-system','preferences-desktop','applications-system'],
    'emblem-favorite': ['emblem-favorite','starred','rating'],
    'application-x-executable': ['application-x-executable','application-default-icon','exec', GENERIC_ICON],
}

_ICON_OBJECT_CACHE = {}

def get_icon(name, fallback='application-x-executable'):
    icon_theme_setup()
    cache_key=(str(name), str(fallback), QIcon.themeName())
    cached=_ICON_OBJECT_CACHE.get(cache_key)
    if cached is not None:
        return cached
    candidates=[]
    for item in [name, *(ICON_ALIASES.get(str(name), []) if name else [])]:
        if item and item not in candidates: candidates.append(item)
    if isinstance(fallback, (list, tuple)):
        fb=list(fallback)
    else:
        fb=[fallback]
    for f in fb:
        if f and f not in candidates: candidates.append(f)
        for a in ICON_ALIASES.get(str(f), []):
            if a and a not in candidates: candidates.append(a)
    if GENERIC_ICON not in candidates: candidates.append(GENERIC_ICON)
    for n in candidates:
        if not n: continue
        if os.path.exists(str(n)):
            ic=QIcon(str(n))
        else:
            ic=QIcon.fromTheme(str(n))
            if ic.isNull():
                found=_find_icon_file(str(n))
                ic=QIcon(found) if found else ic
        if not ic.isNull():
            _ICON_OBJECT_CACHE[cache_key]=ic
            return ic
    ic=QIcon(GENERIC_ICON) if os.path.exists(GENERIC_ICON) else QIcon()
    _ICON_OBJECT_CACHE[cache_key]=ic
    return ic

def menu_button_icon_size(icon, height, keep_aspect=True):
    """Size for the Eduka-Menu button image.

    Theme icons are square. A custom picture keeps its proportions (up to 3:1,
    e.g. a school logo) so it is not squeezed into a square.
    """
    from PyQt5.QtGui import QImageReader
    height=max(12, int(height))
    width=height
    if keep_aspect and icon and os.path.isfile(str(icon)):
        try:
            real=QImageReader(str(icon)).size()
            if real.isValid() and real.height() > 0:
                ratio=max(0.5, min(3.0, real.width()/real.height()))
                width=int(round(height*ratio))
        except Exception:
            pass
    return QSize(width, height)

def clean_exec(cmd):
    if not cmd: return ''
    for p in ['%f','%F','%u','%U','%i','%c','%k','%d','%D','%n','%N','%v','%m']:
        cmd=cmd.replace(p,'')
    return cmd.strip()

def safe_popen(cmd, shell=False):
    try:
        if shell:
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, env=child_env())
        else:
            if isinstance(cmd, str): cmd=shlex.split(cmd)
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, env=child_env())
        return True
    except Exception:
        return False

def launch_app(cmd, app_name=''):
    cmd=clean_exec(cmd)
    if not cmd: return False
    env=child_env()
    # Safer defaults for old CPUs, VMs and 512MB targets. This helps WebGL/Electron
    # apps such as TurboWarp use software rendering when hardware acceleration is missing.
    env.setdefault('LIBGL_ALWAYS_SOFTWARE', '1')
    env.setdefault('WEBKIT_DISABLE_DMABUF_RENDERER', '1')
    lower=(cmd+' '+app_name).lower()
    if 'turbowarp' in lower or 'scratch' in lower:
        env.setdefault('MESA_GL_VERSION_OVERRIDE', '3.3')
        if '--ignore-gpu-blocklist' not in cmd:
            cmd += ' --ignore-gpu-blocklist --enable-unsafe-swiftshader'
    try:
        args=shlex.split(cmd)
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, env=env)
        return True
    except Exception:
        try:
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, env=env)
            return True
        except Exception:
            return False

def parse_desktop_file(path):
    cp=configparser.ConfigParser(interpolation=None, strict=False)
    try: cp.read(path, encoding='utf-8')
    except Exception:
        try: cp.read(path)
        except Exception: return None
    if 'Desktop Entry' not in cp: return None
    de=cp['Desktop Entry']
    if de.get('Type','Application') != 'Application': return None
    if de.get('NoDisplay','false').lower() == 'true' or de.get('Hidden','false').lower() == 'true': return None
    desktop_id=os.path.basename(path)
    name=de.get('Name','').strip()
    exec_cmd=de.get('Exec','').strip()
    if is_internal_desktop_entry(desktop_id, name, exec_cmd): return None
    if not name or not exec_cmd: return None
    return {
        'name': name,
        'generic': de.get('GenericName',''),
        'icon': de.get('Icon','application-x-executable'),
        'exec': clean_exec(exec_cmd),
        'categories': de.get('Categories',''),
        'path': path,
        'desktop_id': desktop_id,
        'startup_wm_class': de.get('StartupWMClass',''),
        'keywords': de.get('Keywords','')
    }

def _desktop_registry_signature():
    sig=[]
    for d in DESKTOP_DIRS:
        d=os.path.expanduser(d)
        try:
            if not os.path.isdir(d):
                sig.append((d,0,0)); continue
            files=glob.glob(d+'/*.desktop')
            max_m=0
            for f in files:
                try: max_m=max(max_m, int(os.path.getmtime(f)))
                except Exception: pass
            sig.append((d,len(files),max_m))
        except Exception:
            sig.append((d,0,0))
    return sig


_APP_REGISTRY_MEMO = {'stamp': None, 'apps': []}

def read_app_registry_fast():
    """Return the current cached app list without checking signatures.
    This is used by the resident Eduka-Desktop startmenu so the window appears
    immediately. A background warm-up can rebuild the cache later.

    Eduka-Panel calls this for every window on every taskbar refresh, so the
    parsed list is kept in memory until the cache file itself changes.
    """
    ensure_dirs()
    try:
        st=APP_REGISTRY_PATH.stat()
        stamp=(st.st_mtime_ns, st.st_size)
    except OSError:
        return []
    if _APP_REGISTRY_MEMO['stamp'] == stamp:
        return list(_APP_REGISTRY_MEMO['apps'])
    try:
        data=json.loads(APP_REGISTRY_PATH.read_text(encoding='utf-8'))
        apps=data.get('apps', [])
        if isinstance(apps, list):
            apps=sorted(apps, key=lambda a: a.get('name','').casefold())
            _APP_REGISTRY_MEMO['stamp']=stamp; _APP_REGISTRY_MEMO['apps']=apps
            return list(apps)
    except Exception:
        pass
    return []

def is_internal_desktop_entry(desktop_id='', name='', exec_cmd=''):
    did=(desktop_id or '').strip().casefold()
    nm=(name or '').strip().casefold()
    ex=(exec_cmd or '').strip().casefold()
    if did in {x.casefold() for x in HIDE_IDS}: return True
    if nm in INTERNAL_APP_NAMES: return True
    if any(marker in ex for marker in INTERNAL_EXEC_MARKERS): return True
    # Virtual machine helpers (VirtualBox Guest Additions, VMware/SPICE agents)
    # are not applications for students; they work in the background.
    if any(m in did or m in nm or m in ex for m in VM_HELPER_MARKERS): return True
    return False

VM_HELPER_MARKERS = ('vboxclient', 'virtualbox guest', 'vbox-client', 'vboxservice', 'vboxdrmclient',
                     'virtualbox-guest', 'vmware-user', 'vmware user', 'spice-vdagent', 'qemu-guest')

def load_apps(force=False):
    """Fast application cache loader.
    The first scan builds a small JSON application cache in ~/.cache/eduka-desktop.
    Later Eduka-Menu openings read this cache, so clicking Eduka-Menu feels fast
    and RAM usage stays stable instead of repeatedly parsing every .desktop file.
    """
    ensure_dirs()
    sig=_desktop_registry_signature()
    if not force and APP_REGISTRY_PATH.exists():
        try:
            data=json.loads(APP_REGISTRY_PATH.read_text(encoding='utf-8'))
            if data.get('signature') == sig and isinstance(data.get('apps'), list):
                apps = sorted(data['apps'], key=lambda a: a.get('name','').casefold())
                registry_update('apps', {'count': len(apps), 'cache': 'hit', 'path': str(APP_REGISTRY_PATH)})
                return apps
        except Exception:
            pass
    seen={}; apps=[]
    for d in DESKTOP_DIRS:
        d=os.path.expanduser(d)
        if not os.path.isdir(d): continue
        for path in glob.glob(d+'/*.desktop'):
            app=parse_desktop_file(path)
            if not app: continue
            exe=(app['exec'].split() or [''])[0]
            key=(app['name'].casefold(), os.path.basename(exe).casefold(), app['desktop_id'].casefold())
            if key in seen: continue
            seen[key]=True; apps.append(app)
    apps=sorted(apps, key=lambda a: a['name'].casefold())
    try:
        tmp=APP_REGISTRY_PATH.with_suffix('.json.tmp')
        tmp.write_text(json.dumps({'version': VERSION, 'signature': sig, 'apps': apps}, ensure_ascii=False), encoding='utf-8')
        os.replace(tmp, APP_REGISTRY_PATH)
        registry_update('apps', {'count': len(apps), 'cache': 'rebuilt', 'path': str(APP_REGISTRY_PATH)})
    except Exception:
        pass
    return apps

def rebuild_app_registry():
    return load_apps(force=True)

def app_override_category(app):
    name=(app.get('name','') or '').strip().casefold()
    exe=os.path.basename((app.get('exec','').split() or [''])[0]).casefold()
    did=(app.get('desktop_id','') or '').replace('.desktop','').casefold()
    for key, cat in CATEGORY_NAME_OVERRIDES.items():
        if key in name or key == did:
            return cat
    for key, cat in CATEGORY_EXEC_OVERRIDES.items():
        if key == exe or key in did or key in name:
            return cat
    return ''

def app_matches_category(app, category):
    if category == 'All':
        return True
    if category == 'Favorites':
        return False
    override = app_override_category(app)
    if override:
        return category == override
    cats=(app.get('categories','') or '').lower()
    name=(app.get('name','') or '').lower()
    did=(app.get('desktop_id','') or '').lower()
    exe=os.path.basename((app.get('exec','').split() or [''])[0]).lower()
    blob=' '.join([cats,name,did,exe])
    # Category priority rules. These keep broad/incorrect .desktop categories from
    # placing multimedia/education/preference apps in Programming.
    multimedia_words=['audio','video','audiovideo','multimedia','player','vlc','audacious','mpv','celluloid','pavucontrol']
    education_words=['education','science','game','gcompris','tux','scratch','turbowarp','kdeedu','kbruch','kturtle','kstars','kalzium','marble','geogebra']
    pref_words=['settings','preferences','configuration','appearance','brightness','desktopsettings','lxqt-config','nm-connection-editor']
    if category == 'Sound & Video' and any(x in blob for x in multimedia_words):
        return True
    if category == 'Edukasaun' and any(x in blob for x in education_words):
        return True
    if category == 'Preferences' and any(x in blob for x in pref_words):
        return True
    if category == 'Programming' and (any(x in blob for x in multimedia_words+education_words+pref_words) or 'development' not in cats):
        return False
    for cname, icon, needles in CATEGORY_ORDER:
        if cname == category:
            return any(n.lower() in cats or n.lower() in name or n.lower() in did or n.lower() in exe for n in needles)
    return False


def pinned_config_path():
    return PANEL_CONFIG_DIR/'pinned-taskbar.json'

def read_pinned_apps():
    data=read_json(pinned_config_path(), {'pinned': []})
    pins=data.get('pinned', [])
    return pins if isinstance(pins, list) else []

def save_pinned_apps(pins):
    cleaned=[]
    for p in pins:
        if not p or p in cleaned:
            continue
        app = app_by_pin_key(p) if 'app_by_pin_key' in globals() else None
        if app and is_desktop_shell_app(app):
            continue
        cleaned.append(p)
    write_json(pinned_config_path(), {'pinned': cleaned})
    touch_reload()

def pin_app_key(app):
    if not app: return ''
    return app.get('desktop_id') or app.get('path') or app.get('name','')

def is_app_pinned(app):
    key=pin_app_key(app)
    return bool(key and key in read_pinned_apps())

def pin_app(app):
    key=pin_app_key(app)
    if not key: return False
    pins=read_pinned_apps()
    if key not in pins:
        pins.append(key); save_pinned_apps(pins)
    return True

def unpin_app(app_or_key):
    key=pin_app_key(app_or_key) if isinstance(app_or_key, dict) else str(app_or_key or '')
    pins=[p for p in read_pinned_apps() if p != key]
    save_pinned_apps(pins); return True

def favorite_config_path():
    return MENU_CONFIG_DIR/'favorites.json'

def read_favorites():
    data=read_json(favorite_config_path(), {'favorites': []})
    favs=data.get('favorites', [])
    if not isinstance(favs, list):
        return []
    # Keep the right-side Favorites area responsive and visually stable.
    return favs[:MAX_FAVORITES]

def is_favorite(app):
    key=pin_app_key(app)
    return bool(key and key in read_favorites())

def save_favorites(favs):
    cleaned=[]
    for f in favs:
        if f and f not in cleaned:
            cleaned.append(f)
        if len(cleaned) >= MAX_FAVORITES:
            break
    write_json(favorite_config_path(), {'favorites': cleaned})

def favorite_app(app):
    key=pin_app_key(app)
    if not key: return False
    favs=read_favorites()
    if key not in favs:
        if len(favs) >= MAX_FAVORITES:
            return False
        favs.append(key); save_favorites(favs); touch_reload()
    return True

def unfavorite_app(app_or_key):
    key=pin_app_key(app_or_key) if isinstance(app_or_key, dict) else str(app_or_key or '')
    favs=[f for f in read_favorites() if f != key]
    save_favorites(favs); touch_reload(); return True

def app_by_pin_key(key):
    key=str(key or '')
    if not key:
        return None
    apps = read_app_registry_fast() or load_apps(force=False)
    for app in apps:
        if key in [app.get('desktop_id'), app.get('path'), app.get('name')]:
            return app
    return None


def is_desktop_shell_app(app):
    """Return True for desktop/background/helper launchers that must never
    appear as real taskbar entries or pinned taskbar launchers."""
    if not isinstance(app, dict):
        return False
    name=(app.get('name','') or '').strip().casefold()
    did=(app.get('desktop_id','') or '').strip().casefold()
    exe=(app.get('exec','') or '').strip().casefold()
    path=(app.get('path','') or '').strip().casefold()
    blob=' '.join([name,did,exe,path])
    if name in {'desktop','workspace','background','desktop folder'}:
        return True
    if any(x in blob for x in ['eduka-menu','eduka-panel','eduka-desktop','edukasaun-desktop','edukasaun desktop']):
        return True
    if 'pcmanfm' in blob and any(x in blob for x in ['--desktop','desktop.desktop','desktop folder']):
        return True
    if did in {'pcmanfm-qt-desktop.desktop','pcmanfm-desktop.desktop','desktop.desktop'}:
        return True
    return False

def filter_apps(apps, category='All', query=''):
    q=(query or '').strip().casefold(); res=[]
    for app in apps:
        text=' '.join([app.get('name',''), app.get('generic',''), app.get('keywords',''), app.get('categories','')]).casefold()
        if q and q not in text: continue
        if app_matches_category(app, category): res.append(app)
    return sorted(res, key=lambda a: a['name'].casefold())

def _norm_window_text(value):
    return re.sub(r'[^a-z0-9]+', ' ', (value or '').casefold()).strip()

EDUKA_OWN_WINDOWS = [
    (('eduka-settings', 'eduka-menu-settings', 'eduka settings'),
     {'name': 'Eduka-Settings', 'icon': 'preferences-system', 'exec': 'eduka-settings', 'desktop_id': 'eduka-settings.desktop'}),
    (('eduka-about', 'about edukasaun'),
     {'name': 'About Edukasaun', 'icon': 'help-about', 'exec': 'eduka-about', 'desktop_id': 'eduka-about.desktop'}),
]
# Words many application names share; they must not decide a match alone.
GENERIC_WINDOW_WORDS = {'eduka', 'edukasaun', 'settings', 'system', 'manager', 'update', 'updates',
                        'desktop', 'application', 'applications', 'viewer', 'editor', 'tools', 'center',
                        'centre', 'configuration', 'preferences', 'linux', 'debian', 'about'}

def find_app_for_window(title, wm_class=''):
    """Match an X11/LXQt window to its .desktop application.
    0.9.6: improved for PCManFM-Qt and minimized windows so taskbar labels
    show the real app name instead of generic titles such as "Desktop".
    """
    apps=read_app_registry_fast() or load_apps()
    t=_norm_window_text(title)
    c=_norm_window_text(wm_class)
    raw_c=(wm_class or '').casefold()
    raw_t=(title or '').casefold()

    # Eduka's own windows are hidden from the application list, so they
    # would otherwise borrow another Eduka application's name and icon.
    for needles, own in EDUKA_OWN_WINDOWS:
        if any(n in raw_c or raw_t.startswith(n) for n in needles):
            return dict(own)

    # Explicit desktop/file-manager class mapping first.
    if 'pcmanfm' in raw_c:
        for app in apps:
            blob=' '.join([app.get('name',''), app.get('desktop_id',''), app.get('exec','')]).casefold()
            if 'pcmanfm' in blob:
                return app
    if 'qterminal' in raw_c:
        for app in apps:
            blob=' '.join([app.get('name',''), app.get('desktop_id',''), app.get('exec','')]).casefold()
            if 'qterminal' in blob:
                return app

    best=None; best_score=0
    for app in apps:
        exe=os.path.basename((app.get('exec','').split() or [''])[0]).casefold()
        tokens=[app.get('name',''), app.get('startup_wm_class',''), app.get('desktop_id','').replace('.desktop',''), exe]
        norm_tokens=[_norm_window_text(x) for x in tokens if x]
        score=0
        for tok in norm_tokens:
            if not tok: continue
            if c and (tok == c or tok in c or c in tok): score=max(score, 100)
            elif t and (tok == t or tok in t or t in tok): score=max(score, 80)
            else:
                # partial words are useful for titles like "file.txt - FeatherPad".
                for part in tok.split():
                    if len(part) >= 4 and part not in GENERIC_WINDOW_WORDS and (part in t or part in c): score=max(score, 40)
        if score > best_score:
            best_score=score; best=app
    return best

def distro_info():
    """Return the public Edukasaun identity shown in System Information.

    Live-image/remaster build tools can overwrite /etc/os-release with their
    own build metadata.  That implementation detail must not replace the
    product identity presented to desktop users.
    """
    return {
        'os': 'Edukasaun OS',
        'version': '1.0',
        'codename': 'Kameli',
        'base': 'Debian GNU/Linux 13 (Trixie)',
        'desktop': 'Eduka-Desktop (LXQt Session)',
    }

def desktop_folder():
    """Return the user's Desktop folder, following xdg-user-dir when present."""
    try:
        out=subprocess.check_output(['xdg-user-dir','DESKTOP'], text=True, stderr=subprocess.DEVNULL).strip()
        if out:
            return Path(out).expanduser()
    except Exception:
        pass
    return Path.home()/'Desktop'

def _safe_desktop_filename(name):
    base=re.sub(r'[^A-Za-z0-9._-]+','-', str(name or 'application')).strip('-') or 'application'
    if not base.endswith('.desktop'):
        base += '.desktop'
    return base

def add_app_to_desktop(app):
    """Create a desktop shortcut for an application.
    Works with normal .desktop files and generated shortcuts.
    """
    try:
        folder=desktop_folder(); folder.mkdir(parents=True, exist_ok=True)
        src=Path(app.get('path','')) if isinstance(app, dict) else Path('')
        dest=folder/_safe_desktop_filename(app.get('desktop_id') or app.get('name','Application'))
        if src.exists() and src.suffix == '.desktop':
            data=src.read_text(errors='ignore')
        else:
            data='[Desktop Entry]\nType=Application\nName=%s\nExec=%s\nIcon=%s\nTerminal=false\nCategories=Application;\n' % (
                app.get('name','Application'), app.get('exec',''), app.get('icon','application-x-executable'))
        dest.write_text(data, encoding='utf-8')
        try:
            mode=dest.stat().st_mode
            dest.chmod(mode | 0o755)
        except Exception:
            pass
        safe_popen(['gio','set',str(dest),'metadata::trusted','true'])
        return True, str(dest)
    except Exception as e:
        return False, str(e)

_LXQT_SESSION = ['dbus-send','--session','--type=method_call','--print-reply','--dest=org.lxqt.session','/LXQtSession']
SESSION_COMMANDS = {
    # Run directly: Eduka asks for confirmation with its own leave screen
    # (eduka-session-action), so LXQt's plain dialog is never shown.
    'lock': [['lxqt-leave','--lockscreen'], ['loginctl','lock-session'], ['xdg-screensaver','lock']],
    'logout': [_LXQT_SESSION+['org.lxqt.session.logout'], ['loginctl','terminate-session', os.environ.get('XDG_SESSION_ID','')]],
    'shutdown': [_LXQT_SESSION+['org.lxqt.session.powerOff'], ['systemctl','poweroff']],
    'restart': [_LXQT_SESSION+['org.lxqt.session.reboot'], ['systemctl','reboot']],
    'suspend': [['systemctl','suspend']],
}

def session_action(action):
    """Run the first available command for a session action.

    launch_app() falls back to a shell and therefore reports success even when
    the program is missing, so the executable is checked before it is used.
    """
    for cmd in SESSION_COMMANDS.get(action, []):
        if not shutil.which(cmd[0]) or not all(cmd):
            continue
        if cmd[0] == 'dbus-send':
            # Only lxqt-session knows how to end the session cleanly; when it
            # does not answer, use the next command.
            try:
                if subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5).returncode == 0:
                    return True
            except Exception:
                pass
            continue
        if safe_popen(cmd):
            return True
    return False

def confirm_session_action(action):
    """Open the Eduka leave screen (lock runs at once)."""
    if action == 'lock':
        return session_action('lock')
    return safe_popen(['eduka-session-action', action])
