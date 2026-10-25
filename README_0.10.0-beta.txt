Edukasaun Desktop Suite 0.10.0 Beta

All included components use the same version number:
- Eduka-Desktop 0.10.0 Beta
- Eduka-Panel 0.10.0 Beta
- Eduka-Menu 0.10.0 Beta
- Eduka-Settings 0.10.0 Beta
(Debian package version 0.10.0~beta2 = 0.10.0 Beta, update 2)

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
