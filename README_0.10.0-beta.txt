Edukasaun Desktop Suite 0.10.0 Beta

All included components use the same version number:
- Eduka-Desktop 0.10.0 Beta
- Eduka-Panel 0.10.0 Beta
- Eduka-Menu 0.10.0 Beta
- Eduka-Settings 0.10.0 Beta
(Debian package version 0.10.0~beta3 = 0.10.0 Beta, update 3)

Changes in update 3:
- The version stays 0.10.0 Beta; only the Debian package version goes up (0.10.0~beta3).
- Licenses and credits: Edukasaun Desktop is free software under the GNU GPL version 3 or later (LICENSE file, SPDX line in every source file). The Debian copyright file /usr/share/doc/edukasaun-desktop-menu/copyright lists every part with its license: Orchis and Graphite (GPL-3), Yaru-remix (GPL-3 and CC BY-SA 4.0), Noto Emoji (Apache-2.0), Natural Earth (public domain). About Edukasaun Desktop shows the license and thanks Openbox, xfwm4, SDDM, NetworkManager, BlueZ/Blueman, PulseAudio/PipeWire, UDisks, Orca, Qt, PyQt5 and Python as well; the LXQt license is given correctly (LGPL-2.1+, GPL-2.0+).
- LXQt and Debian 13:
  - Eduka-Panel and Eduka-Desktop start as LXQt modules: lxqt-session starts them again if one crashes, and they can be stopped and started in LXQt's session settings. In a plain LXQt session they quit at once, so LXQt keeps its own panel, menu and notifications.
  - The package scripts no longer stop running programs, start programs as root or write into home folders. After an update Eduka-Panel and Eduka-Desktop start again by themselves (from this version on; after updating from update 2 or older, log out and in once).
  - The files in /etc are configuration files of the package now: an unchanged file is updated without a question, a changed one is kept.
  - Removing the package gives plain LXQt sessions their notification daemon back.
  - Debian changelog and manual pages for all 14 commands (man eduka-panel, man eduka-settings, ...); lintian reports no errors or warnings.
  - Dependencies for Debian 13: Qt SVG support (icons), lxqt-session, dbus-bin and the X11 tools that are used; lxqt-config, lxqt-admin, lxqt-policykit, lxqt-qtplugin, NetworkManager and the Qt 6 on-screen keyboard of the login screen are recommended.
  - The package is smaller (about 1 MB instead of 4 MB): the design pictures are no longer installed.
- Window managers and compositors:
  - Openbox: the window border theme is written to the file Openbox really reads (~/.config/openbox/rc.xml with LXQt 1.x and 2.x, or the file it was started with).
  - xfwm4: no more square shadow around the round, see-through Eduka-Panel.
  - Checked with Openbox + picom and with xfwm4 and its own compositor.
- Themes:
  - Liquid Glass: the Action Center and the panel popups use the blue of the theme (they were green); the glass is less see-through over a dark wallpaper, so text stays readable.
  - Icons: light themes now use Papirus-Light, whose status icons (Wi-Fi, sound, battery) are dark; with plain Papirus they were light grey and hard to see on the light Eduka-Panel. Dark themes keep Papirus-Dark.
  - The "Action Center" label on the panel clock is readable on every theme and wallpaper.
  - Login screen, light styles: the clock, the date and the user names have a deeper shadow, so they stay readable on a light picture.
- Security:
  - Switching automatic login on or off always asks for an administrator password (its own polkit action), also for administrators who change the look of the login screen without a password; it is only possible for normal user accounts.
  - The login screen helper copies pictures safely (the file cannot be swapped during the copy).
  - Programs from the application list are started without a shell, as the desktop entry rules say.
  - Eduka keeps its runtime files in a private folder.
- Bug fixes:
  - Close on the task bar asks the window to close (a forced kill could lose unsaved work); Force Close is still in the right-click menu.
  - Eduka-Desktop (the start menu) no longer opens by itself after login.
  - Application list: translated names, OnlyShowIn/NotShowIn, TryExec, Terminal= and Path= of the desktop entries are used; your own entries in ~/.local/share/applications win.
  - Software OpenGL is only used in virtual machines and without 3D graphics, so games and videos are faster on real computers. The WebGL fallback is only given to Scratch 3 and TurboWarp.
  - Task bar names: a window no longer gets the name of another program because of a similar word (seen with "Reset settings") or because both run with python3.
  - The Wired switch works with several network ports; system disks inside LUKS or LVM are never offered for ejecting; names of USB sticks are cleaned before they are used in desktop links.
  - The weather can be switched off (Eduka-Settings, Clock); the town now comes from one service (GeoJS).
  - Battery: only real batteries are shown (not those of a wireless mouse).
  - Parental Control: the password window shows above the lock screen.
  - eduka-panel-reset keeps a copy of the old settings and the agenda, favorites and pinned applications.
- Translations for Portuguese, Indonesian and Tetun of the new texts.

Changes in update 2:
- The version stays 0.10.0 Beta for Eduka-Desktop, Eduka-Panel, Eduka-Menu and Eduka-Settings; only the Debian package version goes up (0.10.0~beta2), so apt installs this update over 0.10.0~beta1.
- Eduka-Pastel redone in soft mint green and sky blue instead of orange (coral), after the pastel dashboard design, with cute colored badges and raised round cards:
  - Eduka-Desktop: mint category column; every category has its own pastel badge color, the chosen category is a raised pill in its own color; the application cards fade into their own pastel color and get stronger under the pointer.
  - Eduka-Panel: soft mint bar, sky blue start button, mint highlights; Action Center tiles in mint, sky blue, butter, lilac, rose and aqua, raised, deeper color when on; weekend days in rose.
  - Eduka-Settings, popups, menus, tooltips, dialog boxes, About and the leave screen in the same colors.
  - GTK 2/3/4 programs: the Eduka-Pastel GTK theme was rebuilt from Orchis (green variant) with mint surfaces and a mint green accent; checked with the GTK 3 and GTK 4 widget factories. Window borders (Openbox, xfwm4) and Qt colors follow.
  - Login screen (SDDM Pastel style): sky blue to mint background, mint accent.
- Raised look without drawing errors: the soft shadow line under round cards (which Qt drew with small tails at the corners) was replaced by a soft color fade and a clean outline.
- Eduka-Panel applies the theme once after each package update (also when only the package version changes), so the new colors come at the next login.
- Bug check: all programs were run again on every theme (panel popups, Action Center, Eduka-Desktop, every Eduka-Settings page): no errors.
- Translations for Portuguese, Indonesian and Tetun of the new texts.
- Development continues (slow ring) toward the final version 1.1.12 (November 2026).

Changes in the first 0.10.0 Beta package (0.10.0~beta1):
- New theme Eduka-Pastel, now the default theme (its first colors: warm cream surfaces, a soft mint sidebar, coral buttons and big round cards with a soft shadow line, after the pastel school dashboard design; in update 2 mint green and sky blue). It covers everything:
  - Eduka-Desktop: mint category column with a white pill for the chosen category, pastel color badges, white rounded application cards, round search field and pill buttons.
  - Eduka-Panel: cream bar, coral pill start button, peach highlights; the Action Center tiles are soft pastel cards (mint, peach, butter, sky, lilac, rose).
  - Eduka-Settings: mint sidebar with a white pill for the open page, rounded cards and coral buttons.
  - Popups, menus, tooltips, dialog boxes, About and the leave screen.
  - GTK programs: new GTK theme Eduka-Pastel (Orchis with coral accent and cream surfaces, by vinceliuice, GPL-3.0), window borders, Qt colors and a new Pastel style for the login screen (SDDM, now the default there too).
- Icons: with the theme, Papirus (light themes) or Papirus-Dark (dark themes) is used for LXQt, GTK and Eduka, so all icons have one style. Choosing another icon theme in Eduka-Settings keeps that choice. Every icon name Eduka uses was checked against Papirus.
- Bug fixes: the pastel colors of Eduka-Desktop no longer fall back to the old colors after the menu was closed or a tile was pointed at.
- Versions: this is 0.10.0 Beta (Debian package 0.10.0~beta1). From now on development is slower (slow ring): fewer changes, more checking.
- Translations for Portuguese, Indonesian and Tetun of the new texts.

The Tetun check against the Timor Aid dictionary follows when www.timoraid.org can be reached from the build environment.
Development continues slowly (slow ring) toward the final version 1.1.12 (November 2026).
