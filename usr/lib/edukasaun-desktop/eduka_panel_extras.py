#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Parts of Eduka-Panel added in 0.11 Pre-Stable (see eduka_windows):

* WorkspaceSwitcher: small numbered buttons for the virtual workspaces.
* HotCorners: an action when the pointer is pushed into a screen corner.
* ClipboardHistory: Super+V lists what was copied (text only, kept in
  memory, never on the disk; secrets of password managers are skipped).
* RecordButton: the red REC button while the screen is recorded.

Every part fails on its own: Eduka-Panel keeps running without it.
"""
import shutil, subprocess, time

from PyQt5.QtCore import Qt, QTimer, QObject, QSize, pyqtSignal
from PyQt5.QtGui import QCursor, QGuiApplication
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QPushButton, QToolButton

import eduka_windows


def _start(cmd):
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return True
    except OSError:
        return False


class WorkspaceSwitcher(QFrame):
    """1 2 3 4: the current workspace is highlighted; a click or the mouse
    wheel changes it."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('workspaceSwitcher'); self.setAccessibleName('Workspaces')
        self.lay = QHBoxLayout(self); self.lay.setContentsMargins(4, 0, 4, 0); self.lay.setSpacing(3)
        self.count = 0; self.current = 0; self.buttons = []
        self.setVisible(False)

    def set_state(self, count, current):
        count = max(1, int(count or 1)); current = max(0, int(current or 0))
        if count != self.count:
            for b in self.buttons:
                b.hide(); b.deleteLater()
            self.buttons = []
            for i in range(count):
                b = QToolButton(); b.setObjectName('workspaceButton'); b.setText(str(i + 1)); b.setCheckable(True)
                b.setFixedSize(QSize(22, 22)); b.setCursor(Qt.PointingHandCursor)
                b.setAccessibleName(f'Workspace {i + 1}'); b.setToolTip(f'Workspace {i + 1}\nScroll to change; Ctrl+Alt+Left/Right too')
                b.clicked.connect(lambda _c=False, n=i: self.go(n))
                self.lay.addWidget(b); self.buttons.append(b)
            self.count = count
        self.current = min(current, count - 1)
        for i, b in enumerate(self.buttons):
            b.setChecked(i == self.current)

    def go(self, index):
        eduka_windows.switch_workspace(index)
        self.set_state(self.count, index)

    def wheelEvent(self, e):
        if self.count > 1:
            step = -1 if e.angleDelta().y() > 0 else 1
            self.go((self.current + step) % self.count)
        e.accept()


class HotCorners(QObject):
    """Pushing the pointer into a corner of a screen runs that corner's
    action once (it waits until the pointer has left the corner again).
    X11 only: Wayland does not tell where the pointer is."""
    triggered = pyqtSignal(str)
    ZONE, LEAVE = 2, 48

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self); self.timer.setInterval(120); self.timer.timeout.connect(self.poll)
        self.corners = {}; self.delay = 0.18; self.armed = True; self.enter_at = None; self.where = ''
        self.reload()

    def reload(self):
        prefs = eduka_windows.read_prefs()
        self.corners = {k: v for k, v in prefs['corners'].items() if v}
        self.delay = prefs['corner_delay'] / 1000.0
        wayland = QGuiApplication.platformName() not in ('xcb', 'offscreen')
        if self.corners and not wayland:
            self.timer.start()
        else:
            self.timer.stop()

    def _corner_at(self, pos):
        for screen in QGuiApplication.screens():
            g = screen.geometry()
            if not g.adjusted(-1, -1, 1, 1).contains(pos):
                continue
            left = pos.x() <= g.left() + self.ZONE; right = pos.x() >= g.right() - self.ZONE
            top = pos.y() <= g.top() + self.ZONE; bottom = pos.y() >= g.bottom() - self.ZONE
            if top and left: return 'top-left'
            if top and right: return 'top-right'
            if bottom and left: return 'bottom-left'
            if bottom and right: return 'bottom-right'
            near = min(abs(pos.x() - g.left()), abs(g.right() - pos.x())) < self.LEAVE and \
                min(abs(pos.y() - g.top()), abs(g.bottom() - pos.y())) < self.LEAVE
            return 'near' if near else ''
        return ''

    def poll(self):
        if QApplication.mouseButtons() != Qt.NoButton:
            return                       # dragging a window or a file: no action
        where = self._corner_at(QCursor.pos())
        if where in ('', 'near'):
            if where == '':
                self.armed = True
            self.enter_at = None; self.where = ''
            return
        if not self.armed:
            return
        now = time.monotonic()
        if where != self.where:
            self.where = where; self.enter_at = now
        if now - (self.enter_at or now) >= self.delay and where in self.corners:
            self.armed = False
            self.triggered.emit(self.corners[where])


class ClipboardHistory(QObject):
    """Text that was copied, newest first (memory only)."""
    LIMIT, MAX_CHARS = 25, 65536

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []; self.enabled = True; self._own = None
        cb = QApplication.clipboard()
        cb.dataChanged.connect(self.changed)

    def set_enabled(self, on):
        self.enabled = bool(on)
        if not on:
            self.items = []

    def changed(self):
        if not self.enabled:
            return
        try:
            data = QApplication.clipboard().mimeData()
            if data is None or not data.hasText():
                return
            # KeePassXC and other password managers mark their secrets.
            if data.hasFormat('x-kde-passwordManagerHint') and bytes(data.data('x-kde-passwordManagerHint')).strip() == b'secret':
                return
            text = data.text()
        except RuntimeError:
            return
        if not text or not text.strip() or len(text) > self.MAX_CHARS or text == self._own:
            self._own = None
            return
        if text in self.items:
            self.items.remove(text)
        self.items.insert(0, text)
        del self.items[self.LIMIT:]

    def choose(self, text):
        self._own = text
        QApplication.clipboard().setText(text)
        QApplication.clipboard().setText(text, QApplication.clipboard().Selection)
        QTimer.singleShot(120, self.paste)

    def paste(self):
        """Paste into the window that had the keyboard (Ctrl+Shift+V in a terminal)."""
        if not shutil.which('xdotool'):
            return
        try:
            wid = subprocess.run(['xdotool', 'getactivewindow'], capture_output=True, text=True, timeout=2).stdout.strip()
            cls = subprocess.run(['xprop', '-id', wid, 'WM_CLASS'], capture_output=True, text=True, timeout=2).stdout.lower() if wid else ''
        except (OSError, subprocess.SubprocessError):
            cls = ''
        terminal = any(t in cls for t in ('term', 'konsole', 'tilix', 'alacritty', 'kitty', 'xterm', 'qterminal'))
        _start(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+v' if terminal else 'ctrl+v'])

    def fill_menu(self, menu, tr=lambda s: s):
        if not self.items:
            a = menu.addAction(tr('Nothing was copied yet')); a.setEnabled(False)
        for text in self.items:
            line = ' '.join(text.split())
            label = (line[:60] + '…') if len(line) > 60 else line
            a = menu.addAction(label.replace('&', '&&'))
            a.setToolTip(text[:400])
            a.triggered.connect(lambda _c=False, t=text: self.choose(t))
        menu.addSeparator()
        clear = menu.addAction(tr('Clear the history'))
        clear.setEnabled(bool(self.items))
        clear.triggered.connect(lambda: self.items.clear())


class RecordButton(QPushButton):
    """● REC 0:12 — a click stops the screen recording."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('recordButton'); self.setVisible(False); self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName('Stop the screen recording'); self.setToolTip('Recording the screen\nClick (or Super+Alt+R) to stop')
        self.setStyleSheet('QPushButton#recordButton{background:#e5484d;color:white;border:0;border-radius:11px;'
                           'padding:2px 9px;font-weight:800;} QPushButton#recordButton:hover{background:#c93338;}')
        self.started = 0.0
        self.timer = QTimer(self); self.timer.setInterval(1000); self.timer.timeout.connect(self.tick)
        self.clicked.connect(self.stop)

    def set_recording(self, on, started=None):
        if on:
            self.started = started or time.time(); self.tick(); self.show(); self.timer.start()
        else:
            self.timer.stop(); self.hide()

    def tick(self):
        s = int(max(0, time.time() - self.started))
        self.setText(f'●  REC {s // 60}:{s % 60:02d}')

    def stop(self):
        self.setEnabled(False); self.setText('● …')
        import threading
        def work():
            try:
                import eduka_capture; eduka_capture.stop()
            except Exception:
                pass
        threading.Thread(target=work, daemon=True).start()
        QTimer.singleShot(4000, lambda: self.setEnabled(True))

    def sync(self):
        """At start: a recording that runs already (Eduka-Panel restarted)."""
        try:
            import eduka_capture
            state = eduka_capture.recording()
        except Exception:
            state = None
        self.set_recording(bool(state), (state or {}).get('started'))


def corner_action(panel, action):
    """Run a hot corner action (inside Eduka-Panel where it can)."""
    if action == 'menu':
        panel.toggle_menu()
    elif action == 'action-center':
        panel.toggle_action_center()
    elif action == 'notifications':
        panel.notification_popup()
    elif action == 'quick':
        _start(['eduka-quick'])
    elif action:
        _start(['eduka-shortcut', action])
