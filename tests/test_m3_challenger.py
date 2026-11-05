"""Milestone 3 Empirical Challenger Verification Suite.

Author: m3_challenger_1 (teamwork_challenger: Critic & Specialist)
Focus:
  1. robots.txt RFC 9309 & urllib.robotparser.RobotFileParser empirical stress testing
     across 22 User-Agents (standard search, AI/GEO, social, unknown, and wildcard bots)
     for public routes and internal disallowed directories (/uploads/, /output/, /download-font/).
  2. sitemap.xml xml.etree.ElementTree schema parsing, namespace verification,
     0 duplicate <loc> entries, 0 HTTP links, 0 deprecated domains, valid ISO 8601 dates,
     and valid priority/changefreq enums.
  3. ASGI test client resolution of all sitemap URLs returning HTTP 200, matching Content-Types,
     and 1:1 canonical link reciprocity with target HTML documents.
"""

from datetime import date
import os
import re
import sys
import unittest
import urllib.robotparser
import xml.etree.ElementTree as ET
from pathlib import Path

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


class TestRobotsTxtUrllibRobotParser(unittest.TestCase):
    """Empirically stress-test frontend/robots.txt with urllib.robotparser.RobotFileParser."""

    @classmethod
    def setUpClass(cls):
        cls.robots_file = FRONTEND_DIR / "robots.txt"
        with open(cls.robots_file, "r", encoding="utf-8") as f:
            cls.robots_content = f.read()
            cls.robots_lines = cls.robots_content.splitlines(keepends=True)

        cls.parser = urllib.robotparser.RobotFileParser()
        cls.parser.parse(cls.robots_lines)

        cls.user_agents = [
            # Major Search Engine Crawlers
            "Googlebot",
            "Bingbot",
            "Slurp",
            "DuckDuckBot",
            "Baiduspider",
            "YandexBot",
            # AI Search, Answer Engine & GEO Crawlers
            "GPTBot",
            "ChatGPT-User",
            "PerplexityBot",
            "ClaudeBot",
            "Claude-Web",
            "Google-Extended",
            "Applebot",
            "Applebot-Extended",
            "Amazonbot",
            "CCBot",
            "Cohere-ai",
            # Social media / aggregator crawlers
            "facebookexternalhit",
            "Twitterbot",
            # Unknown / generic / wildcard bots
            "badbot",
            "CustomScraperBot/1.0",
            "*",
        ]

        cls.public_urls = [
            "https://hatekhori.onrender.com/",
            "https://hatekhori.onrender.com/compare/calligraphr-alternative",
            "https://hatekhori.onrender.com/bengali-font-maker",
            "https://hatekhori.onrender.com/hindi-font-generator",
            "https://hatekhori.onrender.com/guideline-sheet-bengali.png",
            "https://hatekhori.onrender.com/guideline-sheet-hindi.png",
            "https://hatekhori.onrender.com/guideline-sheet-english.png",
            "https://hatekhori.onrender.com/llms.txt",
            "https://hatekhori.onrender.com/sitemap.xml",
            "https://hatekhori.onrender.com/style.css",
            "https://hatekhori.onrender.com/script.js",
        ]

        cls.disallowed_urls = [
            "https://hatekhori.onrender.com/uploads/",
            "https://hatekhori.onrender.com/uploads/photo.jpg",
            "https://hatekhori.onrender.com/uploads/nested/test.png",
            "https://hatekhori.onrender.com/output/",
            "https://hatekhori.onrender.com/output/font.otf",
            "https://hatekhori.onrender.com/output/font.ttf",
            "https://hatekhori.onrender.com/download-font/",
            "https://hatekhori.onrender.com/download-font/123e4567-e89b-12d3-a456-426614174000",
        ]

    def test_robots_file_exists_and_utf8(self):
        """Verify robots.txt exists on disk and is valid UTF-8."""
        self.assertTrue(self.robots_file.exists(), f"robots.txt not found at {self.robots_file}")
        self.assertGreater(len(self.robots_content), 100, "robots.txt is unexpectedly short")
        self.assertNotIn("hatekhori.com", self.robots_content, "Deprecated domain hatekhori.com found in robots.txt")

    def test_robotparser_sitemap_extraction(self):
        """Verify RobotFileParser extracts the canonical sitemap URL."""
        sitemaps = getattr(self.parser, "site_maps", lambda: [])()
        self.assertIn(
            "https://hatekhori.onrender.com/sitemap.xml",
            sitemaps,
            f"Expected canonical sitemap in site_maps(), found {sitemaps}",
        )

    def test_robotparser_22_user_agents_public_urls_allowed(self):
        """Verify all 22 User-Agents can fetch every public route and asset."""
        for ua in self.user_agents:
            for url in self.public_urls:
                can_fetch = self.parser.can_fetch(ua, url)
                self.assertTrue(
                    can_fetch,
                    f"User-agent '{ua}' was unexpectedly blocked from public URL: {url}",
                )

    def test_robotparser_22_user_agents_disallowed_paths(self):
        """Verify all 22 User-Agents are strictly disallowed from internal scratch/download paths."""
        for ua in self.user_agents:
            for url in self.disallowed_urls:
                can_fetch = self.parser.can_fetch(ua, url)
                self.assertFalse(
                    can_fetch,
                    f"User-agent '{ua}' was unexpectedly allowed to fetch protected path: {url}",
                )

    def test_robotparser_agent_case_insensitivity(self):
        """Verify RobotFileParser handles lower-cased and mixed-cased bot names per RFC 9309."""
        case_variations = [
            ("googlebot", "https://hatekhori.onrender.com/bengali-font-maker", True),
            ("GOOGLEBOT", "https://hatekhori.onrender.com/uploads/secret.png", False),
            ("gptbot", "https://hatekhori.onrender.com/compare/calligraphr-alternative", True),
            ("GptBot", "https://hatekhori.onrender.com/output/custom.otf", False),
            ("perplexitybot", "https://hatekhori.onrender.com/hindi-font-generator", True),
            ("PERPLEXITYBOT", "https://hatekhori.onrender.com/download-font/123", False),
        ]
        for ua, url, expected in case_variations:
            can_fetch = self.parser.can_fetch(ua, url)
            self.assertEqual(
                can_fetch,
                expected,
                f"Case-insensitivity failure for User-agent '{ua}' on {url}: expected {expected}, got {can_fetch}",
            )

    def test_robotparser_disallowed_with_query_params(self):
        """Verify disallowed paths cannot be bypassed with query strings or hashes."""
        bypass_attempts = [
            "https://hatekhori.onrender.com/uploads/?token=xyz",
            "https://hatekhori.onrender.com/uploads/photo.jpg?version=2",
            "https://hatekhori.onrender.com/output/?q=font",
            "https://hatekhori.onrender.com/download-font/abc?session=1",
        ]
        for ua in ["Googlebot", "GPTBot", "*"]:
            for url in bypass_attempts:
                can_fetch = self.parser.can_fetch(ua, url)
                self.assertFalse(
                    can_fetch,
                    f"Bypass query attempt succeeded: User-agent '{ua}' allowed on {url}",
                )

    def test_robots_txt_rfc9309_structure_and_isolation(self):
        """Verify robots.txt has proper User-agent blocks and Allow immediately following User-agent."""
        lines = [line.strip() for line in self.robots_lines if line.strip() and not line.strip().startswith("#")]
        user_agent_indices = [i for i, line in enumerate(lines) if line.lower().startswith("user-agent:")]
        self.assertGreaterEqual(len(user_agent_indices), 15, "Expected at least 15 User-agent blocks")

        for idx in user_agent_indices:
            self.assertLess(idx + 1, len(lines), "User-agent block has no trailing directive")
            next_line = lines[idx + 1]
            self.assertEqual(
                next_line,
                "Allow: /",
                f"Expected line following User-agent to be 'Allow: /', got '{next_line}' at index {idx+1}",
            )

    def test_robots_txt_asgi_http_serving(self):
        """Verify ASGI server serves robots.txt with HTTP 200, text/plain, and security headers."""
        res = client.get("/robots.txt")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(
            res.headers.get("content-type", "").startswith("text/plain"),
            f"Expected text/plain content-type, got {res.headers.get('content-type')}",
        )
        self.assertEqual(res.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(res.headers.get("x-frame-options"), "DENY")


class TestSitemapXmlETreeValidation(unittest.TestCase):
    """Empirically stress-test frontend/sitemap.xml with xml.etree.ElementTree."""

    @classmethod
    def setUpClass(cls):
        cls.sitemap_file = FRONTEND_DIR / "sitemap.xml"
        with open(cls.sitemap_file, "r", encoding="utf-8") as f:
            cls.sitemap_content = f.read()

        cls.root = ET.fromstring(cls.sitemap_content)
        cls.ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def test_sitemap_file_exists_and_utf8(self):
        """Verify sitemap.xml exists on disk and has XML declaration."""
        self.assertTrue(self.sitemap_file.exists())
        self.assertTrue(self.sitemap_content.startswith("<?xml"), "sitemap.xml missing XML declaration")
        self.assertNotIn("hatekhori.com", self.sitemap_content, "Deprecated domain hatekhori.com found in sitemap.xml")

    def test_sitemap_root_tag_and_namespace(self):
        """Verify root tag matches the standard sitemaps 0.9 schema namespace."""
        expected_tag = "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"
        self.assertEqual(self.root.tag, expected_tag, f"Root tag mismatch: {self.root.tag} != {expected_tag}")

    def test_sitemap_exact_url_count_and_no_duplicates(self):
        """Verify sitemap contains exactly 7 entries and 0 duplicate <loc> tags."""
        urls = self.root.findall("sm:url", self.ns)
        self.assertEqual(len(urls), 7, f"Expected exactly 7 <url> entries, found {len(urls)}")

        locs = [url.find("sm:loc", self.ns).text.strip() for url in urls if url.find("sm:loc", self.ns) is not None]
        self.assertEqual(len(locs), 7, f"Expected 7 <loc> elements, found {len(locs)}")
        self.assertEqual(len(locs), len(set(locs)), f"Found duplicate <loc> entries in sitemap: {locs}")

    def test_sitemap_all_urls_https_and_clean(self):
        """Verify all <loc> entries use HTTPS, canonical domain, no trailing garbage."""
        urls = self.root.findall("sm:url", self.ns)
        for url_elem in urls:
            loc = url_elem.find("sm:loc", self.ns).text
            self.assertIsNotNone(loc)
            self.assertEqual(loc, loc.strip(), f"URL '{loc}' has leading or trailing whitespace")
            self.assertFalse(loc.startswith("http://"), f"Insecure HTTP protocol in <loc>: {loc}")
            self.assertTrue(
                loc.startswith("https://hatekhori.onrender.com/"),
                f"URL '{loc}' does not start with https://hatekhori.onrender.com/",
            )
            self.assertNotIn("#", loc, f"URL '{loc}' contains anchor fragment")
            self.assertNotIn("?", loc, f"URL '{loc}' contains query string")

    def test_sitemap_iso8601_dates(self):
        """Verify all <lastmod> entries are valid ISO 8601 YYYY-MM-DD dates."""
        urls = self.root.findall("sm:url", self.ns)
        for url_elem in urls:
            lastmod_elem = url_elem.find("sm:lastmod", self.ns)
            self.assertIsNotNone(lastmod_elem, "Missing <lastmod> in <url> entry")
            lastmod = lastmod_elem.text.strip()
            try:
                parsed_date = date.fromisoformat(lastmod)
            except ValueError as e:
                self.fail(f"Invalid ISO 8601 date '{lastmod}': {e}")
            self.assertGreaterEqual(parsed_date.year, 2026, f"Suspicious lastmod year: {parsed_date.year}")

    def test_sitemap_changefreq_and_priority_bounds(self):
        """Verify all <changefreq> and <priority> elements conform strictly to sitemaps.org spec."""
        valid_freqs = {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}
        urls = self.root.findall("sm:url", self.ns)
        for url_elem in urls:
            loc = url_elem.find("sm:loc", self.ns).text.strip()
            cf_elem = url_elem.find("sm:changefreq", self.ns)
            self.assertIsNotNone(cf_elem, f"Missing <changefreq> in entry: {loc}")
            cf = cf_elem.text.strip().lower()
            self.assertIn(cf, valid_freqs, f"Invalid changefreq '{cf}' for {loc}")

            pri_elem = url_elem.find("sm:priority", self.ns)
            self.assertIsNotNone(pri_elem, f"Missing <priority> in entry: {loc}")
            try:
                pri = float(pri_elem.text.strip())
            except ValueError:
                self.fail(f"Non-numeric priority '{pri_elem.text}' for {loc}")
            self.assertTrue(0.0 <= pri <= 1.0, f"Priority {pri} out of range [0.0, 1.0] for {loc}")


class TestSitemapAsgiResolutionAndReciprocity(unittest.TestCase):
    """Empirically test HTTP 200 resolution and canonical reciprocity for all sitemap URLs."""

    @classmethod
    def setUpClass(cls):
        sitemap_file = FRONTEND_DIR / "sitemap.xml"
        root = ET.parse(sitemap_file).getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        cls.locs = [elem.text.strip() for elem in root.findall(".//sm:loc", ns)]

    def test_sitemap_asgi_resolution_all_urls_200(self):
        """Verify every single URL declared in sitemap.xml returns HTTP 200 OK via ASGI test client."""
        self.assertEqual(len(self.locs), 7)
        for url in self.locs:
            path = url.replace("https://hatekhori.onrender.com", "") or "/"
            res = client.get(path)
            self.assertEqual(
                res.status_code,
                200,
                f"Sitemap URL '{url}' (path: '{path}') returned HTTP {res.status_code} instead of 200",
            )

    def test_sitemap_content_types_match_asset_type(self):
        """Verify HTML pages return text/html and printable sheets return image/png."""
        for url in self.locs:
            path = url.replace("https://hatekhori.onrender.com", "") or "/"
            res = client.get(path)
            ct = res.headers.get("content-type", "")
            if path.endswith(".png"):
                self.assertTrue(ct.startswith("image/png"), f"Expected image/png for '{path}', got '{ct}'")
            else:
                self.assertTrue(ct.startswith("text/html"), f"Expected text/html for '{path}', got '{ct}'")

    def test_sitemap_canonical_reciprocity_for_html_pages(self):
        """Verify 1:1 canonical reciprocity between sitemap <loc> and HTML <link rel='canonical'>."""
        html_urls = [u for u in self.locs if not u.endswith(".png")]
        self.assertEqual(len(html_urls), 4, f"Expected 4 HTML routes, found {len(html_urls)}")

        for url in html_urls:
            path = url.replace("https://hatekhori.onrender.com", "") or "/"
            res = client.get(path)
            match = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', res.text, re.IGNORECASE)
            if not match:
                match = re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', res.text, re.IGNORECASE)
            self.assertIsNotNone(match, f"Page at '{path}' missing <link rel='canonical'> tag")
            page_canonical = match.group(1).strip()
            self.assertEqual(
                page_canonical,
                url,
                f"Canonical mismatch for '{path}': sitemap has '{url}' but page has '{page_canonical}'",
            )

    def test_sitemap_xml_asgi_serving_headers(self):
        """Verify /sitemap.xml served via ASGI returns HTTP 200, XML content-type, and security headers."""
        res = client.get("/sitemap.xml")
        self.assertEqual(res.status_code, 200)
        self.assertIn("xml", res.headers.get("content-type", "").lower())
        self.assertEqual(res.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(res.headers.get("x-frame-options"), "DENY")


def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestRobotsTxtUrllibRobotParser))
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestSitemapXmlETreeValidation))
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestSitemapAsgiResolutionAndReciprocity))
    return s


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
