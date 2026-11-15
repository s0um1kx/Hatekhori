import wave
import struct
import math
import random
import os

SAMPLE_RATE = 44100

def write_stereo_wav(filepath, left_samples, right_samples):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    num_samples = min(len(left_samples), len(right_samples))
    with wave.open(filepath, 'w') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        raw = bytearray()
        for i in range(num_samples):
            # Soft-clip and master limiting
            l = max(-0.98, min(0.98, left_samples[i]))
            r = max(-0.98, min(0.98, right_samples[i]))
            il = int(l * 32767.0)
            ir = int(r * 32767.0)
            raw.extend(struct.pack('<hh', il, ir))
        f.writeframes(raw)
    print(f"Generated {filepath} ({num_samples / SAMPLE_RATE:.2f}s)")

# Simple stereo delay / reverb processor
def apply_reverb(left, right, decay=0.45, delay_ms=180):
    delay_samples = int(SAMPLE_RATE * (delay_ms / 1000.0))
    d_left = int(delay_samples * 1.0)
    d_right = int(delay_samples * 1.25)
    
    out_l = list(left)
    out_r = list(right)
    
    for i in range(len(left)):
        if i >= d_left:
            out_l[i] += out_l[i - d_left] * decay
        if i >= d_right:
            out_r[i] += out_r[i - d_right] * decay
            
    return out_l, out_r

# Piano Note Synthesizer (Acoustic physical modeling approximation)
def synth_piano_note(freq, duration, velocity=0.8):
    samples = []
    n = int(SAMPLE_RATE * duration)
    # Partials with exponential damping
    partials = [
        (1.0, 1.0, 1.2),     # Fundamental
        (2.0, 0.55, 2.0),    # 2nd harmonic
        (3.0, 0.35, 3.1),    # 3rd harmonic
        (4.0, 0.22, 4.2),    # 4th harmonic
        (5.0, 0.14, 5.5),    # 5th harmonic
        (6.0, 0.08, 7.0),    # 6th harmonic
        (7.0, 0.04, 8.5),    # 7th harmonic
    ]
    for i in range(n):
        t = i / SAMPLE_RATE
        # Hammer attack click
        hammer = math.exp(-140.0 * t) * math.sin(2.0 * math.pi * 800.0 * t) * 0.25
        val = 0.0
        for mult, amp, damp in partials:
            # Slight detuning for acoustic warmth (chorus)
            f = freq * mult
            detune = 1.0 + (mult - 1) * 0.0006
            env = math.exp(-damp * (2.8 / (1.0 + freq / 400.0)) * t)
            val += amp * env * math.sin(2.0 * math.pi * f * detune * t)
        
        total = (val + hammer) * velocity * 0.4
        samples.append(total)
    return samples

# Orchestral String Pad Synthesizer
def synth_string_pad(freqs, duration, attack=1.2, release=1.5):
    n = int(SAMPLE_RATE * duration)
    left = [0.0] * n
    right = [0.0] * n
    
    for fi, base_f in enumerate(freqs):
        for i in range(n):
            t = i / SAMPLE_RATE
            # Envelope with smooth attack and release
            if t < attack:
                env = math.sin((t / attack) * (math.pi / 2.0))
            elif t > (duration - release):
                env = math.cos(((t - (duration - release)) / release) * (math.pi / 2.0))
            else:
                env = 1.0
                
            # Ensemble chorus oscillators
            osc1 = math.sin(2.0 * math.pi * base_f * t)
            osc2 = math.sin(2.0 * math.pi * (base_f * 1.002) * t) * 0.8
            osc3 = math.sin(2.0 * math.pi * (base_f * 0.998) * t) * 0.8
            # Gentle vibrato
            vib = math.sin(2.0 * math.pi * 5.0 * t) * 0.003
            osc4 = math.sin(2.0 * math.pi * (base_f * (1.0 + vib)) * t) * 0.6
            
            combined = (osc1 + osc2 + osc3 + osc4) * 0.25 * env
            # Stereo spread based on chord position
            pan = (fi / max(1, len(freqs) - 1)) * 0.6 - 0.3
            left[i] += combined * (0.5 - pan * 0.5)
            right[i] += combined * (0.5 + pan * 0.5)
            
    return left, right

# 1. BGM: High-End Cinematic Soundtrack (28.0s)
def generate_cinematic_bgm():
    total_duration = 28.0
    num_samples = int(SAMPLE_RATE * total_duration)
    master_left = [0.0] * num_samples
    master_right = [0.0] * num_samples
    
    # Chord schedule (Time, Name, Chord Frequencies)
    # Evocative, emotional, luxury progression:
    # 0.0s - 5.5s : Dm9 (D2, A2, F3, A3, C4, E4)
    # 5.2s - 11.5s: Fmaj9 (F2, C3, A3, C4, E4, G4)
    # 11.2s - 17.5s: Bbmaj7#11 (Bb1, F2, D3, A3, C4, E4)
    # 17.2s - 22.5s: Gm9 -> C7sus (G1, D2, Bb2, D3, F3, A3)
    # 22.2s - 28.0s: Dm(add9) Resolution (D2, A2, D3, F3, A3, E4)
    
    chords = [
        (0.0, 5.5, [73.42, 110.00, 174.61, 220.00, 261.63, 329.63]),
        (5.2, 11.5, [87.31, 130.81, 220.00, 261.63, 329.63, 392.00]),
        (11.2, 17.5, [58.27, 87.31, 146.83, 220.00, 261.63, 329.63]),
        (17.2, 22.5, [49.00, 73.42, 116.54, 146.83, 174.61, 220.00]),
        (22.2, 28.0, [73.42, 110.00, 146.83, 174.61, 220.00, 329.63])
    ]
    
    # Add Lush Strings
    for start_t, end_t, chord_freqs in chords:
        dur = end_t - start_t
        str_l, str_r = synth_string_pad(chord_freqs[1:], dur, attack=0.8, release=1.0)
        start_idx = int(start_t * SAMPLE_RATE)
        for i in range(len(str_l)):
            idx = start_idx + i
            if idx < num_samples:
                master_left[idx] += str_l[i] * 0.45
                master_right[idx] += str_r[i] * 0.45

    # Piano Melodic Motifs (Elegantly spaced notes that create space and emotion)
    piano_notes = [
        # Scene 1: Calm, reflective opening
        (0.2, 73.42, 4.5, 0.85),   # D2 (Deep root)
        (0.8, 220.00, 3.5, 0.75),  # A3
        (1.5, 329.63, 3.0, 0.70),  # E4
        (2.4, 440.00, 2.5, 0.80),  # A4
        (3.5, 392.00, 2.0, 0.65),  # G4
        
        # Scene 2: Brightening up for multi-script reveal
        (5.3, 87.31, 4.5, 0.85),   # F2
        (5.8, 261.63, 3.2, 0.75),  # C4
        (6.5, 329.63, 3.0, 0.70),  # E4
        (7.4, 392.00, 2.8, 0.82),  # G4
        (8.5, 523.25, 2.2, 0.85),  # C5
        (9.8, 440.00, 2.0, 0.70),  # A4
        
        # Scene 3: The precision atelier engine
        (11.3, 58.27, 4.8, 0.90),  # Bb1
        (11.9, 293.66, 3.5, 0.78), # D4
        (12.7, 329.63, 3.0, 0.72), # E4 (#11 color)
        (13.6, 440.00, 2.5, 0.80), # A4
        (14.8, 587.33, 2.2, 0.88), # D5
        (16.0, 523.25, 1.8, 0.75), # C5
        
        # Scene 4: Typographic specimen flow
        (17.3, 49.00, 4.5, 0.90),  # G1
        (17.9, 220.00, 3.2, 0.75), # A3
        (18.6, 349.23, 2.8, 0.80), # F4
        (19.4, 440.00, 2.5, 0.82), # A4
        (20.3, 523.25, 2.0, 0.85), # C5
        (21.2, 659.25, 1.8, 0.78), # E5
        
        # Scene 5: Resolution & Climax
        (22.4, 73.42, 5.5, 0.95),  # D2 (Grand bottom octave)
        (22.4, 146.83, 5.5, 0.85), # D3
        (22.8, 220.00, 5.0, 0.80), # A3
        (23.2, 329.63, 4.5, 0.82), # E4
        (23.8, 440.00, 4.2, 0.88), # A4
        (24.5, 587.33, 3.8, 0.92), # D5
        (25.4, 880.00, 3.0, 0.75), # A5 (Glittering high note)
    ]
    
    for note_time, freq, dur, vel in piano_notes:
        p_samples = synth_piano_note(freq, dur, vel)
        start_idx = int(note_time * SAMPLE_RATE)
        # Pan piano slightly left for bass, slightly right for trebles
        pan = 0.5 + (math.log(freq / 220.0) if freq > 0 else 0) * 0.15
        pan = max(0.2, min(0.8, pan))
        for i in range(len(p_samples)):
            idx = start_idx + i
            if idx < num_samples:
                master_left[idx] += p_samples[i] * (1.0 - pan) * 0.65
                master_right[idx] += p_samples[i] * pan * 0.65

    # Cinematic Heartbeat / Sub Pulse (starts at Scene 2 @ 5.2s until 24.5s)
    # 108 BPM: Beat period = 60 / 108 = 0.5555s
    beat_period = 60.0 / 108.0
    pulse_start_t = 5.2
    pulse_end_t = 24.0
    cur_t = pulse_start_t
    while cur_t < pulse_end_t:
        idx = int(cur_t * SAMPLE_RATE)
        # Deep soft warm sub kick (50Hz sine with quick decay)
        kick_dur = 0.35
        kick_n = int(SAMPLE_RATE * kick_dur)
        for ki in range(kick_n):
            kt = ki / SAMPLE_RATE
            kfreq = 48.0 + 40.0 * math.exp(-25.0 * kt)
            kval = math.sin(2.0 * math.pi * kfreq * kt) * math.exp(-12.0 * kt) * 0.28
            target_idx = idx + ki
            if target_idx < num_samples:
                master_left[target_idx] += kval
                master_right[target_idx] += kval
                
        # Delicate organic paper/brush hi-hat on the off-beat (+0.277s)
        hat_t = cur_t + beat_period * 0.5
        hat_idx = int(hat_t * SAMPLE_RATE)
        hat_n = int(SAMPLE_RATE * 0.08)
        rng = random.Random(int(hat_t * 1000))
        for hi in range(hat_n):
            ht = hi / SAMPLE_RATE
            hval = (rng.random() * 2.0 - 1.0) * math.exp(-55.0 * ht) * 0.05
            target_idx = hat_idx + hi
            if target_idx < num_samples:
                master_left[target_idx] += hval * 0.6
                master_right[target_idx] += hval * 0.4
                
        cur_t += beat_period

    # Add Stereo Reverb space
    master_left, master_right = apply_reverb(master_left, master_right, decay=0.35, delay_ms=160)

    # Master Fade-in and Fade-out
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = 1.0
        if t < 0.6:
            env = t / 0.6
        elif t > 25.5:
            env = max(0.0, (28.0 - t) / 2.5)
        # Soft tape saturation
        master_left[i] = math.tanh(master_left[i] * env * 1.05) * 0.88
        master_right[i] = math.tanh(master_right[i] * env * 1.05) * 0.88

    write_stereo_wav("assets/audio/bgm-ambient.wav", master_left, master_right)

# 2. Tactile, Premium Sound Effects Suite
def generate_sfx():
    # 2.1 Sub Drop: Velvety cinematic low-end boom
    dur = 2.5
    n = int(SAMPLE_RATE * dur)
    left, right = [], []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 30.0 + 45.0 * math.exp(-3.0 * t)
        phase = 2.0 * math.pi * (30.0 * t + (45.0 / -3.0) * (math.exp(-3.0 * t) - 1.0))
        val = math.sin(phase) * math.exp(-1.2 * t) * 0.75
        val += 0.25 * math.sin(phase * 0.5) * math.exp(-1.5 * t)
        val = math.tanh(val) * 0.8
        left.append(val)
        right.append(val)
    write_stereo_wav("assets/audio/sfx-sub-drop.wav", left, right)

    # 2.2 Chalk Stroke: Tactile chalk on slate / pen on paper ASMR
    dur = 1.2
    n = int(SAMPLE_RATE * dur)
    left, right = [], []
    rng = random.Random(42)
    for i in range(n):
        t = i / SAMPLE_RATE
        stroke = (math.sin(math.pi * min(1.0, max(0.0, (t - 0.05) / 0.45))) ** 2 if 0.05 <= t <= 0.50 else 0.0) + \
                 (math.sin(math.pi * min(1.0, max(0.0, (t - 0.52) / 0.55))) ** 2 if 0.52 <= t <= 1.07 else 0.0)
        noise = rng.random() * 2.0 - 1.0
        # Resonance peaks around 1.1kHz and 2.4kHz
        sig = (math.sin(2.0 * math.pi * 1100.0 * t + noise * 0.3) * 0.35 +
               math.sin(2.0 * math.pi * 2350.0 * t + noise * 0.4) * 0.25 +
               noise * 0.2) * stroke * 0.55
        left.append(sig)
        right.append(sig * 0.95)
    write_stereo_wav("assets/audio/sfx-chalk-stroke.wav", left, right)

    # 2.3 Whoosh: Smooth air sweep with stereo panning
    dur = 0.9
    n = int(SAMPLE_RATE * dur)
    left, right = [], []
    rng = random.Random(1337)
    for i in range(n):
        t = i / SAMPLE_RATE
        p = t / dur
        env = math.exp(-((p - 0.45) ** 2) / 0.035)
        sweep_freq = 180.0 + 2200.0 * math.exp(-((p - 0.42) ** 2) / 0.045)
        noise = rng.random() * 2.0 - 1.0
        tone = math.sin(2.0 * math.pi * sweep_freq * t) * 0.25
        comb = (noise * 0.75 + tone) * env * 0.65
        pan = (p * 1.6) - 0.8
        pan_l = math.cos((pan + 1.0) * math.pi / 4.0)
        pan_r = math.sin((pan + 1.0) * math.pi / 4.0)
        left.append(comb * pan_l)
        right.append(comb * pan_r)
    write_stereo_wav("assets/audio/sfx-whoosh.wav", left, right)

    # 2.4 Card Pop: Crisp tactile acoustic tap (like Apple UI feedback)
    dur = 0.22
    n = int(SAMPLE_RATE * dur)
    left, right = [], []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 160.0 + 460.0 * math.exp(-45.0 * t)
        phase = 2.0 * math.pi * (160.0 * t + (460.0 / -45.0) * (math.exp(-45.0 * t) - 1.0))
        val = math.sin(phase) * math.exp(-24.0 * t) * 0.75
        left.append(val)
        right.append(val)
    write_stereo_wav("assets/audio/sfx-card-pop.wav", left, right)

    # 2.5 Shutter: Mechanical precision leaf shutter
    dur = 0.35
    n = int(SAMPLE_RATE * dur)
    left, right = [], []
    rng = random.Random(888)
    for i in range(n):
        t = i / SAMPLE_RATE
        c1 = math.exp(-140.0 * abs(t - 0.02)) * (math.sin(2.0 * math.pi * 1600.0 * t) + rng.random()*0.4) if t >= 0.01 else 0.0
        c2 = math.exp(-110.0 * abs(t - 0.075)) * (math.sin(2.0 * math.pi * 1100.0 * t) + rng.random()*0.3) if t >= 0.065 else 0.0
        body = math.exp(-32.0 * t) * math.sin(2.0 * math.pi * 380.0 * t) * 0.3
        val = (c1 * 0.7 + c2 * 0.85 + body) * 0.7
        left.append(val)
        right.append(val)
    write_stereo_wav("assets/audio/sfx-shutter.wav", left, right)

    # 2.6 Matrix Tick: Micro quartz tick
    dur = 0.12
    n = int(SAMPLE_RATE * dur)
    left, right = [], []
    for i in range(n):
        t = i / SAMPLE_RATE
        val = (math.sin(2.0 * math.pi * 2200.0 * t) * 0.7 + math.sin(2.0 * math.pi * 4400.0 * t) * 0.3) * math.exp(-95.0 * t) * 0.55
        left.append(val)
        right.append(val)
    write_stereo_wav("assets/audio/sfx-matrix-tick.wav", left, right)

    # 2.7 Chime: Crystal celestial chord
    dur = 2.2
    n = int(SAMPLE_RATE * dur)
    left, right = [], []
    harmonics = [587.33, 739.99, 880.0, 1174.66, 1479.98]
    weights = [0.35, 0.28, 0.22, 0.15, 0.08]
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-2.0 * t)
        l_val, r_val = 0.0, 0.0
        for idx, (f, w) in enumerate(zip(harmonics, weights)):
            l_val += math.sin(2.0 * math.pi * (f - 0.3 * idx) * t) * w
            r_val += math.sin(2.0 * math.pi * (f + 0.3 * idx) * t) * w
        left.append(l_val * env * 0.6)
        right.append(r_val * env * 0.6)
    write_stereo_wav("assets/audio/sfx-chime.wav", left, right)

if __name__ == '__main__':
    os.chdir("C:/Users/Administrator/Hatekhori/launch-video")
    print("Generating high-end cinematic soundtrack and tactile SFX...")
    generate_cinematic_bgm()
    generate_sfx()
    print("Audio suite generated successfully!")
