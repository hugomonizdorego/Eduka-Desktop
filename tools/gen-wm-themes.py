#!/usr/bin/env python3
"""Generate the xfwm4 and Openbox window border themes of the Eduka themes.

The xfwm4 assets that came with Orchis use GTK "symbolic" colors; LXQt has no
XSETTINGS daemon, so xfwm4 filled them with light default colors and the
white buttons became invisible. These themes use fixed colors only: a solid
title bar, round buttons with clear glyphs and a red close button.

    python3 tools/gen-wm-themes.py            # writes usr/share/themes/<name>/{xfwm4,openbox-3}
"""
import math, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'usr' / 'share' / 'themes'
TITLE_H = 30
BTN = 30          # button image size (square)
DOT = 18          # button circle diameter
SS = 4            # supersampling

THEMES = {
    # name: palette
    'Edukasaun-Dark': dict(title='#2c2c2c', title_in='#242424', text='#ffffff', text_in='#8c8c8c', border='#383838',
                           btn='#3d3d3d', btn_hover='#4f4f4f', btn_press='#26a69a', glyph='#e6e6e6', glyph_in='#8c8c8c',
                           close='#e5484d', close_hover='#ff5f63', accent='#26a69a', comment='Orchis dark colors (GPL-3.0)'),
    'Eduka-Transparan': dict(title='#1c1c1c', title_in='#191919', text='#f2f2f2', text_in='#9c9c9c', border='#2a2a2a',
                             btn='#333333', btn_hover='#454545', btn_press='#5c5c5c', glyph='#f2f2f2', glyph_in='#8f8f8f',
                             close='#c01c28', close_hover='#e01b24', accent='#9a9a9a',
                             comment='colors of Transparent-Shell-Theme by mrbrownstone07'),
    'Eduka-Low': dict(title='#323030', title_in='#2b2929', text='#f7f7f7', text_in='#aea79f', border='#3d3d3d',
                      btn='#454343', btn_hover='#5d5d5d', btn_press='#315bef', glyph='#f7f7f7', glyph_in='#aea79f',
                      close='#c7162b', close_hover='#e01b24', accent='#315bef', comment='Yaru-remix colors (CC BY-SA 4.0 / GPL-3.0)'),
    'Eduka-MultiColor': dict(title='#ffffff', title_in='#f5f5f5', text='#212121', text_in='#8a8a8a', border='#d9d9d9',
                             btn='#ececec', btn_hover='#dcdcdc', btn_press='#5b6ee1', glyph='#3d3d3d', glyph_in='#a0a0a0',
                             close='#ef5350', close_hover='#f44336', accent='#5b6ee1',
                             comment='Graphite light colors by vinceliuice (GPL-3.0)'),
}


def rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def hexc(c):
    return '#%02X%02X%02X' % tuple(max(0, min(255, int(round(v)))) for v in c)


def blend(a, b, t):
    return tuple(a[i]*(1-t)+b[i]*t for i in range(3))


def write_xpm(path, name, pixels, w, h):
    """pixels: rows of '#RRGGBB' or None (transparent)."""
    colors = {}
    for row in pixels:
        for c in row:
            if c not in colors:
                colors[c] = None
    keys = list(colors)
    chars = '.#abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+@$%&*=-;:>,<1234567890'
    if len(keys) <= len(chars):
        cpp = 1; codes = {k: chars[i] for i, k in enumerate(keys)}
    else:
        cpp = 2; codes = {k: chars[i // len(chars)] + chars[i % len(chars)] for i, k in enumerate(keys)}
    lines = ['/* XPM */', f'static char *{name}[] = {{', f'"{w} {h} {len(keys)} {cpp}",']
    for k in keys:
        lines.append(f'"{codes[k]} c {k if k else "None"}",')
    for i, row in enumerate(pixels):
        lines.append('"' + ''.join(codes[c] for c in row) + '"' + (',' if i < h-1 else ''))
    lines.append('};')
    path.write_text('\n'.join(lines) + '\n', encoding='ascii')


def coverage(fn, w, h):
    """Supersampled coverage (0..1) of shape fn(x, y) -> bool."""
    out = []
    for y in range(h):
        row = []
        for x in range(w):
            hit = 0
            for sy in range(SS):
                for sx in range(SS):
                    if fn(x + (sx+0.5)/SS, y + (sy+0.5)/SS): hit += 1
            row.append(hit / (SS*SS))
        out.append(row)
    return out


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx-ax, by-ay
    t = max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy or 1)))
    return math.hypot(px-(ax+t*dx), py-(ay+t*dy))


def glyph_fn(kind, cx, cy, s):
    """Glyph strokes inside the circle (s = half size of the glyph box)."""
    lw = 1.05
    segs = []
    if kind == 'close':
        segs = [(cx-s, cy-s, cx+s, cy+s), (cx-s, cy+s, cx+s, cy-s)]
    elif kind == 'hide':
        segs = [(cx-s, cy+s*0.15, cx+s, cy+s*0.15)]
    elif kind == 'maximize':
        a = s*0.95
        segs = [(cx-a, cy-a, cx+a, cy-a), (cx+a, cy-a, cx+a, cy+a), (cx+a, cy+a, cx-a, cy+a), (cx-a, cy+a, cx-a, cy-a)]
    elif kind == 'maximize-toggled':
        a = s*0.7; o = s*0.35
        segs = [(cx-a-o, cy-a+o, cx+a-o, cy-a+o), (cx+a-o, cy-a+o, cx+a-o, cy+a+o), (cx+a-o, cy+a+o, cx-a-o, cy+a+o), (cx-a-o, cy+a+o, cx-a-o, cy-a+o),
                (cx-a+o, cy-a-o, cx+a+o, cy-a-o), (cx+a+o, cy-a-o, cx+a+o, cy+a-o)]
    elif kind in ('shade', 'shade-toggled'):
        d = 1 if kind == 'shade' else -1
        segs = [(cx-s, cy+d*s*0.4, cx, cy-d*s*0.5), (cx, cy-d*s*0.5, cx+s, cy+d*s*0.4)]
    elif kind in ('stick', 'stick-toggled'):
        r = s*(0.5 if kind == 'stick' else 0.8)
        return lambda x, y: math.hypot(x-cx, y-cy) <= r
    elif kind == 'menu':
        segs = [(cx-s, cy-s*0.5, cx+s, cy-s*0.5), (cx-s, cy+s*0.1, cx+s, cy+s*0.1), (cx-s, cy+s*0.7, cx+s, cy+s*0.7)]
    return lambda x, y: any(seg_dist(x, y, *sg) <= lw for sg in segs)


def button_pixels(p, kind, state):
    bg = rgb(p['title'] if state != 'inactive' else p['title_in'])
    if kind == 'close':
        circle = {'active': p['close'], 'inactive': p['btn'], 'prelight': p['close_hover'], 'pressed': p['close']}[state]
        glyph = '#ffffff' if state != 'inactive' else p['glyph_in']
    else:
        circle = {'active': p['btn'], 'inactive': p['title_in'], 'prelight': p['btn_hover'], 'pressed': p['btn_press']}[state]
        glyph = p['glyph'] if state != 'inactive' else p['glyph_in']
        if state == 'pressed': glyph = '#ffffff'
    cx = cy = BTN/2; r = DOT/2
    circ = coverage(lambda x, y: math.hypot(x-cx, y-cy) <= r, BTN, BTN)
    g = coverage(glyph_fn(kind, cx, cy, 3.6), BTN, BTN)
    rows = []
    for y in range(BTN):
        row = []
        for x in range(BTN):
            c = blend(bg, rgb(circle), circ[y][x])
            c = blend(c, rgb(glyph), g[y][x] * (1 if circ[y][x] > 0.5 else 0))
            row.append(hexc(c))
        rows.append(row)
    return rows


def solid(color, w, h):
    return [[color]*w for _ in range(h)]


def corner(p, state, side):
    """Rounded top corner (radius 7): outside pixels are transparent."""
    bg = p['title'] if state == 'active' else p['title_in']
    w = 8; r = 7
    cov = coverage((lambda x, y: math.hypot(x-r, y-r) <= r or y >= r or x >= r) if side == 'left'
                   else (lambda x, y: math.hypot(x-(w-r), y-r) <= r or y >= r or x <= w-r), w, TITLE_H)
    return [[(bg if c > 0.5 else None) for c in row] for row in cov]


def make_xfwm4(name, p):
    d = ROOT / name / 'xfwm4'
    d.mkdir(parents=True, exist_ok=True)
    for f in d.iterdir():
        f.unlink()
    (d / 'themerc').write_text(f"""# {name} for xfwm4 - generated by tools/gen-wm-themes.py ({p['comment']})
button_layout=O|HMC
button_offset=4
button_spacing=2
full_width_title=true
title_alignment=center
title_shadow_active=false
title_shadow_inactive=false
title_vertical_offset_active=0
title_vertical_offset_inactive=0
title_horizontal_offset=4
maximized_offset=0
show_app_icon=false
active_text_color={p['text']}
inactive_text_color={p['text_in']}
active_border_color={p['border']}
inactive_border_color={p['border']}
shadow_delta_height=2
shadow_delta_width=0
shadow_delta_x=0
shadow_delta_y=-5
shadow_opacity=40
""", encoding='utf-8')
    for state in ('active', 'inactive'):
        col = p['title'] if state == 'active' else p['title_in']
        for i in range(1, 6):
            write_xpm(d / f'title-{i}-{state}.xpm', f'title_{i}_{state}', solid(col, 4, TITLE_H), 4, TITLE_H)
        write_xpm(d / f'top-left-{state}.xpm', 'top_left', corner(p, state, 'left'), 8, TITLE_H)
        write_xpm(d / f'top-right-{state}.xpm', 'top_right', corner(p, state, 'right'), 8, TITLE_H)
        for part, (w, h) in {'left': (1, 8), 'right': (1, 8), 'bottom': (8, 1), 'bottom-left': (1, 1), 'bottom-right': (1, 1)}.items():
            write_xpm(d / f'{part}-{state}.xpm', part.replace('-', '_'), solid(p['border'], w, h), w, h)
    for kind in ('close', 'hide', 'maximize', 'maximize-toggled', 'shade', 'shade-toggled', 'stick', 'stick-toggled', 'menu'):
        for state in ('active', 'inactive', 'prelight', 'pressed'):
            write_xpm(d / f'{kind}-{state}.xpm', f"{kind.replace('-', '_')}_{state}", button_pixels(p, kind, state), BTN, BTN)


def make_openbox(name, p):
    d = ROOT / name / 'openbox-3'
    d.mkdir(parents=True, exist_ok=True)
    (d / 'themerc').write_text(f"""# {name} for Openbox - generated by tools/gen-wm-themes.py ({p['comment']})
border.width: 1
padding.width: 8
padding.height: 6
window.handle.width: 0
window.client.padding.width: 0
window.client.padding.height: 0
window.label.text.justify: center
window.active.label.text.font: shadow=n
window.inactive.label.text.font: shadow=n
window.active.border.color: {p['border']}
window.inactive.border.color: {p['border']}
window.active.client.color: {p['title']}
window.inactive.client.color: {p['title_in']}
window.active.title.separator.color: {p['title']}
window.inactive.title.separator.color: {p['title_in']}
window.active.title.bg: flat solid
window.active.title.bg.color: {p['title']}
window.inactive.title.bg: flat solid
window.inactive.title.bg.color: {p['title_in']}
window.active.label.bg: parentrelative
window.inactive.label.bg: parentrelative
window.active.label.text.color: {p['text']}
window.inactive.label.text.color: {p['text_in']}
window.active.button.unpressed.bg: flat solid
window.active.button.unpressed.bg.color: {p['btn']}
window.active.button.unpressed.image.color: {p['glyph']}
window.active.button.hover.bg: flat solid
window.active.button.hover.bg.color: {p['btn_hover']}
window.active.button.hover.image.color: #ffffff
window.active.button.pressed.bg: flat solid
window.active.button.pressed.bg.color: {p['btn_press']}
window.active.button.pressed.image.color: #ffffff
window.active.button.disabled.bg: parentrelative
window.active.button.disabled.image.color: {p['glyph_in']}
window.active.button.toggled.bg: flat solid
window.active.button.toggled.bg.color: {p['btn']}
window.active.button.toggled.image.color: {p['accent']}
window.inactive.button.unpressed.bg: parentrelative
window.inactive.button.unpressed.image.color: {p['glyph_in']}
window.inactive.button.hover.bg: flat solid
window.inactive.button.hover.bg.color: {p['btn_hover']}
window.inactive.button.hover.image.color: #ffffff
window.inactive.button.pressed.bg: flat solid
window.inactive.button.pressed.bg.color: {p['btn_press']}
window.inactive.button.pressed.image.color: #ffffff
window.inactive.button.disabled.bg: parentrelative
window.inactive.button.disabled.image.color: {p['glyph_in']}
window.inactive.button.toggled.bg: parentrelative
window.inactive.button.toggled.image.color: {p['glyph_in']}
window.active.button.close.unpressed.bg: flat solid
window.active.button.close.unpressed.bg.color: {p['close']}
window.active.button.close.unpressed.image.color: #ffffff
window.active.button.close.hover.bg: flat solid
window.active.button.close.hover.bg.color: {p['close_hover']}
window.active.button.close.hover.image.color: #ffffff
window.active.handle.bg: flat solid
window.active.handle.bg.color: {p['title']}
window.inactive.handle.bg: flat solid
window.inactive.handle.bg.color: {p['title_in']}
window.active.grip.bg: flat solid
window.active.grip.bg.color: {p['title']}
window.inactive.grip.bg: flat solid
window.inactive.grip.bg.color: {p['title_in']}
menu.border.width: 1
menu.border.color: {p['border']}
menu.items.bg: flat solid
menu.items.bg.color: {p['title']}
menu.items.text.color: {p['text']}
menu.items.disabled.text.color: {p['text_in']}
menu.items.active.bg: flat solid
menu.items.active.bg.color: {p['accent']}
menu.items.active.text.color: #ffffff
menu.title.bg: flat solid
menu.title.bg.color: {p['title_in']}
menu.title.text.color: {p['text']}
menu.separator.color: {p['border']}
osd.border.width: 1
osd.border.color: {p['border']}
osd.bg: flat solid
osd.bg.color: {p['title']}
osd.label.text.color: {p['text']}
osd.hilight.bg: flat solid
osd.hilight.bg.color: {p['accent']}
osd.unhilight.bg: flat solid
osd.unhilight.bg.color: {p['btn']}
""", encoding='utf-8')


if __name__ == '__main__':
    names = sys.argv[1:] or list(THEMES)
    for n in names:
        make_xfwm4(n, THEMES[n]); make_openbox(n, THEMES[n])
        print('generated', n)
