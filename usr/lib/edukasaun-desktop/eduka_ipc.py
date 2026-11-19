#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""How the programs of Eduka-Desktop reach each other (0.11 Pre-Stable).

Only the Python standard library is used here, so a key press (Super,
Alt+F1) or a click opens Eduka-Desktop without loading Qt first; on an old
computer that alone took a second or more.

* Eduka-Desktop, the resident start menu (eduka-menu --daemon), reads its
  commands from menu-command.json in the private runtime folder and touches
  menu-daemon.beat every two seconds (its heartbeat).
* Eduka-Panel listens on panel.sock, one command per line (action-center,
  notifications, close-popups, osd volume, trim).

Every file is written to a temporary file of its own first and then renamed,
so two programs that write at the same moment never leave half a file.
"""
import json, os, signal, socket, stat, subprocess, tempfile, threading, time
from pathlib import Path


def _runtime_base():
    """The private runtime folder of this account ($XDG_RUNTIME_DIR, else a
    folder only this account may use; never a shared one where another
    account could take over the lock and state files of another)."""
    base = os.environ.get('XDG_RUNTIME_DIR')
    if base and os.path.isdir(base):
        return Path(base)
    private = Path(tempfile.gettempdir())/f'eduka-runtime-{os.getuid()}'
    try:
        private.mkdir(mode=0o700, exist_ok=True)
        st = os.lstat(private)
        if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid():
            raise OSError('not our own folder')
        if st.st_mode & 0o077:
            os.chmod(private, 0o700)
        return private
    except OSError:
        return Path.home()/'.cache'/'eduka-desktop'/'runtime'


RUNTIME_BASE = _runtime_base()
RUNTIME_DIR = RUNTIME_BASE/'eduka-desktop'
MENU_COMMAND_PATH = RUNTIME_DIR/'menu-command.json'
MENU_DAEMON_PID = RUNTIME_DIR/'menu-daemon.pid'
MENU_DAEMON_BEAT = RUNTIME_DIR/'menu-daemon.beat'
MENU_DAEMON_LOCK = RUNTIME_DIR/'menu-daemon.lock'
PANEL_SOCKET = RUNTIME_DIR/'panel.sock'
# Without a heartbeat for this long the daemon is asked once more (ping)
# and only stopped when it does not answer.
BEAT_STALE_SECONDS = 20
PING_WAIT_SECONDS = 2.5


def runtime_dir():
    try:
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return RUNTIME_DIR


def write_atomic(path, text):
    """Write a file through a temporary file of this process and thread,
    then rename it: readers see the old or the new file, never a mix."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f'.{path.name}.{os.getpid()}-{threading.get_ident()}.tmp')
    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_json_atomic(path, data, indent=4):
    write_atomic(path, json.dumps(data, indent=indent, ensure_ascii=False))


# ---------------------------------------------------------------- Eduka-Desktop (start menu)
_SEQ = {'n': 0}


def send_menu_command(action='toggle'):
    """Ask the resident Eduka-Desktop to show, hide or toggle itself (and a
    few more commands, see eduka-menu: check_command)."""
    runtime_dir()
    _SEQ['n'] += 1
    now = time.time()
    payload = {'action': str(action), 'time': now,
               # Unique also for two commands in the same millisecond.
               'id': f'{time.time_ns()}-{os.getpid()}-{_SEQ["n"]}'}
    try:
        write_json_atomic(MENU_COMMAND_PATH, payload, indent=None)
        return True
    except OSError:
        return False


def _pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def _is_eduka_menu(pid):
    try:
        cmd = Path(f'/proc/{int(pid)}/cmdline').read_bytes().replace(b'\0', b' ').decode('utf-8', 'ignore')
        state = Path(f'/proc/{int(pid)}/stat').read_text().split(')')[-1].split()[0]
        return 'eduka-menu' in cmd and state != 'Z'
    except (OSError, ValueError, IndexError):
        return False


def _beat_mtime():
    try:
        return MENU_DAEMON_BEAT.stat().st_mtime_ns
    except OSError:
        return None


def menu_daemon_pid():
    try:
        pid = int(MENU_DAEMON_PID.read_text().strip())
    except (OSError, ValueError):
        return None
    return pid if _pid_alive(pid) and _is_eduka_menu(pid) else None


def menu_daemon_alive(ping_wait=PING_WAIT_SECONDS):
    """True when the resident Eduka-Desktop runs and answers.

    A daemon whose heartbeat is old is asked once (ping) before it is
    stopped: after a suspend, a clock change (time sync) or on a busy old
    computer the heartbeat can be old although the menu is fine, and
    stopping it then made the next opening slow (RC3)."""
    pid = menu_daemon_pid()
    if pid is None:
        return False
    try:
        beat = MENU_DAEMON_BEAT.stat().st_mtime
        started = MENU_DAEMON_PID.stat().st_mtime
    except OSError:
        return True          # an older daemon without heartbeat
    now = time.time()
    if now - beat <= BEAT_STALE_SECONDS or now - started <= BEAT_STALE_SECONDS + 10:
        return True
    before = _beat_mtime()
    send_menu_command('ping')
    end = time.monotonic() + max(0.0, ping_wait)
    while time.monotonic() < end:
        time.sleep(0.05)
        if _beat_mtime() != before:
            return True
        if not _pid_alive(pid):
            return False
    # No answer: the daemon hangs. Stop it so the next opening starts a
    # fresh one instead of writing commands nobody reads.
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.kill(pid, sig)
        except OSError:
            break
        time.sleep(0.3)
        if not _pid_alive(pid):
            break
    for f in (MENU_DAEMON_PID, MENU_DAEMON_BEAT):
        try:
            f.unlink()
        except OSError:
            pass
    return False


def start_menu_daemon(show=False):
    """Start the resident Eduka-Desktop (it refuses to run twice)."""
    env = os.environ.copy()
    try:
        subprocess.Popen(['eduka-menu', '--daemon'] + (['--show'] if show else []), env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return True
    except OSError:
        return False


def menu_client(action='toggle'):
    """eduka-menu --toggle | --show | --hide without the daemon's Qt."""
    runtime_dir()
    if menu_daemon_alive():
        return send_menu_command(action)
    if action == 'hide':
        return start_menu_daemon(show=False)
    return start_menu_daemon(show=True)


# ---------------------------------------------------------------- Eduka-Panel
def panel_command(command, timeout=0.4):
    """Send one command to Eduka-Panel (panel.sock). False when it is not
    running or does not take it."""
    path = str(PANEL_SOCKET)
    if len(path.encode()) >= 108 or not os.path.exists(path):
        return False
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.settimeout(timeout)
        s.connect(path)
        s.sendall(str(command).strip().encode('utf-8')[:200] + b'\n')
        return True
    except OSError:
        return False
    finally:
        s.close()



# ---------------------------------------------------------------- notifications
def _gvariant_string(text):
    return "'" + str(text).replace('\\', '\\\\').replace("'", "\\'") + "'"


def notify(summary, body='', icon='dialog-information', app='Eduka-Desktop'):
    """A desktop notification (shown by Eduka-Panel, the notification server
    of the session). notify-send (libnotify-bin) is not always installed, so
    gdbus (libglib2.0-bin) sends it too. False when neither can."""
    import shutil
    if shutil.which('notify-send'):
        cmd = ['notify-send', '-a', app, '-i', icon, summary, body]
    elif shutil.which('gdbus'):
        cmd = ['gdbus', 'call', '--session', '--dest', 'org.freedesktop.Notifications',
               '--object-path', '/org/freedesktop/Notifications', '--method', 'org.freedesktop.Notifications.Notify',
               _gvariant_string(app), 'uint32 0', _gvariant_string(icon), _gvariant_string(summary), _gvariant_string(body),
               '@as []', '@a{sv} {}', 'int32 -1']
    else:
        return False
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return True
    except OSError:
        return False

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == 'panel':
        sys.exit(0 if panel_command(' '.join(sys.argv[2:])) else 1)
    if len(sys.argv) > 2 and sys.argv[1] == 'notify':
        sys.exit(0 if notify(*sys.argv[2:5]) else 1)
    sys.exit(0 if menu_client(sys.argv[1] if len(sys.argv) > 1 else 'toggle') else 1)
