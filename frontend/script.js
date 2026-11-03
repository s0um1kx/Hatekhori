/* ==========================================================================
   Hatekhori — Modern Handwriting-to-Font Engine
   Language-aware guideline sheets & primary alphabet pipeline.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => document.querySelectorAll(s);

  // --- 1. Constants & Configurations ---
  const SCRIPTS = {
    bn: {
      font: "'Tiro Bangla', serif",
      text: 'নমস্কার, হাতে খড়ি দিয়ে নিজের হাতের লেখা ফন্ট বানান।',
      glyphs: 'অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎংঃঁ',
      sheetUrl: 'guideline-sheet-bengali.png',
      sheetFile: 'hatekhori-bengali-sheet.png',
      sheetName: 'Bengali Sheet (বাংলা)',
      sheetTitle: 'Get Bengali Guideline Sheet',
      sheetSubtitle: 'বাংলা বর্ণমালা ও কারচিহ্ন (A4 grid with 4 registration fiducials)',
      sheetBadge: '10×6 Grid • 60 Cells',
      sheetMeta: ['60 Bengali Cells', '11 স্বর • 39 ব্যঞ্জন • 10 কার', 'A4 (100% scale)'],
      matrixTitle: 'Extracted Character Set (60 Glyphs)',
      modalTitle: 'Bengali Guideline Sheet (বাংলা)',
      modalDesc: 'A4 grid • 60 cells (11 স্বরবর্ণ, 39 ব্যঞ্জনবর্ণ, 10 কারচিহ্ন) with 4 registration fiducials.'
    },
    en: {
      font: "'Kalam', cursive",
      text: 'Write it once. Use it everywhere. 12345',
      glyphs: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?&-@#',
      sheetUrl: 'guideline-sheet-english.png',
      sheetFile: 'hatekhori-english-sheet.png',
      sheetName: 'English Sheet (Latin)',
      sheetTitle: 'Get English Guideline Sheet',
      sheetSubtitle: 'A–Z, a–z, 0–9 & symbols (A4 grid with 4 registration fiducials)',
      sheetBadge: '10×9 Grid • 90 Cells',
      sheetMeta: ['90 Latin Cells', 'A–Z, a–z, 0–9, Punctuation', 'A4 (100% scale)'],
      matrixTitle: 'Extracted Character Set (90 Glyphs)',
      modalTitle: 'English Guideline Sheet (Latin)',
      modalDesc: 'A4 grid • 90 cells (A–Z, a–z, 0–9, punctuation) with 4 registration fiducials.'
    },
    hi: {
      font: "'Kalam', cursive",
      text: 'नमस्ते, अपने हाथ की लिखाई को डिजिटल फॉन्ट में बदलें।',
      glyphs: 'अआइईउऊऋएऐओऔकखगঘङचছजঝञटठडঢणतथदধনपফबভমयरलवशषसह१२३४५६७८९०',
      sheetUrl: 'guideline-sheet-bengali.png',
      sheetFile: 'hatekhori-bengali-sheet.png',
      sheetName: 'Guideline Sheet',
      sheetTitle: 'Get Guideline Sheet',
      sheetSubtitle: 'Printable A4 grid with 4 registration fiducials',
      sheetMeta: ['Indic Grid', 'A4 (100% scale)', '4 Corner Fiducials'],
      matrixTitle: 'Extracted Character Set'
    }
  };

  // 60 Bengali Primary Characters: 11 স্বরবর্ণ, 39 ব্যঞ্জনবর্ণ, 10 কারচিহ্ন
  const BENGALI_STUDIO_GLYPHS = [
    'অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'এ', 'ঐ', 'ও', 'ঔ',
    'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ',
    'ট', 'ঠ', 'ড', 'ঢ', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন',
    'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ',
    'স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ',
    'া', 'ি', 'ী', 'ু', 'ূ', 'ৃ', 'ে', 'ৈ', 'ো', 'ৌ'
  ];

  const LATIN_STUDIO_GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?\'"()-:;@#$%&*+=/'.split('');

  // --- 2. State ---
  let currentScript = 'bn';
  let activeUploadId = null;
  let activeSelectedFile = null;
  let currentLoadedFontFamily = null;
  let isSimulating = false;
  let toastTimer = null;

  // --- 3. DOM Elements ---
  // Views & Global Navigation
  const landingView = $('#landing-view');
  const studioView = $('#studio-view');
  const navLaunchStudio = $('#nav-launch-studio');
  const heroEnterStudio = $('#hero-enter-studio');
  const ctaEnterStudio = $('#cta-enter-studio');
  const studioBackBtn = $('#studio-back-btn');
  const toastEl = $('#toast');
  const privacyModal = $('#privacy-modal');
  const navPrivacyBtn = $('#nav-privacy-btn');
  const footerPrivacyBtn = $('#footer-privacy-btn');
  const closePrivacyBtn = $('#close-privacy-btn');
  const btnModalUnderstand = $('#btn-modal-understand');

  // Specimen Section
  const heroLiveText = $('#hero-live-text');
  const heroSizeSlider = $('#hero-size-slider');
  const heroSizeReadout = $('#hero-size-readout');
  const scriptTabButtons = $$('.script-tabs .tab-btn');
  const cellsContainer = $('#cells');
  const bigGlyph = $('#big');
  const cpReadout = $('#cp');

  // Studio Ingest & Dropzone
  const dropzone = $('#dropzone');
  const dropzoneIdle = $('#dropzone-idle');
  const dropzonePreview = $('#dropzone-preview');
  const fileInput = $('#file-input');
  const previewImg = $('#preview');
  const btnRemovePhoto = $('#btn-remove-photo');
  const btnChangePhoto = $('#btn-change-photo');
  const fileMetaName = $('#file-meta-name');
  const fileMetaSize = $('#file-meta-size');

  // Stepper Pills & Actions
  const spillSheet = $('#spill-sheet');
  const spillUpload = $('#spill-upload');
  const spillCompile = $('#spill-compile');
  const spillExport = $('#spill-export');
  const legalCheckbox = $('#legal-consent');
  const btnCompile = $('#btn-compile');
  const compileConsentWarning = $('#compile-consent-warning');

  // Studio Progress & Results
  const stepProgress = $('#step-progress');
  const progressText = $('#progress-text');
  const psteps = [
    $('#pstep-1'),
    $('#pstep-2'),
    $('#pstep-3'),
    $('#pstep-4'),
    $('#pstep-5'),
    $('#pstep-6')
  ];
  const studioEmptyState = $('#studio-empty-state');
  const stepResult = $('#step-result');
  const downloadFontLink = $('#download-font');
  const previewText = $('#preview-text');
  const previewSize = $('#preview-size');
  const studioSizeVal = $('#studio-size-val');
  const previewNote = $('#preview-note');
  const studioLoadDemoBtn = $('#studio-load-demo-btn');
  const btnCopyCss = $('#btn-copy-css');
  const btnToggleMatrix = $('#btn-toggle-matrix');
  const glyphMatrixDrawer = $('#glyph-matrix-drawer');
  const glyphGrid = $('#glyph-grid');

  // Card 1 Showcase & Modal Elements
  const sheetScriptPills = $$('.sheet-script-picker .sheet-script-pill');
  const sheetPreviewShowcase = $('#sheet-preview-showcase');
  const studioSheetImg = $('#studio-sheet-img');
  const studioSheetBadge = $('#studio-sheet-badge');
  const sheetLightboxModal = $('#sheet-lightbox-modal');
  const sheetModalBackdrop = $('#sheet-modal-backdrop');
  const btnCloseSheetModal = $('#btn-close-sheet-modal');
  const modalSheetTitle = $('#modal-sheet-title');
  const modalSheetDesc = $('#modal-sheet-desc');
  const modalSheetImg = $('#modal-sheet-img');
  const modalDownloadSheet = $('#modal-download-sheet');

  // --- 4. Helper Functions ---
  function showToast(message) {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.classList.add('visible');
    
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toastEl.classList.remove('visible');
    }, 2800);
  }
  window.showToast = showToast;

  function inspectGlyph(ch) {
    if (bigGlyph) {
      bigGlyph.textContent = ch;
      bigGlyph.style.fontFamily = SCRIPTS[currentScript].font;
    }
    if (cpReadout) {
      const codePoint = ch.codePointAt(0);
      cpReadout.textContent = codePoint 
        ? 'U+' + codePoint.toString(16).toUpperCase().padStart(4, '0') 
        : 'U+????';
    }
    if (cellsContainer) {
      cellsContainer.querySelectorAll('button').forEach((btn) => {
        btn.setAttribute('aria-pressed', btn.textContent === ch ? 'true' : 'false');
      });
    }
  }

  function populateCharacterMatrix(scriptKey) {
    if (!cellsContainer) return;
    cellsContainer.innerHTML = '';
    const script = SCRIPTS[scriptKey] || SCRIPTS.bn;
    const glyphs = Array.from(script.glyphs);

    glyphs.forEach((ch) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = ch;
      btn.style.fontFamily = script.font;
      btn.addEventListener('click', () => {
        inspectGlyph(ch);
        if (heroLiveText) {
          heroLiveText.value += ch;
          heroLiveText.focus();
        }
      });
      cellsContainer.appendChild(btn);
    });

    if (glyphs.length > 0) {
      inspectGlyph(glyphs[0]);
    }
  }

  function renderStudioGlyphMatrix() {
    if (!glyphGrid) return;
    glyphGrid.innerHTML = '';
    const chars = currentScript === 'en' ? LATIN_STUDIO_GLYPHS : BENGALI_STUDIO_GLYPHS;
    const fontFallback = currentScript === 'en' ? 'Kalam, cursive' : "'Tiro Bangla', serif";

    for (const ch of chars) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'glyph-cell';
      b.textContent = ch;
      b.title = ch;
      b.style.fontFamily = currentLoadedFontFamily ? `"${currentLoadedFontFamily}", ${fontFallback}` : fontFallback;
      b.addEventListener('click', () => {
        if (previewText) {
          previewText.value += ch;
          previewText.focus();
        }
      });
      glyphGrid.appendChild(b);
    }
  }

  function setScript(key) {
    if (!SCRIPTS[key]) return;
    currentScript = key;
    const s = SCRIPTS[key];

    scriptTabButtons.forEach((b) => {
      const active = b.dataset.k === key;
      b.classList.toggle('active', active);
      b.setAttribute('aria-selected', active ? 'true' : 'false');
    });

    // Sync Card 1 language selector pills
    sheetScriptPills.forEach((pill) => {
      const active = pill.dataset.script === key;
      pill.classList.toggle('active', active);
      pill.setAttribute('aria-selected', active ? 'true' : 'false');
    });

    if (heroLiveText) {
      heroLiveText.value = s.text;
      heroLiveText.style.fontFamily = s.font;
    }

    // Dynamic Sheet Links & Meta Sync across navigation, studio, CTA, and lightbox modal
    const sheetLinks = [
      $('#studio-download-sheet'),
      $('#nav-download-sheet'),
      $('#hero-download-sheet'),
      $('#cta-download-sheet'),
      modalDownloadSheet
    ];
    sheetLinks.forEach((link) => {
      if (!link) return;
      link.href = s.sheetUrl;
      link.setAttribute('download', s.sheetFile);
    });

    // Update Studio Card 1 visual preview showcase
    if (studioSheetImg && s.sheetUrl) {
      studioSheetImg.src = s.sheetUrl;
      studioSheetImg.alt = `${s.sheetName} Preview`;
    }
    if (studioSheetBadge && s.sheetBadge) {
      studioSheetBadge.textContent = s.sheetBadge;
    }

    // Update Lightbox Modal content
    if (modalSheetImg && s.sheetUrl) modalSheetImg.src = s.sheetUrl;
    if (modalSheetTitle && s.modalTitle) modalSheetTitle.textContent = s.modalTitle;
    if (modalSheetDesc && s.modalDesc) modalSheetDesc.textContent = s.modalDesc;
    if (modalDownloadSheet && s.sheetUrl) {
      modalDownloadSheet.href = s.sheetUrl;
      modalDownloadSheet.setAttribute('download', s.sheetFile);
      modalDownloadSheet.textContent = `Download ${s.sheetName} (A4)`;
    }

    const studioSheetTitle = $('#studio-sheet-title');
    if (studioSheetTitle && s.sheetTitle) studioSheetTitle.textContent = s.sheetTitle;
    const studioSheetSub = $('#studio-sheet-sub');
    if (studioSheetSub && s.sheetSubtitle) studioSheetSub.textContent = s.sheetSubtitle;
    const studioSheetBtnLabel = $('#studio-sheet-btn-label');
    if (studioSheetBtnLabel && s.sheetName) studioSheetBtnLabel.textContent = `Download ${s.sheetName}`;
    const studioSheetMeta = $('#studio-sheet-meta');
    if (studioSheetMeta && s.sheetMeta) {
      studioSheetMeta.innerHTML = s.sheetMeta.map((m) => `<span class="sheet-meta-tag">${m}</span>`).join('');
    }
    const matrixDrawerTitle = $('#matrix-drawer-title');
    if (matrixDrawerTitle && s.matrixTitle) matrixDrawerTitle.textContent = s.matrixTitle;

    populateCharacterMatrix(key);
    renderStudioGlyphMatrix();
  }

  function switchView(viewName, pushHistory = true) {
    if (viewName === 'studio') {
      if (landingView) {
        landingView.classList.remove('active-view');
        landingView.hidden = true;
      }
      if (studioView) {
        studioView.classList.add('active-view');
        studioView.hidden = false;
      }
      if (navLaunchStudio) {
        navLaunchStudio.innerHTML = `<span>Atelier Studio</span>`;
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
      if (pushHistory && window.location.hash !== '#studio') {
        history.pushState({ view: 'studio' }, '', '#studio');
      }
    } else {
      if (studioView) {
        studioView.classList.remove('active-view');
        studioView.hidden = true;
      }
      if (landingView) {
        landingView.classList.add('active-view');
        landingView.hidden = false;
      }
      if (navLaunchStudio) {
        navLaunchStudio.innerHTML = `
          <span>Launch Studio</span>
          <svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        `;
      }
      if (pushHistory && window.location.hash) {
        history.pushState({ view: 'landing' }, '', window.location.pathname + window.location.search);
      }
    }
  }

  function updateStepperPill(activePill) {
    [spillSheet, spillUpload, spillCompile, spillExport].forEach((pill) => {
      if (pill) pill.classList.remove('active');
    });
    if (activePill) activePill.classList.add('active');
  }

  function updateCompileButtonState() {
    if (!btnCompile) return;
    const hasPhoto = Boolean(activeSelectedFile || (fileInput && fileInput.files && fileInput.files.length > 0));
    const hasConsent = legalCheckbox ? legalCheckbox.checked : true;
    btnCompile.disabled = !hasPhoto || !hasConsent;

    if (compileConsentWarning) {
      compileConsentWarning.hidden = hasConsent;
    }
  }

  function handleFileSelected(file) {
    if (!file) return;
    if (!file.type.match(/^image\/(jpeg|png|heic)$/i) && !file.name.match(/\.(jpg|jpeg|png|heic)$/i)) {
      alert("Invalid format: Please upload a JPG, PNG, or HEIC photo of the guideline sheet.");
      return;
    }

    activeSelectedFile = file;
    if (previewImg.src && previewImg.src.startsWith('blob:')) {
      URL.revokeObjectURL(previewImg.src);
    }
    const url = URL.createObjectURL(file);
    previewImg.src = url;
    fileMetaName.textContent = file.name;
    fileMetaSize.textContent = `${(file.size / (1024 * 1024)).toFixed(1)} MB`;

    dropzoneIdle.hidden = true;
    dropzonePreview.hidden = false;
    updateStepperPill(spillCompile);
    updateCompileButtonState();
  }

  function clearSelectedPhoto() {
    activeSelectedFile = null;
    if (fileInput) fileInput.value = '';
    if (previewImg.src && previewImg.src.startsWith('blob:')) {
      URL.revokeObjectURL(previewImg.src);
    }
    previewImg.src = '';
    dropzonePreview.hidden = true;
    dropzoneIdle.hidden = false;
    updateStepperPill(spillUpload);
    updateCompileButtonState();
  }

  function simulateProgress(pstepsList, onStepChange) {
    let current = 0;
    const steps = [
      { text: "Binarizing and removing table shadows...", duration: 600 },
      { text: "Detecting 4 corner fiducial markers...", duration: 800 },
      { text: "Correcting perspective keystone...", duration: 700 },
      { text: "Slicing guideline matrix cells...", duration: 900 },
      { text: "Tracing Bézier contours...", duration: 1100 },
      { text: "Compiling OpenType (.otf) font tables...", duration: 800 }
    ];

    function runStep() {
      if (!isSimulating || current >= steps.length) return;
      onStepChange(current, steps[current].text);
      pstepsList.forEach((el, idx) => {
        if (!el) return;
        el.classList.toggle('active', idx === current);
        el.classList.toggle('done', idx < current);
      });
      setTimeout(() => {
        current++;
        runStep();
      }, steps[current].duration);
    }
    runStep();
  }

  async function loadStudioFont(id) {
    if (previewNote) previewNote.hidden = true;
    try {
      const family = `Hatekhori-${id}`;
      const face = new FontFace(family, `url(/download-font/${id}?inline=true)`);
      await face.load();
      document.fonts.add(face);
      currentLoadedFontFamily = family;
      const fallbackFont = currentScript === 'en' ? 'Kalam, cursive' : "'Tiro Bangla', serif";
      if (previewText) previewText.style.fontFamily = `"${family}", ${fallbackFont}`;
      applyStudioSize();
    } catch (err) {
      if (previewNote) {
        previewNote.textContent = 'Webfont preview could not load inline, but your font files are ready to download below.';
        previewNote.hidden = false;
      }
    }
  }

  function applyStudioSize() {
    if (previewText && previewSize) {
      previewText.style.fontSize = `${previewSize.value}px`;
      if (studioSizeVal) studioSizeVal.textContent = `${previewSize.value}px`;
    }
  }

  // --- 5. Wire Event Handlers ---
  // Script selection tabs (Specimen)
  scriptTabButtons.forEach((btn) => {
    btn.addEventListener('click', () => setScript(btn.dataset.k));
  });

  // Card 1 Language sheet selection pills
  sheetScriptPills.forEach((pill) => {
    pill.addEventListener('click', () => setScript(pill.dataset.script));
  });

  // Guideline Sheet Lightbox Modal Controls
  function openSheetModal() {
    if (!sheetLightboxModal) return;
    if (typeof sheetLightboxModal.showModal === 'function') {
      sheetLightboxModal.showModal();
    } else {
      sheetLightboxModal.setAttribute('open', '');
    }
  }

  function closeSheetModal() {
    if (!sheetLightboxModal) return;
    if (typeof sheetLightboxModal.close === 'function') {
      sheetLightboxModal.close();
    } else {
      sheetLightboxModal.removeAttribute('open');
    }
  }

  if (sheetPreviewShowcase) {
    sheetPreviewShowcase.addEventListener('click', openSheetModal);
    sheetPreviewShowcase.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openSheetModal();
      }
    });
  }

  if (btnCloseSheetModal) btnCloseSheetModal.addEventListener('click', closeSheetModal);
  if (sheetModalBackdrop) sheetModalBackdrop.addEventListener('click', closeSheetModal);

  // Privacy Policy Modal Controls
  function openPrivacyModal() {
    if (!privacyModal) return;
    privacyModal.hidden = false;
    privacyModal.classList.add('visible');
    privacyModal.setAttribute('aria-hidden', 'false');
  }

  function closePrivacyModal() {
    if (!privacyModal) return;
    privacyModal.classList.remove('visible');
    privacyModal.hidden = true;
    privacyModal.setAttribute('aria-hidden', 'true');
  }

  if (navPrivacyBtn) navPrivacyBtn.addEventListener('click', openPrivacyModal);
  if (footerPrivacyBtn) footerPrivacyBtn.addEventListener('click', openPrivacyModal);
  if (closePrivacyBtn) closePrivacyBtn.addEventListener('click', closePrivacyModal);
  if (btnModalUnderstand) btnModalUnderstand.addEventListener('click', closePrivacyModal);
  if (privacyModal) {
    privacyModal.addEventListener('click', (e) => {
      if (e.target === privacyModal) closePrivacyModal();
    });
  }

  // Specimen font slider
  if (heroSizeSlider && heroLiveText && heroSizeReadout) {
    heroSizeSlider.addEventListener('input', (e) => {
      const val = e.target.value;
      heroLiveText.style.fontSize = `${val}px`;
      heroSizeReadout.textContent = `${val}px`;
    });
  }

  // View navigation
  if (navLaunchStudio) navLaunchStudio.addEventListener('click', () => switchView('studio'));
  if (heroEnterStudio) heroEnterStudio.addEventListener('click', () => switchView('studio'));
  if (ctaEnterStudio) ctaEnterStudio.addEventListener('click', () => switchView('studio'));
  if (studioBackBtn) studioBackBtn.addEventListener('click', () => switchView('landing'));

  window.addEventListener('popstate', () => {
    switchView(window.location.hash === '#studio' ? 'studio' : 'landing', false);
  });

  document.addEventListener('keydown', (e) => {
    if (!e || !e.target) return;
    if (['INPUT', 'TEXTAREA'].includes(e.target.tagName) || e.target.isContentEditable) return;
    if (e.key === 's' || e.key === 'S') {
      switchView('studio');
    } else if (e.key === 'Escape') {
      switchView('landing');
    }
  });

  // File Dropzone Handlers
  if (dropzone && fileInput) {
    dropzone.addEventListener('click', (e) => {
      if (e.target === btnRemovePhoto) return;
      fileInput.click();
    });

    ['dragenter', 'dragover'].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        handleFileSelected(files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelected(e.target.files[0]);
      }
    });
  }

  if (btnRemovePhoto) {
    btnRemovePhoto.addEventListener('click', (e) => {
      e.stopPropagation();
      clearSelectedPhoto();
    });
  }

  if (btnChangePhoto && fileInput) {
    btnChangePhoto.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.click();
    });
  }

  if (legalCheckbox) {
    legalCheckbox.addEventListener('change', updateCompileButtonState);
  }

  // Font Compilation Handler
  if (btnCompile) {
    btnCompile.addEventListener('click', async () => {
      const fileToUpload = activeSelectedFile || (fileInput ? fileInput.files[0] : null);
      if (!fileToUpload) {
        alert("Please upload a photo of your guideline sheet first.");
        return;
      }
      if (legalCheckbox && !legalCheckbox.checked) {
        alert("Please confirm the legal consent warranty before continuing.");
        return;
      }

      btnCompile.disabled = true;
      if (stepProgress) stepProgress.hidden = false;
      if (studioEmptyState) studioEmptyState.hidden = true;
      if (stepResult) stepResult.hidden = true;
      updateStepperPill(spillCompile);

      isSimulating = true;
      simulateProgress(psteps, (stepIdx, txt) => {
        if (progressText) progressText.textContent = txt;
      });

      try {
        const formData = new FormData();
        formData.append('file', fileToUpload);

        const ingestRes = await fetch('/ingest', {
          method: 'POST',
          body: formData
        });

        if (!ingestRes.ok) {
          const errData = await ingestRes.json().catch(() => ({}));
          throw new Error(errData.detail || `Upload failed with HTTP ${ingestRes.status}`);
        }

        const { id } = await ingestRes.json();
        activeUploadId = id;

        const genRes = await fetch(`/generate/${id}?script=${currentScript}`, {
          method: 'POST'
        });

        if (!genRes.ok) {
          const errData = await genRes.json().catch(() => ({}));
          throw new Error(errData.detail || `Vector tracing & compilation failed.`);
        }

        const genData = await genRes.json();
        isSimulating = false;

        psteps.forEach((el) => {
          if (el) {
            el.classList.remove('active');
            el.classList.add('done');
          }
        });

        if (stepProgress) stepProgress.hidden = true;
        if (stepResult) stepResult.hidden = false;
        updateStepperPill(spillExport);

        if (downloadFontLink) downloadFontLink.href = `/download-font/${id}`;

        if (previewText) {
          if (currentScript === 'en') {
            previewText.value = 'The quick brown fox jumps over the lazy dog. 12345';
          } else {
            previewText.value = 'নমস্কার, হাতে খড়ি দিয়ে নিজের হাতের লেখা ফন্ট বানান।';
          }
        }

        if (genData.warnings && genData.warnings.length > 0) {
          if (previewNote) {
            previewNote.textContent = genData.warnings.join(' ');
            previewNote.hidden = false;
          }
          showToast(`Note: ${genData.warnings[0]}`);
        } else if (genData.skipped_blank && genData.skipped_blank.length > 0) {
          if (previewNote) {
            previewNote.textContent = `${genData.skipped_blank.length} empty cells were omitted from the font.`;
            previewNote.hidden = false;
          }
        }

        await loadStudioFont(id);
        renderStudioGlyphMatrix();
      } catch (err) {
        isSimulating = false;
        if (stepProgress) stepProgress.hidden = true;
        if (studioEmptyState) studioEmptyState.hidden = false;
        updateStepperPill(spillUpload);
        alert(`Notice:\n\n${err.message || 'Processing failed.'}`);
      } finally {
        updateCompileButtonState();
      }
    });
  }

  // Specimen preview font size
  if (previewSize) previewSize.addEventListener('input', applyStudioSize);

  // CSS snippet copy button
  if (btnCopyCss) {
    btnCopyCss.addEventListener('click', () => {
      const family = currentLoadedFontFamily || 'Hatekhori-Personal';
      const url = activeUploadId ? `/download-font/${activeUploadId}` : 'hatekhori-font.otf';
      const fallback = currentScript === 'en' ? 'Kalam, cursive' : "'Tiro Bangla', serif";
      const snippet = `@font-face {\n  font-family: "${family}";\n  src: url("${url}") format("opentype");\n}\n\nbody {\n  font-family: "${family}", ${fallback};\n}`;

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(snippet).then(() => {
          showToast('@font-face CSS snippet copied!');
        }).catch(() => {
          showToast('Snippet ready in console.');
          console.log(snippet);
        });
      } else {
        showToast('Snippet ready in console.');
        console.log(snippet);
      }
    });
  }

  // Drawer toggle for matrix
  if (btnToggleMatrix && glyphMatrixDrawer) {
    btnToggleMatrix.addEventListener('click', () => {
      glyphMatrixDrawer.hidden = !glyphMatrixDrawer.hidden;
      if (!glyphMatrixDrawer.hidden && glyphGrid && glyphGrid.children.length === 0) {
        renderStudioGlyphMatrix();
      }
    });
  }

  // Demo font loader
  if (studioLoadDemoBtn) {
    studioLoadDemoBtn.addEventListener('click', () => {
      if (studioEmptyState) studioEmptyState.hidden = true;
      if (stepResult) stepResult.hidden = false;
      updateStepperPill(spillExport);
      if (previewText) {
        if (currentScript === 'en') {
          previewText.style.fontFamily = "'Kalam', cursive";
          previewText.value = 'The quick brown fox jumps over the lazy dog. 12345';
          currentLoadedFontFamily = 'Kalam';
        } else {
          previewText.style.fontFamily = "'Tiro Bangla', serif";
          previewText.value = 'নমস্কার, হাতে খড়ি দিয়ে নিজের হাতের লেখা ফন্ট বানান।';
          currentLoadedFontFamily = 'Tiro Bangla';
        }
      }
      renderStudioGlyphMatrix();
      showToast('Demo handwriting font loaded in tester.');
    });
  }

  // --- 6. Initial Page Boot ---
  setScript('bn');
  updateCompileButtonState();
  if (window.location.hash === '#studio') {
    switchView('studio', false);
  }
});
