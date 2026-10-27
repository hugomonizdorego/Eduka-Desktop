#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Write the manual pages of the Eduka-Desktop commands.

    python3 tools/gen-manpages.py OUTDIR

tools/build-deb.sh calls it and installs the pages (gzip -9n) to
/usr/share/man/man1. Text markup: **bold**, *italic*; a paragraph per string.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# command: (summary, synopsis, description paragraphs, options, files, see also)
PAGES = {
    'eduka-panel': (
        'task bar, Action Center and notifications of Eduka-Desktop',
        ['[**--autostart**]'],
        ['**eduka-panel** shows the Eduka-Panel on one edge of the screen: the menu button, the open windows, '
         'the clock and the status icons for sound, network, Bluetooth, battery and drives. A click on the clock '
         'opens the Action Center with the calendar, the agenda, the weather and quick settings.',
         'Inside an Eduka-Desktop session it is also the notification service (org.freedesktop.Notifications) '
         'and replaces lxqt-panel and lxqt-notificationd, which it stops through lxqt-session. Only one '
         'Eduka-Panel runs per session. After a package update it starts again by itself.'],
        [('--autostart', 'Started by the session autostart (/etc/xdg/autostart). Outside an Eduka-Desktop session '
          '(a plain LXQt session) the program quits at once, so LXQt keeps its own panel and notifications, '
          'unless "run_in_lxqt_sessions" is true in the Eduka-Desktop settings.')],
        [('~/.config/eduka-desktop/panel/settings.json', 'panel settings (written by eduka-settings)'),
         ('~/.config/eduka-desktop/agenda.json', 'agenda of the Action Center calendar'),
         ('~/.config/eduka-desktop/notifications.json', 'the last notifications'),
         ('$XDG_RUNTIME_DIR/eduka-desktop/', 'locks and state of the running session')],
        ['eduka-menu', 'eduka-settings', 'eduka-session-action', 'eduka-compositor', 'lxqt-session']),
    'eduka-menu': (
        'Eduka-Desktop start menu',
        ['[**--show** | **--hide** | **--toggle**]', '**--daemon** [**--show**] [**--autostart**]'],
        ['**eduka-menu** opens or closes Eduka-Desktop, the start menu of Edukasaun OS with the application '
         'categories, search, favorites and the session buttons. The menu itself runs as a small resident '
         'program (the daemon) so it opens at once; **eduka-menu** without **--daemon** only tells the daemon '
         'what to do and starts it when it does not run yet.'],
        [('--toggle', 'Open the menu when it is closed, close it when it is open (the default).'),
         ('--show', 'Open the menu.'),
         ('--hide', 'Close the menu.'),
         ('--daemon', 'Run the resident menu program. A second daemon in the same session quits at once.'),
         ('--autostart', 'Used by the session autostart: outside an Eduka-Desktop session the program quits.')],
        [('~/.config/eduka-desktop/menu/settings.json', 'menu settings'),
         ('~/.config/eduka-desktop/menu/favorites.json', 'favorite applications'),
         ('~/.cache/eduka-desktop/app-registry.json', 'cache of the application list')],
        ['eduka-panel', 'eduka-settings', 'eduka-app-cache', 'edukasaun-desktop-menu-open']),
    'eduka-settings': (
        'settings of Eduka-Desktop',
        ['[**--page** *PAGE*]'],
        ['**eduka-settings** changes the look and behaviour of Eduka-Desktop: theme, accent color, icons and '
         'cursor, wallpaper, desktop icons, effects, the menu and the panel, clock and weather, notifications, '
         'keyboard, mouse and touchpad, language, accessibility, Parental Control, the login screen and '
         'maintenance tasks. Changes to Parental Control and the login screen ask for an administrator '
         'password (pkexec).',
         'When Eduka-Settings is already open, its window is raised and shows the requested page.'],
        [('--page PAGE', 'Open one page: appearance, wallpaper, desktopicons, effects, desktop, panel, clock, '
          'notifications, keyboard, mouse, touchpad, general, accessibility, parental, login or maintenance.')],
        [('~/.config/eduka-desktop/', 'settings of this account'),
         ('/etc/edukasaun-desktop/parental.json', 'Parental Control settings (system-wide)'),
         ('/usr/share/sddm/themes/edukasaun/theme.conf.user', 'login screen settings')],
        ['eduka-panel', 'eduka-menu', 'eduka-panel-reset', 'eduka-compositor', 'pkexec']),
    'eduka-menu-settings': (
        'old name of eduka-settings',
        ['[*OPTION*]...'],
        ['**eduka-menu-settings** starts **eduka-settings** with the same arguments. It is kept so menu entries '
         'and scripts written for versions before 0.9.16 keep working.'],
        [], [], ['eduka-settings']),
    'eduka-about': (
        'About Edukasaun Desktop: version, credits and licenses',
        [''],
        ['**eduka-about** shows the version of Edukasaun Desktop, the projects it is built on with their '
         'authors and licenses, and the license of Edukasaun Desktop itself (GNU GPL version 3 or later).'],
        [], [('/usr/share/doc/edukasaun-desktop-menu/copyright', 'copyright and license of every part')],
        ['eduka-settings']),
    'eduka-app-cache': (
        'build the application list of Eduka-Desktop',
        ['[**--warm** | **--rebuild**] [**--print**]'],
        ['**eduka-app-cache** reads the desktop entries of the installed applications (XDG data directories, '
         'Flatpak and Snap) and stores the list Eduka-Desktop and Eduka-Panel use. The list is rebuilt by '
         'itself when applications are installed or removed, so this command is only needed for tests.'],
        [('--warm, --rebuild', 'Read every desktop entry again instead of using the stored list.'),
         ('--print', 'Print the path of the stored list instead of a summary.')],
        [('~/.cache/eduka-desktop/app-registry.json', 'the stored list')],
        ['eduka-menu', 'eduka-app-registry']),
    'eduka-app-registry': (
        'build the application list of Eduka-Desktop',
        ['[**--warm** | **--rebuild**] [**--print**]'],
        ['**eduka-app-registry** is the same program as **eduka-app-cache**.'],
        [('--warm, --rebuild', 'Read every desktop entry again instead of using the stored list.'),
         ('--print', 'Print the path of the stored list instead of a summary.')],
        [], ['eduka-app-cache']),
    'eduka-compositor': (
        'show or change the compositor used by Eduka-Desktop',
        ['[**status**]', '**restart**', '**set** *MODE*'],
        ['Eduka-Panel and Eduka-Desktop are transparent and have rounded corners only while a compositor runs. '
         'xfwm4 composites by itself; with Openbox Eduka-Desktop starts picom. Without a compositor every '
         'Eduka window uses an opaque look, so no part of the screen turns black.',
         'Without arguments **eduka-compositor** prints a report: window manager, compositor, picom backend, '
         'who started it, virtual machine and OpenGL renderer.'],
        [('restart', 'Start the compositor again, also after it crashed several times.'),
         ('set MODE', 'auto, xrender, glx, wm or off; the same as Eduka-Settings, Appearance, Compositor.')],
        [('$XDG_RUNTIME_DIR/eduka-desktop/picom.json', 'state of the picom started by Eduka-Desktop'),
         ('$XDG_RUNTIME_DIR/eduka-desktop/picom.log', 'its last messages')],
        ['picom', 'xfwm4', 'openbox', 'eduka-settings']),
    'eduka-default-user': (
        'create the standard Edukasaun account',
        [''],
        ['**eduka-default-user** creates the account *edukasaun* with the password *edukasaun* and administrator '
         'rights (group sudo). It must be run as root. The package runs it by itself only while the Edukasaun OS '
         'image is built, when no personal account exists yet; the live session uses this account. On an '
         'installed computer the account is locked once its owner has an own account. An existing account '
         'only gets its groups updated; its password is never changed.'],
        [], [('/var/lib/edukasaun-desktop/default-user', 'marks an account made by this command')],
        ['useradd(8)', 'chpasswd(8)']),
    'eduka-desktop-session': (
        'start an Eduka-Desktop login session',
        ['[**--wayland**]'],
        ['**eduka-desktop-session** is started by the display manager for the Eduka-Desktop session '
         '(/usr/share/xsessions/edukasaun-desktop.desktop). It applies the language chosen on the login screen, '
         'makes sure LXQt knows a window manager and starts LXQt with **startlxqt**; LXQt then starts '
         'Eduka-Panel and Eduka-Desktop from /etc/xdg/autostart.'],
        [('--wayland', 'Start LXQt on Wayland (startlxqtwayland). For tests only; not offered on the login screen.')],
        [('/var/lib/edukasaun-desktop/login/language', 'language chosen on the login screen'),
         ('~/.config/lxqt/session.conf', 'LXQt session settings (window manager)')],
        ['startlxqt', 'lxqt-session', 'eduka-panel']),
    'eduka-lxqt-repair': (
        'start again with the LXQt defaults',
        [''],
        ['**eduka-lxqt-repair** moves ~/.config/lxqt to ~/.config/lxqt.backup-*DATE-TIME*, so LXQt uses its '
         'defaults at the next login. It repairs accounts that ask for a window manager or look unthemed after '
         'a broken LXQt configuration. It is also found in Eduka-Settings, Maintenance.'],
        [], [('~/.config/lxqt/', 'LXQt settings of this account')],
        ['lxqt-session', 'eduka-settings']),
    'eduka-panel-reset': (
        'restore the default Eduka-Desktop settings',
        ['[**--all**]'],
        ['**eduka-panel-reset** restores the default settings of Eduka-Desktop, Eduka-Panel and the menu for '
         'this account and restarts a running Eduka-Panel. A copy of ~/.config/eduka-desktop is kept first. '
         'The agenda, favorites, pinned applications and saved notifications stay.'],
        [('--all', 'Start again from an empty settings folder (after the copy).')],
        [('~/.config/eduka-desktop.backup-*DATE-TIME*', 'copy of the old settings')],
        ['eduka-settings', 'eduka-panel']),
    'eduka-session-action': (
        'leave screen of Eduka-Desktop: lock, log out, restart, shut down',
        ['[**lock** | **logout** | **restart** | **shutdown**]', '**--now** *ACTION*'],
        ['**eduka-session-action** dims the desktop and shows the four actions as large buttons. The chosen '
         'action runs after a short countdown, so one wrong click in a classroom never powers a computer off; '
         'Escape or a click on the dim area cancels. With an action as argument that action is preselected.'],
        [('--now ACTION', 'Run lock, logout, restart or shutdown at once (through lxqt-session, else systemd).')],
        [], ['lxqt-leave', 'loginctl', 'eduka-panel']),
    'edukasaun-desktop-menu-open': (
        'open or close the Eduka-Desktop menu',
        [''],
        ['**edukasaun-desktop-menu-open** runs **eduka-menu --toggle**. Keyboard shortcuts and older menu entries '
         'use it.'],
        [], [], ['eduka-menu']),
}


def dash(text):
    return text.replace('-', '\\-')


def roff(text):
    """Escape for roff and turn **bold** / *italic* into fonts."""
    text = text.replace('\\', '\\e')
    def mark(m, font):
        return f'\\f{font}' + m.group(1).replace('-', '\\-') + '\\fR'
    text = re.sub(r'\*\*(.+?)\*\*', lambda m: mark(m, 'B'), text)
    text = re.sub(r'\*(.+?)\*', lambda m: mark(m, 'I'), text)
    return text


def line(text):
    out = roff(text)
    return '\\&' + out if out[:1] in ('.', "'") else out


def release():
    control = (ROOT / 'DEBIAN/control').read_text(encoding='utf-8')
    version = re.search(r'^Version: *(\S+)', control, re.M).group(1)
    shown = re.search(r'^VERSION = "(.*)"', (ROOT / 'usr/lib/edukasaun-desktop/eduka_common.py').read_text(encoding='utf-8'), re.M).group(1)
    date = 'October 2026'
    changelog = ROOT / 'packaging/changelog'
    if changelog.exists():
        m = re.search(r'^ -- .*?  \w{3}, +(\d+) (\w{3}) (\d{4})', changelog.read_text(encoding='utf-8'), re.M)
        if m:
            months = dict(Jan='January', Feb='February', Mar='March', Apr='April', May='May', Jun='June', Jul='July',
                          Aug='August', Sep='September', Oct='October', Nov='November', Dec='December')
            date = f'{months.get(m.group(2), m.group(2))} {m.group(3)}'
    return version, shown, date


def page(name, data, shown, date):
    summary, synopsis, description, options, files, see_also = data
    out = [f'.TH {dash(name.upper())} 1 "{date}" "Eduka-Desktop {shown}" "Edukasaun OS"',
           '.SH NAME', f'{dash(name)} \\- {roff(summary)}', '.SH SYNOPSIS']
    for i, syn in enumerate(synopsis):
        if i:
            out.append('.br')
        out.append(f'\\fB{dash(name)}\\fR {roff(syn)}'.rstrip())
    out.append('.SH DESCRIPTION')
    for i, para in enumerate(description):
        if i:
            out.append('.PP')
        out.append(line(para))
    if options:
        out.append('.SH OPTIONS')
        for opt, text in options:
            words = opt.split(' ', 1)
            head = f'\\fB{dash(words[0])}\\fR' + (f' \\fI{words[1]}\\fR' if len(words) > 1 else '')
            if ', ' in opt:
                head = ', '.join(f'\\fB{dash(o)}\\fR' for o in opt.split(', '))
            out += ['.TP', head, line(text)]
    if files:
        out.append('.SH FILES')
        for path, text in files:
            out += ['.TP', f'\\fI{roff(path)}\\fR', line(text)]
    out += ['.SH LICENSE',
            'Eduka-Desktop is free software under the GNU General Public License, version 3 or later. '
            'See /usr/share/doc/edukasaun-desktop-menu/copyright.']
    if see_also:
        out.append('.SH SEE ALSO')
        refs = []
        for ref in see_also:
            name_, _, section = ref.partition('(')
            refs.append(f'\\fB{dash(name_)}\\fR({section.rstrip(")") or "1"})')
        out.append(', '.join(refs))
    return '\n'.join(out) + '\n'


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    target = Path(argv[1])
    target.mkdir(parents=True, exist_ok=True)
    _, shown, date = release()
    missing = sorted(p.name for p in (ROOT / 'usr/bin').iterdir() if p.is_file() and p.name not in PAGES)
    if missing:
        print('No manual page for: ' + ', '.join(missing), file=sys.stderr)
        return 1
    for name, data in PAGES.items():
        (target / f'{name}.1').write_text(page(name, data, shown, date), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
