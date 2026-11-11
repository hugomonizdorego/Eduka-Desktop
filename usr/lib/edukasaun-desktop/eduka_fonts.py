#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fonts for the whole desktop (Eduka-Settings → Appearance → Fonts).

One choice is written where the programs of an Eduka-Desktop session read
fonts, the way LXQt Appearance, lxappearance and GNOME write them:

- Qt and LXQt: ~/.config/lxqt/lxqt.conf [Qt] font and fixedFont (running Qt
  programs follow at once: LXQt's platform plugin watches the file)
- GTK 3 and 4: settings.ini gtk-font-name and gtk-xft-*; GTK 2: ~/.gtkrc-2.0
- the GNOME keys read by GTK 4, Electron and Flatpak programs
- fontconfig: ~/.config/fontconfig/conf.d/50-eduka-fonts.conf (smoothing for
  every program, and the monospace font for terminals)
- X resources (Xft.*) for older X programs, merged at once with xrdb
- desktop icons: pcmanfm-qt [Desktop] Font
- window titles: Openbox (rc.xml) and xfwm4 (xfconf)

Every change writes only the places of the font that changed, so fonts chosen
with other tools stay as they are until they are changed here.
"""
import json, os, re, shutil, subprocess, time
from pathlib import Path
from xml.sax.saxutils import escape

from eduka_common import (DESKTOP_CONFIG_DIR, child_env, safe_popen, write_json, _get_ini_value, _set_ini_value,
                          _home, _openbox_rc_files, _xfwm4_get, _xfwm4_set, _write_atomic_text, _real_file)

FONTS_FILE = DESKTOP_CONFIG_DIR/'fonts.json'
LXQT_CONF = _home('.config', 'lxqt', 'lxqt.conf')
LXQT_SYSTEM_CONF = Path('/usr/share/lxqt/lxqt.conf')
GTK3 = _home('.config', 'gtk-3.0', 'settings.ini')
GTK4 = _home('.config', 'gtk-4.0', 'settings.ini')
GTK2 = _home('.gtkrc-2.0')
XRESOURCES = _home('.Xresources')
FONTCONFIG_FILE = _home('.config', 'fontconfig', 'conf.d', '50-eduka-fonts.conf')
PCMANFM_CONF = _home('.config', 'pcmanfm-qt', 'lxqt', 'settings.conf')
FONTCONFIG_MARK = 'Written by Eduka-Settings (Appearance → Fonts)'

ROLES = ('default', 'desktop', 'document', 'monospace', 'title')
HINTING = ('none', 'slight', 'medium', 'full')
ANTIALIAS = ('none', 'grayscale', 'rgba')
RGBA = ('rgb', 'bgr', 'vrgb', 'vbgr')
SCALE_MIN, SCALE_MAX = 0.8, 2.0

DEFAULT_RENDER = {'hinting': 'slight', 'antialias': 'grayscale', 'rgba': 'rgb', 'scale': 1.0}

# CSS / OpenType weights and the names Pango and the font dialogs use.
WEIGHT_NAMES = ((100, 'Thin'), (200, 'Extra Light'), (300, 'Light'), (400, 'Regular'), (500, 'Medium'),
                (600, 'Semi-Bold'), (700, 'Bold'), (800, 'Extra Bold'), (900, 'Black'))
# Qt 5 weights (QFont::Weight) for the same steps.
QT5_WEIGHTS = ((100, 0), (200, 12), (300, 25), (400, 50), (500, 57), (600, 63), (700, 75), (800, 81), (900, 87))


def _clean_family(name):
    name = re.sub(r'[\x00-\x1f,"<>&\\]', '', str(name or '')).strip()
    return name[:80]


def make_font(family, size=10, weight=400, italic=False):
    try: size = float(size)
    except (TypeError, ValueError): size = 10.0
    try: weight = int(weight)
    except (TypeError, ValueError): weight = 400
    size = min(72.0, max(5.0, round(size * 2) / 2))
    weight = min(900, max(100, int(round(weight / 100.0)) * 100))
    return {'family': _clean_family(family) or 'Sans', 'size': size, 'weight': weight, 'italic': bool(italic)}


def weight_name(weight):
    return min(WEIGHT_NAMES, key=lambda item: abs(item[0] - int(weight)))[1]


def size_text(size):
    return ('%g' % float(size))


def describe(font):
    """'Ubuntu Regular 10': the label of a font button, as in other desktops."""
    style = weight_name(font['weight'])
    if font.get('italic'):
        style = 'Italic' if style == 'Regular' else style + ' Italic'
    return f"{font['family']} {style} {size_text(font['size'])}"


def pango_string(font):
    """A Pango font description: GTK, GNOME keys and xfwm4."""
    style = [] if font['weight'] == 400 else [weight_name(font['weight']).replace(' ', '-')]
    if font.get('italic'): style.append('Italic')
    return ' '.join([font['family']] + style + [size_text(font['size'])])


def qt_weight(weight):
    return min(QT5_WEIGHTS, key=lambda item: abs(item[0] - int(weight)))[1]


def css_weight(qt5_weight):
    """The CSS weight of a Qt 5 weight (QFont.weight())."""
    return min(QT5_WEIGHTS, key=lambda item: abs(item[1] - int(qt5_weight)))[0]


def qt_string(font):
    """QFont::toString() in the Qt 5 form, which Qt 6 (LXQt 2) reads too."""
    return f"{font['family']},{size_text(font['size'])},-1,5,{qt_weight(font['weight'])},{1 if font.get('italic') else 0},0,0,0,0"


def parse_qt_string(text):
    """A font from QFont::toString() of Qt 5 (10/11 fields) or Qt 6 (16/17 fields)."""
    text = str(text or '').strip().strip('"')
    parts = text.split(',')
    if not parts or not parts[0].strip():
        return None
    family = parts[0]
    try: size = float(parts[1]) if len(parts) > 1 and float(parts[1]) > 0 else 10.0
    except ValueError: size = 10.0
    weight = 400
    if len(parts) >= 5:
        try:
            raw = int(parts[4])
            if len(parts) >= 16:
                weight = raw
            else:
                weight = css_weight(raw)
        except ValueError:
            pass
    italic = len(parts) >= 6 and parts[5].strip() not in ('', '0')
    return make_font(family, size, weight, italic)


def parse_pango_string(text):
    """A font from a Pango description such as 'DejaVu Sans Mono Bold 10'."""
    words = str(text or '').strip().strip("'\"").split()
    if not words:
        return None
    size = 10.0
    if re.match(r'^\d+(\.\d+)?$', words[-1]):
        size = float(words.pop())
    weight, italic = 400, False
    names = {n.lower().replace(' ', '-'): w for w, n in WEIGHT_NAMES}
    names.update({'normal': 400, 'book': 400, 'regular': 400, 'semibold': 600, 'demibold': 600, 'demi-bold': 600,
                  'ultra-light': 200, 'ultralight': 200, 'extralight': 200, 'ultra-bold': 800, 'ultrabold': 800,
                  'extrabold': 800, 'heavy': 900})
    while words and words[-1].lower() in tuple(names) + ('italic', 'oblique'):
        word = words.pop().lower()
        if word in ('italic', 'oblique'): italic = True
        else: weight = names[word]
    return make_font(' '.join(words) or 'Sans', size, weight, italic) if words else None


def _gsettings_get(schema, key):
    if not shutil.which('gsettings'):
        return None
    try:
        out = subprocess.run(['gsettings', 'get', schema, key], capture_output=True, text=True, timeout=3)
        return out.stdout.strip().strip("'") if out.returncode == 0 else None
    except Exception:
        return None


def _gsettings_set(schema, key, value):
    if shutil.which('gsettings'):
        safe_popen(['gsettings', 'set', schema, key, str(value)])


def read_saved():
    try:
        data = json.loads(FONTS_FILE.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save(update):
    data = read_saved(); data.update(update)
    try:
        write_json(FONTS_FILE, data)
    except Exception:
        pass


def _openbox_title_font():
    for path in _openbox_rc_files():
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        m = re.search(r'<font\s+place="ActiveWindow"\s*>(.*?)</font>', text, re.S)
        if not m: continue
        body = m.group(1)
        def tag(name, default=''):
            t = re.search(r'<%s>\s*([^<]*?)\s*</%s>' % (name, name), body)
            return t.group(1) if t else default
        try: size = float(tag('size', '9') or 9)
        except ValueError: size = 9.0
        return make_font(tag('name', 'Sans') or 'Sans', size, 700 if tag('weight').lower() == 'bold' else 400,
                         tag('slant').lower() in ('italic', 'oblique'))
    return None


def current_fonts():
    """The five fonts as they are now (saved choice, else what the programs read)."""
    saved = read_saved().get('fonts') or {}
    fonts = {}
    base = (parse_qt_string(_get_ini_value(LXQT_CONF, 'Qt', 'font'))
            or parse_qt_string(_get_ini_value(LXQT_SYSTEM_CONF, 'Qt', 'font'))
            or make_font('Sans', 10))
    fonts['default'] = base
    fonts['desktop'] = parse_qt_string(_get_ini_value(PCMANFM_CONF, 'Desktop', 'Font')) or dict(base)
    fonts['document'] = (parse_pango_string(_gsettings_get('org.gnome.desktop.interface', 'document-font-name'))
                         if 'document' not in saved else None) or dict(base)
    fonts['monospace'] = parse_qt_string(_get_ini_value(LXQT_CONF, 'Qt', 'fixedFont')) or make_font('Monospace', base['size'])
    fonts['title'] = _openbox_title_font() or parse_pango_string(_xfwm4_get('/general/title_font')) or make_font(base['family'], base['size'], 700)
    # The document font has no file of its own outside GNOME: the saved one.
    value = saved.get('document')
    if isinstance(value, dict) and value.get('family'):
        fonts['document'] = make_font(value.get('family'), value.get('size'), value.get('weight'), value.get('italic'))
    return fonts


def current_rendering():
    saved = read_saved().get('render') or {}
    render = dict(DEFAULT_RENDER)
    gtk_hint = (_get_ini_value(GTK3, 'Settings', 'gtk-xft-hintstyle') or '').strip('"')
    gtk_hinting = (_get_ini_value(GTK3, 'Settings', 'gtk-xft-hinting') or '').strip()
    if gtk_hinting == '0': render['hinting'] = 'none'
    elif gtk_hint.startswith('hint') and gtk_hint[4:] in HINTING: render['hinting'] = gtk_hint[4:]
    aa = (_get_ini_value(GTK3, 'Settings', 'gtk-xft-antialias') or '').strip()
    rgba = (_get_ini_value(GTK3, 'Settings', 'gtk-xft-rgba') or '').strip('"')
    if aa == '0': render['antialias'] = 'none'
    elif rgba in RGBA: render['antialias'], render['rgba'] = 'rgba', rgba
    elif aa == '1': render['antialias'] = 'grayscale'
    for key, allowed in (('hinting', HINTING), ('antialias', ANTIALIAS), ('rgba', RGBA)):
        if saved.get(key) in allowed: render[key] = saved[key]
    try:
        render['scale'] = min(SCALE_MAX, max(SCALE_MIN, float(saved.get('scale', render['scale']))))
    except (TypeError, ValueError):
        pass
    return render


# ---------------------------------------------------------------------------
# Writing

def _set_ini_if(path, section, key, value):
    if _get_ini_value(path, section, key) != value:
        _set_ini_value(path, section, key, value)


def _gtk2_lines(values):
    """~/.gtkrc-2.0 is edited line by line: the other lines stay."""
    try:
        path = _real_file(GTK2)
        old = path.read_text(encoding='utf-8', errors='ignore') if path.exists() else ''
        keys = tuple(values)
        lines = [l for l in old.splitlines() if not l.strip().startswith(keys)]
        lines += [f'{k}={v}' for k, v in values.items()]
        text = '\n'.join(lines) + '\n'
        if text != old:
            path.write_text(text, encoding='utf-8')
    except Exception:
        pass


def _xresources(values):
    try:
        path = _real_file(XRESOURCES)
        old = path.read_text(encoding='utf-8', errors='ignore') if path.exists() else ''
        keys = tuple(k + ':' for k in values)
        lines = [l for l in old.splitlines() if not l.replace(' ', '').startswith(tuple(k.replace(' ', '') for k in keys))]
        lines += [f'{k}: {v}' for k, v in values.items()]
        text = '\n'.join(lines) + '\n'
        if text != old:
            path.write_text(text, encoding='utf-8')
    except Exception:
        return
    if os.environ.get('DISPLAY') and shutil.which('xrdb'):
        try:
            subprocess.run(['xrdb', '-merge', str(XRESOURCES)], timeout=3, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, env=child_env())
        except Exception:
            pass


def _write_fontconfig(render, mono):
    """Smoothing for every program, and the monospace font for terminals.
    Only Eduka's own file is replaced."""
    try:
        if FONTCONFIG_FILE.exists() and FONTCONFIG_MARK not in FONTCONFIG_FILE.read_text(encoding='utf-8', errors='ignore'):
            return False
        aa = render['antialias'] != 'none'
        hint = render['hinting'] != 'none'
        rgba = render['rgba'] if render['antialias'] == 'rgba' else 'none'
        lines = ['<?xml version="1.0"?>', '<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">',
                 f'<!-- {FONTCONFIG_MARK}; replaced on every change. -->', '<fontconfig>',
                 '  <match target="font">',
                 f'    <edit name="antialias" mode="assign"><bool>{str(aa).lower()}</bool></edit>',
                 f'    <edit name="hinting" mode="assign"><bool>{str(hint).lower()}</bool></edit>',
                 f'    <edit name="hintstyle" mode="assign"><const>hint{render["hinting"]}</const></edit>',
                 f'    <edit name="rgba" mode="assign"><const>{rgba}</const></edit>',
                 f'    <edit name="lcdfilter" mode="assign"><const>{"lcddefault" if rgba != "none" else "lcdnone"}</const></edit>',
                 '  </match>']
        if mono and mono.get('family') and mono['family'].lower() not in ('monospace', 'mono'):
            lines += ['  <alias binding="same">', '    <family>monospace</family>',
                      f'    <prefer><family>{escape(mono["family"])}</family></prefer>', '  </alias>']
        lines.append('</fontconfig>')
        text = '\n'.join(lines) + '\n'
        if FONTCONFIG_FILE.exists() and FONTCONFIG_FILE.read_text(encoding='utf-8', errors='ignore') == text:
            return False
        FONTCONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        _write_atomic_text(FONTCONFIG_FILE, text)
        return True
    except Exception:
        return False


LXQT_FONTCONFIG = _home('.config', 'fontconfig', 'fonts.conf')

def _update_lxqt_fontconfig(render, dpi):
    """LXQt Appearance keeps its smoothing in ~/.config/fontconfig/fonts.conf,
    read after Eduka's file: the same values are written there, so both
    tools show and use one setting."""
    try:
        path = _real_file(LXQT_FONTCONFIG)
        if not path.is_file():
            return False
        text = path.read_text(encoding='utf-8', errors='ignore')
        if 'lxqt-config-appearance' not in text:
            return False
        aa = render['antialias'] != 'none'
        rgba = render['rgba'] if render['antialias'] == 'rgba' else 'none'
        values = {'antialias': ('bool', str(aa).lower()), 'hinting': ('bool', str(render['hinting'] != 'none').lower()),
                  'hintstyle': ('const', 'hint' + render['hinting']), 'rgba': ('const', rgba),
                  'lcdfilter': ('const', 'lcddefault' if rgba != 'none' else 'lcdnone'), 'dpi': ('double', str(dpi))}
        new = text
        for name, (kind, value) in values.items():
            new = re.sub(r'(<edit\s+name="%s"[^>]*>\s*<%s>)[^<]*(</%s>)' % (name, kind, kind),
                         lambda m: m.group(1) + value + m.group(2), new)
        if new != text:
            _write_atomic_text(path, new)
        return True
    except Exception:
        return False


def _pcmanfm_running():
    try:
        from eduka_wallpaper import pcmanfm_desktop_running
        return pcmanfm_desktop_running()
    except Exception:
        return False


def _set_desktop_font(font):
    """pcmanfm-qt saves its settings when it quits: quit first, write after,
    then the desktop icons start again with the new font."""
    value = '"' + qt_string(font) + '"'
    if _get_ini_value(PCMANFM_CONF, 'Desktop', 'Font') == value:
        return False
    running = _pcmanfm_running() and shutil.which('pcmanfm-qt')
    if running:
        subprocess.run(['pcmanfm-qt', '--profile=lxqt', '--quit'], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=10, env=child_env())
        for _ in range(50):
            if not _pcmanfm_running(): break
            time.sleep(0.1)
    _set_ini_value(PCMANFM_CONF, 'Desktop', 'Font', value)
    if running:
        subprocess.Popen(['pcmanfm-qt', '--desktop', '--profile=lxqt'], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, env=child_env(), start_new_session=True)
    return True


def _openbox_font_block(place, font, indent):
    weight = 'Bold' if font['weight'] >= 600 else 'Normal'
    slant = 'Italic' if font.get('italic') else 'Normal'
    inner = indent + '  '
    return (f'<font place="{place}">\n{inner}<name>{escape(font["family"])}</name>\n'
            f'{inner}<size>{int(round(font["size"]))}</size>\n{inner}<weight>{weight}</weight>\n'
            f'{inner}<slant>{slant}</slant>\n{indent}</font>')


def _set_openbox_title_font(font):
    changed = False
    for path in _openbox_rc_files(create=True):
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
            theme = re.search(r'<theme>(.*?)</theme>', text, re.S)
            if not theme:
                continue
            body = theme.group(1)
            new_body = body
            for place in ('ActiveWindow', 'InactiveWindow'):
                pattern = re.compile(r'([ \t]*)<font\s+place="%s"\s*>.*?</font>' % place, re.S)
                m = pattern.search(new_body)
                if m:
                    block = _openbox_font_block(place, font, m.group(1))
                    new_body = new_body[:m.start()] + m.group(1) + block + new_body[m.end():]
                else:
                    indent = '    '
                    new_body = new_body.rstrip() + '\n' + indent + _openbox_font_block(place, font, indent) + '\n  '
            if new_body != body:
                text = text[:theme.start(1)] + new_body + text[theme.end(1):]
                path.write_text(text, encoding='utf-8'); changed = True
        except Exception:
            pass
    if changed and shutil.which('openbox'):
        safe_popen(['openbox', '--reconfigure'])
    return changed


def apply_font(role, font):
    """Use one font of the five where the programs read it."""
    if role not in ROLES:
        return False
    font = make_font(font.get('family'), font.get('size'), font.get('weight'), font.get('italic'))
    saved = read_saved(); fonts = dict(saved.get('fonts') or {}); fonts[role] = font
    _save({'fonts': fonts})
    try:
        if role == 'default':
            _set_ini_if(LXQT_CONF, 'Qt', 'font', '"' + qt_string(font) + '"')
            for path in (GTK3, GTK4):
                _set_ini_if(path, 'Settings', 'gtk-font-name', pango_string(font))
            _gtk2_lines({'gtk-font-name': '"' + pango_string(font) + '"'})
            _gsettings_set('org.gnome.desktop.interface', 'font-name', pango_string(font))
        elif role == 'desktop':
            _set_desktop_font(font)
        elif role == 'document':
            _gsettings_set('org.gnome.desktop.interface', 'document-font-name', pango_string(font))
        elif role == 'monospace':
            _set_ini_if(LXQT_CONF, 'Qt', 'fixedFont', '"' + qt_string(font) + '"')
            _gsettings_set('org.gnome.desktop.interface', 'monospace-font-name', pango_string(font))
            _write_fontconfig(current_rendering(), font)
        elif role == 'title':
            _set_openbox_title_font(font)
            if shutil.which('xfconf-query') and (_xfwm4_get('/general/theme') is not None or shutil.which('xfwm4')):
                _xfwm4_set('/general/title_font', 'string', pango_string(font))
            _gsettings_set('org.gnome.desktop.wm.preferences', 'titlebar-font', pango_string(font))
    except Exception:
        return False
    return True


def apply_rendering(render):
    """Smoothing (hinting, antialiasing, subpixel order) and the text size."""
    new = dict(current_rendering())
    for key, allowed in (('hinting', HINTING), ('antialias', ANTIALIAS), ('rgba', RGBA)):
        if render.get(key) in allowed: new[key] = render[key]
    try:
        new['scale'] = round(min(SCALE_MAX, max(SCALE_MIN, float(render.get('scale', new['scale'])))), 2)
    except (TypeError, ValueError):
        pass
    _save({'render': new})
    aa = new['antialias'] != 'none'
    hint = new['hinting'] != 'none'
    rgba = new['rgba'] if new['antialias'] == 'rgba' else 'none'
    dpi = int(round(96 * new['scale']))
    try:
        for path in (GTK3, GTK4):
            _set_ini_if(path, 'Settings', 'gtk-xft-antialias', '1' if aa else '0')
            _set_ini_if(path, 'Settings', 'gtk-xft-hinting', '1' if hint else '0')
            _set_ini_if(path, 'Settings', 'gtk-xft-hintstyle', 'hint' + new['hinting'])
            _set_ini_if(path, 'Settings', 'gtk-xft-rgba', rgba)
        _set_ini_if(GTK3, 'Settings', 'gtk-xft-dpi', str(dpi * 1024))
        _gtk2_lines({'gtk-xft-antialias': '1' if aa else '0', 'gtk-xft-hinting': '1' if hint else '0',
                     'gtk-xft-hintstyle': '"hint%s"' % new['hinting'], 'gtk-xft-rgba': '"%s"' % rgba,
                     'gtk-xft-dpi': str(dpi * 1024)})
        _xresources({'Xft.antialias': '1' if aa else '0', 'Xft.hinting': '1' if hint else '0',
                     'Xft.hintstyle': 'hint' + new['hinting'], 'Xft.rgba': rgba,
                     'Xft.lcdfilter': 'lcddefault' if rgba != 'none' else 'lcdnone', 'Xft.dpi': str(dpi)})
        fonts = read_saved().get('fonts') or {}
        _write_fontconfig(new, fonts.get('monospace') or current_fonts().get('monospace'))
        _update_lxqt_fontconfig(new, dpi)
        iface = 'org.gnome.desktop.interface'
        _gsettings_set(iface, 'text-scaling-factor', '%g' % new['scale'])
        _gsettings_set(iface, 'font-antialiasing', 'none' if not aa else ('rgba' if rgba != 'none' else 'grayscale'))
        _gsettings_set(iface, 'font-hinting', new['hinting'])
        _gsettings_set(iface, 'font-rgba-order', new['rgba'])
    except Exception:
        return False
    return True


def default_fonts():
    """The fonts of a new Edukasaun account (Noto/DejaVu, which Debian installs)."""
    family = 'Noto Sans' if _font_installed('Noto Sans') else 'DejaVu Sans' if _font_installed('DejaVu Sans') else 'Sans'
    mono = 'Noto Sans Mono' if _font_installed('Noto Sans Mono') else 'DejaVu Sans Mono' if _font_installed('DejaVu Sans Mono') else 'Monospace'
    return {'default': make_font(family, 10), 'desktop': make_font(family, 10), 'document': make_font(family, 10),
            'monospace': make_font(mono, 10), 'title': make_font(family, 10, 700)}


def _font_installed(family):
    if not shutil.which('fc-list'):
        return False
    try:
        out = subprocess.run(['fc-list', family, 'family'], capture_output=True, text=True, timeout=5)
        return any(family in line.split(',') for line in out.stdout.splitlines())
    except Exception:
        return False


def reset_fonts():
    """Back to the Edukasaun defaults: the five fonts and the smoothing."""
    for role, font in default_fonts().items():
        apply_font(role, font)
    apply_rendering(DEFAULT_RENDER)
    return True


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--show':
        for role, font in current_fonts().items():
            print(f'{role}: {describe(font)}')
        print('rendering:', current_rendering())
