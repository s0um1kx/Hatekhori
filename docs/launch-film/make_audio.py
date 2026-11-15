import array
import json
import math
import wave
from pathlib import Path

SR = 44100
DURATION = 20.0
TOTAL_SAMPLES = int(SR * DURATION)
BPM = 120
BEAT_DUR = 60.0 / BPM  # 0.50 s

def clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))

# Sound synthesis primitives
def make_kick(t_rel):
    if t_rel < 0 or t_rel > 0.35:
        return 0.0
    f = 50 + 110 * math.exp(-t_rel / 0.04)
    amp = math.exp(-t_rel / 0.12)
    return math.sin(2 * math.pi * f * t_rel) * amp

def make_snare(t_rel):
    if t_rel < 0 or t_rel > 0.25:
        return 0.0
    tonal = math.sin(2 * math.pi * 180 * t_rel) * math.exp(-t_rel / 0.05) * 0.4
    # Deterministic noise burst
    noise = (math.sin(t_rel * 98234.1) * 43758.5453 % 1.0) * 2 - 1
    noise_env = math.exp(-t_rel / 0.08) * 0.6
    return (tonal + noise * noise_env)

def make_hihat(t_rel, closed=True):
    dur = 0.05 if closed else 0.15
    if t_rel < 0 or t_rel > dur:
        return 0.0
    noise = (math.sin(t_rel * 148234.7) * 43758.5453 % 1.0) * 2 - 1
    # High-pass resonance simulation
    res = math.sin(2 * math.pi * 8500 * t_rel) * 0.3
    amp = math.exp(-t_rel / (0.02 if closed else 0.07))
    return (noise * 0.7 + res) * amp * 0.35

def make_bass(t_rel, freq, dur=0.45):
    if t_rel < 0 or t_rel > dur:
        return 0.0
    amp = math.exp(-t_rel / (dur * 0.8))
    # Soft saturation
    raw = math.sin(2 * math.pi * freq * t_rel) + 0.3 * math.sin(4 * math.pi * freq * t_rel)
    return math.tanh(raw * 1.5) * amp * 0.5

def make_chord(t_rel, freqs, dur=1.8):
    if t_rel < 0 or t_rel > dur:
        return 0.0
    amp = math.sin(math.pi * min(1.0, t_rel / (dur * 0.15))) * math.exp(-t_rel / dur)
    s = sum(math.sin(2 * math.pi * f * t_rel) for f in freqs) / len(freqs)
    return s * amp * 0.4

def main():
    print(f"Generating 120 BPM sound composition for {DURATION}s ({TOTAL_SAMPLES} samples)...")
    music_l = [0.0] * TOTAL_SAMPLES
    music_r = [0.0] * TOTAL_SAMPLES

    # Frequencies for C minor palette (C3=130.81, Eb3=155.56, G3=196.00, Bb3=233.08, C4=261.63, Eb4=311.13, G4=392.00, Bb4=466.16)
    CHORD_CM = [261.63, 311.13, 392.00, 466.16]  # Cm7
    CHORD_FM = [261.63, 349.23, 415.30, 523.25]  # Fm7
    CHORD_AB = [261.63, 329.63, 415.30, 523.25]  # Abmaj7
    CHORD_BB = [233.08, 293.66, 349.23, 466.16]  # Bb7

    # 1. Synthesize Beat & Musical Elements
    for i in range(TOTAL_SAMPLES):
        t = i / SR
        beat_idx = t / BEAT_DUR
        beat_num = int(beat_idx)
        t_beat = (t % BEAT_DUR)

        val_l = 0.0
        val_r = 0.0

        # Ambient low-end drone throughout (C2 = 65.41 Hz)
        drone = math.sin(2 * math.pi * 65.41 * t) * 0.12 * (1 + 0.08 * math.sin(2 * math.pi * 0.25 * t))
        val_l += drone
        val_r += drone

        # Hi-hats: every 8th note (every 0.25s) starting at Beat 4
        if beat_num >= 4:
            t_sub = (t % 0.25)
            hh = make_hihat(t_sub, closed=(int(t / 0.25) % 2 == 0))
            val_l += hh * 0.7
            val_r += hh * 0.9

        # Part 1 (Beats 0 to 8 - Hook & Sheet): Minimal pulse
        if beat_num < 8:
            if beat_num % 2 == 0:
                k = make_kick(t_beat)
                val_l += k * 0.8
                val_r += k * 0.8
            if beat_num in (0, 4):
                ch = make_chord(t % (BEAT_DUR * 4), CHORD_CM, dur=1.8)
                val_l += ch * 0.6
                val_r += ch * 0.7

        # Part 2 (Beats 8 to 16 - Ingest & Scanning): Rhythm picks up
        elif beat_num < 16:
            # Kick on 1 and 3
            if beat_num % 2 == 0:
                k = make_kick(t_beat)
                val_l += k * 0.85
                val_r += k * 0.85
            # Bassline
            freq = 65.41 if beat_num < 12 else 87.31 # C2 -> F2
            b = make_bass(t_beat, freq)
            val_l += b * 0.7
            val_r += b * 0.7

        # Part 3 (Beats 16 to 20 - Buildup to Drop): Snare roll & riser
        elif beat_num < 20:
            # Riser tension
            progress = (t - 8.0) / 2.0
            riser = math.sin(2 * math.pi * (200 + 600 * (progress ** 2)) * t) * (progress * 0.25)
            val_l += riser
            val_r += riser
            # Fast snare rolls
            sub_step = (t % 0.125)
            sn = make_snare(sub_step) * (progress * 0.6)
            val_l += sn
            val_r += sn

        # Part 4 (Beats 20 to 36 - THE DROP! High Energy):
        elif beat_num < 36:
            # Four on the floor kick
            k = make_kick(t_beat)
            val_l += k * 1.0
            val_r += k * 1.0
            # Snare on beats 2 and 4
            if beat_num % 2 == 1:
                sn = make_snare(t_beat)
                val_l += sn * 0.85
                val_r += sn * 0.85
            # Pumping bassline
            b_freq = [65.41, 77.78, 87.31, 98.00][(beat_num // 4) % 4]
            b = make_bass(t_beat, b_freq)
            val_l += b * 0.9
            val_r += b * 0.9
            # Bright chord stabs
            if beat_num % 4 == 0:
                ch = make_chord(t_beat, CHORD_CM, dur=1.6)
                val_l += ch * 0.8
                val_r += ch * 0.85

        # Part 5 (Beats 36 to 40 - Outro & Resolution):
        else:
            if beat_num == 36:
                ch = make_chord(t_beat, CHORD_CM, dur=2.0)
                val_l += ch * 0.9
                val_r += ch * 0.95
            decay = max(0.0, 1.0 - (t - 18.0) / 2.0)
            val_l *= decay
            val_r *= decay

        music_l[i] = val_l
        music_r[i] = val_r

    # 2. Add Synthesized SFX Cues from scenes.js
    cues_list = [
        ("whoosh", 0.1,  -4),
        ("click",  1.5,  -2),
        ("whoosh", 2.0,  -3),
        ("click",  2.5,  -2),
        ("whoosh", 4.0,  -3),
        ("thud",   4.4,  -4),
        ("pop",    4.7,  -2),
        ("click",  5.6,  -2),
        ("click",  6.1,  -2),
        ("whoosh", 7.0,  -3),
        ("chime",  10.0, 0),  # THE DROP CLIMAX!
        ("click",  10.2, -2),
        ("tick",   10.4, -3),
        ("tick",   10.6, -3),
        ("tick",   10.8, -3),
        ("tick",   11.0, -3),
        ("click",  12.0, -2),
        ("tick",   12.2, -3),
        ("tick",   12.4, -3),
        ("click",  13.0, -2),
        ("whoosh", 14.0, -3),
        ("whoosh", 17.0, -3),
        ("chime",  18.0, -1),
        ("click",  18.0, -2)
    ]

    for sound_type, cue_t, gain_db in cues_list:
        start_samp = int(cue_t * SR)
        gain = 10 ** (gain_db / 20.0)

        if sound_type == "chime":
            # Resonant bell chime (C5 = 523.25 Hz + rich harmonics)
            for s in range(int(SR * 2.2)):
                idx = (start_samp + s) % TOTAL_SAMPLES
                t_c = s / SR
                sig = (math.sin(2 * math.pi * 523.25 * t_c) * 1.0 +
                       math.sin(2 * math.pi * 1046.5 * t_c) * 0.4 +
                       math.sin(2 * math.pi * 1569.75 * t_c) * 0.25) * math.exp(-t_c / 0.6)
                music_l[idx] += sig * gain * 0.6
                music_r[idx] += sig * gain * 0.7

        elif sound_type == "click":
            for s in range(int(SR * 0.04)):
                idx = (start_samp + s) % TOTAL_SAMPLES
                t_c = s / SR
                sig = math.sin(2 * math.pi * 3200 * t_c) * math.exp(-t_c / 0.006)
                music_l[idx] += sig * gain * 0.5
                music_r[idx] += sig * gain * 0.5

        elif sound_type == "tick":
            for s in range(int(SR * 0.025)):
                idx = (start_samp + s) % TOTAL_SAMPLES
                t_c = s / SR
                sig = math.sin(2 * math.pi * 4800 * t_c) * math.exp(-t_c / 0.004)
                music_l[idx] += sig * gain * 0.4
                music_r[idx] += sig * gain * 0.4

        elif sound_type == "whoosh":
            for s in range(int(SR * 0.4)):
                idx = (start_samp + s) % TOTAL_SAMPLES
                t_c = s / SR
                p = t_c / 0.4
                f = 300 + 1800 * math.sin(p * math.pi)
                sig = math.sin(2 * math.pi * f * t_c) * math.sin(p * math.pi) * 0.3
                music_l[idx] += sig * gain * (1.0 - p * 0.5)
                music_r[idx] += sig * gain * (0.5 + p * 0.5)

        elif sound_type == "pop":
            for s in range(int(SR * 0.08)):
                idx = (start_samp + s) % TOTAL_SAMPLES
                t_c = s / SR
                f = 800 * (1.0 - t_c / 0.08)
                sig = math.sin(2 * math.pi * f * t_c) * math.exp(-t_c / 0.02)
                music_l[idx] += sig * gain * 0.5
                music_r[idx] += sig * gain * 0.5

        elif sound_type == "thud":
            for s in range(int(SR * 0.2)):
                idx = (start_samp + s) % TOTAL_SAMPLES
                t_c = s / SR
                sig = math.sin(2 * math.pi * 75 * t_c) * math.exp(-t_c / 0.05)
                music_l[idx] += sig * gain * 0.6
                music_r[idx] += sig * gain * 0.6

    # 3. Master Limiting & 16-bit PCM Conversion
    # Peak normalization
    max_peak = max(max(abs(l) for l in music_l), max(abs(r) for r in music_r), 1.0)
    norm = 0.92 / max_peak

    interleaved = array.array("h")
    for l, r in zip(music_l, music_r):
        int_l = int(clamp(l * norm) * 32767)
        int_r = int(clamp(r * norm) * 32767)
        interleaved.append(int_l)
        interleaved.append(int_r)

    out_path = Path("docs/launch-film/audio/edit.wav")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(interleaved.tobytes())

    # Also save a copy as track.wav for web preview
    track_path = Path("docs/launch-film/audio/track.wav")
    track_path.write_bytes(out_path.read_bytes())

    print(f"Master soundtrack written successfully to {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")

if __name__ == "__main__":
    main()
