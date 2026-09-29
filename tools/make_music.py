"""Calm procedural music loop + forest ambience for Timber Valley."""
import numpy as np, soundfile as sf
def write_ogg(path, data, sr):
    with sf.SoundFile(path, 'w', sr, data.shape[1], format='OGG', subtype='VORBIS') as f:
        for i in range(0, len(data), 4096):
            f.write(np.ascontiguousarray(data[i:i+4096]))
from scipy.signal import fftconvolve, butter, sosfilt
SR = 44100
rng = np.random.default_rng(7)
BPM = 76
beat = 60 / BPM
bars = 16
dur = bars * 4 * beat
N = int(dur * SR)
L = np.zeros(N); R = np.zeros(N)

def note_hz(m): return 440 * 2 ** ((m - 69) / 12)

def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if i >= N: return
    buf[i:j] += sig[: j - i] * gain
    # wrap the tail around so the loop is seamless
    rest = len(sig) - (j - i)
    if rest > 0:
        buf[:rest] += sig[j - i:] * gain

def epiano(m, length, vel=0.5):
    t = np.arange(int((length + 2.5) * SR)) / SR
    f = note_hz(m)
    env = np.exp(-t * 1.6) * np.minimum(1, t * 200)
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3) + 0.08 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 5)
    sig *= 1 + 0.04 * np.sin(2 * np.pi * 4.5 * t)
    return sig * env * vel

def pluck(m, vel=0.4, length=3.0):
    f = note_hz(m); n = int(SR / f)
    buf = rng.uniform(-1, 1, n)
    out = np.zeros(int(length * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]
        buf[i % n] = 0.996 * 0.5 * (buf[i % n] + buf[(i + 1) % n])
    return out * vel

def pad(ms, length, vel=0.12):
    t = np.arange(int((length + 1.5) * SR)) / SR
    env = np.minimum(1, t / 1.2) * np.minimum(1, np.maximum(0, (length + 1.5 - t) / 1.5))
    sig = np.zeros_like(t)
    for m in ms:
        for det in (-0.12, 0.12):
            f = note_hz(m + det)
            sig += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return sig * env * vel / len(ms)

# Cmaj7 - Am7 - Fmaj7 - G6sus, two bars each, twice.
chords = [[48, 55, 59, 64], [45, 52, 55, 60], [41, 48, 52, 57], [43, 50, 55, 59]]
penta = [60, 62, 64, 67, 69, 72, 74, 76]
t0 = 0.0
for rep in range(2):
    for ci, ch in enumerate(chords):
        start = (rep * 8 + ci * 2) * 4 * beat
        p = pad(ch, 8 * beat)
        add(L, start, p, 0.9); add(R, start, p, 1.0)
        bass = epiano(ch[0] - 12, 2, 0.35)
        add(L, start, bass); add(R, start, bass)
        add(L, start + 4 * beat, epiano(ch[0] - 12, 2, 0.28)); add(R, start + 4 * beat, epiano(ch[0] - 12, 2, 0.28))
        # gentle broken chord on the piano
        for k, bt in enumerate([0, 1.5, 3, 4.5, 6]):
            m = ch[1 + (k % 3)] + 12
            s = epiano(m, 1.5, 0.16)
            pan = 0.35 + 0.3 * (k % 2)
            add(L, start + bt * beat, s, 1 - pan); add(R, start + bt * beat, s, pan)
# sparse plucked melody drawn from the pentatonic scale
for b in range(bars * 4):
    if rng.random() < 0.38 and b % 2 == 0 or rng.random() < 0.12:
        m = int(rng.choice(penta))
        s = pluck(m, 0.22)
        pan = rng.uniform(0.3, 0.7)
        add(L, b * beat + rng.choice([0, 0.5]) * beat, s, 1 - pan); add(R, b * beat, s, pan)

def reverb(x):
    t = np.arange(int(1.8 * SR)) / SR
    ir = rng.normal(0, 1, len(t)) * np.exp(-t * 3.2)
    ir[0] = 0
    y = fftconvolve(x, ir)[: len(x) + len(ir)]
    # fold the tail back into the start for a seamless loop
    out = y[: len(x)].copy(); out[: len(y) - len(x)] += y[len(x):]
    return out
wetL, wetR = reverb(L), reverb(R)
L = L + 0.05 * wetL; R = R + 0.05 * wetR
sos = butter(2, 5500, 'low', fs=SR, output='sos')
L = sosfilt(sos, L); R = sosfilt(sos, R)
mx = max(np.abs(L).max(), np.abs(R).max())
st = np.stack([L, R], 1) / mx * 0.7
write_ogg('music.ogg', st, SR)
print('music', dur, 's')

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
