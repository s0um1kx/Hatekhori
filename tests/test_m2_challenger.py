"""
Milestone 2 Empirical Challenger Verification Test Suite
Targets: Clean routes, HTTP status codes, trailing slashes, security headers,
         and Schema.org JSON-LD metadata for:
         - /compare/calligraphr-alternative
         - /bengali-font-maker
         - /hindi-font-generator
Author: m2_challenger_1 (Empirical Challenger: Critic & Specialist)
"""

import os
import re
import sys
import json
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
COMPARE_HTML_PATH = os.path.join(FRONTEND_DIR, "compare", "calligraphr-alternative.html")
BENGALI_HTML_PATH = os.path.join(FRONTEND_DIR, "bengali-font-maker.html")
HINDI_HTML_PATH = os.path.join(FRONTEND_DIR, "hindi-font-generator.html")

# Safe Unicode output for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

# Sandboxed test setup & Windows IOCP event loop patch
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
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))
from app.main import app


class ASGIResponse:
    def __init__(self, status_code: int, headers: dict[str, str], body: bytes):
        self.status_code = status_code
        self.headers = headers
        self.content = body
        self.text = body.decode("utf-8", errors="replace")


class ASGIClient:
    def __init__(self, asgi_app):
        self.app = asgi_app

    def request(self, method: str, path: str, headers: dict[str, str] | None = None, query_string: bytes = b"") -> ASGIResponse:
        import asyncio
        req_headers = []
        if headers:
            for k, v in headers.items():
                req_headers.append((k.lower().encode("latin1"), v.encode("latin1")))

        req_path = path.split("#")[0]
        if not req_path:
            req_path = "/"

        if "?" in req_path:
            req_path, qs_str = req_path.split("?", 1)
            query_string = qs_str.encode("latin1")

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method.upper(),
            "scheme": "http",
            "path": req_path,
            "raw_path": req_path.encode("latin1", errors="replace"),
            "query_string": query_string,
            "headers": req_headers,
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        }

        response_status = 200
        response_headers = {}
        response_body = bytearray()

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            nonlocal response_status, response_headers, response_body
            if message["type"] == "http.response.start":
                response_status = message["status"]
                for k, v in message.get("headers", []):
                    response_headers[k.decode("latin1").lower()] = v.decode("latin1")
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.app(scope, receive, send))
        finally:
            loop.close()

        return ASGIResponse(response_status, response_headers, bytes(response_body))

    def get(self, path: str, headers: dict[str, str] | None = None) -> ASGIResponse:
        return self.request("GET", path, headers=headers)

    def post(self, path: str, headers: dict[str, str] | None = None) -> ASGIResponse:
        return self.request("POST", path, headers=headers)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta_tags = []
        self.links = []
        self.scripts = []
        self.headings = []
        self.anchors = []
        self.html_attrs = {}
        self.title = None
        self._in_title = False
        self._in_script = False
        self._curr_heading = None
        self._curr_script_attrs = {}
        self._curr_script_content = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "html":
            self.html_attrs = attr_dict
        elif tag == "meta":
            self.meta_tags.append(attr_dict)
        elif tag == "link":
            self.links.append(attr_dict)
        elif tag == "a":
            self.anchors.append(attr_dict)
        elif tag == "title":
            self._in_title = True
        elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self._curr_heading = {"tag": tag, "text": ""}
        elif tag == "script":
            self._in_script = True
            self._curr_script_attrs = attr_dict
            self._curr_script_content = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"] and self._curr_heading:
            self.headings.append(self._curr_heading)
            self._curr_heading = None
        elif tag == "script":
            self._in_script = False
            self.scripts.append({
                "attrs": self._curr_script_attrs,
                "content": "".join(self._curr_script_content)
            })
            self._curr_script_attrs = {}
            self._curr_script_content = []

    def handle_data(self, data):
        if self._in_title:
            self.title = data if not self.title else self.title + data
        elif self._curr_heading:
            self._curr_heading["text"] += data
        elif self._in_script:
            self._curr_script_content.append(data)


def parse_page_file(filepath: str) -> tuple[str, PageParser, list[dict]]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    parser = PageParser()
    parser.feed(content)
    json_ld_blocks = []
    for s in parser.scripts:
        if s["attrs"].get("type") == "application/ld+json":
            json_ld_blocks.append(json.loads(s["content"].strip()))
    return content, parser, json_ld_blocks


class EmpiricalM2ChallengerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = ASGIClient(app)
        cls.compare_html, cls.compare_parser, cls.compare_json_ld = parse_page_file(COMPARE_HTML_PATH)
        cls.bengali_html, cls.bengali_parser, cls.bengali_json_ld = parse_page_file(BENGALI_HTML_PATH)
        cls.hindi_html, cls.hindi_parser, cls.hindi_json_ld = parse_page_file(HINDI_HTML_PATH)

    # =========================================================================
    # SUITE 1: CLEAN ROUTE STATUS CODES & CONTENT-TYPE VERIFICATION
    # =========================================================================

    def test_compare_clean_route_status_and_content_type(self):
        """GET /compare/calligraphr-alternative returns 200 OK and text/html."""
        res = self.client.get("/compare/calligraphr-alternative")
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}")
        ct = res.headers.get("content-type", "")
        self.assertTrue(ct.startswith("text/html"), f"Unexpected Content-Type: {ct}")
        self.assertIn("Hatekhori", res.text)
        self.assertIn("Calligraphr", res.text)

    def test_bengali_clean_route_status_and_content_type(self):
        """GET /bengali-font-maker returns 200 OK and text/html."""
        res = self.client.get("/bengali-font-maker")
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}")
        ct = res.headers.get("content-type", "")
        self.assertTrue(ct.startswith("text/html"), f"Unexpected Content-Type: {ct}")
        self.assertIn("বাংলা", res.text)

    def test_hindi_clean_route_status_and_content_type(self):
        """GET /hindi-font-generator returns 200 OK and text/html."""
        res = self.client.get("/hindi-font-generator")
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}")
        ct = res.headers.get("content-type", "")
        self.assertTrue(ct.startswith("text/html"), f"Unexpected Content-Type: {ct}")
        self.assertIn("हिन्दी", res.text)

    # =========================================================================
    # SUITE 2: SECURITY HEADERS & CACHE-CONTROL ON CLEAN ROUTES
    # =========================================================================

    def test_security_headers_on_all_three_clean_routes(self):
        """Verify required security headers (CSP, nosniff, DENY, etc.) on all M2 clean routes."""
        routes = [
            "/compare/calligraphr-alternative",
            "/bengali-font-maker",
            "/hindi-font-generator"
        ]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} did not return 200")
            headers = res.headers

            # 1. Content-Security-Policy
            csp = headers.get("content-security-policy", "")
            self.assertIn("default-src 'self'", csp, f"{route} missing default-src in CSP")
            self.assertIn("frame-ancestors 'none'", csp, f"{route} missing frame-ancestors in CSP")
            self.assertIn("https://fonts.gstatic.com", csp, f"{route} missing font source in CSP")

            # 2. X-Content-Type-Options
            self.assertEqual(headers.get("x-content-type-options"), "nosniff", f"{route} missing nosniff")

            # 3. X-Frame-Options
            self.assertEqual(headers.get("x-frame-options"), "DENY", f"{route} missing X-Frame-Options DENY")

            # 4. Referrer-Policy
            self.assertEqual(headers.get("referrer-policy"), "strict-origin-when-cross-origin", f"{route} bad Referrer-Policy")

            # 5. Permissions-Policy
            self.assertEqual(headers.get("permissions-policy"), "camera=(), microphone=(), geolocation=()", f"{route} bad Permissions-Policy")

    def test_cache_control_revalidation_on_clean_routes(self):
        """Verify Cache-Control: no-cache, must-revalidate is served on all clean routes."""
        routes = [
            "/compare/calligraphr-alternative",
            "/bengali-font-maker",
            "/hindi-font-generator"
        ]
        for route in routes:
            res = self.client.get(route)
            cache_ctrl = res.headers.get("cache-control", "")
            self.assertIn("no-cache", cache_ctrl, f"{route} missing no-cache in Cache-Control: {cache_ctrl}")
            self.assertIn("must-revalidate", cache_ctrl, f"{route} missing must-revalidate in Cache-Control: {cache_ctrl}")

    # =========================================================================
    # SUITE 3: TRAILING SLASH, CASE SENSITIVITY & NON-EXISTENT ROUTE PROBING
    # =========================================================================

    def test_trailing_slash_behavior(self):
        """Empirically document and verify trailing slash behavior.
        Canonical URLs do not use trailing slashes. Requests with trailing slashes
        must not return 200 duplicate HTML without canonical grounding, and
        must return 404 cleanly without server error.
        """
        routes_with_slash = [
            "/compare/calligraphr-alternative/",
            "/bengali-font-maker/",
            "/hindi-font-generator/"
        ]
        for route in routes_with_slash:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 404, f"Route {route} expected 404 for trailing slash, got {res.status_code}")

    def test_uppercase_route_returns_404(self):
        """Empirically test uppercase paths: URL paths are case-sensitive per RFC 7230."""
        uppercase_routes = [
            "/BENGALI-FONT-MAKER",
            "/HINDI-FONT-GENERATOR",
            "/COMPARE/CALLIGRAPHR-ALTERNATIVE"
        ]
        for route in uppercase_routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 404, f"Uppercase route {route} should return 404, got {res.status_code}")

    def test_nonexistent_routes_return_404(self):
        """Arbitrary non-existent paths return 404 without leaking stack traces."""
        res = self.client.get("/non-existent-cluster-path")
        self.assertEqual(res.status_code, 404)
        res_comp = self.client.get("/compare/non-existent-subpage")
        self.assertEqual(res_comp.status_code, 404)

    def test_static_html_files_accessible(self):
        """Direct .html paths are served cleanly via StaticFiles or routes."""
        res_bn = self.client.get("/bengali-font-maker.html")
        self.assertEqual(res_bn.status_code, 200)
        res_hi = self.client.get("/hindi-font-generator.html")
        self.assertEqual(res_hi.status_code, 200)
        res_comp = self.client.get("/compare/calligraphr-alternative.html")
        self.assertEqual(res_comp.status_code, 200)

    def test_query_string_handling_and_no_reflection(self):
        """Test URL query strings (e.g. UTM tracking parameters from search engines).
        Clean routes must still respond 200 OK and not reflect arbitrary query input into HTML.
        """
        routes = [
            "/compare/calligraphr-alternative?utm_source=google&utm_medium=cpc",
            "/bengali-font-maker?ref=seo_audit&q=test_query_string",
            "/hindi-font-generator?s=devanagari"
        ]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Query string request failed for {route}")
            self.assertNotIn("test_query_string", res.text, "Arbitrary query string reflected in output (potential XSS)")

    def test_http_method_not_allowed(self):
        """POST requests to static clean routes return 405 Method Not Allowed."""
        routes = [
            "/compare/calligraphr-alternative",
            "/bengali-font-maker",
            "/hindi-font-generator"
        ]
        for route in routes:
            res = self.client.post(route)
            self.assertEqual(res.status_code, 405, f"Expected 405 Method Not Allowed for POST {route}, got {res.status_code}")

    # =========================================================================
    # SUITE 4: SCHEMA.ORG JSON-LD STRICT PARSING & GRAPH NODE VALIDATION
    # =========================================================================

    def test_compare_page_schema_graph(self):
        """Empirically test /compare/calligraphr-alternative Schema.org JSON-LD graph nodes."""
        self.assertGreaterEqual(len(self.compare_json_ld), 1, "Missing JSON-LD script tag on compare page")
        data = self.compare_json_ld[0]
        self.assertEqual(data.get("@context"), "https://schema.org")
        self.assertIn("@graph", data)
        graph = data["@graph"]
        self.assertEqual(len(graph), 4, f"Expected 4 entities in compare @graph, got {len(graph)}")

        types = {node["@type"] for node in graph}
        self.assertEqual(types, {"WebPage", "BreadcrumbList", "SoftwareApplication", "FAQPage"})

        # WebPage node
        wp = next(n for n in graph if n["@type"] == "WebPage")
        self.assertEqual(wp["url"], "https://hatekhori.onrender.com/compare/calligraphr-alternative")
        self.assertEqual(wp["isPartOf"]["@id"], "https://hatekhori.onrender.com/#website")
        self.assertIn("en", wp["inLanguage"])

        # BreadcrumbList node
        bc = next(n for n in graph if n["@type"] == "BreadcrumbList")
        items = bc["itemListElement"]
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["name"], "Home")
        self.assertEqual(items[0]["item"], "https://hatekhori.onrender.com/")
        self.assertEqual(items[1]["name"], "Compare")
        self.assertEqual(items[2]["name"], "Calligraphr Alternative")

        # SoftwareApplication node
        app_node = next(n for n in graph if n["@type"] == "SoftwareApplication")
        self.assertEqual(app_node["name"], "Hatekhori")
        self.assertEqual(app_node["alternateName"], "হাতে খড়ি")
        self.assertEqual(app_node["offers"]["price"], "0")
        self.assertEqual(app_node["offers"]["priceCurrency"], "USD")
        self.assertEqual(app_node["aggregateRating"]["ratingValue"], "4.9")
        self.assertGreaterEqual(len(app_node["featureList"]), 5)

        # FAQPage node
        faq = next(n for n in graph if n["@type"] == "FAQPage")
        faqs = faq["mainEntity"]
        self.assertGreaterEqual(len(faqs), 4)
        for q in faqs:
            self.assertEqual(q["@type"], "Question")
            self.assertTrue(q["name"].endswith("?"))
            ans = q["acceptedAnswer"]["text"]
            self.assertGreaterEqual(len(ans), 25, f"FAQ answer too short: {ans}")

    def test_bengali_page_schema_graph(self):
        """Empirically test /bengali-font-maker Schema.org JSON-LD graph nodes."""
        self.assertGreaterEqual(len(self.bengali_json_ld), 1, "Missing JSON-LD script on bengali page")
        data = self.bengali_json_ld[0]
        self.assertEqual(data.get("@context"), "https://schema.org")
        self.assertIn("@graph", data)
        graph = data["@graph"]
        self.assertGreaterEqual(len(graph), 4, f"Expected at least 4 entities in bengali @graph, got {len(graph)}")

        types = {node["@type"] for node in graph}
        self.assertTrue({"SoftwareApplication", "WebPage", "BreadcrumbList", "FAQPage"}.issubset(types))

        # SoftwareApplication
        app_node = next(n for n in graph if n["@type"] == "SoftwareApplication")
        self.assertIn("Bengali", app_node["name"])
        self.assertEqual(app_node["offers"]["price"], "0")
        self.assertIn("60-Cell", " ".join(app_node["featureList"]))
        self.assertIn("Vowels", " ".join(app_node["featureList"]))

        # WebPage
        wp = next(n for n in graph if n["@type"] == "WebPage")
        self.assertEqual(wp["url"], "https://hatekhori.onrender.com/bengali-font-maker")
        self.assertIn("bn", wp["inLanguage"])

        # BreadcrumbList
        bc = next(n for n in graph if n["@type"] == "BreadcrumbList")
        self.assertEqual(len(bc["itemListElement"]), 2)
        self.assertEqual(bc["itemListElement"][0]["item"], "https://hatekhori.onrender.com/")
        self.assertEqual(bc["itemListElement"][1]["item"], "https://hatekhori.onrender.com/bengali-font-maker")

        # FAQPage
        faq = next(n for n in graph if n["@type"] == "FAQPage")
        for q in faq["mainEntity"]:
            self.assertEqual(q["@type"], "Question")
            ans = q["acceptedAnswer"]["text"]
            self.assertGreaterEqual(len(ans), 25)

    def test_hindi_page_schema_graph(self):
        """Empirically test /hindi-font-generator Schema.org JSON-LD graph nodes."""
        self.assertGreaterEqual(len(self.hindi_json_ld), 1, "Missing JSON-LD script on hindi page")
        data = self.hindi_json_ld[0]
        self.assertEqual(data.get("@context"), "https://schema.org")
        self.assertIn("@graph", data)
        graph = data["@graph"]
        self.assertGreaterEqual(len(graph), 4, f"Expected at least 4 entities in hindi @graph, got {len(graph)}")

        types = {node["@type"] for node in graph}
        self.assertTrue({"SoftwareApplication", "WebPage", "BreadcrumbList", "FAQPage"}.issubset(types))

        # SoftwareApplication
        app_node = next(n for n in graph if n["@type"] == "SoftwareApplication")
        self.assertIn("Hindi", app_node["name"])
        self.assertEqual(app_node["offers"]["price"], "0")
        self.assertTrue(any("Shirorekha" in f or "Devanagari" in f for f in app_node["featureList"]))

        # WebPage
        wp = next(n for n in graph if n["@type"] == "WebPage")
        self.assertEqual(wp["url"], "https://hatekhori.onrender.com/hindi-font-generator")
        self.assertIn("hi", wp["inLanguage"])

        # BreadcrumbList
        bc = next(n for n in graph if n["@type"] == "BreadcrumbList")
        self.assertEqual(len(bc["itemListElement"]), 2)
        self.assertEqual(bc["itemListElement"][0]["item"], "https://hatekhori.onrender.com/")
        self.assertEqual(bc["itemListElement"][1]["item"], "https://hatekhori.onrender.com/hindi-font-generator")

        # FAQPage
        faq = next(n for n in graph if n["@type"] == "FAQPage")
        for q in faq["mainEntity"]:
            self.assertEqual(q["@type"], "Question")
            ans = q["acceptedAnswer"]["text"]
            self.assertGreaterEqual(len(ans), 25)

    # =========================================================================
    # SUITE 5: HTML TAGS, CANONICALS, GSC VERIFICATION & SOCIAL CARDS
    # =========================================================================

    def test_canonical_links_clean_and_absolute(self):
        """Check rel='canonical' on all three landing pages matches exact clean URL."""
        pages = [
            (self.compare_parser, "https://hatekhori.onrender.com/compare/calligraphr-alternative"),
            (self.bengali_parser, "https://hatekhori.onrender.com/bengali-font-maker"),
            (self.hindi_parser, "https://hatekhori.onrender.com/hindi-font-generator"),
        ]
        for parser, expected_canonical in pages:
            canonical_tags = [l.get("href") for l in parser.links if l.get("rel") == "canonical"]
            self.assertEqual(canonical_tags, [expected_canonical], f"Expected canonical {expected_canonical}, got {canonical_tags}")

    def test_dual_gsc_verification_tokens_on_all_pages(self):
        """Confirm both Google Search Console tokens exist on all three pages."""
        expected_tokens = {
            "ywFgWCyBD6nzTB9FV6Df3cGfGpcPVhtdGiTvXt_wf20",
            "google283830a3fd2e4cf3"
        }
        for name, parser in [("compare", self.compare_parser), ("bengali", self.bengali_parser), ("hindi", self.hindi_parser)]:
            tokens = {
                m.get("content") for m in parser.meta_tags
                if m.get("name") == "google-site-verification"
            }
            self.assertEqual(tokens, expected_tokens, f"{name} page GSC tokens mismatch: {tokens}")

    def test_opengraph_and_twitter_cards_presence(self):
        """Verify complete Open Graph and Twitter Card tags across all pages."""
        pages = [
            ("compare", self.compare_parser, "https://hatekhori.onrender.com/compare/calligraphr-alternative"),
            ("bengali", self.bengali_parser, "https://hatekhori.onrender.com/bengali-font-maker"),
            ("hindi", self.hindi_parser, "https://hatekhori.onrender.com/hindi-font-generator"),
        ]
        for name, parser, url in pages:
            og = {m.get("property")[3:]: m.get("content") for m in parser.meta_tags if m.get("property", "").startswith("og:")}
            tw = {m.get("name")[8:]: m.get("content") for m in parser.meta_tags if m.get("name", "").startswith("twitter:")}

            self.assertEqual(og.get("url"), url, f"{name} og:url mismatch")
            self.assertEqual(og.get("type"), "article", f"{name} og:type mismatch")
            self.assertTrue(og.get("image", "").endswith(".png"), f"{name} og:image invalid")
            self.assertEqual(tw.get("card"), "summary_large_image", f"{name} twitter:card mismatch")
            self.assertIsNotNone(tw.get("image:alt"), f"{name} missing twitter:image:alt")

    def test_html_lang_attribute(self):
        """Verify appropriate html lang attributes (en for compare, bn for Bengali, hi for Hindi)."""
        self.assertEqual(self.compare_parser.html_attrs.get("lang"), "en")
        self.assertEqual(self.bengali_parser.html_attrs.get("lang"), "bn")
        self.assertEqual(self.hindi_parser.html_attrs.get("lang"), "hi")

    def test_mobile_viewport_and_theme_color(self):
        """Verify mobile viewport and theme color on all three pages."""
        pages = [
            ("compare", self.compare_parser),
            ("bengali", self.bengali_parser),
            ("hindi", self.hindi_parser),
        ]
        for name, parser in pages:
            viewport = [m.get("content") for m in parser.meta_tags if m.get("name") == "viewport"]
            self.assertEqual(len(viewport), 1, f"{name} missing viewport meta tag")
            self.assertIn("width=device-width", viewport[0])
            self.assertIn("initial-scale=1", viewport[0])

    def test_no_insecure_mixed_content_links(self):
        """Verify no insecure http:// external resource links exist (mixed content risk)."""
        pages = [
            ("compare", self.compare_html),
            ("bengali", self.bengali_html),
            ("hindi", self.hindi_html),
        ]
        for name, html in pages:
            http_matches = re.findall(r'http://[^\s"\'<>]+', html)
            insecure = [m for m in http_matches if not m.startswith('http://schema.org')]
            self.assertEqual(insecure, [], f"{name} contains insecure HTTP resources: {insecure}")

    def test_indic_unicode_scripts_presence(self):
        """Verify that Bengali and Hindi pages actually contain native Unicode script characters."""
        # Bengali block: U+0980 to U+09FF
        bengali_chars = re.findall(r'[\u0980-\u09FF]', self.bengali_html)
        self.assertGreater(len(bengali_chars), 100, "Bengali page lacks native Bengali script characters")

        # Devanagari block: U+0900 to U+097F
        devanagari_chars = re.findall(r'[\u0900-\u097F]', self.hindi_html)
        self.assertGreater(len(devanagari_chars), 100, "Hindi page lacks native Devanagari script characters")

    # =========================================================================
    # SUITE 6: INTER-TOPIC NAVIGATION & ACCESSIBILITY TOKENS
    # =========================================================================

    def test_inter_topic_cross_links(self):
        """Verify cross-links between all M2 cluster pages and home."""
        # Compare page links to topic pages
        comp_hrefs = {a.get("href") for a in self.compare_parser.anchors if a.get("href")}
        self.assertIn("/bengali-font-maker", comp_hrefs)
        self.assertIn("/hindi-font-generator", comp_hrefs)
        self.assertTrue("/" in comp_hrefs or "../" in comp_hrefs or "https://hatekhori.onrender.com/" in comp_hrefs)

        # Bengali page links to Hindi, Compare, Home
        bn_hrefs = {a.get("href") for a in self.bengali_parser.anchors if a.get("href")}
        self.assertIn("/hindi-font-generator", bn_hrefs)
        self.assertIn("/compare/calligraphr-alternative", bn_hrefs)
        self.assertIn("/", bn_hrefs)

        # Hindi page links to Bengali, Compare, Home
        hi_hrefs = {a.get("href") for a in self.hindi_parser.anchors if a.get("href")}
        self.assertIn("/bengali-font-maker", hi_hrefs)
        self.assertIn("/compare/calligraphr-alternative", hi_hrefs)
        self.assertIn("/", hi_hrefs)

    def test_touch_target_rules_and_reduced_motion(self):
        """Verify Emil Kowalski 44px min-height rule and prefers-reduced-motion media query."""
        pages = [
            ("compare", self.compare_html),
            ("bengali", self.bengali_html),
            ("hindi", self.hindi_html),
        ]
        for name, html in pages:
            self.assertIn("min-height: 44px", html, f"{name} missing 44px min-height rule")
            self.assertIn("prefers-reduced-motion", html, f"{name} missing prefers-reduced-motion")

    def test_referenced_static_assets_exist(self):
        """Verify all stylesheet and image assets referenced by the pages exist on disk."""
        assets = [
            os.path.join(FRONTEND_DIR, "style.css"),
            os.path.join(FRONTEND_DIR, "guideline-sheet-bengali.png"),
            os.path.join(FRONTEND_DIR, "guideline-sheet-hindi.png"),
            os.path.join(FRONTEND_DIR, "google283830a3fd2e4cf3.html"),
            os.path.join(FRONTEND_DIR, "robots.txt"),
            os.path.join(FRONTEND_DIR, "sitemap.xml"),
            os.path.join(FRONTEND_DIR, "llms.txt"),
        ]
        for path in assets:
            self.assertTrue(os.path.exists(path), f"Asset missing on disk: {path}")
            self.assertGreater(os.path.getsize(path), 0, f"Asset is empty: {path}")


if __name__ == "__main__":
    unittest.main()
