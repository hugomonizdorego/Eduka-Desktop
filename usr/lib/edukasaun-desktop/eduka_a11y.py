#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Accessibility of Eduka-Desktop (Eduka-Settings → Accessibility).

Vision   large text (the text scaling factor of eduka_fonts), a bigger mouse
         pointer, high contrast and less motion (Eduka's own settings), the
         magnifier and the on-screen keyboard.
Hearing  status as text on Eduka-Panel and mono sound: a PulseAudio /
         PipeWire remap sink that plays both channels in both ears, made
         again at every login by Eduka-Panel.
Speech   Orca with a voice that is easy to follow: rate, pitch, volume and
         language are written to Orca's own settings (a missing key keeps
         Orca's default), and the voice can be tried with spd-say.
"""
import json, os, re, shutil, subprocess
from pathlib import Path

from eduka_common import DESKTOP_CONFIG_DIR, write_json, safe_popen, child_env

A11Y_FILE = DESKTOP_CONFIG_DIR/'a11y.json'
ORCA_SETTINGS = Path.home()/'.local'/'share'/'orca'/'user-settings.conf'
MONO_SINK = 'eduka_mono'
POINTER_SIZES = ((24, 'Normal'), (32, 'Large'), (48, 'Larger'), (64, 'Largest'))
# Orca's voice: rate 0-99 (50 = normal), pitch 0-9 (5), volume 0-9 (9 = full).
VOICE_DEFAULT = {'rate': 45, 'pitch': 5, 'volume': 9, 'lang': ''}
VOICE_LANGUAGES = (('', 'Follow the language of the computer'), ('en', 'English'), ('id', 'Bahasa Indonesia'),
                   ('pt', 'Português'), ('pt', 'Tetun (Portuguese voice)'))
SAMPLES = {'en': 'Welcome to Edukasaun Desktop. This is how the screen reader sounds.',
           'id': 'Selamat datang di Edukasaun Desktop. Beginilah suara pembaca layar.',
           'pt': 'Bem-vindo ao Edukasaun Desktop. Assim soa o leitor de ecrã.',
           'tet': 'Bemvindu ba Edukasaun Desktop. Ida-ne\'e mak lian husi lee-na-ekran.'}


def read_a11y():
    try:
        data = json.loads(A11Y_FILE.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_a11y(update):
    data = read_a11y(); data.update(update)
    try: write_json(A11Y_FILE, data)
    except Exception: pass
    return data


# ---------------------------------------------------------------- vision
def large_text_on():
    try:
        import eduka_fonts
        return eduka_fonts.current_rendering().get('scale', 1.0) >= 1.2
    except Exception:
        return False


def set_large_text(on):
    import eduka_fonts
    return eduka_fonts.apply_rendering({'scale': 1.25 if on else 1.0})


def _cursor_theme():
    from eduka_common import current_cursor_theme
    name = (current_cursor_theme() or '').strip()
    if name and name != 'default':
        return name
    for cand in ('Adwaita', 'breeze_cursors', 'DMZ-White', 'Papirus', 'Yaru'):
        for base in ('/usr/share/icons', str(Path.home()/'.icons')):
            if os.path.isdir(os.path.join(base, cand, 'cursors')):
                return cand
    return ''


def pointer_size():
    try:
        from eduka_common import current_cursor_size
        return int(current_cursor_size())
    except Exception:
        return 24


def set_pointer_size(size):
    from eduka_common import set_cursor_theme
    name = _cursor_theme()
    if not name:
        return False
    return set_cursor_theme(name, int(size))


def first_installed(names):
    return next((n for n in names if shutil.which(n)), None)


def open_magnifier():
    cmd = first_installed(('magnus', 'kmag', 'xzoom'))
    return bool(cmd) and safe_popen([cmd])


def open_onscreen_keyboard():
    return bool(shutil.which('onboard')) and safe_popen(['onboard'])


# ---------------------------------------------------------------- hearing
def _pactl(*args, timeout=6):
    try:
        return subprocess.run(['pactl', *args], capture_output=True, text=True, timeout=timeout, env=child_env())
    except Exception:
        return None


def _mono_modules():
    out = _pactl('list', 'short', 'modules')
    if not out or out.returncode != 0:
        return []
    return [line.split('\t', 1)[0] for line in out.stdout.splitlines()
            if 'module-remap-sink' in line and f'sink_name={MONO_SINK}' in line]


def _sinks():
    out = _pactl('list', 'short', 'sinks')
    if not out or out.returncode != 0:
        return []
    return [line.split('\t')[1] for line in out.stdout.splitlines() if '\t' in line]


def mono_sound_on():
    return bool(read_a11y().get('mono_sound', False))


def apply_mono_sound(on):
    """(ok, message). On: every program plays through a mono copy of the
    speakers; off: back to the speakers chosen before."""
    if not shutil.which('pactl'):
        return False, 'Mono sound needs pactl (package pulseaudio-utils).'
    modules = _mono_modules()
    if on:
        if not modules:
            default = _pactl('get-default-sink')
            master = default.stdout.strip() if default and default.returncode == 0 else ''
            if not master or master == MONO_SINK:
                master = next((s for s in _sinks() if s != MONO_SINK), '')
            if not master:
                return False, 'No speakers or headphones were found.'
            res = _pactl('load-module', 'module-remap-sink', f'sink_name={MONO_SINK}', f'master={master}',
                         'channels=2', 'channel_map=mono,mono', 'sink_properties=device.description=Mono')
            if not res or res.returncode != 0:
                return False, 'The sound server did not accept mono sound.'
            save_a11y({'mono_master': master})
        _pactl('set-default-sink', MONO_SINK)
        inputs = _pactl('list', 'short', 'sink-inputs')
        if inputs and inputs.returncode == 0:
            for line in inputs.stdout.splitlines():
                ident = line.split('\t', 1)[0]
                if ident.isdigit():
                    _pactl('move-sink-input', ident, MONO_SINK)
        save_a11y({'mono_sound': True})
        return True, 'Mono sound is on: both ears hear everything.'
    master = read_a11y().get('mono_master', '')
    if master and master in _sinks():
        _pactl('set-default-sink', master)
    for ident in modules:
        _pactl('unload-module', ident)
    save_a11y({'mono_sound': False})
    return True, 'Mono sound is off.'


def restore_session():
    """At login (Eduka-Panel): mono sound again, when it was on."""
    if mono_sound_on() and not _mono_modules():
        return apply_mono_sound(True)
    return True, ''


def open_sound_settings():
    cmd = first_installed(('pavucontrol-qt', 'pavucontrol'))
    return bool(cmd) and safe_popen([cmd])


# ---------------------------------------------------------------- speech
def _load_orca():
    try:
        prefs = json.loads(ORCA_SETTINGS.read_text(encoding='utf-8'))
        if isinstance(prefs, dict):
            return prefs
    except Exception:
        pass
    return None


def orca_voice():
    voice = dict(VOICE_DEFAULT)
    prefs = _load_orca() or {}
    for source in ((prefs.get('general') or {}), ((prefs.get('profiles') or {}).get('default') or {})):
        default = ((source.get('voices') or {}).get('default') or {})
        if 'rate' in default: voice['rate'] = int(default['rate'])
        if 'average-pitch' in default: voice['pitch'] = int(round(float(default['average-pitch'])))
        if 'gain' in default: voice['volume'] = min(9, int(round(float(default['gain']))))
        fam = default.get('family') or {}
        if isinstance(fam, dict) and fam.get('lang') is not None: voice['lang'] = str(fam.get('lang') or '')
    if read_a11y().get('voice_tetun'):
        voice['tetun'] = True
    return voice


def set_orca_voice(rate, pitch, volume, lang='', tetun=False):
    """Write the voice into Orca's settings (keeps everything else)."""
    rate = max(0, min(99, int(rate))); pitch = max(0, min(9, int(pitch))); volume = max(0, min(9, int(volume)))
    lang = lang if re.fullmatch(r'[a-z]{2,3}(-[A-Za-z]{2})?', lang or '') else ''
    prefs = _load_orca() or {'general': {}, 'pronunciations': {}, 'keybindings': {},
                             'profiles': {'default': {'profile': ['Default', 'default']}}}
    prefs.setdefault('general', {}); prefs.setdefault('pronunciations', {}); prefs.setdefault('keybindings', {})
    profiles = prefs.setdefault('profiles', {})
    profiles.setdefault('default', {'profile': ['Default', 'default']})
    for target in (prefs['general'], profiles['default']):
        voices = target.setdefault('voices', {})
        default = voices.setdefault('default', {})
        default.update({'rate': rate, 'average-pitch': pitch, 'gain': volume, 'established': True})
        fam = dict(default.get('family') or {})
        if fam.get('lang', '') != lang:
            fam['name'] = None          # a voice of another language would win
        fam.update({'lang': lang or None, 'dialect': None})
        fam.setdefault('variant', None)
        default['family'] = fam
    try:
        ORCA_SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        tmp = ORCA_SETTINGS.with_suffix('.eduka-tmp')
        tmp.write_text(json.dumps(prefs, indent=4), encoding='utf-8'); os.replace(tmp, ORCA_SETTINGS)
    except Exception:
        return False
    save_a11y({'voice_tetun': bool(tetun)})
    return True


def restart_orca_if_running():
    try:
        running = subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'orca'], capture_output=True, timeout=3).returncode == 0
    except Exception:
        running = False
    if running:
        safe_popen(['orca', '--replace', '--enable=speech'])
    return running


def test_voice(rate, pitch, volume, lang='', tetun=False):
    """Say a sample sentence with these values (speech-dispatcher)."""
    if not shutil.which('spd-say'):
        return False
    sd_rate = int(2 * max(0, min(99, int(rate))) - 98)
    sd_pitch = int(20 * max(0, min(9, int(pitch))) - 90)
    sd_volume = int(15 * max(0, min(9, int(volume))) - 35)
    key = 'tet' if tetun else (lang or os.environ.get('LANG', 'en')[:2])
    text = SAMPLES.get(key, SAMPLES['en'])
    cmd = ['spd-say', '-C']
    safe_popen(cmd)
    cmd = ['spd-say', '-r', str(sd_rate), '-p', str(sd_pitch), '-i', str(max(-100, min(100, sd_volume)))]
    if lang: cmd += ['-l', lang]
    return safe_popen(cmd + ['--', text])
