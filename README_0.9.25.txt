Edukasaun Desktop Suite 0.9.25

All included components use the same version number:
- Eduka-Desktop 0.9.25
- Eduka-Panel 0.9.25
- Eduka-Menu 0.9.25
- Eduka-Settings 0.9.25

Changes in this patch (last 0.9 patch):
- One look for the whole desktop: every Eduka theme now brings its own GTK theme (GTK 2, 3 and 4 / libadwaita), Qt colors (with the Fusion style, which draws them exactly), the LXQt light or dark theme and the window borders (Openbox and xfwm4). Eduka-Default-Theme and Liquid Glass got their own GTK themes, Eduka-Default and Eduka-Liquid (Orchis teal and blue, light, by vinceliuice, GPL-3.0), and their own window borders, so no window or dialog box keeps an old look.
- The chosen accent color also marks selections in Qt programs.
- Dialog boxes of Eduka (messages, questions, input boxes, file and color choosers), right-click menus, tooltips, the About window and the leave screen use the colors of the theme (light and dark).
- After this update Eduka-Panel applies the theme once by itself, so the new system part is used at the next login without opening Eduka-Settings. When ~/.config/openbox/lxqt-rc.xml is missing, it is created from the system file so the window borders can follow the theme. A GTK 4 style of your own (~/.config/gtk-4.0/gtk.css) is never replaced.
- Theme changes only write the values that really change (no needless reloads of Eduka-Panel).
- Action Center: when a tile is missing (no Bluetooth), the tiles of the last row stretch, so there is no hole.
- Network popup: the Wireless line shows the network that is connected.
- Bug check: a hidden error where a loop variable named "_" covered the translation function was fixed in Eduka-Desktop, Eduka-Panel and Eduka-Settings; all programs were run on every theme without errors.
- Translations for Portuguese, Indonesian and Tetun of the new texts.
- 0.9.25 is the last 0.9 patch; the next version is the 0.10.0 beta.

The Tetun check against the Timor Aid dictionary follows when www.timoraid.org can be reached from the build environment.
Next: 0.10.0 beta, then the final version 1.1.12 (November 2026).
