Edukasaun Desktop Suite 0.11 RC3 (release candidate 3)

All included components use the same version number:
- Eduka-Desktop 0.11 RC3
- Eduka-Panel 0.11 RC3
- Eduka-Menu 0.11 RC3
- Eduka-Settings 0.11 RC3
- Eduka-Quick 0.11 RC3
(Debian package version 0.11.0~rc3 = 0.11 RC3, release candidate 3)

The full list of changes is in /usr/share/edukasaun-desktop/doc/HISTORY.txt;
the most important ones:

- Login screen (SDDM): new glass "bento" cards in the Eduka colors (sign
  in, clock, profile, system) with one-click Sleep, Restart and Shut Down
  and a rail for language, keyboard, on-screen keyboard and accessibility.
  LightDM greeters get the same glass look and are optional third-party
  programs, installed from Eduka-Settings.
- Leave screen: one click runs the action (no countdown, no small buttons).
- Eduka-Quick: see-through, movable (hold and drag), 4 to 12 slices,
  programs used most, right-click → Add to Eduka-Quick.
- Eduka-Panel: oval, rounded or square ends.
- Keyboard shortcuts of LXQt and Windows together, without clashes
  (Super+E, Super+D, Super+L, Super+arrows, Super+Shift+S, Ctrl+Shift+Esc,
  the volume and media keys …). List: Eduka-Settings → Keyboard → Shortcuts.
- Smart device detection (laptop, desktop, tablet, virtual machine) and
  Num Lock that follows it; display scale from 75 to 200 %.
- Fingerprint: all readers are found (with hints), the password is asked
  first (no waiting at the login screen), forgotten passwords can be
  replaced with the finger.
- Memory saver, memory warning, Maintenance → Memory with zram and earlyoom.
- Touch: three- and four-finger gestures, long press for menus, smooth
  scrolling in Firefox, on-screen keyboard on tablets.

Recommended settings and configuration (in addition to 0.11 RC2)
------------------------------------------------------------------
1. Packages for the ISO (Cubic chroot), Debian 13 with LXQt:
     apt install zram-tools earlyoom touchegg
   apt installs them by itself as recommended packages; leave them in.
   zram-tools and earlyoom keep computers with 2 to 4 GB of memory smooth;
   touchegg gives the touch and touchpad gestures.
2. Fingerprint login: install fprintd and libpam-fprintd (recommended
   packages), add a finger in Eduka-Settings → Login & Fingerprint →
   Fingerprint and switch on "Use the fingerprint". The password is asked
   first; for the finger leave it empty and press Enter (or the fingerprint
   button of the login screen), then touch the reader.
3. Display: Eduka-Settings → Display recommends a scale for the screen of
   each computer; 100 % for school laptops with 1366 x 768.
4. Shortcuts: everything is set at login. Teachers can untick a shortcut
   in Eduka-Settings → Keyboard → Shortcuts to free its key.
5. LightDM stays optional: SDDM with the new glass design is the default.

Everything else from 0.11 RC2 stays valid:

Edukasaun Desktop Suite 0.11 RC2 (release candidate 2)

All included components use the same version number:
- Eduka-Desktop 0.11 RC2
- Eduka-Panel 0.11 RC2
- Eduka-Menu 0.11 RC2
- Eduka-Settings 0.11 RC2
- Eduka-Quick 0.11 RC2 (new)
(Debian package version 0.11.0~rc2 = 0.11 RC2, release candidate 2)

0.11 RC2 is the second release candidate and close to the final stable
version. The full list of changes is in
/usr/share/edukasaun-desktop/doc/HISTORY.txt; the most important ones:

- Eduka-Settings opens on All Settings: every setting with a search box,
  in sections like a full desktop (Appearance, Eduka, Preferences,
  Hardware, Administration).
- New pages: Users (accounts, administrators, passwords, pictures), Fonts,
  Date & Time, LightDM, Privacy and Eduka-Quick; Accessibility rebuilt
  (Vision, Hearing, Screen Reader); Parental Control with recommendations
  by age and a break reminder.
- Action Center: Sync time (network time and the time zone of the place).
- Eduka-Quick: a round quick launcher on Super+Q (idea of Gnome-Pie).
- LightDM: slick-greeter and lightdm-gtk-greeter in the Edukasaun styles,
  set together with the same options as the SDDM login screen.

Recommended settings and configuration (in addition to 0.11 RC)
-----------------------------------------------------------------
1. Packages for the ISO (Cubic chroot), Debian 13 with LXQt:
     apt install accountsservice systemd-timesyncd
   apt installs them by itself as recommended packages; leave them in.
   For the magnifier: apt install magnus. For a firewall: apt install gufw.
2. Login screen: SDDM stays the default. A school that prefers LightDM:
     apt install lightdm slick-greeter        (or lightdm-gtk-greeter)
   then Eduka-Settings → Login & Fingerprint → LightDM → "Use LightDM at
   the next start", choose the greeter and the look ("Same look as SDDM"
   copies the SDDM settings) and press Save LightDM settings.
3. Accounts: make one account per teacher (Administrator) and per pupil or
   class (Standard) in Eduka-Settings → Users. Accounts that should not be
   on the login screen: switch off "Show on the login screen" (the person
   types the name). Keep at least two administrator accounts at school.
4. Time: keep "Set the clock automatically from the internet" on. With the
   Sync time button of the Action Center the clock and the time zone follow
   the internet; pupils need no password for it, only for changing the
   time zone by hand or setting the clock.
5. Parental Control: choose a recommendation (for example "Computer
   lesson at school") and press Save Parental Control. The break reminder
   also works without a time limit.
6. Accessibility: for pupils who use Orca, set the voice in Accessibility →
   Screen Reader → Voice (Try the voice, then Use this voice). Mono sound
   helps with one earphone or one speaker.
7. Eduka-Quick: Super+Q. Teachers can put the programs of a lesson on it
   (Eduka-Settings → Eduka-Quick → Program…).

Everything else from 0.11 RC stays valid:

Edukasaun Desktop Suite 0.11 RC (release candidate)

All included components use the same version number:
- Eduka-Desktop 0.11 RC
- Eduka-Panel 0.11 RC
- Eduka-Menu 0.11 RC
- Eduka-Settings 0.11 RC
(Debian package version 0.11.0~rc1 = 0.11 RC, release candidate 1)

0.11 RC is the release candidate of the final stable version. The full
list of changes is in /usr/share/edukasaun-desktop/doc/HISTORY.txt; the
most important ones:

- Login: lxqt-panel, LXQt's notification daemon and picom's own autostart no
  longer start in Eduka-Desktop sessions (Eduka-Panel replaces them and starts
  the compositor with Eduka's settings); no panel flash at login; the Super
  key opens Eduka-Desktop; a new account gets the Edukasaun wallpaper.
- Official Edukasaun OS logo on the MENU button, at the top of Eduka-Desktop
  (a click opens www.edukasaunos.tl), on the login screen and in About.
- Eduka-Settings: similar pages share one entry with tabs (11 entries instead
  of 17); new Touch Screen and Fingerprint pages.
- Edukasaun is the one menu for learning, science and games.
- Wallpapers: /usr/share/background/Edukasaun.
- Better X11 and Wayland support; smoother menu and dark theme.

LXQt and Eduka
--------------
Edukasaun Desktop Suite runs on the LXQt core: lxqt-session starts the
session; pcmanfm-qt draws the desktop icons and is the file manager; LXQt's
terminal, password windows (lxqt-policykit), runner (Alt+F2), shortcuts
(lxqt-globalkeys) and settings tools are used. The panel, start menu,
notifications, Action Center and settings are Eduka's own: lxqt-panel and
lxqt-notificationd are switched off in Eduka-Desktop sessions (the LXQt way,
an autostart entry with Hidden=true in ~/.config/autostart; removing the
package removes it again).

Recommended settings and configuration
--------------------------------------
For the ISO (Cubic chroot), with Debian 13 (stable) and LXQt:

1. Packages next to edukasaun-desktop-menu:
     apt install xfwm4 picom lxqt-globalkeys papirus-icon-theme \
         fprintd libpam-fprintd onboard network-manager-gnome blueman \
         qml6-module-qtquick-virtualkeyboard fonts-noto-color-emoji
   apt installs the recommended packages by itself; leave them in.
2. Window manager and compositor: xfwm4 (it composites by itself) on
   computers with 3D graphics; Openbox with picom (XRender) on old computers
   and in virtual machines. Keep Eduka-Settings → Appearance → Compositor on
   "Automatic". Eduka-Low-Theme is the lightest theme for very old computers
   (no transparency, no effects). `eduka-compositor` shows what runs.
3. Wallpapers: copy the Edukasaun pictures to /usr/share/background/Edukasaun
   and call the default one default.jpg (or default.png): new accounts get it
   at their first login, and every picture there is offered in
   Eduka-Settings → Wallpaper & Icons.
4. Login screen: the official logo is built in; a school can put its own
   logo at /usr/share/Edukasaun/Logo/Edukasaun Logo.png and the background at
   /usr/share/Edukasaun/SDDM/Default.png (or set both in Eduka-Settings →
   Login & Fingerprint).
5. Accounts: the administrator account edukasaun (password edukasaun) exists
   only while the ISO is built and for the live session. After installing,
   make a personal account for every teacher and pupil.
6. Fingerprint readers: `fprintd-list $USER` shows the reader. Every account
   adds its own fingers in Eduka-Settings → Login & Fingerprint. On computers
   shared by a class keep "Accept a finger at the login screen ..." off and
   use passwords; on a personal laptop switch it on (the password keeps
   working).
7. Touch screens: keep "Automatic" for the screen; with a projector the touch
   stays on the built-in screen. On tablets switch on "Start the on-screen
   keyboard (Onboard) at login" and press "Bigger buttons for fingers".
8. Sessions: only Eduka-Desktop is on the login screen (the plain LXQt and
   Openbox sessions are hidden on purpose). The Wayland session
   (eduka-desktop-session --wayland) is for tests only; use X11 at school.
9. Shortcuts: Super opens the menu, Ctrl+Alt+T the terminal, Alt+F2 the
   runner, Print a screenshot, Ctrl+Alt+L locks the screen.
10. Updates: install a new package with
      apt install ./edukasaun-desktop-menu_<version>_all.deb
    Eduka-Panel and Eduka-Desktop start again by themselves a few seconds
    later; your settings are kept.
11. Repair: Eduka-Settings → Maintenance (or eduka-panel-reset and
    eduka-lxqt-repair) puts an account back to the defaults; a copy of the old
    settings is kept.

Next: the final stable version (only bug fixes until then).
