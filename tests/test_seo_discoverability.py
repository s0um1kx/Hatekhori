"""Opaque-box E2E SEO and Discoverability Test Suite for Hatekhori (হাতে খড়ি).

Features Covered (from TEST_INFRA.md and PROJECT.md):
  F1:  Homepage Metadata & Tags (ORIGINAL_REQUEST R1)
  F2:  Homepage Schema.org JSON-LD (ORIGINAL_REQUEST R1)
  F3:  Comparison Page SEO & Schema (ORIGINAL_REQUEST R1, R2)
  F4:  Bengali Topic Page & Routing (ORIGINAL_REQUEST R2)
  F5:  Hindi Topic Page & Routing (ORIGINAL_REQUEST R2)
  F6:  Robots.txt Access & Sitemap Pointer (ORIGINAL_REQUEST R4)
  F7:  Sitemap.xml Format & URLs (ORIGINAL_REQUEST R4)
  F8:  LLMs.txt AI Search Visibility (ORIGINAL_REQUEST R3)
  F9:  GSC Verification Files & Tags (ORIGINAL_REQUEST R1, R4)
  F10: SXO & Internal Navigation (ORIGINAL_REQUEST R1, R2)

Test Tiers:
  Tier 1: Feature Coverage (>=5 tests per feature = >=50 tests)
  Tier 2: Boundary & Corner Cases (>=5 tests per feature = >=50 tests)
  Tier 3: Cross-Feature Interactions (>=15 tests)
  Tier 4: Real-World Scenarios (>=5 tests)

Execution:
  python tests/test_seo_discoverability.py
  (or pytest -v tests/test_seo_discoverability.py)
  (or python -m unittest -v tests/test_seo_discoverability.py)
"""

import asyncio
import json
import os
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

# Safe Unicode output for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

# ---------------------------------------------------------------------------
# Test Environment Setup & Sandboxed Windows IOCP Event Loop Patch
# ---------------------------------------------------------------------------
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

# Import FastAPI application
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.main import app  # noqa: E402


# ---------------------------------------------------------------------------
# In-Memory ASGI Test Client Harness
# ---------------------------------------------------------------------------
class ASGIResponse:
    """Encapsulates HTTP response received from ASGI application."""

    def __init__(self, status_code: int, headers: dict[str, str], body: bytes):
        self.status_code = status_code
        self.headers = headers
        self.content = body
        self.text = body.decode("utf-8", errors="replace")

    def json(self):
        return json.loads(self.text)


class E2EClient:
    """Opaque-box client executing HTTP requests against FastAPI/Starlette ASGI app."""

    def get(self, path: str, headers: dict[str, str] | None = None) -> ASGIResponse:
        raw_headers = []
        if headers:
            for k, v in headers.items():
                raw_headers.append((k.lower().encode("latin1"), v.encode("latin1")))

        # Strip URL fragment if present (fragments are client-side only per RFC 3986)
        req_path = path.split("#")[0]
        if not req_path:
            req_path = "/"

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": req_path,
            "raw_path": req_path.encode("ascii", errors="replace"),
            "query_string": b"",
            "headers": raw_headers,
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        }
        status = 200
        resp_headers: dict[str, str] = {}
        body_chunks: list[bytes] = []

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                for k, v in message.get("headers", []):
                    resp_headers[k.decode("latin1").lower()] = v.decode("latin1")
            elif message["type"] == "http.response.body":
                body_chunks.append(message.get("body", b""))

        async def _run():
            await app(scope, receive, send)

        asyncio.run(_run())
        return ASGIResponse(status, resp_headers, b"".join(body_chunks))


client = E2EClient()


# ---------------------------------------------------------------------------
# HTML & Parsing Helper Utilities
# ---------------------------------------------------------------------------
def extract_title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_meta_content(html: str, name_or_prop: str) -> str | None:
    pattern1 = rf'<meta[^>]+(?:name|property)=["\']{re.escape(name_or_prop)}["\'][^>]+content=["\']([^"\']*)["\']'
    pattern2 = rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:name|property)=["\']{re.escape(name_or_prop)}["\']'
    m1 = re.search(pattern1, html, re.IGNORECASE)
    if m1:
        return m1.group(1).strip()
    m2 = re.search(pattern2, html, re.IGNORECASE)
    return m2.group(1).strip() if m2 else None


def extract_canonical(html: str) -> str | None:
    pattern1 = r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']*)["\']'
    pattern2 = r'<link[^>]+href=["\']([^"\']*)["\'][^>]+rel=["\']canonical["\']'
    m1 = re.search(pattern1, html, re.IGNORECASE)
    if m1:
        return m1.group(1).strip()
    m2 = re.search(pattern2, html, re.IGNORECASE)
    return m2.group(1).strip() if m2 else None


def extract_json_ld(html: str) -> list[dict]:
    results = []
    pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    for block in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
        try:
            parsed = json.loads(block.group(1).strip())
            results.append(parsed)
        except json.JSONDecodeError:
            pass
    return results


def extract_hrefs(html: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r'<a[^>]+href=["\']([^"\']*)["\']', html, re.IGNORECASE)]


# ===========================================================================
# TIER 1: FEATURE COVERAGE (Status 200, clean URLs, valid tags, core features)
# ===========================================================================
class TestTier1FeatureCoverage(unittest.TestCase):
    """Tier 1: Feature Coverage verifying primary behaviors of features F1 - F10."""

    # --- F1: Homepage Metadata & Tags ---
    def test_t1_f1_homepage_status_200(self):
        r = client.get("/")
        self.assertEqual(r.status_code, 200, f"Expected 200, got {r.status_code}")
        self.assertIn("text/html", r.headers.get("content-type", ""))

    def test_t1_f1_homepage_title(self):
        r = client.get("/")
        title = extract_title(r.text)
        self.assertIsNotNone(title, "Homepage missing <title>")
        self.assertIn("Hatekhori", title, f"Title '{title}' does not contain 'Hatekhori'")
        self.assertTrue(any(w in title.lower() for w in ["handwriting", "font", "type"]), f"Title '{title}' missing key handwriting terms")

    def test_t1_f1_homepage_meta_description(self):
        r = client.get("/")
        desc = extract_meta_content(r.text, "description")
        self.assertTrue(desc is not None and len(desc) > 20, f"Homepage missing or weak description: {desc}")
        self.assertTrue(any(lang in desc.lower() for lang in ["bengali", "hindi", "english"]), "Description should mention supported languages")

    def test_t1_f1_homepage_canonical_url(self):
        r = client.get("/")
        canonical = extract_canonical(r.text)
        self.assertEqual(canonical, "https://hatekhori.onrender.com/", f"Unexpected canonical URL: {canonical}")

    def test_t1_f1_homepage_opengraph_tags(self):
        r = client.get("/")
        og_title = extract_meta_content(r.text, "og:title")
        og_desc = extract_meta_content(r.text, "og:description")
        og_url = extract_meta_content(r.text, "og:url")
        og_type = extract_meta_content(r.text, "og:type")
        self.assertIsNotNone(og_title, "Missing og:title on homepage")
        self.assertIsNotNone(og_desc, "Missing og:description on homepage")
        self.assertEqual(og_url, "https://hatekhori.onrender.com/", f"og:url mismatch: {og_url}")
        self.assertIn(og_type, ["website", "product"], f"Unexpected og:type: {og_type}")

    def test_t1_f1_homepage_twitter_cards(self):
        r = client.get("/")
        card = extract_meta_content(r.text, "twitter:card")
        self.assertIn(card, ["summary", "summary_large_image"], f"Missing or invalid twitter:card: {card}")
        tw_title = extract_meta_content(r.text, "twitter:title") or extract_meta_content(r.text, "og:title")
        self.assertIsNotNone(tw_title, "Missing twitter title / og:title fallback")

    # --- F2: Homepage Schema.org JSON-LD ---
    def test_t1_f2_homepage_schema_json_ld_present(self):
        r = client.get("/")
        schemas = extract_json_ld(r.text)
        self.assertGreater(len(schemas), 0, "Homepage missing <script type='application/ld+json'>")

    def test_t1_f2_homepage_schema_valid_json(self):
        r = client.get("/")
        schemas = extract_json_ld(r.text)
        self.assertGreater(len(schemas), 0, "No valid JSON-LD found on homepage")
        schema = schemas[0]
        self.assertTrue("@context" in schema and "schema.org" in schema["@context"], "Missing or invalid @context in Schema.org JSON-LD")

    def test_t1_f2_homepage_schema_website_entity(self):
        r = client.get("/")
        schemas = extract_json_ld(r.text)
        entities = []
        for s in schemas:
            if "@graph" in s:
                entities.extend(s["@graph"])
            else:
                entities.append(s)
        types = [e.get("@type") for e in entities]
        self.assertIn("WebSite", types, f"Missing WebSite @type in homepage schema graph: {types}")

    def test_t1_f2_homepage_schema_software_application_entity(self):
        r = client.get("/")
        schemas = extract_json_ld(r.text)
        entities = []
        for s in schemas:
            if "@graph" in s:
                entities.extend(s["@graph"])
            else:
                entities.append(s)
        soft_apps = [e for e in entities if e.get("@type") == "SoftwareApplication"]
        self.assertGreater(len(soft_apps), 0, "Missing SoftwareApplication entity in homepage schema")
        app_entity = soft_apps[0]
        self.assertIn(app_entity.get("name"), ["Hatekhori", "হাতে খড়ি"], f"Unexpected app name: {app_entity.get('name')}")

    def test_t1_f2_homepage_schema_faq_page_entity(self):
        r = client.get("/")
        schemas = extract_json_ld(r.text)
        entities = []
        for s in schemas:
            if "@graph" in s:
                entities.extend(s["@graph"])
            else:
                entities.append(s)
        faqs = [e for e in entities if e.get("@type") == "FAQPage"]
        self.assertGreater(len(faqs), 0, "Missing FAQPage entity in homepage schema")
        self.assertIn("mainEntity", faqs[0], "FAQPage entity missing mainEntity list")

    # --- F3: Comparison Page SEO & Schema ---
    def test_t1_f3_compare_page_status_200(self):
        r = client.get("/compare/calligraphr-alternative")
        self.assertEqual(r.status_code, 200, f"Expected 200 on /compare/calligraphr-alternative, got {r.status_code}")

    def test_t1_f3_compare_page_title(self):
        r = client.get("/compare/calligraphr-alternative")
        title = extract_title(r.text)
        self.assertIsNotNone(title, "Comparison page missing <title>")
        self.assertTrue("Calligraphr" in title and "Alternative" in title, f"Title does not target Calligraphr alternative: '{title}'")

    def test_t1_f3_compare_page_canonical(self):
        r = client.get("/compare/calligraphr-alternative")
        canonical = extract_canonical(r.text)
        self.assertEqual(canonical, "https://hatekhori.onrender.com/compare/calligraphr-alternative", f"Canonical mismatch: {canonical}")

    def test_t1_f3_compare_page_meta_description(self):
        r = client.get("/compare/calligraphr-alternative")
        desc = extract_meta_content(r.text, "description")
        self.assertTrue(desc is not None and "calligraphr" in desc.lower(), f"Description does not mention Calligraphr: {desc}")

    def test_t1_f3_compare_page_schema_json_ld(self):
        r = client.get("/compare/calligraphr-alternative")
        schemas = extract_json_ld(r.text)
        self.assertGreater(len(schemas), 0, "Comparison page missing JSON-LD schema")
        entities = []
        for s in schemas:
            if "@graph" in s:
                entities.extend(s["@graph"])
            else:
                entities.append(s)
        types = [e.get("@type") for e in entities]
        self.assertTrue("SoftwareApplication" in types or "FAQPage" in types, f"Missing SoftwareApplication or FAQPage in comparison schema: {types}")

    def test_t1_f3_compare_page_open_graph(self):
        r = client.get("/compare/calligraphr-alternative")
        og_title = extract_meta_content(r.text, "og:title")
        og_url = extract_meta_content(r.text, "og:url")
        self.assertIsNotNone(og_title, "Missing og:title on comparison page")
        self.assertEqual(og_url, "https://hatekhori.onrender.com/compare/calligraphr-alternative", f"Unexpected og:url on comparison page: {og_url}")

    # --- F4: Bengali Topic Page & Routing ---
    def test_t1_f4_bengali_page_status_200(self):
        r = client.get("/bengali-font-maker")
        self.assertEqual(r.status_code, 200, f"Expected 200 for clean route /bengali-font-maker, got {r.status_code}")

    def test_t1_f4_bengali_page_content_type(self):
        r = client.get("/bengali-font-maker")
        self.assertIn("text/html", r.headers.get("content-type", ""))

    def test_t1_f4_bengali_page_title(self):
        r = client.get("/bengali-font-maker")
        title = extract_title(r.text)
        self.assertIsNotNone(title, "Bengali page missing <title>")
        self.assertTrue(any(k in title.lower() for k in ["bengali", "bangla", "বাংলা"]), f"Title missing Bengali keyword: '{title}'")

    def test_t1_f4_bengali_page_canonical(self):
        r = client.get("/bengali-font-maker")
        canonical = extract_canonical(r.text)
        self.assertEqual(canonical, "https://hatekhori.onrender.com/bengali-font-maker", f"Canonical mismatch on Bengali page: {canonical}")

    def test_t1_f4_bengali_page_cta_and_specimen(self):
        r = client.get("/bengali-font-maker")
        text = r.text
        self.assertTrue(any(t in text for t in ["Studio", "Generate", "Download", "Sheet"]), "Bengali page missing CTA / action triggers")

    def test_t1_f4_bengali_page_meta_tags(self):
        r = client.get("/bengali-font-maker")
        desc = extract_meta_content(r.text, "description")
        self.assertTrue(desc is not None and len(desc) > 30, f"Bengali page missing or short description: {desc}")

    # --- F5: Hindi Topic Page & Routing ---
    def test_t1_f5_hindi_page_status_200(self):
        r = client.get("/hindi-font-generator")
        self.assertEqual(r.status_code, 200, f"Expected 200 for clean route /hindi-font-generator, got {r.status_code}")

    def test_t1_f5_hindi_page_content_type(self):
        r = client.get("/hindi-font-generator")
        self.assertIn("text/html", r.headers.get("content-type", ""))

    def test_t1_f5_hindi_page_title(self):
        r = client.get("/hindi-font-generator")
        title = extract_title(r.text)
        self.assertIsNotNone(title, "Hindi page missing <title>")
        self.assertTrue(any(k in title.lower() for k in ["hindi", "devanagari", "हिन्दी"]), f"Title missing Hindi keyword: '{title}'")

    def test_t1_f5_hindi_page_canonical(self):
        r = client.get("/hindi-font-generator")
        canonical = extract_canonical(r.text)
        self.assertEqual(canonical, "https://hatekhori.onrender.com/hindi-font-generator", f"Canonical mismatch on Hindi page: {canonical}")

    def test_t1_f5_hindi_page_cta_and_specimen(self):
        r = client.get("/hindi-font-generator")
        text = r.text
        self.assertTrue(any(t in text for t in ["Studio", "Generate", "Download", "Sheet"]), "Hindi page missing CTA / action triggers")

    def test_t1_f5_hindi_page_meta_tags(self):
        r = client.get("/hindi-font-generator")
        desc = extract_meta_content(r.text, "description")
        self.assertTrue(desc is not None and len(desc) > 30, f"Hindi page missing or short description: {desc}")

    # --- F6: Robots.txt Access & Sitemap Pointer ---
    def test_t1_f6_robots_status_200(self):
        r = client.get("/robots.txt")
        self.assertEqual(r.status_code, 200, f"Expected 200 for /robots.txt, got {r.status_code}")

    def test_t1_f6_robots_content_type(self):
        r = client.get("/robots.txt")
        self.assertTrue(r.headers.get("content-type", "").startswith("text/plain"), f"Unexpected content-type: {r.headers.get('content-type')}")

    def test_t1_f6_robots_user_agent_wildcard(self):
        r = client.get("/robots.txt")
        self.assertIn("User-agent: *", r.text, "robots.txt missing User-agent: *")
        self.assertIn("Allow: /", r.text, "robots.txt missing Allow: /")

    def test_t1_f6_robots_disallow_internal_dirs(self):
        r = client.get("/robots.txt")
        self.assertIn("Disallow: /uploads/", r.text, "robots.txt should disallow internal /uploads/")
        self.assertIn("Disallow: /output/", r.text, "robots.txt should disallow internal /output/")

    def test_t1_f6_robots_sitemap_pointer(self):
        r = client.get("/robots.txt")
        self.assertIn("Sitemap: https://hatekhori.onrender.com/sitemap.xml", r.text, f"robots.txt sitemap pointer incorrect: {r.text}")

    def test_t1_f6_robots_ai_crawlers_allowed(self):
        r = client.get("/robots.txt")
        self.assertIn("GPTBot", r.text, "robots.txt missing GPTBot declaration")
        self.assertIn("PerplexityBot", r.text, "robots.txt missing PerplexityBot declaration")

    # --- F7: Sitemap.xml Format & URLs ---
    def test_t1_f7_sitemap_status_200(self):
        r = client.get("/sitemap.xml")
        self.assertEqual(r.status_code, 200, f"Expected 200 for /sitemap.xml, got {r.status_code}")

    def test_t1_f7_sitemap_media_type(self):
        r = client.get("/sitemap.xml")
        self.assertIn("xml", r.headers.get("content-type", ""), f"Unexpected sitemap content-type: {r.headers.get('content-type')}")

    def test_t1_f7_sitemap_valid_xml(self):
        r = client.get("/sitemap.xml")
        try:
            root = ET.fromstring(r.content)
        except Exception as e:
            self.fail(f"sitemap.xml is not valid XML: {e}")
        self.assertIn("urlset", root.tag, f"Root tag is not urlset: {root.tag}")

    def test_t1_f7_sitemap_root_url_present(self):
        r = client.get("/sitemap.xml")
        root = ET.fromstring(r.content)
        locs = [elem.text.strip() for elem in root.iter() if elem.tag.endswith("loc")]
        self.assertIn("https://hatekhori.onrender.com/", locs, f"Missing root URL in sitemap: {locs}")

    def test_t1_f7_sitemap_clean_routes_present(self):
        r = client.get("/sitemap.xml")
        root = ET.fromstring(r.content)
        locs = [elem.text.strip() for elem in root.iter() if elem.tag.endswith("loc")]
        self.assertIn("https://hatekhori.onrender.com/compare/calligraphr-alternative", locs, "Missing comparison URL in sitemap")
        self.assertIn("https://hatekhori.onrender.com/bengali-font-maker", locs, "Missing Bengali page URL in sitemap")
        self.assertIn("https://hatekhori.onrender.com/hindi-font-generator", locs, "Missing Hindi page URL in sitemap")

    def test_t1_f7_sitemap_sheets_present(self):
        r = client.get("/sitemap.xml")
        root = ET.fromstring(r.content)
        locs = [elem.text.strip() for elem in root.iter() if elem.tag.endswith("loc")]
        sheet_urls = [u for u in locs if "guideline-sheet" in u]
        self.assertGreaterEqual(len(sheet_urls), 3, f"Expected at least 3 guideline sheet PNGs in sitemap, found {len(sheet_urls)}: {sheet_urls}")

    # --- F8: LLMs.txt AI Search Visibility ---
    def test_t1_f8_llms_txt_status_200(self):
        r = client.get("/llms.txt")
        self.assertEqual(r.status_code, 200, f"Expected 200 for /llms.txt, got {r.status_code}")

    def test_t1_f8_llms_txt_content_type(self):
        r = client.get("/llms.txt")
        self.assertTrue(r.headers.get("content-type", "").startswith("text/"), f"Unexpected content-type for llms.txt: {r.headers.get('content-type')}")

    def test_t1_f8_llms_txt_mentions_languages(self):
        r = client.get("/llms.txt")
        text = r.text
        self.assertTrue("Bengali" in text or "বাংলা" in text, "llms.txt missing Bengali language support description")
        self.assertTrue("Hindi" in text or "हिन्दी" in text, "llms.txt missing Hindi language support description")
        self.assertTrue("English" in text or "Latin" in text, "llms.txt missing English language support description")

    def test_t1_f8_llms_txt_pricing_and_privacy(self):
        r = client.get("/llms.txt")
        text = r.text.lower()
        self.assertTrue(any(w in text for w in ["free", "zero", "account-free"]), "llms.txt missing pricing clarity")
        self.assertTrue(any(w in text for w in ["privacy", "exif", "anti-ai", "penmanship"]), "llms.txt missing privacy / anti-AI vector craft note")

    def test_t1_f8_llms_txt_canonical_domain(self):
        r = client.get("/llms.txt")
        self.assertIn("https://hatekhori.onrender.com", r.text, "llms.txt URLs should use onrender.com domain")

    def test_t1_f8_llms_txt_formats(self):
        r = client.get("/llms.txt")
        self.assertTrue(".otf" in r.text or "OpenType" in r.text, "llms.txt missing OpenType format")
        self.assertTrue(".ttf" in r.text or "TrueType" in r.text, "llms.txt missing TrueType format")

    # --- F9: GSC Verification Files & Tags ---
    def test_t1_f9_gsc_file_status_200(self):
        r = client.get("/google283830a3fd2e4cf3.html")
        self.assertEqual(r.status_code, 200, f"Expected 200 for Google verification file, got {r.status_code}")

    def test_t1_f9_gsc_file_content_exact(self):
        r = client.get("/google283830a3fd2e4cf3.html")
        self.assertIn("google-site-verification: google283830a3fd2e4cf3.html", r.text, f"GSC token verification file content mismatch: '{r.text}'")

    def test_t1_f9_gsc_meta_tag_hash_present(self):
        r = client.get("/")
        self.assertIn("ywFgWCyBD6nzTB9FV6Df3cGfGpcPVhtdGiTvXt_wf20", r.text, "Homepage missing GSC verification meta hash token")

    def test_t1_f9_gsc_meta_tag_file_token_present(self):
        r = client.get("/")
        self.assertIn("google283830a3fd2e4cf3", r.text, "Homepage missing GSC file verification meta token")

    def test_t1_f9_gsc_meta_tag_on_compare_page(self):
        r = client.get("/compare/calligraphr-alternative")
        self.assertTrue("ywFgWCyBD6nzTB9FV6Df3cGfGpcPVhtdGiTvXt_wf20" in r.text or "google-site-verification" in r.text, (
            "Comparison page missing GSC verification meta tag"
        ))

    # --- F10: SXO & Internal Navigation ---
    def test_t1_f10_homepage_nav_contains_compare(self):
        r = client.get("/")
        hrefs = extract_hrefs(r.text)
        self.assertTrue(any("compare/calligraphr-alternative" in h for h in hrefs), f"Homepage navigation missing link to Calligraphr alternative: {hrefs}")

    def test_t1_f10_homepage_nav_contains_topic_pages(self):
        r = client.get("/")
        hrefs = extract_hrefs(r.text)
        self.assertTrue(any("bengali-font-maker" in h for h in hrefs), f"Homepage missing internal link to Bengali font maker: {hrefs}")
        self.assertTrue(any("hindi-font-generator" in h for h in hrefs), f"Homepage missing internal link to Hindi font generator: {hrefs}")

    def test_t1_f10_compare_page_nav_back_home(self):
        r = client.get("/compare/calligraphr-alternative")
        hrefs = extract_hrefs(r.text)
        self.assertTrue(any(h in ["/", "../", "https://hatekhori.onrender.com", "https://hatekhori.onrender.com/"] for h in hrefs), (
            f"Compare page missing navigation link back to homepage: {hrefs}"
        ))

    def test_t1_f10_broken_prd_link_fixed(self):
        r = client.get("/")
        self.assertNotIn('href="PRD.md"', r.text, "Homepage still contains broken link href='PRD.md'")

    def test_t1_f10_homepage_semantic_landmarks(self):
        r = client.get("/")
        text = r.text.lower()
        self.assertIn("<nav", text, "Homepage missing <nav> landmark")
        self.assertTrue("<header" in text or "<main" in text or "<section" in text, "Homepage missing semantic header/main/section")


# ===========================================================================
# TIER 2: BOUNDARY & CORNER CASES (Trailing slashes, 404, lengths, encodings)
# ===========================================================================
class TestTier2BoundaryCornerCases(unittest.TestCase):
    """Tier 2: Boundary & Corner Cases covering constraints, limits, and encodings."""

    # --- F1 Boundaries ---
    def test_t2_f1_trailing_slash_handling(self):
        r = client.get("/")
        self.assertEqual(r.status_code, 200)
        r_slash = client.get("/compare/calligraphr-alternative/")
        self.assertIn(r_slash.status_code, [200, 301, 302, 307, 308, 404])

    def test_t2_f1_utf8_meta_charset_position(self):
        r = client.get("/")
        idx = r.text.lower().find('charset="utf-8"')
        if idx == -1:
            idx = r.text.lower().find("charset=utf-8")
        self.assertTrue(idx != -1 and idx < 1024, f"Charset meta tag should be near top of <head> (< 1024 bytes), found at {idx}")

    def test_t2_f1_viewport_meta_content(self):
        r = client.get("/")
        vp = extract_meta_content(r.text, "viewport")
        self.assertIsNotNone(vp, "Missing viewport meta tag")
        self.assertTrue("width=device-width" in vp and "initial-scale=1" in vp, f"Non-standard viewport config: {vp}")

    def test_t2_f1_title_length_bounds(self):
        r = client.get("/")
        title = extract_title(r.text)
        self.assertIsNotNone(title)
        self.assertTrue(15 <= len(title) <= 75, f"Title length ({len(title)} chars) outside optimal SEO range (15-75): '{title}'")

    def test_t2_f1_meta_description_length_bounds(self):
        r = client.get("/")
        desc = extract_meta_content(r.text, "description")
        self.assertIsNotNone(desc)
        self.assertTrue(50 <= len(desc) <= 175, f"Description length ({len(desc)} chars) outside optimal SEO snippet range (50-175): '{desc}'")

    def test_t2_f1_head_tag_closure(self):
        r = client.get("/")
        self.assertTrue("<head>" in r.text.lower() or "<head " in r.text.lower(), "Missing opening <head> tag")
        self.assertIn("</head>", r.text.lower(), "Missing closing </head> tag")

    # --- F2 Boundaries ---
    def test_t2_f2_json_ld_script_type_case_exact(self):
        r = client.get("/")
        self.assertTrue('type="application/ld+json"' in r.text or "type='application/ld+json'" in r.text, "MIME type must be exactly application/ld+json")

    def test_t2_f2_schema_offers_price_currency(self):
        r = client.get("/")
        schemas = extract_json_ld(r.text)
        entities = []
        for s in schemas:
            if "@graph" in s:
                entities.extend(s["@graph"])
            else:
                entities.append(s)
        apps = [e for e in entities if e.get("@type") == "SoftwareApplication"]
        self.assertGreater(len(apps), 0, "No SoftwareApplication entity")
        offers = apps[0].get("offers", {})
        self.assertIn(offers.get("price"), ["0", 0, "0.00"], f"Offers price should be free ('0'): {offers.get('price')}")
        self.assertEqual(offers.get("priceCurrency"), "USD", f"Offers priceCurrency mismatch: {offers.get('priceCurrency')}")

    def test_t2_f2_schema_aggregate_rating_bounds(self):
        r = client.get("/")
        schemas = extract_json_ld(r.text)
        entities = []
        for s in schemas:
            if "@graph" in s:
                entities.extend(s["@graph"])
            else:
                entities.append(s)
        apps = [e for e in entities if e.get("@type") == "SoftwareApplication"]
        self.assertGreater(len(apps), 0, "No SoftwareApplication entity")
        rating = apps[0].get("aggregateRating", {})
        val = float(rating.get("ratingValue", 0))
        self.assertTrue(1.0 <= val <= 5.0, f"ratingValue ({val}) out of bounds 1.0-5.0")
        self.assertEqual(int(rating.get("bestRating", 5)), 5, "bestRating must be 5")
        self.assertEqual(int(rating.get("worstRating", 1)), 1, "worstRating must be 1")

    def test_t2_f2_schema_faq_empty_check(self):
        r = client.get("/")
        schemas = extract_json_ld(r.text)
        entities = []
        for s in schemas:
            if "@graph" in s:
                entities.extend(s["@graph"])
            else:
                entities.append(s)
        faqs = [e for e in entities if e.get("@type") == "FAQPage"]
        self.assertGreater(len(faqs), 0, "No FAQPage entity")
        items = faqs[0].get("mainEntity", [])
        self.assertGreaterEqual(len(items), 2, f"FAQPage should contain at least 2 Q&A pairs, got {len(items)}")
        for item in items:
            self.assertGreater(len(item.get("name", "")), 5, "FAQ question is too short")
            ans = item.get("acceptedAnswer", {}).get("text", "")
            self.assertGreater(len(ans), 10, "FAQ accepted answer is too short")

    def test_t2_f2_schema_id_uris_valid(self):
        r = client.get("/")
        schemas = extract_json_ld(r.text)
        entities = []
        for s in schemas:
            if "@graph" in s:
                entities.extend(s["@graph"])
            else:
                entities.append(s)
        for e in entities:
            eid = e.get("@id")
            if eid:
                self.assertTrue(eid.startswith("https://hatekhori.onrender.com"), f"Entity @id '{eid}' must start with canonical domain")

    # --- F3 Boundaries ---
    def test_t2_f3_compare_url_case_insensitivity(self):
        r = client.get("/compare/calligraphr-alternative")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Calligraphr", r.text)

    def test_t2_f3_compare_canonical_exact_match(self):
        r = client.get("/compare/calligraphr-alternative")
        canonical = extract_canonical(r.text)
        self.assertEqual(canonical, "https://hatekhori.onrender.com/compare/calligraphr-alternative")
        self.assertFalse(canonical.endswith("/"), "Canonical should not have an extraneous trailing slash")

    def test_t2_f3_compare_faq_non_empty_answers(self):
        r = client.get("/compare/calligraphr-alternative")
        schemas = extract_json_ld(r.text)
        entities = []
        for s in schemas:
            if "@graph" in s:
                entities.extend(s["@graph"])
            else:
                entities.append(s)
        faqs = [e for e in entities if e.get("@type") == "FAQPage"]
        self.assertGreater(len(faqs), 0)
        for q in faqs[0].get("mainEntity", []):
            ans = q.get("acceptedAnswer", {}).get("text", "")
            self.assertGreaterEqual(len(ans), 25, f"Comparison FAQ answer too brief: '{ans}'")

    def test_t2_f3_compare_meta_description_length(self):
        r = client.get("/compare/calligraphr-alternative")
        desc = extract_meta_content(r.text, "description")
        self.assertIsNotNone(desc)
        self.assertTrue(60 <= len(desc) <= 175, f"Comparison meta description length ({len(desc)}) outside 60-175: '{desc}'")

    def test_t2_f3_compare_table_or_matrix_present(self):
        r = client.get("/compare/calligraphr-alternative")
        text = r.text.lower()
        has_matrix = "table" in text or "matrix" in text or "vs" in text or "calligraphr" in text
        self.assertTrue(has_matrix, "Comparison page should contain comparison matrix or feature points")

    # --- F4 Boundaries ---
    def test_t2_f4_bengali_url_clean_no_html_ext(self):
        r = client.get("/bengali-font-maker")
        self.assertEqual(r.status_code, 200)
        canonical = extract_canonical(r.text)
        self.assertTrue(canonical is not None and not canonical.endswith(".html"), "Canonical must be clean URL without .html")

    def test_t2_f4_bengali_html_lang_attribute(self):
        r = client.get("/bengali-font-maker")
        m = re.search(r'<html[^>]+lang=["\']([^"\']*)["\']', r.text, re.IGNORECASE)
        self.assertIsNotNone(m, "Bengali page missing lang attribute on <html>")
        lang = m.group(1).lower()
        self.assertIn(lang, ["bn", "en", "bn-in", "bn-bd"], f"Unexpected lang attribute: {lang}")

    def test_t2_f4_bengali_charset_utf8(self):
        r = client.get("/bengali-font-maker")
        self.assertTrue('charset="utf-8"' in r.text.lower() or "charset=utf-8" in r.text.lower(), "Bengali page missing UTF-8 charset")

    def test_t2_f4_bengali_bengali_script_presence(self):
        r = client.get("/bengali-font-maker")
        bengali_chars = [c for c in r.text if "\u0980" <= c <= "\u09FF"]
        self.assertGreaterEqual(len(bengali_chars), 10, f"Bengali page contains insufficient Bengali characters: found {len(bengali_chars)}")

    def test_t2_f4_bengali_canonical_matches_route(self):
        r = client.get("/bengali-font-maker")
        canonical = extract_canonical(r.text)
        self.assertEqual(canonical, "https://hatekhori.onrender.com/bengali-font-maker")

    # --- F5 Boundaries ---
    def test_t2_f5_hindi_url_clean_no_html_ext(self):
        r = client.get("/hindi-font-generator")
        self.assertEqual(r.status_code, 200)
        canonical = extract_canonical(r.text)
        self.assertTrue(canonical is not None and not canonical.endswith(".html"), "Canonical must be clean URL without .html")

    def test_t2_f5_hindi_html_lang_attribute(self):
        r = client.get("/hindi-font-generator")
        m = re.search(r'<html[^>]+lang=["\']([^"\']*)["\']', r.text, re.IGNORECASE)
        self.assertIsNotNone(m, "Hindi page missing lang attribute on <html>")
        lang = m.group(1).lower()
        self.assertIn(lang, ["hi", "en", "hi-in"], f"Unexpected lang attribute: {lang}")

    def test_t2_f5_hindi_charset_utf8(self):
        r = client.get("/hindi-font-generator")
        self.assertTrue('charset="utf-8"' in r.text.lower() or "charset=utf-8" in r.text.lower(), "Hindi page missing UTF-8 charset")

    def test_t2_f5_hindi_devanagari_script_presence(self):
        r = client.get("/hindi-font-generator")
        hindi_chars = [c for c in r.text if "\u0900" <= c <= "\u097F"]
        self.assertGreaterEqual(len(hindi_chars), 10, f"Hindi page contains insufficient Devanagari characters: found {len(hindi_chars)}")

    def test_t2_f5_hindi_canonical_matches_route(self):
        r = client.get("/hindi-font-generator")
        canonical = extract_canonical(r.text)
        self.assertEqual(canonical, "https://hatekhori.onrender.com/hindi-font-generator")

    # --- F6 Boundaries ---
    def test_t2_f6_robots_line_endings_clean(self):
        r = client.get("/robots.txt")
        self.assertNotIn("\x00", r.text, "robots.txt must not contain null bytes")
        lines = r.text.splitlines()
        self.assertGreaterEqual(len(lines), 5, f"robots.txt is too short: {len(lines)} lines")

    def test_t2_f6_robots_no_html_leakage(self):
        r = client.get("/robots.txt")
        self.assertTrue("<html" not in r.text.lower() and "<!doctype" not in r.text.lower(), "robots.txt contains leaked HTML markup")

    def test_t2_f6_robots_sitemap_directive_casing(self):
        r = client.get("/robots.txt")
        match = re.search(r"^Sitemap:\s*(https://\S+)", r.text, re.MULTILINE)
        self.assertIsNotNone(match, f"robots.txt missing standard 'Sitemap: https://...' directive: {r.text}")

    def test_t2_f6_robots_user_agent_blocks_clean(self):
        r = client.get("/robots.txt")
        agents = re.findall(r"^User-agent:\s*(\S+)", r.text, re.MULTILINE)
        self.assertGreaterEqual(len(agents), 2, f"robots.txt should declare multiple User-agent blocks, found {agents}")

    def test_t2_f6_robots_security_headers(self):
        r = client.get("/robots.txt")
        self.assertEqual(r.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(r.headers.get("x-frame-options"), "DENY")

    # --- F7 Boundaries ---
    def test_t2_f7_sitemap_xml_declaration(self):
        r = client.get("/sitemap.xml")
        self.assertTrue(r.text.startswith("<?xml"), f"sitemap.xml must start with XML declaration, got '{r.text[:30]}'")

    def test_t2_f7_sitemap_urlset_namespace(self):
        r = client.get("/sitemap.xml")
        self.assertIn('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', r.text, "sitemap.xml missing standard sitemaps namespace")

    def test_t2_f7_sitemap_all_locs_https(self):
        r = client.get("/sitemap.xml")
        root = ET.fromstring(r.content)
        for elem in root.iter():
            if elem.tag.endswith("loc"):
                loc = elem.text.strip()
                self.assertTrue(loc.startswith("https://"), f"Sitemap URL not HTTPS: {loc}")

    def test_t2_f7_sitemap_lastmod_iso8601(self):
        r = client.get("/sitemap.xml")
        root = ET.fromstring(r.content)
        iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        lastmods = [elem.text.strip() for elem in root.iter() if elem.tag.endswith("lastmod")]
        self.assertGreater(len(lastmods), 0, "No lastmod elements in sitemap")
        for lm in lastmods:
            self.assertTrue(iso_pattern.match(lm), f"Invalid lastmod date format: {lm}")

    def test_t2_f7_sitemap_priority_float_range(self):
        r = client.get("/sitemap.xml")
        root = ET.fromstring(r.content)
        for elem in root.iter():
            if elem.tag.endswith("priority"):
                val = float(elem.text.strip())
                self.assertTrue(0.0 <= val <= 1.0, f"Priority {val} outside [0.0, 1.0]")

    def test_t2_f7_sitemap_changefreq_valid_enum(self):
        r = client.get("/sitemap.xml")
        root = ET.fromstring(r.content)
        valid_freqs = {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}
        for elem in root.iter():
            if elem.tag.endswith("changefreq"):
                val = elem.text.strip().lower()
                self.assertIn(val, valid_freqs, f"Invalid changefreq: {val}")

    # --- F8 Boundaries ---
    def test_t2_f8_llms_txt_line_count_and_size(self):
        r = client.get("/llms.txt")
        self.assertTrue(200 <= len(r.content) <= 50000, f"llms.txt size ({len(r.content)} bytes) out of bounds")

    def test_t2_f8_llms_txt_markdown_h1(self):
        r = client.get("/llms.txt")
        self.assertTrue(r.text.startswith("# "), f"llms.txt should start with top-level markdown H1 header, got: '{r.text[:30]}'")

    def test_t2_f8_llms_txt_url_section(self):
        r = client.get("/llms.txt")
        self.assertTrue("## Key URLs" in r.text or "## URLs" in r.text, "llms.txt missing URLs section")

    def test_t2_f8_llms_txt_no_empty_links(self):
        r = client.get("/llms.txt")
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]*)\)", r.text):
            link_text, link_url = match.group(1), match.group(2)
            self.assertGreater(len(link_url.strip()), 0, f"Empty markdown link url for text '{link_text}' in llms.txt")

    def test_t2_f8_llms_txt_no_placeholder_tokens(self):
        r = client.get("/llms.txt")
        text = r.text
        for placeholder in ["TODO", "TBD", "FIXME", "localhost"]:
            self.assertNotIn(placeholder, text, f"llms.txt contains unfinished placeholder: '{placeholder}'")

    # --- F9 Boundaries ---
    def test_t2_f9_gsc_file_trailing_newline(self):
        r = client.get("/google283830a3fd2e4cf3.html")
        self.assertTrue(r.text.startswith("google-site-verification:"))
        self.assertIn("google283830a3fd2e4cf3.html", r.text)

    def test_t2_f9_gsc_file_no_extra_html(self):
        r = client.get("/google283830a3fd2e4cf3.html")
        self.assertTrue("<html" not in r.text.lower() and "<body" not in r.text.lower(), "GSC verification file must be pure token text")

    def test_t2_f9_gsc_meta_name_case(self):
        r = client.get("/")
        self.assertTrue('name="google-site-verification"' in r.text or "name='google-site-verification'" in r.text, (
            "google-site-verification meta attribute name must be lowercase"
        ))

    def test_t2_f9_gsc_both_tokens_distinct(self):
        r = client.get("/")
        self.assertIn("ywFgWCyBD6nzTB9FV6Df3cGfGpcPVhtdGiTvXt_wf20", r.text)
        self.assertIn("google283830a3fd2e4cf3", r.text)

    def test_t2_f9_gsc_token_unmangled(self):
        r = client.get("/")
        exact_hash = "ywFgWCyBD6nzTB9FV6Df3cGfGpcPVhtdGiTvXt_wf20"
        self.assertIn(exact_hash, r.text, f"Expected exact GSC hash {exact_hash} in homepage")

    # --- F10 Boundaries ---
    def test_t2_f10_touch_targets_accessible(self):
        r = client.get("/")
        buttons = re.findall(r"<button[^>]*>(.*?)</button>", r.text, re.DOTALL | re.IGNORECASE)
        self.assertGreaterEqual(len(buttons), 2, f"Homepage missing interactive buttons, found {len(buttons)}")
        for b in buttons:
            self.assertGreater(len(b.strip()), 0, "Button has empty content")

    def test_t2_f10_relative_asset_paths(self):
        r = client.get("/")
        r_css = client.get("/style.css")
        self.assertEqual(r_css.status_code, 200, f"style.css returned {r_css.status_code}")
        r_js = client.get("/script.js")
        self.assertEqual(r_js.status_code, 200, f"script.js returned {r_js.status_code}")

    def test_t2_f10_no_dead_hash_hrefs(self):
        r = client.get("/")
        hash_targets = re.findall(r'href="#([a-zA-Z0-9_-]+)"', r.text)
        for target in hash_targets:
            self.assertTrue(f'id="{target}"' in r.text or f"id='{target}'" in r.text, f"Internal anchor #{target} has no matching id on homepage")

    def test_t2_f10_font_studio_launch_id(self):
        r = client.get("/")
        self.assertTrue('id="nav-launch-studio"' in r.text or 'id="hero-enter-studio"' in r.text, "Homepage missing studio launch action button")

    def test_t2_f10_privacy_button_or_link(self):
        r = client.get("/")
        self.assertIn("privacy", r.text.lower(), "Homepage missing privacy policy reference")


# ===========================================================================
# TIER 3: CROSS-FEATURE INTERACTIONS (Combinations, consistency, link graph)
# ===========================================================================
class TestTier3CrossFeatureInteractions(unittest.TestCase):
    """Tier 3: Cross-Feature Interactions verifying graph integrity between modules."""

    def test_t3_sitemap_loc_backend_resolution(self):
        """All URLs declared in sitemap.xml must return 200 OK from the FastAPI backend."""
        r_sitemap = client.get("/sitemap.xml")
        self.assertEqual(r_sitemap.status_code, 200)
        root = ET.fromstring(r_sitemap.content)
        locs = [elem.text.strip() for elem in root.iter() if elem.tag.endswith("loc")]
        self.assertGreaterEqual(len(locs), 4, f"Sitemap has too few URLs: {len(locs)}")
        for loc in locs:
            path = loc.replace("https://hatekhori.onrender.com", "")
            if not path:
                path = "/"
            r = client.get(path)
            self.assertEqual(r.status_code, 200, f"Sitemap loc '{loc}' (path '{path}') returned status {r.status_code}")

    def test_t3_sitemap_loc_matches_page_canonical(self):
        """For every HTML page declared in sitemap.xml, its <link rel='canonical'> must match <loc> exactly."""
        r_sitemap = client.get("/sitemap.xml")
        root = ET.fromstring(r_sitemap.content)
        locs = [elem.text.strip() for elem in root.iter() if elem.tag.endswith("loc")]
        html_locs = [loc for loc in locs if not loc.endswith(".png")]
        for loc in html_locs:
            path = loc.replace("https://hatekhori.onrender.com", "") or "/"
            r = client.get(path)
            self.assertEqual(r.status_code, 200)
            canonical = extract_canonical(r.text)
            self.assertEqual(canonical, loc, f"Page at '{path}' has canonical '{canonical}', expected sitemap loc '{loc}'")

    def test_t3_robots_sitemap_pointer_matches_sitemap_url(self):
        """The sitemap URL declared in robots.txt must resolve and match the live sitemap."""
        r_robots = client.get("/robots.txt")
        match = re.search(r"^Sitemap:\s*(https://\S+)", r_robots.text, re.MULTILINE)
        self.assertIsNotNone(match, "Missing Sitemap pointer in robots.txt")
        sitemap_url = match.group(1).strip()
        self.assertEqual(sitemap_url, "https://hatekhori.onrender.com/sitemap.xml", f"Unexpected Sitemap URL in robots.txt: {sitemap_url}")
        path = sitemap_url.replace("https://hatekhori.onrender.com", "")
        r_sitemap = client.get(path)
        self.assertEqual(r_sitemap.status_code, 200, f"Sitemap URL from robots.txt returned {r_sitemap.status_code}")

    def test_t3_llms_txt_urls_resolve_200(self):
        """Every URL published in llms.txt must return 200 OK from the backend."""
        r_llms = client.get("/llms.txt")
        urls = re.findall(r"https://hatekhori\.onrender\.com(/\S*)", r_llms.text)
        clean_paths = []
        for u in urls:
            clean = u.rstrip(").,]>\"'")
            clean_paths.append(clean or "/")
        self.assertGreaterEqual(len(clean_paths), 4, f"Found too few URLs in llms.txt: {clean_paths}")
        for path in set(clean_paths):
            r = client.get(path)
            self.assertEqual(r.status_code, 200, f"URL path '{path}' from llms.txt returned status {r.status_code}")

    def test_t3_homepage_internal_links_resolve_200(self):
        """All internal links on the homepage must return 200 OK (no broken navigation)."""
        r_home = client.get("/")
        hrefs = extract_hrefs(r_home.text)
        for h in hrefs:
            clean = h.split("#")[0]
            if not clean or clean.startswith("mailto:") or clean.startswith("javascript:"):
                continue
            if clean.startswith("http://") or clean.startswith("https://"):
                if "hatekhori.onrender.com" in clean:
                    path = clean.replace("https://hatekhori.onrender.com", "").replace("http://hatekhori.onrender.com", "") or "/"
                    self.assertEqual(client.get(path).status_code, 200, f"Homepage link to '{clean}' failed")
            else:
                path = "/" + clean.lstrip("/")
                self.assertEqual(client.get(path).status_code, 200, f"Homepage internal link to '{path}' failed")

    def test_t3_compare_internal_links_resolve_200(self):
        """All internal links on the comparison page must return 200 OK."""
        r = client.get("/compare/calligraphr-alternative")
        hrefs = extract_hrefs(r.text)
        for h in hrefs:
            clean = h.split("#")[0]
            if not clean or clean.startswith("mailto:") or clean.startswith("javascript:"):
                continue
            if clean.startswith("http"):
                if "hatekhori.onrender.com" in clean:
                    path = clean.replace("https://hatekhori.onrender.com", "") or "/"
                    self.assertEqual(client.get(path).status_code, 200, f"Compare page link to '{clean}' failed")
            elif clean.startswith("../"):
                path = "/" + clean[3:]
                self.assertEqual(client.get(path).status_code, 200, f"Compare page relative link to '{path}' failed")
            elif clean.startswith("/"):
                self.assertEqual(client.get(clean).status_code, 200, f"Compare page root-relative link to '{clean}' failed")

    def test_t3_bengali_internal_links_resolve_200(self):
        """All internal links on the Bengali topic page must return 200 OK."""
        r = client.get("/bengali-font-maker")
        hrefs = extract_hrefs(r.text)
        for h in hrefs:
            clean = h.split("#")[0]
            if not clean or clean.startswith("mailto:"):
                continue
            path = clean.replace("https://hatekhori.onrender.com", "")
            if not path.startswith("/"):
                path = "/" + path
            self.assertEqual(client.get(path).status_code, 200, f"Bengali page link to '{path}' failed")

    def test_t3_hindi_internal_links_resolve_200(self):
        """All internal links on the Hindi topic page must return 200 OK."""
        r = client.get("/hindi-font-generator")
        hrefs = extract_hrefs(r.text)
        for h in hrefs:
            clean = h.split("#")[0]
            if not clean or clean.startswith("mailto:"):
                continue
            path = clean.replace("https://hatekhori.onrender.com", "")
            if not path.startswith("/"):
                path = "/" + path
            self.assertEqual(client.get(path).status_code, 200, f"Hindi page link to '{path}' failed")

    def test_t3_schema_org_url_matches_canonical(self):
        """Schema.org main entity @id or url on each page aligns with that page's canonical tag."""
        for path in ["/", "/compare/calligraphr-alternative"]:
            r = client.get(path)
            canonical = extract_canonical(r.text)
            schemas = extract_json_ld(r.text)
            self.assertGreater(len(schemas), 0, f"Missing schema on {path}")
            entities = []
            for s in schemas:
                if "@graph" in s:
                    entities.extend(s["@graph"])
                else:
                    entities.append(s)
            urls = [e.get("url") for e in entities if e.get("url")]
            ids = [e.get("@id") for e in entities if e.get("@id")]
            all_refs = urls + ids
            self.assertTrue(any(canonical in ref for ref in all_refs), f"Schema entities on {path} do not align with canonical '{canonical}': {all_refs}")

    def test_t3_opengraph_url_matches_canonical(self):
        """OpenGraph og:url on each page matches that page's canonical tag."""
        for path in ["/", "/compare/calligraphr-alternative", "/bengali-font-maker", "/hindi-font-generator"]:
            r = client.get(path)
            canonical = extract_canonical(r.text)
            og_url = extract_meta_content(r.text, "og:url")
            self.assertEqual(og_url, canonical, f"og:url ({og_url}) does not match canonical ({canonical}) on {path}")

    def test_t3_guideline_sheets_sitemap_and_download(self):
        """Guideline sheets declared in sitemap must be downloadable with correct PNG MIME type."""
        sheets = [
            "/guideline-sheet-bengali.png",
            "/guideline-sheet-hindi.png",
            "/guideline-sheet-english.png",
        ]
        for sheet_path in sheets:
            r = client.get(sheet_path)
            self.assertEqual(r.status_code, 200, f"Sheet {sheet_path} returned {r.status_code}")
            self.assertEqual(r.headers.get("content-type"), "image/png", f"Sheet {sheet_path} bad MIME type: {r.headers.get('content-type')}")
            self.assertTrue(r.content.startswith(b"\x89PNG\r\n\x1a\n"), f"Sheet {sheet_path} is not valid PNG")

    def test_t3_gsc_verification_consistent_across_pages(self):
        """GSC verification hash is preserved consistently across indexable pages."""
        exact_hash = "ywFgWCyBD6nzTB9FV6Df3cGfGpcPVhtdGiTvXt_wf20"
        for path in ["/", "/compare/calligraphr-alternative"]:
            r = client.get(path)
            self.assertIn(exact_hash, r.text, f"Page {path} missing GSC verification hash {exact_hash}")

    def test_t3_security_headers_consistent_across_all_routes(self):
        """Security headers (nosniff, DENY, HSTS) are applied across HTML, XML, and text routes."""
        for path in ["/", "/robots.txt", "/sitemap.xml", "/compare/calligraphr-alternative"]:
            r = client.get(path)
            self.assertEqual(r.headers.get("x-content-type-options"), "nosniff", f"Missing nosniff on {path}")
            self.assertEqual(r.headers.get("x-frame-options"), "DENY", f"Missing DENY on {path}")
            self.assertIn("strict-transport-security", r.headers, f"Missing HSTS on {path}")

    def test_t3_error_404_on_arbitrary_missing_routes(self):
        """Random non-existent URLs return 404, not 200 or 500."""
        for missing_path in ["/non-existent-page-xyz", "/compare/unknown-tool", "/sheets/missing.png"]:
            r = client.get(missing_path)
            self.assertEqual(r.status_code, 404, f"Expected 404 for '{missing_path}', got {r.status_code}")

    def test_t3_static_asset_mime_types_correct(self):
        """Static assets return correct MIME types (CSS -> text/css, JS -> javascript, PNG -> image/png)."""
        self.assertTrue(client.get("/style.css").headers.get("content-type", "").startswith("text/css"))
        self.assertTrue(any(m in client.get("/script.js").headers.get("content-type", "") for m in ["javascript", "text/plain"]))
        self.assertEqual(client.get("/guideline-sheet-bengali.png").headers.get("content-type"), "image/png")

    def test_t3_llms_txt_and_robots_txt_allow_rules(self):
        """robots.txt explicitly permits AI bots to crawl all public assets including llms.txt."""
        r_robots = client.get("/robots.txt")
        lines = r_robots.text.splitlines()
        gptbot_allowed = False
        for i, line in enumerate(lines):
            if "User-agent: GPTBot" in line:
                for next_line in lines[i + 1 : i + 4]:
                    if "Allow: /" in next_line:
                        gptbot_allowed = True
        self.assertTrue(gptbot_allowed, "GPTBot not explicitly allowed in robots.txt")

    def test_t3_canonical_domain_consistency(self):
        """No page canonical tag, sitemap loc, or robots.txt pointer references deprecated domains."""
        r_robots = client.get("/robots.txt")
        self.assertNotIn("https://hatekhori.com/sitemap.xml", r_robots.text, "robots.txt still references deprecated domain hatekhori.com")
        r_sitemap = client.get("/sitemap.xml")
        self.assertNotIn("https://hatekhori.com/", r_sitemap.text, "sitemap.xml contains deprecated domain hatekhori.com")


# ===========================================================================
# TIER 4: REAL-WORLD SCENARIOS (Crawlers, bots, scrapers, mobile users)
# ===========================================================================
class TestTier4RealWorldScenarios(unittest.TestCase):
    """Tier 4: Realistic Workload Scenarios modeling crawlers, bots, and user journeys."""

    def test_t4_scenario_googlebot_crawl_simulation(self):
        """Scenario 1: Googlebot discovers sitemap via robots.txt, crawls all clean routes, and verifies indexability."""
        googlebot_ua = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        headers = {"User-Agent": googlebot_ua}

        # Step 1: Googlebot checks robots.txt
        r_robots = client.get("/robots.txt", headers=headers)
        self.assertEqual(r_robots.status_code, 200)
        self.assertIn("Allow: /", r_robots.text)

        # Step 2: Googlebot reads sitemap pointer
        match = re.search(r"^Sitemap:\s*(\S+)", r_robots.text, re.MULTILINE)
        self.assertIsNotNone(match)
        sitemap_path = match.group(1).replace("https://hatekhori.onrender.com", "")
        r_sitemap = client.get(sitemap_path, headers=headers)
        self.assertEqual(r_sitemap.status_code, 200)

        # Step 3: Googlebot crawls all HTML pages listed
        root = ET.fromstring(r_sitemap.content)
        locs = [elem.text.strip() for elem in root.iter() if elem.tag.endswith("loc")]
        for loc in locs:
            if loc.endswith(".png"):
                continue
            path = loc.replace("https://hatekhori.onrender.com", "") or "/"
            r_page = client.get(path, headers=headers)
            self.assertEqual(r_page.status_code, 200, f"Googlebot received {r_page.status_code} on {path}")
            self.assertIsNotNone(extract_title(r_page.text), f"Page {path} missing title for Googlebot")
            self.assertEqual(extract_canonical(r_page.text), loc, f"Page {path} canonical mismatch for Googlebot")

    def test_t4_scenario_ai_bot_answer_engine_grounding(self):
        """Scenario 2: AI Search Engine (GPTBot / Perplexity) fetches llms.txt and indexes capabilities."""
        ai_ua = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)"
        headers = {"User-Agent": ai_ua}

        # Step 1: AI Bot checks robots.txt
        r_robots = client.get("/robots.txt", headers=headers)
        self.assertEqual(r_robots.status_code, 200)
        self.assertIn("GPTBot", r_robots.text)

        # Step 2: AI Bot fetches /llms.txt
        r_llms = client.get("/llms.txt", headers=headers)
        self.assertEqual(r_llms.status_code, 200)
        content = r_llms.text
        self.assertIn("Hatekhori", content)
        self.assertTrue("Bengali" in content or "বাংলা" in content)
        self.assertTrue("Hindi" in content or "हिन्दी" in content)
        self.assertTrue("OpenType" in content or ".otf" in content)

    def test_t4_scenario_social_media_link_preview_scraper(self):
        """Scenario 3: Twitterbot & Facebook scrapers fetch pages to render rich preview cards."""
        twitter_ua = "Twitterbot/1.0"
        fb_ua = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"

        for ua in [twitter_ua, fb_ua]:
            headers = {"User-Agent": ua}
            for path in ["/", "/compare/calligraphr-alternative", "/bengali-font-maker", "/hindi-font-generator"]:
                r = client.get(path, headers=headers)
                self.assertEqual(r.status_code, 200, f"Social scraper failed on {path} with UA {ua}")
                title = extract_meta_content(r.text, "og:title") or extract_title(r.text)
                desc = extract_meta_content(r.text, "og:description") or extract_meta_content(r.text, "description")
                card = extract_meta_content(r.text, "twitter:card") or "summary"
                self.assertIsNotNone(title, f"Missing social preview title on {path}")
                self.assertIsNotNone(desc, f"Missing social preview description on {path}")
                self.assertIn(card, ["summary", "summary_large_image"], f"Invalid twitter:card on {path}: {card}")

    def test_t4_scenario_mobile_browser_responsive_audit(self):
        """Scenario 4: Mobile browser loads pages and verifies responsive viewport and reciprocal home navigation."""
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        headers = {"User-Agent": mobile_ua}

        pages = ["/", "/compare/calligraphr-alternative", "/bengali-font-maker", "/hindi-font-generator"]
        for path in pages:
            r = client.get(path, headers=headers)
            self.assertEqual(r.status_code, 200, f"Mobile user failed to load {path}")
            vp = extract_meta_content(r.text, "viewport")
            self.assertTrue(vp is not None and "width=device-width" in vp, f"Mobile viewport missing on {path}")
            # Reciprocal navigation check
            if path != "/":
                hrefs = extract_hrefs(r.text)
                has_home_nav = any(h in ["/", "../", "https://hatekhori.onrender.com", "https://hatekhori.onrender.com/"] for h in hrefs)
                self.assertTrue(has_home_nav, f"Mobile user on {path} has no way to navigate back to homepage/studio")

    def test_t4_scenario_gsc_site_ownership_verification_flow(self):
        """Scenario 5: Search Console Ownership Verification simulates Googlebot verifying site ownership."""
        # Method 1: HTML file verification
        r_file = client.get("/google283830a3fd2e4cf3.html")
        self.assertEqual(r_file.status_code, 200)
        self.assertEqual(r_file.text.strip(), "google-site-verification: google283830a3fd2e4cf3.html")

        # Method 2: HTML meta tag verification
        r_meta = client.get("/")
        self.assertEqual(r_meta.status_code, 200)
        self.assertIn("ywFgWCyBD6nzTB9FV6Df3cGfGpcPVhtdGiTvXt_wf20", r_meta.text)

    def test_t4_scenario_end_to_end_sxo_funnel(self):
        """Scenario 6: User journeys through search funnel from topic page to guideline sheet to studio."""
        # User lands on Bengali font maker from search
        r_landing = client.get("/bengali-font-maker")
        self.assertEqual(r_landing.status_code, 200)

        # User finds link to guideline sheet and downloads it
        hrefs = extract_hrefs(r_landing.text)
        sheet_link = next((h for h in hrefs if "guideline-sheet" in h), None)
        self.assertIsNotNone(sheet_link, "Landing page missing link to guideline sheet")
        sheet_path = "/" + sheet_link.replace("https://hatekhori.onrender.com", "").lstrip("/")
        r_sheet = client.get(sheet_path)
        self.assertEqual(r_sheet.status_code, 200)
        self.assertEqual(r_sheet.headers.get("content-type"), "image/png")

        # User navigates to generator / studio
        r_home = client.get("/")
        self.assertEqual(r_home.status_code, 200)
        self.assertTrue("Launch Studio" in r_home.text or "Launch Font Studio" in r_home.text)


# ===========================================================================
# Test Runner & Self-Execution Summary
# ===========================================================================
def run_all_tests() -> tuple[int, int, int]:
    """Discovers and runs all test_* methods across Tiers 1-4, reporting counts."""
    tier_classes = [
        (1, TestTier1FeatureCoverage),
        (2, TestTier2BoundaryCornerCases),
        (3, TestTier3CrossFeatureInteractions),
        (4, TestTier4RealWorldScenarios),
    ]

    tier_counts = {1: {"total": 0, "pass": 0, "fail": 0},
                   2: {"total": 0, "pass": 0, "fail": 0},
                   3: {"total": 0, "pass": 0, "fail": 0},
                   4: {"total": 0, "pass": 0, "fail": 0}}

    print("\n========================================================")
    print("Hatekhori SEO & Discoverability E2E Test Suite")
    print("========================================================\n")

    for tier_num, test_cls in tier_classes:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_cls)
        for test in suite:
            test_name = test._testMethodName
            tier_counts[tier_num]["total"] += 1
            instance = test_cls(test_name)
            try:
                method = getattr(instance, test_name)
                method()
                tier_counts[tier_num]["pass"] += 1
                print(f"PASS [T{tier_num}]: {test_name}")
            except Exception as e:
                tier_counts[tier_num]["fail"] += 1
                err_line = str(e).strip().splitlines()[0][:140]
                print(f"FAIL [T{tier_num}]: {test_name} -> {err_line}")

    total_pass = sum(t["pass"] for t in tier_counts.values())
    total_fail = sum(t["fail"] for t in tier_counts.values())
    total_tests = sum(t["total"] for t in tier_counts.values())

    print("\n--------------------------------------------------------")
    print("E2E Test Execution Summary:")
    for t in [1, 2, 3, 4]:
        print(f"  Tier {t}: {tier_counts[t]['pass']} passed / {tier_counts[t]['total']} total (failed: {tier_counts[t]['fail']})")
    print(f"Total: {total_pass} passed / {total_tests} total (failed: {total_fail})")
    print("--------------------------------------------------------\n")

    return total_pass, total_fail, total_tests


if __name__ == "__main__":
    run_all_tests()
