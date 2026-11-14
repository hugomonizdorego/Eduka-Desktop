#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Touch screens and touchpads that feel like Windows and macOS (0.11 RC3).

* Gestures with three and four fingers on touch screens and touchpads,
  through Touchégg (package touchegg: a small service reads the touch
  devices, its client runs in the session). Eduka writes the gestures of
  this account (~/.config/touchegg/touchegg.conf, recognized by its first
  line) and leaves a file the user wrote alone:
      3 fingers up / down     maximize / minimize the window
      3 fingers left / right  window on the left / right half
      4 fingers left / right  previous / next workspace
      4 fingers up            Eduka-Desktop (start menu)
      4 fingers down          show the desktop
      3-finger tap            search
* Firefox scrolls and zooms smoothly with a finger and with two fingers on
  a touchpad (MOZ_USE_XINPUT2=1 in the session).
* In Eduka's own programs a long press is a right click (context menus on
  a touch screen), see enable_long_press().
* On a tablet or a convertible without a keyboard, the on-screen keyboard
  starts at the first login and comes up by itself in a text field
  (Onboard's auto-show).
"""
import os, shutil, subprocess
from pathlib import Path

MARK = '<!-- Edukasaun Desktop gestures (Eduka-Settings → Mouse & Touch). -->'
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')/'touchegg'/'touchegg.conf'

GESTURES = (
    ('SWIPE', 3, 'UP', 'MAXIMIZE_RESTORE_WINDOW', '', 'Maximize or restore the window'),
    ('SWIPE', 3, 'DOWN', 'MINIMIZE_WINDOW', '', 'Minimize the window'),
    ('SWIPE', 3, 'LEFT', 'TILE_WINDOW', 'left', 'Window on the left half'),
    ('SWIPE', 3, 'RIGHT', 'TILE_WINDOW', 'right', 'Window on the right half'),
    ('SWIPE', 4, 'LEFT', 'CHANGE_DESKTOP', 'previous', 'Previous workspace'),
    ('SWIPE', 4, 'RIGHT', 'CHANGE_DESKTOP', 'next', 'Next workspace'),
    ('SWIPE', 4, 'UP', 'RUN_COMMAND', 'eduka-shortcut menu', 'Open Eduka-Desktop (start menu)'),
    ('SWIPE', 4, 'DOWN', 'SHOW_DESKTOP', '', 'Show the desktop'),
    ('TAP', 3, '', 'RUN_COMMAND', 'eduka-shortcut search', 'Search apps and files'),
)


def touchegg_installed():
    return bool(shutil.which('touchegg'))


def touchegg_service_active():
    if not shutil.which('systemctl'):
        return False
    try:
        return subprocess.run(['systemctl', 'is-active', '--quiet', 'touchegg.service'], timeout=3).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def gestures_config():
    """The Touchégg configuration of Eduka (XML)."""
    out = ['<touchégg>', MARK, '  <settings>',
           '    <property name="animation_delay">150</property>',
           '    <property name="action_execute_threshold">20</property>',
           '    <property name="color">auto</property>',
           '    <property name="borderColor">auto</property>',
           '  </settings>', '  <application name="All">']
    for kind, fingers, direction, action, arg, _label in GESTURES:
        attrs = f'type="{kind}" fingers="{fingers}"' + (f' direction="{direction}"' if direction else '')
        out.append(f'    <gesture {attrs}>')
        out.append(f'      <action type="{action}">')
        if action in ('MAXIMIZE_RESTORE_WINDOW', 'MINIMIZE_WINDOW', 'TILE_WINDOW', 'SHOW_DESKTOP', 'CHANGE_DESKTOP'):
            out.append('        <animate>true</animate>')
        if action == 'TILE_WINDOW':
            out.append(f'        <direction>{arg}</direction>')
        if action == 'CHANGE_DESKTOP':
            out.append(f'        <direction>{arg}</direction>')
            out.append('        <animationPosition>auto</animationPosition>')
        if action == 'RUN_COMMAND':
            out.append('        <repeat>false</repeat>')
            out.append(f'        <command>{arg}</command>')
            out.append('        <on>begin</on>')
        out.append('      </action>')
        out.append('    </gesture>')
    out += ['  </application>', '</touchégg>', '']
    return '\n'.join(out)


def gestures_state():
    """'eduka' (Eduka's gestures), 'own' (a file the user made), 'off'."""
    try:
        text = CONFIG.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return 'off'
    return 'eduka' if MARK in text else 'own'


def set_gestures(on):
    """Write (or remove) Eduka's gestures; a file the user made stays."""
    state = gestures_state()
    if state == 'own':
        return False
    try:
        if on:
            CONFIG.parent.mkdir(parents=True, exist_ok=True)
            tmp = CONFIG.with_suffix('.eduka-tmp')
            tmp.write_text(gestures_config(), encoding='utf-8'); os.replace(tmp, CONFIG)
        elif state == 'eduka':
            CONFIG.unlink()
    except OSError:
        return False
    restart_client()
    return True


def restart_client():
    """The Touchégg client of this session reads its file when it starts."""
    if not touchegg_installed():
        return
    try:
        subprocess.run(['pkill', '-u', str(os.getuid()), '-x', 'touchegg'], capture_output=True, timeout=3)
        subprocess.Popen(['touchegg'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    except OSError:
        pass


def install_command():
    return ['sh', '-c', 'echo "Installing Touchégg (touch and touchpad gestures)..."; echo; '
                        'sudo apt-get install touchegg; echo; '
                        'printf "Press Enter to close this window. "; read _answer']


# ---------------------------------------------------------------- session (eduka-session-prepare)
def session_environment():
    """Environment for every program of the session (LXQt's session.conf)."""
    return {'MOZ_USE_XINPUT2': '1'}


def first_login(cfg=None):
    """Once per account: gestures where Touchégg is installed, and on a tablet
    or convertible without a keyboard the on-screen keyboard."""
    import json
    cfg = Path(cfg or os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')
    marker = cfg/'eduka-desktop'/'desktop'/'touch.json'
    if marker.exists():
        return False
    done = {'gestures': False, 'osk': False}
    if touchegg_installed() and gestures_state() == 'off':
        done['gestures'] = set_gestures(True)
    try:
        import eduka_device, eduka_input
        p = eduka_device.profile()
        touch_first = p['kind'] in ('tablet', 'detachable', 'convertible') and p['touchscreens'] and \
            not any(kb['connection'] in ('usb', 'bluetooth', 'built-in') for kb in p['keyboards'])
        if touch_first and eduka_input.onboard_installed() and not eduka_input.osk_autostart_enabled():
            done['osk'] = eduka_input.set_osk_autostart(True)
            onboard_auto_show(True)
    except Exception:
        pass
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(done) + '\n', encoding='utf-8')
    return True


def onboard_auto_show(on):
    """Onboard comes up by itself when a text field gets the focus."""
    if not shutil.which('gsettings'):
        return False
    try:
        return subprocess.run(['gsettings', 'set', 'org.onboard.auto-show', 'enabled', 'true' if on else 'false'],
                              capture_output=True, timeout=5).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


# ---------------------------------------------------------------- long press (Qt programs of Eduka)
_long_press = None


def enable_long_press(app, ms=550):
    """A finger held still on a touch screen opens the context menu, as a
    right click does (Qt only turns touch into left clicks)."""
    global _long_press
    if _long_press is not None or app is None:
        return
    from PyQt5.QtCore import QObject, QEvent, QTimer, Qt, QPoint
    from PyQt5.QtGui import QContextMenuEvent, QCursor
    from PyQt5.QtWidgets import QApplication

    class LongPress(QObject):
        def __init__(self):
            super().__init__(app)
            self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.fire)
            self.target = None; self.start = QPoint(); self.fired = False

        def eventFilter(self, obj, e):
            t = e.type()
            if t == QEvent.MouseButtonPress and e.button() == Qt.LeftButton and \
                    e.source() in (Qt.MouseEventSynthesizedBySystem, Qt.MouseEventSynthesizedByQt):
                self.target, self.start, self.fired = obj, e.globalPos(), False
                self.timer.start(ms)
            elif t == QEvent.MouseMove and self.timer.isActive():
                if (e.globalPos() - self.start).manhattanLength() > 12:
                    self.timer.stop()
            elif t == QEvent.MouseButtonRelease:
                self.timer.stop()
                if self.fired and obj is self.target:
                    self.fired = False
                    return True                  # the menu is open: no click after it
            return False

        def fire(self):
            w = self.target
            if w is None:
                return
            try:
                widget = QApplication.widgetAt(self.start) or w
                local = widget.mapFromGlobal(self.start)
            except RuntimeError:
                return
            self.fired = True
            ev = QContextMenuEvent(QContextMenuEvent.Mouse, local, self.start)
            QApplication.sendEvent(widget, ev)
            QCursor.setPos(QCursor.pos())

    _long_press = LongPress()
    app.installEventFilter(_long_press)
