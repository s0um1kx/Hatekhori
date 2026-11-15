// Interaction and stage helpers for 16:9 Hatekhori launch film

const POINTER_ARROW = `<svg width="28" height="28" viewBox="0 0 28 28" fill="none">
  <path d="M4 3.5V23.5L9.2 18.7L12.6 26.5L16.2 25L12.8 17.2H19.8L4 3.5Z" fill="#191816" stroke="#FFFFFF" stroke-width="1.8" stroke-linejoin="round"/>
</svg>`;

function pointerMarkup() {
  return `<div class="pointer" data-k="pointer" style="left:0;top:0;width:28px;height:28px;">${POINTER_ARROW}</div>`;
}

function getPointer(t, keys) {
  if (!keys || keys.length === 0) return { x: 960, y: 540, press: 1 };
  const first = keys[0];
  let cur = { x: first.x, y: first.y, press: 1 };
  for (let i = 0; i < keys.length; i++) {
    const k = keys[i];
    if (t >= k.t) {
      if (i === keys.length - 1) {
        cur.x = k.x;
        cur.y = k.y;
      } else {
        const next = keys[i + 1];
        const dur = next.d || (next.t - k.t);
        const p = prog(t, next.t - dur, dur, E.smooth);
        cur.x = lerp(k.x, next.x, p);
        cur.y = lerp(k.y, next.y, p);
      }
      if (k.click) {
        cur.press = press(t, k.click, 0.88);
      }
    }
  }
  return cur;
}

function sceneFade(t, tIn, tOut, blurMax = 12) {
  if (t < tIn - 0.05 || t > tOut + 0.05) {
    return { visible: false, opacity: 0, blur: blurMax, scale: 0.98, y: 16 };
  }
  const inDur = 0.35;
  const outDur = 0.28;
  let opacity = 1;
  let blur = 0;
  let scale = 1;
  let y = 0;

  if (t < tIn + inDur) {
    const p = prog(t, tIn, inDur, E.out);
    const sp = spring(t, tIn, 0.42, 0.88);
    opacity = p;
    blur = (1 - p) * blurMax;
    scale = lerp(0.98, 1.0, sp);
    y = (1 - sp) * 16;
  } else if (t > tOut - outDur) {
    const p = prog(t, tOut - outDur, outDur, E.in);
    opacity = 1 - p;
    blur = p * blurMax;
    scale = lerp(1.0, 0.98, p);
    y = -p * 14;
  }

  return {
    visible: opacity > 0.005,
    opacity: clamp(opacity, 0, 1),
    blur: Math.max(0, blur),
    scale: clamp(scale, 0.92, 1.04),
    y,
  };
}

function applyScene(el, state) {
  if (!el) return;
  if (!state.visible) {
    el.style.visibility = "hidden";
    el.style.opacity = "0";
    return;
  }
  el.style.visibility = "";
  el.style.opacity = state.opacity.toFixed(3);
  el.style.filter = state.blur > 0.1 ? `blur(${state.blur.toFixed(1)}px)` : "";
  el.style.transform = `translateY(${state.y.toFixed(2)}px) scale(${state.scale.toFixed(4)})`;
}
