#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Date, time and time zone: Eduka-Settings → Date & Time and the Sync time
button of the Action Center.

systemd-timedated does the work (timedatectl) and polkit decides who may.
Edukasaun's rule (50-edukasaun-desktop.rules) lets everyone at the computer
switch network time on and sync the clock, and administrators change the
time zone without a password. Setting the clock by hand, and the time zone
for other accounts, still asks for an administrator password: the clock
could otherwise be moved around Parental Control's daily limit.

Sync time first sets the clock from network time (NTP, which needs no
correct clock), then asks GeoJS - the service Eduka already uses for the
weather - in which time zone the computer is, and follows it.
"""
import json, os, re, shutil, subprocess, time
from pathlib import Path

from eduka_common import DESKTOP_CONFIG_DIR, write_json

CONFIG_FILE = DESKTOP_CONFIG_DIR/'datetime.json'
GEO_URL = 'https://get.geojs.io/v1/ip/geo.json'
HTTP_TIME_HOST = 'deb.debian.org'
REGIONS = ('Africa', 'America', 'Antarctica', 'Arctic', 'Asia', 'Atlantic', 'Australia', 'Europe', 'Indian', 'Pacific')


def _run(cmd, timeout=25):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or '').strip(), (r.stderr or '').strip()
    except subprocess.TimeoutExpired:
        return 124, '', 'timeout'
    except Exception as exc:
        return 127, '', str(exc)


def read_config():
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        data = data if isinstance(data, dict) else {}
    except Exception:
        data = {}
    data.setdefault('auto_timezone', True)
    return data


def save_config(update):
    data = read_config(); data.update(update)
    try: write_json(CONFIG_FILE, data)
    except Exception: pass
    return data


def local_zone():
    try:
        link = os.readlink('/etc/localtime')
        if 'zoneinfo/' in link:
            return link.split('zoneinfo/', 1)[1]
    except OSError:
        pass
    try:
        return Path('/etc/timezone').read_text(encoding='utf-8').strip() or 'UTC'
    except Exception:
        return 'UTC'


def status():
    """What timedated says: zone, network time on, synchronized, possible."""
    info = {'timezone': local_zone(), 'ntp': False, 'synced': False, 'can_ntp': False, 'local_rtc': False,
            'available': False}
    if shutil.which('timedatectl'):
        code, out, _err = _run(['timedatectl', 'show'], 6)
        if code == 0 and out:
            values = dict(line.split('=', 1) for line in out.splitlines() if '=' in line)
            info.update(available=True, timezone=values.get('Timezone') or info['timezone'],
                        ntp=values.get('NTP') == 'yes', synced=values.get('NTPSynchronized') == 'yes',
                        can_ntp=values.get('CanNTP') == 'yes', local_rtc=values.get('LocalRTC') == 'yes')
    return info


_ZONES = None

def zones():
    """Region/City names (and UTC), as timedatectl lists them."""
    global _ZONES
    if _ZONES is not None:
        return _ZONES
    names = []
    if shutil.which('timedatectl'):
        code, out, _err = _run(['timedatectl', 'list-timezones', '--no-pager'], 8)
        if code == 0:
            names = [n.strip() for n in out.splitlines() if n.strip()]
    if not names:
        try:
            import zoneinfo
            names = sorted(zoneinfo.available_timezones())
        except Exception:
            names = []
    keep = sorted({n for n in names if n.split('/', 1)[0] in REGIONS and '/' in n})
    _ZONES = keep + ['UTC']
    return _ZONES


def valid_zone(name):
    name = str(name or '').strip()
    if not re.match(r'^[A-Za-z0-9_+\-]+(/[A-Za-z0-9_+\-]+){0,2}$', name):
        return False
    return name in zones() or (Path('/usr/share/zoneinfo')/name).is_file()


def zone_offset_text(name, when=None):
    """'UTC+09:00' for a zone."""
    try:
        import zoneinfo, datetime
        now = datetime.datetime.fromtimestamp(when or time.time(), zoneinfo.ZoneInfo(name))
        off = now.utcoffset() or datetime.timedelta(0)
        minutes = int(off.total_seconds() // 60); sign = '+' if minutes >= 0 else '-'; minutes = abs(minutes)
        return f'UTC{sign}{minutes // 60:02d}:{minutes % 60:02d}'
    except Exception:
        return ''


def detect_zone(timeout=6):
    """The time zone of the place of the computer (GeoJS), or None."""
    try:
        from eduka_common import _get_json
        tz = str((_get_json(GEO_URL, timeout=timeout) or {}).get('timezone') or '').strip()
        return tz if valid_zone(tz) else None
    except Exception:
        return None


def _timedatectl(args, ask=True):
    if not shutil.which('timedatectl'):
        return False, 'timedatectl is not available.'
    cmd = ['timedatectl'] + ([] if ask else ['--no-ask-password']) + list(args)
    code, _out, err = _run(cmd, 120 if ask else 20)
    if code == 0:
        return True, ''
    low = err.lower()
    if 'access denied' in low or 'not authorized' in low or 'interactive authentication required' in low or 'authentication' in low:
        return False, 'An administrator password is needed.'
    return False, err.splitlines()[-1] if err else 'The clock could not be changed.'


def set_zone(name, ask=True):
    if not valid_zone(name):
        return False, 'Unknown time zone.'
    ok, msg = _timedatectl(['set-timezone', name], ask)
    if ok:
        os.environ.pop('TZ', None)
        try: time.tzset()
        except Exception: pass
    return ok, msg


def set_ntp(on, ask=True):
    return _timedatectl(['set-ntp', 'true' if on else 'false'], ask)


def set_local_rtc(on, ask=True):
    return _timedatectl(['set-local-rtc', '1' if on else '0'], ask)


def set_time(epoch, ask=True):
    """The clock by hand (always asks for an administrator password)."""
    try: time.tzset()
    except Exception: pass
    text = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(epoch)))
    return _timedatectl(['set-time', text], ask)


def http_time(host=HTTP_TIME_HOST, timeout=6):
    """Seconds since 1970 from a web server's Date header. Plain HTTP: a
    computer whose clock is years wrong cannot check HTTPS certificates."""
    import http.client, email.utils
    try:
        conn = http.client.HTTPConnection(host, 80, timeout=timeout)
        conn.request('HEAD', '/', headers={'User-Agent': 'Eduka-Desktop (Edukasaun OS)'})
        date = conn.getresponse().getheader('Date'); conn.close()
        return email.utils.parsedate_to_datetime(date).timestamp() if date else None
    except Exception:
        return None


def wait_synced(seconds=12):
    end = time.time() + seconds
    while time.time() < end:
        if status().get('synced'):
            return True
        time.sleep(0.8)
    return False


def sync_now(follow_zone=None, ask=True):
    """Sync time: the clock from network time, then the time zone of the
    place. Returns {'ok', 'synced', 'zone', 'zone_changed', 'message'}."""
    if follow_zone is None:
        follow_zone = read_config().get('auto_timezone', True)
    res = {'ok': False, 'synced': False, 'zone': local_zone(), 'zone_changed': False, 'message': ''}
    st = status()
    if not st['available']:
        res['message'] = 'The clock service (systemd-timedated) is not running.'
        return res
    notes = []
    if st['can_ntp']:
        # Switching network time off and on again starts a new sync at once.
        if st['ntp']:
            set_ntp(False, ask=False)
        ok, msg = set_ntp(True, ask)
        if ok:
            res['synced'] = wait_synced(12)
            if not res['synced']:
                notes.append('Network time is not reachable now; the clock syncs by itself when it is.')
        else:
            notes.append(msg)
    else:
        stamp = http_time()
        if stamp is None:
            notes.append('No network time service is installed and the internet is not reachable.')
        elif abs(stamp - time.time()) < 2:
            res['synced'] = True
        else:
            ok, msg = set_time(stamp, ask)
            res['synced'] = ok
            if not ok: notes.append(msg)
    if follow_zone:
        zone = detect_zone()
        if zone and zone != st['timezone']:
            ok, msg = set_zone(zone, ask)
            if ok:
                res['zone'], res['zone_changed'] = zone, True
            else:
                notes.append(msg)
        elif not zone:
            notes.append('The time zone could not be found on the internet.')
    res['ok'] = res['synced'] or res['zone_changed']
    if res['ok'] and not notes:
        res['message'] = ('The clock is right. Time zone: {zone}.' if not res['zone_changed']
                          else 'The clock is right. New time zone: {zone}.').replace('{zone}', res['zone'].replace('_', ' '))
    else:
        res['message'] = ' '.join(dict.fromkeys(notes)) or 'The clock could not be synced.'
    return res


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--sync':
        print(json.dumps(sync_now(), indent=1))
    else:
        print(json.dumps(status(), indent=1))
