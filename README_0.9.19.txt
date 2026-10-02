Edukasaun Desktop Suite 0.9.19

All included components use the same version number:
- Eduka-Desktop 0.9.19
- Eduka-Panel 0.9.19
- Eduka-Menu 0.9.19
- Eduka-Settings 0.9.19

Changes in this patch:
- New login screen (SDDM): a row of user pictures (click one, or "Other user…" to type a name), a password field with the login arrow, and a bottom bar with session, keyboard layout, Language, Accessibility (larger text, high contrast, on-screen keyboard) and Power (suspend, hibernate, restart, shut down). The login screen speaks English, Portuguese (PT/BR), Tetun, Indonesian, Malay, Filipino, Thai, Vietnamese and Chinese (simplified/traditional).
- Languages: Eduka-Desktop now follows the language chosen when the computer starts (or on the login screen) instead of staying in English. Portuguese, Brazilian Portuguese, Indonesian and Tetun are fully translated; Malay, Filipino, Thai, Vietnamese and Chinese cover the most visible texts. Dates follow the language too.
- Tetun is built into Eduka-Desktop (there is no system language pack): Eduka-Settings → Language & Startup offers only "System language" and "Tetun (Tetum)"; other programs fall back to Portuguese with Tetun.
- The language picked on the login screen is used for the desktop after login (only for that user, and only languages from the list).
- Clock: the LED clock has no black box any more, and one clock color now applies to the digital, analog and LED clock ("A" follows the theme).
- Action Center: clicking the clock for the globe no longer pushes the Action Center below Eduka-Panel or off the screen; the middle part scrolls when space is short, tiles never hide under the scroll bar and the greeting wraps instead of being cut.
- Action Center opens at once: icon lookups used to search the icon folders again and again (several seconds on slow disks and in VirtualBox); icons are now indexed once.
- Helpers of virtual machines (VirtualBox guest additions, VMware, SPICE, QEMU agent) no longer appear in Eduka-Desktop or on the taskbar.
- Rounded corners everywhere: tooltips, menus, popups, notification bubbles and Eduka-Panel are rounded also without a compositor (Eduka-Low-Theme, VirtualBox without 3D); drop-down lists in Eduka-Settings are rounded.
- Smoother themes: the categories of Eduka-Desktop fit on 1366x768 and 1024x600 screens without a scroll bar, the clock button on Eduka-Panel shows time and date, rounded handle buttons in the Action Center.

Development continues toward the final version 1.1.12 (November 2026).
