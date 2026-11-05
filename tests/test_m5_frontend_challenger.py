"""Tier 5 Adversarial Coverage Hardening Suite: Frontend, Discoverability & Crawler Matrix.

Author: Milestone 5 Challenger 2 (m5_challenger_2)
Role: Empirical Challenger (Critic & Specialist)

Target Files:
  - frontend/index.html
  - frontend/compare/calligraphr-alternative.html
  - frontend/bengali-font-maker.html
  - frontend/hindi-font-generator.html
  - frontend/robots.txt
  - frontend/sitemap.xml
  - frontend/llms.txt
  - frontend/google283830a3fd2e4cf3.html

Coverage Scope:
  1. Schema.org JSON-LD knowledge graph entity relationships and URI anchor stability across all 4 pages
  2. XML sitemap 0.9 schema validation with defusedxml / xml.etree (loc, lastmod, changefreq, priority, zero invalid entities)
  3. Robots.txt RFC 9309 rules across 35+ crawler user-agent strings (Disallow on internal dirs vs Allow on public pages)
  4. Google Search Console (GSC) verification permanence (standalone file byte count == 54, meta tags present on all 4 pages)
  5. Mobile viewport, OpenGraph, and Twitter tags across mobile breakpoints and responsive design tokens
  6. LLMs.txt GEO citability, direct answer summary, and canonical domain alignment
"""

import datetime
import html.parser
import json
import os
import re
import sys
import unittest
import urllib.parse
import urllib.robotparser
from pathlib import Path

# Try importing defusedxml if available, otherwise fall back to xml.etree.ElementTree
try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# Safe Unicode output for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
sys.path.insert(0, str(ROOT_DIR))

# Import ASGI client from test_seo_discoverability
from tests.test_seo_discoverability import client  # noqa: E402


# ---------------------------------------------------------------------------
# White-Box HTML Parser Helper
# ---------------------------------------------------------------------------
class HTMLMetaTagParser(html.parser.HTMLParser):
    """Robust HTML parser extracting metadata, links, and script tags."""

    def __init__(self):
        super().__init__()
        self.meta_tags: list[dict[str, str]] = []
        self.link_tags: list[dict[str, str]] = []
        self.script_tags: list[dict[str, str]] = []
        self.in_script: bool = False
        self.current_script_attrs: dict[str, str] = {}
        self.script_data: list[str] = []
        self.in_head: bool = False
        self.head_closed: bool = False
        self.head_meta_tags: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attr_dict = {k.lower(): (v if v is not None else "") for k, v in attrs}
        if tag.lower() == "head":
            self.in_head = True
        elif tag.lower() == "meta":
            self.meta_tags.append(attr_dict)
            if self.in_head and not self.head_closed:
                self.head_meta_tags.append(attr_dict)
        elif tag.lower() == "link":
            self.link_tags.append(attr_dict)
        elif tag.lower() == "script":
            self.in_script = True
            self.current_script_attrs = attr_dict
            self.script_data = []

    def handle_endtag(self, tag: str):
        if tag.lower() == "head":
            self.in_head = False
            self.head_closed = True
        elif tag.lower() == "script" and self.in_script:
            self.in_script = False
            data = "".join(self.script_data)
            self.script_tags.append({
                "attrs": self.current_script_attrs,
                "content": data,
            })

    def handle_data(self, data: str):
        if self.in_script:
            self.script_data.append(data)


def parse_html_document(html_text: str) -> HTMLMetaTagParser:
    parser = HTMLMetaTagParser()
    parser.feed(html_text)
    return parser


# ---------------------------------------------------------------------------
# Test Suite 1: Schema.org Knowledge Graph & Entity Relationships
# ---------------------------------------------------------------------------
class TestSchemaOrgKnowledgeGraphIntegrity(unittest.TestCase):
    """Stress-test Schema.org JSON-LD knowledge graphs, entity relationships, and URI anchor stability."""

    PAGES = [
        ("frontend/index.html", "https://hatekhori.onrender.com/"),
        ("frontend/compare/calligraphr-alternative.html", "https://hatekhori.onrender.com/compare/calligraphr-alternative"),
        ("frontend/bengali-font-maker.html", "https://hatekhori.onrender.com/bengali-font-maker"),
        ("frontend/hindi-font-generator.html", "https://hatekhori.onrender.com/hindi-font-generator"),
    ]

    def _get_page_json_ld(self, relative_path: str) -> dict:
        file_path = ROOT_DIR / relative_path
        self.assertTrue(file_path.is_file(), f"Target file {file_path} must exist.")
        content = file_path.read_text(encoding="utf-8")
        parser = parse_html_document(content)
        json_ld_scripts = [s for s in parser.script_tags if s["attrs"].get("type") == "application/ld+json"]
        self.assertGreaterEqual(len(json_ld_scripts), 1, f"{relative_path} must contain at least 1 ld+json script.")
        try:
            return json.loads(json_ld_scripts[0]["content"])
        except json.JSONDecodeError as exc:
            self.fail(f"Invalid JSON-LD in {relative_path}: {exc}")

    def test_json_ld_context_is_https_schema_org(self):
        """All 4 pages must specify @context == 'https://schema.org'."""
        for rel_path, _ in self.PAGES:
            with self.subTest(page=rel_path):
                data = self._get_page_json_ld(rel_path)
                self.assertEqual(data.get("@context"), "https://schema.org")

    def test_json_ld_root_contains_graph_array(self):
        """All 4 pages must encapsulate entities inside a non-empty @graph array."""
        for rel_path, _ in self.PAGES:
            with self.subTest(page=rel_path):
                data = self._get_page_json_ld(rel_path)
                self.assertIn("@graph", data)
                self.assertIsInstance(data["@graph"], list)
                self.assertGreaterEqual(len(data["@graph"]), 3)

    def test_homepage_knowledge_graph_entities_and_anchors(self):
        """Homepage graph must contain WebSite, SoftwareApplication, and FAQPage with stable URI anchors."""
        data = self._get_page_json_ld("frontend/index.html")
        graph = {item.get("@type"): item for item in data["@graph"]}

        self.assertIn("WebSite", graph)
        self.assertIn("SoftwareApplication", graph)
        self.assertIn("FAQPage", graph)

        # URI anchor stability
        self.assertEqual(graph["WebSite"]["@id"], "https://hatekhori.onrender.com/#website")
        self.assertEqual(graph["SoftwareApplication"]["@id"], "https://hatekhori.onrender.com/#software")
        self.assertEqual(graph["FAQPage"]["@id"], "https://hatekhori.onrender.com/#faq")

        # Multi-language array in WebSite
        self.assertIn("inLanguage", graph["WebSite"])
        self.assertListEqual(sorted(graph["WebSite"]["inLanguage"]), ["bn", "en", "hi"])

    def test_landing_pages_graph_entities_and_anchors(self):
        """All 3 subpages must contain BreadcrumbList, WebPage, SoftwareApplication, and FAQPage."""
        for rel_path, canonical_url in self.PAGES[1:]:
            with self.subTest(page=rel_path):
                data = self._get_page_json_ld(rel_path)
                graph = {item.get("@type"): item for item in data["@graph"]}

                self.assertIn("WebPage", graph)
                self.assertIn("BreadcrumbList", graph)
                self.assertIn("SoftwareApplication", graph)
                self.assertIn("FAQPage", graph)

                # Check stable anchors
                self.assertEqual(graph["WebPage"]["@id"], f"{canonical_url}#webpage")
                self.assertEqual(graph["BreadcrumbList"]["@id"], f"{canonical_url}#breadcrumb")
                self.assertEqual(graph["FAQPage"]["@id"], f"{canonical_url}#faq")

    def test_graph_entity_relationships_is_part_of_and_breadcrumb(self):
        """WebPage entities must reference #website via isPartOf and #breadcrumb via breadcrumb."""
        for rel_path, canonical_url in self.PAGES[1:]:
            with self.subTest(page=rel_path):
                data = self._get_page_json_ld(rel_path)
                webpage = next((x for x in data["@graph"] if x.get("@type") == "WebPage"), None)
                self.assertIsNotNone(webpage)

                # isPartOf reference to site root
                self.assertIn("isPartOf", webpage)
                self.assertEqual(webpage["isPartOf"].get("@id"), "https://hatekhori.onrender.com/#website")

                # breadcrumb reference to local BreadcrumbList
                self.assertIn("breadcrumb", webpage)
                self.assertEqual(webpage["breadcrumb"].get("@id"), f"{canonical_url}#breadcrumb")

    def test_zero_orphan_entity_references_in_knowledge_graph(self):
        """Every @id referenced within a page's graph must resolve to a declared entity or the known #website root."""
        known_global_ids = {
            "https://hatekhori.onrender.com/#website",
            "https://hatekhori.onrender.com/#software",
            "https://hatekhori.onrender.com/#faq",
        }
        for rel_path, _ in self.PAGES:
            with self.subTest(page=rel_path):
                data = self._get_page_json_ld(rel_path)
                local_ids = {item["@id"] for item in data["@graph"] if "@id" in item}
                accessible_ids = local_ids | known_global_ids

                # Find all referenced @id pointers
                def find_id_refs(obj):
                    refs = []
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k != "@id" and isinstance(v, dict) and "@id" in v:
                                refs.append(v["@id"])
                            else:
                                refs.extend(find_id_refs(v))
                    elif isinstance(obj, list):
                        for item in obj:
                            refs.extend(find_id_refs(item))
                    return refs

                id_refs = find_id_refs(data["@graph"])
                for ref in id_refs:
                    self.assertIn(
                        ref,
                        accessible_ids,
                        f"Dangling reference '{ref}' found in {rel_path} knowledge graph.",
                    )

    def test_breadcrumb_list_hierarchy_and_position_sequence(self):
        """BreadcrumbList must have strict 1-based sequential integers and point to valid HTTPS URLs."""
        for rel_path, canonical_url in self.PAGES[1:]:
            with self.subTest(page=rel_path):
                data = self._get_page_json_ld(rel_path)
                bcl = next((x for x in data["@graph"] if x.get("@type") == "BreadcrumbList"), None)
                self.assertIsNotNone(bcl)
                items = bcl.get("itemListElement", [])
                self.assertGreaterEqual(len(items), 2)

                # Check position sequence (1, 2, ...)
                positions = [item.get("position") for item in items]
                expected_positions = list(range(1, len(items) + 1))
                self.assertListEqual(positions, expected_positions)

                # Position 1 must always be Home (https://hatekhori.onrender.com/)
                self.assertEqual(items[0].get("item"), "https://hatekhori.onrender.com/")

                # Final position must point to the current page canonical URL
                self.assertEqual(items[-1].get("item"), canonical_url)

    def test_software_application_ratings_and_free_offers(self):
        """SoftwareApplication across all pages must specify 100% free price '0' and valid rating bounds."""
        for rel_path, _ in self.PAGES:
            with self.subTest(page=rel_path):
                data = self._get_page_json_ld(rel_path)
                app_entity = next((x for x in data["@graph"] if x.get("@type") == "SoftwareApplication"), None)
                self.assertIsNotNone(app_entity)

                # Offers
                offers = app_entity.get("offers", {})
                self.assertEqual(offers.get("@type"), "Offer")
                self.assertEqual(str(offers.get("price")), "0")
                self.assertEqual(offers.get("priceCurrency"), "USD")
                self.assertEqual(offers.get("availability"), "https://schema.org/InStock")

                # Ratings
                rating = app_entity.get("aggregateRating", {})
                self.assertEqual(rating.get("@type"), "AggregateRating")
                rating_val = float(rating.get("ratingValue", 0))
                self.assertGreaterEqual(rating_val, 1.0)
                self.assertLessEqual(rating_val, 5.0)
                review_count = int(rating.get("reviewCount", 0))
                self.assertGreater(review_count, 10)

    def test_faq_page_questions_answers_and_hygiene(self):
        """FAQPage entities must contain >= 4 valid Q&A pairs with zero placeholder tokens."""
        forbidden_tokens = ["TODO", "TBD", "FIXME", "LOREM", "IPSUM", "PLACEHOLDER"]
        for rel_path, _ in self.PAGES:
            with self.subTest(page=rel_path):
                data = self._get_page_json_ld(rel_path)
                faq = next((x for x in data["@graph"] if x.get("@type") == "FAQPage"), None)
                self.assertIsNotNone(faq)
                questions = faq.get("mainEntity", [])
                self.assertGreaterEqual(len(questions), 4)

                for q in questions:
                    self.assertEqual(q.get("@type"), "Question")
                    q_name = q.get("name", "")
                    self.assertTrue(q_name.strip().endswith("?"), f"Question '{q_name}' should end with '?'")
                    answer = q.get("acceptedAnswer", {})
                    self.assertEqual(answer.get("@type"), "Answer")
                    ans_text = answer.get("text", "")
                    self.assertGreater(len(ans_text), 30)

                    # Hygiene check
                    for tok in forbidden_tokens:
                        self.assertNotIn(tok, q_name.upper())
                        self.assertNotIn(tok, ans_text.upper())


# ---------------------------------------------------------------------------
# Test Suite 2: XML Sitemap 0.9 Schema Validation
# ---------------------------------------------------------------------------
class TestSitemapXmlSchemaAndValidation(unittest.TestCase):
    """Stress-test frontend/sitemap.xml with XML parsing, schema constraint checks, and entity hygiene."""

    @classmethod
    def setUpClass(cls):
        cls.sitemap_file = FRONTEND_DIR / "sitemap.xml"
        cls.assertTrue(cls.sitemap_file.is_file(), "frontend/sitemap.xml must exist.")
        cls.raw_bytes = cls.sitemap_file.read_bytes()
        cls.raw_text = cls.sitemap_file.read_text(encoding="utf-8")
        cls.tree = ET.fromstring(cls.raw_text)

    def test_sitemap_xml_declaration_line(self):
        """Line 1 of sitemap.xml must be a well-formed XML declaration."""
        lines = self.raw_text.splitlines()
        self.assertGreater(len(lines), 0)
        self.assertTrue(
            lines[0].strip().startswith("<?xml") and lines[0].strip().endswith("?>"),
            "Line 1 must be XML declaration.",
        )
        self.assertIn('encoding="UTF-8"', lines[0])

    def test_sitemap_root_namespace_and_tag(self):
        """Root tag must be urlset with sitemaps.org/schemas/sitemap/0.9 namespace."""
        expected_tag = "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"
        self.assertEqual(self.tree.tag, expected_tag)

    def test_sitemap_child_elements_strictly_url_tag(self):
        """All child elements of <urlset> must strictly be <url> tags."""
        expected_child_tag = "{http://www.sitemaps.org/schemas/sitemap/0.9}url"
        for child in self.tree:
            self.assertEqual(
                child.tag,
                expected_child_tag,
                f"Unexpected child tag '{child.tag}' in <urlset>.",
            )

    def test_sitemap_url_element_strict_subelement_schema(self):
        """Inside each <url>, only <loc>, <lastmod>, <changefreq>, and <priority> are allowed."""
        ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
        allowed_subtags = {f"{{{ns}}}{sub}" for sub in ["loc", "lastmod", "changefreq", "priority"]}
        allowed_changefreq = {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}

        urls = self.tree.findall(f"{{{ns}}}url")
        self.assertEqual(len(urls), 7, "Sitemap must contain exactly 7 URLs.")

        for i, url_elem in enumerate(urls):
            subtag_names = {sub.tag for sub in url_elem}
            self.assertTrue(
                subtag_names.issubset(allowed_subtags),
                f"URL entry {i} contains invalid tags: {subtag_names - allowed_subtags}",
            )

            # Check <loc>
            loc_elem = url_elem.find(f"{{{ns}}}loc")
            self.assertIsNotNone(loc_elem, f"Entry {i} missing <loc>")
            self.assertTrue(loc_elem.text.startswith("https://hatekhori.onrender.com/"))

            # Check <lastmod>
            lastmod_elem = url_elem.find(f"{{{ns}}}lastmod")
            self.assertIsNotNone(lastmod_elem, f"Entry {i} missing <lastmod>")
            try:
                dt = datetime.datetime.strptime(lastmod_elem.text.strip(), "%Y-%m-%d").date()
                self.assertGreaterEqual(dt.year, 2026)
            except ValueError:
                self.fail(f"Entry {i} <lastmod> '{lastmod_elem.text}' is not valid ISO 8601 YYYY-MM-DD.")

            # Check <changefreq>
            cf_elem = url_elem.find(f"{{{ns}}}changefreq")
            self.assertIsNotNone(cf_elem, f"Entry {i} missing <changefreq>")
            self.assertIn(cf_elem.text.strip(), allowed_changefreq)

            # Check <priority>
            prio_elem = url_elem.find(f"{{{ns}}}priority")
            self.assertIsNotNone(prio_elem, f"Entry {i} missing <priority>")
            try:
                prio = float(prio_elem.text.strip())
                self.assertGreaterEqual(prio, 0.0)
                self.assertLessEqual(prio, 1.0)
            except ValueError:
                self.fail(f"Entry {i} <priority> '{prio_elem.text}' is not float in [0.0, 1.0]")

    def test_sitemap_zero_duplicate_loc_entries(self):
        """Sitemap must contain 0 duplicate <loc> URLs."""
        ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
        locs = [elem.text.strip() for elem in self.tree.findall(f".//{{{ns}}}loc")]
        self.assertEqual(len(locs), len(set(locs)), "Sitemap contains duplicate <loc> tags.")

    def test_sitemap_zero_unescaped_xml_entities(self):
        """Sitemap XML must not contain unescaped entity characters in text nodes."""
        raw = self.raw_text
        # Stripping valid tags and check for dangling &
        no_tags = re.sub(r"<[^>]+>", "", raw)
        dangling_amp = re.findall(r"&(?!(amp|lt|gt|quot|apos);)", no_tags)
        self.assertEqual(len(dangling_amp), 0, f"Found unescaped '&' in sitemap: {dangling_amp}")

    def test_sitemap_all_urls_resolve_200_via_asgi(self):
        """All 7 declared URLs in sitemap must return HTTP 200 OK via the ASGI test client."""
        ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
        locs = [elem.text.strip() for elem in self.tree.findall(f".//{{{ns}}}loc")]
        for url in locs:
            parsed = urllib.parse.urlparse(url)
            req_path = parsed.path if parsed.path else "/"
            with self.subTest(url=url):
                res = client.get(req_path)
                self.assertEqual(res.status_code, 200, f"URL {url} returned {res.status_code}")


# ---------------------------------------------------------------------------
# Test Suite 3: Robots.txt RFC 9309 Rules Across 35+ Crawler User-Agents
# ---------------------------------------------------------------------------
class TestRobotsTxtRFC9309CrawlerMatrix(unittest.TestCase):
    """Stress-test frontend/robots.txt across 35+ distinct web, AI, search, and social crawler user-agents."""

    CRAWLERS_35 = [
        # Major Search Engines (10)
        "Googlebot",
        "Bingbot",
        "Slurp",
        "DuckDuckBot",
        "Baiduspider",
        "YandexBot",
        "Sogou spider",
        "NaverBot",
        "PetalBot",
        "Qwantify",
        # AI / LLM / Answer Engines (15)
        "GPTBot",
        "ChatGPT-User",
        "PerplexityBot",
        "ClaudeBot",
        "Claude-Web",
        "anthropic-ai",
        "Google-Extended",
        "Applebot",
        "Applebot-Extended",
        "Amazonbot",
        "CCBot",
        "Cohere-ai",
        "Bytespider",
        "YouBot",
        "Diffbot",
        # Social Scrapers & Link Previews (8)
        "Twitterbot",
        "facebookexternalhit",
        "Facebot",
        "LinkedInBot",
        "Pinterestbot",
        "Discordbot",
        "TelegramBot",
        "WhatsApp",
        # Generic & Wildcard (2)
        "*",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    ]

    DISALLOWED_PATHS = [
        "/uploads/",
        "/uploads/test_sheet.png",
        "/uploads/nested/image.jpg",
        "/output/",
        "/output/hatekhori_font.otf",
        "/output/uuid_1234/font.woff2",
        "/download-font/",
        "/download-font/font-sample-12345",
        "/download-font/export.ttf",
    ]

    ALLOWED_PATHS = [
        "/",
        "/compare/calligraphr-alternative",
        "/bengali-font-maker",
        "/hindi-font-generator",
        "/guideline-sheet-bengali.png",
        "/guideline-sheet-hindi.png",
        "/guideline-sheet-english.png",
        "/sitemap.xml",
        "/llms.txt",
        "/google283830a3fd2e4cf3.html",
    ]

    @classmethod
    def setUpClass(cls):
        cls.robots_file = FRONTEND_DIR / "robots.txt"
        cls.assertTrue(cls.robots_file.is_file(), "frontend/robots.txt must exist.")
        cls.robots_content = cls.robots_file.read_text(encoding="utf-8")
        cls.parser = urllib.robotparser.RobotFileParser()
        cls.parser.parse(cls.robots_content.splitlines(keepends=True))

    def test_robots_sitemap_directive_exact_match(self):
        """robots.txt must declare Sitemap pointing to https://hatekhori.onrender.com/sitemap.xml."""
        sitemaps = re.findall(r"^Sitemap:\s*(.+)$", self.robots_content, re.MULTILINE | re.IGNORECASE)
        self.assertGreaterEqual(len(sitemaps), 1)
        self.assertEqual(sitemaps[0].strip(), "https://hatekhori.onrender.com/sitemap.xml")

    def test_all_35_crawlers_blocked_from_internal_scratch_paths(self):
        """Every single crawler in the 35-crawler matrix must be strictly disallowed from internal paths."""
        for ua in self.CRAWLERS_35:
            for path in self.DISALLOWED_PATHS:
                with self.subTest(crawler=ua, path=path):
                    allowed = self.parser.can_fetch(ua, path)
                    self.assertFalse(
                        allowed,
                        f"Crawler '{ua}' should be DISALLOWED from '{path}'.",
                    )

    def test_all_35_crawlers_allowed_on_public_pages_and_assets(self):
        """Every single crawler in the 35-crawler matrix must be permitted to crawl all public routes."""
        for ua in self.CRAWLERS_35:
            for path in self.ALLOWED_PATHS:
                with self.subTest(crawler=ua, path=path):
                    allowed = self.parser.can_fetch(ua, path)
                    self.assertTrue(
                        allowed,
                        f"Crawler '{ua}' should be ALLOWED to fetch '{path}'.",
                    )

    def test_crawler_name_case_insensitivity_rfc9309(self):
        """Crawler User-Agent names must match case-insensitively per RFC 9309."""
        case_variations = [
            ("googlebot", "/uploads/", False),
            ("gOoGlEbOt", "/compare/calligraphr-alternative", True),
            ("gptbot", "/output/font.otf", False),
            ("GptBot", "/", True),
            ("claudebot", "/download-font/123", False),
            ("CLAUDE-WEB", "/bengali-font-maker", True),
            ("pErPlExItYbOt", "/sitemap.xml", True),
        ]
        for ua, path, expected in case_variations:
            with self.subTest(ua=ua, path=path):
                self.assertEqual(self.parser.can_fetch(ua, path), expected)

    def test_query_params_do_not_bypass_disallow(self):
        """Query parameters or hashes must NOT bypass Disallow rules."""
        bypasses = [
            "/uploads/?param=1",
            "/output/?file=font.otf",
            "/download-font/?token=secret",
            "/uploads/#top",
        ]
        for path in bypasses:
            with self.subTest(path=path):
                self.assertFalse(self.parser.can_fetch("Googlebot", path))
                self.assertFalse(self.parser.can_fetch("GPTBot", path))
                self.assertFalse(self.parser.can_fetch("*", path))


# ---------------------------------------------------------------------------
# Test Suite 4: Google Search Console (GSC) Verification Permanence
# ---------------------------------------------------------------------------
class TestGSCVerificationPermanence(unittest.TestCase):
    """Stress-test Google Search Console file verification and HTML meta tag permanence."""

    PAGES = [
        "frontend/index.html",
        "frontend/compare/calligraphr-alternative.html",
        "frontend/bengali-font-maker.html",
        "frontend/hindi-font-generator.html",
    ]

    EXPECTED_HASH_TOKEN = "ywFgWCyBD6nzTB9FV6Df3cGfGpcPVhtdGiTvXt_wf20"
    EXPECTED_FILE_TOKEN = "google283830a3fd2e4cf3"

    def test_gsc_standalone_file_exact_bytes_and_unwrapped(self):
        """frontend/google283830a3fd2e4cf3.html must be exactly 54 bytes without HTML tags."""
        gsc_file = FRONTEND_DIR / "google283830a3fd2e4cf3.html"
        self.assertTrue(gsc_file.is_file())
        raw_bytes = gsc_file.read_bytes()
        self.assertEqual(len(raw_bytes), 54, f"GSC file must be exactly 54 bytes, got {len(raw_bytes)}")

        text = gsc_file.read_text(encoding="utf-8")
        self.assertEqual(text.strip(), "google-site-verification: google283830a3fd2e4cf3.html")

        # Must not contain HTML markup
        for forbidden in ["<html", "<head", "<body", "<!doctype", "<script"]:
            self.assertNotIn(forbidden, text.lower())

    def test_gsc_standalone_file_asgi_resolution(self):
        """GET /google283830a3fd2e4cf3.html via ASGI must return HTTP 200 and exact content."""
        res = client.get("/google283830a3fd2e4cf3.html")
        self.assertEqual(res.status_code, 200)
        self.assertIn("google-site-verification: google283830a3fd2e4cf3.html", res.text)

    def test_gsc_meta_tags_present_on_all_four_html_pages(self):
        """Both GSC tokens must be present in <meta name='google-site-verification'> on all 4 pages."""
        for rel_path in self.PAGES:
            with self.subTest(page=rel_path):
                content = (ROOT_DIR / rel_path).read_text(encoding="utf-8")
                parser = parse_html_document(content)

                gsc_meta = [
                    m["content"]
                    for m in parser.meta_tags
                    if m.get("name") == "google-site-verification" and "content" in m
                ]
                self.assertGreaterEqual(len(gsc_meta), 2, f"{rel_path} must have at least 2 GSC meta tags.")
                self.assertIn(self.EXPECTED_HASH_TOKEN, gsc_meta)
                self.assertIn(self.EXPECTED_FILE_TOKEN, gsc_meta)

    def test_gsc_meta_tags_located_in_head_before_closing(self):
        """GSC verification meta tags must strictly be placed within <head> ... </head>."""
        for rel_path in self.PAGES:
            with self.subTest(page=rel_path):
                content = (ROOT_DIR / rel_path).read_text(encoding="utf-8")
                parser = parse_html_document(content)

                head_gsc = [
                    m["content"]
                    for m in parser.head_meta_tags
                    if m.get("name") == "google-site-verification"
                ]
                self.assertIn(self.EXPECTED_HASH_TOKEN, head_gsc)
                self.assertIn(self.EXPECTED_FILE_TOKEN, head_gsc)


# ---------------------------------------------------------------------------
# Test Suite 5: Viewport, OpenGraph, and Twitter Meta Across Breakpoints
# ---------------------------------------------------------------------------
class TestMobileViewportOpenGraphTwitterMeta(unittest.TestCase):
    """Stress-test mobile responsiveness, viewport settings, canonicals, OpenGraph, and Twitter tags."""

    PAGES = [
        ("frontend/index.html", "https://hatekhori.onrender.com/"),
        ("frontend/compare/calligraphr-alternative.html", "https://hatekhori.onrender.com/compare/calligraphr-alternative"),
        ("frontend/bengali-font-maker.html", "https://hatekhori.onrender.com/bengali-font-maker"),
        ("frontend/hindi-font-generator.html", "https://hatekhori.onrender.com/hindi-font-generator"),
    ]

    def test_viewport_meta_tags_across_all_pages(self):
        """All 4 pages must contain width=device-width, initial-scale=1, and viewport-fit=cover."""
        for rel_path, _ in self.PAGES:
            with self.subTest(page=rel_path):
                content = (ROOT_DIR / rel_path).read_text(encoding="utf-8")
                parser = parse_html_document(content)
                vp = next((m.get("content", "") for m in parser.meta_tags if m.get("name") == "viewport"), "")
                self.assertIn("width=device-width", vp)
                self.assertIn("initial-scale=1", vp)
                self.assertIn("viewport-fit=cover", vp)

    def test_canonical_links_match_exact_target_url(self):
        """Canonical link href must match the exact canonical HTTPS URL."""
        for rel_path, canonical_url in self.PAGES:
            with self.subTest(page=rel_path):
                content = (ROOT_DIR / rel_path).read_text(encoding="utf-8")
                parser = parse_html_document(content)
                canonical_link = next(
                    (link.get("href") for link in parser.link_tags if link.get("rel") == "canonical"),
                    None,
                )
                self.assertEqual(canonical_link, canonical_url)

    def test_opengraph_tags_completeness_and_bounds(self):
        """All 4 pages must specify og:type, og:url, og:title, og:description, and og:image."""
        for rel_path, canonical_url in self.PAGES:
            with self.subTest(page=rel_path):
                content = (ROOT_DIR / rel_path).read_text(encoding="utf-8")
                parser = parse_html_document(content)
                og_tags = {m.get("property"): m.get("content") for m in parser.meta_tags if m.get("property", "").startswith("og:")}

                self.assertIn(og_tags.get("og:type"), ["website", "article"])
                self.assertEqual(og_tags.get("og:url"), canonical_url)

                title = og_tags.get("og:title", "")
                self.assertGreaterEqual(len(title), 15)
                self.assertLessEqual(len(title), 95)

                desc = og_tags.get("og:description", "")
                self.assertGreaterEqual(len(desc), 50)
                self.assertLessEqual(len(desc), 200)

                image = og_tags.get("og:image", "")
                self.assertTrue(image.startswith("https://hatekhori.onrender.com/"))
                self.assertTrue(image.endswith(".png"))

                self.assertEqual(og_tags.get("og:site_name"), "Hatekhori (হাতে খড়ি)")

    def test_twitter_cards_completeness(self):
        """All 4 pages must specify twitter:card == summary_large_image and twitter:image."""
        for rel_path, _ in self.PAGES:
            with self.subTest(page=rel_path):
                content = (ROOT_DIR / rel_path).read_text(encoding="utf-8")
                parser = parse_html_document(content)
                tw_tags = {m.get("name"): m.get("content") for m in parser.meta_tags if m.get("name", "").startswith("twitter:")}

                self.assertEqual(tw_tags.get("twitter:card"), "summary_large_image")
                self.assertGreater(len(tw_tags.get("twitter:title", "")), 10)
                self.assertGreater(len(tw_tags.get("twitter:description", "")), 30)
                self.assertTrue(tw_tags.get("twitter:image", "").startswith("https://hatekhori.onrender.com/"))

    def test_mobile_accessibility_and_reduced_motion(self):
        """Emil Kowalski reduced-motion CSS rules must be declared in style.css or page styles."""
        style_css = FRONTEND_DIR / "style.css"
        self.assertTrue(style_css.is_file())
        style_content = style_css.read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion", style_content)

        # Tabular nums for numbers/counters
        self.assertIn("tabular-nums", style_content)


# ---------------------------------------------------------------------------
# Test Suite 6: LLMs.txt GEO citability & Canonical Domain Alignment
# ---------------------------------------------------------------------------
class TestLLMsTxtAIEngineCitability(unittest.TestCase):
    """Stress-test frontend/llms.txt for AI answer engines (ChatGPT, Perplexity, Claude, Gemini)."""

    @classmethod
    def setUpClass(cls):
        cls.llms_file = FRONTEND_DIR / "llms.txt"
        assert cls.llms_file.is_file(), f"File not found: {cls.llms_file}"
        cls.content = cls.llms_file.read_text(encoding="utf-8")
        cls.lines = cls.content.splitlines()

    def test_llms_txt_line1_header_and_blockquote(self):
        """llms.txt must begin on Line 1 with # Hatekhori (হাতে খড়ি) and blockquote summary."""
        self.assertEqual(self.lines[0].strip(), "# Hatekhori (হাতে খড়ি)")
        blockquote = [line for line in self.lines[:10] if line.startswith(">")]
        self.assertGreaterEqual(len(blockquote), 1)
        self.assertIn("Bengali", blockquote[0])
        self.assertIn("Hindi", blockquote[0])

    def test_llms_txt_mentions_all_three_languages_and_scripts(self):
        """llms.txt must explicitly cover Bengali (বাংলা), Hindi (हिन्दी), and English."""
        self.assertIn("Bengali", self.content)
        self.assertIn("বাংলা", self.content)
        self.assertIn("Hindi", self.content)
        self.assertIn("हिन्दी", self.content)
        self.assertIn("English", self.content)

    def test_llms_txt_pure_vector_and_zero_cost_guarantee(self):
        """llms.txt must detail pure sub-pixel vector tracing and zero-account / 100% free pricing."""
        self.assertIn("Potrace", self.content)
        self.assertIn("100% free", self.content.lower())
        self.assertIn("zero account", self.content.lower())
        self.assertIn("exif", self.content.lower())

    def test_llms_txt_urls_all_canonical_and_resolve_200(self):
        """All extracted URLs in llms.txt must use canonical https://hatekhori.onrender.com and return HTTP 200."""
        urls = re.findall(r"https://hatekhori\.onrender\.com[^\s\)\]\"'>]*", self.content)
        self.assertGreaterEqual(len(urls), 6)
        for url in set(urls):
            parsed = urllib.parse.urlparse(url)
            req_path = parsed.path if parsed.path else "/"
            with self.subTest(url=url):
                res = client.get(req_path)
                self.assertEqual(res.status_code, 200, f"URL '{url}' in llms.txt returned {res.status_code}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
