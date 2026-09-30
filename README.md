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
   apt install -y ./edukasaun-desktop-menu_0.9.13_all.deb
   ```

3. Check the result and remove the copied file:

   ```sh
   dpkg -s edukasaun-desktop-menu | grep -E 'Status|Version'
   rm ./edukasaun-desktop-menu_0.9.13_all.deb
   ```

The post-install script does not start any GUI inside the chroot; Eduka-Panel
and the Eduka-Desktop daemon start from `/etc/xdg/autostart` after login.

To update later, build the new version and run the same `apt install ./...deb`
command; the old version is replaced and user settings are kept.

## Login sessions

| Name in SDDM / LightDM | File | Starts |
|---|---|---|
| Eduka-Desktop | `/usr/share/xsessions/edukasaun-desktop.desktop` | `eduka-desktop-session` → `startlxqt` (X11) |
| Eduka-Desktop Wayland | `/usr/share/wayland-sessions/edukasaun-desktop-wayland.desktop` | `eduka-desktop-session --wayland` → `startlxqtwayland` |

- **SDDM** preselects the session stored in `/var/lib/sddm/state.conf`. The
  package sets it to Eduka-Desktop when nothing is stored, the stored session
  was removed, or it is the plain LXQt session.
- **LightDM** uses `/usr/share/lightdm/lightdm.conf.d/60-edukasaun-desktop.conf`
  (`user-session=edukasaun-desktop`); `/etc/lightdm/lightdm.conf` still wins.
- `eduka-desktop-session` must **never** export `XDG_CONFIG_DIRS`: `startlxqt`
  only adds LXQt's default configuration when that variable is unset.
- The Wayland entry appears only when `lxqt-wayland-session` is installed
  (Suggests). Eduka components run through XWayland there.
- Eduka-Panel stops lxqt-panel through lxqt-session only in Eduka-Desktop
  sessions (`EDUKA_DESKTOP_SESSION`).

## Repairing an account used with 0.9.12

0.9.12 started LXQt without its defaults. If an account still asks for a
window manager or looks unthemed, run **Eduka-Menu Settings → Maintenance →
Repair LXQt theme and session** (or `eduka-lxqt-repair`) and log in again.
Accounts created after installing 0.9.13 are not affected.

## Release checklist

1. Bump `Version:` in `DEBIAN/control` and `VERSION` in
   `usr/lib/edukasaun-desktop/eduka_common.py`.
2. Add the changes to `usr/share/edukasaun-desktop/doc/HISTORY.txt`.
3. `sh tools/build-deb.sh`
