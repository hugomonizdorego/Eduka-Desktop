#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Sound of Eduka-Desktop (0.11 Pre-Stable): Eduka-Settings → Sound.

* Devices and volumes through pactl, which speaks to PipeWire
  (pipewire-pulse) and to PulseAudio alike: the output and the input, their
  volume, mute, connector (speakers or headphones) and the card profile
  (analog, HDMI for a projector, Bluetooth quality).
* A speaker test that says "front left" and "front right" (or plays a tone on
  each side when the voice files of alsa-utils are missing).
* Sound quality: small settings files of this account that fix the most
  common sound problems on Linux, read by PipeWire and WirePlumber (0.4 and
  0.5) or by PulseAudio:
      rates       music plays at its own rate (44.1 or 48 kHz), not resampled
      no_suspend  the sound card stays awake: the first second of a sound and
                  the sound of a projector are no longer cut off, no pop
      buffer      a bigger buffer: no crackling on older or busy computers
      resampler   better resampling (uses more processor time)
* Clear sound with EasyEffects (a separate program, installed on demand):
  Eduka's presets and presets of JackHack96 (MIT License), started with the
  session in the background.
* A check of the usual problems (no sound card, firmware missing, muted,
  Bluetooth in the low quality "headset" mode), each with a fix.

Nothing here needs administrator rights; installing a package opens a
terminal that asks for the password itself.
"""
import json, math, os, re, shutil, struct, subprocess, time, wave
from pathlib import Path

CONFIG_HOME = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')
CACHE_HOME = Path(os.environ.get('XDG_CACHE_HOME') or Path.home()/'.cache')
PREFS = CONFIG_HOME/'eduka-desktop'/'desktop'/'sound.json'
PRESET_SOURCE = Path('/usr/share/edukasaun-desktop/audio/easyeffects')
MARK = 'Eduka-Settings → Sound → Quality (Edukasaun Desktop)'
CONF_NAME = '60-eduka-sound'
EE_APP_ID = 'com.github.wwmm.easyeffects'
AUTOSTART = CONFIG_HOME/'autostart'/'eduka-easyeffects.desktop'

# Friendly titles of the bundled EasyEffects presets.
OUTPUT_PRESETS = (
    ('', 'Off', 'The sound as the program plays it.'),
    ('Eduka Clear Voice', 'Clear voice', 'Lessons, videos and calls: less boom, clearer speech, steady volume.'),
    ('Eduka Music', 'Music', 'A little more bass and sparkle, without distortion.'),
    ('Eduka Even Volume', 'Even volume', 'Loud and quiet videos play at about the same volume.'),
    ('JackHack96 Advanced Auto Gain', 'Laptop speakers', 'Fuller low and high tones and even volume (preset by JackHack96).'),
    ('JackHack96 Loudness+Autogain', 'Loudness', 'Loudness compensation for small speakers (preset by JackHack96).'),
    ('JackHack96 Perfect EQ', 'Headphones', 'The "Perfect EQ" curve for headphones and music (preset by JackHack96).'),
    ('JackHack96 Boosted', 'Bass', 'More bass for music (preset by JackHack96).'),
)
INPUT_PRESETS = (
    ('', 'Off', 'The microphone as it is.'),
    ('Eduka Clear Microphone', 'Clear microphone', 'Less background noise and rumble, steady level: online classes, recordings.'),
)
DEFAULT_PREFS = {'output_preset': '', 'input_preset': '', 'max_volume': 100,
                 'quality': {'rates': True, 'no_suspend': False, 'buffer': False, 'resampler': False}}


# ---------------------------------------------------------------- pactl
def _env():
    env = dict(os.environ)
    # Device names stay in the language of the user; numbers use a decimal
    # point (a decimal comma, pt_PT or id_ID, made the JSON of some pactl
    # versions invalid).
    env.pop('LC_ALL', None)
    env['LC_NUMERIC'] = 'C'
    return env


def max_volume():
    """100, or 150 when "Allow louder than 100%" is on (Sound page)."""
    try:
        return 150 if int(json.loads(PREFS.read_text(encoding='utf-8')).get('max_volume', 100)) > 100 else 100
    except (OSError, ValueError, TypeError, AttributeError):
        return 100


def pactl(*args, timeout=5):
    """Output of pactl (None when it fails or is missing)."""
    if not shutil.which('pactl'):
        return None
    try:
        r = subprocess.run(['pactl', *args], capture_output=True, text=True, timeout=timeout, env=_env())
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def pactl_json(*args, timeout=5):
    out = pactl('-f', 'json', *args, timeout=timeout)
    if out is None:
        return None
    try:
        return json.loads(out)
    except ValueError:
        try:      # "balance":0,00 of old pactl versions
            return json.loads(re.sub(r'(?<=[:\[,])(-?\d+),(\d+)', r'\1.\2', out))
        except ValueError:
            return None


def server_info():
    """{'server': 'pipewire' | 'pulseaudio' | '', 'version', 'default_sink', 'default_source'}"""
    info = pactl_json('info') or {}
    name = str(info.get('server_name') or '')
    server = 'pipewire' if 'pipewire' in name.lower() else ('pulseaudio' if name else '')
    version = ''
    m = re.search(r'PipeWire ([\d.]+)', name)
    if m:
        version = m.group(1)
    elif info.get('server_version'):
        version = str(info.get('server_version'))
    return {'server': server, 'name': name, 'version': version,
            'default_sink': info.get('default_sink_name') or '', 'default_source': info.get('default_source_name') or ''}


def _percent(volume):
    try:
        vals = [int(str(ch.get('value_percent', '0')).rstrip('%')) for ch in (volume or {}).values()]
    except (AttributeError, ValueError):
        return None
    return round(sum(vals) / len(vals)) if vals else None


def _kind(dev):
    props = dev.get('properties') or {}
    name = (dev.get('name') or '').lower(); port = (dev.get('active_port') or '').lower()
    if 'easyeffects' in name:
        return 'effects'
    if props.get('device.bus') == 'bluetooth' or name.startswith('bluez'):
        return 'bluetooth'
    if 'hdmi' in name or 'hdmi' in port or 'displayport' in port or 'iec958' in name:
        return 'hdmi'
    if 'headphone' in port or 'headset' in port:
        return 'headphones'
    if props.get('device.bus') == 'usb':
        return 'usb'
    if props.get('factory.name') in ('support.null-audio-sink',) or name.startswith('auto_null'):
        return 'virtual'
    return 'speakers'


KIND_ICONS = {'bluetooth': 'audio-headset', 'hdmi': 'video-display', 'headphones': 'audio-headphones', 'usb': 'audio-card',
              'virtual': 'audio-card', 'effects': 'audio-x-generic', 'speakers': 'audio-speakers', 'microphone': 'audio-input-microphone'}


def _device(d, default):
    ports = []
    for p in d.get('ports') or []:
        avail = str(p.get('availability') or '')
        ports.append({'name': p.get('name', ''), 'description': p.get('description') or p.get('name', ''),
                      'available': 'not available' not in avail})
    props = d.get('properties') or {}
    return {'name': d.get('name', ''), 'index': d.get('index'), 'description': d.get('description') or d.get('name', ''),
            'volume': _percent(d.get('volume')), 'mute': bool(d.get('mute')), 'default': d.get('name') == default,
            'ports': ports, 'active_port': d.get('active_port') or '', 'card': props.get('device.name') or '',
            'state': d.get('state', ''), 'kind': _kind(d)}


def sinks(info=None):
    info = info or server_info()
    out = [_device(d, info['default_sink']) for d in (pactl_json('list', 'sinks') or [])]
    return out


def sources(info=None):
    """Microphones and line inputs (the monitors of the outputs left out)."""
    info = info or server_info()
    out = []
    for d in pactl_json('list', 'sources') or []:
        if (d.get('properties') or {}).get('device.class') == 'monitor' or str(d.get('name', '')).endswith('.monitor'):
            continue
        dev = _device(d, info['default_source'])
        if dev['kind'] not in ('bluetooth', 'usb', 'effects', 'virtual'):
            dev['kind'] = 'microphone'
        out.append(dev)
    return out


def cards():
    """[{name, description, profiles: [{name, description, available}], active, bluetooth}]"""
    out = []
    for c in pactl_json('list', 'cards') or []:
        raw = c.get('profiles') or {}
        items = raw.items() if isinstance(raw, dict) else [(p.get('name', ''), p) for p in raw]
        profiles = [{'name': n, 'description': (p or {}).get('description') or n, 'available': bool((p or {}).get('available', True))}
                    for n, p in items]
        props = c.get('properties') or {}
        out.append({'name': c.get('name', ''), 'description': props.get('device.description') or c.get('name', ''),
                    'profiles': profiles, 'active': c.get('active_profile') or '',
                    'bluetooth': props.get('device.bus') == 'bluetooth' or str(c.get('name', '')).startswith('bluez')})
    return out


def snapshot():
    """Everything the Sound page shows, in one go (runs in a thread)."""
    info = server_info()
    if not info['server']:
        return {'info': info, 'sinks': [], 'sources': [], 'cards': []}
    return {'info': info, 'sinks': sinks(info), 'sources': sources(info), 'cards': cards()}


def set_default(kind, name):
    """The default output ('sink') or input ('source'); playing sounds and
    recordings move there too."""
    if kind not in ('sink', 'source') or not name:
        return False
    ok = pactl(f'set-default-{kind}', name) is not None
    streams = pactl_json('list', 'sink-inputs' if kind == 'sink' else 'source-outputs') or []
    for s in streams:
        if s.get('index') is not None:
            pactl('move-sink-input' if kind == 'sink' else 'move-source-output', str(s['index']), name, timeout=3)
    return ok


def set_volume(kind, name, percent):
    percent = max(0, min(150, int(percent)))
    return pactl(f'set-{kind}-volume', name, f'{percent}%') is not None


def set_mute(kind, name, mute):
    return pactl(f'set-{kind}-mute', name, '1' if mute else '0') is not None


def set_port(kind, name, port):
    return pactl(f'set-{kind}-port', name, port) is not None


def set_profile(card, profile):
    return pactl('set-card-profile', card, profile) is not None


# ---------------------------------------------------------------- speaker test
def _tone(path, side):
    """A soft tone on one side (left, right) or both, with fade in and out."""
    rate, secs, freq = 44100, 0.8, 523.25 if side == 'left' else (659.25 if side == 'right' else 587.33)
    n = int(rate*secs); frames = bytearray()
    for i in range(n):
        env = min(1.0, i/2000, (n-i)/4000)
        v = int(0.32*32767*env*math.sin(2*math.pi*freq*i/rate))
        lft = v if side in ('left', 'both') else 0
        rgt = v if side in ('right', 'both') else 0
        frames += struct.pack('<hh', lft, rgt)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(rate); w.writeframes(bytes(frames))
    return path


def test_sound_file(side='both'):
    voice = {'left': '/usr/share/sounds/alsa/Front_Left.wav', 'right': '/usr/share/sounds/alsa/Front_Right.wav',
             'both': '/usr/share/sounds/alsa/Front_Center.wav'}.get(side)
    if voice and os.path.exists(voice):
        return voice
    path = CACHE_HOME/'eduka-desktop'/f'sound-test-{side}.wav'
    if not path.exists():
        _tone(path, side)
    return str(path)


def play_test(sink='', side='both'):
    """Play the test on an output; returns the process (None without a player)."""
    f = test_sound_file(side)
    if shutil.which('paplay'):
        cmd = ['paplay'] + ([f'--device={sink}'] if sink else []) + [f]
    elif shutil.which('pw-play'):
        cmd = ['pw-play'] + ([f'--target={sink}'] if sink else []) + [f]
    elif shutil.which('aplay'):
        cmd = ['aplay', '-q', f]
    else:
        return None
    try:
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=_env())
    except OSError:
        return None


# ---------------------------------------------------------------- preferences
def read_prefs():
    prefs = json.loads(json.dumps(DEFAULT_PREFS))
    try:
        data = json.loads(PREFS.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return prefs
    if isinstance(data, dict):
        for k in ('output_preset', 'input_preset', 'last_output_preset'):
            if isinstance(data.get(k), str):
                prefs[k] = data[k]
        try:
            prefs['max_volume'] = 150 if int(data.get('max_volume', 100)) > 100 else 100
        except (TypeError, ValueError):
            pass
        q = data.get('quality')
        if isinstance(q, dict):
            for k in prefs['quality']:
                if k in q:
                    prefs['quality'][k] = bool(q[k])
        prefs['first_done'] = bool(data.get('first_done'))
    return prefs


def save_prefs(prefs):
    PREFS.parent.mkdir(parents=True, exist_ok=True)
    tmp = PREFS.with_name(f'.{PREFS.name}.{os.getpid()}.tmp')
    tmp.write_text(json.dumps(prefs, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, PREFS)


# ---------------------------------------------------------------- quality settings
def wireplumber_version():
    try:
        out = subprocess.run(['wireplumber', '--version'], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return ''
    m = re.search(r'libwireplumber ([\d.]+)', out) or re.search(r'(\d+\.\d+\.\d+)', out)
    return m.group(1) if m else ''


def _version_tuple(text):
    return tuple(int(x) for x in re.findall(r'\d+', text or '')[:3]) or (0,)


def quality_files(q):
    """{path: text or None (removed)} of the quality settings `q`."""
    head = f'# {MARK}.\n# Written by Eduka-Settings; remove this file to undo.\n'
    pw = CONFIG_HOME/'pipewire'
    files = {}
    ctx = []
    if q.get('rates'):
        ctx.append('    default.clock.allowed-rates = [ 44100 48000 ]')
    if q.get('buffer'):
        ctx.append('    default.clock.min-quantum = 1024')
    files[pw/'pipewire.conf.d'/f'{CONF_NAME}.conf'] = (head + 'context.properties = {\n' + '\n'.join(ctx) + '\n}\n') if ctx else None
    pulse = []
    if q.get('buffer'):
        pulse.append('pulse.properties = {\n    pulse.min.quantum = 1024/48000\n    pulse.min.req = 1024/48000\n}')
    if q.get('resampler'):
        pulse.append('stream.properties = {\n    resample.quality = 10\n}')
    files[pw/'pipewire-pulse.conf.d'/f'{CONF_NAME}.conf'] = (head + '\n'.join(pulse) + '\n') if pulse else None
    client = (head + 'stream.properties = {\n    resample.quality = 10\n}\n') if q.get('resampler') else None
    files[pw/'client.conf.d'/f'{CONF_NAME}.conf'] = client
    files[pw/'client-rt.conf.d'/f'{CONF_NAME}.conf'] = client       # PipeWire 0.3 (Debian 12)
    wp = CONFIG_HOME/'wireplumber'
    if q.get('no_suspend'):
        files[wp/'main.lua.d'/f'{CONF_NAME}.lua'] = (
            head.replace('#', '--') + 'table.insert(alsa_monitor.rules, {\n'
            '  matches = {\n    { { "node.name", "matches", "alsa_output.*" } },\n'
            '    { { "node.name", "matches", "alsa_input.*" } },\n  },\n'
            '  apply_properties = { ["session.suspend-timeout-seconds"] = 0 },\n})\n')
        files[wp/'wireplumber.conf.d'/f'{CONF_NAME}.conf'] = (
            head + 'monitor.alsa.rules = [\n  {\n    matches = [\n      { node.name = "~alsa_output.*" }\n'
            '      { node.name = "~alsa_input.*" }\n    ]\n'
            '    actions = { update-props = { session.suspend-timeout-seconds = 0 } }\n  }\n]\n')
    else:
        files[wp/'main.lua.d'/f'{CONF_NAME}.lua'] = None
        files[wp/'wireplumber.conf.d'/f'{CONF_NAME}.conf'] = None
    # PulseAudio (without PipeWire).
    pa = CONFIG_HOME/'pulse'
    daemon = []
    if q.get('rates'):
        daemon += ['avoid-resampling = yes', 'alternate-sample-rate = 44100']
    if q.get('resampler'):
        daemon.append('resample-method = speex-float-5')
    files[pa/'daemon.conf.d'/f'{CONF_NAME}.conf'] = (head + '\n'.join(daemon) + '\n') if daemon else None
    return files


def _own_file(path):
    try:
        return MARK in path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return True      # missing: ours to write


def apply_quality(q):
    """Write (or remove) this account's quality files. Returns the paths changed.
    Files without Eduka's mark (written by the user) are never touched."""
    changed = []
    for path, text in quality_files(q).items():
        if not _own_file(path):
            continue
        try:
            if text is None:
                if path.exists():
                    path.unlink(); changed.append(str(path))
            else:
                old = path.read_text(encoding='utf-8') if path.exists() else None
                if old != text:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    tmp = path.with_name(f'.{path.name}.tmp'); tmp.write_text(text, encoding='utf-8'); os.replace(tmp, path)
                    changed.append(str(path))
        except OSError:
            continue
    return changed


def first_login_defaults():
    """Once per account: music at its own rate always; on desktop computers
    (projectors, HDMI) the sound card stays awake; on small or old computers
    a bigger buffer against crackling. Returns True when it was done now."""
    prefs = read_prefs()
    if prefs.get('first_done'):
        return False
    q = prefs['quality']
    try:
        import eduka_device
        p = eduka_device.profile()
        q['no_suspend'] = p.get('kind') == 'desktop'
    except Exception:
        pass
    try:
        cores = os.cpu_count() or 2
        mem_kb = 0
        with open('/proc/meminfo', encoding='utf-8') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    mem_kb = int(line.split()[1]); break
        q['buffer'] = cores <= 2 or mem_kb < 3 * 1024 * 1024
    except (OSError, ValueError):
        pass
    prefs['first_done'] = True
    save_prefs(prefs)
    apply_quality(q)
    return True


def _systemctl_user(*args, timeout=20):
    if not shutil.which('systemctl'):
        return False
    try:
        return subprocess.run(['systemctl', '--user', *args], capture_output=True, timeout=timeout).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _unit_active(unit):
    return _systemctl_user('is-active', '--quiet', unit, timeout=5)


def restart_sound():
    """Restart the sound system of this account (PipeWire or PulseAudio).
    (ok, message)"""
    ee_was = easyeffects_running()
    if _unit_active('pipewire.service') or _unit_active('pipewire.socket'):
        units = [u for u in ('pipewire.service', 'pipewire-pulse.service', 'wireplumber.service', 'pipewire-media-session.service')
                 if _unit_active(u) or u in ('pipewire.service', 'pipewire-pulse.service')]
        ok = _systemctl_user('restart', *units, timeout=30)
    elif _unit_active('pulseaudio.service') or _unit_active('pulseaudio.socket'):
        ok = _systemctl_user('restart', 'pulseaudio.service', timeout=30)
    else:
        ok = _restart_processes()
    time.sleep(1.5)
    if ee_was:
        start_easyeffects()
    info = server_info()
    if info['server']:
        return True, 'The sound system was restarted.'
    return ok, 'The sound system was restarted, but it does not answer yet. Log out and in again if there is no sound.'


def _restart_processes():
    """Without systemd --user: stop and start the programs themselves."""
    uid = str(os.getuid())
    names = [n for n in ('pipewire-pulse', 'wireplumber', 'pipewire-media-session', 'pipewire') if _running(n)]
    if names:
        for n in names:
            subprocess.run(['pkill', '-u', uid, '-x', n], capture_output=True)
        time.sleep(0.8)
        for n in reversed(names):
            if shutil.which(n):
                subprocess.Popen([n], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                time.sleep(0.4)
        return True
    if shutil.which('pulseaudio'):
        subprocess.run(['pulseaudio', '-k'], capture_output=True)
        time.sleep(0.8)
        subprocess.run(['pulseaudio', '--start'], capture_output=True)
        return True
    return False


def _running(name):
    try:
        return subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', name], capture_output=True, timeout=3).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


# ---------------------------------------------------------------- EasyEffects
def easyeffects_command():
    if shutil.which('easyeffects'):
        return ['easyeffects']
    if shutil.which('flatpak'):
        try:
            r = subprocess.run(['flatpak', 'info', EE_APP_ID], capture_output=True, timeout=8)
            if r.returncode == 0:
                return ['flatpak', 'run', EE_APP_ID]
        except (OSError, subprocess.SubprocessError):
            pass
    return None


def easyeffects_installed():
    return easyeffects_command() is not None


def easyeffects_version():
    """The version of the package (dpkg, no window needed), else of the program."""
    cmd = easyeffects_command()
    if not cmd:
        return ''
    probes = []
    if cmd == ['easyeffects'] and shutil.which('dpkg-query'):
        probes.append(['dpkg-query', '-W', '-f=${Version}', 'easyeffects'])
    probes.append(cmd + ['--version'])
    for probe in probes:
        try:
            out = subprocess.run(probe, capture_output=True, text=True, timeout=10).stdout
        except (OSError, subprocess.SubprocessError):
            continue
        m = re.search(r'(\d+\.\d+\.\d+)', out)
        if m:
            return m.group(1)
    return ''


def easyeffects_running():
    return _running('easyeffects')


def preset_dirs():
    """Where EasyEffects looks for presets: ~/.config/easyeffects (7.x) and
    ~/.local/share/easyeffects (8.x), the Flatpak folders when it is a Flatpak."""
    cmd = easyeffects_command() or []
    if cmd[:1] == ['flatpak']:
        base = Path.home()/'.var'/'app'/EE_APP_ID
        return [base/'config'/'easyeffects', base/'data'/'easyeffects']
    data = Path(os.environ.get('XDG_DATA_HOME') or Path.home()/'.local'/'share')
    return [CONFIG_HOME/'easyeffects', data/'easyeffects']


def install_presets():
    """Copy the bundled presets for EasyEffects. Eduka's own are kept up to
    date; a preset of another author is only added when missing (it may have
    been changed). Returns the number of files written."""
    n = 0
    for sub in ('output', 'input'):
        src = PRESET_SOURCE/sub
        if not src.is_dir():
            continue
        for f in sorted(src.glob('*.json')):
            for base in preset_dirs():
                dest = base/sub/f.name
                try:
                    if dest.exists() and (not f.name.startswith('Eduka ') or dest.read_bytes() == f.read_bytes()):
                        continue
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(f, dest); n += 1
                except OSError:
                    continue
    return n


def start_easyeffects():
    """EasyEffects in the background (no window)."""
    cmd = easyeffects_command()
    if not cmd:
        return False
    if easyeffects_running():
        return True
    try:
        subprocess.Popen(cmd + ['--gapplication-service'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    except OSError:
        return False
    for _i in range(40):
        time.sleep(0.15)
        if easyeffects_running():
            time.sleep(0.6)       # let it connect to the sound server
            return True
    return False


def _ee(*args, timeout=15):
    cmd = easyeffects_command()
    if not cmd:
        return False
    try:
        return subprocess.run(cmd + list(args), capture_output=True, timeout=timeout).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def apply_presets(output_preset, input_preset):
    """Use the chosen presets ('' switches that side off). With both off
    EasyEffects stops (no processor time used) and does not start with the
    session. (ok, message)"""
    if not output_preset and not input_preset:
        if easyeffects_running():
            _ee('-q', timeout=10)
            for _i in range(30):            # it takes a few seconds to let go
                if not easyeffects_running():
                    break
                time.sleep(0.2)
            else:
                subprocess.run(['pkill', '-u', str(os.getuid()), '-x', 'easyeffects'], capture_output=True)
        set_autostart(False)
        return True, 'Clear sound is off.'
    if not easyeffects_installed():
        return False, 'EasyEffects is not installed.'
    install_presets()
    if not start_easyeffects():
        return False, 'EasyEffects did not start.'
    ok = True
    for name in (output_preset, input_preset):
        if name:
            ok = _ee('-l', name) and ok
    _ee('-b', '2')          # effects on (not bypassed)
    set_autostart(True)
    return ok, 'Clear sound is on.' if ok else 'EasyEffects did not take every preset.'


def set_autostart(on):
    cmd = easyeffects_command()
    try:
        if on and cmd:
            AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
            exe = ' '.join(cmd) + ' --gapplication-service'
            AUTOSTART.write_text('[Desktop Entry]\nType=Application\nName=Clear sound (EasyEffects)\n'
                                 'Comment=Started by Eduka-Settings → Sound → Clear Sound\n'
                                 f'Exec={exe}\nNoDisplay=true\nX-Eduka-Desktop=easyeffects\n'
                                 'X-GNOME-Autostart-Delay=3\n', encoding='utf-8')
        elif AUTOSTART.exists():
            AUTOSTART.unlink()
        return True
    except OSError:
        return False


def easyeffects_install_command():
    return ['sh', '-c', 'echo "Installing EasyEffects with its LSP and Calf effects (clear sound)..."; echo; '
                        'sudo apt-get install easyeffects lsp-plugins-lv2 calf-plugins; echo; '
                        'printf "Press Enter to close this window. "; read _answer']


# ---------------------------------------------------------------- problems and fixes
def _alsa_cards():
    try:
        text = Path('/proc/asound/cards').read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return None
    if 'no soundcards' in text:
        return []
    return re.findall(r'^\s*\d+\s+\[[^\]]*\]:\s*(.+)$', text, re.M)


def _pci_audio_devices():
    found = []
    for d in Path('/sys/bus/pci/devices').glob('*'):
        try:
            cls = (d/'class').read_text().strip()
            vendor = (d/'vendor').read_text().strip()
        except OSError:
            continue
        if cls.startswith('0x0401') or cls.startswith('0x0403'):
            found.append((cls, vendor))
    return found


def diagnose():
    """[(level, text, fix)] — level 'ok', 'warn' or 'error'; fix a key for
    fix_problem() or ''."""
    out = []
    if not shutil.which('pactl'):
        out.append(('error', 'pactl is missing (package pulseaudio-utils): Eduka-Settings cannot see the sound devices.', 'install-pactl'))
        return out
    info = server_info()
    if not info['server']:
        out.append(('error', 'No sound system answers (PipeWire or PulseAudio).', 'restart'))
        return out
    out.append(('ok', f"Sound system: {info['name']}.", ''))
    outs = sinks(info)
    real = [s for s in outs if s['kind'] not in ('virtual', 'effects')]
    alsa = _alsa_cards()
    if not real:
        if alsa == [] and _pci_audio_devices():
            vendors = {v for _c, v in _pci_audio_devices()}
            text = 'The computer has a sound chip, but no driver uses it.'
            if '0x8086' in vendors:
                text += ' Intel laptops need the sound firmware: install firmware-sof-signed and alsa-ucm-conf, then restart.'
            out.append(('error', text, 'install-firmware'))
        elif alsa:
            out.append(('error', 'The sound card is switched off or has no output. Choose a profile under Sound → Device.', 'profile'))
        else:
            out.append(('error', 'No speakers or headphones were found ("Dummy Output").', 'restart'))
    default = next((s for s in outs if s['default']), None)
    if default:
        if default['mute']:
            out.append(('warn', f"The sound is muted ({default['description']}).", 'unmute'))
        elif default['volume'] is not None and default['volume'] < 15:
            out.append(('warn', f"The volume is very low ({default['volume']}%).", 'volume'))
        if default['ports'] and default['active_port']:
            port = next((p for p in default['ports'] if p['name'] == default['active_port']), None)
            if port and not port['available']:
                out.append(('warn', f"Nothing is plugged into {port['description']}.", ''))
    for c in cards():
        if c['bluetooth'] and re.search(r'headset|handsfree|hsp|hfp', c['active'], re.I):
            a2dp = next((p for p in c['profiles'] if 'a2dp' in p['name'] and p['available']), None)
            if a2dp:
                out.append(('warn', f"{c['description']} uses the phone call mode (low quality).", f"a2dp:{c['name']}:{a2dp['name']}"))
    if not sources(info):
        out.append(('warn', 'No microphone was found.', ''))
    if info['server'] == 'pulseaudio' and shutil.which('pipewire'):
        out.append(('ok', 'PulseAudio is used; PipeWire is installed too.', ''))
    if len(out) == 1:
        out.append(('ok', 'No problem was found.', ''))
    return out


def fix_problem(key):
    """(ok, message) for a fix key of diagnose()."""
    info = server_info()
    if key == 'restart':
        return restart_sound()
    if key == 'unmute':
        return set_mute('sink', info['default_sink'] or '@DEFAULT_SINK@', False), 'The sound is on again.'
    if key == 'volume':
        return set_volume('sink', info['default_sink'] or '@DEFAULT_SINK@', 60), 'The volume is 60% now.'
    if key.startswith('a2dp:'):
        _a, card, profile = key.split(':', 2)
        return set_profile(card, profile), 'High quality sound (A2DP) is used.'
    return False, ''


def install_command(what):
    pkgs = {'install-pactl': 'pulseaudio-utils', 'install-firmware': 'firmware-sof-signed alsa-ucm-conf'}.get(what)
    if not pkgs:
        return None
    return ['sh', '-c', f'echo "Installing {pkgs} ..."; echo; sudo apt-get install {pkgs}; echo; '
                        'printf "Press Enter to close this window. "; read _answer']


if __name__ == '__main__':
    i = server_info()
    print(json.dumps(i, indent=1))
    for s in sinks(i):
        print('out', s['kind'], s['name'], s['volume'], 'muted' if s['mute'] else '', '*' if s['default'] else '')
    for s in sources(i):
        print('in ', s['kind'], s['name'], s['volume'], '*' if s['default'] else '')
    for level, text, fix in diagnose():
        print(level, text, fix)
