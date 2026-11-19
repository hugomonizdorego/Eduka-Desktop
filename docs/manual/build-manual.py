#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Build the user guide of Edukasaun Desktop Suite as PDF files.

    python3 docs/manual/build-manual.py [en tet pt]

The texts are in content_en.py, content_tet.py and content_pt.py (one
structure, three languages); the pictures in images/ are screenshots of a
real Eduka-Desktop session in English. Each language becomes an HTML page,
which Chromium (Playwright, print-pdf.js) prints to
Edukasaun-Desktop-Guide-<lang>.pdf in this folder.
"""
import html, importlib, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT/'usr'/'lib'/'edukasaun-desktop'))

ACCENT = '#3b87d4'
CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Inter', 'DejaVu Sans', sans-serif; font-size: 10.2pt; line-height: 1.5; color: #1d2b3a; margin: 0; }
h1, h2, h3 { color: #16324f; line-height: 1.25; }
h2 { font-size: 17pt; margin: 0 0 8pt 0; padding: 6pt 0 6pt 0; border-bottom: 2.5pt solid ACCENT; break-after: avoid; }
h2 .num { color: ACCENT; margin-right: 6pt; }
h3 { font-size: 12.2pt; margin: 14pt 0 4pt 0; break-after: avoid; }
p { margin: 0 0 7pt 0; }
ul, ol { margin: 0 0 8pt 0; padding-left: 16pt; }
li { margin: 0 0 3pt 0; }
section.chapter { break-before: page; }
section.chapter.first { break-before: auto; }
figure { margin: 8pt 0 12pt 0; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; border: 1pt solid #c9d6e6; border-radius: 6pt; box-shadow: 0 2pt 6pt rgba(30,60,100,0.12); }
figure.half img { max-width: 62%; }
figure.third img { max-width: 46%; }
figcaption { font-size: 8.6pt; color: #50647a; margin-top: 4pt; }
.tip, .note, .warn { border-radius: 6pt; padding: 7pt 10pt; margin: 8pt 0 10pt 0; break-inside: avoid; }
.tip { background: #eaf3fc; border-left: 4pt solid ACCENT; }
.note { background: #f1f4f8; border-left: 4pt solid #8a9bb0; }
.warn { background: #fff4e5; border-left: 4pt solid #e8a33d; }
.tip b.label, .note b.label, .warn b.label { display: block; font-size: 8.8pt; letter-spacing: 0.4pt; text-transform: uppercase; color: #2f5f93; margin-bottom: 2pt; }
.warn b.label { color: #9a5b00; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 12pt 0; font-size: 9.2pt; break-inside: auto; }
th { background: #e4eef9; color: #16324f; text-align: left; padding: 4pt 6pt; border-bottom: 1.2pt solid #b9cde4; }
td { padding: 3.5pt 6pt; border-bottom: 0.6pt solid #dbe4ee; vertical-align: top; }
tr { break-inside: avoid; }
kbd { font-family: 'Inter', sans-serif; font-size: 8.6pt; background: #f4f7fb; border: 0.8pt solid #b8c6d8; border-bottom-width: 1.6pt; border-radius: 3pt; padding: 0 3pt; white-space: nowrap; }
.cover { height: 257mm; display: flex; flex-direction: column; justify-content: space-between; break-after: page;
         background: linear-gradient(160deg, #eaf3fc 0%, #ffffff 55%, #eef2fb 100%); border-radius: 10pt; padding: 26mm 18mm 16mm 18mm; }
.cover .logo img { height: 22mm; }
.cover h1 { font-size: 30pt; margin: 18mm 0 4mm 0; color: #16324f; }
.cover .sub { font-size: 14pt; color: #2f5f93; margin-bottom: 10mm; }
.cover .shot img { width: 100%; border-radius: 8pt; border: 1pt solid #c9d6e6; box-shadow: 0 4pt 14pt rgba(30,60,100,0.18); }
.cover .meta { font-size: 9.5pt; color: #50647a; }
.toc { break-after: page; }
.toc h2 { border-bottom: 2.5pt solid ACCENT; }
.toc ol { list-style: none; padding-left: 0; columns: 2; column-gap: 12mm; }
.toc li { margin: 0 0 5pt 0; font-size: 10.5pt; break-inside: avoid; }
.toc li .n { display: inline-block; width: 18pt; color: ACCENT; font-weight: 700; }
.toc .intro { color: #50647a; margin-bottom: 10pt; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; align-items: start; }
.grid2 figure { margin: 4pt 0 8pt 0; }
""".replace('ACCENT', ACCENT)


def inline(text):
    """Escape, then turn [[Key]] into <kbd> and **bold** into <b>."""
    t = html.escape(text, quote=False)
    t = re.sub(r'\[\[(.+?)\]\]', lambda m: ''.join(f'<kbd>{k}</kbd>' if i % 2 == 0 else '+'
                                                  for i, k in enumerate(re.split(r'(\+)', m.group(1))) if k != '+')
               .replace('</kbd><kbd>', '</kbd>+<kbd>'), t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return t


def block(b, c):
    kind = b[0]
    if kind == 'p':
        return f'<p>{inline(b[1])}</p>'
    if kind == 'h3':
        return f'<h3>{inline(b[1])}</h3>'
    if kind in ('ul', 'ol'):
        return f'<{kind}>' + ''.join(f'<li>{inline(x)}</li>' for x in b[1]) + f'</{kind}>'
    if kind in ('tip', 'note', 'warn'):
        label = c.LABELS[kind]
        return f'<div class="{kind}"><b class="label">{html.escape(label)}</b>{inline(b[1])}</div>'
    if kind == 'img':
        name, caption = b[1], b[2]
        size = b[3] if len(b) > 3 else ''
        return (f'<figure class="{size}"><img src="images/{name}.jpg" alt="">'
                f'<figcaption>{inline(caption)}</figcaption></figure>')
    if kind == 'img2':
        return '<div class="grid2">' + ''.join(block(('img',) + tuple(x), c) for x in b[1]) + '</div>'
    if kind == 'table':
        head, rows = b[1], b[2]
        return ('<table><thead><tr>' + ''.join(f'<th>{inline(h)}</th>' for h in head) + '</tr></thead><tbody>'
                + ''.join('<tr>' + ''.join(f'<td>{inline(x)}</td>' for x in r) + '</tr>' for r in rows) + '</tbody></table>')
    raise ValueError(kind)


def build_html(lang):
    c = importlib.import_module(f'content_{lang}')
    import eduka_common
    version = eduka_common.VERSION
    out = [f'<!doctype html><html lang="{c.HTML_LANG}"><head><meta charset="utf-8"><title>{html.escape(c.TITLE)}</title>'
           f'<style>{CSS}</style></head><body>']
    out.append('<div class="cover"><div><div class="logo"><img src="../../usr/share/edukasaun-desktop/assets/edukasaun-os-wordmark.svg" alt=""></div>'
               f'<h1>{html.escape(c.TITLE)}</h1><div class="sub">{html.escape(c.SUBTITLE.replace("{version}", version))}</div></div>'
               '<div class="shot"><img src="images/desktop.jpg" alt=""></div>'
               f'<div class="meta">{inline(c.COVER_META.replace("{version}", version))}</div></div>')
    out.append(f'<div class="toc"><h2>{html.escape(c.LABELS["contents"])}</h2><p class="intro">{inline(c.TOC_INTRO)}</p><ol>')
    for i, (sid, title, _blocks) in enumerate(c.SECTIONS, 1):
        out.append(f'<li><span class="n">{i}</span>{html.escape(title)}</li>')
    out.append('</ol></div>')
    for i, (sid, title, blocks) in enumerate(c.SECTIONS, 1):
        cls = 'chapter first' if i == 1 else 'chapter'
        out.append(f'<section class="{cls}" id="{sid}"><h2><span class="num">{i}</span>{html.escape(title)}</h2>')
        out.extend(block(b, c) for b in blocks)
        out.append('</section>')
    out.append('</body></html>')
    path = HERE/f'guide-{lang}.html'
    path.write_text('\n'.join(out), encoding='utf-8')
    return path, c


def main():
    langs = sys.argv[1:] or ['en', 'tet', 'pt']
    for lang in langs:
        page, c = build_html(lang)
        pdf = HERE/f'Edukasaun-Desktop-Guide-{c.FILE_SUFFIX}.pdf'
        subprocess.run(['node', str(HERE/'print-pdf.js'), str(page), str(pdf), c.FOOTER], check=True)
        page.unlink()
        print(pdf.relative_to(ROOT))


if __name__ == '__main__':
    main()
