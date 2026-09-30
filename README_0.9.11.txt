Edukasaun Desktop Suite 0.9.11

All included components use the same version number:
- Eduka-Desktop 0.9.11
- Eduka-Panel 0.9.11
- Eduka-Menu 0.9.11
- Eduka-Menu-Settings 0.9.11

Changes in this patch:
- Eduka-Desktop: search now covers every application instead of only the selected category.
- Eduka-Desktop: the search box is focused when the menu opens; Enter opens the first result and Escape clears the search or closes the menu.
- Eduka-Desktop: the search is cleared when the menu hides, so it always reopens on the category view.
- Eduka-Desktop: the 35 ms command poll only parses the command file when it changes.
- Eduka-Desktop: Open Containing Folder works for paths with spaces.
- Eduka-Panel: only one panel runs per session; Restart Eduka-Panel waits for the old panel to exit.
- Eduka-Panel: the application list is kept in memory and window types are cached, reducing CPU use on every taskbar refresh.
- Eduka-Panel: re-layouts automatically when the screen resolution changes or a projector is connected.
- Eduka-Panel: the keyboard indicator shows the active layout instead of a fixed EN.
- Eduka-Panel: scrolling over the volume icon stays within 0-100 %.
- Eduka-Panel: the two-line clock fits the default panel height; pinned apps offer Remove from Favorites.
- Eduka-Menu-Settings: pages scroll on small screens and the window sizes itself to the display.
- Eduka-Menu-Settings: Apply shows an inline confirmation instead of a dialog; Ctrl+S applies.
- Eduka-Menu-Settings: "Preload Eduka-Desktop at login" and the language option are now saved and honored.
- Eduka-Menu-Settings: Reset to Defaults refreshes the form instead of closing and keeps favorites and pinned apps.
- Eduka-Menu-Settings: live Icon & Name preview, a Default icon button and clearer Maintenance actions.
- Eduka-Menu-Settings: value ranges match what Eduka-Panel and Eduka-Desktop accept; leaving Liquid Glass restores Low resource mode.
- Shutdown and Restart use lxqt-leave confirmation first and fall back to systemctl only when it is missing.
- Runtime state is only written to disk when a value actually changes.

Development continues toward Final Version 1.1 in November 2026.
