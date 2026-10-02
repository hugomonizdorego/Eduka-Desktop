Edukasaun Desktop Suite 0.9.21

All included components use the same version number:
- Eduka-Desktop 0.9.21
- Eduka-Panel 0.9.21
- Eduka-Menu 0.9.21
- Eduka-Settings 0.9.21

Changes in this patch (compositor):
- Compositor check: Eduka-Settings → Appearance → Compositor shows which compositor draws the desktop (picom, xfwm4, KWin, ...), its backend, who started it, the window manager and whether the computer is a virtual machine. "Copy report" copies the details for help.
- Compositor choice: Automatic (recommended), picom XRender, picom OpenGL, the window manager's own compositor, or Off. xfwm4's compositor is switched on or off to match, so two compositors never fight.
- picom settings follow the installed picom version, based on picom's upstream changelog (github.com/yshui/picom): --backend is always given (picom 12 refuses to start without it), options an older picom does not know are never passed (they make it exit), frame pacing is off on picom 12.0 / 12.1 (random screen delays, #1345), picom 12.0 is restarted after a monitor change (#1338), and the report warns about picom 12.0–12.2 (#1350).
- Full-screen videos and games bypass the compositor (--unredir-if-possible with a 500 ms delay against flicker). OpenGL with vsync only on real 3D graphics; VirtualBox, other virtual machines and software rendering (llvmpipe) use XRender.
- picom that keeps crashing no longer makes Eduka-Panel restart again and again: after 3 crashes in 5 minutes it is not started again (opaque look) until "Restart compositor". A picom that died is now noticed even while it is a zombie process.
- picom warnings go to $XDG_RUNTIME_DIR/eduka-desktop/picom.log and appear in the report.
- New command eduka-compositor: report, "restart" and "set auto|xrender|glx|wm|off".
- About: picom (Yuxuan Shui and contributors) added to the credits.

The Tetun check against the Timor Aid dictionary follows when www.timoraid.org can be reached from the build environment.
Development continues toward 0.10.0 and the final version 1.1.12 (November 2026).
