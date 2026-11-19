#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Recolor the Eduka-Pastel GTK theme from mint green to the soft blue of the
Edukasaun OS logo (0.11 Pre-Stable).

The logo is #1E88E5. The theme uses a calmer shade of it (#3B87D4, and
#2C72BA where white text sits on it), and only a faint blue tint on the
surfaces, so the default look follows the logo without shouting.

    python3 tools/recolor-pastel.py          # rewrites usr/share/themes/Eduka-Pastel/gtk-*

The xfwm4 and openbox-3 window borders come from tools/gen-wm-themes.py.
Running this twice changes nothing (every old color is gone after the first run).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent/'usr'/'share'/'themes'/'Eduka-Pastel'

# Light variant (gtk.css): mint → logo blue, mint-tinted whites → blue-tinted.
LIGHT = {
    '#3FA684': '#3B87D4', '#2F8F6F': '#2C72BA', '#FCFEFD': '#FCFDFF', '#F6FBF9': '#F6F9FD',
    '#F2F8F6': '#F2F6FB', '#D7EAE4': '#D7E3F0', '#E9F8F0': '#E9F1FA', '#DDEDE8': '#DDE7F2',
    '#D6F1E4': '#D6E6F6', '#6FCAA8': '#73AEE6',
}
# Dark variant (gtk-dark.css): a lighter blue reads well on the dark grey.
DARK = {'#3FA684': '#5A9BE0', '#6FCAA8': '#80B4EA', '#2F8F6F': '#3F84CC'}
RGB = {
    (47, 143, 111): (44, 114, 186), (63, 166, 132): (59, 135, 212), (252, 254, 253): (252, 253, 255),
    (242, 248, 246): (242, 246, 251), (119, 182, 161): (110, 160, 212), (52, 117, 95): (40, 96, 156),
    (232, 234, 233): (232, 234, 237), (231, 235, 233): (231, 234, 238), (182, 186, 185): (182, 185, 190),
}
RGB_DARK = {**RGB, (63, 166, 132): (90, 155, 224)}
# GTK 2 still had the green of Orchis.
GTK2 = {'#4CAF50': '#2C72BA'}


def recolor_text(text, table, rgb):
    def hex_sub(m):
        return table.get(m.group(0).upper(), m.group(0))
    text = re.sub(r'#[0-9a-fA-F]{6}\b', hex_sub, text)

    def rgb_sub(m):
        key = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
        if key not in rgb:
            return m.group(0)
        r, g, b = rgb[key]
        return f'{m.group(1)}({r}, {g}, {b}'
    return re.sub(r'(rgba?)\(\s*(\d+),\s*(\d+),\s*(\d+)', rgb_sub, text)


def recolor_png(path):
    """Green pixels of the GTK 2 assets turn blue (hue moved, lightness kept)."""
    import colorsys
    from PyQt5.QtGui import QImage, QColor
    im = QImage(str(path))
    if im.isNull():
        return False
    im = im.convertToFormat(QImage.Format_ARGB32)
    changed = False
    for y in range(im.height()):
        for x in range(im.width()):
            c = im.pixelColor(x, y)
            if not c.alpha():
                continue
            h, l, s = colorsys.rgb_to_hls(c.red()/255, c.green()/255, c.blue()/255)
            if s > 0.18 and 0.22 < h < 0.48:          # green to teal
                nr, ng, nb = colorsys.hls_to_rgb(0.585, l, min(1.0, s*0.9))
                im.setPixelColor(x, y, QColor(round(nr*255), round(ng*255), round(nb*255), c.alpha()))
                changed = True
    if changed:
        im.save(str(path), 'PNG')
    return changed


def main():
    if not ROOT.is_dir():
        sys.exit(f'{ROOT} is missing')
    done = []
    for css in sorted(ROOT.glob('gtk-[34].0/*.css')):
        dark = css.name.endswith('-dark.css')
        old = css.read_text(encoding='utf-8')
        new = recolor_text(old, {**LIGHT, **DARK} if dark else LIGHT, RGB_DARK if dark else RGB)
        if new != old:
            css.write_text(new, encoding='utf-8'); done.append(str(css.relative_to(ROOT)))
    for rc in sorted(ROOT.glob('gtk-2.0/*rc')):
        old = rc.read_text(encoding='utf-8')
        new = recolor_text(old, GTK2, {})
        if new != old:
            rc.write_text(new, encoding='utf-8'); done.append(str(rc.relative_to(ROOT)))
    for png in sorted(ROOT.glob('gtk-2.0/assets/*.png')):
        if recolor_png(png):
            done.append(str(png.relative_to(ROOT)))
    print(f'{len(done)} files recolored')


if __name__ == '__main__':
    main()
