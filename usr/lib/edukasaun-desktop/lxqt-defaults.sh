# Shared shell helpers for Eduka-Desktop's LXQt integration.
# Sourced by /usr/bin/eduka-desktop-session and the package postinst.

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
