"""Parental Control: the message screen shown when the time is up.

The time is counted by eduka-parental.service (root); Eduka-Panel reads its
state and shows this screen. Keyboard and mouse are taken by the screen so
the computer is not used any more; the service shuts the computer down a
little later. A parent can press Ctrl+Alt+P and type an administrator
password to add 30 minutes.
"""
import json, os, time, subprocess, shutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import Qt, QTimer, QProcess
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QKeySequence
from eduka_common import _, theme_accent

STATE = '/run/edukasaun-parental/state.json'
HELPER = '/usr/lib/edukasaun-desktop/eduka-parental-apply'
EMOJIS = ['😊', '😴', '📚', '⏰', '🌙', '👋', '❤️', '⭐', '🙏', '🏃', '🌈', '🧸', '🎒', '☀️', '🍎', '💤']


def read_state():
    try:
        with open(STATE, encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def minutes_text(seconds):
    m = max(0, int(seconds)) // 60
    if m >= 60:
        return _('{h} h {m} min').replace('{h}', str(m // 60)).replace('{m}', str(m % 60))
    return _('{m} min').replace('{m}', str(max(1, m) if seconds > 0 else 0))


class ParentalLockScreen(QWidget):
    def __init__(self, message='', emoji='😊', shutdown_at=None, preview=False):
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        if not preview:
            flags |= Qt.X11BypassWindowManagerHint
        super().__init__(None, flags)
        self.preview = preview; self.shutdown_at = shutdown_at or (time.time() + (12 if preview else 90))
        self.accent = QColor(theme_accent()); self.proc = None
        self.setAttribute(Qt.WA_DeleteOnClose, preview)
        self.setCursor(Qt.BlankCursor if not preview else Qt.ArrowCursor)
        self.setStyleSheet('QLabel{color:#ffffff;background:transparent;}'
                           'QLabel#emoji{font-size:110px;}'
                           'QLabel#title{font-size:34px;font-weight:800;}'
                           'QLabel#message{font-size:22px;}'
                           'QLabel#count{font-size:16px;font-weight:700;color:rgba(255,255,255,210);}'
                           'QLabel#hint{font-size:12px;color:rgba(255,255,255,120);}')
        v = QVBoxLayout(self); v.setContentsMargins(60, 60, 60, 40); v.setSpacing(14)
        v.addStretch(2)
        self.emoji = QLabel(emoji if emoji in EMOJIS else EMOJIS[0]); self.emoji.setObjectName('emoji'); self.emoji.setAlignment(Qt.AlignCenter); v.addWidget(self.emoji)
        title = QLabel(_('Time is up for today') if not preview else _('Preview: time is up')); title.setObjectName('title'); title.setAlignment(Qt.AlignCenter); v.addWidget(title)
        self.message = QLabel(message or _('It is time to rest. See you later!')); self.message.setObjectName('message')
        self.message.setAlignment(Qt.AlignCenter); self.message.setWordWrap(True); self.message.setTextFormat(Qt.PlainText); v.addWidget(self.message)
        v.addSpacing(10)
        self.count = QLabel(''); self.count.setObjectName('count'); self.count.setAlignment(Qt.AlignCenter); v.addWidget(self.count)
        v.addStretch(3)
        hint = QLabel(_('Parents: Ctrl+Alt+P adds 30 minutes (administrator password).') if not preview else _('Press Esc or click to close the preview.'))
        hint.setObjectName('hint'); hint.setAlignment(Qt.AlignCenter); v.addWidget(hint)
        self.timer = QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(500)
        self.phase = 0.0
        self.tick()

    def show_locked(self):
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.show(); self.raise_(); self.activateWindow()
        if not self.preview:
            QTimer.singleShot(100, self.grab)

    def grab(self):
        if self.preview or (self.proc is not None):
            return
        self.grabKeyboard(); self.grabMouse()

    def tick(self):
        self.phase = (self.phase + 0.5) % 6.0
        left = max(0, int(self.shutdown_at - time.time()))
        self.count.setText(_('This computer shuts down in {n} s').replace('{n}', str(left)))
        if self.preview and left <= 0:
            self.close(); return
        if not self.preview and self.proc is None and self.isVisible():
            self.raise_(); self.grab()       # keep keyboard and mouse
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        g = QLinearGradient(0, 0, self.width(), self.height())
        a = QColor(self.accent); a2 = a.darker(260)
        g.setColorAt(0, a2); g.setColorAt(1, QColor(10, 14, 30))
        p.fillRect(self.rect(), g)

    def keyPressEvent(self, e):
        if self.preview and e.key() == Qt.Key_Escape:
            self.close(); return
        if not self.preview and e.key() == Qt.Key_P and e.modifiers() & Qt.ControlModifier and e.modifiers() & Qt.AltModifier:
            self.ask_parent(); return
        e.accept()          # every other key does nothing

    def mousePressEvent(self, e):
        if self.preview:
            self.close(); return
        e.accept()

    def ask_parent(self):
        if self.proc is not None or shutil.which('pkexec') is None or not os.path.exists(HELPER):
            return
        # The password window needs the keyboard and mouse.
        self.releaseKeyboard(); self.releaseMouse(); self.setCursor(Qt.ArrowCursor)
        self.proc = QProcess(self)
        self.proc.finished.connect(self.parent_done)
        self.proc.start('pkexec', [HELPER])
        self.proc.write(json.dumps({'action': 'extend', 'minutes': 30}).encode()); self.proc.closeWriteChannel()

    def parent_done(self, code, _status=None):
        self.proc = None
        if code == 0:
            self.timer.stop(); self.releaseKeyboard(); self.releaseMouse(); self.hide(); self.deleteLater()
        else:
            self.setCursor(Qt.BlankCursor); self.grab()

    def closeEvent(self, e):
        if not self.preview and self.isVisible() and self.proc is None and read_state().get('phase') == 'lock':
            e.ignore(); return
        self.releaseKeyboard(); self.releaseMouse()
        super().closeEvent(e)
