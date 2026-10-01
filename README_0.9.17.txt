Edukasaun Desktop Suite 0.9.17

All included components use the same version number:
- Eduka-Desktop 0.9.17
- Eduka-Panel 0.9.17
- Eduka-Menu 0.9.17
- Eduka-Settings 0.9.17

Changes in this patch:
- One account for the live system and the ISO: edukasaun / edukasaun, now an administrator (group sudo), so every "Authentication required" prompt asks for the edukasaun password instead of root. live-config uses the same account (no second "user" account). After installation the installer creates the owner's own account; the live account edukasaun is then locked and hidden from the login screen (its files are kept).
- Eduka-Menu Settings is now Eduka-Settings (eduka-settings; the old command still works). It configures everything: General (language), Appearance (theme, icons, mouse cursor), Eduka-Desktop, Eduka-Panel (start button, panel, clock), Notifications, Accessibility, Login Screen and Maintenance.
- New mouse cursor chooser: any installed cursor theme and size, applied to LXQt, GTK and X (new windows at once, everything after logging in).
- Language setting (System, English, Bahasa Indonesia, Tetun, Português) for greetings such as "Selamat pagi / siang / sore / malam" in Eduka-Desktop, the Action Center and the leave screen.
- Action Center redesigned: the double date is gone; a large clock in the middle (digital or analog, 24 or 12 hours with AM/PM, right-click to switch) with a greeting in the chosen language. The handle at the top really resizes now: drag down to fold the month calendar away, drag up to show it; the choice is remembered and the Action Center always stays above the panel (also on 1366x768).
- Smart network tile: shows the Wi-Fi name and signal when on Wi-Fi, a LAN socket with a blinking green light on a cable, a red light when offline; hovering shows "Network not connected" (in the chosen language). The same picture is used in the tray. Clicking opens the network list.
- Lock, Log Out, Restart and Shut Down are now in the Action Center (removed from Eduka-Desktop, where only About remains, in the corner). They open the new Eduka leave screen (large round buttons, 30 s countdown, Esc cancels) instead of LXQt's plain dialog.
- Eduka-Panel is the notification server of Eduka-Desktop sessions: LXQt's notification daemon is stopped and every notification appears as an Eduka bubble above the panel (actions, urgent notifications stay, hover keeps it open), goes to the history and can be silenced with Do Not Disturb (Action Center tile, Notifications popup or Eduka-Settings). Duration and history are set in Eduka-Settings → Notifications, with a test button.
- Login Screen page: live preview that changes at once, status of the active SDDM theme and greeter, and automatic saving for administrators (polkit rule, no password per change). Saving also makes sure SDDM really uses the Edukasaun theme (/etc/sddm.conf.d/zz-edukasaun-theme.conf and /etc/sddm.conf) and marks the theme QtVersion=6 when only the Qt 6 greeter is installed (SDDM 0.21).
- Login screen pre-fills a user only when that account is listed by SDDM (no locked live account after installation).

Development continues toward Final Version 1.1.25.
