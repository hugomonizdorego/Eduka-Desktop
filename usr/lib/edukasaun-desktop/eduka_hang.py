#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Force Close (0.11 Pre-Stable).

A program that hangs (crashed or frozen) keeps its window but no longer
answers. Eduka-Panel asks every window that supports it (_NET_WM_PING of the
EWMH, as window managers do) every few seconds whether its program still
answers. When a program has not answered for two minutes (Eduka-Settings →
Windows changes the time), a small window offers to wait or to force it to
close. Ctrl+Alt+Esc and "Force close" in the taskbar menu do the same at
once (eduka-force-close).

Only programs of this account on this computer are closed: first politely
(SIGTERM), then for sure (SIGKILL). The X11 work runs in a thread with its
own connection (ctypes and libX11); on Wayland there is no watch.
"""
import ctypes, ctypes.util, os, select, signal, socket, struct, threading, time

# ---------------------------------------------------------------- libX11 (ctypes)
_X = {'lib': None, 'handler': None}
ClientMessage, PropertyNotify = 33, 28
SubstructureNotifyMask, SubstructureRedirectMask = 1 << 19, 1 << 20
AnyPropertyType = 0


class XClientMessageEvent(ctypes.Structure):
    _fields_ = [('type', ctypes.c_int), ('serial', ctypes.c_ulong), ('send_event', ctypes.c_int),
                ('display', ctypes.c_void_p), ('window', ctypes.c_ulong), ('message_type', ctypes.c_ulong),
                ('format', ctypes.c_int), ('data', ctypes.c_long * 5)]


class XEvent(ctypes.Union):
    _fields_ = [('type', ctypes.c_int), ('xclient', XClientMessageEvent), ('pad', ctypes.c_long * 24)]


_ERROR_HANDLER = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)


def _ignore_errors(_display, _event):
    return 0       # a window that closed meanwhile (BadWindow): never stop the program


def xlib():
    if _X['lib'] is None:
        _X['lib'] = False
        try:
            lib = ctypes.cdll.LoadLibrary(ctypes.util.find_library('X11') or 'libX11.so.6')
            lib.XOpenDisplay.restype = ctypes.c_void_p; lib.XOpenDisplay.argtypes = [ctypes.c_char_p]
            lib.XDefaultRootWindow.restype = ctypes.c_ulong; lib.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
            lib.XInternAtom.restype = ctypes.c_ulong; lib.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
            lib.XGetWindowProperty.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_long, ctypes.c_long,
                                               ctypes.c_int, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong),
                                               ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_ulong),
                                               ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_void_p)]
            lib.XFree.argtypes = [ctypes.c_void_p]
            lib.XSendEvent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_long, ctypes.POINTER(XEvent)]
            lib.XSelectInput.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_long]
            lib.XPending.argtypes = [ctypes.c_void_p]
            lib.XNextEvent.argtypes = [ctypes.c_void_p, ctypes.POINTER(XEvent)]
            lib.XFlush.argtypes = [ctypes.c_void_p]
            lib.XCloseDisplay.argtypes = [ctypes.c_void_p]
            lib.XKillClient.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            lib.XConnectionNumber.argtypes = [ctypes.c_void_p]
            lib.XSetErrorHandler.restype = ctypes.c_void_p; lib.XSetErrorHandler.argtypes = [_ERROR_HANDLER]
            _X['handler'] = _ERROR_HANDLER(_ignore_errors)
            lib.XSetErrorHandler(_X['handler'])
            _X['lib'] = lib
        except (OSError, AttributeError):
            _X['lib'] = False
    return _X['lib'] or None


class Display:
    """A small libX11 connection of its own (one thread only)."""
    def __init__(self):
        self.x = xlib()
        self.d = self.x.XOpenDisplay(None) if self.x and os.environ.get('DISPLAY') else None
        if not self.d:
            raise OSError('no X11 display')
        self.root = self.x.XDefaultRootWindow(self.d)
        self._atoms = {}

    def atom(self, name):
        if name not in self._atoms:
            self._atoms[name] = self.x.XInternAtom(self.d, name.encode(), 0)
        return self._atoms[name]

    def prop(self, window, name, kind=AnyPropertyType, length=1024):
        """(format, [items]) of a window property; strings for format 8."""
        actual, fmt, n, after, data = ctypes.c_ulong(), ctypes.c_int(), ctypes.c_ulong(), ctypes.c_ulong(), ctypes.c_void_p()
        if self.x.XGetWindowProperty(self.d, window, self.atom(name), 0, length, 0, kind, ctypes.byref(actual),
                                     ctypes.byref(fmt), ctypes.byref(n), ctypes.byref(after), ctypes.byref(data)) != 0:
            return 0, []
        try:
            if not data.value or not n.value:
                return fmt.value, []
            if fmt.value == 32:
                return 32, list((ctypes.c_ulong * n.value).from_address(data.value))
            if fmt.value == 8:
                return 8, [ctypes.string_at(data.value, n.value).decode('utf-8', 'replace')]
            return fmt.value, []
        finally:
            if data.value:
                self.x.XFree(data)

    def clients(self):
        return self.prop(self.root, '_NET_CLIENT_LIST')[1]

    def protocols(self, window):
        return set(self.prop(window, 'WM_PROTOCOLS')[1])

    def pid(self, window):
        items = self.prop(window, '_NET_WM_PID')[1]
        return int(items[0]) if items else 0

    def title(self, window):
        for name in ('_NET_WM_NAME', 'WM_NAME'):
            items = self.prop(window, name)[1]
            if items and items[0]:
                return items[0]
        return ''

    def machine(self, window):
        items = self.prop(window, 'WM_CLIENT_MACHINE')[1]
        return items[0].strip('\0') if items else ''

    def window_types(self, window):
        return set(self.prop(window, '_NET_WM_WINDOW_TYPE')[1])

    def ping(self, window):
        ev = XEvent()
        ev.xclient.type = ClientMessage; ev.xclient.window = window
        ev.xclient.message_type = self.atom('WM_PROTOCOLS'); ev.xclient.format = 32
        ev.xclient.data[0] = self.atom('_NET_WM_PING'); ev.xclient.data[1] = 0; ev.xclient.data[2] = window
        self.x.XSendEvent(self.d, window, 0, 0, ctypes.byref(ev))

    def kill_client(self, window):
        self.x.XKillClient(self.d, window); self.x.XFlush(self.d)

    def close(self):
        if self.d:
            self.x.XCloseDisplay(self.d); self.d = None


# ---------------------------------------------------------------- closing a program
def _alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _own(pid):
    try:
        return os.stat(f'/proc/{pid}').st_uid == os.getuid()
    except OSError:
        return False


def program_name(pid):
    try:
        with open(f'/proc/{pid}/comm', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()
    except OSError:
        return ''


def force_close_window(window, wait=2.5):
    """Close the program of an X11 window. (ok, message)"""
    try:
        dpy = Display()
    except OSError as e:
        return False, str(e)
    try:
        pid, machine = dpy.pid(window), dpy.machine(window)
        local = not machine or machine == socket.gethostname()
        if pid and local and pid != os.getpid():
            if not _own(pid):
                return False, 'This program belongs to another account.'
            protected = {'lxqt-session', 'eduka-panel', 'xfwm4', 'openbox', 'Xorg', 'pcmanfm-qt', 'compiz', 'kwin_x11'}
            if program_name(pid) in protected:
                return False, 'This program keeps the desktop running and is not closed.'
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.kill(pid, sig)
                    if sig == signal.SIGTERM:
                        os.kill(pid, signal.SIGCONT)     # a stopped program gets the TERM too
                except OSError:
                    break
                end = time.monotonic() + wait
                while time.monotonic() < end and _alive(pid):
                    time.sleep(0.1)
                if not _alive(pid):
                    return True, 'The program was closed.'
            return (not _alive(pid)), 'The program was closed.' if not _alive(pid) else 'The program did not close.'
        # Without a process number (or from another computer): the X server
        # closes the connection of the program.
        dpy.kill_client(window)
        return True, 'The program was closed.'
    finally:
        dpy.close()


# ---------------------------------------------------------------- answers (X RECORD)
# The answer to a ping goes to the root window, and the X server gives it only
# to the window manager. The RECORD extension (libXtst, which xdotool needs
# too) lets Eduka-Panel see the SendEvent requests of the programs, so it
# sees every answer.
class _R8(ctypes.Structure):
    _fields_ = [('first', ctypes.c_ubyte), ('last', ctypes.c_ubyte)]


class _R16(ctypes.Structure):
    _fields_ = [('first', ctypes.c_ushort), ('last', ctypes.c_ushort)]


class _ExtRange(ctypes.Structure):
    _fields_ = [('ext_major', _R8), ('ext_minor', _R16)]


class XRecordRange(ctypes.Structure):
    _fields_ = [('core_requests', _R8), ('core_replies', _R8), ('ext_requests', _ExtRange), ('ext_replies', _ExtRange),
                ('delivered_events', _R8), ('device_events', _R8), ('errors', _R8),
                ('client_started', ctypes.c_int), ('client_died', ctypes.c_int)]


class XRecordInterceptData(ctypes.Structure):
    _fields_ = [('id_base', ctypes.c_ulong), ('server_time', ctypes.c_ulong), ('client_seq', ctypes.c_ulong),
                ('category', ctypes.c_int), ('client_swapped', ctypes.c_int),
                ('data', ctypes.POINTER(ctypes.c_ubyte)), ('data_len', ctypes.c_ulong)]


_RECORD_CB = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.POINTER(XRecordInterceptData))
X_SendEvent, XRecordFromClient, XRecordAllClients = 25, 1, 3
_XT = {'lib': None}


def xtst():
    if _XT['lib'] is None:
        _XT['lib'] = False
        try:
            lib = ctypes.cdll.LoadLibrary(ctypes.util.find_library('Xtst') or 'libXtst.so.6')
            lib.XRecordQueryVersion.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
            lib.XRecordAllocRange.restype = ctypes.POINTER(XRecordRange)
            lib.XRecordCreateContext.restype = ctypes.c_ulong
            lib.XRecordCreateContext.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_ulong), ctypes.c_int,
                                                 ctypes.POINTER(ctypes.POINTER(XRecordRange)), ctypes.c_int]
            lib.XRecordEnableContextAsync.argtypes = [ctypes.c_void_p, ctypes.c_ulong, _RECORD_CB, ctypes.c_void_p]
            lib.XRecordProcessReplies.argtypes = [ctypes.c_void_p]
            lib.XRecordFreeData.argtypes = [ctypes.POINTER(XRecordInterceptData)]
            lib.XRecordDisableContext.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            lib.XRecordFreeContext.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            _XT['lib'] = lib
        except (OSError, AttributeError):
            _XT['lib'] = False
    return _XT['lib'] or None


class PongRecorder:
    """Sees the answers (pongs) of all programs. poll() calls `on_pong(window)`."""
    def __init__(self, on_pong):
        self.xt = xtst()
        if self.xt is None:
            raise OSError('libXtst is missing')
        self.ctrl, self.data = Display(), Display()
        major, minor = ctypes.c_int(), ctypes.c_int()
        if not self.xt.XRecordQueryVersion(self.ctrl.d, ctypes.byref(major), ctypes.byref(minor)):
            self.close(); raise OSError('the X server has no RECORD extension')
        self.ping_atom, self.proto_atom, self.root = self.ctrl.atom('_NET_WM_PING'), self.ctrl.atom('WM_PROTOCOLS'), self.ctrl.root
        self.on_pong = on_pong
        rng = self.xt.XRecordAllocRange()
        rng.contents.core_requests.first = X_SendEvent; rng.contents.core_requests.last = X_SendEvent
        clients = (ctypes.c_ulong * 1)(XRecordAllClients)
        ranges = (ctypes.POINTER(XRecordRange) * 1)(rng)
        self.ctx = self.xt.XRecordCreateContext(self.ctrl.d, 0, clients, 1, ranges, 1)
        self.ctrl.x.XFree(rng)
        self.ctrl.x.XFlush(self.ctrl.d)
        if not self.ctx:
            self.close(); raise OSError('no RECORD context')
        self._cb = _RECORD_CB(self._intercept)       # keep it alive
        if not self.xt.XRecordEnableContextAsync(self.data.d, self.ctx, self._cb, None):
            self.close(); raise OSError('RECORD did not start')
        self.fd = self.data.x.XConnectionNumber(self.data.d)

    def _intercept(self, _closure, item):
        try:
            i = item.contents
            if i.category != XRecordFromClient or i.data_len < 11:
                return
            raw = ctypes.string_at(i.data, min(i.data_len, 11) * 4)
            if raw[0] != X_SendEvent:
                return
            native = '<' if _little_endian() else '>'
            order = ({'<': '>', '>': '<'}[native]) if i.client_swapped else native
            dest, = struct.unpack_from(order + 'I', raw, 4)
            if dest != self.root or (raw[12] & 0x7f) != ClientMessage or raw[13] != 32:
                return
            mtype, = struct.unpack_from(order + 'I', raw, 20)
            l0, _l1, l2 = struct.unpack_from(order + '3I', raw, 24)
            if mtype == self.proto_atom and l0 == self.ping_atom and l2:
                self.on_pong(int(l2))
        except Exception:
            pass
        finally:
            self.xt.XRecordFreeData(item)

    def poll(self, timeout=0.25):
        try:
            select.select([self.fd], [], [], timeout)
        except (OSError, ValueError):
            time.sleep(timeout)
        self.xt.XRecordProcessReplies(self.data.d)

    def close(self):
        try:
            if getattr(self, 'ctx', 0):
                self.xt.XRecordDisableContext(self.ctrl.d, self.ctx); self.xt.XRecordFreeContext(self.ctrl.d, self.ctx)
                self.ctrl.x.XFlush(self.ctrl.d); self.ctx = 0
        except Exception:
            pass
        for d in (getattr(self, 'data', None), getattr(self, 'ctrl', None)):
            if d is not None:
                d.close()


def _little_endian():
    import sys
    return sys.byteorder == 'little'


# ---------------------------------------------------------------- the watch (Qt)
def make_watcher(parent, seconds=120):
    """A HangWatcher (QThread) for Eduka-Panel, or None without X11."""
    if not os.environ.get('DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland' or xlib() is None or xtst() is None:
        return None
    from PyQt5.QtCore import QThread, pyqtSignal

    class HangWatcher(QThread):
        """Pings the windows every PERIOD seconds; `hung(window, title,
        seconds)` when a window that answered before has not answered for
        `seconds` (once, until it answers again or is snoozed)."""
        hung = pyqtSignal(int, str, int)
        PERIOD = 10

        def __init__(self, parent, seconds):
            super().__init__(parent)
            self.seconds = seconds; self.snoozed = {}; self._lock = threading.Lock()

        def snooze(self, window, seconds=None):
            with self._lock:
                self.snoozed[int(window)] = time.monotonic() + (seconds or self.seconds)

        def run(self):
            last_pong, last_ping, told = {}, {}, set()

            def pong(window):
                last_pong[window] = time.monotonic(); told.discard(window)
            try:
                rec = PongRecorder(pong)
            except OSError:
                return
            dpy = rec.ctrl
            skip_types = {dpy.atom(t) for t in ('_NET_WM_WINDOW_TYPE_DESKTOP', '_NET_WM_WINDOW_TYPE_DOCK')}
            own_pid, next_round = os.getpid(), 0.0
            try:
                while not self.isInterruptionRequested():
                    now = time.monotonic()
                    if now >= next_round:
                        next_round = now + self.PERIOD
                        clients = set(dpy.clients())
                        for w in list(last_ping):
                            if w not in clients:
                                last_pong.pop(w, None); last_ping.pop(w, None); told.discard(w)
                        for w in clients:
                            if rec.ping_atom not in dpy.protocols(w) or dpy.window_types(w) & skip_types or dpy.pid(w) == own_pid:
                                continue
                            dpy.ping(w); last_ping.setdefault(w, now)
                            if last_pong.get(w, 0) >= last_ping[w]:
                                last_ping[w] = now
                        dpy.x.XFlush(dpy.d)
                    rec.poll(0.25)
                    now = time.monotonic()
                    for w, pinged in list(last_ping.items()):
                        answered = last_pong.get(w)
                        if answered is None:
                            continue           # never answered: it may not really support pings
                        quiet = now - answered
                        with self._lock:
                            snoozed = self.snoozed.get(w, 0) > now
                        if quiet >= self.seconds and pinged > answered and w not in told and not snoozed:
                            told.add(w)
                            self.hung.emit(w, dpy.title(w), int(quiet))
            finally:
                rec.close()

    return HangWatcher(parent, seconds)


def ask_dialog(window, title, seconds, on_wait=None, parent=None):
    """The question when a program hangs: Wait or Force Close."""
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
    try:
        from eduka_common import _, get_icon
    except Exception:
        _ = lambda s: s; get_icon = None
    d = QDialog(parent, Qt.Dialog | Qt.WindowStaysOnTopHint)
    d.setAttribute(Qt.WA_DeleteOnClose); d.setWindowTitle(_('A program is not answering'))
    v = QVBoxLayout(d); v.setContentsMargins(22, 18, 22, 16); v.setSpacing(10)
    name = title or _('This program')
    head = QLabel(_('{name} is not answering').replace('{name}', name)); head.setWordWrap(True)
    head.setStyleSheet('font-size:15px;font-weight:800;'); head.setTextFormat(Qt.PlainText)
    minutes = round(seconds / 60)
    if seconds < 55:
        when = _('It has not answered for {n} seconds.').replace('{n}', str(int(seconds)))
    elif minutes <= 1:
        when = _('It has not answered for a minute.')
    else:
        when = _('It has not answered for {n} minutes.').replace('{n}', str(minutes))
    text = QLabel(when + ' ' + _('You can wait for it, or force it to close: work that is not saved is lost.'))
    text.setWordWrap(True); text.setMinimumWidth(360)
    v.addWidget(head); v.addWidget(text)
    row = QHBoxLayout(); row.addStretch(1)
    wait = QPushButton(_('Wait')); close = QPushButton(_('Force Close'))
    if get_icon:
        close.setIcon(get_icon('process-stop', 'window-close'))
    close.setStyleSheet('QPushButton{background:#e5484d;color:white;border:0;border-radius:10px;padding:7px 14px;font-weight:800;}'
                        'QPushButton:hover{background:#c93338;}')
    row.addWidget(wait); row.addWidget(close); v.addLayout(row)
    wait.setDefault(True)

    def do_wait():
        if on_wait:
            on_wait(window)
        d.close()

    def do_close():
        ok, msg = force_close_window(window)
        d.close()
    wait.clicked.connect(do_wait); close.clicked.connect(do_close)
    d.rejected.connect(lambda: on_wait(window) if on_wait else None)
    # Without a parent the window must be kept, or Python frees it at once.
    _OPEN_DIALOGS.add(d)
    d.finished.connect(lambda _r, dd=d: _OPEN_DIALOGS.discard(dd))
    d.show(); d.raise_(); d.activateWindow()
    return d


_OPEN_DIALOGS = set()
