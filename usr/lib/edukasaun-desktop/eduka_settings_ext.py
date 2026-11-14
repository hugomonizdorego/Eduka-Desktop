# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Pages of Eduka-Settings added in 0.11 RC2 (users, fonts, date and time,
LightDM, Eduka-Quick, the settings overview and the pages taken over from a
full desktop's system settings).

The pages are methods of the mixin ExtPages, which the Settings window of
/usr/bin/eduka-settings inherits. The small building blocks of the window
(Page, form rows, hints) live in eduka-settings and are handed over in UI
before the window is made, so the look stays the same everywhere.
"""
import os, re, json, shutil, subprocess, threading
from pathlib import Path
from types import SimpleNamespace

from PyQt5.QtWidgets import (QAbstractItemView, QAbstractSpinBox, QCheckBox, QComboBox, QDialog, QSpinBox,
                             QDateTimeEdit, QDialogButtonBox, QDoubleSpinBox, QFileDialog, QFontDialog, QFrame, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMenu, QMessageBox,
                             QPushButton, QRadioButton, QSlider, QToolButton, QVBoxLayout, QSizePolicy,
                             QColorDialog, QTreeWidget, QTreeWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QSize, QTimer, QRectF, QDateTime, QLocale
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QColor, QFont, QImage, QImageReader

from eduka_common import (_, get_icon, theme_accent, safe_popen, CACHE_DIR, MULTI_COLORS)

# Filled in by eduka-settings: Page, form, hint_label.
UI = SimpleNamespace(Page=None, form=None, hint_label=None)

EMOJI_DIR = Path('/usr/share/edukasaun-desktop/emoji')


def round_pixmap(source, size):
    """A round picture (path or QImage) of size x size pixels."""
    img = QImage()
    if isinstance(source, QImage):
        img = source
    elif source and os.path.isfile(str(source)):
        reader = QImageReader(str(source)); reader.setAutoTransform(True); img = reader.read()
    out = QPixmap(size, size); out.fill(Qt.transparent)
    if img.isNull():
        return out
    side = min(img.width(), img.height())
    img = img.copy((img.width() - side) // 2, (img.height() - side) // 2, side, side)
    img = img.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    p = QPainter(out); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
    path = QPainterPath(); path.addEllipse(QRectF(0, 0, size, size)); p.setClipPath(path)
    p.drawImage(0, 0, img); p.end()
    return out


def user_picture(user, size):
    """The account picture, or a circle with the initials."""
    import eduka_accounts as ea
    if user.get('avatar'):
        pix = round_pixmap(user['avatar'], size)
        if not pix.toImage().isNull():
            return pix
    color = MULTI_COLORS[sum(map(ord, user.get('name', 'x'))) % len(MULTI_COLORS)]
    return round_pixmap(ea.initials_avatar(user.get('full_name', ''), user.get('name', ''), color), size)


# The overview of Eduka-Settings (RC2), like the system settings of a full
# desktop: Eduka pages by their key, other tools ('@...') by the first of
# their commands that is installed. Tools that are missing are not shown.
SETTINGS_SECTIONS = [
    ('Appearance', [
        ('appearance', 'Themes', 'preferences-desktop-theme', 'theme style dark light colors accent'),
        ('wallpaper', 'Backgrounds', 'preferences-desktop-wallpaper', 'wallpaper picture background'),
        ('fonts', 'Font Selection', 'preferences-desktop-font', 'fonts letters text size scaling hinting'),
        ('effects', 'Effects', 'applications-graphics', 'effects animation compositor transparency'),
        ('desktopicons', 'Desktop', 'user-desktop', 'desktop icons home trash computer'),
    ]),
    ('Eduka', [
        ('desktop', 'Eduka-Desktop', 'start-here', 'menu start applications tiles'),
        ('quick', 'Eduka-Quick', '', 'pie quick launcher round hotkey'),
        ('panel', 'Eduka-Panel', 'preferences-desktop', 'panel taskbar start button'),
        ('clock', 'Clock', 'preferences-system-time', 'clock weather action center'),
        ('notifications', 'Notifications', 'preferences-system-notifications', 'notifications messages do not disturb'),
    ]),
    ('Preferences', [
        ('accessibility', 'Accessibility', 'preferences-desktop-accessibility', 'vision contrast large text pointer'),
        ('users', 'Account details', 'user-info', 'account picture avatar name password'),
        ('datetime', 'Date & Time', 'preferences-system-time', 'date time zone clock ntp sync'),
        ('general', 'Languages', 'preferences-desktop-locale', 'language tetun indonesia portugues startup'),
        ('@input', 'Input Method', 'fcitx', 'input method ime ibus fcitx'),
        ('parental', 'Parental Control', 'preferences-system-parental-controls', 'parental time limit children break'),
        ('@startup', 'Startup Applications', 'preferences-system-session', 'startup autostart session'),
        ('@defaults', 'Preferred Applications', 'preferences-desktop-default-applications', 'default applications file associations browser'),
        ('privacy', 'Privacy', 'preferences-system-privacy', 'privacy recent files history thumbnails trash'),
        ('screenreader', 'Screen Reader', 'orca', 'orca screen reader voice speech'),
        ('@screensaver', 'Screensaver', 'preferences-desktop-screensaver', 'screensaver lock idle'),
        ('@windows', 'Windows', 'preferences-system-windows', 'windows window manager openbox xfwm4 borders'),
    ]),
    ('Hardware', [
        ('@bluetooth', 'Bluetooth', 'bluetooth', 'bluetooth wireless devices'),
        ('@disks', 'Disks', 'drive-harddisk', 'disks drives partitions usb'),
        ('@display', 'Display', 'preferences-desktop-display', 'display monitor screen resolution projector'),
        ('keyboard', 'Keyboard', 'input-keyboard', 'keyboard layout shortcuts'),
        ('mouse', 'Mouse and Touchpad', 'input-mouse', 'mouse touchpad pointer speed gestures'),
        ('touchscreen', 'Touch Screen', 'input-tablet', 'touch screen tablet on-screen keyboard'),
        ('@network', 'Network', 'preferences-system-network', 'network wifi wired vpn internet'),
        ('@power', 'Power Management', 'preferences-system-power-management', 'power battery suspend sleep'),
        ('@printers', 'Printers', 'printer', 'printers printing scanner'),
        ('@sound', 'Sound', 'preferences-desktop-sound', 'sound volume speakers microphone'),
        ('@sysinfo', 'System Information', 'computer', 'system information about version memory'),
    ]),
    ('Administration', [
        ('fingerprint', 'Fingerprints', 'fingerprint', 'fingerprint login reader'),
        ('@firewall', 'Firewall', 'gufw', 'firewall security ports'),
        ('login', 'Login Window', 'system-users', 'login screen sddm autologin'),
        ('lightdm', 'LightDM', 'system-users', 'lightdm greeter slick login'),
        ('@software', 'Software Sources', 'software-properties', 'software sources repositories apt updates'),
        ('maintenance', 'System Maintenance', 'applications-system', 'maintenance repair reset'),
        ('users', 'Users and Groups', 'system-users', 'users accounts administrator groups'),
    ]),
]
TOOLS = {
    '@input': (['fcitx5-configtool', 'im-config', 'ibus-setup'], False),
    '@startup': (['lxqt-config-session'], False),
    '@defaults': (['lxqt-config-file-associations'], False),
    '@screensaver': (['xscreensaver-settings', 'xscreensaver-demo', 'lxqt-config-powermanagement'], False),
    '@windows': (['obconf-qt', 'xfwm4-settings'], False),
    '@bluetooth': (['blueman-manager'], False),
    '@disks': (['gnome-disks', 'partitionmanager', 'gparted'], False),
    '@display': (['lxqt-config-monitor', 'arandr'], False),
    '@network': (['nm-connection-editor'], False),
    '@power': (['lxqt-config-powermanagement', 'xfce4-power-manager-settings'], False),
    '@printers': (['system-config-printer'], False),
    '@sound': (['pavucontrol-qt', 'pavucontrol'], False),
    '@sysinfo': (['eduka-about'], False),
    '@firewall': (['gufw'], False),
    '@software': (['software-properties-qt', 'software-properties-gtk', 'synaptic-pkexec'], False),
}


def tool_command(key):
    cmds, _x = TOOLS.get(key, ([], False))
    return next((c for c in cmds if shutil.which(c)), None)


def quick_icon(size=48, accent=None):
    """The Eduka-Quick icon (hicolor eduka-quick.svg; drawn when missing)."""
    svg = '/usr/share/icons/hicolor/scalable/apps/eduka-quick.svg'
    if os.path.exists(svg):
        return QIcon(svg)
    import math
    accent = QColor(accent or theme_accent() or '#3fa684')
    pix = QPixmap(size, size); pix.fill(Qt.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.Antialiasing)
    c = size / 2; r = size * 0.44
    p.setPen(Qt.NoPen); p.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 60)); p.drawEllipse(QRectF(c - r, c - r, 2 * r, 2 * r))
    path = QPainterPath(); path.moveTo(c, c); path.arcTo(QRectF(c - r, c - r, 2 * r, 2 * r), 22.5, 45); path.closeSubpath()
    p.setBrush(accent); p.drawPath(path)
    for i in range(8):
        a = math.radians(-90 + 45 * i); d = r * 0.66
        p.setBrush(QColor('#ffffff') if i == 1 else accent.darker(115))
        p.drawEllipse(QRectF(c + math.cos(a) * d - size * 0.06, c + math.sin(a) * d - size * 0.06, size * 0.12, size * 0.12))
    p.setBrush(QColor('#ffffff')); p.drawEllipse(QRectF(c - size * 0.13, c - size * 0.13, size * 0.26, size * 0.26))
    p.end()
    return QIcon(pix)


class AppChooser(QDialog):
    """Choose an installed program (for an Eduka-Quick slice)."""
    def __init__(self, parent, apps):
        super().__init__(parent)
        self.setWindowTitle(_('Add a program')); self.setModal(True); self.resize(420, 520)
        v = QVBoxLayout(self); v.setContentsMargins(16, 14, 16, 12); v.setSpacing(8)
        self.search = QLineEdit(); self.search.setPlaceholderText(_('Search programs')); self.search.setClearButtonEnabled(True)
        self.search.setAccessibleName(_('Search programs'))
        self.list = QListWidget(); self.list.setIconSize(QSize(28, 28)); self.list.setAccessibleName(_('Programs'))
        v.addWidget(self.search); v.addWidget(self.list, 1)
        for app in sorted(apps, key=lambda a: a.get('name', '').casefold()):
            it = QListWidgetItem(get_icon(app.get('icon')), app.get('name', '')); it.setData(Qt.UserRole, app.get('desktop_id'))
            it.setToolTip(app.get('comment') or app.get('desktop_id', '')); self.list.addItem(it)
        self.search.textChanged.connect(self.filter)
        self.list.itemDoubleClicked.connect(lambda *_a: self.accept())
        box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); box.accepted.connect(self.accept); box.rejected.connect(self.reject)
        v.addWidget(box)
        if self.list.count(): self.list.setCurrentRow(0)

    def filter(self, text):
        q = text.strip().casefold(); first = None
        for i in range(self.list.count()):
            it = self.list.item(i); hide = bool(q) and q not in it.text().casefold() and q not in str(it.data(Qt.UserRole)).casefold()
            it.setHidden(hide)
            if not hide and first is None: first = i
        if first is not None: self.list.setCurrentRow(first)

    def chosen(self):
        it = self.list.currentItem()
        return it.data(Qt.UserRole) if it and not it.isHidden() else None


def run_in_background(owner, func, done=None):
    """func() in a thread, done(result, error) back in the window's thread
    (Qt widgets are only touched there)."""
    box = {}
    def work():
        try: box['result'] = func()
        except Exception as exc: box['error'] = exc
    thread = threading.Thread(target=work, daemon=True); thread.start()
    timer = QTimer(owner); timer.setInterval(80)
    def check():
        if thread.is_alive(): return
        timer.stop(); timer.deleteLater()
        if done: done(box.get('result'), box.get('error'))
    timer.timeout.connect(check); timer.start()
    return thread


# ---------------------------------------------------------------- dialogs
class AvatarPicker(QDialog):
    """Choose an account picture: your own photo, the initials in a color,
    or one of the friendly pictures (Noto Emoji)."""
    def __init__(self, parent, user):
        super().__init__(parent)
        self.setWindowTitle(_('Account picture')); self.setModal(True)
        self.user = user; self.result_image = None
        v = QVBoxLayout(self); v.setContentsMargins(20, 18, 20, 14); v.setSpacing(10)
        v.addWidget(QLabel(_('Choose a picture for {n}.').replace('{n}', user.get('full_name') or user.get('name'))))
        grid = QGridLayout(); grid.setSpacing(8); v.addLayout(grid)
        import eduka_accounts as ea
        options = []
        for color in MULTI_COLORS[:6]:
            options.append(('initials', color, ea.initials_avatar(user.get('full_name', ''), user.get('name', ''), color)))
        for path in sorted(EMOJI_DIR.glob('emoji_u*.png')):
            img = QImage(str(path))
            if not img.isNull():
                canvas = QImage(256, 256, QImage.Format_ARGB32_Premultiplied); canvas.fill(QColor('#eaf6f1'))
                p = QPainter(canvas); p.setRenderHint(QPainter.SmoothPixmapTransform)
                p.drawImage(QRectF(40, 40, 176, 176), img); p.end()
                options.append(('emoji', str(path), canvas))
        for i, (_kind, _value, img) in enumerate(options):
            b = QToolButton(); b.setIcon(QIcon(round_pixmap(img, 64))); b.setIconSize(QSize(56, 56)); b.setFixedSize(66, 66)
            b.setAutoRaise(True); b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, im=img: self.choose(im))
            grid.addWidget(b, i // 6, i % 6)
        row = QHBoxLayout()
        own = QPushButton(get_icon('document-open', 'folder'), ' ' + _('Choose a photo…')); own.clicked.connect(self.choose_file)
        row.addWidget(own); row.addStretch(1)
        cancel = QPushButton(_('Cancel')); cancel.clicked.connect(self.reject); row.addWidget(cancel)
        v.addLayout(row)

    def choose(self, image):
        self.result_image = image; self.accept()

    def choose_file(self):
        f, _x = QFileDialog.getOpenFileName(self, _('Account picture'), str(Path.home()/'Pictures'),
                                            _('Pictures') + ' (*.png *.jpg *.jpeg *.webp *.bmp)')
        if f:
            reader = QImageReader(f); reader.setAutoTransform(True); img = reader.read()
            if img.isNull():
                QMessageBox.warning(self, _('Account picture'), _('This file is not a picture.')); return
            self.choose(img)


class PasswordDialog(QDialog):
    """New password (and the current one for your own account). With a
    fingerprint set up, a forgotten current password can be replaced: the
    finger confirms it is you (0.11 RC3)."""
    def __init__(self, parent, user, own, fingerprint=False, forgot=False):
        super().__init__(parent)
        self.setWindowTitle(_('Change password')); self.setModal(True); self.setMinimumWidth(380)
        self.own = own
        v = QVBoxLayout(self); v.setContentsMargins(20, 18, 20, 14); v.setSpacing(8)
        v.addWidget(QLabel(_('Password of {n}').replace('{n}', user.get('full_name') or user.get('name'))))
        self.old = QLineEdit(); self.old.setEchoMode(QLineEdit.Password); self.old.setPlaceholderText(_('Current password'))
        self.new = QLineEdit(); self.new.setEchoMode(QLineEdit.Password); self.new.setPlaceholderText(_('New password'))
        self.again = QLineEdit(); self.again.setEchoMode(QLineEdit.Password); self.again.setPlaceholderText(_('New password again'))
        self.forgot = QCheckBox(_('I forgot my current password: confirm with my fingerprint'))
        self.forgot.setVisible(bool(own and fingerprint)); self.forgot.setChecked(bool(own and fingerprint and forgot))
        if own:
            v.addWidget(self.forgot); v.addWidget(self.old)
        self.forgot.toggled.connect(lambda on: (self.old.setVisible(not on), self.update_hint()))
        self.old.setVisible(not self.forgot.isChecked())
        v.addWidget(self.new); v.addWidget(self.again)
        self.show_pw = QCheckBox(_('Show the passwords')); v.addWidget(self.show_pw)
        self.show_pw.toggled.connect(lambda on: [w.setEchoMode(QLineEdit.Normal if on else QLineEdit.Password) for w in (self.old, self.new, self.again)])
        self.hint = QLabel(''); self.hint.setObjectName('fieldHint'); self.hint.setWordWrap(True); v.addWidget(self.hint)
        box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.button(QDialogButtonBox.Ok).setText(_('Change password')); box.button(QDialogButtonBox.Cancel).setText(_('Cancel'))
        box.accepted.connect(self.check); box.rejected.connect(self.reject); v.addWidget(box)
        self.ok_button = box.button(QDialogButtonBox.Ok)
        for w in (self.old, self.new, self.again):
            w.textChanged.connect(self.update_hint)
        self.update_hint()

    def update_hint(self):
        import eduka_accounts as ea
        new, again = self.new.text(), self.again.text()
        if not new:
            text = ''
        elif again and new != again:
            text = _('The two new passwords are not the same.')
        else:
            text = _(ea.password_hint(new)) if ea.password_hint(new) else _('Good password.')
        self.hint.setText(text)
        self.ok_button.setEnabled(bool(new) and new == again and (not self.own or self.forgot.isChecked() or bool(self.old.text())))

    def check(self):
        if self.new.text() == self.again.text() and self.new.text():
            self.accept()


class AddUserDialog(QDialog):
    """A new account: name, login name, password, type and picture."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(_('Add account')); self.setModal(True); self.setMinimumWidth(420)
        self.image = None; self._name_edited = False
        v = QVBoxLayout(self); v.setContentsMargins(20, 18, 20, 14); v.setSpacing(8)
        top = QHBoxLayout(); top.setSpacing(12)
        self.pic = QToolButton(); self.pic.setFixedSize(76, 76); self.pic.setIconSize(QSize(68, 68)); self.pic.setAutoRaise(True)
        self.pic.setToolTip(_('Choose a picture')); self.pic.setCursor(Qt.PointingHandCursor); self.pic.clicked.connect(self.pick)
        top.addWidget(self.pic)
        names = QVBoxLayout(); names.setSpacing(6)
        self.full = QLineEdit(); self.full.setPlaceholderText(_('Full name (for example Maria da Costa)')); self.full.setMaxLength(64)
        self.login = QLineEdit(); self.login.setPlaceholderText(_('Login name (for example maria)')); self.login.setMaxLength(32)
        names.addWidget(self.full); names.addWidget(self.login); top.addLayout(names, 1); v.addLayout(top)
        self.type = QComboBox(); self.type.addItem(_('Standard account (for pupils and most people)'), False)
        self.type.addItem(_('Administrator (can install programs and change the computer)'), True)
        v.addWidget(self.type)
        self.pw = QLineEdit(); self.pw.setEchoMode(QLineEdit.Password); self.pw.setPlaceholderText(_('Password'))
        self.pw2 = QLineEdit(); self.pw2.setEchoMode(QLineEdit.Password); self.pw2.setPlaceholderText(_('Password again'))
        v.addWidget(self.pw); v.addWidget(self.pw2)
        self.visible = QCheckBox(_('Show this account on the login screen')); self.visible.setChecked(True); v.addWidget(self.visible)
        self.hint = QLabel(''); self.hint.setObjectName('fieldHint'); self.hint.setWordWrap(True); v.addWidget(self.hint)
        box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.button(QDialogButtonBox.Ok).setText(_('Add account')); box.button(QDialogButtonBox.Cancel).setText(_('Cancel'))
        box.accepted.connect(self.accept); box.rejected.connect(self.reject); v.addWidget(box)
        self.ok_button = box.button(QDialogButtonBox.Ok)
        self.full.textChanged.connect(self.full_changed); self.login.textEdited.connect(lambda *_a: setattr(self, '_name_edited', True))
        for w in (self.full, self.login, self.pw, self.pw2):
            w.textChanged.connect(self.check)
        self.update_picture(); self.check()

    def full_changed(self, text):
        import eduka_accounts as ea
        if not self._name_edited:
            self.login.blockSignals(True); self.login.setText(ea.suggest_name(text)); self.login.blockSignals(False)
        self.update_picture()

    def update_picture(self):
        import eduka_accounts as ea
        img = self.image or ea.initials_avatar(self.full.text(), self.login.text(), theme_accent())
        self.pic.setIcon(QIcon(round_pixmap(img, 68)))

    def pick(self):
        d = AvatarPicker(self, {'full_name': self.full.text(), 'name': self.login.text()})
        if d.exec_() and d.result_image is not None:
            self.image = d.result_image; self.update_picture()

    def check(self, *_a):
        import eduka_accounts as ea
        name = self.login.text().strip(); reason = ''
        if self.full.text() and ea.check_full_name(self.full.text()):
            reason = ea.check_full_name(self.full.text())
        elif name and ea.check_name(name):
            reason = ea.check_name(name)
        elif self.pw.text() and self.pw2.text() and self.pw.text() != self.pw2.text():
            reason = 'The two passwords are not the same.'
        elif self.pw.text():
            reason = ea.password_hint(self.pw.text())
        self.hint.setText(_(reason) if reason else '')
        ok = bool(name) and not ea.check_name(name) and not ea.check_full_name(self.full.text()) \
            and bool(self.pw.text()) and self.pw.text() == self.pw2.text()
        self.ok_button.setEnabled(ok)

    def request(self):
        return {'action': 'create', 'name': self.login.text().strip(), 'full_name': self.full.text().strip(),
                'password': self.pw.text(), 'admin': bool(self.type.currentData()), 'hidden': not self.visible.isChecked()}


# ---------------------------------------------------------------- pages
LIGHTDM_HELPER = '/usr/lib/edukasaun-desktop/eduka-lightdm-apply'
LIGHTDM_STATE = Path('/etc/edukasaun-desktop/lightdm.json')
LIGHTDM_SEAT = Path('/etc/lightdm/lightdm.conf.d/50-eduka-settings.conf')
LIGHTDM_AUTOLOGIN = Path('/etc/lightdm/lightdm.conf.d/50-eduka-autologin.conf')
LIGHTDM_GREETERS = (('slick-greeter', 'Slick greeter', 'Big account names over the background, with the logo in the corner.'),
                    ('lightdm-gtk-greeter', 'GTK greeter', 'A login card in the middle, like the SDDM login screen.'))
LOGIN_STYLES = (('follow', 'Follow Eduka-Desktop theme'), ('pastel', 'Pastel'), ('light', 'Light'), ('dark', 'Dark'), ('glass', 'Glass'))
LOGIN_ACCENTS = {'light': '#00a879', 'dark': '#26a69a', 'glass': '#1e9bd7', 'pastel': '#3fa684'}


def current_display_manager():
    try:
        path = Path('/etc/X11/default-display-manager').read_text(encoding='utf-8').strip()
        return os.path.basename(path)
    except Exception:
        for name in ('sddm', 'lightdm'):
            if Path('/etc/systemd/system/display-manager.service').resolve().name == name + '.service':
                return name
    return ''


def ini_values(path):
    out = {}
    try:
        for line in Path(path).read_text(encoding='utf-8', errors='ignore').splitlines():
            m = re.match(r'\s*([A-Za-z0-9_-]+)\s*=\s*(.*?)\s*$', line)
            if m: out[m.group(1)] = m.group(2)
    except Exception:
        pass
    return out


FONT_ROLES = (('default', 'Default font', 'Menus, buttons and windows of Eduka, LXQt and GTK programs.'),
              ('desktop', 'Desktop font', 'The names under the desktop icons.'),
              ('document', 'Document font', 'Programs that show documents and web pages.'),
              ('monospace', 'Monospace font', 'Terminal, code and tables; every letter has the same width.'),
              ('title', 'Window title font', 'The title bar of windows (Openbox and xfwm4).'))


class MemoryBar(QFrame):
    """Used memory as a wide rounded bar: green, orange when low, red when
    almost full."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.used = 0.0; self.total = 1.0; self.state = 'ok'
        self.setMinimumHeight(30); self.setAccessibleName(_('Memory in use'))

    def set_values(self, used, total, state):
        self.used, self.total, self.state = used, max(1.0, total), state
        self.setAccessibleDescription(f'{int(used * 100 / self.total)} %'); self.update()

    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 4, -1, -4)
        p.setPen(Qt.NoPen); p.setBrush(QColor('#dfeee9')); p.drawRoundedRect(r, r.height() / 2, r.height() / 2)
        frac = max(0.0, min(1.0, self.used / self.total))
        color = {'ok': '#3fa684', 'low': '#f08c2e', 'critical': '#e5484d'}.get(self.state, '#3fa684')
        if frac:
            p.setBrush(QColor(color)); p.drawRoundedRect(QRectF(r.x(), r.y(), max(r.height(), r.width() * frac), r.height()), r.height() / 2, r.height() / 2)
        p.setPen(QColor('#ffffff' if frac > 0.12 else '#1f3d36')); f = p.font(); f.setBold(True); p.setFont(f)
        p.drawText(r.adjusted(12, 0, -12, 0), Qt.AlignVCenter | Qt.AlignLeft, f'{int(frac * 100)} %')


class ExtPages:
    """New pages of Eduka-Settings (0.11 RC2)."""

    # ------------------------------------------------------------ memory (0.11 RC3)
    def page_memory(self):
        import eduka_memory as em
        self._em = em
        p = UI.Page('Memory', 'How much memory this computer has free, and what keeps it running smoothly when it '
                              'is almost full.')
        self.mem_bar = MemoryBar(); p.v.addWidget(self.mem_bar)
        self.mem_text = UI.hint_label(''); p.v.addWidget(self.mem_text)
        t = p.new_card('Programs using the most memory')
        self.mem_list = QListWidget(); self.mem_list.setObjectName('layoutList'); self.mem_list.setFixedHeight(190)
        t.addWidget(self.mem_list)
        self.mem_list.currentItemChanged.connect(lambda cur, _prev: self.mem_close.setEnabled(bool(cur) and not cur.data(Qt.UserRole + 2)))
        trow = QHBoxLayout(); trow.setSpacing(8)
        self.mem_close = QPushButton(get_icon('process-stop', 'window-close'), ' ' + _('Close program'))
        self.mem_close.clicked.connect(self.memory_close_program)
        self.mem_free = QPushButton(get_icon('edit-clear', 'view-refresh'), ' ' + _('Free memory of Eduka-Desktop'))
        self.mem_free.clicked.connect(self.memory_free_now)
        trow.addWidget(self.mem_close); trow.addStretch(1); trow.addWidget(self.mem_free); t.addLayout(trow)
        t.addWidget(UI.hint_label('All windows and helpers of a program are counted together. Programs of the desktop '
                                  'itself cannot be closed here. Save your work before closing a program.'))
        o = p.new_card('Keep the computer smooth')
        prefs = em.read_prefs()
        self.mem_saver = QCheckBox('Memory saver: Eduka-Desktop and Eduka-Panel give memory back when they are not used')
        self.mem_warn = QCheckBox('Warn me when the memory is almost full')
        self.mem_saver.setChecked(prefs['saver']); self.mem_warn.setChecked(prefs['warn'])
        for w in (self.mem_saver, self.mem_warn):
            o.addWidget(w); w.toggled.connect(self.memory_prefs_changed)
        self.mem_zram = QCheckBox('Compressed memory (zram): about half again as much memory, without a disk')
        self.mem_oom = QCheckBox('earlyoom: when the memory is full, close the biggest program instead of freezing')
        o.addWidget(self.mem_zram); o.addWidget(self.mem_oom)
        self.mem_zram.clicked.connect(lambda on: self.memory_helper('--zram', 'on' if on else 'off'))
        self.mem_oom.clicked.connect(lambda on: self.memory_helper('--earlyoom', 'on' if on else 'off'))
        self.mem_tools_hint = UI.hint_label(''); o.addWidget(self.mem_tools_hint)
        irow = QHBoxLayout(); irow.addStretch(1)
        self.mem_install = QPushButton(get_icon('system-software-install', 'list-add'), ' ' + _('Install zram-tools and earlyoom…'))
        self.mem_install.clicked.connect(self.memory_install); irow.addWidget(self.mem_install); o.addLayout(irow)
        self.mem_timer = QTimer(self); self.mem_timer.setInterval(2500); self.mem_timer.timeout.connect(self.memory_refresh)
        self.mem_timer.start()
        self.memory_refresh(full=True)
        return p.finish()

    def memory_refresh(self, full=False):
        em = self._em
        if not full and not self.mem_bar.isVisible():
            return
        s = em.summary(); state = em.pressure(s)
        self.mem_bar.set_values(s['used'], s['total'], state)
        gb = lambda mb: f'{mb / 1024:.1f} GB' if mb >= 1024 else f'{int(mb)} MB'
        text = _('{used} of {total} in use, {free} free.').replace('{used}', gb(s['used'])).replace('{total}', gb(s['total'])).replace('{free}', gb(s['available']))
        if s['swap_total']:
            text += ' ' + (_('Compressed memory: {used} of {total} used.') if s['zram'] else _('Swap: {used} of {total} used.')).replace('{used}', gb(s['swap_used'])).replace('{total}', gb(s['swap_total']))
        text += ' ' + {'ok': _('Memory is fine.'), 'low': _('Memory is getting low.'), 'critical': _('Memory is almost full: close programs you do not use.')}[state]
        self.mem_text.setText(text)
        current = self.mem_list.currentItem().data(Qt.UserRole + 1) if self.mem_list.currentItem() else None
        self.mem_list.clear()
        for g in em.top_programs(10):
            it = QListWidgetItem(get_icon(g['name'], 'application-x-executable'), f"{g['name']}  —  {gb(g['mb'])}" + ('  ' + _('(desktop)') if g['protected'] else ''))
            it.setData(Qt.UserRole, g['pids']); it.setData(Qt.UserRole + 1, g['name']); it.setData(Qt.UserRole + 2, g['protected'])
            self.mem_list.addItem(it)
            if g['name'] == current:
                self.mem_list.setCurrentItem(it)
        item = self.mem_list.currentItem()
        self.mem_close.setEnabled(bool(item) and not item.data(Qt.UserRole + 2))
        if full:
            zi, ei = em.zram_installed(), em.earlyoom_installed()
            admin = shutil.which('pkexec') is not None
            for box, inst, on in ((self.mem_zram, zi, em.zram_active()), (self.mem_oom, ei, em.earlyoom_active())):
                box.blockSignals(True); box.setChecked(on); box.setEnabled(inst and admin); box.blockSignals(False)
            missing = [n for n, ok in (('zram-tools', zi), ('earlyoom', ei)) if not ok]
            self.mem_install.setVisible(bool(missing))
            self.mem_tools_hint.setText(_('Not installed: {list}.').replace('{list}', ', '.join(missing)) if missing else
                                        _('These two change the whole computer and ask for an administrator password.'))

    def memory_prefs_changed(self, *_a):
        self._em.save_prefs({'saver': self.mem_saver.isChecked(), 'warn': self.mem_warn.isChecked()})
        self.show_status(_('Saved.'))

    def memory_close_program(self):
        item = self.mem_list.currentItem()
        if item is None or item.data(Qt.UserRole + 2):
            return
        name = item.data(Qt.UserRole + 1)
        if QMessageBox.question(self, _('Close program'), _('Close {name}? Work that is not saved is lost.').replace('{name}', name),
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        n = self._em.close_program(item.data(Qt.UserRole) or [])
        self.show_status(_('{name} was asked to close.').replace('{name}', name) if n else _('Nothing was closed.'), error=not n)
        QTimer.singleShot(1500, self.memory_refresh)

    def memory_free_now(self):
        from eduka_common import send_menu_command
        import socket
        before = self._em.summary()['available']
        send_menu_command('trim')
        try:
            from eduka_common import RUNTIME_DIR
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sk:
                sk.settimeout(1.0); sk.connect(str(RUNTIME_DIR/'panel.sock')); sk.sendall(b'trim\n')
        except OSError:
            pass
        freed = self._em.trim(qt=True)
        def report():
            gained = max(0, self._em.summary()['available'] - before) + freed
            self.show_status(_('Eduka-Desktop gave back {n} MB of memory.').replace('{n}', str(int(gained))))
            self.memory_refresh()
        QTimer.singleShot(1200, report)

    def memory_helper(self, flag, value):
        def done(result, error):
            ok, msg = result if result and not error else (False, str(error))
            self.memory_refresh(full=True)
            self.show_status(_(msg) if ok else _('Not changed: ') + _(msg), error=not ok)
        run_in_background(self, lambda: self._em.run_helper(flag, value), done)

    def memory_install(self):
        from eduka_common import terminal_command
        if not shutil.which('apt-get'):
            self.show_status(_('Install zram-tools and earlyoom with the package manager of this system.'), error=True); return
        try:
            proc = subprocess.Popen(terminal_command(self._em.install_command()), stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, start_new_session=True)
        except Exception as e:
            self.show_status(_('Could not open a terminal: ') + str(e), error=True); return
        timer = QTimer(self); timer.setInterval(1500)
        def check():
            if proc.poll() is None: return
            timer.stop(); timer.deleteLater(); self.memory_refresh(full=True)
        timer.timeout.connect(check); timer.start()

    # ------------------------------------------------------------ display (0.11 RC3)
    @staticmethod
    def scale_preview(scale, accent='#3fa684', w=92, h=58):
        """A window and a panel drawn at this scale (on 100 % they fill the
        same share of the picture as on a normal screen)."""
        pix = QPixmap(w, h); pix.fill(Qt.transparent)
        p = QPainter(pix); p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QColor('#9fb3ad')); p.setBrush(QColor('#eef6f2')); p.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), 7, 7)
        k = scale
        bar = 6 * k
        p.setPen(Qt.NoPen); p.setBrush(QColor('#ffffff')); p.drawRoundedRect(QRectF(4, h - 4 - bar, w - 8, bar), bar / 2, bar / 2)
        p.setBrush(QColor(accent)); p.drawEllipse(QRectF(6, h - 4 - bar + 1, bar - 2, bar - 2))
        ww, wh = 46 * k, 28 * k
        win = QRectF(8, 6, min(ww, w - 14), min(wh, h - 14 - bar))
        p.setBrush(QColor('#ffffff')); p.setPen(QColor('#b8c9c3')); p.drawRoundedRect(win, 3 * k, 3 * k)
        p.setPen(Qt.NoPen); p.setBrush(QColor(accent)); p.drawRoundedRect(QRectF(win.x(), win.y(), win.width(), 5 * k), 2, 2)
        p.setBrush(QColor('#9fb3ad'))
        y = win.y() + 8 * k
        while y + 2 * k < win.bottom() - 2:
            p.drawRoundedRect(QRectF(win.x() + 3 * k, y, win.width() * 0.6, 2 * k), 1, 1); y += 5 * k
        p.end()
        return pix

    def page_display(self):
        import eduka_device as edev
        self._edev = edev
        p = UI.Page('Display', 'The kind of computer Eduka-Desktop found, and the size of everything on the screen.')
        c = p.v
        try:
            prof = edev.profile()
        except Exception:
            prof = {'kind': 'desktop', 'kind_name': 'Desktop computer', 'icon': 'computer', 'vendor': '', 'model': '',
                    'batteries': [], 'keyboards': [], 'touchpads': [], 'touchscreens': [], 'screens': [], 'recommended_scale': 1.0, 'vm': ''}
        self._display_profile = prof
        row = QHBoxLayout(); row.setSpacing(14)
        pic = QLabel(); pic.setPixmap(get_icon(prof['icon'], 'computer').pixmap(56, 56)); row.addWidget(pic, 0, Qt.AlignTop)
        info = QVBoxLayout(); info.setSpacing(3)
        title = QLabel(_(prof['kind_name'])); title.setObjectName('sectionTitle'); info.addWidget(title)
        model = ' '.join(x for x in (prof.get('vendor', ''), prof.get('model', '')) if x and x.lower() not in ('to be filled by o.e.m.', 'default string'))
        facts = []
        if prof.get('vm'):
            facts.append(_('Runs in a virtual machine ({name}).').replace('{name}', prof['vm']))
        if model:
            facts.append(model)
        facts += [_(k.split(': ', 1)[0]) + (': ' + k.split(': ', 1)[1] if ': ' in k else '') for k in edev.keyboard_text(prof)]
        if prof['touchpads']:
            facts.append(_('Touchpad: ') + prof['touchpads'][0])
        if prof['touchscreens']:
            facts.append(_('Touch screen: ') + prof['touchscreens'][0])
        if prof['batteries']:
            facts.append(_('Battery: ') + ', '.join(prof['batteries']))
        for scr in prof['screens']:
            inches, dpi = edev.screen_facts(scr)
            line = f"{scr['name']}: {scr['width']} × {scr['height']}"
            if inches:
                line += ' · ' + _('{n} inches').replace('{n}', f'{inches:g}') + ' · ' + _('{n} dots per inch').replace('{n}', str(int(dpi)))
            if scr['built_in']:
                line += ' · ' + _('built in')
            facts.append(line)
        for fact in facts or [_('No details found.')]:
            lab = QLabel(fact); lab.setWordWrap(True); lab.setTextInteractionFlags(Qt.TextSelectableByMouse); info.addWidget(lab)
        row.addLayout(info, 1); c.addLayout(row)
        c.addWidget(UI.hint_label('Eduka-Desktop uses this to set Num Lock, the touchpad key and the recommended scale.'))

        sc = p.new_card('Scale')
        sc.addWidget(UI.hint_label('Makes text, icons, panels and windows bigger or smaller together. 100 % is the normal size.'))
        cur = edev.read_display() or {'scale': 1.0, 'auto': False}
        rec = prof.get('recommended_scale', 1.0)
        from PyQt5.QtWidgets import QButtonGroup
        grid = QGridLayout(); grid.setSpacing(10); self.scale_cards = {}; group = QButtonGroup(self)
        accent = theme_accent() if callable(theme_accent) else '#3fa684'
        for i, value in enumerate(edev.SCALES):
            text = f'{int(value * 100)} %' + ('\n' + _('Recommended') if value == rec else '')
            card = QToolButton(); card.setObjectName('posCard'); card.setCheckable(True); card.setText(text)
            card.setIcon(QIcon(self.scale_preview(value, accent))); card.setIconSize(QSize(92, 58))
            card.setToolButtonStyle(Qt.ToolButtonTextUnderIcon); card.setCursor(Qt.PointingHandCursor)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); card.setMinimumHeight(112)
            card.setAccessibleName(_('Scale {n} percent').replace('{n}', str(int(value * 100))))
            card.setChecked(abs(value - cur['scale']) < 0.01)
            card.clicked.connect(lambda _c=False, v=value: self.set_display_scale(v))
            group.addButton(card); grid.addWidget(card, i // 3, i % 3); self.scale_cards[value] = card
        sc.addLayout(grid)
        self.scale_state = UI.hint_label(''); sc.addWidget(self.scale_state)
        actions = QHBoxLayout(); actions.addStretch(1)
        out = QPushButton(get_icon('system-log-out'), ' ' + _('Log out now')); out.clicked.connect(self.logout_for_scale)
        actions.addWidget(out); sc.addLayout(actions)
        self.update_scale_state(cur['scale'], applied=True)
        return p.finish()

    def update_scale_state(self, value, applied=False):
        running = os.environ.get('QT_SCALE_FACTOR', '1') or '1'
        try:
            running = float(running)
        except ValueError:
            running = 1.0
        rec = self._display_profile.get('recommended_scale', 1.0)
        text = _('Recommended for this screen: {n} %.').replace('{n}', str(int(rec * 100)))
        if abs(running - value) > 0.01:
            text += ' ' + _('{n} % is used after you log out and in again.').replace('{n}', str(int(value * 100)))
        self.scale_state.setText(text)

    def set_display_scale(self, value):
        try:
            self._edev.apply_scale(value)
            if value >= 1.5:
                # A bigger pointer with a big scale (the Accessibility choice wins when it is bigger).
                import eduka_a11y as ea
                if ea.pointer_size() < round(24 * value):
                    ea.set_pointer_size(min(64, round(24 * value)))
        except Exception as e:
            self.show_status(_('Not changed: ') + str(e), error=True); return
        self.update_scale_state(value)
        self.show_status(_('Scale {n} % saved; log out to use it.').replace('{n}', str(int(value * 100))))

    def logout_for_scale(self):
        if QMessageBox.question(self, _('Log out'), _('Log out now? Save your work in other programs first.'),
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            safe_popen(['eduka-session-action', '--now', 'logout'])

    # ------------------------------------------------------------ shortcuts (0.11 RC3)
    SHORTCUT_STATES = {'on': 'On', 'custom': 'Your own key', 'off': 'Off', 'taken': 'Used by: {what}',
                       'wm': 'Used by the window manager', 'missing': 'No program for it on this computer'}

    def page_shortcuts(self):
        import eduka_shortcuts as es
        self._es = es
        p = UI.Page('Shortcuts', 'The shortcuts of LXQt and the Windows shortcuts people know, in one list. A key that '
                                 'LXQt, you or the window manager already use is never given a second job.')
        top = QHBoxLayout(); top.setSpacing(10)
        self.sc_enabled = QCheckBox('Use the Windows shortcuts and the sound and media keys')
        self.sc_enabled.setAccessibleDescription(_('Super+E, Super+D, Super+L, Super+arrows, Super+Shift+S and more'))
        top.addWidget(self.sc_enabled, 1)
        self.sc_apply = QPushButton(get_icon('view-refresh'), ' ' + _('Apply now'))
        self.sc_apply.setToolTip(_('Restarts the LXQt shortcut service so the keys work at once'))
        top.addWidget(self.sc_apply)
        p.v.addLayout(top)
        self.sc_state = UI.hint_label(''); p.v.addWidget(self.sc_state)
        self.sc_tree = QTreeWidget(); self.sc_tree.setObjectName('shortcutTree')
        self.sc_tree.setColumnCount(3); self.sc_tree.setHeaderLabels([_('Keys'), _('What it does'), _('State')])
        self.sc_tree.setRootIsDecorated(False); self.sc_tree.setUniformRowHeights(True); self.sc_tree.setAlternatingRowColors(True)
        self.sc_tree.setSelectionMode(QAbstractItemView.NoSelection); self.sc_tree.setFocusPolicy(Qt.StrongFocus)
        self.sc_tree.setMinimumHeight(380)
        hdr = self.sc_tree.header(); hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch); hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        p.v.addWidget(self.sc_tree, 1)
        p.v.addWidget(UI.hint_label('Untick a line to free its key. Keys you changed with LXQt\'s shortcut editor '
                                    '(lxqt-config-globalkeyshortcuts) are kept. Super alone opens Eduka-Desktop.'))
        self.sc_enabled.toggled.connect(self.shortcuts_changed)
        self.sc_apply.clicked.connect(lambda: self.apply_shortcuts(force=True))
        self.sc_tree.itemChanged.connect(self.shortcut_item_changed)
        self.load_shortcuts()
        return p.finish()

    def load_shortcuts(self):
        es = self._es
        prefs = es.read_prefs()
        self._sc_loading = True
        self.sc_enabled.blockSignals(True); self.sc_enabled.setChecked(prefs['enabled']); self.sc_enabled.blockSignals(False)
        try:
            rows = es.plan(prefs=prefs)
        except Exception:
            rows = []
        self.sc_tree.clear()
        bold = QFont(); bold.setBold(True)
        active = 0
        for g in es.GROUPS:
            head = QTreeWidgetItem([_(g), '', '']); head.setFont(0, bold); head.setFlags(Qt.ItemIsEnabled)
            self.sc_tree.addTopLevelItem(head); head.setFirstColumnSpanned(True)
            for keys, label, group in es.BUILT_IN:
                if group == g:
                    it = QTreeWidgetItem(['   ' + _(keys), _(label), _('Built in')]); it.setFlags(Qt.ItemIsEnabled)
                    self.sc_tree.addTopLevelItem(it)
            for action, keys, label, group, state, detail in rows:
                if group != g:
                    continue
                text = self.SHORTCUT_STATES.get(state, state)
                it = QTreeWidgetItem([' ' + ', '.join(_(es.human(k)) for k in keys), _(label),
                                      _(text).replace('{what}', detail or '?')])
                it.setData(0, Qt.UserRole, action)
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
                it.setCheckState(0, Qt.Unchecked if state == 'off' else Qt.Checked)
                if state in ('taken', 'wm', 'missing'):
                    for col in range(3):
                        it.setForeground(col, QColor('#8a9a95'))
                if state in ('on', 'custom'):
                    active += 1
                self.sc_tree.addTopLevelItem(it)
        wm = es.running_wm()
        self.sc_state.setText(_('{n} Eduka shortcuts are active.').replace('{n}', str(active)) + ' ' +
                              (_('Window manager: {wm}.').replace('{wm}', wm) if wm else ''))
        self.sc_tree.setEnabled(prefs['enabled'])
        self._sc_loading = False

    def shortcut_item_changed(self, item, column):
        if getattr(self, '_sc_loading', False) or column != 0 or item.data(0, Qt.UserRole) is None:
            return
        prefs = self._es.read_prefs()
        action = item.data(0, Qt.UserRole)
        off = set(prefs['off'])
        (off.discard if item.checkState(0) == Qt.Checked else off.add)(action)
        prefs['off'] = sorted(off)
        self._es.save_prefs(prefs)
        self.apply_shortcuts()

    def shortcuts_changed(self, on):
        prefs = self._es.read_prefs(); prefs['enabled'] = bool(on)
        self._es.save_prefs(prefs)
        self.apply_shortcuts()

    def apply_shortcuts(self, force=False):
        es = self._es
        self.sc_apply.setEnabled(False)
        def done(result, error):
            self.sc_apply.setEnabled(True)
            self.load_shortcuts()
            if error:
                self.show_status(_('Shortcuts not changed: ') + str(error), error=True)
            else:
                self.show_status(_('Shortcuts saved; the keys work now.') if es.daemon_running()
                                 else _('Shortcuts saved; they work from the next login.'))
        run_in_background(self, lambda: es.apply_now(), done)

    # ------------------------------------------------------------ date and time
    def page_datetime(self):
        import eduka_datetime as ed
        self._ed = ed
        p = UI.Page('Date & Time', 'The clock and the time zone of this computer. With network time the clock is '
                                   'always right; Sync now also finds the time zone of the place you are.')
        top = QHBoxLayout(); top.setSpacing(14)
        clock = QVBoxLayout(); clock.setSpacing(0)
        self.dt_time = QLabel(''); self.dt_time.setObjectName('bigClock'); self.dt_time.setAccessibleName('Time now')
        self.dt_time.setStyleSheet('font-size:30px;font-weight:800;')
        self.dt_date = QLabel(''); self.dt_date.setObjectName('cardTitle')
        self.dt_zone = QLabel(''); self.dt_zone.setObjectName('fieldHint')
        for w in (self.dt_time, self.dt_date, self.dt_zone): clock.addWidget(w)
        top.addLayout(clock, 1)
        self.dt_sync = QPushButton(get_icon('emblem-synchronizing', ['view-refresh', 'preferences-system-time']), ' ' + _('Sync now'))
        self.dt_sync.setObjectName('primaryButton'); self.dt_sync.setMinimumHeight(38); self.dt_sync.clicked.connect(self.sync_time_now)
        self.dt_sync.setToolTip(_('Set the clock from network time and follow the time zone of this place'))
        top.addWidget(self.dt_sync, 0, Qt.AlignTop)
        p.v.addLayout(top)
        f = UI.form()
        self.dt_ntp = QCheckBox('Set the clock automatically from the internet (network time)')
        self.dt_ntp.clicked.connect(self.change_ntp)
        self.dt_ntp_state = UI.hint_label('')
        box = QVBoxLayout(); box.setSpacing(3); box.addWidget(self.dt_ntp); box.addWidget(self.dt_ntp_state)
        f.addRow('Network time', box)
        zone = QHBoxLayout(); zone.setSpacing(8)
        self.dt_region = QComboBox(); self.dt_region.setAccessibleName('Region'); self.dt_region.setMinimumWidth(130)
        self.dt_city = QComboBox(); self.dt_city.setAccessibleName('City'); self.dt_city.setMinimumWidth(220)
        self.dt_city.setMaxVisibleItems(18)
        zone.addWidget(self.dt_region); zone.addWidget(self.dt_city, 1)
        self.dt_detect = QPushButton(get_icon('find-location', ['mark-location', 'applications-internet']), ' ' + _('Find'))
        self.dt_detect.setToolTip(_('Find the time zone of this place on the internet')); self.dt_detect.clicked.connect(self.detect_time_zone)
        zone.addWidget(self.dt_detect)
        self.dt_auto_zone = QCheckBox('Follow the time zone of the place when the clock is synced')
        self.dt_auto_zone.clicked.connect(lambda on: self._ed.save_config({'auto_timezone': bool(on)}))
        zbox = QVBoxLayout(); zbox.setSpacing(6); zbox.addLayout(zone); zbox.addWidget(self.dt_auto_zone)
        f.addRow('Time zone', zbox)
        p.v.addLayout(f)

        c = p.new_card('Set the clock by hand')
        g = UI.form()
        manual = QHBoxLayout(); manual.setSpacing(8)
        self.dt_edit = QDateTimeEdit(); self.dt_edit.setCalendarPopup(True); self.dt_edit.setDisplayFormat('yyyy-MM-dd  HH:mm')
        self.dt_edit.setAccessibleName('Date and time'); self.dt_edit.setMinimumWidth(190)
        self.dt_set = QPushButton(_('Set the clock')); self.dt_set.clicked.connect(self.set_clock_by_hand)
        manual.addWidget(self.dt_edit); manual.addWidget(self.dt_set); manual.addStretch(1)
        g.addRow('Date and time', manual)
        g.addRow('', UI.hint_label('Switch network time off first. Setting the clock asks for an administrator password.'))
        self.dt_rtc = QCheckBox('The hardware clock keeps local time (Windows is also on this computer)')
        self.dt_rtc.clicked.connect(self.change_local_rtc)
        g.addRow('Hardware clock', self.dt_rtc)
        c.addLayout(g)
        row = QHBoxLayout()
        row.addWidget(UI.hint_label('The look of the clock (24 hours, seconds, LED face, weather) is in Eduka-Panel → Clock.'), 1)
        look = QPushButton(get_icon('preferences-system-time'), ' ' + _('Clock settings')); look.clicked.connect(lambda: self.open_page('clock'))
        row.addWidget(look)
        p.outer.addLayout(row)
        self._dt_status = {}; self._dt_busy = False
        self.dt_region.currentIndexChanged.connect(self.fill_cities)
        self.dt_city.activated.connect(self.choose_time_zone)
        self._dt_timer = QTimer(self); self._dt_timer.timeout.connect(self.tick_datetime); self._dt_timer.start(1000)
        self.tick_datetime()
        QTimer.singleShot(0, self.load_datetime)
        return p.finish()

    def tick_datetime(self):
        if not self.dt_time.isVisible() and self.dt_time.text():
            return
        now = QDateTime.currentDateTime(); loc = QLocale()
        self.dt_time.setText(now.toString('HH:mm:ss'))
        self.dt_date.setText(loc.toString(now.date(), QLocale.LongFormat))
        zone = self._dt_status.get('timezone') or self._ed.local_zone()
        self.dt_zone.setText(zone.replace('_', ' ') + '  ·  ' + self._ed.zone_offset_text(zone))

    def load_datetime(self):
        def done(st, error):
            if error or not st: st = {'timezone': self._ed.local_zone(), 'available': False}
            self._dt_status = st
            zone = st.get('timezone') or 'UTC'
            regions = sorted({z.split('/', 1)[0] for z in self._ed.zones() if '/' in z}) + ['UTC']
            self.dt_region.blockSignals(True); self.dt_region.clear()
            for r in regions: self.dt_region.addItem(_(r), r)
            region = zone.split('/', 1)[0] if '/' in zone and zone in self._ed.zones() else 'UTC'
            self.dt_region.setCurrentIndex(max(0, self.dt_region.findData(region)))
            self.dt_region.blockSignals(False)
            self.fill_cities(select=zone)
            self.dt_auto_zone.setChecked(bool(self._ed.read_config().get('auto_timezone', True)))
            self.update_datetime_state()
        run_in_background(self, self._ed.status, done)

    def update_datetime_state(self):
        st = self._dt_status
        self.dt_ntp.setChecked(bool(st.get('ntp')))
        self.dt_ntp.setEnabled(bool(st.get('can_ntp')) and not self._dt_busy)
        if not st.get('available'):
            text = _('The clock service (systemd-timedated) is not running here, so the clock cannot be changed.')
        elif not st.get('can_ntp'):
            text = _('No network time service is installed; install systemd-timesyncd. Sync now then reads the time from a web server.')
        elif st.get('ntp') and st.get('synced'):
            text = _('The clock follows network time and is synchronized.')
        elif st.get('ntp'):
            text = _('The clock follows network time; it is not synchronized yet (no internet?).')
        else:
            text = _('Network time is off: the clock only keeps its own time.')
        self.dt_ntp_state.setText(text)
        manual = bool(st.get('available')) and not st.get('ntp') and not self._dt_busy
        self.dt_edit.setEnabled(manual); self.dt_set.setEnabled(manual)
        if not self.dt_edit.hasFocus(): self.dt_edit.setDateTime(QDateTime.currentDateTime())
        self.dt_rtc.setChecked(bool(st.get('local_rtc'))); self.dt_rtc.setEnabled(bool(st.get('available')) and not self._dt_busy)
        for w in (self.dt_sync, self.dt_detect, self.dt_city, self.dt_region):
            w.setEnabled(bool(st.get('available')) and not self._dt_busy)

    def fill_cities(self, *_a, select=None):
        region = self.dt_region.currentData() or 'UTC'
        self.dt_city.blockSignals(True); self.dt_city.clear()
        names = ['UTC'] if region == 'UTC' else [z for z in self._ed.zones() if z.startswith(region + '/')]
        for z in names:
            label = z.split('/', 1)[1].replace('_', ' ').replace('/', ' / ') if '/' in z else z
            self.dt_city.addItem(f'{label}   ({self._ed.zone_offset_text(z)})', z)
        current = select or self._dt_status.get('timezone')
        if current in ('Etc/UTC', 'Etc/UCT', 'UCT', 'Universal', 'Zulu', 'Etc/Zulu', 'Etc/Universal', 'GMT', 'Etc/GMT'):
            current = 'UTC'
        idx = self.dt_city.findData(current)
        self.dt_city.setCurrentIndex(idx if idx >= 0 else 0)
        self.dt_city.blockSignals(False)

    def _dt_run(self, work, message, after=None):
        self._dt_busy = True; self.update_datetime_state()
        def done(result, error):
            self._dt_busy = False
            ok, text = (result if isinstance(result, tuple) else (bool(result), '')) if not error else (False, str(error))
            if after: after(ok, text)
            if message:
                self.show_status(_(message) if ok else (_(text) if text else _('The clock could not be changed.')), error=not ok)
            self.load_datetime()
        run_in_background(self, work, done)

    def choose_time_zone(self, *_a):
        zone = self.dt_city.currentData()
        if zone and zone != self._dt_status.get('timezone'):
            self._dt_run(lambda: self._ed.set_zone(zone), 'Time zone changed.')

    def change_ntp(self, on):
        self._dt_run(lambda: self._ed.set_ntp(bool(on)), 'Network time switched on.' if on else 'Network time switched off.')

    def change_local_rtc(self, on):
        self._dt_run(lambda: self._ed.set_local_rtc(bool(on)), 'Hardware clock mode changed.')

    def set_clock_by_hand(self):
        stamp = self.dt_edit.dateTime().toSecsSinceEpoch()
        self._dt_run(lambda: self._ed.set_time(stamp), 'The clock is set.')

    def detect_time_zone(self):
        def work():
            zone = self._ed.detect_zone()
            if not zone:
                return False, 'The time zone could not be found on the internet.'
            if zone == self._ed.local_zone():
                return True, ''
            return self._ed.set_zone(zone)
        self._dt_run(work, 'The time zone follows this place.')

    def sync_time_now(self):
        self.dt_sync.setText(' ' + _('Syncing…'))
        def work():
            res = self._ed.sync_now(follow_zone=self.dt_auto_zone.isChecked())
            return res['ok'], res['message']
        def after(ok, text):
            self.dt_sync.setText(' ' + _('Sync now'))
            if ok and text: QTimer.singleShot(0, lambda: self.show_status(_(text)))
        self._dt_run(work, None, after)

    # ------------------------------------------------------------ overview
    def page_overview(self):
        from PyQt5.QtWidgets import QListView
        p = UI.Page('All Settings', 'Every setting of Edukasaun Desktop in one place. Type to search, or choose a tile.')
        self.ov_search = QLineEdit(); self.ov_search.setPlaceholderText(_('Search settings')); self.ov_search.setClearButtonEnabled(True)
        self.ov_search.setAccessibleName(_('Search settings')); self.ov_search.setMinimumHeight(36)
        self.ov_search.textChanged.connect(self.filter_overview)
        p.v.addWidget(self.ov_search)
        self.ov_sections = []
        for title, entries in SETTINGS_SECTIONS:
            items = []
            for key, name, icon, words in entries:
                if key.startswith('@'):
                    if not tool_command(key): continue
                elif key not in self.page_nav and key not in ('overview',):
                    # pages are made after the overview: check by name later
                    pass
                items.append((key, name, icon, words))
            if not items: continue
            head = QLabel(_(title)); head.setObjectName('cardTitle')
            lst = QListWidget(); lst.setObjectName('overviewList'); lst.setViewMode(QListView.ListMode); lst.setFlow(QListView.LeftToRight)
            lst.setWrapping(True); lst.setResizeMode(QListView.Adjust); lst.setGridSize(QSize(196, 46)); lst.setIconSize(QSize(28, 28))
            lst.setUniformItemSizes(True); lst.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); lst.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            lst.setFrameShape(QFrame.NoFrame); lst.setAccessibleName(_(title)); lst.setMouseTracking(True)
            lst.setSelectionMode(QAbstractItemView.SingleSelection); lst.setCursor(Qt.PointingHandCursor)
            for key, name, icon, words in items:
                ic = quick_icon(28) if key == 'quick' else (self.sub_icon(key, icon) if hasattr(self, 'sub_icon') else get_icon(icon))
                if not icon and key != 'quick': ic = get_icon('preferences-system')
                it = QListWidgetItem(ic, _(name)); it.setData(Qt.UserRole, key)
                it.setData(Qt.UserRole + 1, ' '.join([name, _(name), words, _(title), title]).casefold())
                tool = tool_command(key) if key.startswith('@') else ''
                it.setToolTip(_('Opens {tool}').replace('{tool}', tool) if tool else _(name))
                it.setSizeHint(QSize(190, 42)); lst.addItem(it)
            lst.itemActivated.connect(self.open_overview_item); lst.itemClicked.connect(self.open_overview_item)
            p.v.addWidget(head); p.v.addWidget(lst)
            self.ov_sections.append((head, lst))
        p.v.addWidget(UI.hint_label('Tiles with a tool of LXQt or Debian open that tool; it is shown only when it is installed.'))
        self._ov_timer = QTimer(self); self._ov_timer.setSingleShot(True); self._ov_timer.setInterval(0)
        self._ov_timer.timeout.connect(self.size_overview)
        p.installEventFilter(self); self._ov_page = p
        QTimer.singleShot(0, self.size_overview)
        return p.finish()

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        if obj is getattr(self, '_ov_page', None) and event.type() in (QEvent.Resize, QEvent.Show):
            self._ov_timer.start()
        return super().eventFilter(obj, event)

    def size_overview(self):
        """Each section is as tall as its rows of tiles (no inner scrolling)."""
        import math
        for head, lst in getattr(self, 'ov_sections', []):
            shown = sum(1 for i in range(lst.count()) if not lst.item(i).isHidden())
            cols = max(1, (lst.viewport().width() or lst.width()) // lst.gridSize().width())
            rows = math.ceil(shown / cols) if shown else 0
            lst.setFixedHeight(rows * lst.gridSize().height() + (6 if rows else 0))
            head.setVisible(shown > 0); lst.setVisible(shown > 0)

    def filter_overview(self, text):
        q = text.strip().casefold()
        for _head, lst in self.ov_sections:
            for i in range(lst.count()):
                it = lst.item(i)
                it.setHidden(bool(q) and not all(w in it.data(Qt.UserRole + 1) for w in q.split()))
        self.size_overview()

    def open_overview_item(self, item):
        key = item.data(Qt.UserRole)
        if key.startswith('@'):
            cmd = tool_command(key)
            if cmd and safe_popen([cmd]):
                self.show_status(_('{tool} opened.').replace('{tool}', cmd))
            else:
                self.show_status(_('This tool is not installed.'), error=True)
        else:
            self.open_page(key)

    # ------------------------------------------------------------ privacy
    def page_privacy(self):
        p = UI.Page('Privacy', 'What this computer remembers about your work: recent files, small pictures of '
                               'files and the trash. Edukasaun sends nothing about you anywhere.')
        f = UI.form()
        self.priv_recent = self._own(QCheckBox('Remember the files I opened (recent files)'))
        self.priv_recent.clicked.connect(self.change_recent_files)
        clear = QPushButton(get_icon('edit-clear-history', ['edit-clear']), ' ' + _('Clear the list now')); clear.clicked.connect(lambda: self.clear_recent_files())
        box = QVBoxLayout(); box.setSpacing(6); box.addWidget(self.priv_recent)
        row = QHBoxLayout(); row.addWidget(clear); row.addStretch(1); box.addLayout(row)
        f.addRow('Recent files', box)
        thumbs = QPushButton(get_icon('edit-delete', ['user-trash']), ' ' + _('Delete the small pictures of files')); thumbs.clicked.connect(self.clear_thumbnails)
        row = QHBoxLayout(); row.addWidget(thumbs); row.addStretch(1); f.addRow('Thumbnails', row)
        f.addRow('', UI.hint_label('The file manager makes them again when needed.'))
        trash = QPushButton(get_icon('user-trash-full', ['user-trash']), ' ' + _('Empty the trash')); trash.clicked.connect(self.empty_trash)
        row = QHBoxLayout(); row.addWidget(trash); row.addStretch(1); f.addRow('Trash', row)
        weather = QPushButton(get_icon('weather-few-clouds', ['preferences-system-time']), ' ' + _('Weather and location…'))
        weather.clicked.connect(lambda: self.open_page('clock'))
        row = QHBoxLayout(); row.addWidget(weather); row.addStretch(1); f.addRow('Internet', row)
        f.addRow('', UI.hint_label('Only the weather (GeoJS, Open-Meteo) and Sync time use the internet; both can be switched off.'))
        p.v.addLayout(f)
        from eduka_common import _get_ini_value
        value = (_get_ini_value(Path.home()/'.config/gtk-3.0/settings.ini', 'Settings', 'gtk-recent-files-enabled') or 'true').lower()
        self.priv_recent.setChecked(value not in ('false', '0'))
        return p.finish()

    def change_recent_files(self, on):
        from eduka_common import _set_ini_value
        for gtk in ('gtk-3.0', 'gtk-4.0'):
            try: _set_ini_value(Path.home()/'.config'/gtk/'settings.ini', 'Settings', 'gtk-recent-files-enabled', 'true' if on else 'false')
            except Exception: pass
        if shutil.which('gsettings'):
            safe_popen(['gsettings', 'set', 'org.gnome.desktop.privacy', 'remember-recent-files', 'true' if on else 'false'])
        if not on: self.clear_recent_files(quiet=True)
        self.show_status(_('Recent files are remembered.') if on else _('Recent files are not remembered any more.'))

    def clear_recent_files(self, quiet=False):
        path = Path.home()/'.local/share/recently-used.xbel'
        try:
            if path.exists():
                path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<xbel version="1.0"\n      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"\n'
                                '      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info"\n></xbel>\n', encoding='utf-8')
            ok = True
        except Exception:
            ok = False
        if not quiet:
            self.show_status(_('The list of recent files is empty.') if ok else _('The list could not be cleared.'), error=not ok)

    def clear_thumbnails(self):
        folder = Path.home()/'.cache/thumbnails'
        try:
            if folder.is_dir() and not folder.is_symlink(): shutil.rmtree(folder)
            self.show_status(_('The small pictures of files were deleted.'))
        except Exception:
            self.show_status(_('The small pictures could not be deleted.'), error=True)

    def empty_trash(self):
        if QMessageBox.question(self, _('Empty the trash'), _('Delete everything in the trash for good?'),
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        ok = shutil.which('gio') is not None and subprocess.run(['gio', 'trash', '--empty'], capture_output=True, timeout=120).returncode == 0
        if not ok:
            base = Path.home()/'.local/share/Trash'
            try:
                for sub in ('files', 'info', 'expunged'):
                    d = base/sub
                    if d.is_dir() and not d.is_symlink(): shutil.rmtree(d)
                ok = True
            except Exception:
                ok = False
        self.show_status(_('The trash is empty.') if ok else _('The trash could not be emptied.'), error=not ok)

    # ------------------------------------------------------------ Eduka-Quick
    def page_quick(self):
        import eduka_quick as eq
        self._eq = eq
        self._quick = eq.read_config()
        p = UI.Page('Eduka-Quick', 'A round quick launcher: press the key, point in a direction and click. '
                                   'Choose the programs, actions and groups it shows.')
        top = QHBoxLayout(); top.setSpacing(16)
        self.quick_preview = QLabel(); self.quick_preview.setFixedSize(210, 210); self.quick_preview.setAlignment(Qt.AlignCenter)
        self.quick_preview.setAccessibleName(_('Preview of Eduka-Quick'))
        top.addWidget(self.quick_preview, 0, Qt.AlignTop)
        opts = QVBoxLayout(); opts.setSpacing(8)
        self.quick_on = self._own(QCheckBox('Use Eduka-Quick')); opts.addWidget(self.quick_on)
        self.quick_on.setStyleSheet('font-weight:800;font-size:15px;')
        self.quick_state = UI.hint_label(''); opts.addWidget(self.quick_state)
        grid = QGridLayout(); grid.setHorizontalSpacing(8); grid.setVerticalSpacing(6)
        def combo(name, items):
            c = self._own(QComboBox()); c.setAccessibleName(_(name))
            for key, label in items: c.addItem(_(label), key)
            return c
        self.quick_key = combo('Key for Eduka-Quick', eq.HOTKEYS)
        self.quick_pos = combo('Where Eduka-Quick opens', eq.POSITIONS)
        self.quick_look = combo('Look of Eduka-Quick', eq.LOOKS)
        self.quick_count = self._own(QSpinBox()); self.quick_count.setRange(eq.MIN_SLICES, eq.MAX_SLICES)
        self.quick_count.setAccessibleName(_('Number of slices')); self.quick_count.setSuffix(' ' + _('slices'))
        for r, (title, w) in enumerate((('Key:', self.quick_key), ('Opens:', self.quick_pos), ('Look:', self.quick_look),
                                         ('Size:', self.quick_count))):
            grid.addWidget(QLabel(_(title)), r, 0); grid.addWidget(w, r, 1)
        grid.setColumnStretch(2, 1); opts.addLayout(grid)
        self.quick_auto = self._own(QCheckBox('Fill free slices with the programs I use most')); opts.addWidget(self.quick_auto)
        self.quick_numbers = self._own(QCheckBox('Show numbers for the keyboard (1–9)')); opts.addWidget(self.quick_numbers)
        trow = QHBoxLayout()
        test = QPushButton(quick_icon(20), ' ' + _('Try it now')); test.clicked.connect(lambda: self._eq.send_menu_command('quick'))
        trow.addWidget(test); trow.addStretch(1); opts.addLayout(trow)
        opts.addStretch(1)
        top.addLayout(opts, 1)
        p.v.addLayout(top)
        p.v.addWidget(UI.hint_label('Point at a slice and click. Hold the mouse button (or drag the clear center) to move '
                                    'Eduka-Quick anywhere; it opens there again. Keys: arrows, 1–9, Enter; Esc closes. '
                                    'Dots mark a group: it opens a smaller circle, Esc goes back. In Eduka-Desktop, '
                                    'right-click a program → Add to Eduka-Quick.'))
        c = p.new_card('Slices')
        body = QHBoxLayout(); body.setSpacing(12)
        self.quick_list = QListWidget(); self.quick_list.setIconSize(QSize(28, 28)); self.quick_list.setMinimumHeight(260)
        self.quick_list.setDragDropMode(QAbstractItemView.InternalMove); self.quick_list.setAccessibleName(_('Slices of Eduka-Quick'))
        self.quick_list.model().rowsMoved.connect(lambda *_a: self.quick_from_list())
        body.addWidget(self.quick_list, 1)
        side = QVBoxLayout(); side.setSpacing(6)
        add_app = QPushButton(get_icon('list-add'), ' ' + _('Program…')); add_app.clicked.connect(self.quick_add_app)
        add_action = QPushButton(get_icon('system-run', ['list-add']), ' ' + _('Action')); amenu = QMenu(add_action)
        for key, (name, icon, hint) in eq.ACTIONS.items():
            act = amenu.addAction(get_icon(icon), _(name)); act.setToolTip(_(hint))
            act.triggered.connect(lambda _c=False, k=key: self.quick_add({'type': 'action', 'action': k}))
        add_action.setMenu(amenu)
        add_group = QPushButton(get_icon('folder', ['list-add']), ' ' + _('Group')); gmenu = QMenu(add_group)
        for name, icon in eq.categories():
            act = gmenu.addAction(get_icon(icon), _(name))
            act.triggered.connect(lambda _c=False, n=name, i=icon: self.quick_add({'type': 'category', 'category': n, 'name': n, 'icon': i}))
        add_group.setMenu(gmenu)
        up = QPushButton(get_icon('go-up'), ' ' + _('Up')); up.clicked.connect(lambda: self.quick_move(-1))
        down = QPushButton(get_icon('go-down'), ' ' + _('Down')); down.clicked.connect(lambda: self.quick_move(1))
        rem = QPushButton(get_icon('list-remove'), ' ' + _('Remove')); rem.clicked.connect(self.quick_remove)
        reset = QPushButton(get_icon('edit-undo'), ' ' + _('Default slices')); reset.clicked.connect(self.quick_reset)
        for b in (add_app, add_action, add_group, up, down, rem): side.addWidget(b)
        side.addStretch(1); side.addWidget(reset)
        body.addLayout(side)
        c.addLayout(body)
        c.addWidget(UI.hint_label(_('At most {n} slices; programs that are not installed are skipped. Changes are used at once.').replace('{n}', str(eq.MAX_SLICES))
                                  + ' ' + _('Free slices show the programs you use most when that option is on.')))
        self.quick_on.setChecked(bool(self._quick.get('enabled', True)))
        self.quick_key.setCurrentIndex(max(0, self.quick_key.findData(self._quick.get('hotkey'))))
        self.quick_pos.setCurrentIndex(max(0, self.quick_pos.findData(self._quick.get('position', 'mouse'))))
        self.quick_look.setCurrentIndex(max(0, self.quick_look.findData(self._quick.get('look', 'glass'))))
        self.quick_count.setValue(int(self._quick.get('count', 8)))
        self.quick_auto.setChecked(bool(self._quick.get('auto_fill', True)))
        self.quick_numbers.setChecked(bool(self._quick.get('numbers', True)))
        self.quick_on.clicked.connect(lambda *_a: self.quick_save(hotkey=True))
        self.quick_key.activated.connect(lambda *_a: self.quick_save(hotkey=True))
        for w in (self.quick_pos, self.quick_look):
            w.activated.connect(lambda *_a: self.quick_save())
        self.quick_count.valueChanged.connect(lambda *_a: self.quick_save())
        self.quick_auto.clicked.connect(lambda *_a: self.quick_save())
        self.quick_numbers.clicked.connect(lambda *_a: self.quick_save())
        self.quick_show_state()
        self.quick_list.currentRowChanged.connect(lambda *_a: self.quick_update_preview())
        QTimer.singleShot(0, self.quick_fill)
        return p.finish()

    def quick_fill(self, select=0):
        eq = self._eq
        self.quick_list.blockSignals(True); self.quick_list.clear()
        for sl in self._quick['slices']:
            name, icon, ok = eq.describe_slice(sl)
            kind = {'app': _('program'), 'action': _('action'), 'category': _('group'), 'group': _('group')}.get(sl.get('type'), '')
            text = f'{name}  ·  {kind}' + ('' if ok else '  ' + _('(not installed)'))
            it = QListWidgetItem(get_icon(icon), text); it.setData(Qt.UserRole, json.dumps(sl))
            if not ok: it.setForeground(QColor('#8a8f8d'))
            self.quick_list.addItem(it)
        self.quick_list.blockSignals(False)
        if self.quick_list.count(): self.quick_list.setCurrentRow(max(0, min(select, self.quick_list.count() - 1)))
        self.quick_update_preview()

    def quick_show_state(self):
        on = self.quick_on.isChecked()
        for w in (self.quick_key, self.quick_pos, self.quick_look, self.quick_count, self.quick_auto, self.quick_numbers):
            w.setEnabled(on)
        self.quick_state.setText(_('On: {k} opens it.').replace('{k}', self.quick_key.currentText()) if on
                                 else _('Off: the key does nothing and Eduka-Quick never opens.'))

    def quick_update_preview(self):
        try:
            active = sum(1 for sl in self._quick['slices'][:max(0, self.quick_list.currentRow())] if self._eq.resolve(sl))
            shown = self._eq.effective_slices(self._quick)
            self.quick_preview.setPixmap(self._eq.preview_pixmap(shown, 210, active=min(active, max(0, len(shown) - 1))))
        except Exception:
            self.quick_preview.setPixmap(quick_icon(160).pixmap(160, 160))

    def quick_from_list(self):
        self._quick['slices'] = [json.loads(self.quick_list.item(i).data(Qt.UserRole)) for i in range(self.quick_list.count())]
        self.quick_save()

    def quick_save(self, hotkey=False):
        q = self._quick
        q.update(enabled=self.quick_on.isChecked(), hotkey=self.quick_key.currentData(),
                 position=self.quick_pos.currentData(), look=self.quick_look.currentData(),
                 count=self.quick_count.value(), auto_fill=self.quick_auto.isChecked(),
                 numbers=self.quick_numbers.isChecked())
        self._quick = self._eq.save_config(q)
        self.quick_update_preview(); self.quick_show_state()
        if hotkey:
            ok = self._eq.apply_hotkey(q['enabled'], q['hotkey'])
            key = self.quick_key.currentText()
            if not ok:
                self.show_status(_('The key could not be set; it is used after the next login.'), error=True)
            else:
                self.show_status(_('Eduka-Quick opens with {k}.').replace('{k}', key) if q['enabled'] else _('Eduka-Quick is off.'))

    def quick_add(self, sl):
        if len(self._quick['slices']) >= self._eq.MAX_SLICES:
            self.show_status(_('Eduka-Quick has the most slices already; remove one first.'), error=True); return
        row = self.quick_list.currentRow() + 1 if self.quick_list.currentRow() >= 0 else len(self._quick['slices'])
        self._quick['slices'].insert(row, sl); self.quick_save(); self.quick_fill(select=row)

    def quick_add_app(self):
        dlg = AppChooser(self, list(self._eq.apps_by_id().values()))
        if dlg.exec_() == QDialog.Accepted and dlg.chosen():
            self.quick_add({'type': 'app', 'ids': [dlg.chosen()]})

    def quick_move(self, step):
        row = self.quick_list.currentRow(); new = row + step
        sl = self._quick['slices']
        if 0 <= row < len(sl) and 0 <= new < len(sl):
            sl[row], sl[new] = sl[new], sl[row]; self.quick_save(); self.quick_fill(select=new)

    def quick_remove(self):
        row = self.quick_list.currentRow()
        if 0 <= row < len(self._quick['slices']):
            del self._quick['slices'][row]; self.quick_save(); self.quick_fill(select=row)

    def quick_reset(self):
        self._quick['slices'] = self._eq.default_slices(); self.quick_save(); self.quick_fill()

    # ------------------------------------------------------------ accessibility
    @staticmethod
    def _own(*widgets):
        """Controls that apply themselves: not part of the window's Apply."""
        for w in widgets:
            w.setProperty('eduka_no_live', True)
        return widgets[0] if len(widgets) == 1 else widgets

    def page_a11y_vision(self):
        import eduka_a11y as ea
        self._a11y = ea
        p = UI.Page('Vision', 'See the screen better: strong contrast, bigger letters and mouse pointer, less movement, '
                              'a magnifier and an on-screen keyboard.')
        f = UI.form()
        self.visual_access = QCheckBox('Strong contrast in Eduka-Desktop, Eduka-Panel and menus')
        f.addRow('High contrast', self.visual_access)
        f.addRow('', UI.hint_label('Opaque surfaces, clear borders and larger text in the Eduka programs.'))
        self.a11y_large = self._own(QCheckBox('Large text (125 %) in every program'))
        self.a11y_large.clicked.connect(self.change_large_text)
        f.addRow('Large text', self.a11y_large)
        f.addRow('', UI.hint_label('The exact size is the text scaling factor in Appearance → Fonts.'))
        self.a11y_pointer = self._own(QComboBox()); self.a11y_pointer.setAccessibleName('Mouse pointer size')
        self.a11y_pointer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed); self.a11y_pointer.setMinimumWidth(200)
        for size, name in ea.POINTER_SIZES:
            self.a11y_pointer.addItem(f'{_(name)} ({size} px)', size)
        self.a11y_pointer.activated.connect(self.change_pointer_size)
        prow = QHBoxLayout(); prow.addWidget(self.a11y_pointer); prow.addStretch(1)
        f.addRow('Mouse pointer', prow)
        self.a11y_motion = self._own(QCheckBox('Reduce motion: no animations or effects'))
        self.a11y_motion.clicked.connect(self.change_reduce_motion)
        f.addRow('Motion', self.a11y_motion)
        p.v.addLayout(f)
        tools = p.new_card('Tools')
        row = QHBoxLayout(); row.setSpacing(8)
        mag = QPushButton(get_icon('zoom-in', ['system-search']), ' ' + _('Magnifier'))
        mag.clicked.connect(lambda: ea.open_magnifier() or self.show_status(_('Install the magnifier first: sudo apt install magnus'), error=True))
        osk = QPushButton(get_icon('input-keyboard', ['preferences-desktop-keyboard']), ' ' + _('On-screen keyboard'))
        osk.clicked.connect(lambda: ea.open_onscreen_keyboard() or self.show_status(_('Install the on-screen keyboard first: sudo apt install onboard'), error=True))
        for b in (mag, osk): row.addWidget(b)
        row.addStretch(1); tools.addLayout(row)
        have = [n for n in ('magnus', 'kmag', 'onboard') if shutil.which(n)]
        tools.addWidget(UI.hint_label(_('The magnifier follows the mouse (magnus). The on-screen keyboard (Onboard) can '
                                        'start at every login: Mouse & Touch → Touch Screen.') +
                                      ('' if have else ' ' + _('Neither is installed yet.'))))
        QTimer.singleShot(0, self.load_a11y_vision)
        return p.finish()

    def load_a11y_vision(self):
        ea = self._a11y
        self.a11y_large.setChecked(ea.large_text_on())
        size = ea.pointer_size()
        idx = self.a11y_pointer.findData(size)
        if idx < 0:
            idx = min(range(self.a11y_pointer.count()), key=lambda i: abs(self.a11y_pointer.itemData(i) - size))
        self.a11y_pointer.setCurrentIndex(idx)
        effects = getattr(self, 'effects_on', None)
        self.a11y_motion.setChecked(effects is not None and not effects.isChecked())

    def change_large_text(self, on):
        ea = self._a11y
        def done(ok, error):
            self.show_status(_('Large text is on; programs that are open use it when they start again.') if on else _('Large text is off.'),
                             error=bool(error) or not ok)
        run_in_background(self, lambda: ea.set_large_text(bool(on)), done)

    def change_pointer_size(self, *_a):
        size = self.a11y_pointer.currentData()
        ok = self._a11y.set_pointer_size(size)
        self.show_status(_('Mouse pointer size: {n} px. New windows use it at once.').replace('{n}', str(size)) if ok
                         else _('The mouse pointer could not be changed (no cursor theme found).'), error=not ok)

    def change_reduce_motion(self, on):
        effects = getattr(self, 'effects_on', None)
        if effects is not None:
            effects.setChecked(not on)      # saved by the window with the Effects page
        self.show_status(_('Animations and effects are off.') if on else _('Animations and effects can be used again (Appearance → Effects).'))

    def page_a11y_hearing(self):
        import eduka_a11y as ea
        self._a11y = ea
        p = UI.Page('Hearing', 'See what you cannot hear and hear everything with one ear: sound and network status as '
                               'text, mono sound and longer notifications.')
        f = UI.form()
        self.hearing_access = QCheckBox('Show network, sound and alert status as text on Eduka-Panel')
        f.addRow('Status as text', self.hearing_access)
        self.a11y_mono = self._own(QCheckBox('Mono sound: both ears and both speakers play everything'))
        self.a11y_mono.clicked.connect(self.change_mono_sound)
        f.addRow('Mono sound', self.a11y_mono)
        f.addRow('', UI.hint_label('Good with one earphone, one speaker or hearing on one side. It stays on after logging in again.'))
        row = QHBoxLayout(); row.setSpacing(8)
        snd = QPushButton(get_icon('audio-volume-high', ['preferences-desktop-sound']), ' ' + _('Sound settings…'))
        snd.clicked.connect(lambda: ea.open_sound_settings() or self.show_status(_('Install pavucontrol-qt for the sound settings.'), error=True))
        notes = QPushButton(get_icon('preferences-system-notifications'), ' ' + _('Notifications…'))
        notes.clicked.connect(lambda: self.open_page('notifications'))
        row.addWidget(snd); row.addWidget(notes); row.addStretch(1)
        f.addRow('More', row)
        p.v.addLayout(f)
        self.a11y_mono.setChecked(ea.mono_sound_on())
        return p.finish()

    def change_mono_sound(self, on):
        ea = self._a11y
        def done(result, error):
            ok, text = result if result and not error else (False, str(error))
            if not ok: self.a11y_mono.setChecked(ea.mono_sound_on())
            self.show_status(_(text), error=not ok)
        run_in_background(self, lambda: ea.apply_mono_sound(bool(on)), done)

    def page_a11y_speech(self):
        import eduka_a11y as ea
        from eduka_common import orca_available
        self._a11y = ea
        p = UI.Page('Screen Reader', 'Orca reads aloud what is on the screen: Eduka-Desktop, Eduka-Panel, Eduka-Settings '
                                     'and the programs. Set a voice that is easy to follow.')
        f = UI.form()
        self.orca = QCheckBox('Orca screen reader — speaks focused applications and menus')
        f.addRow('Screen reader', self.orca)
        f.addRow('', UI.hint_label(('Orca is ready.' if orca_available() else
                                    'Orca is not installed: sudo apt install orca speech-dispatcher-espeak-ng.') +
                                   ' Pointer announcements use a short dwell so speech stays smooth.'))
        p.v.addLayout(f)
        v = p.new_card('Voice')
        g = UI.form()
        self.a11y_lang = self._own(QComboBox()); self.a11y_lang.setAccessibleName('Voice language')
        for i, (code, name) in enumerate(ea.VOICE_LANGUAGES):
            self.a11y_lang.addItem(_(name), (code, i == len(ea.VOICE_LANGUAGES) - 1))
        g.addRow('Language', self.a11y_lang)
        def slider(lo, hi, name, low, high):
            s = self._own(QSlider(Qt.Horizontal)); s.setRange(lo, hi); s.setAccessibleName(name); s.setMinimumWidth(220)
            s.setPageStep(max(1, (hi - lo) // 10))
            box = QHBoxLayout(); box.setSpacing(8)
            a = QLabel(_(low)); a.setObjectName('fieldHint'); b = QLabel(_(high)); b.setObjectName('fieldHint')
            box.addWidget(a); box.addWidget(s, 1); box.addWidget(b)
            return s, box
        self.a11y_rate, box = slider(0, 99, 'Speed', 'Slow', 'Fast'); g.addRow('Speed', box)
        self.a11y_pitch, box = slider(0, 9, 'Pitch', 'Low', 'High'); g.addRow('Pitch', box)
        self.a11y_volume, box = slider(0, 9, 'Volume', 'Quiet', 'Loud'); g.addRow('Volume', box)
        v.addLayout(g)
        row = QHBoxLayout(); row.setSpacing(8)
        test = QPushButton(get_icon('media-playback-start'), ' ' + _('Try the voice')); test.clicked.connect(self.try_voice)
        save = QPushButton(get_icon('document-save'), ' ' + _('Use this voice')); save.setObjectName('primary'); save.clicked.connect(self.save_voice)
        more = QPushButton(get_icon('preferences-desktop-accessibility'), ' ' + _('Orca settings…')); more.clicked.connect(self.open_orca_voice_settings)
        for b in (test, more): row.addWidget(b)
        row.addStretch(1); row.addWidget(save); v.addLayout(row)
        keys = p.new_card('Keys to know')
        lines = [('Insert + H', 'Orca help (Insert is the Orca key; on laptops Caps Lock)'),
                 ('Super', 'open Eduka-Desktop; type to search, arrows move between the tiles, Enter opens'),
                 ('Tab / Shift+Tab', 'next or previous control in Eduka-Settings and in programs'),
                 ('Alt+Tab', 'switch between windows'),
                 ('Ctrl+Alt+T', 'terminal'), ('Alt+F2', 'run a command'), ('Ctrl+Alt+L', 'lock the screen'),
                 ('Esc', 'close Eduka-Desktop, menus and dialogs')]
        grid = QGridLayout(); grid.setHorizontalSpacing(14); grid.setVerticalSpacing(4)
        for i, (k, what) in enumerate(lines):
            a = QLabel(k); a.setObjectName('rowTitle'); b = QLabel(_(what)); b.setWordWrap(True)
            a.setAccessibleName(k); b.setAccessibleName(_(what))
            grid.addWidget(a, i, 0, Qt.AlignTop); grid.addWidget(b, i, 1)
        grid.setColumnStretch(1, 1); keys.addLayout(grid)
        voice = ea.orca_voice()
        self.a11y_rate.setValue(voice['rate']); self.a11y_pitch.setValue(voice['pitch']); self.a11y_volume.setValue(voice['volume'])
        want = (voice.get('lang', ''), bool(voice.get('tetun')))
        idx = next((i for i in range(self.a11y_lang.count()) if tuple(self.a11y_lang.itemData(i)) == want), 0)
        self.a11y_lang.setCurrentIndex(idx)
        return p.finish()

    def _voice_values(self):
        code, tetun = self.a11y_lang.currentData()
        return self.a11y_rate.value(), self.a11y_pitch.value(), self.a11y_volume.value(), code, tetun

    def try_voice(self):
        if not self._a11y.test_voice(*self._voice_values()):
            self.show_status(_('No voice: install speech-dispatcher and espeak-ng.'), error=True)

    def save_voice(self):
        if self._a11y.set_orca_voice(*self._voice_values()):
            again = self._a11y.restart_orca_if_running()
            self.show_status(_('Orca uses this voice now.') if again else _('Orca uses this voice when it starts.'))
        else:
            self.show_status(_('The voice could not be saved.'), error=True)

    # ------------------------------------------------------------ LightDM
    def page_lightdm(self):
        p = UI.Page('LightDM', 'SDDM is the login screen of Edukasaun OS. LightDM with slick-greeter or '
                               'lightdm-gtk-greeter is an optional third-party login screen: install it first, then '
                               'it can be chosen here. Both greeters get the Edukasaun look of the SDDM login screen.')
        self.ldm_state = UI.hint_label(''); p.v.addWidget(self.ldm_state)
        dm_row = QHBoxLayout(); dm_row.setSpacing(8)
        self.ldm_use_lightdm = QPushButton(get_icon('system-reboot', 'view-refresh'), ' ' + _('Use LightDM at the next start'))
        self.ldm_use_sddm = QPushButton(get_icon('system-reboot', 'view-refresh'), ' ' + _('Use SDDM at the next start'))
        self.ldm_use_lightdm.clicked.connect(lambda: self.switch_display_manager('lightdm'))
        self.ldm_use_sddm.clicked.connect(lambda: self.switch_display_manager('sddm'))
        dm_row.addWidget(self.ldm_use_lightdm); dm_row.addWidget(self.ldm_use_sddm); dm_row.addStretch(1)
        p.v.addLayout(dm_row)

        # 0.11 RC3: the greeters are third-party programs (Debian packages),
        # not part of Edukasaun OS: each one can be chosen once it is installed.
        g = p.new_card('Third-party greeters (optional)')
        self.ldm_greeter_buttons = {}; self.ldm_greeter_status = {}; self.ldm_greeter_install = {}
        for key, name, hint in LIGHTDM_GREETERS:
            row = QHBoxLayout(); row.setSpacing(8)
            r = QRadioButton(f'{_(name)} ({key})'); r.setAccessibleDescription(_(hint))
            state = QLabel(''); state.setObjectName('stateChip')
            inst = QPushButton(get_icon('system-software-install', 'list-add'), ' ' + _('Install…'))
            inst.setToolTip(_('Opens a terminal that installs LightDM and this greeter (asks for your password)'))
            inst.clicked.connect(lambda _c=False, k=key: self.install_lightdm_greeter(k))
            row.addWidget(r); row.addWidget(state); row.addStretch(1); row.addWidget(inst)
            g.addLayout(row); g.addWidget(UI.hint_label(hint))
            self.ldm_greeter_buttons[key] = r; self.ldm_greeter_status[key] = state; self.ldm_greeter_install[key] = inst
        g.addWidget(UI.hint_label('While LightDM is installed, its own question "Default display manager" may come up '
                                  'in the terminal: choose sddm to keep the Edukasaun login screen for now.'))

        c = p.new_card('Look')
        f = UI.form()
        self.ldm_style = QComboBox(); self.ldm_style.setAccessibleName('Style')
        for key, label in LOGIN_STYLES: self.ldm_style.addItem(_(label), key)
        f.addRow('Style', self.ldm_style)
        self.ldm_accent_value = '#3fa684'
        self.ldm_accent = QPushButton(''); self.ldm_accent.setObjectName('swatch'); self.ldm_accent.setAccessibleName('Accent color')
        self.ldm_accent.setToolTip(_('Accent color of the login button')); self.ldm_accent.clicked.connect(self.pick_lightdm_accent)
        arow = QHBoxLayout(); arow.addWidget(self.ldm_accent); arow.addStretch(1); f.addRow('Accent color', arow)
        self.ldm_clock = QCheckBox('Show the clock'); self.ldm_host = QCheckBox('Show the computer name')
        self.ldm_clock_format = QComboBox(); self.ldm_clock_format.addItem(_('24 hours (14:30)'), '24h'); self.ldm_clock_format.addItem(_('12 hours (2:30 PM)'), '12h')
        crow = QHBoxLayout(); crow.addWidget(self.ldm_clock); crow.addWidget(self.ldm_clock_format); crow.addStretch(1)
        cbox = QVBoxLayout(); cbox.setSpacing(6); cbox.addLayout(crow); cbox.addWidget(self.ldm_host)
        f.addRow('Clock', cbox)
        self.ldm_bg_thumb = QLabel(); self.ldm_bg_thumb.setObjectName('thumb'); self.ldm_bg_thumb.setFixedSize(160, 90); self.ldm_bg_thumb.setAlignment(Qt.AlignCenter)
        bgb = QVBoxLayout(); bgb.setSpacing(6)
        for text, handler in (('Choose picture…', self.choose_lightdm_background), ('Same as the SDDM login screen', lambda: self.set_lightdm_background('sddm')),
                              ('Style gradient', lambda: self.set_lightdm_background('reset'))):
            b = QPushButton(_(text)); b.clicked.connect(handler); bgb.addWidget(b)
        brow = QHBoxLayout(); brow.addWidget(self.ldm_bg_thumb); brow.addLayout(bgb); brow.addStretch(1)
        f.addRow('Background', brow)
        self.ldm_logo_thumb = QLabel(); self.ldm_logo_thumb.setObjectName('thumb'); self.ldm_logo_thumb.setFixedSize(72, 72); self.ldm_logo_thumb.setAlignment(Qt.AlignCenter)
        lgb = QVBoxLayout(); lgb.setSpacing(6)
        for text, handler in (('Choose logo…', self.choose_lightdm_logo), ('Same as the SDDM login screen', lambda: self.set_lightdm_logo('sddm')),
                              ('Edukasaun logo', lambda: self.set_lightdm_logo('reset'))):
            b = QPushButton(_(text)); b.clicked.connect(handler); lgb.addWidget(b)
        lrow = QHBoxLayout(); lrow.addWidget(self.ldm_logo_thumb); lrow.addLayout(lgb); lrow.addStretch(1)
        f.addRow('Logo', lrow)
        c.addLayout(f)
        same = QPushButton(get_icon('edit-copy'), ' ' + _('Same look as SDDM')); same.clicked.connect(self.copy_sddm_look)
        same.setToolTip(_('Copy the style, accent, clock, background and logo of the SDDM login screen'))
        srow = QHBoxLayout(); srow.addStretch(1); srow.addWidget(same); c.addLayout(srow)

        s = p.new_card('Sign-in')
        fs = UI.form()
        self.ldm_hide = QCheckBox('Hide the list of accounts (everyone types their name)')
        self.ldm_manual = QCheckBox('Allow typing a name that is not in the list')
        self.ldm_guest = QCheckBox('Guest account (a fresh account that is emptied after logging out)')
        box = QVBoxLayout(); box.setSpacing(6)
        for w in (self.ldm_hide, self.ldm_manual, self.ldm_guest): box.addWidget(w)
        fs.addRow('Accounts', box)
        self.ldm_autologin = QCheckBox('Log in automatically as'); self.ldm_autologin_user = QComboBox()
        self.ldm_autologin_user.setMinimumWidth(150)
        auto = QHBoxLayout(); auto.addWidget(self.ldm_autologin); auto.addWidget(self.ldm_autologin_user); auto.addStretch(1)
        fs.addRow('Automatic login', auto)
        fs.addRow('', UI.hint_label('Accounts hidden in Users are not listed by LightDM either. Automatic login '
                                    'always asks for an administrator password.'))
        s.addLayout(fs)
        actions = QHBoxLayout(); actions.addStretch(1)
        self.ldm_save = QPushButton(get_icon('document-save'), ' ' + _('Save LightDM settings')); self.ldm_save.setObjectName('primary')
        self.ldm_save.clicked.connect(self.save_lightdm)
        actions.addWidget(self.ldm_save); s.addLayout(actions)
        self.ldm_style.currentIndexChanged.connect(lambda *_a: self.ldm_accent.setEnabled(self.ldm_style.currentData() != 'follow'))
        self.ldm_clock.toggled.connect(self.ldm_clock_format.setEnabled)
        self.ldm_autologin.toggled.connect(self.ldm_autologin_user.setEnabled)
        self._ldm_background = ''; self._ldm_logo = ''; self._ldm_logo_small = ''
        self.load_lightdm()
        return p.finish()

    def lightdm_installed(self):
        return os.path.exists('/usr/sbin/lightdm')

    def install_lightdm_greeter(self, key):
        """Install LightDM and a greeter in a terminal window (apt asks for
        the password there; nothing is installed behind the user's back).
        The page is read again when the terminal closes."""
        if key not in {k for k, _n, _h in LIGHTDM_GREETERS}:
            return
        from eduka_common import terminal_command
        if not shutil.which('apt-get'):
            self.show_status(_('This computer has no apt-get: install lightdm and {name} with its package manager.').replace('{name}', key), error=True)
            return
        script = ('echo "Installing LightDM and %s (third-party login screen)..."; echo; '
                  'sudo apt-get install lightdm %s; echo; '
                  'printf "Press Enter to close this window. "; read _answer' % (key, key))
        try:
            proc = subprocess.Popen(terminal_command(['sh', '-c', script]), stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, start_new_session=True)
        except Exception as e:
            self.show_status(_('Could not open a terminal: ') + str(e), error=True); return
        self.show_status(_('Installing {name} in the terminal…').replace('{name}', key))
        timer = QTimer(self); timer.setInterval(1500)
        def check():
            if proc.poll() is None:
                return
            timer.stop(); timer.deleteLater()
            self.load_lightdm()
            ok = os.path.exists(f'/usr/share/xgreeters/{key}.desktop') and self.lightdm_installed()
            self.show_status(_('{name} is installed and can be chosen.').replace('{name}', key) if ok
                             else _('{name} was not installed.').replace('{name}', key), error=not ok)
        timer.timeout.connect(check); timer.start()

    def load_lightdm(self):
        state = {}
        try:
            state = json.loads(LIGHTDM_STATE.read_text(encoding='utf-8'))
        except Exception:
            pass
        seat = ini_values(LIGHTDM_SEAT)
        installed = self.lightdm_installed()
        greeters = [k for k, _n, _h in LIGHTDM_GREETERS if os.path.exists(f'/usr/share/xgreeters/{k}.desktop')]
        dm = current_display_manager()
        names = {'sddm': 'SDDM', 'lightdm': 'LightDM'}
        lines = [_('Display manager: {dm}.').replace('{dm}', names.get(dm, dm or _('unknown')))]
        if not installed:
            lines.append(_('LightDM is not installed: press Install… next to a greeter below.'))
        elif not greeters:
            lines.append(_('No greeter for LightDM is installed: press Install… next to one below.'))
        else:
            lines.append(_('Installed greeters: {list}.').replace('{list}', ', '.join(greeters)))
        self.ldm_state.setText(' '.join(lines))
        self.ldm_use_lightdm.setVisible(installed and bool(greeters) and dm != 'lightdm')
        self.ldm_use_sddm.setVisible(dm == 'lightdm' and os.path.exists('/usr/bin/sddm'))
        chosen = seat.get('greeter-session') or state.get('greeter') or (greeters[0] if greeters else '')
        for key, r in self.ldm_greeter_buttons.items():
            ready = installed and key in greeters
            r.setEnabled(ready); r.setChecked(ready and key == chosen)
            chip = self.ldm_greeter_status.get(key)
            if chip is not None:
                chip.setText(_('Installed') if ready else _('Not installed'))
                chip.setProperty('ok', ready); chip.style().unpolish(chip); chip.style().polish(chip)
            if key in self.ldm_greeter_install:
                self.ldm_greeter_install[key].setVisible(not ready)
        follow = state.get('follow', True)
        style = 'follow' if follow else state.get('style', 'pastel')
        self.ldm_style.setCurrentIndex(max(0, self.ldm_style.findData(style)))
        self.ldm_accent.setEnabled(style != 'follow')
        self.set_lightdm_accent(state.get('accent', LOGIN_ACCENTS.get(state.get('style', 'pastel'), '#3fa684')))
        self.ldm_clock.setChecked(bool(state.get('show_clock', True)))
        self.ldm_clock_format.setCurrentIndex(max(0, self.ldm_clock_format.findData(state.get('clock_format', '24h'))))
        self.ldm_clock_format.setEnabled(self.ldm_clock.isChecked())
        self.ldm_host.setChecked(bool(state.get('show_hostname', True)))
        self.ldm_hide.setChecked(seat.get('greeter-hide-users', 'false') == 'true')
        self.ldm_manual.setChecked(seat.get('greeter-show-manual-login', 'true') == 'true')
        guest_ok = os.path.exists('/usr/sbin/guest-account')
        self.ldm_guest.setEnabled(guest_ok); self.ldm_guest.setChecked(guest_ok and seat.get('allow-guest', 'false') == 'true')
        self.ldm_guest.setToolTip('' if guest_ok else _('LightDM of this system has no guest account support.'))
        users = self.human_users() if hasattr(self, 'human_users') else []
        self.ldm_autologin_user.clear(); self.ldm_autologin_user.addItems(users)
        auto = ini_values(LIGHTDM_AUTOLOGIN).get('autologin-user', '')
        self._ldm_auto_now = auto
        self.ldm_autologin.setChecked(bool(auto)); self.ldm_autologin_user.setEnabled(bool(auto))
        if auto: self.ldm_autologin_user.setCurrentText(auto)
        self._ldm_bg_kind = state.get('background', 'style'); self._ldm_logo_kind = state.get('logo', 'default')
        self.update_lightdm_thumbs()
        for w in (self.ldm_style, self.ldm_accent, self.ldm_clock, self.ldm_hide, self.ldm_manual, self.ldm_autologin, self.ldm_save):
            w.setEnabled(installed and w.isEnabled())
        self.ldm_save.setEnabled(installed and bool(greeters))

    def lightdm_style(self):
        style = self.ldm_style.currentData()
        if style == 'follow':
            from eduka_common import read_desktop_config, normalize_theme_style, THEME_DARK, THEME_TRANSPARENT, THEME_LIQUID, THEME_PASTEL
            theme = normalize_theme_style(read_desktop_config().get('theme_style'))
            style = {THEME_DARK: 'dark', THEME_TRANSPARENT: 'dark', THEME_LIQUID: 'glass', THEME_PASTEL: 'pastel'}.get(theme, 'light')
            return style, LOGIN_ACCENTS[style]
        return style, self.ldm_accent_value

    def update_lightdm_thumbs(self):
        style, _accent = self.lightdm_style()
        bg = self._ldm_background
        if not bg or bg in ('reset', 'sddm'):
            kind = {'reset': 'style', 'sddm': 'sddm'}.get(bg, self._ldm_bg_kind)
            bg = {'own': '/usr/share/Edukasaun/LightDM/Default.png', 'sddm': '/usr/share/Edukasaun/SDDM/Default.png'}.get(kind, '')
            if not os.path.exists(bg):
                bg = f'/usr/share/edukasaun-desktop/login/{style}.png'
        pix = QPixmap(bg)
        self.ldm_bg_thumb.setPixmap(pix.scaled(160, 90, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation) if not pix.isNull() else QPixmap())
        logo = self._ldm_logo
        if not logo or logo in ('reset', 'sddm'):
            kind = {'reset': 'default', 'sddm': 'sddm'}.get(logo, self._ldm_logo_kind)
            logo = {'own': '/usr/share/Edukasaun/LightDM/Logo.png', 'sddm': '/usr/share/Edukasaun/SDDM/Logo.png'}.get(kind, '')
            if not os.path.exists(logo):
                logo = next((p for p in ('/usr/share/Edukasaun/Logo/Edukasaun Logo.png', '/usr/share/sddm/themes/edukasaun/logo.png') if os.path.exists(p)), '')
        pix = QPixmap(logo)
        self.ldm_logo_thumb.setPixmap(pix.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation) if not pix.isNull() else QPixmap())

    def pick_lightdm_accent(self):
        color = QColorDialog.getColor(QColor(self.ldm_accent_value), self, _('Accent color'))
        if color.isValid(): self.set_lightdm_accent(color.name())

    def set_lightdm_accent(self, value):
        self.ldm_accent_value = value
        self.ldm_accent.setStyleSheet(f'QPushButton#swatch{{background:{value};border:2px solid rgba(255,255,255,200);}}')

    def choose_lightdm_background(self):
        path, _f = QFileDialog.getOpenFileName(self, _('Login background'), str(Path.home()/'Pictures'), _('Pictures (*.png *.jpg *.jpeg *.webp *.bmp)'))
        if path: self.set_lightdm_background(path)

    def set_lightdm_background(self, value):
        self._ldm_background = value; self.update_lightdm_thumbs()

    def choose_lightdm_logo(self):
        path, _f = QFileDialog.getOpenFileName(self, _('Login logo'), str(Path.home()/'Pictures'), _('Pictures (*.png *.jpg *.jpeg *.webp *.bmp)'))
        if path: self.set_lightdm_logo(path)

    def set_lightdm_logo(self, value):
        """A chosen logo also gets a small copy for slick-greeter, made here
        (as the user), so the root helper never decodes a picture."""
        self._ldm_logo = value; self._ldm_logo_small = ''
        source = value if value not in ('reset', 'sddm') else ('/usr/share/Edukasaun/SDDM/Logo.png' if value == 'sddm' else '')
        if value == 'sddm' and not os.path.exists(source):
            source = next((p for p in ('/usr/share/Edukasaun/Logo/Edukasaun Logo.png', '/usr/share/sddm/themes/edukasaun/logo.png') if os.path.exists(p)), '')
        if source:
            img = QImage(source)
            if not img.isNull():
                out = CACHE_DIR/'ui'/'lightdm-logo-small.png'; out.parent.mkdir(parents=True, exist_ok=True)
                img.scaledToHeight(min(112, img.height()), Qt.SmoothTransformation).save(str(out), 'PNG')
                os.chmod(out, 0o600); self._ldm_logo_small = str(out)
        self.update_lightdm_thumbs()

    def copy_sddm_look(self):
        """The same look as the SDDM login screen: style, accent, clock,
        background and logo."""
        cfg = {}
        for name in ('theme.conf', 'theme.conf.user'):
            cfg.update(ini_values(f'/usr/share/sddm/themes/edukasaun/{name}'))
        try:
            from eduka_common import read_menu_config
            follow = bool(read_menu_config().get('sddm_follow', True))
        except Exception:
            follow = False
        style = 'follow' if follow else cfg.get('style', 'pastel')
        self.ldm_style.setCurrentIndex(max(0, self.ldm_style.findData(style)))
        if re.fullmatch(r'#[0-9a-fA-F]{6}', cfg.get('accent', '')): self.set_lightdm_accent(cfg['accent'])
        self.ldm_clock.setChecked(cfg.get('showClock', 'true').lower() != 'false')
        self.set_lightdm_background('sddm'); self.set_lightdm_logo('sddm')
        self.show_status(_('The look of the SDDM login screen is ready; press Save LightDM settings.'))

    def run_lightdm_helper(self, mode, request):
        try:
            out = subprocess.run(['pkexec', LIGHTDM_HELPER, mode], input=json.dumps(request), capture_output=True, text=True, timeout=180)
        except Exception as exc:
            return False, str(exc)
        if out.returncode == 0:
            return True, ''
        if out.returncode in (126, 127):
            return False, _('the administrator password was not given')
        reason = (out.stderr or out.stdout).strip().splitlines()
        return False, reason[-1] if reason else _('unknown error')

    def save_lightdm(self):
        if not shutil.which('pkexec') or not os.path.exists(LIGHTDM_HELPER):
            self.show_status(_('LightDM can only be changed on Edukasaun OS (pkexec missing).'), error=True); return
        style, accent = self.lightdm_style()
        look = {'style': style, 'accent': accent, 'show_clock': self.ldm_clock.isChecked(),
                'clock_format': self.ldm_clock_format.currentData(), 'show_hostname': self.ldm_host.isChecked(),
                'background': self._ldm_background, 'logo': self._ldm_logo, 'logo_small': self._ldm_logo_small,
                'follow': self.ldm_style.currentData() == 'follow'}
        greeter = next((k for k, r in self.ldm_greeter_buttons.items() if r.isChecked() and r.isEnabled()), '')
        seat = {'greeter': greeter, 'hide_users': self.ldm_hide.isChecked(), 'manual_login': self.ldm_manual.isChecked(),
                'guest': self.ldm_guest.isChecked()}
        auto = self.ldm_autologin_user.currentText() if self.ldm_autologin.isChecked() else ''
        self.ldm_save.setEnabled(False)
        def work():
            ok, why = self.run_lightdm_helper('--look', look)
            if not ok: return False, _('Look not saved: ') + why
            ok, why = self.run_lightdm_helper('--seat', seat)
            if not ok: return False, _('Sign-in options not saved: ') + why
            if auto != self._ldm_auto_now:
                ok, why = self.run_lightdm_helper('--autologin', {'autologin_user': auto})
                if not ok: return False, _('Automatic login not changed: ') + why
            return True, _('LightDM login screen saved; it is used at the next login.')
        def done(result, error):
            ok, text = result if result and not error else (False, str(error))
            self.ldm_save.setEnabled(True)
            self._ldm_background = ''; self._ldm_logo = ''; self._ldm_logo_small = ''
            self.load_lightdm(); self.show_status(text, error=not ok)
        run_in_background(self, work, done)

    def switch_display_manager(self, dm):
        name = {'sddm': 'SDDM', 'lightdm': 'LightDM'}[dm]
        if QMessageBox.question(self, _('Display manager'), _('Use {dm} for the login screen from the next start of the computer?').replace('{dm}', name),
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        def done(result, error):
            ok, why = result if result and not error else (False, str(error))
            self.load_lightdm()
            self.show_status(_('{dm} is used from the next start.').replace('{dm}', name) if ok else _('Not changed: ') + why, error=not ok)
        run_in_background(self, lambda: self.run_lightdm_helper('--display-manager', {'display_manager': dm}), done)

    # ------------------------------------------------------------ fonts
    def page_fonts(self):
        import eduka_fonts as ef
        self._ef = ef
        p = UI.Page('Fonts', 'The letters of the whole desktop: Eduka, LXQt and GTK programs, the desktop icons '
                             'and the window titles. A change is used at once.')
        f = UI.form(); self.font_buttons = {}
        for role, name, hint in FONT_ROLES:
            b = QPushButton(); b.setObjectName('fontButton'); b.setMinimumWidth(270); b.setMinimumHeight(34)
            b.setCursor(Qt.PointingHandCursor); b.setAccessibleName(name); b.setAccessibleDescription(hint)
            b.clicked.connect(lambda _c=False, r=role: self.choose_font(r))
            box = QVBoxLayout(); box.setSpacing(3); box.addWidget(b, 0, Qt.AlignLeft); box.addWidget(UI.hint_label(hint))
            f.addRow(name, box); self.font_buttons[role] = b
        p.v.addLayout(f)

        c = p.new_card('Font Settings')
        g = UI.form()
        scale = QHBoxLayout(); scale.setSpacing(6)
        minus = QToolButton(); minus.setText('−'); minus.setObjectName('stepButton'); minus.setFixedSize(34, 32)
        plus = QToolButton(); plus.setText('+'); plus.setObjectName('stepButton'); plus.setFixedSize(34, 32)
        minus.setAccessibleName('Smaller text'); plus.setAccessibleName('Bigger text')
        self.font_scale = QDoubleSpinBox(); self.font_scale.setRange(ef.SCALE_MIN, ef.SCALE_MAX); self.font_scale.setSingleStep(0.05)
        self.font_scale.setDecimals(2); self.font_scale.setButtonSymbols(QAbstractSpinBox.NoButtons); self.font_scale.setAlignment(Qt.AlignCenter)
        self.font_scale.setFixedWidth(76); self.font_scale.setAccessibleName('Text scaling factor')
        minus.clicked.connect(self.font_scale.stepDown); plus.clicked.connect(self.font_scale.stepUp)
        minus.setAutoRepeat(True); plus.setAutoRepeat(True)
        scale.addWidget(minus); scale.addWidget(self.font_scale); scale.addWidget(plus); scale.addStretch(1)
        g.addRow('Text scaling factor', scale)
        g.addRow('', UI.hint_label('Bigger or smaller letters everywhere; programs that are open use it when they start again.'))
        self.font_hinting = QComboBox(); self.font_hinting.setAccessibleName('Hinting')
        for key, text in (('none', 'None'), ('slight', 'Slight'), ('medium', 'Medium'), ('full', 'Full')):
            self.font_hinting.addItem(_(text), key)
        g.addRow('Hinting', self.font_hinting)
        self.font_aa = QComboBox(); self.font_aa.setAccessibleName('Antialiasing')
        for key, text in (('none', 'None (sharp edges)'), ('grayscale', 'Grayscale (projectors and all screens)'),
                          ('rgba', 'Subpixel (flat LCD screens)')):
            self.font_aa.addItem(_(text), key)
        g.addRow('Antialiasing', self.font_aa)
        self.font_rgba = QComboBox(); self.font_rgba.setAccessibleName('RGBA order')
        for key, text in (('rgb', 'RGB'), ('bgr', 'BGR'), ('vrgb', 'Vertical RGB'), ('vbgr', 'Vertical BGR')):
            self.font_rgba.addItem(_(text), key)
        g.addRow('RGBA order', self.font_rgba)
        c.addLayout(g)
        self.font_preview = QLabel('Edukasaun ba ema hotu — Pendidikan untuk semua — Education for everyone. 0123456789')
        self.font_preview.setObjectName('fontPreview'); self.font_preview.setWordWrap(True)
        self.font_preview.setAccessibleName('Font preview')
        c.addWidget(self.font_preview)
        row = QHBoxLayout(); row.addStretch(1)
        reset = QPushButton(get_icon('edit-undo', 'document-revert'), ' ' + _('Reset to defaults')); reset.clicked.connect(self.reset_fonts)
        row.addWidget(reset); c.addLayout(row)
        p.v.addWidget(UI.hint_label('Fonts are written for Qt (LXQt), GTK 2, 3 and 4, the X resources, fontconfig, '
                                    'the desktop icons (pcmanfm-qt), Openbox and xfwm4.'))
        self._font_timer = QTimer(self); self._font_timer.setSingleShot(True); self._font_timer.setInterval(650)
        self._font_timer.timeout.connect(self.save_font_rendering)
        self.load_fonts()
        self.font_scale.valueChanged.connect(lambda *_a: self._font_timer.start())
        for combo in (self.font_hinting, self.font_aa, self.font_rgba):
            combo.activated.connect(lambda *_a: self._font_timer.start())
        self.font_aa.currentIndexChanged.connect(lambda *_a: self.font_rgba.setEnabled(self.font_aa.currentData() == 'rgba'))
        return p.finish()

    def load_fonts(self):
        ef = self._ef
        self._fonts = ef.current_fonts()
        for role, b in self.font_buttons.items():
            font = self._fonts[role]
            self.show_font_on(b, font)
            b.setToolTip(_('Choose the font…'))
        render = ef.current_rendering()
        for combo, key in ((self.font_hinting, 'hinting'), (self.font_aa, 'antialias'), (self.font_rgba, 'rgba')):
            combo.blockSignals(True); combo.setCurrentIndex(max(0, combo.findData(render[key]))); combo.blockSignals(False)
        self.font_rgba.setEnabled(render['antialias'] == 'rgba')
        self.font_scale.blockSignals(True); self.font_scale.setValue(render['scale']); self.font_scale.blockSignals(False)
        self.font_preview.setFont(self.qfont(self._fonts['default'], limit=18))

    def show_font_on(self, button, font):
        """The button names the font and is written in it (at most 13 pt)."""
        family = font['family'].replace('"', '')
        button.setText(self._ef.describe(font))
        button.setStyleSheet('font-family:"%s";font-size:%gpt;font-weight:%d;font-style:%s;padding:4px 18px;'
                             % (family, min(font['size'], 13), font['weight'], 'italic' if font.get('italic') else 'normal'))

    def qfont(self, font, limit=None):
        q = QFont(font['family']); size = font['size']
        q.setPointSizeF(min(size, limit) if limit else size)
        q.setWeight(self._ef.qt_weight(font['weight'])); q.setItalic(bool(font.get('italic')))
        return q

    def choose_font(self, role):
        ef = self._ef
        name = dict((r, n) for r, n, _h in FONT_ROLES)[role]
        options = QFontDialog.FontDialogOptions()
        if role == 'monospace':
            options |= QFontDialog.MonospacedFonts
        font, ok = QFontDialog.getFont(self.qfont(self._fonts[role]), self, _(name), options)
        if not ok:
            return
        new = ef.make_font(font.family(), font.pointSizeF() if font.pointSizeF() > 0 else self._fonts[role]['size'],
                           ef.css_weight(font.weight()), font.italic())
        self._fonts[role] = new
        b = self.font_buttons[role]; self.show_font_on(b, new); b.setEnabled(False)
        if role == 'default':
            self.font_preview.setFont(self.qfont(new, limit=18))
        def done(ok, error):
            b.setEnabled(True)
            if ok and not error:
                self.show_status(_('{name}: {font}').replace('{name}', _(name)).replace('{font}', ef.describe(new)))
            else:
                self.show_status(_('The font could not be saved.'), error=True)
        run_in_background(self, lambda: ef.apply_font(role, new), done)

    def save_font_rendering(self):
        ef = self._ef
        render = {'hinting': self.font_hinting.currentData(), 'antialias': self.font_aa.currentData(),
                  'rgba': self.font_rgba.currentData(), 'scale': round(self.font_scale.value(), 2)}
        def done(ok, error):
            if ok and not error:
                self.show_status(_('Font settings saved. Programs that are open use them when they start again.'))
            else:
                self.show_status(_('The font settings could not be saved.'), error=True)
        run_in_background(self, lambda: ef.apply_rendering(render), done)

    def reset_fonts(self):
        if QMessageBox.question(self, _('Reset fonts'), _('Use the Edukasaun fonts and font settings again?'),
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        ef = self._ef
        for b in self.font_buttons.values(): b.setEnabled(False)
        def done(_ok, error):
            for b in self.font_buttons.values(): b.setEnabled(True)
            self.load_fonts()
            self.show_status(_('The fonts are the Edukasaun fonts again.') if not error else _('The fonts could not be reset.'), error=bool(error))
        run_in_background(self, ef.reset_fonts, done)

    # ------------------------------------------------------------ users
    def page_users(self):
        import eduka_accounts as ea
        self._ea = ea
        p = UI.Page('Users', 'The accounts of the people who use this computer: add and remove accounts, '
                             'change names, pictures, passwords and who is an administrator.')
        body = QHBoxLayout(); body.setSpacing(14)
        left = QVBoxLayout(); left.setSpacing(8)
        self.users_list = QListWidget(); self.users_list.setObjectName('layoutList'); self.users_list.setIconSize(QSize(40, 40))
        self.users_list.setFixedWidth(232); self.users_list.setMinimumHeight(300); self.users_list.setSpacing(2)
        self.users_list.setAccessibleName(_('User accounts'))
        left.addWidget(self.users_list, 1)
        add = QPushButton(get_icon('list-add'), ' ' + _('Add account…')); add.clicked.connect(self.add_user)
        left.addWidget(add)
        body.addLayout(left)

        det = QVBoxLayout(); det.setSpacing(8)
        head = QHBoxLayout(); head.setSpacing(12)
        self.user_pic = QToolButton(); self.user_pic.setFixedSize(92, 92); self.user_pic.setIconSize(QSize(84, 84)); self.user_pic.setAutoRaise(True)
        self.user_pic.setCursor(Qt.PointingHandCursor); self.user_pic.setToolTip(_('Change the picture')); self.user_pic.clicked.connect(self.change_user_picture)
        self.user_pic.setAccessibleName(_('Account picture'))
        head.addWidget(self.user_pic)
        names = QVBoxLayout(); names.setSpacing(2)
        self.user_title = QLabel(''); self.user_title.setObjectName('cardTitle'); self.user_title.setWordWrap(True)
        self.user_sub = QLabel(''); self.user_sub.setObjectName('fieldHint'); self.user_sub.setWordWrap(True)
        names.addWidget(self.user_title); names.addWidget(self.user_sub); names.addStretch(1)
        head.addLayout(names, 1); det.addLayout(head)
        # A compact grid (short titles) leaves the fields room next to the list.
        f = QGridLayout(); f.setHorizontalSpacing(10); f.setVerticalSpacing(8); f.setColumnStretch(1, 1)
        def title(text):
            t = QLabel(text); t.setObjectName('rowTitle'); return t
        self.user_full = QLineEdit(); self.user_full.setMaxLength(64)
        save_name = QPushButton(_('Save')); save_name.clicked.connect(self.save_user_full_name)
        self.user_full.returnPressed.connect(self.save_user_full_name)
        f.addWidget(title('Full name'), 0, 0); f.addWidget(self.user_full, 0, 1); f.addWidget(save_name, 0, 2)
        self.user_login = QLabel(''); rename = QPushButton(_('Rename…')); rename.clicked.connect(self.rename_user)
        f.addWidget(title('Login name'), 1, 0); f.addWidget(self.user_login, 1, 1); f.addWidget(rename, 1, 2)
        self.user_type = QComboBox(); self.user_type.addItem(_('Standard'), False); self.user_type.addItem(_('Administrator'), True)
        self.user_type.activated.connect(self.change_user_type)
        f.addWidget(title('Account type'), 2, 0); f.addWidget(self.user_type, 2, 1, 1, 2)
        pw = QPushButton(get_icon('dialog-password', 'document-encrypt'), ' ' + _('Change password…')); pw.clicked.connect(self.change_user_password)
        f.addWidget(title('Password'), 3, 0); f.addWidget(pw, 3, 1, 1, 2, Qt.AlignLeft)
        self.user_visible = QCheckBox(_('Show on the login screen')); self.user_visible.clicked.connect(self.change_user_hidden)
        f.addWidget(self.user_visible, 4, 0, 1, 3)
        self.user_enabled = QCheckBox(_('This account can log in')); self.user_enabled.clicked.connect(self.change_user_lock)
        f.addWidget(self.user_enabled, 5, 0, 1, 3)
        det.addLayout(f)
        self.user_note = UI.hint_label(''); det.addWidget(self.user_note)
        drow = QHBoxLayout(); drow.addStretch(1)
        self.user_delete = QPushButton(get_icon('list-remove', 'edit-delete'), ' ' + _('Delete account…')); self.user_delete.clicked.connect(self.delete_user)
        drow.addWidget(self.user_delete); det.addLayout(drow)
        det.addStretch(1)
        body.addLayout(det, 1)
        p.v.addLayout(body)
        p.v.addWidget(UI.hint_label('Changing another account asks for an administrator password. Your own picture, '
                                    'name and password can be changed without one. Pictures are used by the login '
                                    'screen (SDDM and LightDM) and by Eduka-Desktop.'))
        self.users_list.currentRowChanged.connect(self.show_user)
        self._users = []
        QTimer.singleShot(0, self.reload_users)
        return p.finish()

    def reload_users(self, select=None):
        ea = self._ea
        current = select or (self._users[self.users_list.currentRow()]['name'] if 0 <= self.users_list.currentRow() < len(self._users) else None)
        self._users = ea.list_users()
        self.users_list.blockSignals(True); self.users_list.clear()
        row = 0
        for i, u in enumerate(self._users):
            kind = _('Administrator') if u['admin'] else _('Standard')
            extra = []
            if u['current']: extra.append(_('you'))
            if u['hidden']: extra.append(_('hidden'))
            if u.get('locked'): extra.append(_('locked'))
            text = (u['full_name'] or u['name']) + '\n' + u['name'] + ' · ' + kind + (' · ' + ', '.join(extra) if extra else '')
            it = QListWidgetItem(QIcon(user_picture(u, 40)), text); it.setSizeHint(QSize(212, 52))
            it.setToolTip(u['home']); self.users_list.addItem(it)
            if u['name'] == current:
                row = i
        self.users_list.blockSignals(False)
        if self._users:
            self.users_list.setCurrentRow(row); self.show_user(row)

    def selected_user(self):
        row = self.users_list.currentRow()
        return self._users[row] if 0 <= row < len(self._users) else None

    def show_user(self, row):
        u = self.selected_user()
        if not u:
            return
        self.user_pic.setIcon(QIcon(user_picture(u, 84)))
        self.user_title.setText(u['full_name'] or u['name'])
        bits = [_('Administrator') if u['admin'] else _('Standard account')]
        if u['current']: bits.append(_('this is you'))
        if u['logged_in'] and not u['current']: bits.append(_('logged in now'))
        self.user_sub.setText(' · '.join(bits) + '\n' + u['home'])
        self.user_full.setText(u['full_name']); self.user_login.setText(u['name'])
        self.user_type.setCurrentIndex(1 if u['admin'] else 0)
        self.user_visible.setChecked(not u['hidden'])
        self.user_enabled.setChecked(u.get('locked') is not True)
        self.user_enabled.setEnabled(not u['current'])
        self.user_delete.setEnabled(not u['current'])
        notes = []
        if u['current']:
            notes.append(_('Your own account: it cannot be deleted, locked or renamed from here.'))
        if u['logged_in'] and not u['current']:
            notes.append(_('This account is logged in; log it out before you rename or delete it.'))
        self.user_note.setText(' '.join(notes))

    def users_done(self, ok, message, select=None):
        self.show_status(_(message) if ok else _('Not changed: {e}').replace('{e}', _(message)), error=not ok)
        self.reload_users(select)

    def add_user(self):
        d = AddUserDialog(self)
        if not d.exec_():
            return
        req = d.request()
        ok, msg = self._ea.run_helper(req)
        if ok:
            img = d.image or self._ea.initials_avatar(req['full_name'], req['name'], theme_accent())
            self.set_picture_for({'name': req['name'], 'current': False}, img, quiet=True)
        self.users_done(ok, msg, req['name'])

    def set_picture_for(self, user, image, quiet=False):
        ea = self._ea
        target = CACHE_DIR/'ui'/f'avatar-{user["name"]}.png'
        if not ea.make_avatar(image, target):
            return False, 'The picture could not be prepared.'
        os.chmod(target, 0o600)
        if user.get('current'):
            ok, msg = ea.set_own_avatar(str(target))
        else:
            ok, msg = ea.run_helper({'action': 'avatar', 'name': user['name'], 'image': str(target)})
        if not quiet:
            self.users_done(ok, msg, user['name'])
        return ok, msg

    def change_user_picture(self):
        u = self.selected_user()
        if not u:
            return
        d = AvatarPicker(self, u)
        if d.exec_() and d.result_image is not None:
            self.set_picture_for(u, d.result_image)

    def save_user_full_name(self):
        u = self.selected_user()
        if not u:
            return
        text = self.user_full.text().strip()
        if text == u['full_name']:
            return
        if u['current']:
            ok, msg = self._ea.set_own_full_name(text)
        else:
            ok, msg = self._ea.run_helper({'action': 'full_name', 'name': u['name'], 'full_name': text})
        self.users_done(ok, msg, u['name'])

    def rename_user(self):
        u = self.selected_user()
        if not u:
            return
        if u['current']:
            self.show_status(_('Your own login name can only be changed from another administrator account.'), error=True); return
        from PyQt5.QtWidgets import QInputDialog
        new, ok = QInputDialog.getText(self, _('Rename login name'), _('New login name for {n}:').replace('{n}', u['name']), text=u['name'])
        new = (new or '').strip()
        if not ok or not new or new == u['name']:
            return
        reason = self._ea.check_name(new)
        if reason:
            self.show_status(_(reason), error=True); return
        ok, msg = self._ea.run_helper({'action': 'rename', 'name': u['name'], 'new_name': new})
        self.users_done(ok, msg, new if ok else u['name'])

    def change_user_type(self, *_a):
        u = self.selected_user()
        if not u:
            return
        want = bool(self.user_type.currentData())
        if want == u['admin']:
            return
        if not want and u['current'] and QMessageBox.question(self, _('Account type'),
                _('You will no longer be an administrator. Continue?')) != QMessageBox.Yes:
            self.user_type.setCurrentIndex(1); return
        ok, msg = self._ea.run_helper({'action': 'admin', 'name': u['name'], 'admin': want})
        self.users_done(ok, msg, u['name'])

    def change_user_password(self):
        u = self.selected_user()
        if not u:
            return
        import eduka_fingerprint as efp
        d = PasswordDialog(self, u, own=u['current'], fingerprint=efp.pam_mode() != 'off')
        if not d.exec_():
            return
        if u['current'] and d.forgot.isChecked():
            ok, msg = self._ea.reset_own_password(d.new.text())
        elif u['current']:
            ok, msg = self._ea.change_own_password(d.old.text(), d.new.text())
        else:
            ok, msg = self._ea.run_helper({'action': 'password', 'name': u['name'], 'password': d.new.text()})
        self.users_done(ok, msg, u['name'])

    def change_user_hidden(self, visible):
        u = self.selected_user()
        if not u:
            return
        ok, msg = self._ea.run_helper({'action': 'hidden', 'name': u['name'], 'hidden': not visible})
        self.users_done(ok, msg, u['name'])

    def change_user_lock(self, enabled):
        u = self.selected_user()
        if not u:
            return
        ok, msg = self._ea.run_helper({'action': 'lock', 'name': u['name'], 'locked': not enabled})
        if not ok:
            self.user_enabled.setChecked(not enabled)
        self.users_done(ok, msg, u['name'])

    def delete_user(self):
        u = self.selected_user()
        if not u or u['current']:
            return
        box = QMessageBox(self); box.setWindowTitle(_('Delete account')); box.setIcon(QMessageBox.Warning)
        box.setText(_('Delete the account {n}?').replace('{n}', u['full_name'] or u['name']))
        box.setInformativeText(_('Its files in {h} can be kept or deleted.').replace('{h}', u['home']))
        delete_all = box.addButton(_('Delete account and files'), QMessageBox.DestructiveRole)
        keep = box.addButton(_('Delete account, keep files'), QMessageBox.AcceptRole)
        box.addButton(_('Cancel'), QMessageBox.RejectRole)
        box.exec_()
        if box.clickedButton() not in (delete_all, keep):
            return
        ok, msg = self._ea.run_helper({'action': 'delete', 'name': u['name'], 'keep_files': box.clickedButton() is keep})
        self.users_done(ok, msg)
