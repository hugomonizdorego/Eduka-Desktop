Edukasaun Desktop Suite 0.9.14

All included components use the same version number:
- Eduka-Desktop 0.9.14
- Eduka-Panel 0.9.14
- Eduka-Menu 0.9.14
- Eduka-Menu-Settings 0.9.14

Changes in this patch:
- Fixed the black areas (panel corners, Eduka-Desktop frame, tooltips): X11 paints transparent windows black when no compositor runs. Eduka-Panel and Eduka-Desktop now make sure one runs before they open: xfwm4 and KWin composite themselves; with Openbox, picom is started (xrender backend, no shadows or fading; stable in VirtualBox).
- Without any compositor, Eduka-Panel, Eduka-Desktop, menus and popups use a clean opaque look instead of black, and switch back to transparent automatically when a compositor starts.
- Fixed "Welcome to LXQt - select your default window manager" again: the package fills a missing window manager in /etc/skel (live and new users) and in existing accounts, preferring xfwm4 (built-in compositor), then KWin, then Openbox. A window manager someone already chose is kept.
- Login screen: SDDM, LightDM and other greeters now list only "Eduka-Desktop". The LXQt, Openbox and labwc session entries are hidden with dpkg-divert (moved, not deleted; the programs stay installed; removing the package restores them). SDDM preselects and autologins into Eduka-Desktop.
- Removed the "Eduka-Desktop Wayland" login entry; labwc and lxqt-wayland-session are no longer suggested.
- Liquid Glass redesigned after the Liquid Glass look (github.com/ryohsuke1231/liquid-glass): clear glass with a bright specular top, light rim and soft base on the panel, Eduka-Desktop, buttons and popups. It is only used while a compositor runs, otherwise Eduka-Default-Theme is used, so it can never turn the desktop black.
- Removed the heavy drop-shadow effect from Liquid Glass that made the panel and Eduka-Desktop sluggish.
- Tooltips are opaque so they never appear as black boxes.
- Recommends xfwm4 | openbox and picom; Eduka-Desktop keeps working without them.

Development continues toward Final Version 1.1.25.
