Edukasaun Desktop Suite 0.9.16

All included components use the same version number:
- Eduka-Desktop 0.9.16
- Eduka-Panel 0.9.16
- Eduka-Menu 0.9.16
- Eduka-Menu-Settings 0.9.16

Changes in this patch:
- Eduka-Menu-Settings redesigned: sidebar navigation and rounded cards that follow the chosen theme (Eduka-Default-Theme, Liquid Glass, Edukasaun-Dark), themed check boxes, clear arrows, a status line instead of pop-up dialogs.
- Fixed Reset to Defaults: Eduka-Desktop now really returns to the defaults (Grid layout, Edukasaun section, size, theme, search and colors), together with Eduka-Panel, the menu button and the desktop theme. Favorites, pinned applications and the login screen are kept.
- Apply takes effect immediately: the visual theme (also for GTK/Qt applications and window borders), the icon theme, the compositor mode, Eduka-Panel and Eduka-Desktop are all updated at once, without logging out.
- New Login Screen page in Eduka-Menu-Settings for SDDM: style (follow the desktop theme, light, dark or glass), accent color, title, clock, background picture (own picture, desktop wallpaper or the default gradient), logo, pre-filled user and optional automatic login, with a Preview button. Changes are written by a small checked helper (pkexec, administrator password).
- Edukasaun-Dark (Orchis dark by vinceliuice, GPL-3.0) is now a real system theme: the GTK 2/3/4, xfwm4 and Openbox themes are installed in /usr/share/themes/Edukasaun-Dark, and choosing Edukasaun-Dark switches GTK applications, the Qt palette and window borders; switching back restores the previous settings.
- Liquid Glass redesigned to be smoother: soft milky glass, gentle highlight and thin light rim (after github.com/ryohsuke1231/liquid-glass). Optional real background blur behind Eduka-Panel and Eduka-Desktop (picom glx, off by default, falls back automatically). Liquid Glass now runs on computers with 2 GB of memory.
- Eduka-Desktop refreshed: greeting header, search box with icon, Grid/List switch, a footer with File Manager, Terminal and Settings on the left and round About, Lock, Logout, Restart and Shut Down buttons on the right.
- Eduka-Panel refreshed: accent start button, flat task buttons with an accent indicator for the active window, cleaner tray. Still plain stylesheets, light enough for 2 GB / 2017 computers.
- Action Center: drag the handle at the top (or use the chevron, or scroll on the clock) to switch between the full view with the month calendar and a compact view that shows only today's date. The choice is remembered; when the screen is too small the compact view is used automatically, and the Action Center always stays above the panel.
- Notifications: Eduka-Panel keeps a history of desktop notifications (the bell shows a badge with the number of unread ones). The Notifications popup lists them with dismiss and Clear all; the latest one is also shown in the Action Center.
- Eduka-Panel follows settings changes reliably (the settings file watch is renewed after each save) and refreshes the icon theme and launcher icons.
- New login screen design (SDDM, Qt 5 and Qt 6 greeters): large clock, card with logo and user initial, password field with a login arrow, Caps Lock hint, panel-style bottom bar with restart and shut down buttons; light, dark and glass styles with a selectable accent color.
- Live session autologin is also written into the [Autologin] section of /etc/sddm.conf (live-config writes one there and SDDM reads it last), so the live system always logs straight into Eduka-Desktop.

Development continues toward Final Version 1.1.25.
