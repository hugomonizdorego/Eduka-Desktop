#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
"""Screen recording (0.11 Pre-Stable).

Super+Alt+R (as on Windows) starts and stops a recording of the whole
screen with the sound of the computer, and the microphone when it is chosen
in Eduka-Settings → Windows → Screenshots & Recording. The video (MP4: H.264
and AAC, it plays everywhere) is saved in Videos/Screen recordings.
While it records Eduka-Panel shows a red REC button that stops it.

ffmpeg does the work: x11grab for the picture, PulseAudio or PipeWire for
the sound (the "monitor" of the speakers). On Wayland wf-recorder is used
when it is installed. Only the standard library is needed here.
"""
import json, os, re, shutil, signal, subprocess, time
from pathlib import Path

import eduka_ipc

CONFIG_HOME = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')
PREFS = CONFIG_HOME/'eduka-desktop'/'desktop'/'capture.json'
STATE = eduka_ipc.RUNTIME_DIR/'recording.json'
DEFAULTS = {'sound': True, 'mic': False, 'fps': 25, 'pointer': True, 'quality': 'normal'}
QUALITY = {'small': ('ultrafast', 30), 'normal': ('ultrafast', 25), 'best': ('veryfast', 21)}


def read_prefs():
    prefs = dict(DEFAULTS)
    try:
        data = json.loads(PREFS.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return prefs
    if isinstance(data, dict):
        for k in ('sound', 'mic', 'pointer'):
            if k in data:
                prefs[k] = bool(data[k])
        try:
            prefs['fps'] = max(10, min(60, int(data.get('fps', 25))))
        except (TypeError, ValueError):
            pass
        if data.get('quality') in QUALITY:
            prefs['quality'] = data['quality']
    return prefs


def save_prefs(prefs):
    PREFS.parent.mkdir(parents=True, exist_ok=True)
    eduka_ipc.write_json_atomic(PREFS, {k: prefs.get(k, v) for k, v in DEFAULTS.items()}, indent=2)


def videos_dir():
    base = ''
    if shutil.which('xdg-user-dir'):
        try:
            base = subprocess.run(['xdg-user-dir', 'VIDEOS'], capture_output=True, text=True, timeout=3).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            base = ''
    if not base or base == str(Path.home()):
        base = str(Path.home()/'Videos')
    return Path(base)/'Screen recordings'


def wayland():
    return (os.environ.get('XDG_SESSION_TYPE') == 'wayland' or bool(os.environ.get('WAYLAND_DISPLAY'))) and \
        not os.environ.get('EDUKA_FORCE_X11_CAPTURE')


def tool():
    """'ffmpeg', 'wf-recorder' or '' (nothing can record)."""
    if wayland():
        return 'wf-recorder' if shutil.which('wf-recorder') else ''
    return 'ffmpeg' if shutil.which('ffmpeg') and os.environ.get('DISPLAY') else ''


def _pactl(*args):
    if not shutil.which('pactl'):
        return ''
    env = dict(os.environ); env.pop('LC_ALL', None)
    try:
        r = subprocess.run(['pactl', *args], capture_output=True, text=True, timeout=4, env=env)
        return r.stdout.strip() if r.returncode == 0 else ''
    except (OSError, subprocess.SubprocessError):
        return ''


def sound_sources(prefs):
    """The PulseAudio source names to record: the monitor of the default
    output (the sound of the computer) and the default microphone."""
    out = []
    if prefs.get('sound'):
        sink = _pactl('get-default-sink')
        if sink:
            out.append(sink + '.monitor')
    if prefs.get('mic'):
        src = _pactl('get-default-source')
        if src and not src.endswith('.monitor'):
            out.append(src)
    return out


def screen_size():
    for cmd in (['xdotool', 'getdisplaygeometry'], ['xdpyinfo']):
        if not shutil.which(cmd[0]):
            continue
        try:
            text = subprocess.run(cmd, capture_output=True, text=True, timeout=4).stdout
        except (OSError, subprocess.SubprocessError):
            continue
        m = re.search(r'(\d+)\s+(\d+)\s*$', text.strip()) if cmd[0] == 'xdotool' else re.search(r'dimensions:\s+(\d+)x(\d+)', text)
        if m:
            w, h = int(m.group(1)), int(m.group(2))
            return w - w % 2, h - h % 2          # H.264 needs even sizes
    return 0, 0


def command(prefs, target):
    """The recording command (a list) for `target` (a .mp4 path)."""
    fps = str(prefs.get('fps', 25))
    preset, crf = QUALITY.get(prefs.get('quality'), QUALITY['normal'])
    sources = sound_sources(prefs)
    if tool() == 'wf-recorder':
        cmd = ['wf-recorder', '-f', str(target), '-c', 'libx264', '-p', f'preset={preset}', '-p', f'crf={crf}', '-r', fps]
        if sources:
            cmd.append(f'--audio={sources[0]}')
        return cmd
    w, h = screen_size()
    display = os.environ.get('DISPLAY', ':0')
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-thread_queue_size', '512', '-f', 'x11grab',
           '-draw_mouse', '1' if prefs.get('pointer', True) else '0', '-framerate', fps]
    if w and h:
        cmd += ['-video_size', f'{w}x{h}']
    cmd += ['-i', f'{display}+0,0' if w else display]
    for src in sources:
        cmd += ['-thread_queue_size', '1024', '-f', 'pulse', '-i', src]
    if len(sources) == 2:
        cmd += ['-filter_complex', '[1:a][2:a]amix=inputs=2:duration=longest:dropout_transition=0[a]', '-map', '0:v', '-map', '[a]']
    cmd += ['-c:v', 'libx264', '-preset', preset, '-crf', str(crf), '-pix_fmt', 'yuv420p', '-g', str(int(fps) * 2)]
    if sources:
        cmd += ['-c:a', 'aac', '-b:a', '128k']
    cmd.append(str(target))
    return cmd


# ---------------------------------------------------------------- state
def _cmdline(pid):
    try:
        return Path(f'/proc/{int(pid)}/cmdline').read_bytes().replace(b'\0', b' ').decode('utf-8', 'ignore')
    except (OSError, ValueError):
        return ''


def recording():
    """The running recording {pid, file, started} or None."""
    try:
        state = json.loads(STATE.read_text(encoding='utf-8'))
        pid = int(state.get('pid'))
    except (OSError, ValueError, TypeError):
        return None
    line = _cmdline(pid)
    if not line or str(state.get('file', '\0')) not in line:
        try:
            STATE.unlink()
        except OSError:
            pass
        return None
    return state


def notify(summary, body='', icon='media-record'):
    if shutil.which('notify-send'):
        try:
            subprocess.Popen(['notify-send', '-a', 'Eduka-Desktop', '-i', icon, summary, body],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        except OSError:
            pass


def start(prefs=None):
    """Start recording. (ok, message)"""
    if recording():
        return False, 'A recording is running already.'
    t = tool()
    if not t:
        if wayland():
            return False, 'Recording on Wayland needs wf-recorder (sudo apt-get install wf-recorder).'
        return False, 'Recording needs ffmpeg (sudo apt-get install ffmpeg).'
    prefs = prefs or read_prefs()
    folder = videos_dir()
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return False, str(e)
    target = folder/time.strftime('Screen recording %Y-%m-%d %H-%M-%S.mp4')
    try:
        proc = subprocess.Popen(command(prefs, target), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True)
    except OSError as e:
        return False, str(e)
    time.sleep(0.6)
    if proc.poll() is not None:
        return False, 'The recording did not start (ffmpeg stopped at once).'
    eduka_ipc.runtime_dir()
    eduka_ipc.write_json_atomic(STATE, {'pid': proc.pid, 'file': str(target), 'started': time.time()}, indent=None)
    eduka_ipc.panel_command('recording on')
    notify('Recording the screen', 'Press Super+Alt+R or the red REC button on the panel to stop.')
    return True, str(target)


def stop():
    """Stop the recording and keep the video. (ok, message)"""
    state = recording()
    if not state:
        eduka_ipc.panel_command('recording off')
        return False, 'Nothing is being recorded.'
    pid = int(state['pid'])
    try:
        os.kill(pid, signal.SIGINT)          # ffmpeg finishes the file properly
    except OSError:
        pass
    for _i in range(100):
        if not _cmdline(pid):
            break
        time.sleep(0.1)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    try:
        STATE.unlink()
    except OSError:
        pass
    eduka_ipc.panel_command('recording off')
    target = Path(state['file'])
    if target.exists() and target.stat().st_size > 0:
        notify('Screen recording saved', str(target), 'video-x-generic')
        return True, str(target)
    notify('The screen recording failed', 'Nothing was saved.', 'dialog-error')
    return False, 'Nothing was saved.'


def toggle():
    return stop() if recording() else start()


if __name__ == '__main__':
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else 'toggle'
    ok, msg = {'start': start, 'stop': stop}.get(action, toggle)()
    print(msg)
    sys.exit(0 if ok else 1)
