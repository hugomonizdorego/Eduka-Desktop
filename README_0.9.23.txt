Edukasaun Desktop Suite 0.9.23

All included components use the same version number:
- Eduka-Desktop 0.9.23
- Eduka-Panel 0.9.23
- Eduka-Menu 0.9.23
- Eduka-Settings 0.9.23

Changes in this patch:
- Eduka-Desktop: application tiles keep one size and one gap and start in the top-left corner, so a category with only a few applications no longer spreads them across the whole screen (seen on all-in-one computers). "All" fits as many columns as the width allows and never shows a sideways scroll bar.
- Effects: the pointer effect of the categories now also plays on the application tiles (Wave, Glow, Slide and the new Pop and Bounce); clicking a tile plays the opening effect. New options in Eduka-Settings → Effects: Speed (slow, normal, fast), Size (small, normal, big) and Random effects; Application tiles: tile size (small, normal, large).
- White right-click menu of the desktop (LXQt / pcmanfm-qt) fixed: when the Qt colors in lxqt.conf have text and background (almost) the same color, Eduka-Panel and Eduka-Settings write a complete readable palette for the current theme. Leaving a dark or multi-color theme always ends with readable colors.
- Eduka-Panel no longer closes on an error: a Python error in a button or timer is written to ~/.cache/eduka-desktop/eduka-panel-errors.log and the panel keeps running (the same for Eduka-Desktop and Eduka-Settings); a real crash writes its trace to the same file.
- Eduka-Desktop that stopped answering is detected (heartbeat): the next click on the start button replaces it, so logging out is no longer needed to open Eduka-Desktop again.
- Eduka-Panel: the time and date (and the "Action Center" label) are sized to the real height of the panel and the system font, so they are never cut at the top or bottom; the panel items get a little more height.
- Tetun language pack: with eduka-language-pack-tet installed, choosing Tetun in Eduka-Settings → Language & Startup sets LANGUAGE=tet:pt:en for the LXQt session, so every program with a Tetun translation uses it after logging out and in; a system set to Tetun is recognised by Eduka directly.
- Translations for Portuguese, Indonesian and Tetun of the new texts.
- A welcome screen is planned for 0.10.0 (design concept).

Error logs: ~/.cache/eduka-desktop/eduka-panel-errors.log, eduka-menu-errors.log, eduka-settings-errors.log.
The Tetun check against the Timor Aid dictionary follows when www.timoraid.org can be reached from the build environment.
Development continues toward 0.10.0 and the final version 1.1.12 (November 2026).
