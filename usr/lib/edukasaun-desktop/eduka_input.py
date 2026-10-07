"""Keyboard, mouse and touchpad of Eduka-Desktop (taken over from LXQt's
input settings).

The settings live in ~/.config/eduka-desktop/input.json. Eduka-Settings
applies every change at once; Eduka-Panel applies them again when the session
starts and whenever a mouse, touchpad or keyboard is plugged in.

* Keyboard: layouts and the key that switches between them (setxkbmap),
  key repeat delay and speed (xset r rate), Num Lock (numlockx).
* Mouse and touchpad: libinput properties set with xinput (speed, left-handed
  buttons, natural scrolling, tap to click, disable while typing, scrolling
  method, touchpad on/off). Without xinput the speed falls back to xset m.
* Double-click time and wheel lines: Qt (lxqt.conf) and GTK (settings.ini).

The same values are written to LXQt's session.conf, so lxqt-session does not
bring old values back at the next login.
"""
import os, re, shutil, subprocess
from pathlib import Path

from eduka_common import BASE_CONFIG, read_json, write_json, _set_ini_value, _get_ini_value


def _set_ini(path, section, key, value):
    """Writes only when the value changes: Eduka-Panel watches lxqt.conf and
    the GTK settings for theme changes."""
    if _get_ini_value(path, section, key) != str(value):
        _set_ini_value(path, section, key, str(value))

INPUT_CONFIG = BASE_CONFIG/'input.json'
EVDEV_LST = Path('/usr/share/X11/xkb/rules/evdev.lst')

DEFAULTS = {
    'layouts': [],            # [] = keep the layout the system set up (installer / keyboard-configuration)
    'switch': 'grp:alt_shift_toggle',
    'repeat_delay': 500, 'repeat_rate': 30, 'numlock': False,
    'mouse_speed': 0.0, 'left_handed': False, 'mouse_natural': False, 'middle_emulation': False,
    'double_click': 400, 'wheel_lines': 3,
    'tp_enabled': True, 'tp_tap': True, 'tp_natural': True, 'tp_dwt': True, 'tp_speed': 0.0,
    'tp_scroll': 'two-finger', 'tp_icon': True,
}

SWITCH_KEYS = [('grp:alt_shift_toggle', 'Alt + Shift'), ('grp:win_space_toggle', 'Super + Space'),
               ('grp:ctrl_shift_toggle', 'Ctrl + Shift'), ('grp:alts_toggle', 'Both Alt keys'),
               ('grp:caps_toggle', 'Caps Lock'), ('', 'No key (use Eduka-Panel)')]
SCROLL_METHODS = [('two-finger', 'Two fingers'), ('edge', 'Right edge'), ('none', 'No scrolling')]

TOUCHPAD_NAME = re.compile(r'touch\s*pad|trackpad|glidepoint|synaptics|alps|elan\s*\d*\s*:?\s*tp|\bTP\b', re.I)
SKIP_POINTER = re.compile(r'XTEST|Virtual core|Video Bus|Power Button|Sleep Button|Lid Switch|\bkeyboard\b|consumer control|system control|wmi hotkeys', re.I)


def input_config():
    cfg = dict(DEFAULTS)
    data = read_json(INPUT_CONFIG, {})
    if isinstance(data, dict):
        cfg.update({k: v for k, v in data.items() if k in DEFAULTS})
    return cfg


def save_input_config(cfg):
    write_json(INPUT_CONFIG, {k: cfg.get(k, v) for k, v in DEFAULTS.items()})


def _run(args, timeout=3):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None


# ------------------------------------------------------------------ keyboard
def keyboard_layouts():
    """[(code, name)] from xkb's evdev.lst, sorted by name."""
    out = []; section = ''
    try:
        for line in EVDEV_LST.read_text(encoding='utf-8', errors='ignore').splitlines():
            if line.startswith('!'):
                section = line[1:].strip(); continue
            if section == 'layout' and line.strip():
                code, _sp, name = line.strip().partition(' ')
                out.append((code, name.strip()))
    except Exception:
        pass
    if not out:
        out = [('us', 'English (US)'), ('pt', 'Portuguese'), ('br', 'Portuguese (Brazil)'), ('gb', 'English (UK)'), ('id', 'Indonesian')]
    return sorted(out, key=lambda x: x[1].lower())


def current_layouts():
    o = _run(['setxkbmap', '-query']) or ''
    m = re.search(r'^layout:\s*(\S+)', o, re.M)
    return [x for x in (m.group(1).split(',') if m else []) if x]


def apply_keyboard(cfg):
    ok = True
    if shutil.which('setxkbmap'):
        layouts = [re.sub(r'[^A-Za-z0-9_()-]', '', x) for x in cfg['layouts'] if x][:4]
        if layouts:
            # Keep the other xkb options of the system (for example ctrl:nocaps);
            # only the layout switch key (grp:...) is Eduka's.
            q = _run(['setxkbmap', '-query']) or ''
            m = re.search(r'^options:\s*(\S+)', q, re.M)
            keep = [o for o in (m.group(1).split(',') if m else []) if o and not o.startswith('grp:')]
            switch = cfg.get('switch') or ''
            if switch and len(layouts) > 1 and switch in dict(SWITCH_KEYS):
                keep.append(switch)
            args = ['setxkbmap', '-layout', ','.join(layouts), '-option', '']
            for o in keep:
                args += ['-option', o]
            ok = _run(args) is not None and ok
    if shutil.which('xset'):
        delay = max(150, min(1000, int(cfg['repeat_delay']))); rate = max(5, min(60, int(cfg['repeat_rate'])))
        ok = _run(['xset', 'r', 'rate', str(delay), str(rate)]) is not None and ok
    if shutil.which('numlockx'):
        _run(['numlockx', 'on' if cfg['numlock'] else 'off'])
    session = Path.home()/'.config/lxqt/session.conf'
    try:
        _set_ini(session, 'Keyboard', 'delay', str(int(cfg['repeat_delay'])))
        _set_ini(session, 'Keyboard', 'interval', str(max(1, int(1000/max(1, int(cfg['repeat_rate']))))))
        _set_ini(session, 'Keyboard', 'numlock', 'true' if cfg['numlock'] else 'false')
    except Exception:
        pass
    return ok


# ------------------------------------------------------------------ pointers
def pointer_devices():
    """[{id, name, touchpad}] of the real mice and touchpads (xinput)."""
    if not shutil.which('xinput'):
        return []
    o = _run(['xinput', 'list']) or ''
    devs = []
    for line in o.splitlines():
        m = re.search(r'↳\s*(.+?)\s+id=(\d+)\s+\[slave\s+pointer', line)
        if not m or SKIP_POINTER.search(m.group(1)):
            continue
        name, did = m.group(1).strip(), int(m.group(2))
        props = _run(['xinput', 'list-props', str(did)]) or ''
        touch = bool(TOUCHPAD_NAME.search(name)) or 'libinput Tapping Enabled' in props or 'Synaptics' in props
        devs.append({'id': did, 'name': name, 'touchpad': touch, 'libinput': 'libinput' in props, 'props': props})
    return devs


def touchpads():
    return [d for d in pointer_devices() if d['touchpad']]


def _set_prop(dev, prop, *values):
    if prop not in dev.get('props', ''):
        return False
    return _run(['xinput', 'set-prop', str(dev['id']), prop] + [str(v) for v in values]) is not None


def apply_pointers(cfg, devices=None):
    devices = pointer_devices() if devices is None else devices
    b = lambda v: 1 if v else 0
    for d in devices:
        if d['touchpad']:
            _set_prop(d, 'Device Enabled', b(cfg['tp_enabled']))
            _set_prop(d, 'libinput Tapping Enabled', b(cfg['tp_tap']))
            _set_prop(d, 'libinput Natural Scrolling Enabled', b(cfg['tp_natural']))
            _set_prop(d, 'libinput Disable While Typing Enabled', b(cfg['tp_dwt']))
            _set_prop(d, 'libinput Accel Speed', f"{max(-1.0, min(1.0, float(cfg['tp_speed']))):.2f}")
            method = {'two-finger': (1, 0, 0), 'edge': (0, 1, 0), 'none': (0, 0, 0)}.get(cfg['tp_scroll'], (1, 0, 0))
            _set_prop(d, 'libinput Scroll Method Enabled', *method)
            _set_prop(d, 'libinput Left Handed Enabled', b(cfg['left_handed']))
        else:
            _set_prop(d, 'libinput Accel Speed', f"{max(-1.0, min(1.0, float(cfg['mouse_speed']))):.2f}")
            _set_prop(d, 'libinput Natural Scrolling Enabled', b(cfg['mouse_natural']))
            _set_prop(d, 'libinput Left Handed Enabled', b(cfg['left_handed']))
            _set_prop(d, 'libinput Middle Emulation Enabled', b(cfg['middle_emulation']))
    if not any(d.get('libinput') for d in devices) and shutil.which('xset'):
        # Old drivers: plain X acceleration (1..5) instead of libinput's speed.
        _run(['xset', 'm', f"{int(round(1+(float(cfg['mouse_speed'])+1)*2))}/1", '4'])
    home = Path.home()
    try:
        _set_ini(home/'.config/lxqt/session.conf', 'Mouse', 'left_handed', 'true' if cfg['left_handed'] else 'false')
        _set_ini(home/'.config/lxqt/lxqt.conf', 'Qt', 'doubleClickInterval', str(int(cfg['double_click'])))
        _set_ini(home/'.config/lxqt/lxqt.conf', 'Qt', 'wheelScrollLines', str(int(cfg['wheel_lines'])))
        for gtk in ('gtk-3.0', 'gtk-4.0'):
            ini = home/'.config'/gtk/'settings.ini'
            if ini.exists() or gtk == 'gtk-3.0':
                _set_ini(ini, 'Settings', 'gtk-double-click-time', str(int(cfg['double_click'])))
    except Exception:
        pass
    return devices


def apply_all(cfg=None):
    cfg = cfg or input_config()
    apply_keyboard(cfg)
    return apply_pointers(cfg)


def device_signature():
    """Changes when a mouse, touchpad or keyboard is plugged in or out."""
    o = _run(['xinput', 'list', '--id-only']) if shutil.which('xinput') else None
    return (o or '').split()


# ------------------------------------------------------------------ picture
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, QElapsedTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QPainterPath, QPalette
from PyQt5.QtWidgets import QWidget


class TouchpadView(QWidget):
    """A small touchpad that copies the real one: a dot with a short trail
    follows the finger, the left and right buttons light up when they are
    pressed and a wave shows scrolling. Used on Eduka-Panel and in
    Eduka-Settings."""
    def __init__(self, parent=None, ink=None, accent=None):
        super().__init__(parent)
        self.ink = QColor(ink) if ink else None; self.accent = QColor(accent or '#00a879')
        self.pos = [0.5, 0.42]; self.trail = []; self.buttons = set(); self.flash = {}; self.scroll = 0.0
        self.active = 0.0; self.disabled = False
        self.clock = QElapsedTimer(); self.clock.start()
        self.timer = QTimer(self); self.timer.setInterval(33); self.timer.timeout.connect(self._tick)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def set_colors(self, ink=None, accent=None):
        if ink: self.ink = QColor(ink)
        if accent: self.accent = QColor(accent)
        self.update()

    def _wake(self):
        self.active = 1.0
        if not self.timer.isActive(): self.timer.start()

    def motion(self, dx, dy):
        w = max(1.0, self.width()*14.0); h = max(1.0, self.height()*14.0)
        x = min(0.94, max(0.06, self.pos[0]+dx/w)); y = min(0.68, max(0.08, self.pos[1]+dy/h))
        self.pos = [x, y]; self.trail.append((x, y, self.clock.elapsed())); self.trail = self.trail[-10:]
        self._wake()

    def press(self, button):
        if button in (4, 5, 6, 7):
            self.scroll = 1.0 if button in (5, 7) else -1.0; self._wake(); return
        self.buttons.add(button); self.flash[button] = 1.0; self._wake(); self.update()

    def release(self, button):
        self.buttons.discard(button); self._wake()

    def _tick(self):
        now = self.clock.elapsed()
        self.trail = [t for t in self.trail if now-t[2] < 450]
        for b in list(self.flash):
            if b not in self.buttons:
                self.flash[b] = max(0.0, self.flash[b]-0.12)
                if self.flash[b] <= 0: del self.flash[b]
        self.scroll *= 0.85
        if abs(self.scroll) < 0.05: self.scroll = 0.0
        self.active = max(0.0, self.active-0.03)
        if not self.trail and not self.flash and not self.scroll and self.active <= 0:
            self.timer.stop()
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        ink = QColor(self.ink or self.palette().color(QPalette.ButtonText)); acc = QColor(self.accent)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        side = min(r.width(), r.height()*1.3); r = QRectF(r.center().x()-side/2, r.center().y()-side/2.6, side, side/1.3)
        rad = max(2.0, min(14.0, side*0.13)); lw = max(1.2, min(3.0, side*0.07))
        frame = QColor(acc if self.active > 0 else ink); frame.setAlpha(230 if not self.disabled else 90)
        fill = QColor(acc); fill.setAlpha(int(20+40*self.active))
        p.setPen(QPen(frame, lw)); p.setBrush(fill); p.drawRoundedRect(r, rad, rad)
        split = r.top()+r.height()*0.72
        p.drawLine(QPointF(r.left()+lw, split), QPointF(r.right()-lw, split))
        p.drawLine(QPointF(r.center().x(), split), QPointF(r.center().x(), r.bottom()-lw))
        # buttons
        for b, left in ((1, True), (3, False)):
            k = 1.0 if b in self.buttons else self.flash.get(b, 0.0)
            if k > 0:
                c = QColor(acc); c.setAlpha(int(255*k))
                area = QRectF(r.left()+lw, split+lw/2, r.width()/2-lw*1.2, r.bottom()-split-lw*1.2) if left else \
                    QRectF(r.center().x()+lw/2, split+lw/2, r.width()/2-lw*1.2, r.bottom()-split-lw*1.2)
                path = QPainterPath(); path.addRoundedRect(area, rad*0.5, rad*0.5); p.fillPath(path, c)
        if self.disabled:
            p.setPen(QPen(ink, lw)); p.drawLine(r.topLeft()+QPointF(lw, lw), QPointF(r.right()-lw, split)); return
        # finger and trail
        now = self.clock.elapsed(); dot = max(1.6, min(8.0, side*0.1))
        for x, y, t in self.trail:
            a = max(0.0, 1.0-(now-t)/450.0); c = QColor(acc); c.setAlpha(int(140*a))
            p.setPen(Qt.NoPen); p.setBrush(c)
            p.drawEllipse(QPointF(r.left()+x*r.width(), r.top()+y*r.height()), dot*0.6*(0.5+a/2), dot*0.6*(0.5+a/2))
        if self.trail or self.active > 0:
            c = QColor(acc); c.setAlpha(int(110+145*max(self.active, 0.3)))
            p.setPen(Qt.NoPen); p.setBrush(c)
            p.drawEllipse(QPointF(r.left()+self.pos[0]*r.width(), r.top()+self.pos[1]*r.height()), dot, dot)
        if self.scroll:
            c = QColor(acc); c.setAlpha(int(230*abs(self.scroll))); p.setPen(QPen(c, lw)); p.setBrush(Qt.NoBrush)
            x = r.right()-side*0.16; y0 = r.top()+r.height()*0.18; y1 = split-r.height()*0.1
            p.drawLine(QPointF(x, y0), QPointF(x, y1))
            tip = y1 if self.scroll > 0 else y0; d = side*0.07*(1 if self.scroll > 0 else -1)
            p.drawLine(QPointF(x-side*0.06, tip-d), QPointF(x, tip)); p.drawLine(QPointF(x+side*0.06, tip-d), QPointF(x, tip))


def parse_xi2(lines, state):
    """Reads `xinput test-xi2 --root` output. Calls back on the view through
    the returned events: ('move', dx, dy), ('press', n), ('release', n)."""
    events = []
    for line in lines:
        s = line.strip()
        if s.startswith('EVENT type'):
            v = state.get('vals') or {}
            if state.get('kind') == 'motion' and state.get('val_section') and (0 in v or 1 in v):
                events.append(('move', v.get(0, 0.0), v.get(1, 0.0)))
            kind = 'motion' if 'RawMotion' in s else 'press' if 'RawButtonPress' in s else 'release' if 'RawButtonRelease' in s else ''
            state.update(kind=kind, vals={}, val_section=False)
        elif s.startswith('detail:') and state.get('kind') in ('press', 'release'):
            try:
                events.append((state['kind'], int(s.split()[1])))
            except Exception:
                pass
        elif s.startswith('valuators:'):
            state['val_section'] = True
        elif state.get('val_section') and state.get('kind') == 'motion':
            m = re.match(r'(\d+):\s*(-?[\d.]+)', s)
            if m:
                state['vals'][int(m.group(1))] = float(m.group(2))
            elif s.startswith('flags') or not s:
                v = state['vals']; state['val_section'] = False
                if 0 in v or 1 in v:
                    events.append(('move', v.get(0, 0.0), v.get(1, 0.0)))
                if 3 in v or 2 in v:
                    sv = v.get(3, v.get(2, 0.0))
                    if sv: events.append(('press', 5 if sv > 0 else 4))
    return events


def touchpad_icon(size=48, ink='#3b4a46', accent='#00a879'):
    """A touchpad icon drawn like the panel picture (icon themes rarely have
    input-touchpad in color)."""
    from PyQt5.QtGui import QIcon, QPixmap
    view = TouchpadView(ink=ink, accent=accent); view.resize(size, size); view.active = 0.0
    view.setAttribute(Qt.WA_TranslucentBackground); view.setAutoFillBackground(False)
    pix = QPixmap(size, size); pix.fill(Qt.transparent); view.render(pix, flags=QWidget.DrawChildren)
    view.deleteLater()
    return QIcon(pix)
