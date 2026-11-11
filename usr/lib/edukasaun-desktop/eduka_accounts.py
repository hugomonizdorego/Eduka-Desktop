# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""User accounts for Eduka-Settings → Users (0.11 RC2).

* Reading the accounts needs no rights (passwd, group, AccountsService).
* Changing other accounts runs /usr/lib/edukasaun-desktop/eduka-users-apply
  through pkexec (polkit action org.edukasaun.desktop.users, administrator
  password); it checks every value again.
* Your own picture and name go through AccountsService (allowed for your own
  account without a password), your own password through passwd(1) on a
  pseudo terminal, so a standard account can change them as well.

Pictures: AccountsService keeps one picture per account in
/var/lib/AccountsService/icons. SDDM (Eduka's theme), slick-greeter and
lightdm-gtk-greeter read it there; ~/.face and ~/.face.icon get the same
picture for programs that read those, so every place shows the same face.
"""
import grp, json, os, pwd, re, select, shutil, subprocess, time, unicodedata
from pathlib import Path

HELPER = '/usr/lib/edukasaun-desktop/eduka-users-apply'
HIDDEN_FILE = '/etc/edukasaun-desktop/hidden-users'
ACCOUNTS_ICONS = '/var/lib/AccountsService/icons'
ADMIN_GROUP = 'sudo'
UID_MIN, UID_MAX = 1000, 60000
NAME_RE = re.compile(r'^[a-z_][a-z0-9_-]{0,31}$')
# Names that belong to the system or to Edukasaun OS itself.
RESERVED = {'root', 'daemon', 'bin', 'sys', 'sync', 'games', 'man', 'lp', 'mail', 'news', 'uucp', 'proxy',
            'www-data', 'backup', 'list', 'irc', 'gnats', 'nobody', 'systemd-network', 'systemd-resolve',
            'messagebus', 'sddm', 'lightdm', 'polkitd', 'avahi', 'colord', 'pulse', 'rtkit', 'saned',
            'usbmux', 'geoclue', 'admin', 'administrator', 'sudo', 'users', 'edukasaun', 'guest'}


def _valid_shell(shell):
    return os.path.basename(shell or '') not in ('nologin', 'false', '')


def admin_names():
    """Members of the administrator group (sudo)."""
    try:
        g = grp.getgrnam(ADMIN_GROUP)
    except KeyError:
        return set()
    names = set(g.gr_mem)
    for p in pwd.getpwall():
        if p.pw_gid == g.gr_gid:
            names.add(p.pw_name)
    return names


def _sddm_hidden():
    names = set()
    files = sorted(Path('/etc/sddm.conf.d').glob('*.conf')) if Path('/etc/sddm.conf.d').is_dir() else []
    for path in files + [Path('/etc/sddm.conf')]:
        try:
            section = ''
            for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
                line = line.strip()
                if line.startswith('['):
                    section = line.strip('[]')
                elif section == 'Users' and line.startswith('HideUsers='):
                    names = {n.strip() for n in line.split('=', 1)[1].split(',') if n.strip()}
        except OSError:
            continue
    return names


def hidden_names():
    """Accounts that the login screens do not list."""
    names = set()
    try:
        names |= {l.strip() for l in Path(HIDDEN_FILE).read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')}
    except OSError:
        pass
    return names | _sddm_hidden()


def logged_in(uid):
    """True when a program of this account runs (a session is open)."""
    for d in os.listdir('/proc'):
        if d.isdigit():
            try:
                if os.stat(f'/proc/{d}').st_uid == uid:
                    return True
            except OSError:
                continue
    return False


def avatar_path(name, home=''):
    """The picture shown for the account ('' = none)."""
    for path in (os.path.join(ACCOUNTS_ICONS, name),
                 os.path.join(home, '.face.icon') if home else '',
                 os.path.join(home, '.face') if home else ''):
        if path and os.path.isfile(path) and os.access(path, os.R_OK):
            return path
    return ''


def account_locked(name):
    """True / False from AccountsService ('Locked'), None when unknown."""
    user = _accounts_user(name)
    if user is None:
        return None
    value = user.property('Locked')
    return bool(value) if value is not None else None


def list_users():
    me = os.getuid()
    admins = admin_names(); hidden = hidden_names()
    out = []
    for p in pwd.getpwall():
        if not (UID_MIN <= p.pw_uid < UID_MAX) or p.pw_name == 'nobody' or not _valid_shell(p.pw_shell):
            continue
        full = (p.pw_gecos or '').split(',')[0].strip()
        out.append({'name': p.pw_name, 'full_name': full, 'uid': p.pw_uid, 'home': p.pw_dir, 'shell': p.pw_shell,
                    'admin': p.pw_name in admins, 'hidden': p.pw_name in hidden, 'current': p.pw_uid == me,
                    'login_shell': _valid_shell(p.pw_shell), 'logged_in': logged_in(p.pw_uid),
                    'avatar': avatar_path(p.pw_name, p.pw_dir), 'locked': account_locked(p.pw_name)})
    out.sort(key=lambda u: (not u['current'], (u['full_name'] or u['name']).casefold()))
    return out


def suggest_name(full_name, taken=None):
    """'Maria da Costa' -> 'maria'; a free login name (letters a-z only)."""
    taken = set(taken or ())
    text = unicodedata.normalize('NFKD', full_name or '').encode('ascii', 'ignore').decode().lower()
    words = [w for w in re.findall(r'[a-z0-9]+', text) if w]
    if not words:
        return ''
    base = words[0] if words[0][0].isalpha() else 'u' + words[0]
    base = base[:20]
    candidates = [base]
    if len(words) > 1:
        candidates.append((base + words[-1])[:24])
    candidates += [f'{base}{n}' for n in range(2, 100)]
    for c in candidates:
        if NAME_RE.match(c) and c not in RESERVED and c not in taken and not _name_in_use(c):
            return c
    return ''


def _name_in_use(name):
    try:
        pwd.getpwnam(name); return True
    except KeyError:
        pass
    try:
        grp.getgrnam(name); return True
    except KeyError:
        return False


def check_name(name):
    """'' when the login name can be used, else the reason."""
    if not NAME_RE.match(name or ''):
        return 'Login names use small letters a-z, digits, - and _ and start with a letter (at most 32).'
    if name in RESERVED:
        return 'This name belongs to the system.'
    if _name_in_use(name):
        return 'This name is already used.'
    return ''


def check_full_name(text):
    if any(c in (text or '') for c in ':,=\n\r\t') or len(text or '') > 64:
        return 'The full name can have up to 64 characters, without : , or =.'
    return ''


def password_hint(password):
    """A short note on how strong a password is ('' = fine)."""
    if len(password) < 6:
        return 'Short password: easy to guess. Use at least 6 characters.'
    if password.isdigit() or password.isalpha():
        return 'Mix letters and digits for a stronger password.'
    return ''


# ------------------------------------------------------------------ root helper
def run_helper(request, timeout=180):
    """Run eduka-users-apply through pkexec. Returns (ok, message)."""
    if shutil.which('pkexec') is None or not os.path.exists(HELPER):
        return False, 'Accounts can only be changed on Edukasaun OS (pkexec or the Eduka helper is missing).'
    try:
        r = subprocess.run(['pkexec', HELPER], input=json.dumps(request), capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        return False, str(e)
    if r.returncode == 0:
        return True, (r.stdout or '').strip().splitlines()[-1] if (r.stdout or '').strip() else ''
    if r.returncode in (126, 127):
        return False, 'administrator password was not given'
    lines = (r.stderr or r.stdout or '').strip().splitlines()
    return False, lines[-1] if lines else 'unknown error'


# ------------------------------------------------------------------ pictures
def make_avatar(source, target, size=256):
    """Square PNG for an account picture: the middle of the picture, scaled
    smoothly. `source` is a path or a QImage. Returns True on success."""
    from PyQt5.QtGui import QImage, QImageReader
    from PyQt5.QtCore import Qt
    if isinstance(source, QImage):
        img = source
    else:
        reader = QImageReader(str(source)); reader.setAutoTransform(True)
        img = reader.read()
    if img.isNull():
        return False
    side = min(img.width(), img.height())
    img = img.copy((img.width() - side) // 2, (img.height() - side) // 2, side, side)
    img = img.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    return img.save(str(target), 'PNG')


def initials_avatar(full_name, login, color='#3fa684', size=256):
    """A colored circle with the initials (when no picture is chosen)."""
    from PyQt5.QtGui import QImage, QPainter, QColor, QFont
    from PyQt5.QtCore import Qt, QRectF
    words = [w for w in re.split(r'\s+', (full_name or login or '?').strip()) if w]
    text = ''.join(w[0] for w in words[:2]).upper() or '?'
    img = QImage(size, size, QImage.Format_ARGB32_Premultiplied); img.fill(Qt.transparent)
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing)
    p.setPen(Qt.NoPen); p.setBrush(QColor(color)); p.drawEllipse(QRectF(0, 0, size, size))
    f = QFont(); f.setPixelSize(int(size * 0.40)); f.setBold(True); p.setFont(f); p.setPen(QColor('#ffffff'))
    p.drawText(QRectF(0, 0, size, size), Qt.AlignCenter, text); p.end()
    return img


def _accounts_user(name):
    """QDBusInterface of the AccountsService user, or None."""
    try:
        from PyQt5.QtDBus import QDBusConnection, QDBusInterface
    except Exception:
        return None
    bus = QDBusConnection.systemBus()
    if not bus.isConnected():
        return None
    mgr = QDBusInterface('org.freedesktop.Accounts', '/org/freedesktop/Accounts', 'org.freedesktop.Accounts', bus)
    if not mgr.isValid():
        return None
    mgr.setTimeout(6000)
    reply = mgr.call('FindUserByName', name)
    args = reply.arguments()
    if not args:
        return None
    path = args[0].path() if hasattr(args[0], 'path') else str(args[0])
    user = QDBusInterface('org.freedesktop.Accounts', path, 'org.freedesktop.Accounts.User', bus)
    if not user.isValid():
        return None
    user.setTimeout(10000)
    return user


def _dbus_ok(reply):
    from PyQt5.QtDBus import QDBusMessage
    return reply.type() != QDBusMessage.ErrorMessage


def _write_face(png_path):
    home = Path.home()
    for name in ('.face', '.face.icon'):
        target = home/name
        try:
            if target.is_symlink():
                target.unlink()
            shutil.copyfile(png_path, target); os.chmod(target, 0o644)
        except OSError:
            pass


def set_own_avatar(png_path):
    """Your own picture: AccountsService (login screens) and ~/.face."""
    _write_face(png_path)
    name = pwd.getpwuid(os.getuid()).pw_name
    user = _accounts_user(name)
    if user is None:
        return True, 'Picture saved for this account. Install "accountsservice" so the login screen shows it too.'
    reply = user.call('SetIconFile', str(Path.home()/'.face'))
    if not _dbus_ok(reply):
        return False, reply.errorMessage() or 'The login screen picture could not be changed.'
    return True, 'Picture changed.'


def set_own_full_name(full_name):
    """Your own full name through AccountsService (no password needed)."""
    reason = check_full_name(full_name)
    if reason:
        return False, reason
    name = pwd.getpwuid(os.getuid()).pw_name
    user = _accounts_user(name)
    if user is None:
        return run_helper({'action': 'full_name', 'name': name, 'full_name': full_name})
    reply = user.call('SetRealName', full_name)
    if not _dbus_ok(reply):
        # Without permission (some AccountsService setups) ask an administrator.
        return run_helper({'action': 'full_name', 'name': name, 'full_name': full_name})
    return True, 'Name changed.'


# ------------------------------------------------------------------ own password
_PROMPTS = (('current', 'old'), ('(current)', 'old'), ('retype', 'new'), ('again', 'new'), ('new', 'new'))


def change_own_password(old, new, timeout=25):
    """Change your own password with passwd(1) (PAM checks it, so the rules
    of this computer apply). Returns (ok, message)."""
    import pty
    if '\n' in old or '\n' in new:
        return False, 'A password cannot contain a line break.'
    passwd = shutil.which('passwd')
    if not passwd:
        return False, 'passwd is not installed.'
    pid, fd = pty.fork()
    if pid == 0:
        os.environ.update(LC_ALL='C', LANG='C', LANGUAGE='C')
        try:
            os.execv(passwd, [passwd])
        finally:
            os._exit(127)
    out = ''; sent_new = 0; sent_old = 0; consumed = 0
    deadline = time.time() + timeout
    try:
        while time.time() < deadline:
            r, _w, _x = select.select([fd], [], [], 0.3)
            if fd in r:
                try:
                    chunk = os.read(fd, 1024).decode('utf-8', 'replace')
                except OSError:
                    break
                if not chunk:
                    break
                out += chunk
                # Only text after the last answer can be a new question.
                pending = out[consumed:].lower().rstrip()
                if pending.endswith(':'):
                    line = pending.splitlines()[-1] if pending.splitlines() else pending
                    for key, kind in _PROMPTS:
                        if key in line:
                            if kind == 'old':
                                if sent_old >= 1:
                                    raise RuntimeError('wrong')
                                os.write(fd, (old + '\n').encode()); sent_old += 1
                            else:
                                if sent_new >= 2:
                                    raise RuntimeError('rejected')
                                os.write(fd, (new + '\n').encode()); sent_new += 1
                            consumed = len(out)
                            break
            else:
                done, status = os.waitpid(pid, os.WNOHANG)
                if done:
                    break
    except RuntimeError:
        pass
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
    status = 0
    for _i in range(30):
        try:
            done, status = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            done = pid
        if done:
            break
        time.sleep(0.1)
    else:
        # passwd still waits for an answer: stop it.
        try:
            os.kill(pid, 15); _d, status = os.waitpid(pid, 0)
        except (OSError, ChildProcessError):
            pass
    text = out.lower()
    if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0 and 'success' in text:
        return True, 'Password changed.'
    for line in out.splitlines():
        low = line.lower()
        if 'bad password' in low:
            return False, line.strip()          # the rules of this computer (pwquality)
        if 'manipulation' in low or 'authentication' in low:
            return False, 'The current password is not right.'
        if 'unchanged' in low or 'do not match' in low:
            return False, line.strip()
    return False, 'The password was not changed (wrong current password, or the new one was not accepted).'
