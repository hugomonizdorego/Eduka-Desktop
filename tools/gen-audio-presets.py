#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Make the EasyEffects presets of Eduka-Settings → Sound → Clear Sound.

Eduka's own presets are written here (EasyEffects 7 format, every key the
plugin reads, "#0" instance names). They only use effects that come with
EasyEffects itself or with lsp-plugins-lv2 (equalizer, filter, compressor,
limiter, auto gain, Speex noise suppression), so they work on Debian 12
(EasyEffects 7.0) and newer:

    Eduka Clear Voice   lessons, videos and calls: less boom and mud, clearer speech
    Eduka Music         a gentle "smile" curve with a little more bass and air
    Eduka Even Volume   loud and quiet videos play at about the same volume
    Eduka Clear Microphone (input)   less background noise, no rumble

The presets that need no impulse response files are taken from
JackHack96/EasyEffects-Presets (MIT License, Copyright (c) 2018 Matteo
Iervasi) when a checkout of that repository is given:

    python3 tools/gen-audio-presets.py [path/to/EasyEffects-Presets]

Output: usr/share/edukasaun-desktop/audio/easyeffects/{output,input}/
"""
import json, shutil, sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent/'usr'/'share'/'edukasaun-desktop'/'audio'/'easyeffects'
# Presets of JackHack96 that need no impulse response (.irs) files.
# Their names stay, with the author in front (Eduka-Settings shows a
# friendly title: Laptop speakers, Loudness, Headphones, Bass).
THIRD_PARTY = {name: 'JackHack96 ' + name for name in
               ('Advanced Auto Gain.json', 'Loudness+Autogain.json', 'Perfect EQ.json', 'Boosted.json')}


def band(freq, gain, q=1.2, kind='Bell'):
    return {'frequency': float(freq), 'gain': float(gain), 'mode': 'RLC (BT)', 'mute': False, 'q': float(q),
            'slope': 'x1', 'solo': False, 'type': kind, 'width': 4.0}


def equalizer(bands, input_gain=0.0):
    side = {f'band{i}': b for i, b in enumerate(bands)}
    return {'balance': 0.0, 'bypass': False, 'input-gain': float(input_gain), 'mode': 'IIR', 'num-bands': len(bands),
            'output-gain': 0.0, 'pitch-left': 0.0, 'pitch-right': 0.0, 'split-channels': False,
            'left': side, 'right': json.loads(json.dumps(side))}


def high_pass(freq):
    return {'balance': 0.0, 'bypass': False, 'equal-mode': 'IIR', 'frequency': float(freq), 'gain': 0.0,
            'input-gain': 0.0, 'mode': 'RLC (BT)', 'output-gain': 0.0, 'quality': 0.0, 'slope': 'x2',
            'type': 'High-pass', 'width': 4.0}


def compressor(threshold, ratio, attack, release, knee, makeup):
    return {'attack': float(attack), 'boost-amount': 6.0, 'boost-threshold': -72.0, 'bypass': False, 'dry': -100.0,
            'hpf-frequency': 10.0, 'hpf-mode': 'off', 'input-gain': 0.0, 'knee': float(knee), 'lpf-frequency': 20000.0,
            'lpf-mode': 'off', 'makeup': float(makeup), 'mode': 'Downward', 'output-gain': 0.0, 'ratio': float(ratio),
            'release': float(release), 'release-threshold': -100.0,
            'sidechain': {'lookahead': 0.0, 'mode': 'RMS', 'preamp': 0.0, 'reactivity': 10.0, 'source': 'Middle',
                          'type': 'Feed-forward'},
            'stereo-split': False, 'threshold': float(threshold), 'wet': 0.0}


def limiter(threshold):
    return {'alr': False, 'alr-attack': 5.0, 'alr-knee': 0.0, 'alr-release': 50.0, 'attack': 5.0, 'bypass': False,
            'dithering': 'None', 'external-sidechain': False, 'gain-boost': False, 'input-gain': 0.0, 'lookahead': 5.0,
            'mode': 'Herm Thin', 'output-gain': 0.0, 'oversampling': 'None', 'release': 20.0,
            'sidechain-preamp': 0.0, 'stereo-link': 100.0, 'threshold': float(threshold)}


def autogain(target):
    return {'bypass': False, 'input-gain': 0.0, 'maximum-history': 15, 'output-gain': 0.0,
            'reference': 'Geometric Mean (MSI)', 'silence-threshold': -70.0, 'target': float(target)}


def speex(suppression):
    return {'bypass': False, 'enable-agc': False, 'enable-denoise': True, 'enable-dereverb': False, 'input-gain': 0.0,
            'noise-suppression': int(suppression), 'output-gain': 0.0,
            'vad': {'enable': False, 'probability-continue': 90, 'probability-start': 95}}


def preset(section, plugins):
    body = {'blocklist': [], 'plugins_order': list(plugins)}
    body.update(plugins)
    return {section: body}


PRESETS = {
    'output/Eduka Clear Voice.json': preset('output', {
        'filter#0': high_pass(90),
        'equalizer#0': equalizer([band(180, -1.5, 1.0), band(320, -2.5), band(700, -1.0, 1.4), band(1500, 1.0, 1.4),
                                  band(2800, 3.0), band(4500, 2.0, 1.4), band(7500, 1.0, 1.4),
                                  band(11000, 1.0, 0.7, 'Hi-shelf')], input_gain=-3.0),
        'compressor#0': compressor(-22, 2.5, 15, 150, -8, 4),
        'limiter#0': limiter(-1.0)}),
    'output/Eduka Music.json': preset('output', {
        'equalizer#0': equalizer([band(32, 2.5, 1.0), band(64, 3.0, 1.0), band(125, 1.5, 1.0), band(250, 0.0),
                                  band(500, -0.5), band(1000, 0.0), band(2000, 0.5), band(4000, 1.5),
                                  band(8000, 2.5), band(16000, 2.0, 0.7, 'Hi-shelf')], input_gain=-4.0),
        'limiter#0': limiter(-1.0)}),
    'output/Eduka Even Volume.json': preset('output', {
        'autogain#0': autogain(-23),
        'compressor#0': compressor(-26, 4, 10, 200, -10, 3),
        'limiter#0': limiter(-2.0)}),
    'input/Eduka Clear Microphone.json': preset('input', {
        'filter#0': high_pass(80),
        'speex#0': speex(-35),
        'compressor#0': compressor(-20, 3, 10, 120, -6, 4),
        'limiter#0': limiter(-1.0)}),
}


def main():
    for sub in ('output', 'input'):
        (OUT/sub).mkdir(parents=True, exist_ok=True)
    for rel, data in PRESETS.items():
        (OUT/rel).write_text(json.dumps(data, indent=4, sort_keys=False) + '\n', encoding='utf-8')
        print('wrote', rel)
    if len(sys.argv) > 1:
        src = Path(sys.argv[1])
        for name, target in THIRD_PARTY.items():
            data = json.loads((src/name).read_text(encoding='utf-8'))
            if 'convolver' in json.dumps(data):
                sys.exit(f'{name} needs impulse response files')
            (OUT/'output'/target).write_text(json.dumps(data, indent=4) + '\n', encoding='utf-8')
            print('copied', name, '->', target)
        shutil.copyfile(src/'LICENSE', OUT/'LICENSE.JackHack96-EasyEffects-Presets')


if __name__ == '__main__':
    main()
