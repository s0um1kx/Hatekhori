"""
Milestone 1 Empirical Challenger Verification Test Suite
Targets: frontend/index.html & FastAPI static serving
Author: m1_challenger_1 (Empirical Challenger: Critic & Specialist)
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
INDEX_PATH = os.path.join(ROOT_DIR, "frontend", "index.html")
GSC_FILE_PATH = os.path.join(ROOT_DIR, "frontend", "google283830a3fd2e4cf3.html")
OG_IMAGE_PATH = os.path.join(ROOT_DIR, "frontend", "guideline-sheet-bengali.png")

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

    def get(self, path: str, headers: dict[str, str] | None = None) -> ASGIResponse:
        import asyncio
        req_headers = []
        if headers:
            for k, v in headers.items():
                req_headers.append((k.lower().encode("latin1"), v.encode("latin1")))

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("latin1"),
            "query_string": b"",
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
                    response_headers[k.decode("latin1")] = v.decode("latin1")
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.app(scope, receive, send))
        finally:
            loop.close()

        return ASGIResponse(response_status, response_headers, bytes(response_body))


class MetaTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta_tags = []
        self.links = []
        self.scripts = []
        self.headings = []
        self.title = None
        self._in_title = False
        self._in_script = False
        self._curr_heading = None
        self._curr_script_attrs = {}
        self._curr_script_content = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "meta":
            self.meta_tags.append(attr_dict)
        elif tag == "link":
            self.links.append(attr_dict)
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


class EmpiricalM1ChallengerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            cls.raw_html = f.read()

        cls.parser = MetaTagParser()
        cls.parser.feed(cls.raw_html)

        # Extract JSON-LD script
        cls.json_ld_blocks = [
            s["content"] for s in cls.parser.scripts 
            if s["attrs"].get("type") == "application/ld+json"
        ]
        cls.client = ASGIClient(app)

    # =========================================================================
    # SUITE 1: JSON-LD SYNTAX & SCHEMA.ORG PROPERTY VALIDATION
    # =========================================================================

    def test_json_ld_presence_and_syntax(self):
        """Empirically parse JSON-LD with json.loads and test strict JSON compliance."""
        self.assertGreater(len(self.json_ld_blocks), 0, "No application/ld+json script tags found")
        raw_json = self.json_ld_blocks[0].strip()
        try:
            data = json.loads(raw_json)
        except Exception as e:
            self.fail(f"JSON-LD syntax error: {e}")

        self.assertIsInstance(data, dict, "Root JSON-LD is not a JSON object")
        self.assertEqual(data.get("@context"), "https://schema.org", "Context must be https://schema.org")
        self.assertIn("@graph", data, "Root JSON-LD must contain @graph")
        self.assertIsInstance(data["@graph"], list, "@graph must be a list of entities")
        self.assertEqual(len(data["@graph"]), 3, f"Expected 3 entities in @graph, found {len(data['@graph'])}")

    def test_schema_website_entity_properties(self):
        """Stress-test WebSite entity types and required attributes."""
        data = json.loads(self.json_ld_blocks[0].strip())
        sites = [e for e in data["@graph"] if e.get("@type") == "WebSite"]
        self.assertEqual(len(sites), 1, "Must contain exactly one WebSite entity")
        site = sites[0]

        self.assertEqual(site.get("@id"), "https://hatekhori.onrender.com/#website")
        self.assertEqual(site.get("url"), "https://hatekhori.onrender.com/")
        self.assertEqual(site.get("name"), "Hatekhori")
        self.assertIsInstance(site.get("alternateName"), list)
        self.assertIn("হাতে খড়ি", site.get("alternateName"))
        self.assertIsInstance(site.get("inLanguage"), list)
        self.assertEqual(set(site.get("inLanguage")), {"en", "bn", "hi"})
        self.assertIsInstance(site.get("description"), str)
        self.assertGreater(len(site.get("description")), 30)

    def test_schema_software_application_properties(self):
        """Stress-test SoftwareApplication entity properties, rating, and offer structure."""
        data = json.loads(self.json_ld_blocks[0].strip())
        apps = [e for e in data["@graph"] if e.get("@type") == "SoftwareApplication"]
        self.assertEqual(len(apps), 1, "Must contain exactly one SoftwareApplication entity")
        app = apps[0]

        # Basic properties
        self.assertEqual(app.get("@id"), "https://hatekhori.onrender.com/#software")
        self.assertEqual(app.get("name"), "Hatekhori")
        self.assertEqual(app.get("alternateName"), "হাতে খড়ি")
        self.assertEqual(app.get("applicationCategory"), "MultimediaApplication")
        self.assertIn("Web", app.get("operatingSystem"))
        self.assertTrue(app.get("image", "").startswith("https://hatekhori.onrender.com/"))
        self.assertIsInstance(app.get("inLanguage"), list)

        # Offers
        offers = app.get("offers")
        self.assertIsInstance(offers, dict, "offers must be an Offer object")
        self.assertEqual(offers.get("@type"), "Offer")
        self.assertIn(offers.get("price"), ["0", 0, "0.00"])
        self.assertEqual(offers.get("priceCurrency"), "USD")
        self.assertEqual(offers.get("availability"), "https://schema.org/InStock")

        # FeatureList
        features = app.get("featureList")
        self.assertIsInstance(features, list)
        self.assertGreaterEqual(len(features), 5)
        for f in features:
            self.assertIsInstance(f, str)
            self.assertGreater(len(f), 5)

        # AggregateRating
        rating = app.get("aggregateRating")
        self.assertIsInstance(rating, dict)
        self.assertEqual(rating.get("@type"), "AggregateRating")
        rating_val = float(rating.get("ratingValue"))
        self.assertTrue(1.0 <= rating_val <= 5.0)
        review_count = int(rating.get("reviewCount"))
        self.assertGreater(review_count, 0)
        self.assertEqual(int(rating.get("bestRating")), 5)
        self.assertEqual(int(rating.get("worstRating")), 1)

    def test_schema_faq_page_entity_properties(self):
        """Stress-test FAQPage entity and all Q&A nodes."""
        data = json.loads(self.json_ld_blocks[0].strip())
        faqs = [e for e in data["@graph"] if e.get("@type") == "FAQPage"]
        self.assertEqual(len(faqs), 1, "Must contain exactly one FAQPage entity")
        faq = faqs[0]

        self.assertEqual(faq.get("@id"), "https://hatekhori.onrender.com/#faq")
        items = faq.get("mainEntity")
        self.assertIsInstance(items, list, "mainEntity must be a list of questions")
        self.assertGreaterEqual(len(items), 3, "FAQPage should contain at least 3 Q&A pairs")

        for idx, item in enumerate(items):
            self.assertEqual(item.get("@type"), "Question", f"Item {idx} @type is not Question")
            q_name = item.get("name")
            self.assertIsInstance(q_name, str, f"Item {idx} question name is not string")
            self.assertGreater(len(q_name), 10, f"Item {idx} question '{q_name}' too short")
            self.assertTrue(q_name.endswith("?"), f"Item {idx} question should end with '?'")

            ans = item.get("acceptedAnswer")
            self.assertIsInstance(ans, dict, f"Item {idx} acceptedAnswer is not an object")
            self.assertEqual(ans.get("@type"), "Answer")
            ans_text = ans.get("text")
            self.assertIsInstance(ans_text, str)
            self.assertGreater(len(ans_text), 30, f"Item {idx} answer too short")

    # =========================================================================
    # SUITE 2: OPEN GRAPH & TWITTER CARD REGEX VS DOM EXTRACTION
    # =========================================================================

    def test_opengraph_regex_extraction(self):
        """Simulate fast regex scraper (e.g. social crawlers without full DOM parsers)."""
        html = self.raw_html
        og_tags = {}
        for match in re.finditer(r'<meta\s+property=["\']og:([a-zA-Z0-9_:]+)["\']\s+content=["\']([^"\']*)["\']', html):
            prop = match.group(1)
            val = match.group(2)
            if prop in og_tags:
                if not isinstance(og_tags[prop], list):
                    og_tags[prop] = [og_tags[prop]]
                og_tags[prop].append(val)
            else:
                og_tags[prop] = val

        for match in re.finditer(r'<meta\s+content=["\']([^"\']*)["\']\s+property=["\']og:([a-zA-Z0-9_:]+)["\']', html):
            prop = match.group(2)
            val = match.group(1)
            og_tags[prop] = val

        self.assertEqual(og_tags.get("type"), "website")
        self.assertEqual(og_tags.get("url"), "https://hatekhori.onrender.com/")
        self.assertEqual(og_tags.get("title"), "Hatekhori — Your handwriting, set as type")
        self.assertIn("physical handwriting", og_tags.get("description", ""))
        self.assertEqual(og_tags.get("image"), "https://hatekhori.onrender.com/guideline-sheet-bengali.png")
        self.assertEqual(og_tags.get("image:width"), "1240")
        self.assertEqual(og_tags.get("image:height"), "1754")
        self.assertEqual(og_tags.get("image:type"), "image/png")
        self.assertEqual(og_tags.get("locale"), "en_US")
        self.assertIsInstance(og_tags.get("locale:alternate"), list)
        self.assertEqual(set(og_tags.get("locale:alternate")), {"bn_BD", "hi_IN"})

    def test_twitter_card_regex_extraction(self):
        """Simulate Twitterbot card tag extraction via regex."""
        html = self.raw_html
        tw_tags = {}
        for match in re.finditer(r'<meta\s+name=["\']twitter:([a-zA-Z0-9_:]+)["\']\s+content=["\']([^"\']*)["\']', html):
            tw_tags[match.group(1)] = match.group(2)

        self.assertEqual(tw_tags.get("card"), "summary_large_image")
        self.assertEqual(tw_tags.get("title"), "Hatekhori — Your handwriting, set as type")
        self.assertEqual(tw_tags.get("image"), "https://hatekhori.onrender.com/guideline-sheet-bengali.png")
        self.assertGreater(len(tw_tags.get("description", "")), 40)
        self.assertIn("Hatekhori", tw_tags.get("image:alt", ""))

    def test_dom_vs_regex_metadata_consistency(self):
        """Verify that parsed DOM attributes perfectly match regex extractions."""
        dom_og = {}
        dom_tw = {}
        for meta in self.parser.meta_tags:
            prop = meta.get("property")
            name = meta.get("name")
            content = meta.get("content")
            if prop and prop.startswith("og:"):
                k = prop[3:]
                if k in dom_og:
                    if not isinstance(dom_og[k], list):
                        dom_og[k] = [dom_og[k]]
                    dom_og[k].append(content)
                else:
                    dom_og[k] = content
            if name and name.startswith("twitter:"):
                dom_tw[name[8:]] = content

        self.assertEqual(dom_og.get("type"), "website")
        self.assertEqual(dom_tw.get("card"), "summary_large_image")
        self.assertEqual(dom_og.get("image"), dom_tw.get("image"))
        self.assertEqual(dom_og.get("title"), dom_tw.get("title"))

    # =========================================================================
    # SUITE 3: GOOGLE SEARCH CONSOLE VERIFICATION TOKENS
    # =========================================================================

    def test_gsc_verification_tokens_in_html(self):
        """Confirm GSC verification meta tags exist unmangled."""
        expected_tokens = {
            "ywFgWCyBD6nzTB9FV6Df3cGfGpcPVhtdGiTvXt_wf20",
            "google283830a3fd2e4cf3"
        }
        gsc_metas = [
            m.get("content") for m in self.parser.meta_tags 
            if m.get("name") == "google-site-verification"
        ]
        self.assertEqual(set(gsc_metas), expected_tokens, f"GSC tokens mismatch: {gsc_metas}")

    def test_gsc_verification_file_intact(self):
        """Confirm standalone google283830a3fd2e4cf3.html file exists and has correct content."""
        self.assertTrue(os.path.exists(GSC_FILE_PATH), f"GSC verification HTML file missing at {GSC_FILE_PATH}")
        with open(GSC_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
        self.assertTrue(content.startswith("google-site-verification: google283830a3fd2e4cf3.html"))

    def test_og_image_asset_exists_on_disk(self):
        """Confirm that the OG/Twitter image asset actually exists in frontend/."""
        self.assertTrue(os.path.exists(OG_IMAGE_PATH), f"OG image asset missing at {OG_IMAGE_PATH}")
        size = os.path.getsize(OG_IMAGE_PATH)
        self.assertGreater(size, 10000, f"OG image asset unexpectedly tiny ({size} bytes)")

    # =========================================================================
    # SUITE 4: CRAWLER EXTRACTION SIMULATION & HTTP CLOAKING CHECKS
    # =========================================================================

    def test_simulated_googlebot_crawl(self):
        """Simulate Googlebot crawler indexing pipeline via HTTP client."""
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        res = self.client.get("/", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))

        # 1. Document title
        self.assertIsNotNone(self.parser.title)
        self.assertEqual(self.parser.title.strip(), "Hatekhori — Your handwriting, set as type")

        # 2. Meta description
        desc_meta = [m.get("content") for m in self.parser.meta_tags if m.get("name") == "description"]
        self.assertEqual(len(desc_meta), 1)
        self.assertTrue(100 <= len(desc_meta[0]) <= 200, f"Description length {len(desc_meta[0])} outside bounds")

        # 3. Canonical link
        canonical = [l.get("href") for l in self.parser.links if l.get("rel") == "canonical"]
        self.assertEqual(canonical, ["https://hatekhori.onrender.com/"])

        # 4. Viewport tag
        viewport = [m.get("content") for m in self.parser.meta_tags if m.get("name") == "viewport"]
        self.assertEqual(len(viewport), 1)
        self.assertIn("width=device-width", viewport[0])

        # 5. Charset within first 1024 bytes
        first_1024 = self.raw_html[:1024]
        self.assertTrue('<meta charset="utf-8"' in first_1024 or '<meta charset="UTF-8"' in first_1024)

    def test_simulated_social_crawlers_get_200(self):
        """Simulate social crawlers (Twitterbot, Facebookexternalhit, Slackbot, LinkedInBot)."""
        user_agents = [
            "Twitterbot/1.0",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com)",
            "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)",
            "Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"
        ]
        for ua in user_agents:
            res = self.client.get("/", headers={"User-Agent": ua})
            self.assertEqual(res.status_code, 200, f"Bot {ua} received non-200 status {res.status_code}")
            self.assertEqual(res.text, self.raw_html, f"Cloaking detected: content served to {ua} differs from raw_html")

    def test_simulated_social_card_snippet(self):
        """Simulate social card generator (OpenGraph / Twitter)."""
        og = {m.get("property")[3:]: m.get("content") for m in self.parser.meta_tags if m.get("property", "").startswith("og:")}
        card_preview = {
            "title": og.get("title"),
            "description": og.get("description"),
            "image": og.get("image"),
            "url": og.get("url"),
            "site_name": og.get("site_name")
        }
        self.assertIsNotNone(card_preview["title"])
        self.assertIsNotNone(card_preview["description"])
        self.assertTrue(card_preview["image"].endswith(".png"))
        self.assertEqual(card_preview["url"], "https://hatekhori.onrender.com/")

    def test_simulated_ai_bot_answer_grounding(self):
        """Simulate AI Bot (Perplexity/ChatGPT) knowledge extraction from homepage."""
        data = json.loads(self.json_ld_blocks[0].strip())
        app_node = [e for e in data["@graph"] if e.get("@type") == "SoftwareApplication"][0]
        # Verify AI grounding facts
        self.assertEqual(app_node.get("offers", {}).get("price"), "0")
        self.assertEqual(app_node.get("offers", {}).get("priceCurrency"), "USD")
        features = app_node.get("featureList", [])
        self.assertTrue(any("Bengali" in f for f in features))
        self.assertTrue(any("Hindi" in f for f in features))
        self.assertTrue(any("Zero Account" in f for f in features))
        self.assertTrue(any("EXIF" in f for f in features))

    # =========================================================================
    # SUITE 5: INTERNAL LINKING TOPOLOGY & DEAD LINK AUDIT
    # =========================================================================

    def test_no_dead_relative_prd_link(self):
        """Empirically prove the old 404 /docs/PRD.md defect is completely absent."""
        self.assertNotIn('href="/docs/PRD.md"', self.raw_html)
        self.assertNotIn("href='/docs/PRD.md'", self.raw_html)

    def test_internal_links_topology(self):
        """Verify presence of key discoverability links in navigation and footer."""
        required_links = [
            "/bengali-font-maker",
            "/hindi-font-generator",
            "/compare/calligraphr-alternative",
            "/llms.txt",
            "/sitemap.xml",
            "#how",
            "#specimen"
        ]
        for link in required_links:
            self.assertIn(f'href="{link}"', self.raw_html, f"Missing required internal link: {link}")

    # =========================================================================
    # SUITE 6: CSS / ACCESSIBILITY / DESIGN COMPLIANCE
    # =========================================================================

    def test_touch_target_rules_and_brand_tokens(self):
        """Verify that Emil Kowalski design tokens and 44px min-height rules are in style block."""
        self.assertIn("--brand-stage: #F2ECE1;", self.raw_html)
        self.assertIn("--brand-ink: #0034D3;", self.raw_html)
        self.assertIn("min-height: 44px;", self.raw_html)
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.raw_html)

    def test_no_insecure_http_assets(self):
        """Empirically verify no insecure http:// asset URLs are loaded (mixed content)."""
        http_matches = re.findall(r'http://[^\s"\'<>]+', self.raw_html)
        insecure = [m for m in http_matches if not m.startswith('http://schema.org')]
        self.assertEqual(insecure, [], f"Insecure HTTP URLs detected: {insecure}")


if __name__ == "__main__":
    unittest.main()
