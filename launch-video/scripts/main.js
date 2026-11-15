/**
 * Hatekhori Product Launch Video - Master Timeline Choreography
 * English Dominant -> Bengali -> Hindi Hierarchy.
 * HyperFrames-compliant deterministic animation & camera stages.
 */
(function() {
  'use strict';

  function initTimeline() {
    const gsap = window.gsap;
    if (!gsap) {
      console.error('HyperFrames: GSAP not loaded');
      return;
    }

    const master = gsap.timeline({ paused: true });

    // ==========================================
    // CAMERA RIG CHOREOGRAPHY (#camera-rig)
    // ==========================================
    // Scene 1: Slow continuous Ken Burns drift
    master.fromTo('#camera-rig', 
      { scale: 1.0, x: 0, y: 0 }, 
      { scale: 1.05, x: 0, y: -12, duration: 5.2, ease: 'none' }, 
      0
    );

    // Scene 2: Sweep across 3D floating cards
    master.fromTo('#camera-rig',
      { scale: 1.04, x: 20, y: -8 },
      { scale: 1.00, x: -20, y: 0, duration: 6.0, ease: 'power1.inOut' },
      5.2
    );

    // Scene 3: Settles smoothly on Atelier scanner/vectorizer
    master.fromTo('#camera-rig',
      { scale: 1.00, x: 0, y: 0 },
      { scale: 1.04, x: 0, y: 4, duration: 6.0, ease: 'power1.inOut' },
      11.2
    );

    // Scene 4: Wide view -> Dynamic punch-in into Unicode Character Inspector
    master.fromTo('#camera-rig',
      { scale: 1.00, x: 0, y: 0 },
      { scale: 1.00, x: 0, y: 0, duration: 2.2, ease: 'none' },
      17.2
    );
    // Camera punch-in
    master.fromTo('#camera-rig',
      { scale: 1.00, x: 0, y: 0 },
      { scale: 1.58, x: -380, y: -25, duration: 1.2, ease: 'power3.inOut' },
      19.4
    );
    // Hold focus with subtle drift
    master.fromTo('#camera-rig',
      { scale: 1.58, x: -380, y: -25 },
      { scale: 1.62, x: -390, y: -30, duration: 1.8, ease: 'none' },
      20.6
    );

    // Scene 5: Grand pull-back to resolution
    master.fromTo('#camera-rig',
      { scale: 1.05, x: 0, y: -8 },
      { scale: 1.00, x: 0, y: 0, duration: 5.5, ease: 'power2.out' },
      22.5
    );

    // ==========================================
    // SCENE 1: ENGLISH DOMINANT REVEAL (0.0s - 5.5s)
    // ==========================================
    master.fromTo('#scene-ritual', { opacity: 0 }, { opacity: 1, duration: 0.6, ease: 'power2.out' }, 0);

    // Atelier Emblem
    master.fromTo('#s1-symbol-wrap', 
      { opacity: 0, scale: 0.8 }, 
      { opacity: 1, scale: 1.0, duration: 1.2, ease: 'back.out(1.5)' }, 
      0.2
    );
    master.fromTo('#s1-symbol-glow',
      { opacity: 0, scale: 0.5 },
      { opacity: 0.8, scale: 1.4, duration: 1.8, ease: 'power2.out' },
      0.3
    );

    // English Dominant Brand Headline
    master.fromTo('#s1-english-title',
      { opacity: 0, y: 40, filter: 'blur(12px)' },
      { opacity: 1, y: 0, filter: 'blur(0px)', duration: 1.2, ease: 'power3.out' },
      0.8
    );

    // Bengali & Hindi Subtitle Lockup
    master.fromTo('#s1-scripts-sub',
      { opacity: 0, y: 15 },
      { opacity: 1, y: 0, duration: 0.9, ease: 'power2.out' },
      1.3
    );

    // Editorial Statements
    master.fromTo('#s1-desc',
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 1.0, ease: 'power2.out' },
      1.8
    );
    master.fromTo('#s1-heritage',
      { opacity: 0, y: 15 },
      { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' },
      2.2
    );

    // Minimalist Luxury Badge
    master.fromTo('#s1-badge',
      { opacity: 0, scale: 0.92 },
      { opacity: 1, scale: 1.0, duration: 0.7, ease: 'back.out(1.4)' },
      2.6
    );

    // Outro transition
    master.fromTo('#scene-ritual',
      { opacity: 1, y: 0 },
      { opacity: 0, y: -45, duration: 0.6, ease: 'power2.in' },
      4.8
    );

    // ==========================================
    // SCENE 2: MULTI-SCRIPT FOUNDATION (5.0s - 11.5s)
    // ==========================================
    master.fromTo('#scene-scripts', { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power2.out' }, 5.0);

    master.fromTo('#s2-tag', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }, 5.1);
    master.fromTo('#s2-headline', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }, 5.3);
    master.fromTo('#s2-subline', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' }, 5.6);

    // Card 1: English (Center Hero, pops first)
    master.fromTo('#s2-card-english',
      { opacity: 0, y: 80, scale: 0.88 },
      { opacity: 1, y: 0, scale: 1.05, duration: 1.1, ease: 'back.out(1.4)' },
      5.6
    );

    // Card 2: Bengali (Left, tilted -12deg)
    master.fromTo('#s2-card-bengali',
      { opacity: 0, x: -280, y: 60, rotateY: -22, scale: 0.88 },
      { opacity: 1, x: -350, y: 0, rotateY: -12, scale: 0.96, duration: 1.1, ease: 'power3.out' },
      6.2
    );

    // Card 3: Hindi (Right, tilted +12deg)
    master.fromTo('#s2-card-hindi',
      { opacity: 0, x: 280, y: 60, rotateY: 22, scale: 0.88 },
      { opacity: 1, x: 350, y: 0, rotateY: 12, scale: 0.96, duration: 1.1, ease: 'power3.out' },
      6.8
    );

    // Bottom proof bar
    master.fromTo('#s2-bottom-bar',
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out' },
      7.4
    );

    // Scene 2 Outro
    master.fromTo('#scene-scripts',
      { opacity: 1, x: 0 },
      { opacity: 0, x: -60, duration: 0.6, ease: 'power2.in' },
      10.8
    );

    // ==========================================
    // SCENE 3: ATELIER VECTORIZATION (11.0s - 17.5s)
    // ==========================================
    master.fromTo('#scene-vector', { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power2.out' }, 11.0);

    master.fromTo('#s3-tag', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }, 11.1);
    master.fromTo('#s3-headline', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }, 11.3);
    master.fromTo('#s3-subline', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' }, 11.5);

    // Left Scanner Panel
    master.fromTo('#s3-capture-panel',
      { opacity: 0, x: -50, scale: 0.95 },
      { opacity: 1, x: 0, scale: 1.0, duration: 0.9, ease: 'power3.out' },
      11.8
    );

    // Right Vector Panel
    master.fromTo('#s3-vector-panel',
      { opacity: 0, x: 50, scale: 0.95 },
      { opacity: 1, x: 0, scale: 1.0, duration: 0.9, ease: 'power3.out' },
      12.2
    );

    // Laser sweep
    master.fromTo('#s3-scan-laser',
      { top: '0%' },
      { top: '100%', duration: 1.6, ease: 'power1.inOut' },
      12.8
    );

    // Glyph vector path reveal
    master.fromTo('#s3-glyph-path',
      { opacity: 0, scale: 0.85 },
      { opacity: 1, scale: 1.0, duration: 1.0, ease: 'power2.out' },
      13.6
    );

    // Anchor nodes pop-in
    master.fromTo('.s3-node',
      { opacity: 0, scale: 0 },
      { opacity: 1, scale: 1.0, duration: 0.5, stagger: 0.08, ease: 'back.out(2.0)' },
      14.2
    );

    // Bottom telemetry
    master.fromTo('#s3-bottom-bar',
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out' },
      14.8
    );

    // Scene 3 Outro
    master.fromTo('#scene-vector',
      { opacity: 1, y: 0 },
      { opacity: 0, y: -45, duration: 0.6, ease: 'power2.in' },
      16.8
    );

    // ==========================================
    // SCENE 4: SPECIMEN LAB (17.0s - 23.0s)
    // ==========================================
    master.fromTo('#scene-specimen', { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power2.out' }, 17.0);

    master.fromTo('#s4-tag', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }, 17.1);
    master.fromTo('#s4-headline', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }, 17.3);
    master.fromTo('#s4-subline', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' }, 17.5);

    // Workbench entrance
    master.fromTo('#s4-workbench',
      { opacity: 0, scale: 0.94, y: 35 },
      { opacity: 1, scale: 1.0, y: 0, duration: 0.9, ease: 'power3.out' },
      17.6
    );

    // Optical waterfall cascade (English -> Bengali -> Hindi)
    master.fromTo('#s4-waterfall > div',
      { opacity: 0, x: -30 },
      { opacity: 1, x: 0, duration: 0.6, stagger: 0.12, ease: 'power2.out' },
      18.0
    );

    // Inspector focus pulse
    master.fromTo('#s4-inspector-target',
      { opacity: 0, scale: 0.95 },
      { opacity: 1, scale: 1.0, duration: 0.7, ease: 'power3.out' },
      18.6
    );

    // Scene 4 Outro
    master.fromTo('#scene-specimen',
      { opacity: 1 },
      { opacity: 0, duration: 0.5, ease: 'power2.in' },
      22.2
    );

    // ==========================================
    // SCENE 5: OWNERSHIP & RESOLUTION (22.5s - 28.0s)
    // ==========================================
    master.fromTo('#scene-outro', { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power2.out' }, 22.5);

    master.fromTo('#s5-tag', { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }, 22.6);
    master.fromTo('#s5-headline', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.9, ease: 'power3.out' }, 22.8);

    // 3 Cards stagger
    master.fromTo('.s5-card',
      { opacity: 0, y: 45, scale: 0.92 },
      { opacity: 1, y: 0, scale: 1.0, duration: 0.8, stagger: 0.15, ease: 'back.out(1.3)' },
      23.3
    );

    // Grand Brand Lockup Climax
    master.fromTo('#s5-brand-climax',
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 0.9, ease: 'power2.out' },
      24.6
    );

    window.__timelines = window.__timelines || {};
    window.__timelines['root'] = master;
    window.__masterTimeline = master;

    master.seek(0);
    console.log('HyperFrames: Master timeline registered successfully (Duration:', master.totalDuration(), 'seconds)');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTimeline);
  } else {
    initTimeline();
  }
})();
