# User guide of Edukasaun Desktop Suite: English.
# Blocks: ('p', text) ('h3', text) ('ul'|'ol', [items]) ('tip'|'note'|'warn', text)
# ('img', name, caption[, 'half'|'third']) ('img2', [(name, caption), ...]) ('table', head, rows)
# [[Ctrl+Alt+T]] becomes keys, **text** bold.
HTML_LANG = 'en'
FILE_SUFFIX = 'English'
TITLE = 'Edukasaun Desktop Suite — User Guide'
SUBTITLE = 'Version {version} · Eduka-Desktop, Eduka-Panel, Eduka-Quick and Eduka-Settings'
COVER_META = ('The desktop of **Edukasaun OS**, made for schools, on the LXQt session of Debian. '
              'Screenshots: English interface, theme Eduka-Pastel, 1366 × 768 screen. Version {version}, November 2026.')
FOOTER = 'Edukasaun Desktop Suite — User Guide (English)'
TOC_INTRO = 'Every part of the desktop: the start menu, the panel, the Action Center, the settings and the new features of 0.11 Pre-Stable.'
LABELS = {'contents': 'Contents', 'tip': 'Tip', 'note': 'Note', 'warn': 'Important'}

SECTIONS = [
('intro', 'Welcome to Edukasaun Desktop', [
    ('p', '**Edukasaun Desktop Suite** is the desktop of Edukasaun OS. It is designed for schools: pupils, teachers and school '
          'offices get a clear, friendly desktop that works on new laptops and on old computers alike. It runs in the **LXQt** '
          'session of Debian, so it stays light and fast; LXQt provides the session, the file manager (PCManFM-Qt), the terminal '
          'and many tools, and Eduka adds its own start menu, panel and settings.'),
    ('h3', 'The parts of the suite'),
    ('table', ['Part', 'What it does'], [
        ['**Eduka-Desktop**', 'The start menu: all programs in categories, a search box, favorites and system information.'],
        ['**Eduka-Panel**', 'The bar at the bottom: MENU button, taskbar, workspaces, status icons, notifications and the clock.'],
        ['**Action Center**', 'Opens from the clock: calendar and agenda, quick switches, volume, brightness and the session buttons.'],
        ['**Eduka-Quick**', 'A round, see-through quick launcher for the programs used most ([[Super+Q]]).'],
        ['**Eduka-Settings**', 'One window for every setting: look, panel, windows, display, sound, keyboard, mouse, users and more.'],
    ]),
    ('img', 'desktop', 'The desktop after logging in: desktop icons on the left, Eduka-Panel at the bottom.'),
    ('h3', 'What is new in 0.11 Pre-Stable'),
    ('ul', [
        'Eduka-Desktop opens with one click on MENU or one press of [[Super]], also while the Action Center is open.',
        'The search of Eduka-Desktop also finds the pages of Eduka-Settings ("sound", "mouse", "workspace" …).',
        'A soft blue default theme in the colors of the Edukasaun OS logo.',
        'A complete **Sound** page: devices, tests, clear sound with EasyEffects, and fixes for crackling or missing sound.',
        'Workspaces, hot corners, focus follows the mouse, middle-click paste and a clipboard history ([[Super+V]]).',
        'Screen recording with sound ([[Super+Alt+R]]) and **Force Close** for programs that stop answering.',
        'Frosted glass, touchpad tap-and-drag, pen tablets, the dedicated graphics card for games, optional Compiz effects.',
        'Better support for Wayland sessions (labwc, KWin) and a list of devices that still need a driver.',
    ]),
    ('note', 'The pictures in this guide show the English interface. Eduka-Desktop is also translated into Tetun, Portuguese '
             'and Indonesian (Eduka-Settings → Language & Time).'),
]),
('login', 'Logging in and out', [
    ('p', 'At the login screen choose your account (or type your name), type your password and press [[Enter]]. Computers with a '
          'fingerprint reader can also accept a finger when this was switched on in Eduka-Settings → Login & Fingerprint.'),
    ('p', 'Only the **Eduka-Desktop** session is offered at the login screen; it starts LXQt with Eduka-Panel and Eduka-Desktop. '
          'The first login of a new account sets up the wallpaper, the theme, the keyboard and the recommended display scale.'),
    ('h3', 'The leave screen'),
    ('p', 'Press [[Ctrl+Alt+Delete]], or use the buttons at the bottom of the Action Center, to open the leave screen. One click runs '
          'the action at once: **Lock** (your programs stay open and your password unlocks the screen), **Log Out**, **Sleep**, '
          '**Hibernate** (when the computer supports it), **Restart** or **Shut Down**. [[Esc]] closes the screen without doing anything.'),
    ('img', 'leave', 'The leave screen with the blurred desktop behind it.'),
    ('tip', 'Save your work before you log out, restart or shut down. [[Super+L]] locks the screen quickly when you leave the computer.'),
]),
('menu', 'Eduka-Desktop: the start menu', [
    ('p', 'Click **MENU** at the left end of the panel, or press the [[Super]] key (the key with the Windows logo), to open '
          'Eduka-Desktop. Click MENU again, press [[Super]] again or press [[Esc]] to close it. The menu also opens with one click '
          'while the Action Center or another popup of the panel is open.'),
    ('img', 'menu', 'Eduka-Desktop with the category All in the Grid view.'),
    ('h3', 'Categories'),
    ('p', 'The column on the left lists the categories. **Edukasaun** collects the programs for learning, science and games; '
          'the others follow the usual groups: Accessories, Graphics, Internet, Office, Programming, Sound & Video, System Tools, '
          'Universal Access and Preferences. **All** shows every program. Empty categories are hidden.'),
    ('h3', 'Search'),
    ('p', 'Just start typing when the menu is open. The search covers every program, whatever category is chosen, and it '
          'understands names, descriptions and keywords. [[Enter]] starts the first result. From 0.11 Pre-Stable the search also '
          'lists the matching **pages of Eduka-Settings**: type "sound", "mouse" or "workspace" and open the setting directly.'),
    ('img', 'menu-search', 'Searching for "sound": the matching pages of Eduka-Settings.'),
    ('h3', 'Grid, List and favorites'),
    ('ul', [
        '**Grid** shows big tiles; **List** shows names with a short description (good for screen readers and small screens).',
        'The column **Favorites** on the right keeps the programs you use most. Right-click a program → **Add to Favorites**.',
        '**System Information** shows the version of Edukasaun OS and of the desktop.',
        'The buttons at the bottom open the File Manager, the Terminal, Eduka-Settings and About.',
        'On small screens (under 900 pixels wide) the menu uses a narrower layout and shows the favorites as a category.',
    ]),
    ('h3', 'The right-click menu of a program'),
    ('ul', [
        '**Open** starts the program; **Run with the dedicated graphics card** appears on laptops with two graphics cards.',
        '**Add to Favorites**, **Add to Desktop** (an icon on the desktop) and **Pin to Taskbar** (a button on the panel).',
        '**Add to Eduka-Quick** puts the program into the round quick launcher.',
        '**Open Containing Folder** shows where the program file is.',
    ]),
]),
('panel', 'Eduka-Panel', [
    ('p', 'Eduka-Panel is the bar at the bottom of the screen. From left to right it shows the MENU button, the pinned '
          'programs, the open windows (the taskbar), the workspaces, the status icons and the clock.'),
    ('h3', 'Taskbar'),
    ('p', 'Every open window has a button. A click shows the window, a second click minimizes it. With several workspaces the '
          'taskbar shows the windows of the current workspace. Right-click a window button for more:'),
    ('ul', [
        '**Activate**, **Minimize**, **Maximize** or **Restore**, and **Close**.',
        '**Add to Favorites** and **Pin to Taskbar** (the program keeps its button when it is closed).',
        '**Force Close**: closes a program at once, also when it no longer answers (see chapter "Programs that stop answering").',
    ]),
    ('img', 'task-menu', 'The right-click menu of a window on the taskbar.', 'half'),
    ('h3', 'Workspaces'),
    ('p', 'The numbers **1 2 3 4** are the virtual workspaces: separate desktops for different tasks, for example a lesson on '
          'workspace 1 and the browser on workspace 2. Click a number, scroll over the numbers, or press [[Ctrl+Super+Left]] and '
          '[[Ctrl+Super+Right]]. The number of workspaces is set in Eduka-Settings → Windows & Workspaces.'),
    ('h3', 'Status icons'),
    ('table', ['Icon', 'Click', 'Right-click or more'], [
        ['Removable drives', 'Lists USB sticks and cards; eject them safely.', 'Open the drive in the file manager.'],
        ['Network', 'Wi-Fi networks and cable connection.', 'Network settings.'],
        ['Bluetooth', 'Switch on or off, pair a device (only when the computer has Bluetooth).', 'Bluetooth manager.'],
        ['Sound', 'Volume, output device and the Clear sound switch.', 'Scroll to change the volume.'],
        ['Battery', 'Charge, time left and power mode (laptops).', 'Power settings.'],
        ['Notifications', 'The latest messages; Do Not Disturb.', 'Notification settings.'],
        ['Keyboard (US, PT …)', 'Switches the keyboard layout.', 'Keyboard settings.'],
        ['Clock', 'Opens the Action Center.', 'Clock style and settings.'],
    ]),
    ('img', 'sound-popup', 'The sound popup: volume, output device, Clear sound and Sound Settings.', 'half'),
    ('tip', 'A small red **REC** button appears on the panel while the screen is being recorded; click it to stop.'),
    ('h3', 'Panel position and look'),
    ('p', 'Right-click an empty part of the panel to move it to another edge, to change its ends (oval, rounded or square) and to '
          'open the panel settings. Eduka-Panel keeps its place above maximized windows; only full-screen programs (videos, games, '
          'presentations) cover it.'),
]),
('action-center', 'The Action Center', [
    ('p', 'Click the clock on the panel (or press [[Super+A]]) to open the Action Center. Click the clock again, press [[Esc]] or '
          'click outside to close it.'),
    ('img', 'action-center', 'The Action Center.', 'half'),
    ('ul', [
        '**Clock card**: the time, a greeting and the date, with the weather of today. Click it for the world globe and the time '
        'zones; right-click it for the clock style (digital, analog, with seconds …).',
        '**Sync time** (top left): sets the clock and the time zone from the internet.',
        '**Tiles**: Network, Bluetooth, Airplane mode, Display (projector modes), Do Not Disturb and Settings. Right-click a tile '
        'to open its settings.',
        '**Music and video**: while a program plays, previous, play/pause and next appear at the top.',
        '**Calendar and agenda**: choose a day and press **+ Agenda** to write a note or a reminder with a time.',
        '**Volume and brightness** sliders; the arrow next to the volume chooses the output device.',
        '**Lock, Log Out, Restart, Shut Down** at the bottom.',
        'The grip at the top makes the Action Center smaller or bigger; the arrow at the top right switches the compact mode.',
    ]),
]),
('quick', 'Eduka-Quick', [
    ('p', 'Press [[Super+Q]] to open Eduka-Quick where the mouse pointer is. It shows the programs you use most in a circle. '
          'Point at a slice and click, or press the number shown on it ([[1]] to [[9]]). [[Esc]] closes it.'),
    ('img', 'quick', 'Eduka-Quick, the round quick launcher.', 'half'),
    ('ul', [
        'Hold the mouse button on the clear center and drag to move Eduka-Quick; it opens there next time.',
        'Right-click a program in Eduka-Desktop → **Add to Eduka-Quick** to add it.',
        'Eduka-Settings → Eduka-Quick chooses the number of slices (4 to 12), the look and the programs.',
    ]),
]),
('notifications', 'Notifications', [
    ('p', 'Programs show short messages at the bottom right, above the clock. They disappear by themselves after a few seconds; '
          'the bell icon on the panel keeps the latest ones. Click it to read them again or to clear them.'),
    ('img', 'recording-saved', 'A notification: the screen recording was saved.', 'half'),
    ('p', '**Do Not Disturb** (in the Action Center and the notification list) keeps messages silent; only urgent ones still '
          'appear. Eduka-Settings → Eduka-Panel → Notifications sets how long messages stay and whether they are kept.'),
]),
('settings', 'Eduka-Settings', [
    ('p', 'Open Eduka-Settings from the menu (the **Settings** button), with [[Super+I]], or by right-clicking a tile of the Action '
          'Center. The first page, **All Settings**, shows every setting in groups with its own search box. The list on the left '
          'leads to the pages; pages about the same subject share one entry with tabs at the top.'),
    ('img', 'settings-overview', 'All Settings, the first page of Eduka-Settings.'),
    ('p', 'Most changes are used at once. **Apply** ([[Ctrl+S]]) applies everything and keeps the window open; **Save & Close** '
          'applies and closes. Settings for the whole computer (other accounts, login screen, Parental Control, fingerprints) '
          'ask for an administrator password. **Reset to Defaults** at the bottom left restores the Edukasaun defaults of '
          'Eduka-Desktop and Eduka-Panel (theme, transparency, size, layout, menu button); favorites, pinned programs and the '
          'login screen are kept.'),
    ('table', ['Group', 'Pages'], [
        ['PERSONALIZE', 'Appearance (Theme, Fonts, Effects) · Wallpaper & Icons'],
        ['DESKTOP', 'Eduka-Desktop · Eduka-Quick · Eduka-Panel (Panel, Clock, Notifications) · Windows & Workspaces'],
        ['DEVICES', 'Display · Sound (Sound, Clear Sound, Quality & Fixes) · Keyboard (Keyboard, Shortcuts) · Mouse & Touch'],
        ['SYSTEM', 'Users · Language & Time · Accessibility · Parental Control · Login & Fingerprint · Maintenance'],
    ]),
]),
('look', 'Appearance, wallpaper and fonts', [
    ('p', '**Appearance → Theme** chooses one of seven themes. Each theme also styles the GTK and Qt programs and the window borders.'),
    ('table', ['Theme', 'For'], [
        ['**Eduka-Pastel** (default)', 'The soft blue of the Edukasaun OS logo; light and friendly for school.'],
        ['Eduka-Default-Theme', 'A calm, clear look with colored highlights.'],
        ['**Eduka-Low-Theme**', 'Very old or slow computers: no transparency, no effects, the least memory.'],
        ['Liquid Glass', 'Milky glass with light rims (needs a compositor and 4 GB of memory).'],
        ['Edukasaun-Dark', 'A dark theme for the evening or bright rooms with projectors.'],
        ['Eduka-Transparan', 'See-through panels and menus.'],
        ['Eduka-MultiColor', 'A different color for every category, tile and panel button.'],
    ]),
    ('img', 'settings-appearance', 'Appearance → Theme.'),
    ('ul', [
        '**Accent color**: the color of buttons, switches and highlights.',
        '**Frosted glass**: a blur behind Eduka-Panel, Eduka-Desktop and their popups (needs 3D graphics; it is off in VirtualBox).',
        '**Blurred desktop behind the leave screen**: works on every computer.',
        '**Fonts**: the fonts of the desktop, documents and window titles, their size and smoothing.',
        '**Effects**: animations and the compositor (Automatic is right for most computers).',
        '**Wallpaper & Icons**: pictures from /usr/share/background/Edukasaun or your own, a slideshow, and which icons the desktop shows.',
    ]),
]),
('desktop-panel', 'Eduka-Desktop, Eduka-Quick and Eduka-Panel settings', [
    ('p', '**Eduka-Desktop**: the size of the menu, Grid or List, the categories shown, tile colors and accessibility helpers.'),
    ('img', 'settings-desktop', 'Eduka-Settings → Eduka-Desktop.'),
    ('p', '**Eduka-Panel → Panel**: the height and position of the panel, the label of the MENU button, the pinned programs and the taskbar. '
          '**Clock**: digital or analog clock, seconds, the date and the weather. **Notifications**: how long messages stay, Do Not Disturb and the history.'),
    ('img', 'settings-panel', 'Eduka-Settings → Eduka-Panel → Panel.'),
]),
('windows', 'Windows, workspaces and screen capture', [
    ('p', '**Windows & Workspaces** has three tabs.'),
    ('h3', 'Windows'),
    ('ul', [
        '**Focus**: "Click a window to work in it" (like Windows), or "the window under the pointer gets the keyboard" (focus '
        'follows the mouse; the window is not raised).',
        '**Middle-click paste**: select text, then click the middle mouse button (or tap with three fingers) to paste it.',
        '**Clipboard history**: [[Super+V]] lists the texts you copied. It is kept in memory only, never on the disk; passwords '
        'copied from a password manager are not kept.',
        '**Programs that do not answer**: offer to force close a program that has not answered for 1, 2 or 5 minutes.',
        '**Window manager**: xfwm4 (recommended), Openbox (the lightest), KWin, Marco or Compiz (3D effects, installed separately). '
        'The choice is used from the next login.',
    ]),
    ('img', 'settings-windows', 'Windows & Workspaces → Windows.'),
    ('img', 'clipboard', 'The clipboard history ([[Super+V]]): click a text to copy it again.', 'half'),
    ('h3', 'Workspaces & Corners'),
    ('p', 'Choose the number of workspaces (1 to 8), whether the panel shows them and whether the taskbar shows only the windows of '
          'the current workspace. **Hot corners**: push the pointer into a corner of the screen to open Eduka-Desktop, show the '
          'desktop, open the Action Center or Eduka-Quick, change the workspace, show notifications or lock the screen. '
          'Nothing happens while a mouse button is held. Hot corners work in the X11 session.'),
    ('img', 'settings-workspaces', 'Windows & Workspaces → Workspaces & Corners.'),
    ('h3', 'Screenshots & Recording'),
    ('ul', [
        '[[Print]]: the whole screen · [[Alt+Print]]: the active window · [[Super+Shift+S]]: a part of the screen · '
        '[[Super+Print]]: saved at once in Pictures/Screenshots.',
        '[[Super+Alt+R]] starts a **screen recording** and stops it again; the red REC button on the panel stops it too.',
        'The sound of the computer and, when wanted, the microphone are recorded. The videos are MP4 files in '
        'Videos/Screen recordings; they play on every computer and phone.',
        '"Smoothness" (15, 25 or 30 pictures a second) and "Size" (small file to best picture) fit old and new computers.',
    ]),
    ('img', 'recording', 'While recording: the red REC button with the time on Eduka-Panel.'),
    ('img', 'settings-capture', 'Windows & Workspaces → Screenshots & Recording.'),
]),
('hang', 'Programs that stop answering', [
    ('p', 'Sometimes a program freezes: its window stays but it no longer reacts. Eduka-Panel notices it. When a program has not '
          'answered for two minutes (the time can be changed), a small window asks what to do:'),
    ('img', 'hang-dialog', 'A program is not answering: Wait or Force Close.', 'half'),
    ('ul', [
        '**Wait**: the program gets more time; many programs answer again after a long task.',
        '**Force Close**: the program is closed at once. Work that was not saved in that program is lost.',
    ]),
    ('p', 'You can also close a frozen program yourself: press [[Ctrl+Alt+Esc]] for the active window, or right-click its button '
          'on the taskbar → **Force Close**. Eduka asks first. Programs that keep the desktop running (the panel, the window '
          'manager, the desktop icons) are never closed.'),
    ('img', 'force-close', 'Force close after [[Ctrl+Alt+Esc]].', 'half'),
]),
('display', 'Display and graphics', [
    ('p', 'The **Display** page shows what kind of computer Eduka-Desktop found (laptop, desktop computer, tablet or virtual '
          'machine) and the size of the screen.'),
    ('ul', [
        '**Scale** (75 to 200 %): makes text, icons, panels and windows bigger or smaller together. The recommended scale is marked. '
        'The new scale is used after logging out and in.',
        '**Screens and Resolution**: arrange two monitors or a projector (LXQt monitor settings). [[Super+P]] changes the projector mode.',
        '**Graphics**: the graphics cards and their drivers, with advice when a driver or its firmware is missing. On laptops with '
        'two cards, games and programs that ask for it start on the dedicated card; any program can be started there from its '
        'right-click menu in Eduka-Desktop.',
    ]),
    ('img', 'settings-display', 'Display: the kind of computer and the scale.'),
]),
('sound', 'Sound', [
    ('p', 'Sound problems are common on Linux computers, so Eduka-Settings has a complete **Sound** page with three tabs. It works '
          'with PipeWire and with PulseAudio.'),
    ('h3', 'Sound'),
    ('ul', [
        '**Speakers and headphones**: choose the output (built-in speakers, headphones, HDMI for a projector or TV, Bluetooth, USB) '
        'and its connector; set the volume; **Test left**, **Test both** and **Test right** play a short sound on each side.',
        '"Allow louder than 100%" helps quiet laptop speakers (the sound may distort).',
        '**Microphone**: the input device, its connector and its level.',
        '**Sound card**: the profile of each card. A profile with HDMI sends the sound to a projector; for Bluetooth headphones '
        '"High Fidelity Playback (A2DP)" sounds best, "Headset" is for calls with the microphone.',
    ]),
    ('img', 'settings-sound', 'Sound: devices, volume and tests.'),
    ('h3', 'Clear Sound'),
    ('p', '**EasyEffects** improves the sound of every program. It is a separate program: press **Install EasyEffects…** once, '
          'then choose a sound. For speakers and headphones: Off, **Clear voice** (lessons, videos and calls), Music, Even volume, '
          'Laptop speakers, Loudness, Headphones and Bass (the last four are presets by JackHack96). For the microphone: '
          '**Clear microphone** (less background noise for online classes and recordings). The switch "Clear sound" in the sound '
          'popup of the panel turns it on or off quickly.'),
    ('img', 'settings-clear-sound', 'Clear Sound with EasyEffects.'),
    ('h3', 'Quality & Fixes'),
    ('ul', [
        '**Play music at its own rate** (44.1 or 48 kHz) instead of converting it.',
        '**Keep the sound card awake**: no cut-off first second and no pop; projectors keep their sound.',
        '**Bigger sound buffer**: no crackling on older or busy computers (a little delay).',
        '**Best converting quality** (uses more processor time).',
        '**Apply and restart the sound** uses the choices; **Reset sound settings** removes them again.',
        '**Check my sound** looks for the usual problems (muted, very low volume, no device, Bluetooth in phone mode, missing '
        'firmware) and offers a one-click fix for each.',
    ]),
    ('img', 'settings-sound-quality', 'Quality & Fixes with the result of "Check my sound".'),
    ('tip', 'No sound from the projector? Choose the HDMI output on the Sound tab, or the HDMI profile of the card, and press '
            '"Test both".'),
]),
('keyboard', 'Keyboard and shortcuts', [
    ('p', '**Keyboard**: the layouts (for example US, Portuguese, Indonesian), the key that switches between them, key repeat and '
          'Num Lock ("Automatic" switches it on for desktop computers and off for laptops). The panel shows the current layout.'),
    ('img', 'settings-keyboard', 'Keyboard.'),
    ('p', '**Shortcuts** lists every shortcut of LXQt and Eduka together. Untick a line to free its key. A key that LXQt, you or the '
          'window manager already use is never given a second job.'),
    ('table', ['Keys', 'What they do'], [
        ['[[Super]]', 'Open or close Eduka-Desktop'],
        ['[[Super+Q]]', 'Eduka-Quick'],
        ['[[Super+S]]', 'Search programs and files'],
        ['[[Super+R]] or [[Alt+F2]]', 'Run a command'],
        ['[[Super+V]]', 'Clipboard history'],
        ['[[Super+E]]', 'File manager'],
        ['[[Super+I]]', 'Eduka-Settings'],
        ['[[Super+A]]', 'Action Center'],
        ['[[Super+N]]', 'Notifications'],
        ['[[Super+D]]', 'Show the desktop (again: the windows come back)'],
        ['[[Super+M]] / [[Super+Shift+M]]', 'Minimize all windows / bring them back'],
        ['[[Super+Up]] / [[Super+Down]]', 'Maximize / restore the window'],
        ['[[Super+Left]] / [[Super+Right]]', 'Window on the left / right half of the screen'],
        ['[[Super+Shift+Left]] / [[Super+Shift+Right]]', 'Window to the screen on the left / right'],
        ['[[Ctrl+Super+Left]] / [[Ctrl+Super+Right]]', 'Previous / next workspace'],
        ['[[Alt+Tab]]', 'Switch between windows'],
        ['[[Alt+F4]]', 'Close the window'],
        ['[[Ctrl+Alt+Esc]]', 'Force close the program of the active window'],
        ['[[Ctrl+Shift+Esc]]', 'Task manager'],
        ['[[Ctrl+Alt+T]]', 'Terminal'],
        ['[[Super+L]]', 'Lock the screen'],
        ['[[Ctrl+Alt+Delete]]', 'Leave screen: lock, log out, sleep, restart, shut down'],
        ['[[Print]] / [[Alt+Print]]', 'Screenshot of the screen / of the window'],
        ['[[Super+Shift+S]]', 'Screenshot of an area'],
        ['[[Super+Print]]', 'Screenshot saved at once'],
        ['[[Super+Alt+R]]', 'Start or stop a screen recording'],
        ['[[Super+P]]', 'Screens and projector'],
        ['[[Super+.]]', 'Emoji and symbols'],
        ['[[Super+Space]]', 'Next keyboard layout'],
        ['[[Super+U]]', 'Accessibility settings'],
        ['[[Ctrl+Super+Enter]]', 'Screen reader on or off'],
        ['[[Ctrl+Super+O]]', 'On-screen keyboard on or off'],
        ['[[Super+=]]', 'Magnifier'],
    ]),
    ('img', 'settings-shortcuts', 'Keyboard → Shortcuts.'),
]),
('mouse', 'Mouse, touchpad, touch screen and pen', [
    ('ul', [
        '**Mouse**: pointer speed, left-handed buttons, double-click speed and the scroll wheel.',
        '**Touchpad**: on or off, tap to click (one finger left, two fingers right), natural scrolling, turn off while typing, '
        '**tap and drag** (tap, put the finger down again and move it) and **drag lock** (lifting the finger does not drop what '
        'you drag; tap to drop). Settings made without a touchpad are kept for when one is found.',
        '**Touch Screen**: the screen the touch belongs to, rotation, smooth finger scrolling, gestures with three and four fingers '
        'and the on-screen keyboard.',
        '**Pen tablet** (Touch Screen tab): with a projector or a second monitor the pen draws on one screen, so circles stay round.',
    ]),
    ('img', 'settings-touchpad', 'Mouse & Touch → Touchpad with tap and drag.'),
    ('img', 'settings-touchscreen', 'Mouse & Touch → Touch Screen and pen tablet.'),
]),
('system', 'Users, language, accessibility and Parental Control', [
    ('h3', 'Users'),
    ('p', 'Add and remove accounts, change names, passwords and pictures, and choose who is an administrator. Make one account '
          'per teacher (Administrator) and per pupil or class (Standard). Keep at least two administrator accounts at school.'),
    ('img', 'settings-users', 'Users.'),
    ('h3', 'Language & Time'),
    ('p', '**Language & Startup**: the language of Eduka-Desktop and of the other programs (Tetun, Portuguese, English, '
          'Indonesian …) and the programs that start after login. **Date & Time**: the time zone, network time and the clock.'),
    ('h3', 'Accessibility'),
    ('ul', [
        '**Vision**: strong contrast, large text, a bigger mouse pointer, less movement, the magnifier and the on-screen keyboard.',
        '**Hearing**: network, sound and alert status as text on Eduka-Panel, and mono sound (both ears and both speakers play everything).',
        '**Screen Reader**: Orca reads the screen aloud; choose and try the voice.',
    ]),
    ('img', 'settings-accessibility', 'Accessibility → Vision.'),
    ('h3', 'Parental Control and Privacy'),
    ('p', 'Parental Control sets a time limit for this computer and the time allowed, with recommendations by age (small children, '
          'primary school, teenagers, a computer lesson, homework). Eduka-Panel shows a friendly reminder to rest the eyes and move, '
          'also without a time limit, and a message before the computer shuts down. Changes need an administrator password. '
          '**Privacy** clears the recent files, thumbnails and the trash.'),
    ('img', 'settings-parental', 'Parental Control.'),
    ('h3', 'Login & Fingerprint'),
    ('p', 'The look of the login screen (SDDM, or LightDM as an option), automatic login (always asks for an administrator '
          'password) and fingerprint login: add a finger, then switch on "Use the fingerprint".'),
]),
('maintenance', 'Maintenance, memory, drivers and firmware', [
    ('ul', [
        '**Rebuild application list**: after installing or removing programs.',
        '**Reload Eduka-Desktop** and **Restart Eduka-Panel**: when the menu or the panel looks wrong or stops answering.',
        '**Repair LXQt theme and session**: when LXQt asks for a window manager or the theme looks wrong; the old settings are kept as a backup.',
        '**Drivers and firmware**: lists Wi-Fi, network, sound, graphics and Bluetooth devices that have no driver yet, with the '
        'firmware package to install ("Install the missing firmware…"). Restart the computer afterwards.',
        '**Memory**: memory saver, a warning before the memory is full, the programs that use the most memory, and zram and '
        'earlyoom, which keep computers with 2 to 4 GB of memory smooth.',
    ]),
    ('img', 'settings-maintenance', 'Maintenance with Drivers and firmware.'),
]),
('old-pc', 'Old computers, Wayland and Compiz', [
    ('h3', 'Old and slow computers'),
    ('ul', [
        'Choose **Eduka-Low-Theme** (Appearance → Theme): no transparency and no effects.',
        'Use **Openbox** as window manager (Windows & Workspaces → Windows) and keep the compositor on Automatic.',
        'Switch on zram and earlyoom (Maintenance → Memory); leave Clear Sound off on computers with 2 GB of memory.',
        'Record the screen with "15 pictures a second" and "Small file".',
    ]),
    ('h3', 'Wayland'),
    ('p', 'The usual session at school is X11. The LXQt Wayland session is for tests: Eduka-Desktop and Eduka-Panel run there '
          'through XWayland, and Eduka-Settings also writes the touchpad, mouse, keyboard, focus, middle-click and workspace '
          'settings into the Wayland compositor (labwc or KWin). Hot corners and Force Close work in X11 only.'),
    ('h3', 'Compiz'),
    ('p', 'Compiz adds 3D effects (wobbly windows, the cube, [[Super+W]] shows all windows side by side). It is installed '
          'separately ("Install Compiz (3D effects)…" on the Windows page) and needs real 3D graphics. If Compiz cannot start, '
          'xfwm4 or Openbox takes over by itself, so the windows always keep their borders.'),
]),
('help', 'Problems and help', [
    ('table', ['Problem', 'What to do'], [
        ['No sound', 'Sound → choose the right output and press "Test both"; Quality & Fixes → "Check my sound".'],
        ['Crackling sound', 'Quality & Fixes → "Bigger sound buffer" and "Keep the sound card awake", then "Apply and restart the sound".'],
        ['No sound on the projector', 'Choose the HDMI output or the HDMI profile of the card.'],
        ['Wi-Fi does not work', 'Maintenance → Drivers and firmware: install the firmware that is named, then restart.'],
        ['A program hangs', 'Wait, or [[Ctrl+Alt+Esc]] → Force Close.'],
        ['The menu or the panel looks wrong', 'Maintenance → Reload Eduka-Desktop / Restart Eduka-Panel.'],
        ['Everything is too small or too big', 'Display → Scale, then log out and in.'],
        ['The computer is slow', 'Eduka-Low-Theme, Openbox, zram and earlyoom (chapter "Old computers").'],
        ['Forgot the password', 'An administrator changes it in Users; with fingerprint login a new password can be set after logging in with the finger.'],
    ]),
    ('p', 'About Edukasaun Desktop (menu → About, or Maintenance → About) shows the version and the credits of the projects that '
          'Edukasaun Desktop uses. Website: www.edukasaunos.tl.'),
    ('img', 'about', 'About Edukasaun Desktop.', 'half'),
]),
]
