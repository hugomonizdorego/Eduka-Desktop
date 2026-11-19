#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""The pages of Eduka-Settings and their search words (0.11 Pre-Stable).

Eduka-Settings → All Settings shows these tiles, and the search box of
Eduka-Desktop finds the same pages ("sound", "mouse", "workspace" ...), so a
setting is one search away. Only the standard library is used, so the menu
loads it quickly.
"""
import re

# The overview of Eduka-Settings (RC2), like the system settings of a full
# desktop: Eduka pages by their key, other tools ('@...') by the first of
# their commands that is installed. Tools that are missing are not shown.
SETTINGS_SECTIONS = [
    ('Appearance', [
        ('appearance', 'Themes', 'preferences-desktop-theme', 'theme style dark light colors accent'),
        ('wallpaper', 'Backgrounds', 'preferences-desktop-wallpaper', 'wallpaper picture background'),
        ('fonts', 'Font Selection', 'preferences-desktop-font', 'fonts letters text size scaling hinting'),
        ('effects', 'Effects', 'applications-graphics', 'effects animation compositor transparency'),
        ('desktopicons', 'Desktop', 'user-desktop', 'desktop icons home trash computer'),
    ]),
    ('Eduka', [
        ('desktop', 'Eduka-Desktop', 'start-here', 'menu start applications tiles'),
        ('quick', 'Eduka-Quick', '', 'pie quick launcher round hotkey'),
        ('panel', 'Eduka-Panel', 'preferences-desktop', 'panel taskbar start button'),
        ('clock', 'Clock', 'preferences-system-time', 'clock weather action center'),
        ('notifications', 'Notifications', 'preferences-system-notifications', 'notifications messages do not disturb'),
        ('windows', 'Windows', 'preferences-system-windows', 'focus follows mouse middle click paste clipboard history force close'),
        ('workspaces', 'Workspaces & Corners', 'preferences-desktop', 'workspaces virtual desktops hot corners'),
        ('capture', 'Screenshots & Video', 'camera-photo', 'screenshot screen recording video record'),
    ]),
    ('Preferences', [
        ('accessibility', 'Accessibility', 'preferences-desktop-accessibility', 'vision contrast large text pointer'),
        ('users', 'Account details', 'user-info', 'account picture avatar name password'),
        ('datetime', 'Date & Time', 'preferences-system-time', 'date time zone clock ntp sync'),
        ('general', 'Languages', 'preferences-desktop-locale', 'language tetun indonesia portugues startup'),
        ('@input', 'Input Method', 'fcitx', 'input method ime ibus fcitx'),
        ('parental', 'Parental Control', 'preferences-system-parental-controls', 'parental time limit children break'),
        ('@startup', 'Startup Applications', 'preferences-system-session', 'startup autostart session'),
        ('@defaults', 'Preferred Applications', 'preferences-desktop-default-applications', 'default applications file associations browser'),
        ('privacy', 'Privacy', 'preferences-system-privacy', 'privacy recent files history thumbnails trash'),
        ('screenreader', 'Screen Reader', 'orca', 'orca screen reader voice speech'),
        ('@screensaver', 'Screensaver', 'preferences-desktop-screensaver', 'screensaver lock idle'),
        ('@windows', 'Windows', 'preferences-system-windows', 'windows window manager openbox xfwm4 borders'),
    ]),
    ('Hardware', [
        ('@bluetooth', 'Bluetooth', 'bluetooth', 'bluetooth wireless devices'),
        ('@disks', 'Disks', 'drive-harddisk', 'disks drives partitions usb'),
        ('display', 'Display', 'preferences-desktop-display', 'display monitor screen resolution projector scale size'),
        ('@display', 'Screens and Resolution', 'video-display', 'monitor resolution arrange screens projector'),
        ('keyboard', 'Keyboard', 'input-keyboard', 'keyboard layout num lock'),
        ('shortcuts', 'Keyboard Shortcuts', 'preferences-desktop-keyboard-shortcuts', 'shortcuts hotkeys keys windows super'),
        ('mouse', 'Mouse and Touchpad', 'input-mouse', 'mouse touchpad pointer speed gestures'),
        ('touchscreen', 'Touch Screen', 'input-tablet', 'touch screen tablet on-screen keyboard'),
        ('@network', 'Network', 'preferences-system-network', 'network wifi wired vpn internet'),
        ('@power', 'Power Management', 'preferences-system-power-management', 'power battery suspend sleep'),
        ('@printers', 'Printers', 'printer', 'printers printing scanner'),
        ('sound', 'Sound', 'audio-volume-high', 'sound volume speakers headphones microphone test hdmi bluetooth'),
        ('soundfx', 'Clear Sound', 'audio-x-generic', 'easyeffects equalizer voice music noise clear sound presets'),
        ('soundfix', 'Sound Quality & Fixes', 'preferences-desktop-sound', 'crackling no sound fix pipewire pulseaudio firmware'),
        ('@sysinfo', 'System Information', 'computer', 'system information about version memory'),
    ]),
    ('Administration', [
        ('fingerprint', 'Fingerprints', 'fingerprint', 'fingerprint login reader'),
        ('@firewall', 'Firewall', 'gufw', 'firewall security ports'),
        ('login', 'Login Window', 'system-users', 'login screen sddm autologin'),
        ('lightdm', 'LightDM', 'system-users', 'lightdm greeter slick login'),
        ('@software', 'Software Sources', 'software-properties', 'software sources repositories apt updates'),
        ('maintenance', 'System Maintenance', 'applications-system', 'maintenance repair reset'),
        ('memory', 'Memory', 'utilities-system-monitor', 'memory ram zram earlyoom slow freeze'),
        ('users', 'Users and Groups', 'system-users', 'users accounts administrator groups'),
    ]),
]


def search(query, translate=None, limit=4):
    """Eduka pages for a search: [(key, title, icon, group)], best first.
    Every word of the query must start a word of the title, of its
    translation or of its search words; title matches come first."""
    words = [w for w in re.split(r'\W+', (query or '').lower()) if w]
    if not words or len(''.join(words)) < 3:
        return []
    found = []
    seen = set()
    for order, (group, entries) in enumerate(SETTINGS_SECTIONS):
        for key, title, icon, extra in entries:
            if key.startswith('@') or key in seen:
                continue
            names = title.lower()
            if translate is not None:
                names += ' ' + str(translate(title)).lower()
            title_words = re.split(r'\W+', names)
            all_words = title_words + re.split(r'\W+', extra.lower())
            if not all(any(t.startswith(w) for t in all_words if t) for w in words):
                continue
            in_title = all(any(t.startswith(w) for t in title_words if t) for w in words)
            seen.add(key)
            found.append((0 if in_title else 1, len(found), (key, title, icon, group)))
    found.sort()
    return [hit for _score, _n, hit in found[:limit]]


if __name__ == '__main__':
    import sys
    for hit in search(' '.join(sys.argv[1:]) or 'sound'):
        print(*hit)
