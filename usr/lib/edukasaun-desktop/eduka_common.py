#!/usr/bin/env python3
import os, sys, json, glob, configparser, subprocess, shlex, time, re, html, shutil
from pathlib import Path
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

VERSION = "0.9.11"
SETTINGS_REVISION = "0.9.6-transparency"
MAX_FAVORITES = 5
APP_ID = "eduka-desktop"
THEME_DEFAULT = "Eduka-Default-Theme"
THEME_LIQUID = "Liquid Glass"
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

DEFAULT_PANEL = {
    "height": 42,
    "width_percent": 96,
    "position": "Bottom",
    "transparency": 0.54,
    "icon_size": 24,
    "menu_label": "Edukasaun",
    "menu_icon": START_ICON,
    "menu_icon_size": 26,
    "show_menu_text": True,
    "taskbar_style": "Icon and Text",
    "taskbar_icon_size": 22,
    "autohide": False,
    "locked": True,
    "enable_shadows": False,
    "low_resource_mode": True,
    "theme_style": THEME_DEFAULT,
    "reserve_workarea": True,
    "force_window_above_panel": True,
    "taskbar_max_button_width": 175,
    "taskbar_min_button_width": 46
}
DEFAULT_MENU = {"mode": "Eduka-Desktop", "language": "system"}
DEFAULT_DESKTOP = {"last_category": "Edukasaun", "layout": "Grid", "width_percent": 98, "height_percent": 92, "transparency": 0.51, "enable_shadows": False, "low_resource_mode": True, "theme_style": THEME_DEFAULT, "show_right_panel": True, "smooth_animations": False, "corner_radius": 24, "visual_accessibility": False, "hearing_accessibility": False, "orca_enabled": False}

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
    'edukasaun-desktop.desktop','eduka-menu-settings.desktop',
    'eduka-menu.desktop','eduka-panel.desktop','eduka-about.desktop',
    'edukasaun-desktop-menu-open.desktop','eduka-app-registry.desktop','eduka-app-cache.desktop'
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
    """Map retired 0.9.x theme names to the two supported themes."""
    return THEME_LIQUID if str(value or '').strip().casefold() == THEME_LIQUID.casefold() else THEME_DEFAULT
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


def _find_icon_file(name):
    if not name: return None
    name=str(name).strip()
    if os.path.exists(name): return name
    base=os.path.splitext(os.path.basename(name))[0]
    exts=['.svg','.png','.xpm']
    roots=[]
    for theme in _theme_candidates():
        for root in [Path('/usr/share/icons')/theme, Path('/usr/local/share/icons')/theme, Path.home()/'.icons'/theme, Path.home()/'.local/share/icons'/theme]:
            if root.exists(): roots.append(root)
    for root in [Path('/usr/share/pixmaps'), ASSET_DIR]:
        if root.exists(): roots.append(root)
    preferred=['scalable','128x128','96x96','64x64','48x48','32x32','24x24','22x22','16x16']
    for pref in preferred:
        for root in roots:
            try:
                for ext in exts:
                    matches=list(root.glob(f'**/{pref}/**/{base}{ext}')) if pref != 'scalable' else list(root.glob(f'**/scalable/**/{base}{ext}'))
                    if matches: return str(matches[0])
            except Exception: pass
    for root in roots:
        try:
            for ext in exts:
                matches=list(root.glob(f'**/{base}{ext}'))
                if matches: return str(matches[0])
        except Exception: pass
    return None

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

def clean_exec(cmd):
    if not cmd: return ''
    for p in ['%f','%F','%u','%U','%i','%c','%k','%d','%D','%n','%N','%v','%m']:
        cmd=cmd.replace(p,'')
    return cmd.strip()

def safe_popen(cmd, shell=False):
    try:
        if shell:
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        else:
            if isinstance(cmd, str): cmd=shlex.split(cmd)
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return True
    except Exception:
        return False

def launch_app(cmd, app_name=''):
    cmd=clean_exec(cmd)
    if not cmd: return False
    env=os.environ.copy()
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
    return False

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
                    if len(part) >= 4 and (part in t or part in c): score=max(score, 40)
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

SESSION_COMMANDS = {
    # lxqt-leave is tried first: it asks for confirmation before shutdown or
    # restart, so a single misclick in Eduka-Desktop cannot power off a class PC.
    'lock': [['lxqt-leave','--lockscreen'], ['loginctl','lock-session'], ['xdg-screensaver','lock']],
    'logout': [['lxqt-leave','--logout'], ['qdbus','org.lxqt.session','/LXQtSession','logout']],
    'shutdown': [['lxqt-leave','--shutdown'], ['systemctl','poweroff']],
    'restart': [['lxqt-leave','--reboot'], ['systemctl','reboot']],
}

def session_action(action):
    """Run the first available command for a session action.

    launch_app() falls back to a shell and therefore reports success even when
    the program is missing, so the executable is checked before it is used.
    """
    for cmd in SESSION_COMMANDS.get(action, []):
        if shutil.which(cmd[0]) and safe_popen(cmd):
            return True
    return False
