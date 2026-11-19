#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Drivers and firmware (0.11 Pre-Stable).

Eduka-Settings → Maintenance lists the devices of the computer that work
without a driver yet: Wi-Fi, network, sound, graphics and Bluetooth cards
on the PCI bus (/sys/bus/pci/devices) and USB Wi-Fi or Bluetooth adapters.
Most of them only need their firmware package from Debian's non-free-firmware
section; the hint names it and "Install" opens a terminal with apt-get.
Reading /sys needs no administrator password. Only the standard library is
used.
"""
import os, re
from pathlib import Path

PCI = Path('/sys/bus/pci/devices')
USB = Path('/sys/bus/usb/devices')
# PCI class (first 4 hex digits of the class code) -> kind of device.
KINDS = {'0200': 'Network', '0280': 'Wi-Fi', '0300': 'Graphics', '0302': 'Graphics', '0380': 'Graphics',
         '0401': 'Sound', '0403': 'Sound', '0d11': 'Bluetooth', '0d80': 'Wi-Fi'}
VENDORS = {'8086': 'Intel', '10ec': 'Realtek', '14e4': 'Broadcom', '168c': 'Qualcomm Atheros', '17cb': 'Qualcomm',
           '14c3': 'MediaTek', '1814': 'Ralink', '1002': 'AMD', '10de': 'NVIDIA', '1022': 'AMD', '1106': 'VIA',
           '11ab': 'Marvell', '1969': 'Qualcomm Atheros', '0bda': 'Realtek', '0cf3': 'Qualcomm Atheros',
           '0e8d': 'MediaTek', '148f': 'Ralink', '0a5c': 'Broadcom', '8087': 'Intel', '2357': 'TP-Link', '7392': 'Edimax'}
# (kind, vendor) -> Debian package with the firmware or driver.
PACKAGES = {
    ('Wi-Fi', '8086'): 'firmware-iwlwifi', ('Bluetooth', '8086'): 'firmware-iwlwifi',
    ('Wi-Fi', '10ec'): 'firmware-realtek', ('Network', '10ec'): 'firmware-realtek', ('Bluetooth', '10ec'): 'firmware-realtek',
    ('Wi-Fi', '14e4'): 'firmware-brcm80211 (or broadcom-sta-dkms for older cards)',
    ('Wi-Fi', '168c'): 'firmware-atheros', ('Wi-Fi', '17cb'): 'firmware-atheros', ('Network', '1969'): 'firmware-atheros',
    ('Wi-Fi', '14c3'): 'firmware-mediatek', ('Wi-Fi', '1814'): 'firmware-misc-nonfree',
    ('Network', '14e4'): 'firmware-bnx2', ('Network', '11ab'): 'firmware-misc-nonfree',
    ('Graphics', '1002'): 'firmware-amd-graphics', ('Graphics', '10de'): 'firmware-nvidia-graphics (or nvidia-driver)',
    ('Graphics', '8086'): 'firmware-misc-nonfree', ('Sound', '8086'): 'firmware-sof-signed alsa-ucm-conf',
    ('Sound', '1022'): 'firmware-amd-graphics alsa-ucm-conf', ('Sound', '1002'): 'firmware-amd-graphics',
    ('Wi-Fi', '0bda'): 'firmware-realtek', ('Wi-Fi', '0cf3'): 'firmware-atheros', ('Wi-Fi', '0e8d'): 'firmware-mediatek',
    ('Wi-Fi', '148f'): 'firmware-misc-nonfree', ('Bluetooth', '0a5c'): 'firmware-brcm80211',
    ('Bluetooth', '8087'): 'firmware-iwlwifi', ('Bluetooth', '0bda'): 'firmware-realtek', ('Bluetooth', '0cf3'): 'firmware-atheros',
}


def _read(path):
    try:
        return Path(path).read_text(encoding='utf-8', errors='ignore').strip()
    except OSError:
        return ''


def _driver(path):
    try:
        return os.path.basename(os.readlink(Path(path)/'driver'))
    except OSError:
        return ''


def _hex(value):
    return re.sub(r'^0x', '', value.lower())


def pci_devices():
    """[{kind, vendor_id, vendor, device_id, driver, slot}] of the PCI cards
    that matter for a desktop (network, Wi-Fi, graphics, sound, Bluetooth)."""
    out = []
    try:
        entries = sorted(PCI.iterdir())
    except OSError:
        return out
    for dev in entries:
        cls = _hex(_read(dev/'class'))[:4]
        kind = KINDS.get(cls)
        if not kind:
            continue
        vendor = _hex(_read(dev/'vendor'))
        out.append({'kind': kind, 'vendor_id': vendor, 'vendor': VENDORS.get(vendor, vendor), 'device_id': _hex(_read(dev/'device')),
                    'driver': _driver(dev), 'slot': dev.name, 'bus': 'PCI'})
    return out


def usb_devices():
    """USB Wi-Fi and Bluetooth adapters (interface class e0 = wireless
    controller, or a vendor-specific Wi-Fi stick of a known Wi-Fi maker)."""
    out = []
    try:
        entries = sorted(USB.iterdir())
    except OSError:
        return out
    for dev in entries:
        if ':' not in dev.name:
            continue                        # interfaces only (1-2:1.0)
        cls = _hex(_read(dev/'bInterfaceClass'))
        parent = Path(os.path.realpath(dev)).parent      # the USB device of this interface
        vendor = _hex(_read(parent/'idVendor'))
        if cls == 'e0':
            kind = 'Bluetooth'
        elif cls == 'ff' and vendor in ('0bda', '0cf3', '0e8d', '148f', '2357', '7392') and \
                re.search(r'(?i)wlan|wireless|802\.11|wi-?fi', _read(parent/'product') + ' ' + _read(parent/'manufacturer')):
            kind = 'Wi-Fi'
        else:
            continue
        name = _read(parent/'product')
        out.append({'kind': kind, 'vendor_id': vendor, 'vendor': VENDORS.get(vendor, vendor), 'device_id': _hex(_read(parent/'idProduct')),
                    'driver': _driver(dev), 'slot': dev.name, 'bus': 'USB', 'name': name})
    # One adapter has several interfaces: keep it once (with a driver if any interface has one).
    seen = {}
    for d in out:
        key = (d['vendor_id'], d['device_id'], d['slot'].split(':')[0])
        if key not in seen or (d['driver'] and not seen[key]['driver']):
            seen[key] = d
    return list(seen.values())


def problems():
    """[{kind, name, ids, package}] for each device without a driver."""
    out = []
    for d in pci_devices() + usb_devices():
        if d['driver']:
            continue
        if d['bus'] == 'PCI' and d['kind'] == 'Graphics' and d['vendor_id'] in ('1af4', '15ad', '80ee', '1234', '1414', '1b36'):
            continue                        # virtual graphics of a virtual machine
        pkg = PACKAGES.get((d['kind'], d['vendor_id']), '')
        out.append({'kind': d['kind'], 'name': d.get('name') or f"{d['vendor']} {d['kind']}",
                    'ids': f"{d['bus']} {d['vendor_id']}:{d['device_id']}", 'package': pkg})
    return out


def describe(problem, tr=lambda s: s):
    """One line for a problem, through the translation function tr."""
    text = tr('{kind}: {name} ({ids}) has no driver yet.').replace('{kind}', tr(problem['kind'])) \
        .replace('{name}', problem['name']).replace('{ids}', problem['ids'])
    if problem['package']:
        return text + ' ' + tr('Install {package}, then restart the computer.').replace('{package}', problem['package'])
    return text + ' ' + tr('Look for its driver or firmware package, then restart the computer.')


def summary():
    """Short text for the Maintenance page: which kinds of devices work."""
    devices = pci_devices() + usb_devices()
    working = sorted({d['kind'] for d in devices if d['driver']})
    return working


def install_command(packages):
    pkgs = ' '.join(sorted({p for pkg in packages for p in pkg.split() if re.fullmatch(r'[a-z0-9][a-z0-9.+-]+', p)}))
    if not pkgs:
        return None
    return ['sh', '-c', f'echo "Installing {pkgs} ..."; echo; sudo apt-get install {pkgs}; echo; '
                        'echo "Restart the computer to use the new driver."; printf "Press Enter to close this window. "; read _answer']


if __name__ == '__main__':
    for d in pci_devices() + usb_devices():
        print(d)
    for p in problems():
        print('!', describe(p))
    print('working:', summary())
