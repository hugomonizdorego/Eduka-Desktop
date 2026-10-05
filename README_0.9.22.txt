Edukasaun Desktop Suite 0.9.22

All included components use the same version number:
- Eduka-Desktop 0.9.22
- Eduka-Panel 0.9.22
- Eduka-Menu 0.9.22
- Eduka-Settings 0.9.22

Changes in this patch:
- Eduka-Panel: a new icon for USB flash drives, memory cards and external hard disks / SSDs while they are plugged in. Clicking it opens a list with the name, kind, size and free space of each drive and the buttons Open, Eject and Safely remove (unmount and switch the drive off), plus File Manager. A notification says when a drive was connected and when it is safe to pull out. Disks of the system and the live USB are never listed or ejected.
- Eduka-Panel: when a touchpad is found, a small touchpad picture shows on the panel; it copies the finger (a dot with a short trail), left and right clicks and scrolling. Clicking it opens switches for touchpad on/off, tap to click, natural scrolling and turn off while typing.
- The drives and touchpad icons stay on Eduka-Panel while the Action Center is open.
- Clock on Eduka-Panel: a framed box sized to the time and date; pointing at it says "Click to open the Action Center". While the Action Center is open the box shows "Action Center — click to close" instead of the time (the time is in the Action Center), and the time comes back when it closes.
- Eduka-Settings → Wallpaper (new, replaces LXQt's desktop preferences): all pictures of /usr/share/Edukasaun/Backgrounds as tiles that grow a little under the pointer, a big preview, Zoom / Mosaic / Centered / Scaled / Stretched, a background color, "Add pictures…" and a slideshow of several chosen pictures (minutes, random order and fade speed).
- Eduka-Settings → Desktop Icons (new): Home, Trash, Computer, Network and plugged-in USB/HDD/SSD drives on the desktop, switched on and off at once.
- Eduka-Settings → Keyboard, Mouse and Touchpad (new section Devices): keyboard layouts and the switch key, key repeat delay and speed, Num Lock; pointer speed, left-handed, natural scrolling, middle click, double-click time with a test, wheel lines; touchpad on/off, tap to click, natural scrolling, turn off while typing, scrolling method, speed and a live touchpad picture.
- Eduka-Settings applies every change at once; Apply and Save & Close still work. The login screen and Parental Control keep their own Save button (they need an administrator password).
- New theme Eduka-MultiColor, built from the Graphite GTK theme (light) by vinceliuice (GPL-3.0): calm light grey for applications, a rainbow start button, and a different color for every menu category, Action Center tile, panel button and window button on the taskbar. The same multi-color look can be switched on for the other themes (Eduka-Settings → Appearance → Multi-color).
- Parental Control: emoji now show as pictures (Noto Emoji by Google, Apache-2.0), so they never appear as empty boxes; times from 5 minutes (5, 10, 15, 30 min, 1, 2, 3 hours) and a manual time in hours, minutes and seconds (1 minute to 24 hours). The time service checks more often near the end, so short limits are exact.
- About: credits for the Liquid Glass look (Ryosuke Watanabe, ryohsuke1231/liquid-glass, MIT), the Graphite GTK theme (vinceliuice, GPL-3.0) and Noto Emoji (Google, Apache-2.0).
- Translations for Portuguese, Indonesian and Tetun of all new texts.

The Tetun check against the Timor Aid dictionary follows when www.timoraid.org can be reached from the build environment.
Development continues toward 0.10.0 and the final version 1.1.12 (November 2026).
