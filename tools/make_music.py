"""Calm procedural music loop + forest ambience for Timber Valley."""
import numpy as np, soundfile as sf
def write_ogg(path, data, sr):
    with sf.SoundFile(path, 'w', sr, data.shape[1], format='OGG', subtype='VORBIS') as f:
        for i in range(0, len(data), 4096):
            f.write(np.ascontiguousarray(data[i:i+4096]))
from scipy.signal import fftconvolve, butter, sosfilt
SR = 44100
rng = np.random.default_rng(7)
import argparse
ap = argparse.ArgumentParser(description="Writes music.ogg and/or ambience.ogg into the current folder.")
ap.add_argument("--only", choices=["music", "ambience", "all"], default="music")
ARGS = ap.parse_args()

def note_hz(m): return 440 * 2 ** ((m - 69) / 12)

# ---- Music (2026-10-05): 150 s calm loop, pads + soft bass + slow e-piano + sparse bells,
# no percussion. The old 50 s loop sat about 6 dB under the game's effects and had 88% of its
# energy below 300 Hz, which a phone speaker barely plays (Mats could not hear it). Voiced for
# phone speakers: chords from about 150 Hz up, no sub-bass, 180 Hz high-pass.
BPM = 64
beat = 60 / BPM
BARS = 40
dur = BARS * 4 * beat
N = int(dur * SR)
TAIL = int(8 * SR)
L = np.zeros(N + TAIL); R = np.zeros(N + TAIL)

def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    n = min(len(sig), len(buf) - i)
    if n > 0:
        buf[i:i + n] += sig[:n] * gain

def env_adsr(n, a, r):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-3))
    rel = np.clip((n / SR - t) / max(r, 1e-3), 0, 1)
    return e * rel

def pad(ms, length, vel):
    n = int((length + 2.0) * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for m in ms:
        for det in (-0.07, 0.0, 0.07):
            f = note_hz(m + det)
            ph = rng.uniform(0, 2 * np.pi)
            sig += np.sin(2 * np.pi * f * t + ph) + 0.22 * np.sin(4 * np.pi * f * t + ph)
    slow = 0.85 + 0.15 * np.sin(2 * np.pi * t / 6.0)
    return sig * env_adsr(n, 1.6, 2.0) * slow * vel / (3 * len(ms))

def bass(m, length, vel):
    n = int((length + 1.0) * SR)
    t = np.arange(n) / SR
    f = note_hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.15 * np.sin(4 * np.pi * f * t)) * env_adsr(n, 0.25, 1.2) * vel

def epiano(m, vel, length=3.2):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = note_hz(m)
    tone = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3)
    return tone * np.exp(-t * 1.6) * np.minimum(1, t / 0.006) * vel

def bell(m, vel, length=4.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = note_hz(m)
    tone = np.sin(2 * np.pi * f * t) + 0.12 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 4)
    return tone * np.exp(-t * 1.2) * np.minimum(1, t / 0.004) * vel

A = [[48, 55, 59, 64], [45, 52, 55, 60], [41, 48, 52, 57], [43, 50, 55, 60]]
B = [[40, 47, 50, 55], [45, 52, 55, 60], [38, 45, 48, 53], [43, 50, 53, 55]]
C = [[41, 48, 52, 57], [40, 47, 50, 55], [38, 45, 48, 53], [43, 50, 55, 59]]
chords = A + A + B + A + C
penta = [76, 79, 81, 84, 86, 88, 91]
for ci, ch in enumerate(chords):
    start = ci * 8 * beat
    # Upper chord tones only (the root is the bass), plus a soft octave-up layer.
    p = pad([m + 12 for m in ch[1:]], 8 * beat, 0.50) + np.pad(pad([m + 24 for m in ch[1:]], 8 * beat, 0.22), (0, 0))
    add(L, start, p, 0.95); add(R, start, p, 1.0)
    b = bass(ch[0] + 12, 8 * beat, 0.10)
    add(L, start, b); add(R, start, b)
    for k, bt in enumerate([0, 1.5, 3, 4.5, 6]):
        m = ch[1 + (k % 3)] + 24
        s = epiano(m, rng.uniform(0.10, 0.14))
        pan = 0.38 + 0.24 * (k % 2)
        add(L, start + bt * beat, s, 1 - pan); add(R, start + bt * beat, s, pan)
    if ci in range(4, 8) or ci in range(12, 16):
        for bt in range(0, 8, 2):
            if rng.random() < 0.4:
                s = bell(int(rng.choice(penta)), 0.10)
                pan = rng.uniform(0.3, 0.7)
                add(L, start + bt * beat, s, 1 - pan); add(R, start + bt * beat, s, pan)

def reverb(x):
    t = np.arange(int(2.6 * SR)) / SR
    ir = rng.normal(0, 1, len(t)) * np.exp(-t * 2.4)
    ir[0] = 0
    return fftconvolve(x, ir)[: len(x)] / np.sqrt(len(t))

L = L + 0.9 * reverb(L) * 0.12; R = R + 0.9 * reverb(R) * 0.12
# Seamless loop: what rings past the end is folded back into the start.
L[:TAIL] += L[N:]; R[:TAIL] += R[N:]
L = L[:N]; R = R[:N]
sos = butter(2, [180, 6000], 'band', fs=SR, output='sos')
L = sosfilt(sos, np.concatenate([L, L]))[N:]; R = sosfilt(sos, np.concatenate([R, R]))[N:]
st = np.stack([L, R], 1)
st *= 10 ** (-12 / 20) / np.sqrt(np.mean(st ** 2))   # RMS -12 dBFS
st = np.tanh(st * 1.15) / 1.15                      # soft limit, peaks stay under 0 dBFS
st *= min(1.0, 10 ** (-1 / 20) / np.abs(st).max())  # peak <= -1 dBFS
if ARGS.only in ("music", "all"):
    write_ogg('music.ogg', st, SR)
    print('music', round(dur, 1), 's', 'rms_db', round(20 * np.log10(np.sqrt(np.mean(st ** 2))), 1), 'peak_db', round(20 * np.log10(np.abs(st).max()), 1))

if ARGS.only == "music":
    raise SystemExit(0)
# Ambience: soft wind bed + occasional bird chirps, 40 s loop.
D = 40; N2 = D * SR
noise = rng.normal(0, 1, N2)
sos2 = butter(2, [150, 900], 'band', fs=SR, output='sos')
wind = sosfilt(sos2, noise)
t = np.arange(N2) / SR
wind *= 0.5 + 0.5 * np.sin(2 * np.pi * t / D) ** 2
amb = wind / np.abs(wind).max() * 0.18
for k in range(26):
    st_ = rng.uniform(0, D - 1)
    f0 = rng.uniform(2600, 4200)
    n_ch = rng.integers(2, 5)
    for c in range(n_ch):
        cl = rng.uniform(0.06, 0.12)
        tt = np.arange(int(cl * SR)) / SR
        sweep = f0 * (1 + 0.35 * np.sin(np.pi * tt / cl)) * rng.uniform(0.9, 1.1)
        ph = 2 * np.pi * np.cumsum(sweep) / SR
        ch = np.sin(ph) * np.sin(np.pi * tt / cl) ** 2 * rng.uniform(0.05, 0.12)
        i = int((st_ + c * cl * 1.4) * SR)
        amb[i:i + len(ch)] += ch[: max(0, min(len(ch), N2 - i))]
amb = np.stack([amb * 0.9, amb], 1)
write_ogg('ambience.ogg', amb / np.abs(amb).max() * 0.6, SR)
print('ambience ok')
