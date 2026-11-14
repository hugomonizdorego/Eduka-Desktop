#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Memory of Eduka-Desktop and of the computer (0.11 RC3).

Eduka-Desktop keeps a computer with little memory running smoothly:

* its own resident programs (Eduka-Panel and Eduka-Desktop) use at most two
  malloc arenas and give freed memory back to the system after a menu or a
  popup closes ("memory saver", on by default);
* Eduka-Panel watches the free memory (/proc/meminfo, every 30 seconds) and
  warns before the computer starts to freeze, naming the program that uses
  the most;
* Eduka-Settings → Maintenance → Memory shows the memory, the programs that
  use the most (one line per program, all its processes together) and
  switches zram (compressed memory, package zram-tools) and earlyoom (stops
  the biggest program instead of letting the computer freeze) through the
  helper eduka-memory-apply (administrator password).

Only /proc and /sys are read; nothing here needs administrator rights.
"""
import ctypes, ctypes.util, gc, json, os, re, shutil, signal, subprocess
from pathlib import Path

HELPER = '/usr/lib/edukasaun-desktop/eduka-memory-apply'
LOW_PERCENT, CRITICAL_PERCENT, CRITICAL_MB = 12, 6, 220
# Programs that keep the session running: never offered to be closed.
PROTECTED = {'lxqt-session', 'eduka-panel', 'eduka-menu', 'eduka-desktop-session', 'eduka-desktop-se', 'xfwm4',
             'openbox', 'kwin_x11', 'kwin_wayland', 'labwc', 'picom', 'lxqt-globalkeysd', 'lxqt-globalkeys',
             'lxqt-policykit-agent', 'lxqt-policykit', 'lxqt-powermanagement', 'lxqt-powermanagem', 'pcmanfm-qt',
             'Xorg', 'Xwayland', 'dbus-daemon', 'dbus-broker', 'systemd', 'pipewire', 'pipewire-pulse',
             'wireplumber', 'pulseaudio', 'at-spi-bus-launcher', 'at-spi2-registryd', 'ssh-agent', 'gpg-agent',
             'startlxqt', 'xdg-desktop-portal', 'xdg-document-portal', 'xdg-permission-store', 'gvfsd', 'sh', 'bash'}
M_ARENA_MAX = -8
_libc = None


def _c():
    global _libc
    if _libc is None:
        try:
            _libc = ctypes.CDLL(ctypes.util.find_library('c') or 'libc.so.6')
        except OSError:
            _libc = False
    return _libc or None


def limit_arenas(count=2):
    """At most `count` malloc arenas for this process (glibc makes one per
    thread otherwise, each holding freed memory). Call it early."""
    libc = _c()
    if libc is not None:
        try:
            libc.mallopt(M_ARENA_MAX, int(count))
        except (AttributeError, OSError):
            pass


def rss_mb(pid='self'):
    try:
        with open(f'/proc/{pid}/status', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('VmRSS:'):
                    return int(line.split()[1]) / 1024
    except OSError:
        pass
    return 0.0


def trim(qt=False):
    """Give freed memory of this process back to the system (and with qt=True
    the drawn-icon cache of Qt). Returns the MB given back."""
    before = rss_mb()
    gc.collect()
    if qt:
        try:
            from PyQt5.QtGui import QPixmapCache
            QPixmapCache.clear()
        except Exception:
            pass
    libc = _c()
    if libc is not None:
        try:
            libc.malloc_trim(0)
        except (AttributeError, OSError):
            pass
    return max(0.0, before - rss_mb())


# ---------------------------------------------------------------- the computer
def meminfo():
    info = {}
    try:
        with open('/proc/meminfo', encoding='utf-8') as f:
            for line in f:
                key, _sep, rest = line.partition(':')
                parts = rest.split()
                if parts and parts[0].isdigit():
                    info[key] = int(parts[0])
    except OSError:
        pass
    return info


def summary(info=None):
    """Memory in MB: total, available, used, percent_used; swap total and
    used; zram True when compressed memory is in use."""
    info = info or meminfo()
    total = info.get('MemTotal', 0) / 1024
    avail = info.get('MemAvailable', info.get('MemFree', 0)) / 1024
    swap_total = info.get('SwapTotal', 0) / 1024
    swap_used = swap_total - info.get('SwapFree', 0) / 1024
    used = max(0.0, total - avail)
    return {'total': total, 'available': avail, 'used': used, 'percent_used': (used * 100 / total) if total else 0.0,
            'swap_total': swap_total, 'swap_used': max(0.0, swap_used), 'zram': zram_active()}


def pressure(s=None):
    """ok, low or critical."""
    s = s or summary()
    if not s['total']:
        return 'ok'
    free_pct = s['available'] * 100 / s['total']
    if free_pct < CRITICAL_PERCENT or s['available'] < CRITICAL_MB:
        return 'critical'
    if free_pct < LOW_PERCENT:
        return 'low'
    return 'ok'


def _process_name(pid):
    try:
        with open(f'/proc/{pid}/cmdline', 'rb') as f:
            args = [a.decode('utf-8', 'ignore') for a in f.read().split(b'\0') if a]
    except OSError:
        args = []
    comm = ''
    try:
        comm = Path(f'/proc/{pid}/comm').read_text(encoding='utf-8', errors='ignore').strip()
    except OSError:
        pass
    if args:
        first = os.path.basename(args[0])
        # python3 /usr/bin/eduka-settings → eduka-settings
        if re.match(r'^python[0-9.]*$', first) and len(args) > 1:
            first = os.path.basename(next((a for a in args[1:] if not a.startswith('-')), first))
        if first:
            return first
    return comm


def top_programs(limit=8, uid=None):
    """[{name, pids, mb, protected}] of this user's programs, the biggest
    first; every process of a program (a web browser has many) counted
    together."""
    uid = os.getuid() if uid is None else uid
    groups = {}
    for entry in os.listdir('/proc'):
        if not entry.isdigit():
            continue
        try:
            if os.stat(f'/proc/{entry}').st_uid != uid:
                continue
        except OSError:
            continue
        mb = rss_mb(entry)
        if mb <= 0:
            continue
        name = _process_name(entry)
        if not name:
            continue
        key = re.sub(r'[-_]?(bin|helper|renderer|gpu-process|utility|crashpad.*|content|web|tab|zygote)$', '', name) or name
        g = groups.setdefault(key, {'name': key, 'pids': [], 'mb': 0.0})
        g['pids'].append(int(entry)); g['mb'] += mb
    out = sorted(groups.values(), key=lambda g: g['mb'], reverse=True)[:limit]
    for g in out:
        g['protected'] = g['name'] in PROTECTED or g['name'].startswith(('lxqt-', 'eduka-')) or os.getpid() in g['pids']
    return out


def close_program(pids):
    """Ask the processes of a program to close (SIGTERM, like closing its
    windows); only this user's own processes, never a protected one."""
    done = 0
    for pid in pids:
        try:
            if os.stat(f'/proc/{pid}').st_uid != os.getuid() or pid == os.getpid():
                continue
            if _process_name(pid) in PROTECTED:
                continue
            os.kill(int(pid), signal.SIGTERM); done += 1
        except (OSError, ValueError):
            continue
    return done


# ---------------------------------------------------------------- zram, earlyoom, swappiness
def _unit_exists(name):
    return any(Path(d, name).exists() for d in ('/lib/systemd/system', '/usr/lib/systemd/system', '/etc/systemd/system'))


def _active(unit):
    if not shutil.which('systemctl'):
        return False
    try:
        return subprocess.run(['systemctl', 'is-active', '--quiet', unit], timeout=3).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def zram_installed():
    return _unit_exists('zramswap.service') or os.path.exists('/usr/sbin/zramswap')


def zram_active():
    try:
        with open('/proc/swaps', encoding='utf-8') as f:
            return any(line.split()[0].startswith('/dev/zram') for line in f.readlines()[1:] if line.split())
    except OSError:
        return False


def earlyoom_installed():
    return bool(shutil.which('earlyoom')) or _unit_exists('earlyoom.service')


def earlyoom_active():
    return _active('earlyoom.service')


def swappiness():
    try:
        return int(Path('/proc/sys/vm/swappiness').read_text().strip())
    except (OSError, ValueError):
        return 60


def run_helper(*args, timeout=180):
    """eduka-memory-apply through pkexec. (ok, message)."""
    if not shutil.which('pkexec') or not os.path.exists(HELPER):
        return False, 'The Eduka memory helper or pkexec is missing.'
    try:
        r = subprocess.run(['pkexec', HELPER, *args], capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    if r.returncode in (126, 127):
        return False, 'administrator password was not given'
    lines = (r.stderr if r.returncode else r.stdout or '').strip().splitlines()
    return r.returncode == 0, lines[-1] if lines else ''


def install_command():
    return ['sh', '-c', 'echo "Installing zram-tools and earlyoom (memory helpers)..."; echo; '
                        'sudo apt-get install zram-tools earlyoom; echo; '
                        'printf "Press Enter to close this window. "; read _answer']


# ---------------------------------------------------------------- preferences
def prefs_file():
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')/'eduka-desktop'/'desktop'/'memory.json'


def read_prefs():
    try:
        data = json.loads(prefs_file().read_text(encoding='utf-8'))
        if isinstance(data, dict):
            return {'saver': bool(data.get('saver', True)), 'warn': bool(data.get('warn', True))}
    except (OSError, ValueError):
        pass
    return {'saver': True, 'warn': True}


def save_prefs(prefs):
    path = prefs_file(); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps({'saver': bool(prefs.get('saver', True)), 'warn': bool(prefs.get('warn', True))}) + '\n',
                   encoding='utf-8')
    os.replace(tmp, path)


if __name__ == '__main__':
    s = summary()
    print(json.dumps(s, indent=1), pressure(s))
    for g in top_programs():
        print('%8.0f MB  %-24s %s' % (g['mb'], g['name'], '(session)' if g['protected'] else ''))
