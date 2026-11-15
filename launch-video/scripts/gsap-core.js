/**
 * HyperFrames-compatible Deterministic Motion & GSAP Timeline Core
 * Guarantees 100% reproducible frame-by-frame seeking (seek(t)) across any browser or headless renderer.
 */
(function(window) {
  'use strict';

  // Easing curve functions
  const Easings = {
    'none': t => t,
    'linear': t => t,
    'power1.out': t => 1 - Math.pow(1 - t, 2),
    'power1.inOut': t => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
    'power2.out': t => 1 - Math.pow(1 - t, 3),
    'power2.in': t => Math.pow(t, 3),
    'power2.inOut': t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
    'power3.out': t => 1 - Math.pow(1 - t, 4),
    'power3.in': t => Math.pow(t, 4),
    'power3.inOut': t => t < 0.5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2,
    'expo.out': t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
    'back.out': (s = 1.70158) => t => 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2)
  };

  function parseEase(ease) {
    if (!ease) return Easings['power2.out'];
    if (typeof ease === 'function') return ease;
    if (typeof ease === 'string') {
      if (ease.startsWith('back.out')) {
        const match = ease.match(/back\.out\(([^)]+)\)/);
        const s = match ? parseFloat(match[1]) : 1.70158;
        return Easings['back.out'](s);
      }
      return Easings[ease] || Easings['power2.out'];
    }
    return Easings['power2.out'];
  }

  function resolveTargets(target) {
    if (!target) return [];
    if (typeof target === 'string') {
      return Array.from(document.querySelectorAll(target));
    }
    if (target instanceof Element) return [target];
    if (Array.isArray(target) || target instanceof NodeList) {
      const arr = [];
      Array.from(target).forEach(t => {
        if (typeof t === 'string') arr.push(...document.querySelectorAll(t));
        else if (t instanceof Element) arr.push(t);
      });
      return arr;
    }
    return [];
  }

  class Tween {
    constructor(element, fromVars, toVars, startTime, duration, ease) {
      this.element = element;
      this.fromVars = Object.assign({}, fromVars);
      this.toVars = Object.assign({}, toVars);
      this.startTime = startTime;
      this.duration = Math.max(0.0001, duration);
      this.endTime = startTime + this.duration;
      this.easeFn = parseEase(ease || toVars.ease || fromVars.ease);
    }

    render(time) {
      const el = this.element;
      if (!el) return;

      // Calculate progress clamp [0, 1]
      let progress = 0;
      if (time <= this.startTime) {
        progress = 0;
      } else if (time >= this.endTime) {
        progress = 1;
      } else {
        progress = (time - this.startTime) / this.duration;
      }

      const eased = this.easeFn(progress);

      // Interpolate properties
      const currentProps = {};
      const keys = new Set([...Object.keys(this.fromVars), ...Object.keys(this.toVars)]);

      // Filter out meta keys
      keys.delete('ease');
      keys.delete('duration');
      keys.delete('stagger');

      keys.forEach(key => {
        const startVal = this.fromVars[key] !== undefined ? this.fromVars[key] : this.toVars[key];
        const endVal = this.toVars[key] !== undefined ? this.toVars[key] : this.fromVars[key];

        if (typeof startVal === 'number' && typeof endVal === 'number') {
          currentProps[key] = startVal + (endVal - startVal) * eased;
        } else if (key === 'filter' || key === 'opacity') {
          if (key === 'opacity') {
            const s = parseFloat(startVal) || 0;
            const e = parseFloat(endVal) !== undefined ? parseFloat(endVal) : 1;
            currentProps[key] = s + (e - s) * eased;
          } else if (key === 'filter') {
            // Support blur(Xpx)
            const sBlur = parseFloat((String(startVal).match(/blur\((\d+(\.\d+)?)px\)/) || [0, 0])[1]) || 0;
            const eBlur = parseFloat((String(endVal).match(/blur\((\d+(\.\d+)?)px\)/) || [0, 0])[1]) || 0;
            const curBlur = sBlur + (eBlur - sBlur) * eased;
            currentProps[key] = `blur(${curBlur.toFixed(2)}px)`;
          }
        }
      });

      // Apply to element style using GPU compositor properties
      if (currentProps.opacity !== undefined) {
        el.style.opacity = currentProps.opacity;
      }
      if (currentProps.filter !== undefined) {
        el.style.filter = currentProps.filter;
      }

      // Build 3D Transform matrix
      const transforms = [];
      const x = currentProps.x !== undefined ? currentProps.x : 0;
      const y = currentProps.y !== undefined ? currentProps.y : 0;
      const z = currentProps.z !== undefined ? currentProps.z : 0;
      if (x !== 0 || y !== 0 || z !== 0) {
        transforms.push(`translate3d(${x.toFixed(2)}px, ${y.toFixed(2)}px, ${z.toFixed(2)}px)`);
      }

      const scale = currentProps.scale !== undefined ? currentProps.scale : 1;
      const scaleX = currentProps.scaleX !== undefined ? currentProps.scaleX : scale;
      const scaleY = currentProps.scaleY !== undefined ? currentProps.scaleY : scale;
      if (scaleX !== 1 || scaleY !== 1) {
        transforms.push(`scale3d(${scaleX.toFixed(4)}, ${scaleY.toFixed(4)}, 1)`);
      }

      const rotate = currentProps.rotate !== undefined ? currentProps.rotate : (currentProps.rotation || 0);
      if (rotate !== 0) {
        transforms.push(`rotate(${rotate.toFixed(2)}deg)`);
      }

      const rotateX = currentProps.rotateX !== undefined ? currentProps.rotateX : 0;
      if (rotateX !== 0) {
        transforms.push(`rotateX(${rotateX.toFixed(2)}deg)`);
      }

      const rotateY = currentProps.rotateY !== undefined ? currentProps.rotateY : 0;
      if (rotateY !== 0) {
        transforms.push(`rotateY(${rotateY.toFixed(2)}deg)`);
      }

      if (transforms.length > 0) {
        el.style.transform = transforms.join(' ');
      } else if (keys.has('x') || keys.has('y') || keys.has('scale') || keys.has('rotate')) {
        el.style.transform = 'translate3d(0, 0, 0) scale3d(1, 1, 1)';
      }
    }
  }

  class Timeline {
    constructor(config = {}) {
      this.paused = config.paused !== false;
      this.defaults = config.defaults || {};
      this.tweens = [];
      this.cursor = 0;
      this.duration = 0;
      this._time = 0;
    }

    _resolvePosition(pos) {
      if (pos === undefined || pos === null) return this.cursor;
      if (typeof pos === 'number') return pos;
      if (typeof pos === 'string') {
        if (pos.startsWith('+=')) return this.cursor + parseFloat(pos.slice(2));
        if (pos.startsWith('-=')) return Math.max(0, this.cursor - parseFloat(pos.slice(2)));
        if (pos === '<') return this.tweens.length > 0 ? this.tweens[this.tweens.length - 1].startTime : 0;
        if (pos === '>') return this.duration;
      }
      return parseFloat(pos) || this.cursor;
    }

    fromTo(targets, fromVars, toVars, position) {
      const elements = resolveTargets(targets);
      const startTime = this._resolvePosition(position);
      const dur = toVars.duration !== undefined ? toVars.duration : (fromVars.duration !== undefined ? fromVars.duration : (this.defaults.duration || 1));
      const stagger = toVars.stagger || fromVars.stagger || 0;
      const ease = toVars.ease || fromVars.ease || this.defaults.ease;

      elements.forEach((el, idx) => {
        const itemStart = startTime + (idx * stagger);
        const tween = new Tween(el, fromVars, toVars, itemStart, dur, ease);
        this.tweens.push(tween);
        const itemEnd = itemStart + dur;
        if (itemEnd > this.duration) this.duration = itemEnd;
      });

      this.cursor = Math.max(this.cursor, startTime + dur + (elements.length > 1 ? (elements.length - 1) * stagger : 0));
      return this;
    }

    to(targets, toVars, position) {
      return this.fromTo(targets, {}, toVars, position);
    }

    set(targets, vars, position) {
      return this.fromTo(targets, vars, vars, position);
    }

    seek(time) {
      this._time = Math.max(0, Math.min(time, this.duration || 1000));
      for (let i = 0; i < this.tweens.length; i++) {
        this.tweens[i].render(this._time);
      }
      return this;
    }

    time(t) {
      if (t === undefined) return this._time;
      return this.seek(t);
    }

    progress(val) {
      if (val === undefined) return this.duration ? this._time / this.duration : 0;
      return this.seek(val * this.duration);
    }

    totalDuration() {
      return this.duration;
    }
  }

  const gsap = {
    timeline: (config) => new Timeline(config),
    to: (targets, vars) => {
      const tl = new Timeline({ paused: true });
      tl.to(targets, vars, 0);
      tl.seek(vars.duration || 1);
      return tl;
    },
    fromTo: (targets, fromVars, toVars) => {
      const tl = new Timeline({ paused: true });
      tl.fromTo(targets, fromVars, toVars, 0);
      tl.seek(0);
      return tl;
    },
    set: (targets, vars) => {
      const tl = new Timeline({ paused: true });
      tl.set(targets, vars, 0);
      tl.seek(0);
      return tl;
    }
  };

  window.gsap = gsap;
  window.__timelines = window.__timelines || {};
})(window);
