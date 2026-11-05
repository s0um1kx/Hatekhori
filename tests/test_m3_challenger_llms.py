"""Empirical Challenger Test Suite: Milestone 3 llms.txt & Markdown AST Stress Verification.

Author: m3_challenger_2 (teamwork_challenger: Critic & Specialist)
Role: Critic & Empirical Challenger
Focus:
  1. CommonMark AST & Markdown Syntax Rigorous Validation
  2. 100% URL Extraction and Direct ASGI HTTP 200 OK Resolution
  3. Byte Length Bounds (200 - 50,000 bytes) & Strict Token Hygiene
  4. Script Unicode Character Range Verification (Bengali U+0980-U+09FF & Devanagari U+0900-U+097F)
  5. GEO Direct Answer & 5-Foundry Matrix Parity
  6. Adversarial Parsing & AI Ingestion Stress Simulation
"""

import asyncio
import io
import json
import os
import re
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

# Safe Unicode output for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_DIR = ROOT_DIR / "backend"
LLMS_TXT_PATH = FRONTEND_DIR / "llms.txt"

# ---------------------------------------------------------------------------
# Sandboxed Windows IOCP Event Loop Patch for In-Memory ASGI Testing
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
sys.path.insert(0, str(BACKEND_DIR))
from app.main import app  # noqa: E402


class ASGIResponse:
    """Encapsulates HTTP response received from ASGI application."""

    def __init__(self, status_code: int, headers: dict[str, str], body: bytes):
        self.status_code = status_code
        self.headers = headers
        self.content = body
        self.text = body.decode("utf-8", errors="replace")

    def json(self):
        return json.loads(self.text)


class ASGIClient:
    """Asynchronous/Synchronous in-memory ASGI test client."""

    def __init__(self, asgi_app):
        self.app = asgi_app

    def request(self, method: str, path: str, headers: dict[str, str] | None = None, body: bytes = b"") -> ASGIResponse:
        url_path = path
        query_string = b""
        if "?" in path:
            url_path, qs = path.split("?", 1)
            query_string = qs.encode("utf-8")

        raw_headers = [
            (b"host", b"hatekhori.onrender.com"),
            (b"user-agent", b"Hatekhori-M3-Challenger/1.0"),
        ]
        if headers:
            for k, v in headers.items():
                raw_headers.append((k.lower().encode("utf-8"), v.encode("utf-8")))

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method.upper(),
            "scheme": "https",
            "path": url_path,
            "raw_path": url_path.encode("utf-8"),
            "query_string": query_string,
            "root_path": "",
            "headers": raw_headers,
            "client": ("127.0.0.1", 54321),
            "server": ("hatekhori.onrender.com", 443),
        }

        response_status = 500
        response_headers: dict[str, str] = {}
        response_body = bytearray()
        body_sent = False

        async def receive():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": body, "more_body": False}
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


client = ASGIClient(app)


# ===========================================================================
# 1. CommonMark AST & Markdown Syntax Rigorous Validation
# ===========================================================================
class TestLLMsCommonMarkAST(unittest.TestCase):
    """Stress-test llms.txt markdown against CommonMark AST rules."""

    @classmethod
    def setUpClass(cls):
        cls.assertTrue(LLMS_TXT_PATH.exists(), f"Missing file: {LLMS_TXT_PATH}")
        cls.raw_bytes = LLMS_TXT_PATH.read_bytes()
        cls.text = cls.raw_bytes.decode("utf-8")
        cls.lines = cls.text.splitlines()

    def test_c1_starts_with_single_h1_header(self):
        """Must begin on line 1 with an H1 header `# <Title>` per llmstxt.org."""
        self.assertGreater(len(self.lines), 0, "llms.txt cannot be empty")
        first_line = self.lines[0].strip()
        self.assertTrue(first_line.startswith("# "), f"First line must be an ATX H1 (# Title), found: {first_line}")
        # Ensure only one top-level H1 exists in the whole document
        h1_lines = [line for line in self.lines if re.match(r"^#\s+[^#]", line)]
        self.assertEqual(len(h1_lines), 1, f"Expected exactly 1 H1 heading, found {len(h1_lines)}: {h1_lines}")

    def test_c2_heading_hierarchy_integrity(self):
        """ATX heading levels must increment cleanly without jumping (e.g. H1 -> H2 -> H3)."""
        heading_re = re.compile(r"^(#{1,6})\s+(.*)$")
        headings = []
        for idx, line in enumerate(self.lines, start=1):
            m = heading_re.match(line)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                self.assertGreater(len(title), 0, f"Heading on line {idx} cannot have empty title")
                headings.append((idx, level, title))

        self.assertGreaterEqual(len(headings), 5, "Expected at least 5 structured headings in llms.txt")
        prev_level = 0
        for idx, level, title in headings:
            if prev_level > 0:
                self.assertLessEqual(
                    level, prev_level + 1,
                    f"Heading level jump violation at line {idx}: from H{prev_level} to H{level} ('{title}')"
                )
            prev_level = level

    def test_c3_blockquote_syntax(self):
        """Blockquote lines must strictly begin with `> ` followed by content."""
        blockquote_lines = [l for l in self.lines if l.startswith(">")]
        self.assertGreater(len(blockquote_lines), 0, "llms.txt should contain an elevator pitch blockquote")
        for line in blockquote_lines:
            self.assertTrue(line.startswith("> "), f"Blockquote missing trailing space: '{line}'")
            self.assertGreater(len(line[2:].strip()), 10, f"Blockquote content too short: '{line}'")

    def test_c4_code_spans_strictly_balanced(self):
        """All inline code spans (`...`) must have balanced backticks on each line."""
        for idx, line in enumerate(self.lines, start=1):
            # Count unescaped backticks
            backtick_count = len(re.findall(r"(?<!\\)`", line))
            self.assertEqual(
                backtick_count % 2, 0,
                f"Unbalanced code backticks on line {idx}: '{line}' (count={backtick_count})"
            )

    def test_c5_emphasis_and_strong_delimiters_balanced(self):
        """Bold asterisks (**text**) must be properly balanced per line/paragraph."""
        for idx, line in enumerate(self.lines, start=1):
            # Count double asterisks
            double_star_count = len(re.findall(r"\*\*", line))
            self.assertEqual(
                double_star_count % 2, 0,
                f"Unbalanced bold markers (**) on line {idx}: '{line}' (count={double_star_count})"
            )

    def test_c6_markdown_table_ast_structure(self):
        """Table must have header, delimiter row with alignments, and matching column count."""
        table_lines = [l for l in self.lines if l.startswith("|") and l.endswith("|")]
        self.assertGreaterEqual(len(table_lines), 3, "Table must have at least header, delimiter, and 1 row")

        # Parse header
        header = [c.strip() for c in table_lines[0].strip("|").split("|")]
        col_count = len(header)
        self.assertGreaterEqual(col_count, 3, "Table must have at least 3 columns")

        # Parse delimiter row
        delimiter = [c.strip() for c in table_lines[1].strip("|").split("|")]
        self.assertEqual(len(delimiter), col_count, "Delimiter row column count mismatch")
        for d in delimiter:
            self.assertTrue(
                re.match(r"^:?-+:?$", d),
                f"Invalid markdown table delimiter specification: '{d}'"
            )

        # Parse data rows
        for idx, row_line in enumerate(table_lines[2:], start=3):
            cols = [c.strip() for c in row_line.strip("|").split("|")]
            self.assertEqual(
                len(cols), col_count,
                f"Row {idx} column count mismatch: expected {col_count}, got {len(cols)} ('{row_line}')"
            )

    def test_c7_ordered_and_unordered_lists(self):
        """Lists must use valid markers: `- ` for bullets and sequential numbers for ordered lists."""
        bullet_lines = [l for l in self.lines if l.strip().startswith("- ")]
        self.assertGreater(len(bullet_lines), 5, "Expected at least 5 bullet items in llms.txt")

        # Check ordered pipeline steps (1. to 9.)
        ordered_lines = [l for l in self.lines if re.match(r"^\d+\.\s+", l.strip())]
        self.assertGreaterEqual(len(ordered_lines), 5, "Expected ordered steps in pipeline section")
        expected_num = 1
        for line in ordered_lines:
            m = re.match(r"^(\d+)\.\s+", line.strip())
            num = int(m.group(1))
            self.assertEqual(num, expected_num, f"Non-sequential ordered list: expected {expected_num}, got {num}")
            expected_num += 1

    def test_c8_clean_line_endings_and_no_null_bytes(self):
        """File must not contain null bytes, orphaned carriage returns, or byte-order-marks."""
        self.assertNotIn(b"\x00", self.raw_bytes, "Null byte detected in llms.txt")
        self.assertFalse(self.raw_bytes.startswith(b"\xef\xbb\xbf"), "BOM detected in llms.txt")
        self.assertNotIn(b"\r\r\n", self.raw_bytes, "Corrupted double-CRLF detected")


# ===========================================================================
# 2. 100% URL Extraction and Direct ASGI HTTP 200 OK Resolution
# ===========================================================================
class TestLLMsURLExtractionAndASGIResolution(unittest.TestCase):
    """Extract every URL via regex and empirically verify HTTP 200 OK resolution."""

    @classmethod
    def setUpClass(cls):
        cls.content = LLMS_TXT_PATH.read_text(encoding="utf-8")
        # Comprehensive URL regex extraction
        raw_matches = re.findall(r"https?://[^\s)\]]+", cls.content)
        # Clean trailing punctuation that might be markdown/sentence boundaries
        cls.urls = []
        for u in raw_matches:
            cleaned = u.rstrip(").,;:?!'\"")
            cls.urls.append(cleaned)

    def test_u1_extracted_urls_count_and_canonical_domain(self):
        """At least 5 URLs must be found, and all must use canonical domain https://hatekhori.onrender.com."""
        self.assertGreaterEqual(len(self.urls), 7, f"Expected >= 7 URLs, found {len(self.urls)}")
        for u in self.urls:
            self.assertTrue(
                u.startswith("https://hatekhori.onrender.com"),
                f"URL violates canonical domain requirement: '{u}'"
            )

    def test_u2_100_percent_urls_resolve_200_ok(self):
        """EVERY extracted URL must resolve to HTTP 200 OK via FastAPI ASGI client."""
        failed_urls = []
        for url in self.urls:
            path = url.replace("https://hatekhori.onrender.com", "")
            if not path:
                path = "/"
            resp = client.get(path)
            if resp.status_code != 200:
                failed_urls.append((url, path, resp.status_code))

        self.assertEqual(
            len(failed_urls), 0,
            f"The following URLs in llms.txt failed to resolve with HTTP 200: {failed_urls}"
        )

    def test_u3_url_response_content_types_and_payloads(self):
        """Each URL category must return appropriate MIME types and non-empty bodies."""
        for url in self.urls:
            path = url.replace("https://hatekhori.onrender.com", "") or "/"
            resp = client.get(path)
            self.assertEqual(resp.status_code, 200)

            if path.endswith(".png"):
                self.assertIn("image/png", resp.headers.get("content-type", ""))
                self.assertTrue(resp.content.startswith(b"\x89PNG\r\n\x1a\n"), f"Not a valid PNG: {path}")
            elif path.endswith(".xml"):
                self.assertIn("xml", resp.headers.get("content-type", ""))
                self.assertIn("<urlset", resp.text)
            elif path.endswith(".txt"):
                self.assertIn("text/plain", resp.headers.get("content-type", ""))
                self.assertGreater(len(resp.text), 10)
            elif path == "/privacy":
                data = resp.json()
                self.assertIsInstance(data, dict)
                self.assertIn("product", data)
                self.assertIn("model_training", data)
            elif path == "/health":
                data = resp.json()
                self.assertEqual(data.get("status"), "ok")
            else:
                # HTML Pages
                self.assertIn("text/html", resp.headers.get("content-type", ""))
                self.assertIn("<html", resp.text.lower())
                self.assertIn("<title>", resp.text.lower())

    def test_u4_no_dangling_or_malformed_url_schemes(self):
        """Ensure no accidental 'http://', 'localhost', '127.0.0.1' or 'hatekhori.com' URLs."""
        for u in self.urls:
            self.assertTrue(u.startswith("https://"), f"Insecure HTTP URL found: {u}")
            self.assertNotIn("localhost", u)
            self.assertNotIn("127.0.0.1", u)
            self.assertNotIn("hatekhori.com", u)


# ===========================================================================
# 3. Byte Length Bounds (200 - 50,000 bytes) & Strict Token Hygiene
# ===========================================================================
class TestLLMsByteLengthAndTokenHygiene(unittest.TestCase):
    """Assert size boundaries and complete absence of forbidden placeholder tokens."""

    @classmethod
    def setUpClass(cls):
        cls.raw_bytes = LLMS_TXT_PATH.read_bytes()
        cls.text = cls.raw_bytes.decode("utf-8")

    def test_b1_byte_length_between_200_and_50000(self):
        """Byte length of frontend/llms.txt must strictly fall within [200, 50000]."""
        byte_len = len(self.raw_bytes)
        self.assertGreaterEqual(byte_len, 200, f"llms.txt is too small ({byte_len} bytes)")
        self.assertLessEqual(byte_len, 50000, f"llms.txt exceeds upper bound ({byte_len} bytes)")

    def test_b2_absence_of_forbidden_placeholder_tokens(self):
        """Strict check: zero occurrences of forbidden tokens."""
        forbidden_exact = [
            "TODO",
            "TBD",
            "FIXME",
            "localhost",
            "127.0.0.1",
            "hatekhori.com",
            "example.com",
            "lorem ipsum",
        ]
        violations = []
        for token in forbidden_exact:
            # Case-insensitive check for dev placeholders
            matches = list(re.finditer(re.escape(token), self.text, re.IGNORECASE))
            if matches:
                violations.append((token, len(matches)))

        self.assertEqual(
            len(violations), 0,
            f"Forbidden placeholder tokens detected in llms.txt: {violations}"
        )

    def test_b3_word_and_estimated_token_count_in_target_window(self):
        """Word count and approximate token count should be balanced for AI LLM ingestion."""
        words = self.text.split()
        word_count = len(words)
        # Typically 1 word ~= 1.3 to 1.6 tokens for multilingual Indic text
        self.assertGreaterEqual(word_count, 150, f"Word count too low for comprehensive GEO: {word_count}")
        self.assertLessEqual(word_count, 5000, f"Word count too high, risks context overflow: {word_count}")

    def test_b4_no_empty_markdown_link_targets(self):
        """Markdown links [label]() must not have empty target URLs."""
        empty_links = re.findall(r"\[([^\]]+)\]\(\s*\)", self.text)
        self.assertEqual(len(empty_links), 0, f"Found empty markdown links: {empty_links}")


# ===========================================================================
# 4. Script Unicode Character Range Verification
# ===========================================================================
class TestLLMsUnicodeCoverageAndScripts(unittest.TestCase):
    """Stress-test Bengali and Devanagari Unicode character ranges."""

    @classmethod
    def setUpClass(cls):
        cls.text = LLMS_TXT_PATH.read_text(encoding="utf-8")

    def test_s1_bengali_unicode_range_presence(self):
        """Bengali script (U+0980 to U+09FF) must be densely present in llms.txt."""
        bengali_chars = [c for c in self.text if "\u0980" <= c <= "\u09FF"]
        unique_bengali = set(bengali_chars)
        self.assertGreaterEqual(len(bengali_chars), 50, f"Insufficient Bengali chars: {len(bengali_chars)}")
        self.assertGreaterEqual(len(unique_bengali), 30, f"Insufficient distinct Bengali glyphs: {len(unique_bengali)}")

        # Verify specific critical Bengali archetypes
        self.assertIn("হাতে খড়ি", self.text, "Official Bengali branding missing")
        self.assertIn("বাংলা", self.text, "Bengali language token missing")
        self.assertIn("স্বরবর্ণ", self.text, "Vowel section token missing")
        self.assertIn("ব্যঞ্জনবর্ণ", self.text, "Consonant section token missing")
        self.assertIn("যুক্তবর্ণ", self.text, "Conjunct section token missing")
        self.assertIn("শিরোরেখা", self.text, "Shirorekha / top-line token missing")

    def test_s2_devanagari_unicode_range_presence(self):
        """Devanagari / Hindi script (U+0900 to U+097F) must be densely present in llms.txt."""
        devanagari_chars = [c for c in self.text if "\u0900" <= c <= "\u097F"]
        unique_devanagari = set(devanagari_chars)
        self.assertGreaterEqual(len(devanagari_chars), 50, f"Insufficient Devanagari chars: {len(devanagari_chars)}")
        self.assertGreaterEqual(len(unique_devanagari), 30, f"Insufficient distinct Devanagari glyphs: {len(unique_devanagari)}")

        # Verify specific critical Hindi archetypes
        self.assertIn("हिन्दी", self.text, "Hindi language token missing")
        self.assertIn("स्वर", self.text, "Swar token missing")
        self.assertIn("व्यंजन", self.text, "Vyanjan token missing")
        self.assertIn("संयुक्ताक्षर", self.text, "Samyuktakshar token missing")
        self.assertIn("शिरोरेखा", self.text, "Shirorekha Devanagari token missing")

    def test_s3_unicode_normalization_stability(self):
        """Ensure Unicode encoding integrity, lack of replacement characters, and correct atomic Indic codepoints."""
        # 1. No replacement character U+FFFD
        self.assertNotIn("\ufffd", self.text, "Replacement character U+FFFD detected in llms.txt")

        # 2. Atomic Bengali nukta consonants U+09DC (ড়), U+09DD (ঢ়), U+09DF (য়)
        # In Unicode CompositionExclusions.txt, these decompose under NFC/NFD to base+nukta
        # but modern Bengali typography requires atomic codepoints for OpenType cmap mapping.
        self.assertIn("\u09dc", self.text, "Atomic Bengali ড় (U+09DC) must be present for OpenType cmap mapping")
        self.assertIn("\u09dd", self.text, "Atomic Bengali ঢ় (U+09DD) must be present for OpenType cmap mapping")
        self.assertIn("\u09df", self.text, "Atomic Bengali য় (U+09DF) must be present for OpenType cmap mapping")

        # 3. Roundtrip UTF-8 encoding stability
        encoded = self.text.encode("utf-8")
        decoded = encoded.decode("utf-8")
        self.assertEqual(self.text, decoded, "UTF-8 roundtrip decode mismatch")

        # 4. NFC normalization retains exact line count and semantic content
        nfc_normalized = unicodedata.normalize("NFC", self.text)
        self.assertEqual(len(self.text.splitlines()), len(nfc_normalized.splitlines()))
        self.assertIn("হাতে খড়ি", nfc_normalized)
        self.assertIn("বাংলা", nfc_normalized)
        self.assertIn("हिन्दी", nfc_normalized)


# ===========================================================================
# 5. GEO Direct Answer & 5-Foundry Matrix Parity
# ===========================================================================
class TestLLMsGEOParityAndContentDepth(unittest.TestCase):
    """Verify presence of key generative search engine optimization structures."""

    @classmethod
    def setUpClass(cls):
        cls.text = LLMS_TXT_PATH.read_text(encoding="utf-8")

    def test_g1_front_loaded_direct_answer_summary(self):
        """Direct Answer Summary must appear within the first 1,000 characters."""
        self.assertIn("## Direct Answer Summary", self.text)
        pos = self.text.find("## Direct Answer Summary")
        self.assertLess(pos, 1000, f"Direct answer placed too deep ({pos} chars from top)")

    def test_g2_direct_answer_word_count(self):
        """Direct answer must be concise (between 30 and 120 words) for AI quote extraction."""
        match = re.search(r"## Direct Answer Summary\s*\n+([^#]+)", self.text)
        self.assertIsNotNone(match, "Could not extract Direct Answer paragraph")
        para = match.group(1).strip()
        word_count = len(para.split())
        self.assertGreaterEqual(word_count, 30, f"Direct answer too terse: {word_count} words")
        self.assertLessEqual(word_count, 120, f"Direct answer too verbose: {word_count} words")

    def test_g3_5_foundry_competitive_matrix(self):
        """Matrix must compare Hatekhori against Calligraphr, Lipighor, Fontself, and FontCrafter."""
        matrix_header = [l for l in self.text.splitlines() if "Feature / Criteria" in l]
        self.assertEqual(len(matrix_header), 1, "Matrix header not found")
        header_text = matrix_header[0]
        self.assertIn("Hatekhori", header_text)
        self.assertIn("Calligraphr", header_text)
        self.assertIn("Lipighor", header_text)
        self.assertIn("Fontself", header_text)
        self.assertIn("FontCrafter", header_text)

    def test_g4_faq_question_count(self):
        """FAQ section must contain at least 6 direct Q&A pairs in H3 format."""
        faq_match = re.search(r"## Frequently Asked Questions.*?\n+(.*?)(\n## |\Z)", self.text, re.DOTALL)
        self.assertIsNotNone(faq_match, "FAQ section missing")
        faq_body = faq_match.group(1)
        questions = re.findall(r"^###\s+(.*\?)", faq_body, re.MULTILINE)
        self.assertGreaterEqual(len(questions), 6, f"Expected >= 6 FAQ questions, found {len(questions)}")


# ===========================================================================
# 6. Adversarial Parsing & AI Ingestion Stress Simulation
# ===========================================================================
class TestLLMsAdversarialParsingSimulation(unittest.TestCase):
    """Stress-test AI scraper markdown parsing and FastAPI route serving."""

    def test_a1_fastapi_route_serves_exact_file_content(self):
        """GET /llms.txt on the backend must serve exact byte content as on disk."""
        resp = client.get("/llms.txt")
        self.assertEqual(resp.status_code, 200)
        disk_bytes = LLMS_TXT_PATH.read_bytes()
        self.assertEqual(resp.content, disk_bytes, "FastAPI /llms.txt content diverged from disk")

    def test_a2_fastapi_route_headers(self):
        """Verify headers on /llms.txt include standard nosniff security headers."""
        resp = client.get("/llms.txt")
        self.assertIn("text/plain", resp.headers.get("content-type", ""))
        self.assertEqual(resp.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(resp.headers.get("x-frame-options"), "DENY")

    def test_a3_adversarial_naive_markdown_stripping_retains_meaning(self):
        """When stripped of markdown symbols, the resulting plain text remains clean."""
        text = LLMS_TXT_PATH.read_text(encoding="utf-8")
        # Strip ATX markers, blockquotes, bullets, links, table pipes
        cleaned = re.sub(r"#{1,6}\s*", "", text)
        cleaned = re.sub(r"^>\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"^\s*[-*]\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\|", " ", cleaned)
        cleaned = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", cleaned)
        self.assertGreater(len(cleaned), 5000, "Cleaned text unexpectedly truncated")
        self.assertIn("Hatekhori", cleaned)
        self.assertIn("Bengali", cleaned)
        self.assertIn("Hindi", cleaned)


if __name__ == "__main__":
    unittest.main(verbosity=2)
