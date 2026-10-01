# Eduka-Desktop

Edukasaun Desktop Suite: Eduka-Desktop (start menu), Eduka-Panel and
Eduka-Menu-Settings for Edukasaun OS (Debian 13 Trixie, LXQt).

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
   apt install -y ./edukasaun-desktop-menu_0.9.16_all.deb
   ```

3. Check the result and remove the copied file:

   ```sh
   dpkg -s edukasaun-desktop-menu | grep -E 'Status|Version'
   rm ./edukasaun-desktop-menu_0.9.16_all.deb
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
- **Eduka-Menu Settings → Login Screen** changes the style (follow the desktop
  theme, light, dark, glass), accent color, title, clock, background, logo,
  pre-filled user and automatic login. It runs
  `pkexec /usr/lib/edukasaun-desktop/eduka-sddm-apply` (polkit action
  `org.edukasaun.desktop.sddm-config`, administrator password), which checks
  every value and writes `theme.conf.user`, the pictures in
  `/usr/share/Edukasaun/SDDM/` and `/etc/sddm.conf.d/20-eduka-autologin.conf`.
- Test the theme without logging out:
  `sddm-greeter --test-mode --theme /usr/share/sddm/themes/edukasaun`.
- Live boot (`boot=live`): `eduka-live-autologin.service` writes an SDDM and
  LightDM autologin for the live user before the login screen starts (and
  fixes the `[Autologin]` section live-config writes into `/etc/sddm.conf`),
  so the live session opens Eduka-Desktop directly. On installed systems it
  removes its file again.
- Standard account `edukasaun` / password `edukasaun`: created by the package
  while the ISO is built (when no personal account exists). On another system:
  `sudo eduka-default-user`. The account has no administrator (sudo) rights;
  change the password on shared computers with `passwd`.

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

## Notifications

LXQt's notification daemon shows the bubbles. Eduka-Panel listens to the
`org.freedesktop.Notifications.Notify` calls with `dbus-monitor` and keeps the
last 40 in `~/.config/eduka-desktop/notifications.json` (bell badge, history
popup, latest entry in the Action Center).

## Repairing an account used with 0.9.12

0.9.12 started LXQt without its defaults. If an account still asks for a
window manager or looks unthemed, run **Eduka-Menu Settings → Maintenance →
Repair LXQt theme and session** (or `eduka-lxqt-repair`) and log in again.
Accounts created after installing 0.9.13 or later are not affected.

## Release checklist

1. Bump `Version:` in `DEBIAN/control` and `VERSION` in
   `usr/lib/edukasaun-desktop/eduka_common.py`.
2. Add the changes to `usr/share/edukasaun-desktop/doc/HISTORY.txt`.
3. `sh tools/build-deb.sh`
