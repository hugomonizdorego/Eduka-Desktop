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
   apt install -y ./edukasaun-desktop-menu_0.9.12_all.deb
   ```

3. Check the result and remove the copied file:

   ```sh
   dpkg -s edukasaun-desktop-menu | grep -E 'Status|Version'
   rm ./edukasaun-desktop-menu_0.9.12_all.deb
   ```

The post-install script does not start any GUI inside the chroot; Eduka-Panel
and the Eduka-Desktop daemon start from `/etc/xdg/autostart` after login.

To update later, build the new version and run the same `apt install ./...deb`
command; the old version is replaced and user settings are kept.

## Login sessions

The package registers two sessions for LightDM (slick-greeter,
lightdm-gtk-greeter) and other display managers:

| Session | File | Starts |
|---|---|---|
| Eduka-Desktop (X11) | `/usr/share/xsessions/edukasaun-desktop.desktop` | `eduka-desktop-session` → `startlxqt` |
| Eduka-Desktop (Wayland) | `/usr/share/wayland-sessions/edukasaun-desktop-wayland.desktop` | `eduka-desktop-session --wayland` → `startlxqtwayland` |

- X11 is the default LightDM session
  (`/usr/share/lightdm/lightdm.conf.d/60-edukasaun-desktop.conf`); a
  `user-session=` line in `/etc/lightdm/lightdm.conf` still wins.
- The Wayland entry is only shown when `startlxqtwayland` exists
  (`apt install lxqt-wayland-session labwc`), and the compositor is chosen in
  LXQt Configuration Center → Session Settings → Wayland Settings.
- In Wayland, Eduka-Panel and Eduka-Desktop run through XWayland; the taskbar
  lists XWayland applications only. X11 is recommended for class computers.
- Both sessions hide lxqt-panel via `/usr/share/edukasaun-desktop/xdg`
  (prepended to `XDG_CONFIG_DIRS` only in Eduka sessions).

## Release checklist

1. Bump `Version:` in `DEBIAN/control` and `VERSION` in
   `usr/lib/edukasaun-desktop/eduka_common.py`.
2. Add the changes to `usr/share/edukasaun-desktop/doc/HISTORY.txt`.
3. `sh tools/build-deb.sh`
