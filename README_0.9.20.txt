Edukasaun Desktop Suite 0.9.20

All included components use the same version number:
- Eduka-Desktop 0.9.20
- Eduka-Panel 0.9.20
- Eduka-Menu 0.9.20
- Eduka-Settings 0.9.20

Changes in this patch (preparing 0.10.0):
- Accent color: Eduka-Settings → Appearance → Accent color offers 16 colors and "Other color…"; Eduka-Panel, Eduka-Desktop, the Action Center, Eduka-Settings and the leave screen all follow it ("A" keeps the theme's own color).
- Action Center rearranged: music and video on top, sound and brightness at the bottom (always in reach, never scrolled away), quick tiles and the calendar in between.
- Player: previous, play/pause and next only (no extra volume slider); a long title scrolls; clicking the player opens the application that plays (VLC, Firefox, ...).
- The greeting no longer wraps beside a wide LED clock or a clock with seconds: it moves under the clock. New slider knobs that are never cut off.
- Calendar agenda: choose a day, press "+ Agenda", write what is on that day, the time and the alarm (notification, notification with alarm sound, or blinking notification). Days with an agenda get a dot; at the time a notification appears (with sound) and the clock on Eduka-Panel blinks until the Action Center is opened.
- Weather behind the clock: location from the internet address (GeoJS) and the forecast from Open-Meteo (open source, no account), refreshed every 30 minutes when online. Small animations: a smiling sun, moon and stars at night, drifting clouds with a face, rain, drizzle, snow, fog and lightning.
- Time zone map: click the clock for the globe, click the globe again for a world map with the 24 time zones, the night side, the zone of this computer and a pulsing dot at its city. Daylight saving time follows each country's own rules (IANA time zone database); hovering a city shows its time.
- Eduka-Panel: resting the pointer on a task shows a picture of the window (also for minimized windows, taken while they were open); clicking the picture opens it. Other icons show a small card instead of a plain tooltip.
- The clock on Eduka-Panel follows the clock style of the Action Center (digital, LED or a small analog dial, with the chosen color); a new minute slides in and a new style fades in.
- Battery: right-click → Show: percentage, time left (or until full) or both. The sound icon shows the volume level like the Action Center.
- Parental Control (Eduka-Settings → Parental Control): a time limit (30 min, 1, 2, 3 hours or any time), counted each time the computer starts or in total per day, with your own message and an emoji. When the time is up the message covers the screen, keyboard and mouse stop working and the computer shuts down. A root service counts the time, and changing or switching off the limit always needs an administrator password; a parent can add 30 minutes on the message screen with Ctrl+Alt+P.
- About: credits with links for the themes, icons, map, weather, time zones and the software Edukasaun Desktop is built on.
- Tetun corrected (Botarde, Xave, Keta disturba, klik liman-loos, La iha …, Tekladu, ...) and all new texts translated into Portuguese, Indonesian and Tetun.

Development continues toward 0.10.0 and the final version 1.1.12 (November 2026).
