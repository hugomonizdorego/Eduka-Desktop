# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Fingerprint readers in Eduka-Settings (0.11), the GNU/Linux way:

* fprintd (D-Bus service of libfprint) stores the fingerprints; Eduka uses
  its command line tools fprintd-list, fprintd-enroll, fprintd-verify and
  fprintd-delete as the logged-in user. fprintd asks polkit itself (the
  password window of lxqt-policykit may appear).
* Logging in, unlocking, sudo and polkit use the fingerprint through PAM:
  Debian's libpam-fprintd ships the profile /usr/share/pam-configs/fprintd,
  switched on and off with pam-auth-update by the helper
  /usr/lib/edukasaun-desktop/eduka-fingerprint-apply (pkexec, administrator
  password). pam_fprintd waits a few seconds for a finger, then the password
  is asked as usual, so a password always works.
"""
import os, re, shutil, subprocess

FPRINT_TOOLS = ('fprintd-list', 'fprintd-enroll', 'fprintd-verify', 'fprintd-delete')
PAM_PROFILE = '/usr/share/pam-configs/fprintd'
PAM_COMMON_AUTH = '/etc/pam.d/common-auth'
HELPER = '/usr/lib/edukasaun-desktop/eduka-fingerprint-apply'

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
