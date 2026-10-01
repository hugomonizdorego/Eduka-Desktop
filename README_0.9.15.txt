Edukasaun Desktop Suite 0.9.15

All included components use the same version number:
- Eduka-Desktop 0.9.15
- Eduka-Panel 0.9.15
- Eduka-Menu 0.9.15
- Eduka-Menu-Settings 0.9.15

Changes in this patch:
- Action Center: one sound control. The speaker button mutes/unmutes and shows the state, the slider sets the volume, the chevron opens the output device list and Sound Settings. The separate Mute tile and Sound button are gone; brightness sits directly below the volume. A Display tile opens monitor settings.
- Brightness works on every computer: laptops use the backlight (brightnessctl/xbacklight); desktops, projectors and VirtualBox without a backlight are dimmed with xrandr (never below 30 %) and the level is restored at the next login.
- Modern Action Center calendar: month title, Today button, round chevrons, today as an accent circle, the selected day as a ring, faded days of other months.
- Spin boxes and combo boxes show clear up/down and drop-down arrows in Eduka-Menu-Settings and the panel popups.
- Eduka-Desktop: the black tooltip over application tiles is removed (the name is already on the tile); tooltips elsewhere follow the theme.
- Eduka-Desktop: every time the pointer enters a category or an application tile it gets a new random color from the palette, so the colors keep changing.
- New visual theme Edukasaun-Dark for Eduka-Panel, Action Center, popups, menus, Eduka-Desktop and Eduka-Menu-Settings, using the Orchis dark colors by vinceliuice (github.com/vinceliuice/Orchis-theme, GPL-3.0) with the Orchis teal accent.
- Icon theme chooser in Eduka-Menu-Settings → Appearance: any installed icon theme can be used for the whole desktop (LXQt, GTK applications and Eduka); there is no forced default.
- Login screen: new Edukasaun SDDM theme (no Debian text). The background is /usr/share/Edukasaun/SDDM/Default.png (replace the file to change it; a soft green gradient is shown when it is missing) and the logo /usr/share/Edukasaun/Logo/Edukasaun Logo.png.
- Live session: SDDM (and LightDM) log straight into Eduka-Desktop without user name or password (eduka-live-autologin.service, only when booted with boot=live; removed again on installed systems).
- Standard account: while the ISO is built (no personal account yet) the package creates the user edukasaun with the password edukasaun; the login screen pre-fills edukasaun. On other systems run 'sudo eduka-default-user'.
- Fixed Eduka-Desktop theme switching leaving parts of the old theme in place.

Development continues toward Final Version 1.1.25.
