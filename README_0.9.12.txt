Edukasaun Desktop Suite 0.9.12

All included components use the same version number:
- Eduka-Desktop 0.9.12
- Eduka-Panel 0.9.12
- Eduka-Menu 0.9.12
- Eduka-Menu-Settings 0.9.12

Changes in this patch:
- All right-click context menus (Eduka-Desktop, Eduka-Panel, Eduka-Menu-Settings, submenus and text fields) now have smooth rounded corners without square window edges.
- Eduka-Panel: new Action Center on the clock with time and date, Wi-Fi, Bluetooth, Airplane mode, Mute, Lock and Settings tiles, volume and brightness sliders, battery status, calendar and Network/Sound/Power shortcuts. Right-click a tile to open its settings.
- Eduka-Panel: network, sound, Bluetooth, printer and keyboard status is read in a background thread, so the panel no longer stutters while nmcli or pactl are slow.
- Eduka-Panel: status icons and the clock sit in one rounded tray group; the active task shows an accent underline; popups fade in and close with Escape.
- Eduka-Panel: taskbar refreshes reuse window-to-application matches and only relayout when the button order changes.
- Eduka-Panel: the Wi-Fi list no longer blocks the panel with a network rescan.
- Eduka-Desktop: every category shows its own color badge and every application tile its own soft color; neighbouring tiles never share a color, and a new palette is chosen each time the menu closes.
- Eduka-Desktop: the category list no longer shows a horizontal scrollbar.
- Eduka-Menu-Settings: the menu button picture size is set with a slider (16-64 px), wide pictures can keep their proportions, and the preview shows the picture at its real size on a panel of the chosen height.
- Sessions: login screens (LightDM, slick-greeter, lightdm-gtk-greeter, SDDM and others) now list "Eduka-Desktop (X11)" and "Eduka-Desktop (Wayland)". The Wayland entry only appears when lxqt-wayland-session is installed.
- Sessions: Eduka-Desktop (X11) is the default LightDM session; slick-greeter shows an Eduka-Desktop badge.
- LXQt: Eduka-Desktop sessions hide lxqt-panel through session-scoped XDG settings (a normal LXQt session is unchanged), and Eduka-Menu Settings appears in the LXQt Configuration Center.
- Wayland (preview): Eduka components run through XWayland so the panel and taskbar keep working; launched applications use native Wayland.

Development continues toward Final Version 1.1.25.
