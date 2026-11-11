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
"""
import configparser, json, math, os, re, shutil, time
from pathlib import Path

from eduka_common import (DESKTOP_CONFIG_DIR, write_json, safe_popen, get_icon, theme_accent, is_dark_theme,
                          compositor_running, launch_entry, load_apps, send_menu_command, _)

QUICK_FILE = DESKTOP_CONFIG_DIR/'quick.json'
SHORTCUT_COMMENT = 'Eduka-Quick'
HOTKEYS = (('Meta+Q', 'Super+Q'), ('Control+Alt+Space', 'Ctrl+Alt+Space'), ('Control+Alt+A', 'Ctrl+Alt+A'),
           ('Meta+Space', 'Super+Space'))
MAX_SLICES = 10

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
    data.setdefault('hotkey', HOTKEYS[0][0])
    data.setdefault('centered', False)
    data.setdefault('numbers', True)
    if not isinstance(data.get('slices'), list) or not data['slices']:
        data['slices'] = default_slices()
    return data


def save_config(data):
    data = dict(data)
    data['slices'] = [s for s in data.get('slices', []) if isinstance(s, dict)][:MAX_SLICES]
    write_json(QUICK_FILE, data)
    send_menu_command('quick-reload')
    return data


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
    from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, QVariantAnimation, QEasingCurve, QSize
    from PyQt5.QtGui import (QPainter, QColor, QPen, QFont, QFontMetrics, QRadialGradient, QPainterPath, QRegion,
                             QCursor, QPixmap)
except Exception:          # the settings helpers above work without a display
    QWidget = object


class QuickPie(QWidget):
    """The pie: slices around a center that names the chosen one."""
    RADIUS = 112            # icon centers
    ICON = 44
    SIZE = 380

    def __init__(self, preview=False):
        flags = Qt.Widget if preview else (Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        super().__init__(None, flags)
        self.preview = preview
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName('Eduka-Quick')
        self.translucent = compositor_running() or preview
        if self.translucent:
            self.setAttribute(Qt.WA_TranslucentBackground)
        else:
            # Without a compositor: a round window, no black corners.
            self.setMask(QRegion(QRectF(6, 6, self.SIZE - 12, self.SIZE - 12).toRect(), QRegion.Ellipse))
        self.stack = []          # parent slices when a group is open
        self.items = []          # [(name, icon, kind, payload, QPixmap)]
        self.scales = []
        self.active = -1
        self.progress = 0.0
        self.pressed_at = None
        self.cfg = read_config()
        self.anim = QVariantAnimation(self); self.anim.setDuration(190); self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.valueChanged.connect(self._set_progress)
        self.anim.finished.connect(self._anim_done)
        self.closing = False
        self.hover_timer = QTimer(self); self.hover_timer.setInterval(16); self.hover_timer.timeout.connect(self._step)
        self.launch_fx = None

    # -- content
    def load(self, slices=None):
        self.cfg = read_config()
        slices = slices if slices is not None else self.cfg['slices']
        items = []
        for s in slices:
            r = resolve(s)
            if r:
                pix = get_icon(r[1], 'application-x-executable').pixmap(QSize(64, 64))
                items.append(r + (pix,))
        self.items = items[:MAX_SLICES]
        self.scales = [1.0] * len(self.items)
        self.active = -1
        self.update()

    def popup(self, pos=None):
        self.stack = []
        self.load()
        if not self.items:
            return False
        screen = QApplication.screenAt(pos or QCursor.pos()) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        if self.cfg.get('centered') or pos is None:
            center = area.center()
        else:
            center = pos
        x = min(max(center.x() - self.SIZE // 2, area.left()), area.right() - self.SIZE)
        y = min(max(center.y() - self.SIZE // 2, area.top()), area.bottom() - self.SIZE)
        self.move(x, y)
        self.closing = False; self.pressed_at = None; self.launch_fx = None
        self.progress = 0.0
        self.show(); self.raise_(); self.activateWindow(); self.setFocus()
        self.anim.stop(); self.anim.setEasingCurve(QEasingCurve.OutBack); self.anim.setDuration(190)
        self.anim.setStartValue(0.0); self.anim.setEndValue(1.0); self.anim.start()
        self.hover_timer.start()
        self._pick(self.mapFromGlobal(QCursor.pos()))
        return True

    def close_pie(self):
        if self.closing:
            return
        self.closing = True
        self.anim.stop(); self.anim.setEasingCurve(QEasingCurve.InCubic); self.anim.setDuration(120)
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
        n = max(1, len(self.items))
        return -math.pi / 2 + 2 * math.pi * i / n

    def slice_at(self, point):
        c = self.center(); dx = point.x() - c.x(); dy = point.y() - c.y()
        if math.hypot(dx, dy) < 46 or not self.items:
            return -1
        n = len(self.items)
        a = (math.atan2(dy, dx) + math.pi / 2) % (2 * math.pi)
        return int((a + math.pi / n) // (2 * math.pi / n)) % n

    def _pick(self, point):
        i = self.slice_at(point)
        if i != self.active:
            self.active = i
            name = self.items[i][0] if 0 <= i < len(self.items) else ''
            self.setAccessibleDescription(name)
            self.update()

    def _step(self):
        moving = False
        for i in range(len(self.scales)):
            target = 1.32 if i == self.active else (0.92 if self.active >= 0 else 1.0)
            cur = self.scales[i]
            if abs(cur - target) > 0.004:
                self.scales[i] = cur + (target - cur) * 0.28; moving = True
        if self.launch_fx is not None:
            self.launch_fx = min(1.0, self.launch_fx + 0.09); moving = True
        if moving:
            self.update()

    # -- input
    def mouseMoveEvent(self, e):
        self._pick(e.pos())

    def mousePressEvent(self, e):
        if not self.rect().contains(e.pos()) and not self.preview:
            self.close_pie(); return
        self.pressed_at = e.pos()
        if e.button() == Qt.RightButton:
            self.back_or_close()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        i = self.slice_at(e.pos())
        if i >= 0:
            self.activate(i)
        elif math.hypot(e.pos().x() - self.center().x(), e.pos().y() - self.center().y()) < 46:
            self.back_or_close()

    def keyPressEvent(self, e):
        k = e.key(); n = len(self.items)
        if k == Qt.Key_Escape:
            self.back_or_close()
        elif k == Qt.Key_Backspace:
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
            self.load(self.stack.pop()); self.progress = 0.6
            self.anim.stop(); self.anim.setStartValue(0.6); self.anim.setEndValue(1.0); self.anim.start()
        else:
            self.close_pie()

    def activate(self, i):
        if self.preview or not (0 <= i < len(self.items)):
            return
        name, _icon, kind, payload, _pix = self.items[i]
        if kind == 'group':
            current = [{'type': 'app', 'ids': [it[3].get('desktop_id')]} if it[2] == 'app' else
                       ({'type': 'action', 'action': it[3]} if it[2] == 'action' else None) for it in self.items]
            self.stack.append(self.cfg['slices'] if not self.stack else [c for c in current if c])
            self.load(payload); self.progress = 0.5
            self.anim.stop(); self.anim.setStartValue(0.5); self.anim.setEndValue(1.0); self.anim.start()
            self._pick(self.mapFromGlobal(QCursor.pos()))
            return
        self.active = i; self.launch_fx = 0.0
        QTimer.singleShot(150, lambda: self._run(kind, payload))
        QTimer.singleShot(90, self.close_pie)

    def _run(self, kind, payload):
        if kind == 'app':
            launch_entry(payload)
        elif kind == 'action':
            run_action(payload)

    def focusOutEvent(self, e):
        super().focusOutEvent(e)

    # -- painting
    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
        dark = is_dark_theme()
        accent = QColor(theme_accent() or '#3fa684')
        prog = max(0.0, self.progress)
        c = self.center()
        p.translate(c); p.scale(0.72 + 0.28 * prog, 0.72 + 0.28 * prog); p.translate(-c)
        p.setOpacity(min(1.0, max(0.0, prog)))
        outer = self.SIZE / 2 - 10
        bg = QColor('#20262a' if dark else '#fbfdfc')
        if self.translucent:
            shadow = QRadialGradient(c, outer + 8)
            shadow.setColorAt(0.86, QColor(0, 0, 0, 60)); shadow.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setPen(Qt.NoPen); p.setBrush(shadow); p.drawEllipse(c, outer + 8, outer + 8)
            bg.setAlpha(246)
        p.setPen(QPen(QColor(255, 255, 255, 40) if dark else QColor(0, 0, 0, 28), 1)); p.setBrush(bg)
        p.drawEllipse(c, outer, outer)
        n = len(self.items)
        # The chosen direction: a soft wedge and an arc on the rim.
        if 0 <= self.active < n:
            span = 360.0 / n
            start = -math.degrees(self.angle_of(self.active)) - span / 2
            wedge = QPainterPath(); wedge.moveTo(c)
            wedge.arcTo(QRectF(c.x() - outer, c.y() - outer, 2 * outer, 2 * outer), start, span); wedge.closeSubpath()
            fill = QColor(accent); fill.setAlpha(46 if dark else 34)
            p.setPen(Qt.NoPen); p.setBrush(fill); p.drawPath(wedge)
            p.setPen(QPen(accent, 5, Qt.SolidLine, Qt.RoundCap)); p.setBrush(Qt.NoBrush)
            p.drawArc(QRectF(c.x() - outer + 4, c.y() - outer + 4, 2 * outer - 8, 2 * outer - 8), int(start * 16 + 40), int(span * 16 - 80))
        # Center: the name of the chosen slice.
        inner = 56
        p.setPen(QPen(accent if self.active >= 0 else (QColor(255, 255, 255, 50) if dark else QColor(0, 0, 0, 30)), 2))
        p.setBrush(QColor('#2b3236') if dark else QColor('#ffffff')); p.drawEllipse(c, inner, inner)
        text_color = QColor('#f1f5f3' if dark else '#24403a')
        if 0 <= self.active < n:
            a = self.angle_of(self.active)
            tip = QPointF(c.x() + math.cos(a) * (inner - 6), c.y() + math.sin(a) * (inner - 6))
            p.setPen(Qt.NoPen); p.setBrush(accent); p.drawEllipse(tip, 4, 4)
            name = self.items[self.active][0]
        else:
            name = _('Back') if self.stack else 'Eduka-Quick'
        f = QFont(self.font()); f.setBold(True); f.setPointSizeF(max(8.0, f.pointSizeF() * 0.95)); p.setFont(f)
        p.setPen(text_color)
        p.drawText(QRectF(c.x() - inner + 8, c.y() - inner + 8, 2 * inner - 16, 2 * inner - 16),
                   Qt.AlignCenter | Qt.TextWordWrap, QFontMetrics(f).elidedText(name, Qt.ElideRight, int(3 * inner)))
        # Slices.
        for i, item in enumerate(self.items):
            a = self.angle_of(i); s = self.scales[i] if i < len(self.scales) else 1.0
            size = self.ICON * s
            pos = QPointF(c.x() + math.cos(a) * self.RADIUS, c.y() + math.sin(a) * self.RADIUS)
            if i == self.active:
                halo = QColor(accent); halo.setAlpha(60)
                p.setPen(Qt.NoPen); p.setBrush(halo); p.drawEllipse(pos, size * 0.66, size * 0.66)
            if i == self.active and self.launch_fx is not None:
                p.save(); p.setOpacity(max(0.0, 1.0 - self.launch_fx))
                grow = size * (1 + self.launch_fx)
                p.drawPixmap(QRectF(pos.x() - grow / 2, pos.y() - grow / 2, grow, grow), item[4], QRectF(item[4].rect()))
                p.restore()
            else:
                p.drawPixmap(QRectF(pos.x() - size / 2, pos.y() - size / 2, size, size), item[4], QRectF(item[4].rect()))
            if item[2] == 'group':
                dot = QPointF(pos.x() + size * 0.42, pos.y() + size * 0.42)
                p.setPen(QPen(bg, 2)); p.setBrush(accent); p.drawEllipse(dot, 6, 6)
            if self.cfg.get('numbers', True) and i < 9:
                num = QPointF(c.x() + math.cos(a) * (self.RADIUS + 46), c.y() + math.sin(a) * (self.RADIUS + 46))
                nf = QFont(self.font()); nf.setPointSizeF(max(7.0, nf.pointSizeF() * 0.8)); p.setFont(nf)
                p.setPen(QColor(text_color.red(), text_color.green(), text_color.blue(), 120))
                p.drawText(QRectF(num.x() - 9, num.y() - 9, 18, 18), Qt.AlignCenter, str(i + 1))
        p.end()


def preview_pixmap(slices, size=220, active=0):
    """A small picture of the pie for Eduka-Settings."""
    pie = QuickPie(preview=True)
    pie.load(slices)
    pie.progress = 1.0; pie.active = active if pie.items else -1
    pie.scales = [1.32 if i == pie.active else 0.92 for i in range(len(pie.items))]
    pix = QPixmap(pie.size()); pix.fill(Qt.transparent)
    pie.render(pix, flags=QWidget.RenderFlags(QWidget.DrawChildren))
    pie.deleteLater()
    return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
