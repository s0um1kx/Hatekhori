// Hatekhori Launch Film (16:9 Widescreen Editorial Atelier)
// 120 BPM · 48 Beats · 24.0 Seconds · Pure seek(t) pipeline

film({
  W: 1920,
  H: 1080,
  FPS: 60,
  BPM: 120,
  BEATS: 48,
  holds: []
});

const POINTER_TRACK = [
  { t: 0.0,  x: 1300, y: 750 },
  { t: 1.5,  x: 960,  y: 680, d: 0.6 },
  // Scene 2 (Studio build): Cursor navigates the canvas
  { t: 3.8,  x: 1100, y: 460, d: 0.7 },
  { t: 5.2,  x: 1350, y: 380, d: 0.6, click: 5.2 },
  { t: 6.2,  x: 820,  y: 520, d: 0.5 },
  // Scene 4 (Desktop window): Cursor selects tabs
  { t: 10.8, x: 740,  y: 190, d: 0.6, click: 10.8 },
  { t: 12.2, x: 1150, y: 580, d: 0.8 },
  // Scene 5 (Hover menu): Cursor hovers over Bengali
  { t: 14.5, x: 480,  y: 490, d: 0.6 },
  { t: 16.0, x: 480,  y: 570, d: 0.5 }, // Hover Bengali
  // Scene 6 (Checkout modal): Cursor clicks [INSTALL & OWN FONT]
  { t: 18.5, x: 960,  y: 730, d: 0.7 },
  { t: 19.8, x: 960,  y: 730, click: 19.8 }, // CLICK!
  { t: 21.5, x: 1100, y: 540, d: 0.8 },
  { t: 23.5, x: 1300, y: 750, d: 0.7 },
  { t: 24.0, x: 1300, y: 750 }
];

function build(stage) {
  stage.innerHTML = `
    <!-- SCENE 1: THE TEASE CARD (0.0s – 3.2s) -->
    <div class="scene center" data-k="scene1">
      <div class="col center" style="position: relative;">
        <!-- Floating Product Card -->
        <div style="width: 480px; height: 600px; background: #FFFFFF; border-radius: 20px; box-shadow: var(--shadow-lg); border: 1px solid var(--border); overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; padding: 28px;">
          <div class="row" style="justify-content: space-between; align-items: center;">
            <span class="mono" style="font-size: 11px; padding: 4px 10px; border-radius: 999px; background: var(--terracotta-light); color: var(--terracotta); font-weight: 600;">
              ATELIER 01
            </span>
            <span class="mono" style="font-size: 12px; color: var(--ink-muted);">OPENTYPE ENGINE</span>
          </div>

          <!-- Product Image / Slate Artwork -->
          <div style="height: 300px; border-radius: 12px; overflow: hidden; background: #0D0D0D; position: relative; display: flex; align-items: center; justify-content: center;">
            <img src="${ASSETS.img.poster}" style="width: 100%; height: 100%; object-fit: cover; opacity: 0.85;" />
            <div class="abs col center" style="padding: 16px; text-align: center; background: rgba(0,0,0,0.4); border-radius: 8px;">
              <span class="bengali" style="font-size: 42px; color: #FFF;">হাতে খড়ি</span>
              <span class="mono" style="font-size: 11px; color: #DDD; margin-top: 4px;">CHALK TO OPENTYPE</span>
            </div>
          </div>

          <div class="col" style="gap: 6px;">
            <h2 style="font-size: 26px; font-weight: 700; color: var(--green); letter-spacing: -0.02em;">HATEKHORI</h2>
            <p style="font-size: 14px; color: var(--ink-muted); line-height: 1.4;">
              Turn your real handwriting into an ownable, installable font. Bengali, Hindi, and English.
            </p>
          </div>

          <div class="row" style="justify-content: space-between; align-items: center; border-top: 1px solid var(--border); padding-top: 14px;">
            <span class="mono" style="font-size: 12px; color: var(--ink);">BENGALI · HINDI · LATIN</span>
            <span class="mono" style="font-size: 13px; font-weight: 700; color: var(--green);">$0.00 / FREE</span>
          </div>
        </div>

        <!-- Floating Tag Below Card (Reference Style) -->
        <div style="margin-top: 24px; padding: 8px 18px; border-radius: 8px; background: rgba(255,255,255,0.8); border: 1px solid var(--border); box-shadow: var(--shadow-sm); display: flex; align-items: center; gap: 8px;">
          <span class="mono" style="font-size: 12px; font-weight: 600; text-transform: uppercase;">Real Handwriting Font</span>
          <span style="color: var(--ink-muted);">—</span>
          <span style="font-size: 12px; color: var(--ink-muted);">In our own hand. It's real, ownable.</span>
        </div>
      </div>
    </div>

    <!-- SCENE 2: SPLIT-SCREEN AI STUDIO BUILD (3.0s – 7.2s) -->
    <div class="scene" data-k="scene2" style="display: flex;">
      <!-- Left Column: AI Studio Feed (560px) -->
      <div class="col" style="width: 560px; height: 1080px; background: #FAF7F2; border-right: 1px solid var(--border); padding: 40px; justify-content: space-between;">
        <div class="col" style="gap: 20px;">
          <!-- User Pill -->
          <div class="row" style="gap: 12px;">
            <div style="width: 32px; height: 32px; border-radius: 8px; background: var(--green); display: flex; align-items: center; justify-content: center; color: #FFF; font-weight: bold; font-size: 14px;">H</div>
            <div class="col">
              <strong style="font-size: 14px;">Hatekhori Studio</strong>
              <span class="mono" style="font-size: 11px; color: var(--ink-muted);">atelier@hatekhori.org</span>
            </div>
          </div>

          <p style="font-size: 14px; color: var(--ink-secondary); line-height: 1.5;">
            • Bengali (60 cells), Hindi (60 cells), English (90 cells).<br>
            • Perspective homography, Bézier vectorization, OpenType compilation.
          </p>

          <span class="mono" style="font-size: 11px; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.08em;">
            Compiling font assets in parallel:
          </span>

          <!-- Feed Badge Stream (Reference Style) -->
          <div class="col" style="gap: 8px;">
            <div class="chat-pill" data-k="pill1"><span class="mono" style="color:var(--green)">✓ Ingest</span> <span>guideline-sheet-bengali.png</span></div>
            <div class="chat-pill" data-k="pill2"><span class="mono" style="color:var(--green)">✓ Homography</span> <span>4 corner alignment markers locked</span></div>
            <div class="chat-pill" data-k="pill3"><span class="mono" style="color:var(--green)">✓ Privacy</span> <span>EXIF scrubbed (Zero AI training)</span></div>
            <div class="chat-pill" data-k="pill4"><span class="mono" style="color:var(--green)">✓ Vectorize</span> <span>60 ink contour paths extracted</span></div>
            <div class="chat-pill" data-k="pill5"><span class="mono" style="color:var(--green)">✓ OpenType</span> <span>hatekhori-bengali.otf compiled</span></div>
            <div class="chat-pill" data-k="pill6"><span class="mono" style="color:var(--terracotta)">● Specimen</span> <span>Generating interactive live tester</span></div>
          </div>
        </div>

        <!-- Bottom Prompt Bar -->
        <div style="padding: 16px 20px; border-radius: 12px; background: #FFFFFF; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; box-shadow: var(--shadow-sm);">
          <span style="font-size: 14px; color: var(--ink-muted);">What script would you like to compile?</span>
          <div style="width: 32px; height: 32px; border-radius: 8px; background: #191816; display: flex; align-items: center; justify-content: center; color: #FFF;">↑</div>
        </div>
      </div>

      <!-- Right Canvas: Assembling Site (1360px) -->
      <div class="col" style="flex: 1; height: 1080px; background: #F5EFEB; padding: 48px; position: relative; overflow: hidden;">
        <!-- Top Nav -->
        <div class="row" style="justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 24px;">
          <div class="row" style="gap: 12px;">
            <svg width="24" height="24" viewBox="0 0 256 256" fill="currentColor"><path d="M44 36H96V108H160V36H192L212 56V220H160V148L128 180L96 148V220H44Z"/></svg>
            <strong style="font-size: 18px; letter-spacing: 0.05em;">HATEKHORI</strong>
          </div>
          <div class="row mono" style="gap: 28px; font-size: 13px; color: var(--ink-secondary);">
            <span>ATELIER</span><span>SPECIMEN</span><span>GUIDELINES</span><span>DOWNLOAD</span>
          </div>
        </div>

        <!-- Giant Bold Typography & Floating Elements -->
        <div class="col center" style="flex: 1; position: relative;">
          <!-- Giant Display Title -->
          <h1 style="font-size: 130px; font-weight: 800; color: var(--green); line-height: 0.95; letter-spacing: -0.04em; text-align: center; z-index: 2;">
            REAL HANDWRITING
          </h1>
          <span class="bengali" style="font-size: 48px; color: var(--ink-muted); margin-top: 14px; z-index: 2;">
            হাতে খড়ি — আপনার আসল হাতের লেখা
          </span>

          <!-- Floating Graphic Polaroid Tiles -->
          <div class="abs" data-k="tile1" style="left: 60px; top: 120px; width: 180px; height: 180px; border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-md); border: 4px solid #FFF; transform: rotate(-6deg);">
            <img src="${ASSETS.img.sheetBn}" style="width: 100%; height: 100%; object-fit: cover;" />
          </div>

          <div class="abs" data-k="tile2" style="right: 80px; top: 80px; width: 200px; height: 150px; border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-md); border: 4px solid #FFF; transform: rotate(5deg);">
            <img src="${ASSETS.img.poster}" style="width: 100%; height: 100%; object-fit: cover;" />
          </div>

          <div class="abs" data-k="tile3" style="left: 120px; bottom: 80px; width: 190px; height: 140px; border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-md); border: 4px solid #FFF; transform: rotate(4deg);">
            <img src="${ASSETS.img.sheetEn}" style="width: 100%; height: 100%; object-fit: cover;" />
          </div>

          <div class="abs" data-k="tile4" style="right: 120px; bottom: 90px; width: 220px; height: 160px; border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-md); border: 4px solid #FFF; transform: rotate(-4deg); background: #FFF; padding: 12px; display: flex; flex-direction: column; justify-content: space-between;">
            <span class="mono" style="font-size: 11px; color: var(--terracotta);">COMPILED OPENTYPE</span>
            <span class="bengali" style="font-size: 38px; color: var(--ink); text-align: center;">অ আ ক খ</span>
            <span class="mono" style="font-size: 11px; color: var(--ink-muted);">hatekhori-bengali.otf</span>
          </div>
        </div>
      </div>
    </div>

    <!-- SCENE 3: 3×3 NOTIFICATION CASCADE GRID (7.0s – 10.2s) -->
    <div class="scene" data-k="scene3" style="padding: 32px; display: grid; grid-template-columns: repeat(3, 1fr); grid-template-rows: repeat(3, 1fr); gap: 24px; background: #0E0D0C;">
      ${[
        { tag: "Font Compiled", title: "Rahul's Bengali Hand (.otf) ready", time: "now", img: ASSETS.img.poster },
        { tag: "Specimen Tested", title: "'আমার সোনার বাংলা' typed in live tester", time: "now", img: ASSETS.img.sheetBn },
        { tag: "Hindi Devanagari", title: "60 glyphs compiled & verified", time: "now", img: ASSETS.img.sheetHi },
        { tag: "Zero AI Training", title: "100% private, client-side ephemeral ingest", time: "now", img: ASSETS.img.poster },
        { tag: "A4 Guideline Sheet", title: "Standard paper with 4 corner marks", time: "now", img: ASSETS.img.sheetEn },
        { tag: "Kerning Pairs", title: "142 optical layout rules auto-generated", time: "now", img: ASSETS.img.sheetBn },
        { tag: "English Latin", title: "A to Z, numbers & symbols ready", time: "now", img: ASSETS.img.sheetEn },
        { tag: "Instant Install", title: "Compatible with macOS, iOS, Windows, Android", time: "now", img: ASSETS.img.poster },
        { tag: "100% Ownable", title: "Free and open source. Zero rental.", time: "now", img: ASSETS.img.sheetHi },
      ].map((item, idx) => `
        <div class="rel center" style="border-radius: 16px; overflow: hidden; background: #1A1918;">
          <img src="${item.img}" style="width: 100%; height: 100%; object-fit: cover; opacity: 0.65;" />
          <!-- Toast Over Background -->
          <div class="toast-card abs" data-k="toast${idx}" style="width: 88%; transform: translateY(40px); opacity: 0;">
            <div style="width: 38px; height: 38px; border-radius: 10px; background: var(--terracotta-light); display: flex; align-items: center; justify-content: center;">
              <svg width="20" height="20" viewBox="0 0 256 256" fill="var(--terracotta)"><path d="M44 36H96V108H160V36H192L212 56V220H160V148L128 180L96 148V220H44Z"/></svg>
            </div>
            <div class="col" style="flex: 1; gap: 2px;">
              <div class="row" style="justify-content: space-between;">
                <span class="mono" style="font-size: 11px; font-weight: 700; color: var(--terracotta); text-transform: uppercase;">${item.tag}</span>
                <span class="mono" style="font-size: 10px; color: var(--ink-muted);">${item.time}</span>
              </div>
              <strong style="font-size: 13px; color: var(--ink);">${item.title}</strong>
            </div>
          </div>
        </div>
      `).join("")}
    </div>

    <!-- SCENE 4: DESKTOP ATELIER WINDOW (10.0s – 14.2s) -->
    <div class="scene center" data-k="scene4">
      <div class="desktop-browser" style="width: 1640px; height: 920px;">
        <!-- Browser Bar (Reference Style) -->
        <div class="browser-bar">
          <div class="row" style="gap: 8px;">
            <div style="width: 11px; height: 11px; border-radius: 50%; background: #FF5F57;"></div>
            <div style="width: 11px; height: 11px; border-radius: 50%; background: #FEBC2E;"></div>
            <div style="width: 11px; height: 11px; border-radius: 50%; background: #28C840;"></div>
            <span class="mono" style="margin-left: 12px; font-size: 13px; font-weight: 600; color: var(--ink);">Hatekhori Atelier</span>
            <span class="mono" style="font-size: 12px; color: var(--ink-muted);">Handwriting Engine</span>
          </div>

          <div class="row mono" style="gap: 16px; font-size: 12px;">
            <span style="padding: 4px 10px; border-radius: 4px; background: #ECEAE5; font-weight: 600;">The Atelier</span>
            <span style="color: var(--ink-muted);">Specimen</span>
            <span style="color: var(--ink-muted);">Guidelines</span>
            <span style="color: var(--ink-muted);">Glyph Roster</span>
          </div>

          <div class="row" style="gap: 10px;">
            <span class="mono" style="font-size: 12px; padding: 5px 12px; border-radius: 6px; background: var(--green-light); color: var(--green); font-weight: 600;">
              Active: hatekhori-bengali.otf
            </span>
            <span class="mono" style="font-size: 12px; padding: 5px 14px; border-radius: 6px; background: #191816; color: #FFF; font-weight: 600;">
              Export Font
            </span>
          </div>
        </div>

        <!-- Window Inner Canvas -->
        <div class="col" style="flex: 1; padding: 48px; justify-content: space-between; background: #FFFFFF;">
          <!-- Giant Display Title -->
          <div class="row" style="justify-content: space-between; align-items: baseline; border-bottom: 2px solid var(--ink); padding-bottom: 20px;">
            <h1 style="font-size: 110px; font-weight: 800; color: var(--green); line-height: 0.9; letter-spacing: -0.04em;">
              THE ATELIER
            </h1>
            <span class="mono" style="font-size: 16px; font-weight: 600; color: var(--ink-muted);">
              AUTHENTIC INDIC TYPOGRAPHY
            </span>
          </div>

          <!-- Collage & Typography Showcase -->
          <div class="row" style="flex: 1; gap: 40px; align-items: center; margin: 32px 0;">
            <!-- Left: Slate Photo -->
            <div style="width: 440px; height: 440px; border-radius: 16px; overflow: hidden; box-shadow: var(--shadow-md);">
              <img src="${ASSETS.img.poster}" style="width: 100%; height: 100%; object-fit: cover;" />
            </div>

            <!-- Right: Dynamic Typography Waterfall -->
            <div class="col" style="flex: 1; gap: 24px;">
              <div class="col" style="gap: 6px;">
                <span class="mono" style="font-size: 12px; color: var(--terracotta); text-transform: uppercase;">48px Display</span>
                <p class="bengali" style="font-size: 48px; color: var(--ink); line-height: 1.2;">
                  আমার বাংলা ভাষা ও নিজের হাতের লেখা
                </p>
              </div>

              <div class="col" style="gap: 6px;">
                <span class="mono" style="font-size: 12px; color: var(--terracotta); text-transform: uppercase;">32px Subhead</span>
                <p class="bengali" style="font-size: 32px; color: var(--ink-secondary); line-height: 1.3;">
                  হাতে খড়ি দিয়ে তৈরি আপনার নিজস্ব বাংলা ফন্ট
                </p>
              </div>

              <div class="col" style="gap: 6px;">
                <span class="mono" style="font-size: 12px; color: var(--terracotta); text-transform: uppercase;">20px Continuous Prose</span>
                <p class="bengali" style="font-size: 20px; color: var(--ink-muted); line-height: 1.5; max-width: 900px;">
                  কাগজে কলমে লেখা প্রতিটি হরফের নিজস্ব একটি টান থাকে। সেই স্বাভাবিক রেখাগুলোকে অক্ষুণ্ণ রেখে সরাসরি ডিজিটাল ফন্টে রূপান্তর করে হাতে খড়ি।
                </p>
              </div>
            </div>
          </div>

          <div class="row" style="justify-content: space-between; border-top: 1px solid var(--border); padding-top: 18px;">
            <span class="mono" style="font-size: 13px; color: var(--ink-muted);">First-class support for Bengali (60), Hindi (60), and English (90).</span>
            <span class="mono" style="font-size: 13px; color: var(--green); font-weight: 600;">✓ 100% Vector Precision</span>
          </div>
        </div>
      </div>
    </div>

    <!-- SCENE 5: INTERACTIVE HOVER MENU (14.0s – 18.2s) -->
    <div class="scene" data-k="scene5" style="display: flex;">
      <!-- Left: Giant Typography Menu (Reference Frame 11 Style) -->
      <div class="col" style="width: 860px; height: 1080px; padding: 80px 100px; justify-content: center; background: #F5EFEB;">
        <span class="mono" style="font-size: 14px; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 24px;">
          SCRIPT WORKBENCH
        </span>

        <div class="col" style="gap: 28px;">
          <div class="serif" style="font-size: 56px; color: var(--ink-muted);">All Scripts</div>
          <div class="serif" data-k="menuBn" style="font-size: 64px; font-weight: 700; color: var(--green); display: flex; align-items: baseline; gap: 16px;">
            <span>Bengali (বাংলা)</span>
            <span class="mono" style="font-size: 18px; padding: 4px 12px; border-radius: 999px; background: var(--green-light); color: var(--green);">60 Glyphs</span>
          </div>
          <div class="serif" style="font-size: 56px; color: var(--ink-muted);">Hindi (हिन्दी)</div>
          <div class="serif" style="font-size: 56px; color: var(--ink-muted);">English (Latin)</div>
        </div>
      </div>

      <!-- Right: Split Photo Canvas -->
      <div style="flex: 1; height: 1080px; position: relative;">
        <img src="${ASSETS.img.poster}" style="width: 100%; height: 100%; object-fit: cover;" />
        
        <!-- Floating Interactive Preview Card (Tracks Cursor) -->
        <div data-k="hoverCard" class="abs col" style="left: 100px; top: 400px; width: 340px; background: #FFFFFF; border-radius: 18px; box-shadow: var(--shadow-lg); border: 1px solid var(--border); padding: 24px; gap: 16px;">
          <div class="row" style="justify-content: space-between; align-items: center;">
            <span class="mono" style="font-size: 11px; color: var(--terracotta); font-weight: 600;">ACTIVE GLYPH</span>
            <span class="mono" style="font-size: 12px; color: var(--ink-muted);">U+0985</span>
          </div>

          <div style="height: 160px; border-radius: 10px; background: #FAF7F2; display: flex; align-items: center; justify-content: center;">
            <span class="bengali" style="font-size: 110px; color: var(--ink);">অ</span>
          </div>

          <div class="col" style="gap: 4px;">
            <strong style="font-size: 16px;">Bengali Letter 'A' (অ)</strong>
            <span style="font-size: 13px; color: var(--ink-muted);">Digitized from hand stroke into Bézier OpenType.</span>
          </div>

          <div class="row" style="justify-content: space-between; align-items: center; border-top: 1px solid var(--border); padding-top: 12px;">
            <span class="mono" style="font-size: 14px; font-weight: 700; color: var(--green);">$0.00</span>
            <span style="font-size: 16px; color: var(--ink-muted);">→</span>
          </div>
        </div>
      </div>
    </div>

    <!-- SCENE 6: THE CHECKOUT / FONT RECEIPT MODAL (18.0s – 21.2s) -->
    <div class="scene center" data-k="scene6" style="background: #EBE4DC;">
      <!-- Slate pattern background -->
      <div class="abs full" style="background-image: radial-gradient(var(--ink-muted) 1.5px, transparent 1.5px); background-size: 40px 40px; opacity: 0.15;"></div>

      <!-- Centered Order Summary Card (Exact Reference Frame 14 Layout) -->
      <div style="width: 520px; background: #FFFFFF; border-radius: 20px; box-shadow: var(--shadow-lg); border: 1px solid var(--border); padding: 36px; display: flex; flex-direction: column; gap: 24px; position: relative; z-index: 2;">
        <div class="col" style="gap: 4px;">
          <h2 style="font-size: 32px; font-weight: 800; color: var(--green); letter-spacing: -0.02em;">
            CHECKOUT
          </h2>
          <span class="mono" style="font-size: 11px; color: var(--terracotta); text-transform: uppercase; font-weight: 600; letter-spacing: 0.08em;">
            ORDER SUMMARY
          </span>
        </div>

        <!-- Line items -->
        <div class="col" style="gap: 16px; border-bottom: 1px solid var(--border); padding-bottom: 20px;">
          <div class="row" style="justify-content: space-between; align-items: center;">
            <div class="row" style="gap: 12px;">
              <div style="width: 44px; height: 44px; border-radius: 8px; background: #F5EFEB; display: flex; align-items: center; justify-content: center; font-family: 'HatekhoriBangla', serif; font-size: 22px;">
                অ
              </div>
              <div class="col">
                <strong style="font-size: 14px;">Hatekhori Bengali (.otf)</strong>
                <span class="mono" style="font-size: 11px; color: var(--ink-muted);">60 Hand-Drawn Glyphs</span>
              </div>
            </div>
            <span class="mono" style="font-size: 14px; font-weight: 600;">$0.00</span>
          </div>

          <div class="row" style="justify-content: space-between; align-items: center;">
            <div class="row" style="gap: 12px;">
              <div style="width: 44px; height: 44px; border-radius: 8px; background: #F5EFEB; display: flex; align-items: center; justify-content: center; font-family: 'HatekhoriHindi', serif; font-size: 22px;">
                अ
              </div>
              <div class="col">
                <strong style="font-size: 14px;">Hatekhori Hindi (.otf)</strong>
                <span class="mono" style="font-size: 11px; color: var(--ink-muted);">60 Hand-Drawn Glyphs</span>
              </div>
            </div>
            <span class="mono" style="font-size: 14px; font-weight: 600;">$0.00</span>
          </div>
        </div>

        <!-- Totals calculation -->
        <div class="col" style="gap: 8px; font-size: 13px; color: var(--ink-secondary);">
          <div class="row" style="justify-content: space-between;">
            <span>Subtotal</span>
            <span class="mono">$0.00</span>
          </div>
          <div class="row" style="justify-content: space-between;">
            <span>AI License Training Fee</span>
            <span class="mono" style="color: var(--green); font-weight: 600;">$0.00 (Zero AI Training)</span>
          </div>
          <div class="row" style="justify-content: space-between; font-size: 18px; font-weight: 700; color: var(--ink); border-top: 1px solid var(--border); padding-top: 12px; margin-top: 4px;">
            <span>Total</span>
            <span class="mono" style="color: var(--green);">$0.00 / FREE</span>
          </div>
        </div>

        <!-- Big CTA Button -->
        <div data-k="btnPay" style="padding: 16px; border-radius: 10px; background: var(--green); color: #FFFFFF; font-weight: 700; font-size: 16px; text-align: center; letter-spacing: 0.04em; cursor: pointer; box-shadow: 0 4px 16px rgba(27,67,50,0.25);">
          INSTALL &amp; OWN FONT
        </div>
      </div>
    </div>

    <!-- SCENE 7: PRESERVATION CALENDAR & CLOSING LOCKUP (21.0s – 24.0s) -->
    <div class="scene center" data-k="scene7" style="background: #0E0D0C; color: #FFF;">
      <img src="${ASSETS.img.poster}" style="width: 100%; height: 100%; object-fit: cover; opacity: 0.45; position: absolute;" />

      <div class="col center" style="position: relative; z-index: 2; gap: 32px; text-align: center;">
        <span class="mono" style="font-size: 14px; letter-spacing: 0.2em; color: var(--gold); text-transform: uppercase;">
          PRESERVED FOREVER
        </span>

        <!-- Giant Calendar Slider Row (Reference Frame 15 Style) -->
        <div class="row" style="gap: 48px; align-items: center;">
          <div class="col center" style="opacity: 0.4;">
            <span class="serif" style="font-size: 20px;">Wed</span>
            <strong style="font-size: 72px; font-weight: 800;">12</strong>
          </div>
          <div class="col center" style="opacity: 0.6;">
            <span class="serif" style="font-size: 20px;">Thu</span>
            <strong style="font-size: 72px; font-weight: 800;">13</strong>
          </div>
          <div class="col center" style="opacity: 0.8;">
            <span class="serif" style="font-size: 20px;">Fri</span>
            <strong style="font-size: 72px; font-weight: 800;">14</strong>
          </div>

          <!-- Highlighted / Circled Day -->
          <div class="col center" style="padding: 14px 28px; border: 2.5px solid var(--gold); border-radius: 999px; background: rgba(0,0,0,0.4); box-shadow: 0 0 30px rgba(212,163,115,0.3);">
            <span class="serif" style="font-size: 24px; color: var(--gold);">Today</span>
            <strong style="font-size: 88px; font-weight: 800; color: #FFF; line-height: 1;">15</strong>
          </div>

          <div class="col center" style="opacity: 0.8;">
            <span class="serif" style="font-size: 20px;">Sun</span>
            <strong style="font-size: 72px; font-weight: 800;">16</strong>
          </div>
        </div>

        <div class="col center" style="gap: 8px; margin-top: 20px;">
          <div class="row" style="gap: 14px;">
            <svg width="32" height="32" viewBox="0 0 256 256" fill="currentColor"><path d="M44 36H96V108H160V36H192L212 56V220H160V148L128 180L96 148V220H44Z"/></svg>
            <h2 style="font-size: 32px; font-weight: 700; letter-spacing: 0.04em;">HATEKHORI • হাতে খড়ি</h2>
          </div>
          <p class="mono" style="font-size: 14px; color: #BBB;">
            Your handwriting. Ownable forever. Free and open source.
          </p>
        </div>
      </div>
    </div>

    <!-- Universal Custom Cursor -->
    ${pointerMarkup()}
  `;

  collect(stage);
}

function apply(t) {
  // 1. Scene transitions with smooth blur and fade
  applyScene($.scene1, sceneFade(t, 0.0,  3.2));
  applyScene($.scene2, sceneFade(t, 3.0,  7.2));
  applyScene($.scene3, sceneFade(t, 7.0, 10.2));
  applyScene($.scene4, sceneFade(t, 10.0, 14.2));
  applyScene($.scene5, sceneFade(t, 14.0, 18.2));
  applyScene($.scene6, sceneFade(t, 18.0, 21.2));
  applyScene($.scene7, sceneFade(t, 21.0, 24.0));

  // 2. Cursor motion
  const pt = getPointer(t, POINTER_TRACK);
  setT($.pointer, `translate(${pt.x.toFixed(2)}px, ${pt.y.toFixed(2)}px) scale(${pt.press.toFixed(3)})`);

  // Scene 2: Staggered pill stream
  if (t >= 3.0 && t <= 7.2) {
    const pills = [$.pill1, $.pill2, $.pill3, $.pill4, $.pill5, $.pill6];
    pills.forEach((p, idx) => {
      const pProg = prog(t, 3.2 + idx * 0.45, 0.35, E.out);
      p.style.opacity = pProg.toFixed(2);
      p.style.transform = `translateX(${((1 - pProg) * 20).toFixed(1)}px)`;
    });

    // Floating polaroids gentle inertia
    const f1 = spring(t, 3.4, 0.5, 0.85);
    const f2 = spring(t, 3.6, 0.5, 0.85);
    const f3 = spring(t, 3.8, 0.5, 0.85);
    const f4 = spring(t, 4.0, 0.5, 0.85);
    setT($.tile1, `rotate(-6deg) scale(${f1.toFixed(3)})`);
    setT($.tile2, `rotate(5deg) scale(${f2.toFixed(3)})`);
    setT($.tile3, `rotate(4deg) scale(${f3.toFixed(3)})`);
    setT($.tile4, `rotate(-4deg) scale(${f4.toFixed(3)})`);
  }

  // Scene 3: Staggered toast grid spring pop
  if (t >= 7.0 && t <= 10.2) {
    for (let i = 0; i < 9; i++) {
      const toast = $[`toast${i}`];
      if (toast) {
        const p = prog(t, 7.1 + i * 0.08, 0.3, E.out);
        const sp = spring(t, 7.1 + i * 0.08, 0.38, 0.82);
        toast.style.opacity = p.toFixed(2);
        toast.style.transform = `translateY(${((1 - sp) * 40).toFixed(1)}px)`;
      }
    }
  }

  // Scene 5: Floating card tracks cursor
  if (t >= 14.0 && t <= 18.2) {
    const cardX = lerp(480, 520, prog(t, 14.5, 1.5, E.smooth));
    const cardY = lerp(460, 420, prog(t, 15.0, 1.5, E.smooth));
    setT($.hoverCard, `translate(${cardX.toFixed(1)}px, ${cardY.toFixed(1)}px)`);
  }

  // Scene 6: Checkout button press reaction
  if (t >= 19.8 && t < 20.3) {
    const pr = press(t, 19.8, 0.92);
    setT($.btnPay, `scale(${pr.toFixed(3)})`);
  }
}

function cues() {
  return [
    ["whoosh", 0.1,  { gain: -4 }],
    ["click",  1.5,  { gain: -2 }],
    ["whoosh", 3.0,  { gain: -3 }],
    ["pop",    3.4,  { gain: -2 }],
    ["pop",    3.8,  { gain: -2 }],
    ["click",  5.2,  { gain: -2 }],
    ["whoosh", 7.0,  { gain: -3 }],
    ["chime",  7.2,  { gain: -1, note: 0 }],
    ["pop",    7.3,  { gain: -3 }],
    ["pop",    7.5,  { gain: -3 }],
    ["pop",    7.7,  { gain: -3 }],
    ["whoosh", 10.0, { gain: -3 }],
    ["click",  10.8, { gain: -2 }],
    ["whoosh", 14.0, { gain: -3 }],
    ["tick",   16.0, { gain: -2 }],
    ["whoosh", 18.0, { gain: -3 }],
    ["click",  19.8, { gain: 0 }], // PAY CLICK!
    ["chime",  20.0, { gain: 0, note: 4 }],
    ["whoosh", 21.0, { gain: -3 }],
    ["chime",  23.0, { gain: -2, note: 7 }]
  ];
}
