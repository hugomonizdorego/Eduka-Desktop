#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Graphics cards (0.11 Pre-Stable).

* Which graphics cards the computer has and which driver each one uses
  (/sys/class/drm), with a hint when a card has no driver or firmware.
* Hybrid graphics (a laptop with a built-in Intel or AMD chip and a
  dedicated NVIDIA or AMD card): games and programs that ask for it
  (PrefersNonDefaultGPU=true in their .desktop file) start on the dedicated
  card, and "Run with the dedicated graphics card" is in the right-click
  menu of Eduka-Desktop. Mesa drivers use DRI_PRIME=1, the NVIDIA driver its
  PRIME render offload.
"""
import json, os, re
from pathlib import Path

DRM = Path('/sys/class/drm')
PREFS = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')/'eduka-desktop'/'desktop'/'graphics.json'
VENDORS = {'0x8086': 'Intel', '0x1002': 'AMD', '0x10de': 'NVIDIA', '0x1af4': 'Virtio (virtual)', '0x15ad': 'VMware (virtual)',
           '0x80ee': 'VirtualBox (virtual)', '0x1234': 'QEMU (virtual)', '0x1414': 'Hyper-V (virtual)', '0x1b36': 'QXL (virtual)',
           '0x102b': 'Matrox', '0x1a03': 'ASPEED'}
VIRTUAL = {'0x1af4', '0x15ad', '0x80ee', '0x1234', '0x1414', '0x1b36'}


def _read(path):
    try:
        return Path(path).read_text(encoding='utf-8', errors='ignore').strip()
    except OSError:
        return ''


def gpus():
    """[{card, vendor, vendor_id, device_id, driver, boot, pci}] for each card."""
    out = []
    for card in sorted(DRM.glob('card[0-9]*')):
        if '-' in card.name:
            continue                    # card0-HDMI-A-1: a connector
        dev = card/'device'
        vendor_id = _read(dev/'vendor').lower()
        if not vendor_id:
            continue
        try:
            driver = os.path.basename(os.readlink(dev/'driver'))
        except OSError:
            driver = ''
        try:
            pci = os.path.basename(os.path.realpath(dev))
        except OSError:
            pci = ''
        out.append({'card': card.name, 'vendor_id': vendor_id, 'vendor': VENDORS.get(vendor_id, vendor_id),
                    'device_id': _read(dev/'device').lower(), 'driver': driver, 'boot': _read(dev/'boot_vga') == '1',
                    'pci': pci, 'virtual': vendor_id in VIRTUAL})
    return out


def dedicated(cards=None):
    """The dedicated card of a computer with hybrid graphics, or None."""
    cards = [c for c in (cards if cards is not None else gpus()) if not c['virtual'] and c['driver']]
    if len(cards) < 2:
        return None
    others = [c for c in cards if not c['boot']]
    for c in others:
        if c['vendor_id'] in ('0x10de', '0x1002'):
            return c
    return others[0] if others else None


def offload_env(card=None):
    """Environment that runs a program on the dedicated card ({} without one)."""
    card = card or dedicated()
    if not card:
        return {}
    if card['driver'] == 'nvidia':
        return {'__NV_PRIME_RENDER_OFFLOAD': '1', '__GLX_VENDOR_LIBRARY_NAME': 'nvidia', '__VK_LAYER_NV_optimus': 'NVIDIA_only'}
    env = {'DRI_PRIME': '1'}
    if card.get('pci'):
        # pci-0000_01_00_0: exactly this card (Mesa), also with three cards.
        env['DRI_PRIME'] = 'pci-' + re.sub(r'[:.]', '_', card['pci'])
    return env


def read_prefs():
    try:
        data = json.loads(PREFS.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            return {'auto': bool(data.get('auto', True))}
    except (OSError, ValueError):
        pass
    return {'auto': True}


def save_prefs(prefs):
    import eduka_ipc
    eduka_ipc.write_json_atomic(PREFS, {'auto': bool(prefs.get('auto', True))}, indent=2)


def wants_dedicated(app):
    """True when a program asks for the dedicated card and it is allowed."""
    return bool((app or {}).get('gpu')) and read_prefs()['auto'] and dedicated() is not None


def hints(cards=None, tr=lambda s: s):
    """Advice about drivers: [(level, text)], translated by tr."""
    cards = cards if cards is not None else gpus()
    out = []
    for c in cards:
        if c['virtual']:
            continue
        if not c['driver']:
            pkg = {'0x1002': 'firmware-amd-graphics', '0x10de': 'nvidia-driver (or the free driver nouveau)',
                   '0x8086': 'firmware-misc-nonfree'}.get(c['vendor_id'], 'the firmware of this card')
            out.append(('warn', tr('The {vendor} card has no driver yet: install {package}, then restart.')
                        .replace('{vendor}', c['vendor']).replace('{package}', pkg)))
        elif c['vendor_id'] == '0x10de' and c['driver'] == 'nouveau':
            out.append(('info', tr('The NVIDIA card uses the free driver nouveau. For games the NVIDIA driver (nvidia-driver) is faster.')))
        elif c['vendor_id'] == '0x1002' and c['driver'] == 'radeon':
            out.append(('info', tr('This older AMD card uses the radeon driver; that is right for it.')))
    return out


if __name__ == '__main__':
    for c in gpus():
        print(c)
    print('dedicated:', dedicated(), offload_env())
    for h in hints():
        print(*h)
