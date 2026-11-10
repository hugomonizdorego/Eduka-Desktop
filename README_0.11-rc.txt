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
