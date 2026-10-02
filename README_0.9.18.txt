Edukasaun Desktop Suite 0.9.18

All included components use the same version number:
- Eduka-Desktop 0.9.18
- Eduka-Panel 0.9.18
- Eduka-Menu 0.9.18
- Eduka-Settings 0.9.18

Changes in this patch:
- Fixed (serious): with Eduka-Settings open, the taskbar showed "Eduka-Update-System" with its icon. Eduka's own windows are now recognised by name, and generic words such as "Eduka", "Settings" or "System" no longer decide which application a window belongs to.
- Eduka-Settings redesigned: the sidebar is split into PERSONALIZE, DESKTOP and SYSTEM groups with dividers; every setting sits on its own row with a thin line between rows; themes are chosen from picture cards.
- New Eduka-Panel position: Bottom, Top, Left or Right (Eduka-Settings → Eduka-Panel, or right-click the panel → Panel Position). Left and right give a vertical panel with icons; the work area, popups, the Action Center and notification bubbles follow the edge.
- New Effects page for Eduka-Desktop (off until switched on, only on computers with 4 GB of memory and 4 CPU threads, never with Eduka-Low-Theme): pointer over a category - Wave, Glow or Slide; opening an application - Bubbles, Zoom in, Zoom out, Ripple, Bounce, Confetti or Fade.
- Action Center: clicking the chevron or the handle now really shows and hides the month calendar (it used to work only while holding the mouse button, because the calendar did not fit and was folded away again). When space is short the calendar becomes smaller and the latest-notification line steps aside.
- New clock options: Digital, Analog and LED (seven segments, seven colors), seconds on/off and a blinking colon; right-click the clock or use Eduka-Settings → Clock.
- Click the clock in the Action Center: a rotating Earth with day and night appears; drag it to turn it (map: Natural Earth, public domain).
- Sound in the Action Center: every application playing sound (VLC, SMPlayer, Celluloid, Audacious, Rhythmbox, Spotify, YouTube or films in Firefox/Chromium, ...) gets its own row with mute, volume and play/pause (MPRIS) without opening the player.
- LXQt's black notification bubbles are gone: Eduka-Panel keeps the notification service for the whole session, LXQt's notification daemon is switched off for Eduka-Desktop accounts (autostart override) and ended if it still starts.
- Eduka-Panel right-click menu redesigned: Panel Position, Taskbar Buttons, Show Desktop, Panel Settings and Restart Eduka-Panel (Open Eduka-Desktop, Rebuild App Cache, Lock and Leave were removed; they live in the start button and the Action Center).
- Window buttons (minimize, maximize, close) are clearly visible in the dark themes: new xfwm4 and Openbox borders with fixed colors, round buttons and a red close button (the Orchis xfwm4 files used GTK colors that LXQt cannot provide, so the white buttons sat on a light title bar).
- New theme Eduka-Low-Theme for very low spec computers, built from Yaru-remix (Muqtxdir; GTK 2/3/4 GPL-3.0, assets CC BY-SA 4.0): flat and opaque, no transparency, no compositor (picom not started, xfwm4 compositing off), no effects.
- New theme Eduka-Transparan after Transparent-Shell-Theme (mrbrownstone07): smoky dark glass for Eduka-Panel, Eduka-Desktop, the Action Center and popups; GTK applications use Edukasaun-Dark; falls back to Edukasaun-Dark without a compositor.

Development continues toward Final Version 1.1.25.
