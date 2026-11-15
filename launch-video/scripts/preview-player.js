/**
 * HyperFrames Studio Interactive Player & Frame Scrubber
 * Enables frame-accurate deterministic playback, scrub scrubbing, and audio sync.
 */
(function() {
  'use strict';

  const FPS = 60;
  const TOTAL_DURATION = 28.0;
  const TOTAL_FRAMES = Math.round(TOTAL_DURATION * FPS);

  let isPlaying = false;
  let currentTime = 0;
  let lastTimestamp = null;
  let playbackSpeed = 1.0;
  let isMuted = false;

  const audioClips = [];

  function initPlayer() {
    const root = document.getElementById('root');
    const master = window.__masterTimeline;
    if (!root || !master) {
      setTimeout(initPlayer, 50);
      return;
    }

    // Collect all audio clips
    document.querySelectorAll('audio.clip').forEach(el => {
      audioClips.push({
        element: el,
        start: parseFloat(el.getAttribute('data-start')) || 0,
        duration: parseFloat(el.getAttribute('data-duration')) || 1000,
        volume: parseFloat(el.getAttribute('data-volume')) || 1.0
      });
      el.volume = parseFloat(el.getAttribute('data-volume')) || 1.0;
    });

    // Create Player HUD Overlay
    const hud = document.createElement('div');
    hud.id = 'hyperframes-hud';
    hud.className = 'fixed bottom-4 left-1/2 -translate-x-1/2 w-[95%] max-w-5xl bg-[#0A0A0A]/95 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-[0_20px_50px_rgba(0,0,0,0.9)] z-50 text-white select-none transition-opacity duration-200';
    
    hud.innerHTML = `
      <!-- Top Scrubber Lane -->
      <div class="flex items-center gap-4 mb-3">
        <button id="hf-play-btn" class="w-10 h-10 rounded-xl bg-white text-black flex items-center justify-center font-bold hover:scale-105 active:scale-95 transition-transform shadow-md" title="Play/Pause (Space)">
          <svg id="hf-play-icon" class="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          <svg id="hf-pause-icon" class="w-5 h-5 hidden" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
        </button>

        <div class="flex-1 relative flex items-center">
          <input type="range" id="hf-scrubber" min="0" max="${TOTAL_DURATION}" step="${1/FPS}" value="0" class="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-red-500 focus:outline-none" />
        </div>

        <div class="font-mono text-xs text-zinc-300 min-w-[170px] text-right">
          <span id="hf-timecode" class="text-white font-semibold">00:00:00</span>
          <span class="text-zinc-600">/</span>
          <span class="text-zinc-400">00:28:00</span>
          <span id="hf-framecount" class="text-zinc-500 block text-[10px]">F: 0 / 1680</span>
        </div>
      </div>

      <!-- Bottom Control Bar -->
      <div class="flex items-center justify-between text-xs font-mono text-zinc-400 pt-2 border-t border-white/[0.08]">
        
        <!-- Scene Quick Jumps: English -> Bengali -> Hindi hierarchy -->
        <div class="flex items-center gap-1.5">
          <span class="text-zinc-500 text-[10px] uppercase mr-1">Scenes:</span>
          <button class="hf-jump-btn px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-white/[0.08]" data-time="0.0">1 · Hatekhori Reveal</button>
          <button class="hf-jump-btn px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-white/[0.08]" data-time="5.2">2 · Scripts (EN · BN · HI)</button>
          <button class="hf-jump-btn px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-white/[0.08]" data-time="11.2">3 · Atelier Engine</button>
          <button class="hf-jump-btn px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-white/[0.08]" data-time="17.2">4 · Specimen Lab</button>
          <button class="hf-jump-btn px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-white/[0.08]" data-time="22.5">5 · Ownership & OTF</button>
        </div>

        <!-- Right Side: Audio & Resolution Controls -->
        <div class="flex items-center gap-3">
          <!-- Audio Toggle -->
          <button id="hf-audio-btn" class="flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-white/[0.08]">
            <svg id="hf-sound-on" class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/></svg>
            <svg id="hf-sound-off" class="w-3.5 h-3.5 text-zinc-500 hidden" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"/></svg>
            <span id="hf-audio-text">Audio Sync</span>
          </button>

          <!-- Speed -->
          <select id="hf-speed" class="bg-zinc-900 border border-white/[0.08] text-zinc-300 rounded px-2 py-0.5 text-xs focus:outline-none">
            <option value="0.5">0.5×</option>
            <option value="1.0" selected>1.0×</option>
            <option value="1.5">1.5×</option>
            <option value="2.0">2.0×</option>
          </select>

          <!-- Scale to Fit -->
          <button id="hf-scale-btn" class="px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-white/[0.08]">
            Fit 1080p
          </button>

          <!-- Render Info -->
          <button id="hf-render-btn" class="px-2.5 py-1 rounded bg-red-accent/20 text-red-400 hover:bg-red-accent/30 border border-red-accent/40 font-semibold shadow-sm">
            Render MP4
          </button>
        </div>

      </div>
    `;

    document.body.appendChild(hud);

    function autoScaleViewport() {
      const windowWidth = window.innerWidth;
      const windowHeight = window.innerHeight;
      const targetWidth = 1920;
      const targetHeight = 1080;
      
      const scaleX = windowWidth / targetWidth;
      const scaleY = windowHeight / targetHeight;
      const scale = Math.min(scaleX, scaleY);

      root.style.transformOrigin = 'top left';
      root.style.transform = `scale(${scale})`;
      
      const offsetX = Math.max(0, (windowWidth - targetWidth * scale) / 2);
      const offsetY = Math.max(0, (windowHeight - targetHeight * scale) / 2);
      root.style.marginLeft = `${offsetX}px`;
      root.style.marginTop = `${offsetY}px`;
    }

    window.addEventListener('resize', autoScaleViewport);
    autoScaleViewport();

    const playBtn = document.getElementById('hf-play-btn');
    const playIcon = document.getElementById('hf-play-icon');
    const pauseIcon = document.getElementById('hf-pause-icon');
    const scrubber = document.getElementById('hf-scrubber');
    const timecode = document.getElementById('hf-timecode');
    const framecount = document.getElementById('hf-framecount');
    const audioBtn = document.getElementById('hf-audio-btn');
    const soundOn = document.getElementById('hf-sound-on');
    const soundOff = document.getElementById('hf-sound-off');
    const speedSelect = document.getElementById('hf-speed');
    const renderBtn = document.getElementById('hf-render-btn');

    function updateTimecode(t) {
      const mins = Math.floor(t / 60);
      const secs = Math.floor(t % 60);
      const ms = Math.floor((t % 1) * 100);
      timecode.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}:${String(ms).padStart(2, '0')}`;
      
      const frame = Math.round(t * FPS);
      framecount.textContent = `F: ${frame} / ${TOTAL_FRAMES}`;
      scrubber.value = t;
    }

    function syncAudio(t, isSeeking = false) {
      if (isMuted) {
        audioClips.forEach(c => c.element.pause());
        return;
      }

      audioClips.forEach(c => {
        const el = c.element;
        const clipEnd = c.start + c.duration;
        if (t >= c.start && t < clipEnd) {
          const expectedTime = t - c.start;
          if (isPlaying) {
            if (el.paused || Math.abs(el.currentTime - expectedTime) > 0.15) {
              el.currentTime = expectedTime;
              el.play().catch(() => {});
            }
          } else {
            el.pause();
            el.currentTime = expectedTime;
          }
        } else {
          el.pause();
          el.currentTime = 0;
        }
      });
    }

    function seekTo(t) {
      currentTime = Math.max(0, Math.min(t, TOTAL_DURATION));
      master.seek(currentTime);
      updateTimecode(currentTime);
      syncAudio(currentTime, true);
    }

    function play() {
      if (currentTime >= TOTAL_DURATION) {
        currentTime = 0;
      }
      isPlaying = true;
      lastTimestamp = performance.now();
      playIcon.classList.add('hidden');
      pauseIcon.classList.remove('hidden');
      syncAudio(currentTime);
      requestAnimationFrame(tick);
    }

    function pause() {
      isPlaying = false;
      playIcon.classList.remove('hidden');
      pauseIcon.classList.add('hidden');
      syncAudio(currentTime);
    }

    function togglePlay() {
      if (isPlaying) pause();
      else play();
    }

    function tick(timestamp) {
      if (!isPlaying) return;
      if (!lastTimestamp) lastTimestamp = timestamp;
      const delta = (timestamp - lastTimestamp) / 1000.0;
      lastTimestamp = timestamp;

      currentTime += delta * playbackSpeed;
      if (currentTime >= TOTAL_DURATION) {
        currentTime = TOTAL_DURATION;
        pause();
      }

      master.seek(currentTime);
      updateTimecode(currentTime);
      syncAudio(currentTime);

      if (isPlaying) {
        requestAnimationFrame(tick);
      }
    }

    playBtn.addEventListener('click', togglePlay);

    scrubber.addEventListener('input', e => {
      const val = parseFloat(e.target.value);
      seekTo(val);
    });

    document.querySelectorAll('.hf-jump-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const t = parseFloat(btn.getAttribute('data-time'));
        seekTo(t);
      });
    });

    speedSelect.addEventListener('change', e => {
      playbackSpeed = parseFloat(e.target.value);
    });

    audioBtn.addEventListener('click', () => {
      isMuted = !isMuted;
      if (isMuted) {
        soundOn.classList.add('hidden');
        soundOff.classList.remove('hidden');
      } else {
        soundOn.classList.remove('hidden');
        soundOff.classList.add('hidden');
      }
      syncAudio(currentTime);
    });

    window.addEventListener('keydown', e => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;

      if (e.code === 'Space') {
        e.preventDefault();
        togglePlay();
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        const step = e.shiftKey ? 1.0 : (1 / FPS);
        seekTo(currentTime + step);
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        const step = e.shiftKey ? 1.0 : (1 / FPS);
        seekTo(currentTime - step);
      } else if (e.key === '1') seekTo(0.0);
      else if (e.key === '2') seekTo(5.2);
      else if (e.key === '3') seekTo(11.2);
      else if (e.key === '4') seekTo(17.2);
      else if (e.key === '5') seekTo(22.5);
    });

    renderBtn.addEventListener('click', () => {
      alert(
        "HyperFrames Video Master:\n\n" +
        "To render 60fps high-definition MP4:\n" +
        "Run in terminal: npm run render\n" +
        "(Or: npx hyperframes render --output dist/hatekhori-launch-60fps.mp4 --fps 60 --chroma-subsampling 444)\n\n" +
        "Everything in this timeline is 100% deterministic and frame-accurate."
      );
    });

    seekTo(0);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPlayer);
  } else {
    initPlayer();
  }
})();
