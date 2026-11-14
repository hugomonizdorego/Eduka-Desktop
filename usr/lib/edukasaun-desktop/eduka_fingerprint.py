# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Fingerprint readers in Eduka-Settings (0.11), the GNU/Linux way:

* fprintd (D-Bus service of libfprint) stores the fingerprints; Eduka uses
  its command line tools fprintd-list, fprintd-enroll, fprintd-verify and
  fprintd-delete as the logged-in user. fprintd asks polkit itself (the
  password window of lxqt-policykit may appear).
* Logging in, unlocking, sudo and polkit use the fingerprint through PAM.
  Since 0.11 RC3 the Edukasaun profile /usr/share/pam-configs/eduka-fingerprint
  asks for the password first and for the finger second (an empty password
  and Enter, or the fingerprint button of the login screen), so a typed
  password never waits for the reader. The helper
  /usr/lib/edukasaun-desktop/eduka-fingerprint-apply switches it with
  pam-auth-update (pkexec, administrator password).
* Every fingerprint reader on USB is found, also one libfprint does not
  support yet (0.11 RC3): the list of libfprint in udev's hardware database
  says which driver supports it, and a hint says what can make the others
  work. A forgotten password can be replaced after logging in with a finger
  (Eduka-Settings → Users, polkit asks for the finger).
"""
import os, re, shutil, subprocess

FPRINT_TOOLS = ('fprintd-list', 'fprintd-enroll', 'fprintd-verify', 'fprintd-delete')
PAM_PROFILE = '/usr/share/pam-configs/fprintd'
PAM_COMMON_AUTH = '/etc/pam.d/common-auth'
HELPER = '/usr/lib/edukasaun-desktop/eduka-fingerprint-apply'
FLAG = '/var/lib/edukasaun-desktop/login/fingerprint'
SYS_USB = '/sys/bus/usb/devices'
HWDB_DIRS = ('/usr/lib/udev/hwdb.d', '/lib/udev/hwdb.d', '/etc/udev/hwdb.d')
INSTALL_PACKAGES = ('fprintd', 'libpam-fprintd')

# USB makers of fingerprint readers. The first ones make (almost) nothing
# else on USB; Synaptics, Elan and others also make touchpads and screens.
READER_VENDORS = {'138a': 'Validity Sensors', '27c6': 'Goodix', '2808': 'FocalTech', '08ff': 'AuthenTec',
                  '147e': 'UPEK', '1c7a': 'Egis Technology', '298d': 'Next Biometrics', '10a5': 'Fingerprint Cards',
                  '1162': 'SecuGen', '05ba': 'DigitalPersona', '1491': 'Futronic', '061a': 'Veridicom', '2541': 'Chipsailing',
                  '3274': 'Realtek fingerprint'}
OTHER_VENDORS = {'06cb': 'Synaptics', '04f3': 'Elan', '0483': 'STMicroelectronics', '1fc9': 'NXP'}
NAMED = re.compile(r'finger|fprint|biometric|\bfpc\b|match.on.chip|validity|fingerprint', re.I)

FINGERS = [
    ('right-index-finger', 'Right index finger'), ('right-thumb', 'Right thumb'),
    ('right-middle-finger', 'Right middle finger'), ('right-ring-finger', 'Right ring finger'),
    ('right-little-finger', 'Right little finger'), ('left-index-finger', 'Left index finger'),
    ('left-thumb', 'Left thumb'), ('left-middle-finger', 'Left middle finger'),
    ('left-ring-finger', 'Left ring finger'), ('left-little-finger', 'Left little finger'),
]
FINGER_NAMES = dict(FINGERS)

# fprintd-enroll prints "Enroll result: <status>" for every scan.
ENROLL_MESSAGES = {
    'enroll-stage-passed': 'Good. Lift your finger and place it on the reader again.',
    'enroll-retry-scan': 'That scan did not work. Place your finger on the reader again.',
    'enroll-swipe-too-short': 'The swipe was too short. Swipe your finger again.',
    'enroll-finger-not-centered': 'Place your finger in the middle of the reader.',
    'enroll-remove-and-retry': 'Lift your finger and place it on the reader again.',
    'enroll-completed': 'Done: the fingerprint is saved.',
    'enroll-duplicate': 'This finger is already saved for this account.',
    'enroll-data-full': 'The reader has no room for more fingerprints. Remove one first.',
    'enroll-disconnected': 'The fingerprint reader was disconnected.',
    'enroll-failed': 'The fingerprint could not be saved. Please try again.',
    'enroll-unknown-error': 'The fingerprint reader reported an error. Please try again.',
}
ENROLL_DONE = {'enroll-completed'}
ENROLL_FAILED = {'enroll-duplicate', 'enroll-data-full', 'enroll-disconnected', 'enroll-failed', 'enroll-unknown-error'}
VERIFY_MESSAGES = {
    'verify-match': 'The finger was recognized.',
    'verify-no-match': 'The finger was not recognized.',
    'verify-retry-scan': 'Place your finger on the reader again.',
    'verify-swipe-too-short': 'The swipe was too short. Swipe your finger again.',
    'verify-finger-not-centered': 'Place your finger in the middle of the reader.',
    'verify-remove-and-retry': 'Lift your finger and place it on the reader again.',
    'verify-disconnected': 'The fingerprint reader was disconnected.',
    'verify-unknown-error': 'The fingerprint reader reported an error.',
}


def fprintd_installed():
    return all(shutil.which(t) for t in FPRINT_TOOLS)


def pam_profile_installed():
    return os.path.isfile(PAM_PROFILE)


def pam_enabled():
    """True when pam_fprintd is part of the login stack (common-auth)."""
    try:
        with open(PAM_COMMON_AUTH, encoding='utf-8', errors='ignore') as f:
            return any('pam_fprintd.so' in line and not line.lstrip().startswith('#') for line in f)
    except OSError:
        return False


def user_name():
    import pwd
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except KeyError:
        return os.environ.get('USER', '')


def parse_list(text):
    """(reader name, [fingers]) from fprintd-list output; reader '' = none."""
    reader = ''
    fingers = []
    for line in (text or '').splitlines():
        m = re.search(r'Fingerprints for user \S+ on (.+?):\s*$', line)
        if m:
            reader = m.group(1).strip(); continue
        m = re.search(r'User \S+ has no fingers enrolled for (.+?)\.?\s*$', line)
        if m:
            reader = m.group(1).strip(); continue
        m = re.match(r'\s*-\s*#\d+:\s*(\S+)', line)
        if m and m.group(1) in FINGER_NAMES:
            fingers.append(m.group(1))
    return reader, fingers


def list_fingers(user=None, timeout=12):
    """{'reader': name or '', 'fingers': [...], 'error': text or ''}."""
    if not fprintd_installed():
        return {'reader': '', 'fingers': [], 'error': 'not-installed'}
    try:
        r = subprocess.run(['fprintd-list', user or user_name()], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {'reader': '', 'fingers': [], 'error': 'timeout'}
    except OSError as e:
        return {'reader': '', 'fingers': [], 'error': str(e)}
    out = (r.stdout or '') + (r.stderr or '')
    reader, fingers = parse_list(out)
    if not reader and re.search(r'No devices available|found 0 devices', out, re.I):
        return {'reader': '', 'fingers': [], 'error': 'no-reader'}
    if not reader and r.returncode != 0:
        return {'reader': '', 'fingers': [], 'error': out.strip().splitlines()[-1] if out.strip() else 'error'}
    return {'reader': reader, 'fingers': fingers, 'error': ''}


def enroll_status(line):
    """'enroll-stage-passed' … from a line of fprintd-enroll, or ''."""
    m = re.search(r'Enroll result:\s*(\S+)', line)
    return m.group(1) if m else ''


def verify_status(line):
    m = re.search(r'Verify result:\s*(\S+)', line)
    return m.group(1) if m else ''


def delete_args(finger=None, user=None):
    args = ['fprintd-delete', user or user_name()]
    if finger:
        args += ['-f', finger]
    return args


# ---------------------------------------------------------------- hardware (0.11 RC3)
def libfprint_devices():
    """{(vid, pid): driver} of the readers udev's hardware database knows
    (systemd and libfprint ship it); driver '' = known but not supported."""
    known = {}
    for folder in HWDB_DIRS:
        try:
            names = sorted(os.listdir(folder))
        except OSError:
            continue
        for name in names:
            if 'fprint' not in name and 'fingerprint' not in name:
                continue
            driver = ''
            try:
                with open(os.path.join(folder, name), encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        m = re.match(r'#\s*Supported by libfprint driver\s+(\S+)', line)
                        if m:
                            driver = m.group(1); continue
                        if re.match(r'#\s*Known unsupported', line, re.I):
                            driver = ''; continue
                        m = re.match(r'usb:v([0-9A-Fa-f]{4})p([0-9A-Fa-f]{4})', line)
                        if m:
                            key = (m.group(1).lower(), m.group(2).lower())
                            if driver or key not in known:
                                known[key] = driver
            except OSError:
                continue
    return known


def usb_devices():
    out = []
    try:
        entries = sorted(os.listdir(SYS_USB))
    except OSError:
        return out
    for entry in entries:
        base = os.path.join(SYS_USB, entry)
        def read(key):
            try:
                with open(os.path.join(base, key), encoding='utf-8', errors='ignore') as f:
                    return f.read().strip()
            except OSError:
                return ''
        vid, pid = read('idVendor').lower(), read('idProduct').lower()
        if vid and pid:
            out.append({'vid': vid, 'pid': pid, 'name': read('product'), 'maker': read('manufacturer'), 'path': entry})
    return out


def reader_hint(vid, state, driver=''):
    if state == 'supported':
        return 'Supported by libfprint (driver {driver}).'.replace('{driver}', driver)
    if vid == '138a' or vid == '06cb' and state == 'unsupported':
        return ('libfprint does not support this Validity / Synaptics reader. On many ThinkPad laptops the '
                'community driver python-validity (with open-fprintd) makes it work.')
    if vid == '27c6':
        return ('Goodix reader: some need a newer libfprint, others work only with the driver of the computer '
                'maker (libfprint-2-tod1-goodix).')
    if vid == '06cb':
        return 'Synaptics reader: newer libfprint versions support most of them; keep the system up to date.'
    if vid == '04f3':
        return 'Elan reader: libfprint supports many of them; a system update may add this one.'
    if vid == '1c7a':
        return 'Egis reader: libfprint supports some of them (egis0570, egismoc); a system update may add this one.'
    if vid == '2808':
        return 'FocalTech reader: newer libfprint versions support some of them (focaltech_moc).'
    if state == 'unsupported':
        return 'libfprint knows this reader but cannot use it yet.'
    return 'Not in the list of libfprint on this computer. A system update may add it.'


def readers():
    """Every fingerprint reader on USB: [{id, maker, name, state, driver,
    hint}] with state supported, unsupported or unknown."""
    known = libfprint_devices()
    found = []
    for d in usb_devices():
        key = (d['vid'], d['pid'])
        text = f"{d['name']} {d['maker']}"
        if key not in known and not NAMED.search(text) and d['vid'] not in READER_VENDORS:
            continue
        driver = known.get(key)
        state = 'supported' if driver else ('unsupported' if key in known else 'unknown')
        maker = READER_VENDORS.get(d['vid']) or OTHER_VENDORS.get(d['vid']) or d['maker'] or 'Unknown maker'
        found.append({'id': f"{d['vid']}:{d['pid']}", 'maker': maker, 'name': d['name'] or 'Fingerprint reader',
                      'state': state, 'driver': driver or '', 'hint': reader_hint(d['vid'], state, driver or '')})
    return found


def pam_mode():
    """password-first, finger-first or off."""
    try:
        with open(PAM_COMMON_AUTH, encoding='utf-8', errors='ignore') as f:
            lines = [l for l in f if l.strip() and not l.lstrip().startswith('#')]
    except OSError:
        return 'off'
    fp = next((i for i, l in enumerate(lines) if 'pam_fprintd.so' in l), None)
    if fp is None:
        return 'off'
    unix = next((i for i, l in enumerate(lines) if 'pam_unix.so' in l), None)
    return 'password-first' if unix is not None and unix < fp else 'finger-first'


def install_command():
    """A terminal command that installs fingerprint support (apt asks for
    the password there)."""
    return ['sh', '-c', 'echo "Installing fingerprint support (fprintd, libpam-fprintd)..."; echo; '
                        'sudo apt-get install ' + ' '.join(INSTALL_PACKAGES) + '; echo; '
                        'printf "Press Enter to close this window. "; read _answer']
