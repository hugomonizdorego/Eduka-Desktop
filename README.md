# Eduka-Desktop

Edukasaun Desktop Suite: Eduka-Desktop (start menu), Eduka-Panel and
Eduka-Settings (formerly Eduka-Menu Settings) for Edukasaun OS (Debian 13 Trixie, LXQt).

## Build the .deb

```sh
sh tools/build-deb.sh
# -> dist/edukasaun-desktop-menu_<version>_all.deb
```

Requires `dpkg-deb` and `python3`. The script fixes file permissions, checks
Python syntax, computes Installed-Size and md5sums, and refuses to build when
`DEBIAN/control` and `VERSION` in `eduka_common.py` disagree.

## Install in the Cubic terminal (chroot)

1. Copy the `.deb` into the Cubic terminal (drag and drop it into the terminal
   window, or use the Cubic "Copy" button). It lands in the current folder.
2. Install it with apt so dependencies are pulled from the Debian repository:

   ```sh
   apt update
   apt install -y ./edukasaun-desktop-menu_0.9.24_all.deb
   ```

3. Check the result and remove the copied file:

   ```sh
   dpkg -s edukasaun-desktop-menu | grep -E 'Status|Version'
   rm ./edukasaun-desktop-menu_0.9.24_all.deb
   ```

The post-install script does not start any GUI inside the chroot; Eduka-Panel
and the Eduka-Desktop daemon start from `/etc/xdg/autostart` after login.

To update later, build the new version and run the same `apt install ./...deb`
command; the old version is replaced and user settings are kept.

## Login sessions

Only **Eduka-Desktop** (`/usr/share/xsessions/edukasaun-desktop.desktop`,
started by `eduka-desktop-session` → `startlxqt`) is listed by SDDM, LightDM
and other greeters.

- The LXQt, Openbox and labwc session entries are hidden with `dpkg-divert`
  into `/usr/share/edukasaun-desktop/hidden-sessions/`. The programs stay
  installed (xfwm4 or Openbox still runs as the window manager). Removing the
  package restores the entries. To show one again by hand:
  `dpkg-divert --package edukasaun-desktop-menu --remove --rename /usr/share/xsessions/lxqt.desktop`
- **SDDM** preselects the session in `/var/lib/sddm/state.conf`; the package
  points it (and an autologin `Session=` for a hidden session) to Eduka-Desktop.
- **LightDM** uses `/usr/share/lightdm/lightdm.conf.d/60-edukasaun-desktop.conf`.
- `eduka-desktop-session` must **never** export `XDG_CONFIG_DIRS`: `startlxqt`
  only adds LXQt's default configuration when that variable is unset.

## Login screen, live session and accounts

- SDDM theme `edukasaun` (`/usr/share/sddm/themes/edukasaun`), selected by
  `/etc/sddm.conf.d/10-edukasaun.conf`.
- Background: put any picture at **`/usr/share/Edukasaun/SDDM/Default.png`**.
  Logo: `/usr/share/Edukasaun/Logo/Edukasaun Logo.png`. Both paths are set in
  `/usr/share/sddm/themes/edukasaun/theme.conf`.
- **Eduka-Settings → Login Screen** changes the style (follow the desktop
  theme, light, dark, glass), accent color, title, clock, background, logo,
  pre-filled user and automatic login. It runs
  `pkexec /usr/lib/edukasaun-desktop/eduka-sddm-apply` (polkit action
  `org.edukasaun.desktop.sddm-config`, administrator password), which checks
  every value and writes `theme.conf.user`, the pictures in
  `/usr/share/Edukasaun/SDDM/` and `/etc/sddm.conf.d/20-eduka-autologin.conf`.
- The login screen has a user picture row, keyboard layout, Language,
  Accessibility (larger text, high contrast, Qt Virtual Keyboard when
  `qml-module-qtquick-virtualkeyboard` is installed) and Power menus. The
  language picked there is written with the user name to
  `/var/lib/edukasaun-desktop/login/language` (directory owned by `sddm`;
  `GreeterEnvironment=QML_XHR_ALLOW_FILE_READ=1,QML_XHR_ALLOW_FILE_WRITE=1`
  in `10-edukasaun.conf`). `eduka-desktop-session` uses it only when the user
  matches and the language is in its list; `LANG` is set only when that
  locale is generated.
- Test the theme without logging out:
  `sddm-greeter --test-mode --theme /usr/share/sddm/themes/edukasaun`.
- Live boot (`boot=live`): `eduka-live-autologin.service` writes an SDDM and
  LightDM autologin for the live user before the login screen starts (and
  fixes the `[Autologin]` section live-config writes into `/etc/sddm.conf`),
  so the live session opens Eduka-Desktop directly. On installed systems it
  removes its file again.
- Standard account `edukasaun` / password `edukasaun`: created by the package
  while the ISO is built (when no personal account exists), with administrator
  rights (group `sudo`), so polkit prompts ask for this password and not for
  root. `/etc/live/config.conf.d/90-edukasaun.conf` makes live-config use the
  same account. On another system: `sudo eduka-default-user`.
- After installation the installer creates the owner's account. At the next
  boot `eduka-live-autologin.service` locks `edukasaun` and hides it from SDDM
  (`/etc/sddm.conf.d/30-eduka-hide-live-user.conf`); its files are kept.
- Saving the Login Screen page also writes `/etc/sddm.conf.d/zz-edukasaun-theme.conf`
  (read last) and adds `QtVersion=6` to the theme when only the Qt 6 greeter
  exists. Administrators save without a password prompt
  (`/usr/share/polkit-1/rules.d/50-edukasaun-desktop.rules`).

## Languages

- Eduka follows `LANGUAGE`/`LC_ALL`/`LC_MESSAGES`/`LANG` (the boot or installer
  choice). Catalogs: `usr/share/edukasaun-desktop/i18n/<lang>.json`
  (`{"English text": "translation"}`, `pt_BR.json` only holds the words that
  differ from `pt.json`). Edit `tools/i18n/catalog_full.py` (pt, id, tet) or
  `tools/i18n/catalog_core.py` (ms, tl, th, vi, zh_CN, zh_TW) and run
  `python3 tools/i18n/build-catalogs.py`.
- Tetun has no system language pack: Eduka-Settings → Language & Startup →
  Tetun (or Tetun on the login screen) sets `LANGUAGE=tet:pt:...` at login.

## Window manager and transparency

- LXQt asks for a window manager when `window_manager` is empty. The package
  fills it in `/etc/skel/.config/lxqt/session.conf` and existing accounts
  (preferring xfwm4, then KWin, then Openbox); the session launcher does the
  same at login. A chosen window manager is never changed.
- Transparency needs a compositor. xfwm4 and KWin have one built in; with
  Openbox, Eduka-Panel starts `picom` (xrender, no shadows). Without any
  compositor Eduka uses an opaque look instead of black areas, and Liquid
  Glass falls back to Eduka-Default-Theme.

## Themes

- **Eduka-Default-Theme**: light, opaque enough for any computer.
- **Liquid Glass**: milky glass; needs a compositor (started automatically)
  and at least 2 GB of memory. "Blur behind Liquid Glass" restarts picom with
  the glx backend and dual_kawase blur for Eduka-Panel and Eduka-Desktop only;
  without working OpenGL (VirtualBox without 3D) it falls back to xrender.
- **Edukasaun-Dark**: Orchis dark (vinceliuice, GPL-3.0) installed as
  `/usr/share/themes/Edukasaun-Dark` (GTK 2/3/4, xfwm4, Openbox). Choosing it
  sets the GTK theme, the LXQt Qt palette and the window border theme; the old
  values are saved in `~/.config/eduka-desktop/desktop-theme-backup.json` and
  restored when another Eduka theme is chosen.
- Reset to Defaults restores Eduka-Default-Theme and sends `reset` to
  Eduka-Desktop, which then drops its remembered layout, section and search.

## Panel position, effects and clock

- `position` in the panel settings: `Bottom`, `Top`, `Left`, `Right`.
  Struts (`_NET_WM_STRUT_PARTIAL`) follow the edge.
- Effects: `effects_enabled`, `effect_hover` (`wave`, `glow`, `slide`) and
  `effect_launch` (`bubble`, `zoom-in`, `zoom-out`, `ripple`, `bounce`,
  `confetti`, `fade`) in the desktop settings. Used only with 4 GB of memory
  and 4 CPU threads and never with Eduka-Low-Theme.
- Clock: `clock_style` (`digital`, `analog`, `led`), `clock_format`,
  `clock_seconds`, `clock_blink`, `clock_color` (one color for every clock face;
  empty follows the theme). The globe map
  (`usr/share/edukasaun-desktop/assets/world-map.png`) is drawn by
  `tools/gen-globe-map.py` from Natural Earth 1:110m land (public domain).
- Per-application sound: `pactl list sink-inputs` (pulseaudio-utils) and
  MPRIS players through `dbus-send`, read only while the Action Center is open.

## Compositor

- `compositor` in the desktop settings: `auto`, `xrender`, `glx`, `wm`, `off`
  (Eduka-Settings → Appearance → Compositor, or `eduka-compositor set MODE`).
- `auto`: xfwm4/KWin composite themselves; with Openbox Eduka starts picom
  (XRender; OpenGL only for Liquid Glass blur on real 3D graphics).
  Eduka-Low-Theme: no compositor.
- `picom_args()` builds the picom command for the installed version
  (`picom --version`), following picom's upstream changelog; see
  the 0.9.21 entry of HISTORY.txt. Eduka never ships its own picom build: Debian's picom
  is used, so security updates arrive through apt.
- `eduka-compositor` prints a report (window manager, compositor, backend,
  virtual machine, OpenGL renderer, picom version and its last warnings).
- State: `$XDG_RUNTIME_DIR/eduka-desktop/picom.json` (pid, mode, crashes),
  log: `$XDG_RUNTIME_DIR/eduka-desktop/picom.log`.

## Panel styles and panel popups (0.9.24)

- `panel_style` in the panel settings: `full` (whole edge, no gap, square),
  `floating`, `short` (64 % centered) or `dock` (fits its buttons; task
  buttons icon-only, refit after every taskbar change).
- `panel_clock_seconds`, `panel_clock_blink` for the clock on Eduka-Panel.
- Popups of the panel icons: `NetworkPopup` (nmcli: wired devices, radio,
  inline password with show/hide), `SoundPopup` (installed players from the
  app registry, volume, output device), `BatteryPopup` (sysfs battery,
  brightness, `powerprofilesctl`), `BluetoothPopup` (bluetoothctl: power,
  devices, pair/trust/connect, scan). The Action Center is unchanged.

## Stability, palette and language (0.9.23)

- `install_crash_log(name)` in `eduka_common.py`: Python errors in Qt slots
  are logged to `~/.cache/eduka-desktop/<name>-errors.log` instead of
  aborting the program; `faulthandler` writes crash traces there too.
- The menu daemon touches `$XDG_RUNTIME_DIR/eduka-desktop/menu-daemon.beat`
  every 2 s; `menu_daemon_alive()` stops a daemon without heartbeat for
  20 s so the panel starts a fresh one.
- `repair_qt_palette()` checks the contrast of lxqt.conf `[Palette]` (and the
  system defaults) and writes a readable palette for the current theme.
- `sync_session_language()` writes `LANGUAGE=tet:pt:en` to
  `~/.config/lxqt/session.conf [Environment]` when Tetun is chosen and
  eduka-language-pack-tet is installed.
- Effects: `effect_speed`, `effect_size`, `effect_random`, `tile_size` in the
  desktop settings.

## Drives, touchpad, wallpaper and input devices (0.9.22)

- Removable drives: `lsblk -J` every 3 s in Eduka-Panel; USB sticks, memory
  cards and external HDD/SSD get a panel icon and a popup with Open
  (`udisksctl mount`), Eject (unmount) and Safely remove (unmount and
  `udisksctl power-off`). Disks mounted on system paths and the live medium
  (`/run/live`, `/lib/live`, `/cdrom`) are never listed or ejected.
  The drives and touchpad icons stay on the panel while the Action Center is open.
- Wallpaper: `eduka_wallpaper.py`; settings under `wallpaper` in the desktop
  settings. Eduka renders the picture with the chosen mode and background
  color to `~/.cache/eduka-desktop/wallpaper/` and hands the file to
  pcmanfm-qt (`--set-wallpaper FILE --wallpaper-mode stretch`); the
  slideshow runs in Eduka-Panel with a fade (only with a compositor).
- Desktop icons: pcmanfm-qt's `DesktopShortcuts` (Home, Trash, Computer,
  Network); drives appear as `eduka-drive-*.desktop` links while plugged in
  (`desktop_drives` in the desktop settings).
- Keyboard, mouse and touchpad: `eduka_input.py`, settings in
  `~/.config/eduka-desktop/input.json`, applied with `setxkbmap`, `xset`,
  `numlockx` and libinput properties through `xinput`; Eduka-Panel applies
  them at login and when a device is plugged in. The panel touchpad picture
  follows `xinput test-xi2 --root <id>` (raw motion and button events).
- Eduka-Settings applies every change at once (debounced); the login screen
  and Parental Control keep their Save button because they need an
  administrator password.
- Eduka-MultiColor: GTK theme built from Graphite (vinceliuice, GPL-3.0,
  `install.sh -c light`), window borders from `tools/gen-wm-themes.py`;
  `MULTI_COLORS` / `multicolor_on()` in `eduka_common.py` color the menu
  categories, Action Center tiles and panel buttons (also available as the
  `multicolor` switch for the other themes).
- Parental Control stores `seconds` (60 s – 24 h) besides `minutes`; emoji
  pictures come from Noto Emoji (Apache-2.0) in
  `/usr/share/edukasaun-desktop/emoji/`.

## Accent color, agenda, weather and time zones

- `accent_color` (`#rrggbb`, empty = theme color) in the desktop settings.
  `accentize()` in `eduka_common.py` replaces the built-in accent colors of
  every stylesheet, so new code only needs the usual green tokens.
- Agenda: `~/.config/eduka-desktop/agenda.json`; Eduka-Panel checks it every
  15 s and rings once per entry (`alarm`: `notify`, `sound`, `blink`).
- Weather: GeoJS (`get.geojs.io`) for the location, falling back to the time
  zone's city from `zone1970.tab`; forecast from `api.open-meteo.com`
  (no key, CC BY 4.0). Cache: `~/.cache/eduka-desktop/weather.json`.
  `"weather": false` in the panel settings switches it off.
- Time zone map: `zoneinfo` (IANA tzdata) gives offset and daylight saving.

## Parental Control

- `eduka-parental.service` (root) runs `/usr/lib/edukasaun-desktop/eduka-parental-daemon`,
  counts active graphical sessions (`loginctl`) and writes
  `/run/edukasaun-parental/state.json`; at the limit it waits 90 s and runs
  `systemctl poweroff`.
- Settings: `/etc/edukasaun-desktop/parental.json`, written only by
  `pkexec /usr/lib/edukasaun-desktop/eduka-parental-apply` (polkit action
  `org.edukasaun.desktop.parental`, always `auth_admin`, no exception rule).
  Used time: `/var/lib/edukasaun-desktop/parental-usage.json`.
- Eduka-Panel shows the warnings (10, 5, 1 minutes) and the message screen
  (keyboard and mouse grabbed). Ctrl+Alt+P on that screen asks for an
  administrator password and adds 30 minutes.

## Theme sources

- `tools/gen-wm-themes.py` writes the xfwm4 and Openbox borders of
  Edukasaun-Dark, Eduka-Low and Eduka-Transparan (fixed colors, no GTK
  symbolic colors).
- Eduka-Low GTK: Yaru-remix default flavour, built with
  `meson setup build -Dicons=false -Dgnome-shell=false -Dgresource=false -Dwallpapers=false -Dmetacity=false -Ddark=false -Dlight=false`.

## Notifications

In Eduka-Desktop sessions Eduka-Panel owns `org.freedesktop.Notifications`
and draws the bubbles itself; lxqt-notificationd is stopped through
lxqt-session (`stopModule lxqt-notifications.desktop`). The last 40 are kept in
`~/.config/eduka-desktop/notifications.json`; Do Not Disturb is stored in
`~/.config/eduka-desktop/panel-state.json`. When another server owns the name
(outside Eduka-Desktop) Eduka-Panel only records the calls with `dbus-monitor`.

## Action Center and leave screen

- Clock: `clock_style` (`digital`/`analog`) and `clock_format` (`24h`/`12h`) in
  the panel settings; greetings follow the Eduka-Settings language.
- The handle at the top shows or hides the month calendar (remembered in
  `panel-state.json`).
- `eduka-session-action lock|logout|restart|shutdown` shows the Eduka leave
  screen; `--now` runs the action directly (lxqt-session D-Bus, then systemd).

## Repairing an account used with 0.9.12

0.9.12 started LXQt without its defaults. If an account still asks for a
window manager or looks unthemed, run **Eduka-Settings → Maintenance →
Repair LXQt theme and session** (or `eduka-lxqt-repair`) and log in again.
Accounts created after installing 0.9.13 or later are not affected.

## Release checklist

1. Bump `Version:` in `DEBIAN/control` and `VERSION` in
   `usr/lib/edukasaun-desktop/eduka_common.py`.
2. Add the changes to `usr/share/edukasaun-desktop/doc/HISTORY.txt`.
3. `sh tools/build-deb.sh`
