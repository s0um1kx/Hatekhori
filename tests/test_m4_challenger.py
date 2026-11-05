"""Milestone 4 Empirical Challenger Test Suite.

Author: m4_challenger_1 (teamwork_challenger: Critic & Specialist)
Role: Critic & Empirical Challenger
Focus:
  1. Word counts verification across all Milestone 4 deliverables:
     - TECHNICAL-AUDIT.md >= 3,000 words
     - KEYWORD-CLUSTERS.md >= 2,000 words
     - COMPETITOR-ANALYSIS.md >= 1,800 words
     - SXO-GUIDELINES.md >= 1,800 words
  2. Strict token hygiene & zero forbidden tokens (TODO, TBD, FIXME, localhost, hatekhori.com)
  3. Comprehensive Markdown table delimiter alignment and column integrity validation
  4. Extraction of all URLs and live ASGI HTTP 200 OK resolution of internal URLs
  5. Structural completeness, section blueprints, and Devanagari polish in llms.txt
  6. Cross-file consistency and pre-existing legacy boundary isolation checks
"""

import os
import re
import sys
import unittest
from pathlib import Path

# Safe Unicode output for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_SEO_DIR = ROOT_DIR / "docs" / "seo"
FRONTEND_DIR = ROOT_DIR / "frontend"
sys.path.insert(0, str(ROOT_DIR))

# Import ASGI client from test_seo_discoverability
from tests.test_seo_discoverability import client  # noqa: E402


class TestM4WordCounts(unittest.TestCase):
    """Empirically test word counts and substantive depth of M4 deliverables."""

    @classmethod
    def setUpClass(cls):
        cls.files = {
            "TECHNICAL-AUDIT.md": DOCS_SEO_DIR / "TECHNICAL-AUDIT.md",
            "KEYWORD-CLUSTERS.md": DOCS_SEO_DIR / "KEYWORD-CLUSTERS.md",
            "COMPETITOR-ANALYSIS.md": DOCS_SEO_DIR / "COMPETITOR-ANALYSIS.md",
            "SXO-GUIDELINES.md": DOCS_SEO_DIR / "SXO-GUIDELINES.md",
        }
        cls.texts = {}
        cls.word_counts = {}
        for name, path in cls.files.items():
            if path.exists():
                text = path.read_text(encoding="utf-8")
                cls.texts[name] = text
                cls.word_counts[name] = len(text.split())

    def test_technical_audit_word_count_ge_3000(self):
        """TECHNICAL-AUDIT.md must have at least 3,000 words."""
        count = self.word_counts.get("TECHNICAL-AUDIT.md", 0)
        self.assertGreaterEqual(
            count,
            3000,
            f"TECHNICAL-AUDIT.md has only {count} words, expected >= 3,000",
        )

    def test_keyword_clusters_word_count_ge_2000(self):
        """KEYWORD-CLUSTERS.md must have at least 2,000 words."""
        count = self.word_counts.get("KEYWORD-CLUSTERS.md", 0)
        self.assertGreaterEqual(
            count,
            2000,
            f"KEYWORD-CLUSTERS.md has only {count} words, expected >= 2,000",
        )

    def test_competitor_analysis_word_count_ge_1800(self):
        """COMPETITOR-ANALYSIS.md must have at least 1,800 words."""
        count = self.word_counts.get("COMPETITOR-ANALYSIS.md", 0)
        self.assertGreaterEqual(
            count,
            1800,
            f"COMPETITOR-ANALYSIS.md has only {count} words, expected >= 1,800",
        )

    def test_sxo_guidelines_word_count_ge_1800(self):
        """SXO-GUIDELINES.md must have at least 1,800 words."""
        count = self.word_counts.get("SXO-GUIDELINES.md", 0)
        self.assertGreaterEqual(
            count,
            1800,
            f"SXO-GUIDELINES.md has only {count} words, expected >= 1,800",
        )

    def test_all_m4_deliverables_exist_and_non_trivial(self):
        """All 4 Milestone 4 documentation deliverables must exist and be > 10KB."""
        for name, path in self.files.items():
            self.assertTrue(path.exists(), f"Missing deliverable: {name}")
            size = path.stat().st_size
            self.assertGreater(size, 10000, f"{name} file size {size} bytes is unexpectedly small (<10KB)")


class TestM4ForbiddenTokens(unittest.TestCase):
    """Empirically assert zero forbidden tokens (TODO, TBD, FIXME, localhost, hatekhori.com)."""

    FORBIDDEN = ["TODO", "TBD", "FIXME", "localhost", "hatekhori.com"]
    M4_TARGETS = [
        "TECHNICAL-AUDIT.md",
        "KEYWORD-CLUSTERS.md",
        "COMPETITOR-ANALYSIS.md",
        "SXO-GUIDELINES.md",
    ]

    def test_zero_forbidden_tokens_in_m4_deliverables(self):
        """All 4 Milestone 4 documentation files must have exactly 0 forbidden tokens."""
        violations = []
        for name in self.M4_TARGETS:
            path = DOCS_SEO_DIR / name
            content = path.read_text(encoding="utf-8")
            for token in self.FORBIDDEN:
                matches = list(re.finditer(re.escape(token), content, re.IGNORECASE))
                if matches:
                    for m in matches:
                        line_no = content[:m.start()].count("\n") + 1
                        matched_str = m.group(0)
                        violations.append(f"{name}:{line_no} contains forbidden token '{matched_str}'")

        self.assertEqual(
            violations,
            [],
            f"Found forbidden tokens in M4 deliverables:\n" + "\n".join(violations),
        )

    def test_zero_forbidden_tokens_in_polished_llms_txt(self):
        """frontend/llms.txt must have zero forbidden tokens."""
        llms_path = FRONTEND_DIR / "llms.txt"
        content = llms_path.read_text(encoding="utf-8")
        violations = []
        for token in self.FORBIDDEN:
            matches = list(re.finditer(re.escape(token), content, re.IGNORECASE))
            if matches:
                for m in matches:
                    line_no = content[:m.start()].count("\n") + 1
                    violations.append(f"frontend/llms.txt:{line_no} contains forbidden token '{m.group(0)}'")
        self.assertEqual(violations, [])


class TestM4MarkdownTableIntegrity(unittest.TestCase):
    """Empirically parse and validate every Markdown table across M4 documents."""

    M4_TARGETS = [
        "TECHNICAL-AUDIT.md",
        "KEYWORD-CLUSTERS.md",
        "COMPETITOR-ANALYSIS.md",
        "SXO-GUIDELINES.md",
    ]

    @staticmethod
    def extract_tables(text: str):
        """Extract table blocks: returns list of (table_start_line, header, delimiter, data_rows)."""
        lines = text.splitlines()
        tables = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # A markdown table starts with a line containing |
            if line.startswith("|") and line.endswith("|") and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Check if next_line is a table delimiter (| :--- | :---: | ---: |)
                if next_line.startswith("|") and next_line.endswith("|") and re.match(r"^\|(\s*:?-+:?\s*\|)+$", next_line):
                    header = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
                    delimiter = [c.strip() for c in re.split(r"(?<!\\)\|", next_line)[1:-1]]
                    data_rows = []
                    j = i + 2
                    while j < len(lines):
                        row_line = lines[j].strip()
                        if row_line.startswith("|") and row_line.endswith("|"):
                            # Parse data cells taking escaped pipes \| into account
                            cells = [c.strip() for c in re.split(r"(?<!\\)\|", row_line)[1:-1]]
                            data_rows.append((j + 1, cells, row_line))
                            j += 1
                        else:
                            break
                    tables.append((i + 1, header, delimiter, data_rows))
                    i = j
                    continue
            i += 1
        return tables

    def test_markdown_tables_exist_and_valid_in_m4_deliverables(self):
        """Verify markdown tables exist across all M4 deliverables and have correct delimiter and column counts."""
        total_tables = 0
        for name in self.M4_TARGETS:
            path = DOCS_SEO_DIR / name
            content = path.read_text(encoding="utf-8")
            tables = self.extract_tables(content)
            self.assertGreater(len(tables), 0, f"Expected tables in {name}, found 0")
            total_tables += len(tables)

            for start_line, header, delimiter, data_rows in tables:
                col_count = len(header)
                delim_count = len(delimiter)
                self.assertEqual(
                    col_count,
                    delim_count,
                    f"{name}:{start_line} Header column count ({col_count}) != Delimiter column count ({delim_count})",
                )
                # Verify delimiter syntax
                for d in delimiter:
                    self.assertTrue(
                        re.match(r"^:?-+:?$", d),
                        f"{name}:{start_line+1} Invalid delimiter token: '{d}'",
                    )
                # Verify all data rows have identical column count
                for row_line_no, cells, raw_line in data_rows:
                    self.assertEqual(
                        len(cells),
                        col_count,
                        f"{name}:{row_line_no} Row column count ({len(cells)}) != Header column count ({col_count}). Row: {raw_line}",
                    )

        # Overall check: at least 10 tables across the 4 documents
        self.assertGreaterEqual(total_tables, 10, f"Expected >= 10 tables total, found {total_tables}")

    def test_markdown_tables_in_all_docs_seo_files(self):
        """Verify all markdown files in docs/seo have syntactically aligned tables."""
        all_md_files = list(DOCS_SEO_DIR.glob("*.md"))
        for md_path in all_md_files:
            content = md_path.read_text(encoding="utf-8")
            tables = self.extract_tables(content)
            for start_line, header, delimiter, data_rows in tables:
                self.assertEqual(
                    len(header),
                    len(delimiter),
                    f"{md_path.name}:{start_line} Delimiter count mismatch",
                )
                for row_line_no, cells, raw_line in data_rows:
                    self.assertEqual(
                        len(cells),
                        len(header),
                        f"{md_path.name}:{row_line_no} Column count mismatch",
                    )


class TestM4URLExtractionAndASGIResolution(unittest.TestCase):
    """Empirically extract all URLs from M4 documents and resolve internal URLs via ASGI client."""

    M4_TARGETS = [
        "TECHNICAL-AUDIT.md",
        "KEYWORD-CLUSTERS.md",
        "COMPETITOR-ANALYSIS.md",
        "SXO-GUIDELINES.md",
    ]

    CANONICAL_HOST = "https://hatekhori.onrender.com"

    def _extract_all_urls(self, text: str) -> set[str]:
        urls = set()
        # 1. Standard markdown links: [text](url)
        for _, url in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text):
            clean_url = url.strip().split()[0]
            urls.add(clean_url)

        # 2. Raw absolute http/https URLs
        for m in re.finditer(r"https?://[^\s`\"\'\<\>\)]+", text):
            url = m.group(0).rstrip(".,;:)")
            urls.add(url)

        # 3. Path literals in backticks or tables (e.g. `/compare/calligraphr-alternative`)
        for m in re.finditer(r"[`|\s](/(?:[a-zA-Z0-9_\-\.]+/)*[a-zA-Z0-9_\-\.]*)[`|\s]", text):
            path = m.group(1).strip()
            if path in [
                "/",
                "/bengali-font-maker",
                "/hindi-font-generator",
                "/compare/calligraphr-alternative",
                "/robots.txt",
                "/sitemap.xml",
                "/llms.txt",
                "/guideline-sheet-bengali.png",
                "/guideline-sheet-hindi.png",
                "/guideline-sheet-english.png",
                "/google283830a3fd2e4cf3.html",
            ]:
                urls.add(path)

        return urls

    def test_internal_urls_resolve_to_http_200_ok(self):
        """Every internal URL extracted from M4 docs must return HTTP 200 OK via ASGI test client."""
        tested_paths = set()
        url_occurrences = {}

        for name in self.M4_TARGETS:
            path = DOCS_SEO_DIR / name
            content = path.read_text(encoding="utf-8")
            urls = self._extract_all_urls(content)

            for u in urls:
                # Check if internal
                route_path = None
                if u.startswith(self.CANONICAL_HOST):
                    route_path = u[len(self.CANONICAL_HOST) :]
                    if not route_path:
                        route_path = "/"
                elif u.startswith("/") and not u.startswith("//"):
                    route_path = u

                if route_path:
                    # Strip fragment if present
                    route_clean = route_path.split("#")[0]
                    if not route_clean:
                        route_clean = "/"
                    tested_paths.add(route_clean)
                    url_occurrences.setdefault(route_clean, []).append(f"{name} ({u})")

        # Now query each unique path through ASGI client
        failures = []
        for route in sorted(tested_paths):
            # Skip wildcards like /guideline-sheet-*.png or internal scratch dirs /uploads/
            if "*" in route or route in ["/uploads/", "/output/", "/download-font/"]:
                continue

            response = client.get(route)
            if response.status_code != 200:
                failures.append(
                    f"Route '{route}' returned HTTP {response.status_code} (expected 200). Referenced in: {url_occurrences.get(route)}"
                )
            else:
                # Assert non-empty body
                if len(response.content) == 0:
                    failures.append(f"Route '{route}' returned empty response body (0 bytes)")

        self.assertEqual(
            failures,
            [],
            f"Failed internal URL resolutions:\n" + "\n".join(failures),
        )

        # Assert we actually tested key canonical routes
        expected_routes = {
            "/",
            "/compare/calligraphr-alternative",
            "/bengali-font-maker",
            "/hindi-font-generator",
            "/robots.txt",
            "/sitemap.xml",
            "/llms.txt",
        }
        for exp in expected_routes:
            self.assertIn(exp, tested_paths, f"Expected route {exp} to be cited and tested from M4 docs")

    def test_no_deprecated_http_schemes_or_hatekhori_com(self):
        """Ensure no links use http:// (insecure) or hatekhori.com (deprecated domain)."""
        violations = []
        for name in self.M4_TARGETS:
            path = DOCS_SEO_DIR / name
            content = path.read_text(encoding="utf-8")
            urls = self._extract_all_urls(content)
            for u in urls:
                if "hatekhori.com" in u:
                    violations.append(f"{name}: contains deprecated domain in URL '{u}'")
                if u.startswith("http://hatekhori"):
                    violations.append(f"{name}: contains insecure http:// scheme in URL '{u}'")
        self.assertEqual(violations, [])


class TestM4DocumentSectionCompleteness(unittest.TestCase):
    """Stress-test specific content requirements, blueprints, and data matrices."""

    def test_technical_audit_12_sections(self):
        """TECHNICAL-AUDIT.md must contain all 12 planned architectural sections."""
        content = (DOCS_SEO_DIR / "TECHNICAL-AUDIT.md").read_text(encoding="utf-8")
        required_headers = [
            "Executive Summary & Architecture Overview",
            "Technical Findings & Defect Remediation Matrix",
            "Crawlability & Indexing Infrastructure",
            "Backend Routing & HTTP Response Headers Architecture",
            "On-Page Technical SEO & Document Structure",
            "Schema.org Structured Data & Knowledge Graph Topology",
            "Search Console Verification & Ownership Redundancy",
            "Generative Engine Optimization (GEO) & AI Agent Readiness",
            "Search Experience Optimization (SXO) & Mobile Engineering",
            "Automated Verification & Test Suite Coverage",
            "Core Web Vitals & Real-User Performance Targets",
            "Operational Maintenance & Ongoing Monitoring Protocols",
        ]
        for header in required_headers:
            self.assertIn(
                header.lower(),
                content.lower(),
                f"TECHNICAL-AUDIT.md missing required section: '{header}'",
            )

        # Verify defect IDs TECH-01 through TECH-11 are all covered
        for i in range(1, 12):
            tech_id = f"TECH-{i:02d}"
            self.assertIn(tech_id, content, f"Missing {tech_id} in TECHNICAL-AUDIT.md defect matrix")

    def test_keyword_clusters_6_clusters_and_indic_scripts(self):
        """KEYWORD-CLUSTERS.md must contain all 6 clusters and native Indic search queries."""
        content = (DOCS_SEO_DIR / "KEYWORD-CLUSTERS.md").read_text(encoding="utf-8")
        clusters = [
            "Bengali Indic Handwriting Typography",
            "Hindi & Devanagari Handwriting Typography",
            "Calligraphr Switchers & Competitor Alternatives",
            "Free & No-Subscription Handwriting Font Tools",
            "Physical Pen-to-Vector & Anti-AI Typography",
            "Guideline Sheets & Printable Templates",
        ]
        for c in clusters:
            self.assertIn(c.lower(), content.lower(), f"KEYWORD-CLUSTERS.md missing cluster: '{c}'")

        # Native script query validation
        self.assertIn("বাংলা", content)
        self.assertIn("হাতের লেখা ফন্ট", content)
        self.assertIn("हिन्दी", content)
        self.assertIn("लिखावट", content)
        self.assertIn("शिरोरेखा", content)

    def test_competitor_analysis_5_foundries_and_14_point_matrix(self):
        """COMPETITOR-ANALYSIS.md must detail all 5 foundries and 14-point matrix."""
        content = (DOCS_SEO_DIR / "COMPETITOR-ANALYSIS.md").read_text(encoding="utf-8")
        foundries = ["Hatekhori", "Calligraphr", "Lipighor", "Fontself", "FontCrafter"]
        for f in foundries:
            self.assertIn(f.lower(), content.lower(), f"COMPETITOR-ANALYSIS.md missing foundry: '{f}'")

        # Verify 14 matrix points in table
        for i in range(1, 15):
            self.assertIn(f"**{i}.", content, f"Missing matrix criterion {i} in COMPETITOR-ANALYSIS.md")

        # Verify 2D positioning maps
        self.assertIn("2D Competitive Positioning Maps", content)
        self.assertIn("Map A: Script Complexity vs. Accessibility & Cost", content)
        self.assertIn("Map B: Input Capture Workflow vs. Vector Precision", content)

    def test_sxo_guidelines_motion_and_touch_standards(self):
        """SXO-GUIDELINES.md must specify Emil Kowalski motion CSS and UI/UX Pro Max 44px standards."""
        content = (DOCS_SEO_DIR / "SXO-GUIDELINES.md").read_text(encoding="utf-8")
        self.assertIn("Emil Kowalski", content)
        self.assertIn("cubic-bezier", content)
        self.assertIn("scale(0.97)", content)
        self.assertIn("44px", content)
        self.assertIn("pogo-sticking", content.lower())

        # Verify 4 persona scoring audits
        self.assertIn("4-Persona SXO Scoring & Journey Audits", content)
        self.assertIn("Persona 1: The Indian Developer / Type Designer", content)
        self.assertIn("Persona 2: The Frustrated Calligraphr Switcher", content)
        self.assertIn("Persona 3: The Anti-AI Calligrapher / Purist", content)
        self.assertIn("Persona 4: The Diaspora Cultural Archivist", content)

    def test_llms_txt_devanagari_polish_character_integrity(self):
        """Verify that frontend/llms.txt contains native Devanagari codepoints and zero Bengali cross-script chars."""
        llms_path = FRONTEND_DIR / "llms.txt"
        lines = llms_path.read_text(encoding="utf-8").splitlines()
        devanagari_line = lines[28]  # 0-indexed line 28 is line 29
        matra_line = lines[29]       # 0-indexed line 29 is line 30

        # Assert native Devanagari \u0922 ('ढ') is present and Bengali \u09A2 ('ঢ') is absent
        self.assertIn("\u0922", devanagari_line, "Expected native Devanagari 'ढ' (U+0922) on line 29")
        self.assertNotIn("\u09A2", devanagari_line, "Found leaked Bengali character 'ঢ' (U+09A2) on line 29")

        # Assert native Devanagari \u0903 ('ः') is present and Bengali \u0983 ('ঃ') is absent
        self.assertIn("\u0903", matra_line, "Expected native Devanagari 'ः' (U+0903) on line 30")
        self.assertNotIn("\u0983", matra_line, "Found leaked Bengali character 'ঃ' (U+0983) on line 30")


if __name__ == "__main__":
    unittest.main(verbosity=2)
