"""Wallpaper and desktop icons of Eduka-Desktop (taken over from LXQt's
desktop preferences, which are drawn by pcmanfm-qt).

Eduka renders the wallpaper itself — the picture placed with the chosen mode
(zoom, mosaic, centered, scaled, stretched) on the chosen background color —
into a new file at the size of the screen, and hands that file to the running
pcmanfm-qt desktop (`pcmanfm-qt --set-wallpaper FILE --wallpaper-mode
stretch`). pcmanfm-qt only redraws when the file name changes, so every
rendering gets its own name. This keeps the result identical everywhere and
lets the background color work, which pcmanfm-qt cannot set from the command
line.

Desktop icons (Home, Trash, Computer, Network) are pcmanfm-qt's
`DesktopShortcuts`; pcmanfm-qt reads them only when it starts and saves its
own settings when it quits, so Eduka quits it, writes the setting and starts
the desktop again. Drives are shown as links on the desktop by Eduka-Panel.
"""
import hashlib, os, random, re, shutil, subprocess, time
from pathlib import Path

from eduka_common import (CACHE_DIR, read_desktop_config, save_desktop_config, child_env, _get_ini_value, _set_ini_value)

BACKGROUND_DIRS = [Path('/usr/share/Edukasaun/Backgrounds')]
IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.svg')
MODES = [('zoom', 'Zoom'), ('tile', 'Mosaic'), ('center', 'Centered'), ('fit', 'Scaled'), ('stretch', 'Stretched')]
TRANSITIONS = [('none', 'No transition'), ('fast', 'Fast fade (0.5 s)'), ('normal', 'Fade (1 s)'), ('slow', 'Slow fade (2 s)')]
TRANSITION_MS = {'none': 0, 'fast': 500, 'normal': 1000, 'slow': 2000}
RENDER_DIR = CACHE_DIR/'wallpaper'
PCMANFM_CONF = Path.home()/'.config/pcmanfm-qt/lxqt/settings.conf'
DEFAULTS = {'images': [], 'mode': 'zoom', 'color': '#1f6b45', 'slideshow': False, 'interval': 10,
            'random': True, 'transition': 'normal', 'extra': []}
SHORTCUTS = [('Home', 'user-home.desktop'), ('Trash', 'trash-can.desktop'), ('Computer', 'computer.desktop'), ('Network', 'network.desktop')]


def wallpaper_config():
    cfg = dict(DEFAULTS)
    try:
        data = read_desktop_config().get('wallpaper') or {}
        if isinstance(data, dict):
            cfg.update({k: v for k, v in data.items() if k in DEFAULTS})
    except Exception:
        pass
    if cfg['mode'] not in dict(MODES): cfg['mode'] = 'zoom'
    if not re.fullmatch(r'#[0-9a-fA-F]{6}', str(cfg['color'])): cfg['color'] = DEFAULTS['color']
    if cfg['transition'] not in TRANSITION_MS: cfg['transition'] = 'normal'
    try: cfg['interval'] = max(1, min(1440, int(cfg['interval'])))
    except Exception: cfg['interval'] = 10
    cfg['images'] = [str(p) for p in cfg['images'] if isinstance(p, str)]
    cfg['extra'] = [str(p) for p in cfg['extra'] if isinstance(p, str)]
    return cfg


def save_wallpaper_config(cfg):
    clean = {k: cfg[k] for k in DEFAULTS if k in cfg}
    save_desktop_config({'wallpaper': clean})


def list_wallpapers(extra=()):
    """Every picture in the Edukasaun background folders, plus the pictures
    the user added."""
    seen, out = set(), []
    for d in BACKGROUND_DIRS:
        try:
            for p in sorted(d.rglob('*')):
                if p.suffix.lower() in IMAGE_EXT and p.is_file() and str(p) not in seen:
                    seen.add(str(p)); out.append(str(p))
        except Exception:
            continue
    for p in extra:
        if p not in seen and os.path.isfile(p):
            seen.add(p); out.append(p)
    return out


def screen_size():
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance()
    if app is not None and app.primaryScreen() is not None:
        g = app.primaryScreen().geometry(); r = app.primaryScreen().devicePixelRatio()
        return max(320, int(g.width()*r)), max(240, int(g.height()*r))
    return 1920, 1080


def render(path, mode='zoom', color='#1f6b45', size=None):
    """QImage of the whole screen: the picture placed with the mode on the
    background color. path '' gives the plain color."""
    from PyQt5.QtGui import QImage, QPainter, QColor, QImageReader
    from PyQt5.QtCore import Qt, QRectF
    w, h = size or screen_size()
    out = QImage(w, h, QImage.Format_RGB32); out.fill(QColor(color))
    if not path:
        return out
    reader = QImageReader(path); reader.setAutoTransform(True)
    img = reader.read()
    if img.isNull():
        return out
    p = QPainter(out); p.setRenderHint(QPainter.SmoothPixmapTransform)
    iw, ih = img.width(), img.height()
    if mode == 'stretch':
        p.drawImage(QRectF(0, 0, w, h), img)
    elif mode in ('zoom', 'fit'):
        k = max(w/iw, h/ih) if mode == 'zoom' else min(w/iw, h/ih)
        sw, sh = iw*k, ih*k
        p.drawImage(QRectF((w-sw)/2, (h-sh)/2, sw, sh), img)
    elif mode == 'center':
        p.drawImage(int((w-iw)/2), int((h-ih)/2), img)
    elif mode == 'tile':
        for y in range(0, h, max(1, ih)):
            for x in range(0, w, max(1, iw)):
                p.drawImage(x, y, img)
    p.end()
    return out


def render_file(path, mode, color, size=None):
    """Render once into the cache; the file name changes with every input,
    so pcmanfm-qt always sees a new wallpaper."""
    w, h = size or screen_size()
    try: stamp = os.stat(path).st_mtime_ns if path else 0
    except Exception: stamp = 0
    key = hashlib.sha1(f'{path}|{stamp}|{mode}|{color}|{w}x{h}'.encode()).hexdigest()[:16]
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    target = RENDER_DIR/f'wallpaper-{key}.jpg'
    if not target.exists():
        img = render(path, mode, color, (w, h))
        tmp = target.with_suffix('.tmp.jpg'); img.save(str(tmp), 'JPG', 92); os.replace(tmp, target)
    # Keep the cache small: the 12 newest renderings.
    files = sorted(RENDER_DIR.glob('wallpaper-*.jpg'), key=lambda f: f.stat().st_mtime, reverse=True)
    for old in files[12:]:
        if old != target:
            try: old.unlink()
            except Exception: pass
    os.utime(target, None)
    return str(target)


def pcmanfm_desktop_running():
    for d in Path('/proc').iterdir():
        if not d.name.isdigit(): continue
        try:
            if d.stat().st_uid != os.getuid(): continue
            args = (d/'cmdline').read_bytes().split(b'\0')
            if args and os.path.basename(args[0].decode('utf-8', 'ignore')) == 'pcmanfm-qt' and b'--desktop' in b' '.join(args):
                return int(d.name)
        except Exception:
            continue
    return 0


def set_desktop_wallpaper(file):
    """Show a rendered wallpaper on the desktop now."""
    if shutil.which('pcmanfm-qt') and pcmanfm_desktop_running():
        subprocess.Popen(['pcmanfm-qt', '--profile=lxqt', '--set-wallpaper', file, '--wallpaper-mode', 'stretch'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=child_env(), start_new_session=True)
        return True
    # No pcmanfm-qt desktop: remember it for the next start, and use feh if there.
    try:
        PCMANFM_CONF.parent.mkdir(parents=True, exist_ok=True)
        _set_ini_value(PCMANFM_CONF, 'Desktop', 'Wallpaper', file)
        _set_ini_value(PCMANFM_CONF, 'Desktop', 'WallpaperMode', 'stretch')
    except Exception:
        pass
    if shutil.which('feh'):
        subprocess.Popen(['feh', '--no-fehbg', '--bg-scale', file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=child_env())
        return True
    return False


def current_image(cfg=None):
    cfg = cfg or wallpaper_config()
    imgs = [p for p in cfg['images'] if os.path.isfile(p)]
    return imgs[0] if imgs else ''


def apply_wallpaper(cfg=None, path=None):
    """Render and show the chosen wallpaper (or `path`, used by the slideshow)."""
    cfg = cfg or wallpaper_config()
    image = path if path is not None else current_image(cfg)
    return set_desktop_wallpaper(render_file(image, cfg['mode'], cfg['color']))


def next_slide(cfg, last=''):
    imgs = [p for p in cfg['images'] if os.path.isfile(p)]
    if len(imgs) < 2:
        return imgs[0] if imgs else ''
    if cfg['random']:
        return random.choice([p for p in imgs if p != last] or imgs)
    try: return imgs[(imgs.index(last)+1) % len(imgs)]
    except ValueError: return imgs[0]


# --------------------------------------------------------------- desktop icons
def desktop_dir():
    try:
        out = subprocess.run(['xdg-user-dir', 'DESKTOP'], capture_output=True, text=True, timeout=3).stdout.strip()
        if out: return Path(out)
    except Exception:
        pass
    return Path.home()/'Desktop'


def desktop_shortcuts():
    value = _get_ini_value(PCMANFM_CONF, 'Desktop', 'DesktopShortcuts') if PCMANFM_CONF.exists() else None
    if value is None:
        return {'Home', 'Trash'}
    return {v.strip() for v in str(value).split(',') if v.strip()}


def set_desktop_shortcuts(names, show_drives=None):
    """Home, Trash, Computer and Network on the desktop, applied at once."""
    names = [n for n, _f in SHORTCUTS if n in names]
    if set(names) == desktop_shortcuts() and show_drives is None:
        return False
    running = pcmanfm_desktop_running()
    if running and shutil.which('pcmanfm-qt'):
        # pcmanfm-qt saves its settings when it quits: quit first, write after.
        subprocess.run(['pcmanfm-qt', '--profile=lxqt', '--quit'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, env=child_env())
        for _ in range(50):
            if not pcmanfm_desktop_running(): break
            time.sleep(0.1)
    PCMANFM_CONF.parent.mkdir(parents=True, exist_ok=True)
    _set_ini_value(PCMANFM_CONF, 'Desktop', 'DesktopShortcuts', ', '.join(names))
    # pcmanfm-qt only adds shortcut files; remove the ones switched off.
    ddir = desktop_dir()
    for name, fname in SHORTCUTS:
        if name not in names:
            try: (ddir/fname).unlink()
            except Exception: pass
    if running and shutil.which('pcmanfm-qt'):
        subprocess.Popen(['pcmanfm-qt', '--desktop', '--profile=lxqt'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         env=child_env(), start_new_session=True)
    return True


DRIVE_LINK_PREFIX = 'eduka-drive-'

def sync_drive_links(drives, enabled):
    """Links to mounted USB sticks, memory cards and external disks on the
    desktop (written by Eduka-Panel; removed when the drive goes)."""
    ddir = desktop_dir()
    if not ddir.is_dir():
        return
    wanted = {}
    if enabled:
        for d in drives:
            if d.get('mountpoint'):
                key = re.sub(r'[^A-Za-z0-9_.-]', '_', d.get('uuid') or d['name'])
                wanted[f'{DRIVE_LINK_PREFIX}{key}.desktop'] = d
    for f in ddir.glob(f'{DRIVE_LINK_PREFIX}*.desktop'):
        if f.name not in wanted:
            try: f.unlink()
            except Exception: pass
    for fname, d in wanted.items():
        target = ddir/fname
        text = ('[Desktop Entry]\nType=Link\n'
                f"Name={d.get('label') or d['name']}\n"
                f"Icon={d.get('icon', 'drive-removable-media')}\n"
                f"URL=file://{d['mountpoint']}\nX-Eduka-Drive=true\n")
        try:
            if not target.exists() or target.read_text() != text:
                target.write_text(text)
        except Exception:
            pass
