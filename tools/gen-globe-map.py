#!/usr/bin/env python3
"""Draw the world map used by the Action Center globe.

Input: Natural Earth 1:110m land polygons (public domain,
https://www.naturalearthdata.com), tools/data/ne_110m_land.geojson.
Output: usr/share/edukasaun-desktop/assets/world-map.png, an
equirectangular 1024x512 picture (longitude -180..180, latitude 90..-90).
"""
import json, sys
from pathlib import Path
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QImage, QPainter, QColor, QPolygonF, QLinearGradient, QPen, QBrush
from PyQt5.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent
W, H = 1024, 512
app = QApplication(['gen', '-platform', 'offscreen'])
data = json.loads((ROOT/'tools/data/ne_110m_land.geojson').read_text(encoding='utf-8'))
img = QImage(W, H, QImage.Format_RGB32)
p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
sea = QLinearGradient(0, 0, 0, H)
for pos, col in ((0.0, '#1b4f7a'), (0.5, '#1f6fa8'), (1.0, '#1b4f7a')):
    sea.setColorAt(pos, QColor(col))
p.fillRect(img.rect(), sea)
xy = lambda lon, lat: QPointF((lon+180)/360*W, (90-lat)/180*H)
land = QLinearGradient(0, 0, 0, H)
for pos, col in ((0.0, '#e8eef2'), (0.12, '#8fae7a'), (0.35, '#5f9a52'), (0.5, '#4f8f45'), (0.62, '#a4945f'), (0.82, '#7fa064'), (0.95, '#e8eef2')):
    land.setColorAt(pos, QColor(col))
p.setBrush(QBrush(land)); p.setPen(QPen(QColor('#3d6b3a'), 0.8))
for feature in data['features']:
    geom = feature['geometry']
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    for poly in polys:
        for ring in poly[:1]:
            p.drawPolygon(QPolygonF([xy(lon, lat) for lon, lat in ring]))
# Graticule every 30 degrees, very light.
p.setPen(QPen(QColor(255, 255, 255, 28), 1))
for lon in range(-180, 181, 30):
    p.drawLine(xy(lon, 90), xy(lon, -90))
for lat in range(-60, 61, 30):
    p.drawLine(xy(-180, lat), xy(180, lat))
p.end()
out = ROOT/'usr/share/edukasaun-desktop/assets/world-map.png'
out.parent.mkdir(parents=True, exist_ok=True)
img.save(str(out), 'PNG')
print('wrote', out, out.stat().st_size, 'bytes')
