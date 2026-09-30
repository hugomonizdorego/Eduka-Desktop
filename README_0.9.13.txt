Edukasaun Desktop Suite 0.9.13

All included components use the same version number:
- Eduka-Desktop 0.9.13
- Eduka-Panel 0.9.13
- Eduka-Menu 0.9.13
- Eduka-Menu-Settings 0.9.13

Changes in this patch:
- Fixed: logging in showed "Welcome to LXQt - choose your window manager" and the theme broke. The 0.9.12 session launcher set XDG_CONFIG_DIRS, which stops startlxqt from adding LXQt's default configuration (window manager, theme, icons). The launcher no longer touches it.
- The session launcher now also fills in a missing LXQt window manager (openbox, kwin_x11, xfwm4, ...) so the chooser never appears; a window manager the user picked is never changed.
- New "Repair LXQt theme and session" action in Eduka-Menu-Settings → Maintenance (and eduka-lxqt-repair) for accounts that already logged in with 0.9.12. Old settings are kept as a backup.
- SDDM: the session is listed as "Eduka-Desktop" (X11) and "Eduka-Desktop Wayland", and Eduka-Desktop is preselected when SDDM has no remembered session, a removed one, or the plain LXQt session. LightDM keeps Eduka-Desktop as default.
- LXQt: Eduka-Panel asks lxqt-session to stop lxqt-panel only inside Eduka-Desktop sessions; a plain LXQt session keeps its panel. LXQt Logout/Shutdown/Reboot/Lock/About launchers that Eduka-Desktop already provides are hidden from the application list.
- Theme: Eduka-Desktop tiles, category list, popups and the Action Center follow the transparency and theme set in Eduka-Menu-Settings again; application colors are softer.
- Without a compositor, menus and popups use an opaque fallback so no black corners appear.
- Eduka-Panel: the taskbar reacts instantly to opened, closed and focused windows (event-driven through xprop -spy) instead of polling every 0.9 s.
- Eduka-Panel: while the Action Center is open, the tray icons (network, sound, Bluetooth, battery, keyboard, updates) move into it and return when it closes. Keyboard layout, printer and update status are shown inside the Action Center.
- Eduka-Panel: redesigned Sound popup (mute button, volume, output device selection) and Network popup (Wi-Fi switch, network list with signal, lock and connected state, password prompt, disconnect). Wi-Fi scans run in the background.
- Eduka-Panel: Show Desktop corner button and middle-click on a task or pinned app to open a new window.
- Wayland support stays available as a preview through Suggests (lxqt-wayland-session, labwc) and is no longer pulled in by default.

Development continues toward Final Version 1.1.25.
