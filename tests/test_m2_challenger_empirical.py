"""
Milestone 2 Empirical Challenger Verification Suite
Author: m2_challenger_2 (teamwork_challenger: Critic & Specialist)
Focus:
  1. Indic Script Unicode Range Verification (Bengali U+0980-U+09FF, Devanagari U+0900-U+097F)
  2. Guideline PNG File Integrity & HTTP Download Verification
  3. CSS Touch Target Dimensions (>= 44px min-height) & Active Feedback
  4. Multi-Crawler Simulation (7 Bot User-Agents: Googlebot, Bingbot, Twitterbot, GPTBot, PerplexityBot, ClaudeBot, FacebookExternalHit)
  5. Anti-Cloaking and Robots.txt Directive Validation
"""

import os
import re
import sys
import json
import struct
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser

# Safe Unicode output for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

# Sandboxed test setup
test_tmp = tempfile.mkdtemp()
os.environ["HATEKHORI_DATA_DIR"] = test_tmp

if sys.platform == "win32":
    import asyncio.proactor_events
    import asyncio.windows_events

    class _DummySock:
        def setblocking(self, b): pass
        def fileno(self): return -1
        def close(self): pass
        def send(self, b): return len(b)
        def recv(self, n): return b""

    asyncio.proactor_events.BaseProactorEventLoop._make_self_pipe = (
        lambda self: setattr(self, "_ssock", _DummySock())
        or setattr(self, "_csock", _DummySock())
        or setattr(self, "_internal_fds", getattr(self, "_internal_fds", 0) + 1)
    )
    asyncio.windows_events.ProactorEventLoop._run_forever_setup = (
        lambda self: super(asyncio.windows_events.ProactorEventLoop, self)._run_forever_setup()
    )
    asyncio.windows_events.ProactorEventLoop._run_forever_cleanup = (
        lambda self: super(asyncio.windows_events.ProactorEventLoop, self)._run_forever_cleanup()
    )

import anyio.to_thread
async def _mock_run_sync(func, *args, **kwargs):
    kwargs.pop("abandon_on_cancel", None)
    kwargs.pop("cancellable", None)
    kwargs.pop("limiter", None)
    return func(*args, **kwargs)
anyio.to_thread.run_sync = _mock_run_sync

# Import FastAPI app from backend/app/main.py
sys.path.insert(0, BACKEND_DIR)
from app.main import app

class ASGIResponse:
    def __init__(self, status_code, headers, content):
        self.status_code = status_code
        self.headers = {k.decode("latin1").lower(): v.decode("latin1") for k, v in headers}
        self.content = content
        self.text = content.decode("utf-8", errors="replace")

def make_asgi_request(app, method="GET", path="/", headers=None):
    import asyncio
    headers_list = []
    if headers:
        for k, v in headers.items():
            headers_list.append((k.lower().encode("latin1"), v.encode("latin1")))
    else:
        headers_list.append((b"host", b"testserver"))

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": headers_list,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "scheme": "http",
        "http_version": "1.1",
    }

    status_code = 200
    res_headers = []
    body_chunks = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        nonlocal status_code, res_headers, body_chunks
        if message["type"] == "http.response.start":
            status_code = message["status"]
            res_headers = message["headers"]
        elif message["type"] == "http.response.body":
            body_chunks.append(message.get("body", b""))

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(app(scope, receive, send))
    finally:
        loop.close()

    return ASGIResponse(status_code, res_headers, b"".join(body_chunks))


class TestIndicScriptUnicode(unittest.TestCase):
    """Stress-test Indic script rendering and authenticity in HTML source."""

    def setUp(self):
        self.bn_html_path = os.path.join(FRONTEND_DIR, "bengali-font-maker.html")
        self.hi_html_path = os.path.join(FRONTEND_DIR, "hindi-font-generator.html")
        with open(self.bn_html_path, "r", encoding="utf-8") as f:
            self.bn_html = f.read()
        with open(self.hi_html_path, "r", encoding="utf-8") as f:
            self.hi_html = f.read()

    def test_bengali_unicode_character_count_and_authenticity(self):
        """Stress-test Bengali script (U+0980-U+09FF) glyph density and coverage."""
        bn_chars = [c for c in self.bn_html if "\u0980" <= c <= "\u09FF"]
        # Must have significant vernacular depth (> 100 Bengali characters)
        self.assertGreaterEqual(
            len(bn_chars), 100,
            f"Expected extensive Bengali character presence (>= 100), found {len(bn_chars)}"
        )

        # Check all 11 standard Bengali independent vowels (স্বরবর্ণ)
        vowels = ["অ", "আ", "ই", "ঈ", "উ", "ঊ", "ঋ", "এ", "ঐ", "ও", "ঔ"]
        for v in vowels:
            self.assertIn(v, self.bn_html, f"Bengali page missing vowel: {v} ({ord(v):04X})")

        # Check key consonants (ব্যঞ্জনবর্ণ)
        consonants = ["ক", "খ", "গ", "ঘ", "ঙ", "চ", "ছ", "জ", "ঝ", "ঞ",
                      "ট", "ঠ", "ড", "ঢ", "ণ", "ত", "থ", "দ", "ধ", "ন",
                      "প", "ফ", "ব", "ভ", "ম", "য", "র", "ল", "শ", "ষ",
                      "স", "হ", "ড়", "ঢ়", "য়", "ৎ"]
        for c in consonants:
            self.assertIn(c, self.bn_html, f"Bengali page missing consonant: {c} ({ord(c):04X})")

        # Check 10 dependent vowel signs / matras (কারচিহ্ন)
        matras = ["া", "ি", "ী", "ু", "ূ", "ৃ", "ে", "ৈ", "ো", "ৌ"]
        for m in matras:
            self.assertIn(m, self.bn_html, f"Bengali page missing matra: {m} ({ord(m):04X})")

        # Check additional diacritics
        signs = ["ঁ", "ং", "ঃ", "্"]
        for s in signs:
            self.assertIn(s, self.bn_html, f"Bengali page missing diacritic/sign: {s} ({ord(s):04X})")

        # Check complex conjunct ligatures (যুক্তবর্ণ)
        conjuncts = ["ক্ষ", "জ্ঞ", "ষ্ণ"]
        for cj in conjuncts:
            self.assertIn(cj, self.bn_html, f"Bengali page missing complex conjunct: {cj}")

        # Check for mojibake or corrupt character sequences
        mojibake_tokens = ["Ã", "â€", "\ufffd"]
        for token in mojibake_tokens:
            self.assertNotIn(token, self.bn_html, f"Bengali page contains suspected mojibake: {token}")

    def test_devanagari_unicode_character_count_and_authenticity(self):
        """Stress-test Devanagari script (U+0900-U+097F) glyph density and coverage."""
        hi_chars = [c for c in self.hi_html if "\u0900" <= c <= "\u097F"]
        # Must have significant vernacular depth (> 100 Devanagari characters)
        self.assertGreaterEqual(
            len(hi_chars), 100,
            f"Expected extensive Devanagari character presence (>= 100), found {len(hi_chars)}"
        )

        # Check standard Devanagari independent vowels (स्वर)
        vowels = ["अ", "आ", "इ", "ई", "उ", "ऊ", "ऋ", "ए", "ऐ", "ओ", "औ"]
        for v in vowels:
            self.assertIn(v, self.hi_html, f"Hindi page missing vowel: {v} ({ord(v):04X})")

        # Check key consonants (व्यंजन)
        consonants = ["क", "ख", "ग", "घ", "ङ", "च", "छ", "ज", "झ", "ञ",
                      "ट", "ठ", "ड", "ढ", "ण", "त", "थ", "द", "ध", "न",
                      "प", "फ", "ब", "भ", "म", "य", "र", "ल", "व", "श",
                      "ष", "स", "ह"]
        for c in consonants:
            self.assertIn(c, self.hi_html, f"Hindi page missing consonant: {c} ({ord(c):04X})")

        # Check Devanagari matras (मात्राएं)
        matras = ["ा", "ि", "ी", "ु", "ू", "ृ", "े", "ै", "ो", "ौ"]
        for m in matras:
            self.assertIn(m, self.hi_html, f"Hindi page missing matra: {m} ({ord(m):04X})")

        # Check signs & diacritics
        signs = ["ँ", "ं", "ः", "्", "़"]
        for s in signs:
            self.assertIn(s, self.hi_html, f"Hindi page missing diacritic/sign: {s} ({ord(s):04X})")

        # Check shirorekha (शिरोरेखा) typography explanation presence
        self.assertIn("shirorekha", self.hi_html.lower(), "Hindi page missing shirorekha technical discussion")
        self.assertIn("शिरोरेखा", self.hi_html, "Hindi page missing Devanagari spelling for शिरोरेखा")

        # Check for mojibake or corrupt character sequences
        mojibake_tokens = ["Ã", "â€", "\ufffd"]
        for token in mojibake_tokens:
            self.assertNotIn(token, self.hi_html, f"Hindi page contains suspected mojibake: {token}")


class TestGuidelinePNGAssets(unittest.TestCase):
    """Stress-test guideline PNG files on disk, binary headers, and HTTP download routes."""

    PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

    def test_guideline_png_files_binary_validation(self):
        """Verify guideline PNG files exist, have valid PNG signatures and valid IHDR chunks."""
        sheets = [
            "guideline-sheet-bengali.png",
            "guideline-sheet-hindi.png",
            "guideline-sheet-english.png"
        ]

        for sheet_name in sheets:
            file_path = os.path.join(FRONTEND_DIR, sheet_name)
            self.assertTrue(os.path.isfile(file_path), f"Guideline file missing on disk: {file_path}")

            size = os.path.getsize(file_path)
            self.assertGreater(size, 5000, f"Guideline file too small to be a real image ({size} bytes): {sheet_name}")

            with open(file_path, "rb") as f:
                sig = f.read(8)
                self.assertEqual(sig, self.PNG_SIGNATURE, f"Invalid PNG signature for {sheet_name}: {sig!r}")

                # Read IHDR chunk length (4 bytes) and chunk type (4 bytes)
                ihdr_len_bytes = f.read(4)
                ihdr_len = struct.unpack(">I", ihdr_len_bytes)[0]
                ihdr_type = f.read(4)
                self.assertEqual(ihdr_type, b"IHDR", f"First chunk is not IHDR in {sheet_name}")
                self.assertEqual(ihdr_len, 13, f"IHDR length is not 13 bytes in {sheet_name}: {ihdr_len}")

                # Read IHDR data: width (4), height (4), bit_depth (1), color_type (1), comp (1), filter (1), interlace (1)
                ihdr_data = f.read(13)
                width, height, bit_depth, color_type, comp, fltr, interlace = struct.unpack(">IIBBBBB", ihdr_data)

                self.assertGreater(width, 500, f"Width too small ({width}px) for {sheet_name}")
                self.assertGreater(height, 500, f"Height too small ({height}px) for {sheet_name}")
                self.assertIn(bit_depth, (1, 2, 4, 8, 16), f"Invalid bit depth {bit_depth} in {sheet_name}")
                self.assertIn(color_type, (0, 2, 3, 4, 6), f"Invalid color type {color_type} in {sheet_name}")

    def test_guideline_png_http_serving_and_byte_identity(self):
        """Verify FastAPI backend serves guideline PNGs with status 200, Content-Type, and identical bytes."""
        sheets = [
            "guideline-sheet-bengali.png",
            "guideline-sheet-hindi.png",
            "guideline-sheet-english.png"
        ]

        for sheet_name in sheets:
            file_path = os.path.join(FRONTEND_DIR, sheet_name)
            with open(file_path, "rb") as f:
                disk_bytes = f.read()

            res = make_asgi_request(app, method="GET", path=f"/{sheet_name}")
            self.assertEqual(res.status_code, 200, f"GET /{sheet_name} returned status {res.status_code}")
            content_type = res.headers.get("content-type", "")
            self.assertTrue(
                "image/png" in content_type,
                f"Expected image/png Content-Type for /{sheet_name}, got: {content_type}"
            )
            self.assertEqual(
                len(res.content), len(disk_bytes),
                f"Served byte length ({len(res.content)}) does not match disk size ({len(disk_bytes)}) for {sheet_name}"
            )
            self.assertEqual(res.content, disk_bytes, f"Served bytes differ from disk bytes for {sheet_name}")

    def test_guideline_download_links_in_html_pages(self):
        """Verify all HTML pages reference valid guideline PNG download links."""
        pages = [
            "bengali-font-maker.html",
            "hindi-font-generator.html",
            "compare/calligraphr-alternative.html",
            "index.html"
        ]

        for page in pages:
            page_path = os.path.join(FRONTEND_DIR, page)
            with open(page_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find all links referencing guideline sheets
            links = re.findall(r'href=["\']([^"\']*guideline-sheet[^"\']*)["\']', content)
            self.assertGreater(len(links), 0, f"Page {page} has no guideline sheet links")

            for link in links:
                # Strip leading slash if any
                clean_link = link.lstrip("/")
                disk_target = os.path.join(FRONTEND_DIR, clean_link)
                self.assertTrue(
                    os.path.isfile(disk_target),
                    f"Link '{link}' in {page} does not resolve to a file on disk at {disk_target}"
                )


class TestCSSTouchTargets(unittest.TestCase):
    """Stress-test 44px min-height touch targets, button sizing, active feedback, and spacing."""

    def test_global_button_touch_target_in_style_css(self):
        """Verify frontend/style.css enforces >= 44px height on buttons."""
        style_path = os.path.join(FRONTEND_DIR, "style.css")
        with open(style_path, "r", encoding="utf-8") as f:
            css = f.read()

        # Find .btn declaration
        btn_block_match = re.search(r'\.btn\s*\{([^}]+)\}', css)
        self.assertIsNotNone(btn_block_match, ".btn selector missing from frontend/style.css")
        btn_rules = btn_block_match.group(1)

        # Height or min-height must be >= 44px
        has_44px = "height: 44px" in btn_rules or "min-height: 44px" in btn_rules or "min-height:44px" in btn_rules
        self.assertTrue(has_44px, f".btn selector does not explicitly enforce 44px touch target: {btn_rules}")

        # Active state compression feedback
        active_match = re.search(r'\.btn:active\s*\{([^}]+)\}', css)
        self.assertIsNotNone(active_match, ".btn:active selector missing from frontend/style.css")
        self.assertIn("scale", active_match.group(1), ".btn:active should have tactile scale compression feedback")

    def test_landing_pages_nav_and_button_touch_targets(self):
        """Verify navigation links and buttons have >= 44px touch targets in all landing pages."""
        pages = [
            "bengali-font-maker.html",
            "hindi-font-generator.html",
            "compare/calligraphr-alternative.html",
            "index.html"
        ]

        for page in pages:
            page_path = os.path.join(FRONTEND_DIR, page)
            with open(page_path, "r", encoding="utf-8") as f:
                html = f.read()

            # Verify presence of min-height: 44px for navigation links or buttons
            self.assertIn(
                "min-height: 44px", html,
                f"Page {page} missing explicit min-height: 44px CSS rule"
            )

            # Check viewport meta tag for mobile scaling without zoom lock
            viewport_match = re.search(r'<meta[^>]+name=["\']viewport["\'][^>]*content=["\']([^"\']+)["\']', html)
            self.assertIsNotNone(viewport_match, f"Page {page} missing viewport meta tag")
            vp_content = viewport_match.group(1)
            self.assertIn("width=device-width", vp_content, f"Page {page} viewport missing width=device-width")
            self.assertIn("initial-scale=1", vp_content, f"Page {page} viewport missing initial-scale=1")
            self.assertNotIn("user-scalable=no", vp_content, f"Page {page} inappropriately disables user zoom")

            # Check reduced motion fallback
            self.assertIn(
                "prefers-reduced-motion", html,
                f"Page {page} missing prefers-reduced-motion media query"
            )


class TestMultiCrawlerSimulation(unittest.TestCase):
    """Simulate 7 bot user agents across clean routes, verify 200 OK, identical content (anti-cloaking), and robots.txt allow rules."""

    BOTS = {
        "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Bingbot": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
        "Twitterbot": "Twitterbot/1.0",
        "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
        "PerplexityBot": "PerplexityBot/1.0 (+https://perplexity.ai/perplexitybot)",
        "ClaudeBot": "ClaudeBot/1.0",
        "FacebookExternalHit": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    }

    DESKTOP_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    ROUTES = [
        "/",
        "/compare/calligraphr-alternative",
        "/bengali-font-maker",
        "/hindi-font-generator",
        "/robots.txt",
        "/sitemap.xml",
        "/llms.txt"
    ]

    def test_crawler_status_200_and_anti_cloaking(self):
        """Verify each bot receives HTTP 200 and identical content as standard desktop browser (no cloaking)."""
        for route in self.ROUTES:
            # Baseline request with standard browser UA
            res_browser = make_asgi_request(
                app, method="GET", path=route,
                headers={"Host": "testserver", "User-Agent": self.DESKTOP_UA}
            )
            self.assertEqual(res_browser.status_code, 200, f"Route {route} failed for desktop browser: {res_browser.status_code}")

            for bot_name, bot_ua in self.BOTS.items():
                res_bot = make_asgi_request(
                    app, method="GET", path=route,
                    headers={"Host": "testserver", "User-Agent": bot_ua}
                )

                self.assertEqual(
                    res_bot.status_code, 200,
                    f"Bot '{bot_name}' failed with status {res_bot.status_code} on {route}"
                )

                # Anti-cloaking: body length and content should match browser exactly
                self.assertEqual(
                    len(res_bot.content), len(res_browser.content),
                    f"Anti-cloaking alert on {route}: Bot '{bot_name}' received {len(res_bot.content)} bytes, "
                    f"but browser received {len(res_browser.content)} bytes!"
                )
                self.assertEqual(
                    res_bot.content, res_browser.content,
                    f"Anti-cloaking alert on {route}: Bot '{bot_name}' received different content than browser!"
                )

    def test_robots_txt_does_not_block_crawlers_from_clean_routes(self):
        """Verify robots.txt does not disallow any of the verified bot crawlers from public routes."""
        res = make_asgi_request(app, method="GET", path="/robots.txt")
        self.assertEqual(res.status_code, 200)
        robots_text = res.text

        # Verify User-agent: * block exists and allows root
        self.assertIn("User-agent: *", robots_text)
        self.assertIn("Allow: /", robots_text)

        # Disallow paths should only be internal directories, never our landing pages
        disallows = re.findall(r"^Disallow:\s*(\S+)", robots_text, re.MULTILINE)
        for d in disallows:
            for route in ["/compare/calligraphr-alternative", "/bengali-font-maker", "/hindi-font-generator"]:
                self.assertFalse(
                    route.startswith(d.rstrip("/")),
                    f"robots.txt Disallow rule '{d}' blocks public route '{route}'!"
                )


if __name__ == "__main__":
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(TestIndicScriptUnicode))
    suite.addTest(loader.loadTestsFromTestCase(TestGuidelinePNGAssets))
    suite.addTest(loader.loadTestsFromTestCase(TestCSSTouchTargets))
    suite.addTest(loader.loadTestsFromTestCase(TestMultiCrawlerSimulation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
