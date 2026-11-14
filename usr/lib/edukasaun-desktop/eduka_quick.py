#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Eduka-Quick: a round quick launcher (pie menu) for Eduka-Desktop.

The idea comes from Gnome-Pie by Simon Schneegans (GPL-3.0-or-later,
https://schneegans.github.io/gnome-pie): a circle of programs appears where
the mouse is; pointing in a direction chooses a slice and a click (or
releasing the button after dragging) starts it. A slice can open a smaller
pie (a group). This is a new Python/Qt program written for Eduka; no Gnome-Pie
code is used.

It runs inside the resident Eduka-Desktop daemon (eduka-menu --daemon), so it
appears at once: the command eduka-quick (Super+Q) asks the daemon to show
it. The slices are chosen in Eduka-Settings → Eduka-Quick and kept in
~/.config/eduka-desktop/desktop/quick.json.

0.11 RC3: a glass look (colored, rounded slices around a clear center), it
can be moved by holding and dragging (it opens there again), its size
follows the screen and the number of slices (4 - 12), and free slices are
filled with the programs used most. Eduka-Desktop's right-click menu adds
programs to it.
"""
import configparser, json, math, os, re, shutil, time
from pathlib import Path

from eduka_common import (DESKTOP_CONFIG_DIR, write_json, safe_popen, get_icon, theme_accent, is_dark_theme,
                          compositor_running, launch_entry, load_apps, send_menu_command, _)

QUICK_FILE = DESKTOP_CONFIG_DIR/'quick.json'
SHORTCUT_COMMENT = 'Eduka-Quick'
# Super+Space switches the keyboard layout (as in Windows): not offered.
HOTKEYS = (('Meta+Q', 'Super+Q'), ('Control+Alt+Space', 'Ctrl+Alt+Space'), ('Control+Alt+A', 'Ctrl+Alt+A'))
MAX_SLICES = 12
MIN_SLICES = 4
POSITIONS = (('mouse', 'At the mouse'), ('center', 'In the middle of the screen'), ('last', 'Where I put it last'))
LOOKS = (('glass', 'Glass (see-through)'), ('solid', 'Solid'))
# Slice colors (glass): pinks, yellows and teals, neighbors blend.
PALETTE = ('#f06292', '#f8a5c2', '#ffe08a', '#ffc95c', '#26a69a', '#4dd0e1', '#9fe6e3', '#81c784',
           '#b39ddb', '#90caf9', '#ffab91', '#a5d6a7')

# Things Eduka-Quick can do besides starting a program.
ACTIONS = {
    'menu': ('Eduka-Desktop', 'start-here', 'Open the Eduka-Desktop menu'),
    'settings': ('Eduka-Settings', 'preferences-system', 'Open Eduka-Settings'),
    'screenshot': ('Screenshot', 'applets-screenshooter', 'Take a picture of the screen'),
    'lock': ('Lock screen', 'system-lock-screen', 'Lock the screen'),
    'files': ('Home folder', 'user-home', 'Open your files'),
    'logout': ('Leave', 'system-shutdown', 'Lock, log out, restart or shut down'),
    'quick-settings': ('Eduka-Quick settings', 'preferences-desktop', 'Choose the slices of Eduka-Quick'),
}
# Programs tried in order for the default slices (the first installed one).
DEFAULT_PROGRAMS = (
    ('firefox-esr.desktop', 'firefox.desktop', 'org.mozilla.firefox.desktop', 'chromium.desktop', 'google-chrome.desktop'),
    ('pcmanfm-qt.desktop', 'org.kde.dolphin.desktop', 'thunar.desktop'),
    ('qterminal.desktop', 'org.kde.konsole.desktop', 'xfce4-terminal.desktop', 'lxterminal.desktop'),
    ('featherpad.desktop', 'org.kde.kate.desktop', 'mousepad.desktop', 'org.gnome.TextEditor.desktop', 'gedit.desktop'),
    ('libreoffice-startcenter.desktop', 'libreoffice-writer.desktop', 'abiword.desktop'),
)


def default_slices():
    slices = []
    for ids in DEFAULT_PROGRAMS:
        slices.append({'type': 'app', 'ids': list(ids)})
    slices.append({'type': 'action', 'action': 'screenshot'})
    slices.append({'type': 'action', 'action': 'settings'})
    slices.append({'type': 'category', 'category': 'Edukasaun', 'name': 'Learning', 'icon': 'applications-education'})
    return slices


def read_config():
    try:
        data = json.loads(QUICK_FILE.read_text(encoding='utf-8'))
        data = data if isinstance(data, dict) else {}
    except Exception:
        data = {}
    data.setdefault('enabled', True)
    if data.get('hotkey') not in dict(HOTKEYS):
        data['hotkey'] = HOTKEYS[0][0]
    data.setdefault('numbers', True)
    if data.get('position') not in dict(POSITIONS):
        data['position'] = 'center' if data.get('centered') else 'mouse'
    if data.get('look') not in dict(LOOKS):
        data['look'] = 'glass'
    try:
        data['count'] = max(MIN_SLICES, min(MAX_SLICES, int(data.get('count', 8))))
    except (TypeError, ValueError):
        data['count'] = 8
    data.setdefault('auto_fill', True)
    if not isinstance(data.get('slices'), list) or not data['slices']:
        data['slices'] = default_slices()
    return data


def save_config(data, reload=True):
    data = dict(data)
    data['slices'] = [s for s in data.get('slices', []) if isinstance(s, dict)][:MAX_SLICES]
    data.pop('centered', None)
    write_json(QUICK_FILE, data)
    if reload:
        send_menu_command('quick-reload')
    return data


def effective_slices(cfg=None):
    """The slices shown: the chosen ones (installed), then - with auto_fill -
    the programs used most and the favorites, up to the number chosen."""
    cfg = cfg or read_config()
    count = cfg.get('count', 8)
    out, seen = [], set()
    for s in cfg.get('slices', []):
        if len(out) >= count:
            break
        if resolve(s) is None:
            continue
        out.append(s)
        if s.get('type') == 'app':
            app = find_app(s)
            if app: seen.add((app.get('desktop_id') or '').lower())
    if cfg.get('auto_fill', True) and len(out) < count:
        from eduka_common import most_used_ids, read_favorites
        by_id = apps_by_id()
        favs = []
        for f in read_favorites():
            key = str(f.get('desktop_id') if isinstance(f, dict) else f or '')
            favs.append(os.path.basename(key).lower())
        for did in most_used_ids(24) + favs:
            did = (did or '').lower()
            if len(out) >= count:
                break
            if did and did not in seen and did in by_id:
                out.append({'type': 'app', 'ids': [did], 'auto': True}); seen.add(did)
    return out


def app_in_quick(app):
    did = (app or {}).get('desktop_id', '').lower()
    for s in read_config().get('slices', []):
        if s.get('type') == 'app' and did in [str(i).lower() for i in s.get('ids') or [s.get('id', '')]]:
            if find_app(s) and (find_app(s).get('desktop_id') or '').lower() == did:
                return True
    return False


def add_app(app):
    """Eduka-Desktop → right-click → Add to Eduka-Quick. False when full."""
    did = (app or {}).get('desktop_id')
    if not did or app_in_quick(app):
        return bool(did)
    cfg = read_config()
    pinned = [s for s in cfg['slices'] if resolve(s) is not None]
    if len(pinned) >= MAX_SLICES:
        return False
    cfg['slices'].append({'type': 'app', 'ids': [did]})
    if len(pinned) + 1 > cfg['count']:
        cfg['count'] = min(MAX_SLICES, len(pinned) + 1)
    save_config(cfg)
    return True


def remove_app(app):
    did = (app or {}).get('desktop_id', '').lower()
    cfg = read_config()
    keep = []
    for s in cfg['slices']:
        found = find_app(s) if s.get('type') == 'app' else None
        if found and (found.get('desktop_id') or '').lower() == did:
            continue
        keep.append(s)
    cfg['slices'] = keep
    save_config(cfg)
    return True


# ---------------------------------------------------------------- slices
_APPS = {'stamp': 0, 'by_id': {}, 'list': []}

def apps_by_id():
    if time.monotonic() - _APPS['stamp'] > 20 or not _APPS['by_id']:
        try:
            apps = load_apps()
        except Exception:
            apps = []
        _APPS.update(stamp=time.monotonic(), list=apps,
                     by_id={(a.get('desktop_id') or '').lower(): a for a in apps if a.get('desktop_id')})
    return _APPS['by_id']


def find_app(slice_):
    by_id = apps_by_id()
    for i in slice_.get('ids') or [slice_.get('id', '')]:
        app = by_id.get(str(i).lower())
        if app:
            return app
    return None


def category_apps(category, limit=8):
    """The first programs of an Eduka-Desktop category (as the menu sorts them)."""
    from eduka_common import filter_apps
    apps_by_id()
    try:
        return filter_apps(_APPS['list'], category)[:limit]
    except Exception:
        return []


def categories():
    """(name, icon) of the Eduka-Desktop categories, for groups."""
    from eduka_common import CATEGORY_ORDER
    out = [('Edukasaun', 'applications-education')]
    out += [(name, icon) for name, icon, _needles in CATEGORY_ORDER if name not in ('Edukasaun', 'All', 'Favorites')]
    return out


def resolve(slice_):
    """(name, icon name, kind, payload) of a slice, or None when its program
    is not installed. kind: app | action | group."""
    kind = slice_.get('type')
    if kind == 'app':
        app = find_app(slice_)
        if app:
            return (app.get('name', ''), app.get('icon', ''), 'app', app)
    elif kind == 'action' and slice_.get('action') in ACTIONS:
        name, icon, _hint = ACTIONS[slice_['action']]
        return (_(name), icon, 'action', slice_['action'])
    elif kind == 'category':
        apps = category_apps(str(slice_.get('category', '')))
        if apps:
            items = [{'type': 'app', 'ids': [a.get('desktop_id')]} for a in apps]
            return (_(slice_.get('name') or slice_.get('category')), slice_.get('icon') or 'applications-other', 'group', items)
    elif kind == 'group':
        items = [s for s in slice_.get('items', []) if isinstance(s, dict)]
        if items:
            return (str(slice_.get('name') or _('Group')), slice_.get('icon') or 'folder', 'group', items)
    return None


def describe_slice(slice_):
    """Name and icon for the settings list, also when not installed."""
    r = resolve(slice_)
    if r:
        return r[0], r[1], True
    if slice_.get('type') == 'app':
        ident = (slice_.get('ids') or [slice_.get('id', '?')])[0]
        return ident.replace('.desktop', ''), 'application-x-executable', False
    return str(slice_.get('name') or slice_.get('category') or slice_.get('action') or '?'), 'dialog-question', False


def run_action(action):
    if action == 'menu':
        return send_menu_command('show')
    if action == 'settings':
        return safe_popen(['eduka-settings'])
    if action == 'quick-settings':
        return safe_popen(['eduka-settings', '--page', 'quick'])
    if action == 'screenshot':
        for cmd in (['screengrab', '-f'], ['flameshot', 'gui'], ['spectacle'], ['xfce4-screenshooter']):
            if shutil.which(cmd[0]):
                return safe_popen(cmd)
        return False
    if action == 'lock':
        return safe_popen(['eduka-session-action', '--now', 'lock'])
    if action == 'logout':
        return safe_popen(['eduka-session-action', 'shutdown'])
    if action == 'files':
        return safe_popen(['xdg-open', str(Path.home())])
    return False


# ---------------------------------------------------------------- hotkey
def _shortcut_file():
    cfg = os.environ.get('XDG_CONFIG_HOME') or str(Path.home()/'.config')
    return Path(cfg)/'lxqt'/'globalkeyshortcuts.conf'


def _encode(shortcut):
    return shortcut.replace('+', '%2B')


def hotkey_entry():
    """(section, id, shortcut, enabled) of the Eduka-Quick shortcut, or None."""
    path = _shortcut_file()
    if not path.is_file():
        return None
    parser = configparser.RawConfigParser(strict=False, interpolation=None)
    parser.optionxform = str
    try:
        parser.read(str(path), encoding='utf-8')
    except configparser.Error:
        return None
    for section in parser.sections():
        if parser.get(section, 'Comment', fallback='') == SHORTCUT_COMMENT:
            m = re.match(r'^(.*)\.(\d+)$', section)
            key = (m.group(1) if m else section).replace('%2B', '+')
            return section, int(m.group(2)) if m else None, key, parser.get(section, 'Enabled', fallback='true') == 'true'
    return None


def _globalkeys():
    try:
        from PyQt5.QtDBus import QDBusConnection, QDBusInterface
        iface = QDBusInterface('org.lxqt.global_key_shortcuts', '/native', 'org.lxqt.global_key_shortcuts.native',
                               QDBusConnection.sessionBus())
        return iface if iface.isValid() else None
    except Exception:
        return None


def apply_hotkey(enabled, shortcut):
    """Eduka-Quick on its key in lxqt-globalkeys: through D-Bus while the
    daemon runs (it keeps its own file), otherwise in the file it reads at
    the next login."""
    entry = hotkey_entry()
    iface = _globalkeys()
    if iface is not None:
        try:
            from PyQt5.QtDBus import QDBusArgument
            from PyQt5.QtCore import QMetaType
            if entry and entry[1] is not None:
                ident = entry[1]
                if entry[2] != shortcut:
                    iface.call('changeShortcut', _ulong(ident), shortcut)
                iface.call('enableAction', _ulong(ident), bool(enabled))
                return True
            if enabled:
                args = QDBusArgument(); args.add([], QMetaType.QStringList)
                reply = iface.call('addCommandAction', shortcut, 'eduka-quick', args, SHORTCUT_COMMENT)
                return not reply.errorMessage()
            return True
        except Exception:
            pass
    return _write_hotkey_file(enabled, shortcut)


def _ulong(value):
    from PyQt5.QtCore import QVariant
    v = QVariant(int(value))
    v.convert(QVariant.ULongLong)
    return v


def _write_hotkey_file(enabled, shortcut):
    path = _shortcut_file()
    text = path.read_text(encoding='utf-8', errors='ignore') if path.is_file() else ''
    entry = hotkey_entry()
    if entry:
        section = entry[0]
        lines, out, inside = text.splitlines(), [], False
        for line in lines:
            s = line.strip()
            if s.startswith('[') and s.endswith(']'):
                inside = s[1:-1] == section
                if inside:
                    ident = entry[1] if entry[1] is not None else 950
                    line = f'[{_encode(shortcut)}.{ident}]'
            elif inside and s.startswith('Enabled='):
                line = f'Enabled={"true" if enabled else "false"}'
            out.append(line)
        text = '\n'.join(out) + '\n'
    elif enabled:
        if not text:
            for folder in ('/etc/xdg/lxqt', '/usr/share/lxqt'):
                src = Path(folder)/'globalkeyshortcuts.conf'
                if src.is_dir(): src = src/'globalkeyshortcuts.conf'
                if src.is_file():
                    text = src.read_text(encoding='utf-8', errors='ignore'); break
        text = text.rstrip('\n') + ('\n\n' if text else '') + \
            f'[{_encode(shortcut)}.950]\nComment={SHORTCUT_COMMENT}\nEnabled=true\nExec=eduka-quick\n'
    else:
        return True
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix('.eduka-tmp'); tmp.write_text(text, encoding='utf-8'); os.replace(tmp, path)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------- the pie
try:
    from PyQt5.QtWidgets import QWidget, QApplication
    from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, QPoint, QVariantAnimation, QEasingCurve, QSize
    from PyQt5.QtGui import (QPainter, QColor, QPen, QFont, QFontMetrics, QRadialGradient, QLinearGradient,
                             QPainterPath, QPainterPathStroker, QRegion, QCursor, QPixmap)
except Exception:          # the settings helpers above work without a display
    QWidget = object


def _sector(cx, cy, r_in, r_out, a0, a1, round_px):
    """A ring slice from angle a0 to a1 (degrees, clockwise from the top)
    with rounded corners: a smaller slice, stroked with round joins."""
    rc = max(0.0, min(round_px, (r_out - r_in) / 2.0 - 0.5))
    mid = (r_in + r_out) / 2.0
    pad = math.degrees(rc / max(mid, 1.0))
    if a1 - a0 - 2 * pad <= 1.0:
        rc, pad = 0.0, 0.0
    b0, b1 = a0 + pad, a1 - pad
    ri, ro = r_in + rc, r_out - rc
    def pt(r, a):
        t = math.radians(a - 90)
        return QPointF(cx + r * math.cos(t), cy + r * math.sin(t))
    core = QPainterPath()
    core.moveTo(pt(ri, b0)); core.lineTo(pt(ro, b0))
    core.arcTo(QRectF(cx - ro, cy - ro, 2 * ro, 2 * ro), 90 - b0, -(b1 - b0))
    core.lineTo(pt(ri, b1))
    core.arcTo(QRectF(cx - ri, cy - ri, 2 * ri, 2 * ri), 90 - b1, (b1 - b0))
    core.closeSubpath()
    if rc <= 0:
        return core
    stroker = QPainterPathStroker(); stroker.setWidth(2 * rc)
    stroker.setJoinStyle(Qt.RoundJoin); stroker.setCapStyle(Qt.RoundCap)
    return core.united(stroker.createStroke(core)).simplified()


class QuickPie(QWidget):
    """Eduka-Quick: colored glass slices around a clear center that names the
    chosen one. Hold and drag (or drag the center) to move it."""

    def __init__(self, preview=False):
        flags = Qt.Widget if preview else (Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        super().__init__(None, flags)
        self.preview = preview
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName('Eduka-Quick')
        self.stack = []          # earlier slice lists while a group is open
        self.items = []          # [(name, icon, kind, payload, QPixmap)]
        self.pops = []           # how far each slice stands out (0 - 1)
        self.active = -1
        self.progress = 0.0
        self.cfg = read_config()
        self.sf = 1.0
        self.geo = {}
        self.anim = QVariantAnimation(self); self.anim.setDuration(230); self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.valueChanged.connect(self._set_progress)
        self.anim.finished.connect(self._anim_done)
        self.closing = False
        self.hover_timer = QTimer(self); self.hover_timer.setInterval(16); self.hover_timer.timeout.connect(self._step)
        self.hold_timer = QTimer(self); self.hold_timer.setSingleShot(True); self.hold_timer.setInterval(420)
        self.hold_timer.timeout.connect(self._start_drag)
        self.launch_fx = None
        self.press = None; self.dragging = False; self.drag_offset = QPoint()
        self.translucent = preview or (compositor_running() and self.cfg.get('look') != 'solid')
        if self.translucent:
            self.setAttribute(Qt.WA_TranslucentBackground)

    # -- size (follows the screen and the number of slices)
    def layout_for(self, n, screen=None):
        if screen is not None:
            g = screen.availableGeometry()
            self.sf = max(0.78, min(1.25, min(g.height() / 900.0, g.width() / 1440.0)))
        sf = self.sf; n = max(1, n)
        depth = 76 * sf
        r_center = 58 * sf
        # Up to 8 slices the names fit inside; with more only the icons.
        r_mid = max(r_center + 14 * sf + depth / 2, (13.5 if n <= 8 else 11.0) * n * sf + 8 * sf)
        r_in = r_mid - depth / 2; r_out = r_mid + depth / 2
        pop = 9 * sf
        size = int(2 * (r_out + pop + 16 * sf))
        self.geo = dict(depth=depth, r_center=r_center, r_in=r_in, r_out=r_out, r_mid=r_mid, pop=pop,
                        icon=max(24, min(46, int(depth * 0.48))), gap=7 * sf, round=12 * sf)
        self.setFixedSize(size, size)
        if not self.translucent and not self.preview:
            # Without a compositor: a round window, no black corners.
            m = int(16 * sf) - 4
            self.setMask(QRegion(QRectF(m, m, size - 2 * m, size - 2 * m).toRect(), QRegion.Ellipse))

    # -- content
    def load(self, slices=None):
        self.cfg = read_config()
        slices = slices if slices is not None else effective_slices(self.cfg)
        items = []
        for s in slices:
            r = resolve(s)
            if r:
                pix = get_icon(r[1], 'application-x-executable').pixmap(QSize(96, 96))
                items.append(r + (pix,))
        self.items = items[:MAX_SLICES]
        self.pops = [0.0] * len(self.items)
        self.active = -1
        self.layout_for(len(self.items))      # the scale of popup()'s screen
        self.update()

    def popup(self, pos=None):
        self.stack = []
        self.cfg = read_config()
        cursor = pos or QCursor.pos()
        screen = QApplication.screenAt(cursor) or QApplication.primaryScreen()
        self.layout_for(1, screen)
        self.load()
        if not self.items:
            return False
        area = screen.availableGeometry()
        mode = self.cfg.get('position', 'mouse')
        last = self.cfg.get('last_pos')
        if mode == 'center':
            center = area.center()
        elif mode == 'last' and isinstance(last, list) and len(last) == 2:
            center = QPoint(int(last[0]), int(last[1]))
        else:
            center = cursor
        self.place(center, area)
        self.closing = False; self.press = None; self.dragging = False; self.launch_fx = None
        self.progress = 0.0
        self.show(); self.raise_(); self.activateWindow(); self.setFocus()
        self.anim.stop(); self.anim.setEasingCurve(QEasingCurve.OutBack); self.anim.setDuration(230)
        self.anim.setStartValue(0.0); self.anim.setEndValue(1.0); self.anim.start()
        self.hover_timer.start()
        self._pick(self.mapFromGlobal(QCursor.pos()))
        return True

    def place(self, center, area=None):
        area = area or (QApplication.screenAt(center) or QApplication.primaryScreen()).availableGeometry()
        x = min(max(center.x() - self.width() // 2, area.left()), area.right() - self.width())
        y = min(max(center.y() - self.height() // 2, area.top()), area.bottom() - self.height())
        self.move(x, y)

    def close_pie(self):
        if self.closing:
            return
        self.closing = True; self.hold_timer.stop()
        self.anim.stop(); self.anim.setEasingCurve(QEasingCurve.InCubic); self.anim.setDuration(130)
        self.anim.setStartValue(self.progress); self.anim.setEndValue(0.0); self.anim.start()

    def _anim_done(self):
        if self.closing:
            self.hover_timer.stop(); self.hide(); self.closing = False

    def _set_progress(self, value):
        self.progress = float(value); self.update()

    # -- geometry
    def center(self):
        return QPointF(self.width() / 2, self.height() / 2)

    def angle_of(self, i):
        """Middle of slice i in degrees, clockwise from the top."""
        n = max(1, len(self.items))
        return 360.0 * i / n

    def slice_at(self, point):
        c = self.center(); dx = point.x() - c.x(); dy = point.y() - c.y()
        dist = math.hypot(dx, dy)
        if not self.items or dist < self.geo.get('r_center', 58) + 4:
            return -1
        n = len(self.items)
        a = (math.degrees(math.atan2(dy, dx)) + 90) % 360
        return int((a + 180.0 / n) // (360.0 / n)) % n

    def in_center(self, point):
        c = self.center()
        return math.hypot(point.x() - c.x(), point.y() - c.y()) <= self.geo.get('r_center', 58) + 2

    def _pick(self, point):
        i = self.slice_at(point)
        if i != self.active:
            self.active = i
            name = self.items[i][0] if 0 <= i < len(self.items) else ''
            self.setAccessibleDescription(name)
            self.update()
        self.setCursor(Qt.ClosedHandCursor if self.dragging else
                       (Qt.OpenHandCursor if self.in_center(point) else Qt.PointingHandCursor))

    def _step(self):
        moving = False
        for i in range(len(self.pops)):
            target = 1.0 if i == self.active else 0.0
            cur = self.pops[i]
            if abs(cur - target) > 0.01:
                self.pops[i] = cur + (target - cur) * 0.3; moving = True
        if self.launch_fx is not None:
            self.launch_fx = min(1.0, self.launch_fx + 0.09); moving = True
        if moving:
            self.update()

    # -- moving (hold and drag, or drag the center)
    def _start_drag(self):
        if self.press is not None and not self.preview:
            self.dragging = True
            self.drag_offset = QCursor.pos() - self.pos()
            self.setCursor(Qt.ClosedHandCursor); self.update()

    def _end_drag(self):
        self.dragging = False
        c = self.geometry().center()
        cfg = read_config(); cfg['position'] = 'last'; cfg['last_pos'] = [c.x(), c.y()]
        save_config(cfg, reload=False)
        self.cfg = cfg

    # -- input
    def mouseMoveEvent(self, e):
        if self.press is not None and (e.buttons() & Qt.LeftButton) and not self.dragging:
            if self.in_center(self.press) and (e.pos() - self.press).manhattanLength() > 6:
                self.hold_timer.stop(); self._start_drag()
        if self.dragging:
            self.move(QCursor.pos() - self.drag_offset); return
        self._pick(e.pos())

    def mousePressEvent(self, e):
        if not self.rect().contains(e.pos()) and not self.preview:
            self.close_pie(); return
        if e.button() == Qt.RightButton:
            self.back_or_close(); return
        if e.button() == Qt.LeftButton:
            self.press = e.pos(); self.hold_timer.start()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        self.hold_timer.stop()
        if self.dragging:
            self._end_drag(); self.press = None; self._pick(e.pos()); return
        self.press = None
        i = self.slice_at(e.pos())
        if i >= 0:
            self.activate(i)
        elif self.in_center(e.pos()):
            self.back_or_close()

    def keyPressEvent(self, e):
        k = e.key(); n = len(self.items)
        if k in (Qt.Key_Escape, Qt.Key_Backspace):
            self.back_or_close()
        elif k in (Qt.Key_Right, Qt.Key_Down, Qt.Key_Tab) and n:
            self.active = (self.active + 1) % n if self.active >= 0 else 0; self._announce()
        elif k in (Qt.Key_Left, Qt.Key_Up, Qt.Key_Backtab) and n:
            self.active = (self.active - 1) % n if self.active >= 0 else n - 1; self._announce()
        elif k in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space) and self.active >= 0:
            self.activate(self.active)
        elif Qt.Key_1 <= k <= Qt.Key_9 and k - Qt.Key_1 < n:
            self.activate(k - Qt.Key_1)
        else:
            super().keyPressEvent(e)

    def _announce(self):
        self.setAccessibleDescription(self.items[self.active][0] if 0 <= self.active < len(self.items) else '')
        self.update()

    def back_or_close(self):
        if self.stack:
            center = self.geometry().center()
            self.load(self.stack.pop()); self.place(center)
            self.progress = 0.6
            self.anim.stop(); self.anim.setStartValue(0.6); self.anim.setEndValue(1.0); self.anim.start()
        else:
            self.close_pie()

    def activate(self, i):
        if self.preview or not (0 <= i < len(self.items)):
            return
        name, _icon, kind, payload, _pix = self.items[i]
        if kind == 'group':
            current = []
            for it in self.items:
                if it[2] == 'app': current.append({'type': 'app', 'ids': [it[3].get('desktop_id')]})
                elif it[2] == 'action': current.append({'type': 'action', 'action': it[3]})
            center = self.geometry().center()
            self.stack.append(current)
            self.load(payload); self.place(center)
            self.progress = 0.5
            self.anim.stop(); self.anim.setStartValue(0.5); self.anim.setEndValue(1.0); self.anim.start()
            self._pick(self.mapFromGlobal(QCursor.pos()))
            return
        self.active = i; self.launch_fx = 0.0
        QTimer.singleShot(150, lambda: self._run(kind, payload))
        QTimer.singleShot(110, self.close_pie)

    def _run(self, kind, payload):
        if kind == 'app':
            launch_entry(payload)
        elif kind == 'action':
            run_action(payload)

    # -- painting
    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
        dark = is_dark_theme()
        accent = QColor(theme_accent() or '#3fa684')
        g = self.geo or {}
        prog = max(0.0, self.progress)
        c = self.center(); sf = self.sf
        p.translate(c); p.scale(0.74 + 0.26 * prog, 0.74 + 0.26 * prog); p.rotate(-14 * (1 - min(1.0, prog))); p.translate(-c)
        p.setOpacity(min(1.0, max(0.0, prog)))
        glass = self.translucent
        r_out = g.get('r_out', 150)
        # Without a compositor: one calm disc behind the slices.
        if not glass:
            p.setPen(Qt.NoPen); p.setBrush(QColor('#20262a' if dark else '#f4f8f6'))
            p.drawEllipse(c, r_out + g.get('pop', 9) + 8 * sf, r_out + g.get('pop', 9) + 8 * sf)
        else:
            halo = QRadialGradient(c, r_out + 16 * sf)
            halo.setColorAt(0.80, QColor(0, 0, 0, 34)); halo.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setPen(Qt.NoPen); p.setBrush(halo); p.drawEllipse(c, r_out + 16 * sf, r_out + 16 * sf)
        n = len(self.items)
        text_dark = QColor('#1f3a34')
        for i, item in enumerate(self.items):
            mid = self.angle_of(i); span = 360.0 / max(1, n)
            gap_deg = math.degrees(g.get('gap', 7) / max(g.get('r_mid', 120), 1)) if n > 1 else 0
            a0 = mid - span / 2 + gap_deg / 2; a1 = mid + span / 2 - gap_deg / 2
            pop = self.pops[i] if i < len(self.pops) else 0.0
            off = g.get('pop', 9) * pop
            if i == self.active and self.launch_fx is not None:
                off += g.get('pop', 9) * 2.5 * self.launch_fx
            t = math.radians(mid - 90)
            ox, oy = c.x() + off * math.cos(t), c.y() + off * math.sin(t)
            if n == 1:
                path = QPainterPath(); path.addEllipse(QPointF(ox, oy), g['r_out'], g['r_out'])
                inner = QPainterPath(); inner.addEllipse(QPointF(ox, oy), g['r_in'], g['r_in'])
                path = path.subtracted(inner)
            else:
                path = _sector(ox, oy, g['r_in'], g['r_out'], a0, a1, g.get('round', 12))
            base = QColor(PALETTE[i % len(PALETTE)])
            if dark:
                base = base.darker(118)
            top = QColor(base).lighter(118); low = QColor(base)
            alpha_top, alpha_low = (236, 206) if glass else (255, 255)
            if i == self.active:
                alpha_top, alpha_low = 250, 238
            top.setAlpha(alpha_top); low.setAlpha(alpha_low)
            grad = QLinearGradient(QPointF(ox + g['r_out'] * math.cos(t), oy + g['r_out'] * math.sin(t)),
                                   QPointF(ox + g['r_in'] * math.cos(t), oy + g['r_in'] * math.sin(t)))
            grad.setColorAt(0, top); grad.setColorAt(1, low)
            if i == self.active and self.launch_fx is not None:
                p.save(); p.setOpacity(p.opacity() * max(0.0, 1.0 - self.launch_fx))
            edge = QColor(255, 255, 255, 210 if i == self.active else 140)
            p.setPen(QPen(edge, 2.2 * sf if i == self.active else 1.2 * sf)); p.setBrush(grad)
            p.drawPath(path)
            # icon (and name when the slice is wide enough)
            arc = 2 * math.pi * g['r_mid'] / max(1, n)
            show_name = n <= 8 and arc > 70 * sf
            size = g['icon'] * (1.0 + 0.16 * pop)
            ix = ox + g['r_mid'] * math.cos(t); iy = oy + g['r_mid'] * math.sin(t) - (8 * sf if show_name else 0)
            p.drawPixmap(QRectF(ix - size / 2, iy - size / 2, size, size), item[4], QRectF(item[4].rect()))
            if show_name:
                f = QFont(self.font()); f.setPointSizeF(max(7.0, 8.2 * sf)); f.setBold(True); p.setFont(f)
                lum = 0.299 * base.red() + 0.587 * base.green() + 0.114 * base.blue()
                p.setPen(QColor('#ffffff') if lum < 150 else text_dark)
                # Slices at the top and bottom are wide, those at the sides
                # are as wide as the ring is deep.
                wide = abs(math.cos(math.radians(mid)))
                avail = g['depth'] * 0.92 + (arc * 0.78 - g['depth'] * 0.92) * wide
                avail = max(40 * sf, min(avail, 124 * sf))
                label = QFontMetrics(f).elidedText(item[0], Qt.ElideRight, int(avail))
                p.save(); p.setClipPath(path)
                p.drawText(QRectF(ix - avail / 2, iy + size / 2 + 1, avail, 16 * sf), Qt.AlignHCenter | Qt.AlignTop, label)
                p.restore()
            if item[2] == 'group':
                for k in range(3):
                    p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, 230))
                    p.drawEllipse(QPointF(ix - 7 * sf + 7 * sf * k, iy - size / 2 - 5 * sf), 2.2 * sf, 2.2 * sf)
            if self.cfg.get('numbers', True) and i < 9:
                nx = ox + (g['r_out'] - 11 * sf) * math.cos(math.radians(a0 + 9 - 90 + (span * 0.0)))
                ny = oy + (g['r_out'] - 11 * sf) * math.sin(math.radians(a0 + 9 - 90))
                nf = QFont(self.font()); nf.setPointSizeF(max(6.5, 7.2 * sf)); nf.setBold(True); p.setFont(nf)
                p.setPen(QColor(255, 255, 255, 230) if (0.299 * base.red() + 0.587 * base.green() + 0.114 * base.blue()) < 150
                         else QColor(31, 58, 52, 170))
                p.drawText(QRectF(nx - 8 * sf, ny - 8 * sf, 16 * sf, 16 * sf), Qt.AlignCenter, str(i + 1))
            if i == self.active and self.launch_fx is not None:
                p.restore()
        # The clear center: name and what it is.
        rc = g.get('r_center', 58)
        if glass:
            disc = QRadialGradient(QPointF(c.x() - rc * 0.35, c.y() - rc * 0.45), rc * 1.6)
            disc.setColorAt(0.0, QColor(255, 255, 255, 235 if not dark else 120))
            disc.setColorAt(0.55, QColor(255, 255, 255, 175 if not dark else 70))
            disc.setColorAt(1.0, QColor(225, 240, 236, 150 if not dark else 55))
        else:
            disc = QColor('#2b3236' if dark else '#ffffff')
        ring = QColor(accent) if self.dragging else QColor(255, 255, 255, 235)
        p.setPen(QPen(ring, 2.4 * sf)); p.setBrush(disc); p.drawEllipse(c, rc, rc)
        if glass:
            shine = QPainterPath(); shine.addEllipse(QPointF(c.x(), c.y() - rc * 0.45), rc * 0.72, rc * 0.36)
            p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, 60)); p.drawPath(shine)
        ink = QColor('#f1f5f3' if dark and not glass else '#1f3a34')
        if dark and glass: ink = QColor('#ffffff')
        if 0 <= self.active < n:
            name = self.items[self.active][0]
            kind = self.items[self.active][2]
            sub = _('Group') if kind == 'group' else (_('Action') if kind == 'action' else _('Program'))
        elif self.dragging:
            name, sub = _('Moving'), _('Let go to place it')
        else:
            name = _('Back') if self.stack else 'Eduka-Quick'
            sub = _('Hold and drag to move')
        f = QFont(self.font()); f.setBold(True); f.setPointSizeF(max(8.0, 10.0 * sf)); p.setFont(f)
        p.setPen(ink)
        title_box = QRectF(c.x() - rc + 10 * sf, c.y() - rc * 0.62, 2 * rc - 20 * sf, rc * 0.95)
        p.drawText(title_box, Qt.AlignHCenter | Qt.AlignBottom | Qt.TextWordWrap,
                   QFontMetrics(f).elidedText(name, Qt.ElideRight, int(3.2 * rc)))
        sf2 = QFont(self.font()); sf2.setPointSizeF(max(6.5, 7.4 * sf)); p.setFont(sf2)
        soft = QColor(ink); soft.setAlpha(170); p.setPen(soft)
        p.drawText(QRectF(c.x() - rc + 8 * sf, c.y() + rc * 0.36, 2 * rc - 16 * sf, rc * 0.5),
                   Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap, sub)
        # the direction dot on the center ring
        if 0 <= self.active < n:
            t = math.radians(self.angle_of(self.active) - 90)
            p.setPen(Qt.NoPen); p.setBrush(accent)
            p.drawEllipse(QPointF(c.x() + (rc - 1) * math.cos(t), c.y() + (rc - 1) * math.sin(t)), 4.5 * sf, 4.5 * sf)
        p.end()


def preview_pixmap(slices=None, size=220, active=0, cfg=None):
    """A small picture of Eduka-Quick for Eduka-Settings."""
    pie = QuickPie(preview=True)
    pie.layout_for(1, QApplication.primaryScreen())
    pie.load(slices if slices is not None else effective_slices(cfg))
    pie.progress = 1.0; pie.active = active if pie.items else -1
    pie.pops = [1.0 if i == pie.active else 0.0 for i in range(len(pie.items))]
    pix = QPixmap(pie.size()); pix.fill(Qt.transparent)
    pie.render(pix, flags=QWidget.RenderFlags(QWidget.DrawChildren))
    pie.deleteLater()
    return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
