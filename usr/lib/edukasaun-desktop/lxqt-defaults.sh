# SPDX-License-Identifier: GPL-3.0-or-later
# shellcheck shell=sh
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
# Shared shell helpers for Eduka-Desktop's LXQt integration.
# Sourced by /usr/bin/eduka-desktop-session (at every login, as the user).

# Window managers in order of preference. xfwm4 and kwin_x11 composite by
# themselves, which Eduka-Panel's and Eduka-Desktop's transparency needs.
# With openbox, Eduka-Panel starts picom (if installed) instead.
EDUKA_WM_CANDIDATES="xfwm4 kwin_x11 openbox marco fluxbox icewm"

eduka_pick_window_manager() {
    for candidate in $EDUKA_WM_CANDIDATES; do
        if command -v "$candidate" >/dev/null 2>&1; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

# eduka_ensure_window_manager CONFIG_HOME
# Make sure CONFIG_HOME/lxqt/session.conf names a window manager so LXQt
# never shows "Welcome to LXQt - select your default window manager".
# Only fills a missing or empty value; a user's choice is never changed.
eduka_ensure_window_manager() {
    config_home="$1"
    [ -n "$config_home" ] || return 0
    conf="$config_home/lxqt/session.conf"
    has_wm='^[[:space:]]*window_manager[[:space:]]*=[[:space:]]*[^[:space:]]'
    if [ -f "$conf" ] && grep -Eq "$has_wm" "$conf"; then
        return 0
    fi
    wm=$(eduka_pick_window_manager) || return 0
    mkdir -p "$config_home/lxqt" || return 0
    if [ ! -f "$conf" ]; then
        # Start from LXQt's own defaults so its other session settings stay.
        for system_conf in /etc/xdg/lxqt/session.conf /usr/share/lxqt/session.conf; do
            if [ -f "$system_conf" ]; then
                cp "$system_conf" "$conf" 2>/dev/null || :
                break
            fi
        done
        [ -f "$conf" ] || printf '[General]\n' > "$conf"
    fi
    # Drop an empty window_manager= line, then add the chosen one.
    sed -i '/^[[:space:]]*window_manager[[:space:]]*=[[:space:]]*$/d' "$conf" 2>/dev/null || :
    if grep -Eq "$has_wm" "$conf"; then
        return 0
    fi
    if grep -q '^\[General\]' "$conf"; then
        sed -i "/^\[General\]/a window_manager=$wm" "$conf" 2>/dev/null || :
    else
        tmp="$conf.eduka-tmp"
        { printf '[General]\nwindow_manager=%s\n\n' "$wm"; cat "$conf"; } > "$tmp" && mv "$tmp" "$conf"
    fi
    return 0
}

# Wayland compositors LXQt 2 can run on, in order of preference (labwc is
# the one LXQt recommends and the lightest).
EDUKA_WAYLAND_CANDIDATES="labwc kwin_wayland wayfire niri sway"

# eduka_ensure_wayland_compositor CONFIG_HOME
# The Wayland session (eduka-desktop-session --wayland) needs a compositor
# in CONFIG_HOME/lxqt/session.conf ([General] compositor=…), else LXQt asks
# for one first. Only fills a missing value; a user's choice is never changed.
eduka_ensure_wayland_compositor() {
    config_home="$1"
    [ -n "$config_home" ] || return 0
    conf="$config_home/lxqt/session.conf"
    has_comp='^[[:space:]]*compositor[[:space:]]*=[[:space:]]*[^[:space:]]'
    if [ -f "$conf" ] && grep -Eq "$has_comp" "$conf"; then
        return 0
    fi
    comp=""
    for candidate in $EDUKA_WAYLAND_CANDIDATES; do
        if command -v "$candidate" >/dev/null 2>&1; then
            comp="$candidate"
            break
        fi
    done
    [ -n "$comp" ] || return 0
    mkdir -p "$config_home/lxqt" || return 0
    [ -f "$conf" ] || printf '[General]\n' > "$conf"
    sed -i '/^[[:space:]]*compositor[[:space:]]*=[[:space:]]*$/d' "$conf" 2>/dev/null || :
    if grep -q '^\[General\]' "$conf"; then
        sed -i "/^\[General\]/a compositor=$comp" "$conf" 2>/dev/null || :
    else
        tmp="$conf.eduka-tmp"
        { printf '[General]\ncompositor=%s\n\n' "$comp"; cat "$conf"; } > "$tmp" && mv "$tmp" "$conf"
    fi
    return 0
}

# Variables the login session itself owns: ~/.config/environment.d never
# changes them (XDG_CONFIG_DIRS would also hide LXQt's own defaults).
EDUKA_ENV_KEEP="XDG_CONFIG_DIRS XDG_RUNTIME_DIR XDG_SESSION_ID XDG_SESSION_TYPE XDG_SESSION_CLASS XDG_SEAT XDG_VTNR XDG_CURRENT_DESKTOP XDG_SESSION_DESKTOP DESKTOP_SESSION DISPLAY WAYLAND_DISPLAY XAUTHORITY DBUS_SESSION_BUS_ADDRESS HOME USER LOGNAME SHELL PWD EDUKA_DESKTOP_SESSION"

# eduka_load_environment_d CONFIG_HOME
# The environment variables of ~/.config/environment.d/*.conf (KEY=VALUE, as
# systemd reads them for the services of the account) for every program of
# the session too (0.11 Pre-Stable). systemd's own generator expands $VAR and
# ${VAR}; without it the lines are read as they are.
eduka_load_environment_d() {
    config_home="$1"
    dir="$config_home/environment.d"
    [ -d "$dir" ] || return 0
    gen=""
    for g in /usr/lib/systemd/user-environment-generators/30-systemd-environment-d-generator \
             /lib/systemd/user-environment-generators/30-systemd-environment-d-generator; do
        if [ -x "$g" ]; then gen="$g"; break; fi
    done
    if [ -n "$gen" ]; then
        lines=$("$gen" 2>/dev/null) || lines=""
    else
        lines=$(cat "$dir"/*.conf 2>/dev/null | sed -e 's/^[[:space:]]*//' -e '/^#/d' -e '/^$/d') || lines=""
    fi
    [ -n "$lines" ] || return 0
    old_ifs="$IFS"
    IFS='
'
    for line in $lines; do
        key=${line%%=*}
        value=${line#*=}
        [ "$key" != "$line" ] || continue
        case "$key" in
            ''|[0-9]*|*[!A-Za-z0-9_]*) continue ;;
        esac
        case " $EDUKA_ENV_KEEP " in
            *" $key "*) continue ;;
        esac
        # Quotes around the whole value, as in systemd's files.
        case "$value" in
            \"*\") value=${value#\"}; value=${value%\"} ;;
            \'*\') value=${value#\'}; value=${value%\'} ;;
        esac
        export "$key=$value"
    done
    IFS="$old_ifs"
    return 0
}
