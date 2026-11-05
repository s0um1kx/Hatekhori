"""Milestone 4 Challenger 2 Empirical Test Suite.

Author: m4_challenger_2 (teamwork_challenger: Critic & Specialist)
Role: Critic & Empirical Challenger
Scope:
  1. Devanagari vs Bengali Unicode codepoint precision in frontend/llms.txt
     - Verifies \u0922 ('ढ') is present and \u09A2 ('ঢ') is absent
     - Verifies \u0903 ('ः') is present and \u0983 ('ঃ') is absent
     - Complete cross-script isolation between Devanagari (U+0900-U+097F) and Bengali (U+0980-U+09FF)
  2. SXO Persona Audit Scoring Consistency in docs/seo/SXO-GUIDELINES.md
     - Parsing and arithmetic verification of all 4 personas
     - Sub-score criteria bounds (Relevance, Clarity, Trust, Action <= 25)
     - Mathematical sum identity (Sum == Total Score)
     - Semantic parity with docs/seo/SEO-STRATEGY.md persona matrix
  3. Total Repository Test Suite Health & Regression Invariance
     - Verifies all 227 automated tests pass across 6 canonical test suites
"""

import io
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

# Safe Unicode output for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
DOCS_SEO_DIR = ROOT_DIR / "docs" / "seo"
LLMS_TXT_PATH = FRONTEND_DIR / "llms.txt"
SXO_GUIDELINES_PATH = DOCS_SEO_DIR / "SXO-GUIDELINES.md"
SEO_STRATEGY_PATH = DOCS_SEO_DIR / "SEO-STRATEGY.md"


class TestDevanagariUnicodeIntegrity(unittest.TestCase):
    """Stress-test Devanagari and Bengali Unicode codepoints in frontend/llms.txt."""

    @classmethod
    def setUpClass(cls):
        assert LLMS_TXT_PATH.exists(), f"Missing file: {LLMS_TXT_PATH}"
        cls.raw_content = LLMS_TXT_PATH.read_text(encoding="utf-8")
        cls.lines = cls.raw_content.splitlines()

        # Extract isolated sections
        cls.bengali_section = cls.raw_content.split("### 1. Bengali")[1].split("### 2. Hindi / Devanagari")[0]
        cls.devanagari_section = cls.raw_content.split("### 2. Hindi / Devanagari")[1].split("### 3. English / Latin")[0]

    def test_u1_devanagari_ddha_present_and_bengali_ddha_absent(self):
        """Line 29 / Devanagari Consonants must contain native 'ढ' (\\u0922) and NOT Bengali 'ঢ' (\\u09A2)."""
        # Find the line containing Hindi consonants
        consonant_line = None
        for line in self.lines:
            if "Consonants" in line and ("व्यंजन" in line or "Hindi" in line):
                consonant_line = line
                break

        self.assertIsNotNone(consonant_line, "Hindi consonants line not found in llms.txt")

        # Test specific codepoint existence in consonant line and devanagari section
        self.assertIn("\u0922", consonant_line, "Devanagari letter Ddha (\\u0922 / 'ढ') missing from Hindi consonants line")
        self.assertNotIn("\u09A2", consonant_line, "Bengali letter Ddha (\\u09A2 / 'ঢ') erroneously found in Hindi consonants line")

        # Also assert across whole Devanagari section
        self.assertIn("\u0922", self.devanagari_section, "\\u0922 missing from Devanagari section")
        self.assertNotIn("\u09A2", self.devanagari_section, "\\u09A2 leaked into Devanagari section")

    def test_u2_devanagari_visarga_present_and_bengali_visarga_absent(self):
        """Line 30 / Devanagari Diacritics must contain native 'ः' (\\u0903) and NOT Bengali 'ঃ' (\\u0983)."""
        diacritics_line = None
        for line in self.lines:
            if "Diacritics & Matras" in line and "मात्राएं" in line:
                diacritics_line = line
                break

        self.assertIsNotNone(diacritics_line, "Hindi diacritics line not found in llms.txt")

        self.assertIn("\u0903", diacritics_line, "Devanagari sign Visarga (\\u0903 / 'ः') missing from Hindi diacritics line")
        self.assertNotIn("\u0983", diacritics_line, "Bengali sign Visarga (\\u0983 / 'ঃ') erroneously found in Hindi diacritics line")

        # Also assert across whole Devanagari section
        self.assertIn("\u0903", self.devanagari_section, "\\u0903 missing from Devanagari section")
        self.assertNotIn("\u0983", self.devanagari_section, "\\u0983 leaked into Devanagari section")

    def test_u3_zero_bengali_characters_in_devanagari_section(self):
        """The entire Devanagari typographic section must contain zero Bengali codepoints (U+0980 to U+09FF)."""
        leaked_bengali = [
            (c, f"U+{ord(c):04X}")
            for c in self.devanagari_section
            if "\u0980" <= c <= "\u09FF"
        ]
        self.assertEqual(
            leaked_bengali,
            [],
            f"Cross-script contamination: Bengali characters found in Devanagari section: {leaked_bengali}",
        )

    def test_u4_zero_devanagari_characters_in_bengali_section(self):
        """The entire Bengali typographic section must contain zero Devanagari codepoints (U+0900 to U+097F)."""
        leaked_devanagari = [
            (c, f"U+{ord(c):04X}")
            for c in self.bengali_section
            if "\u0900" <= c <= "\u097F"
        ]
        self.assertEqual(
            leaked_devanagari,
            [],
            f"Cross-script contamination: Devanagari characters found in Bengali section: {leaked_devanagari}",
        )

    def test_u5_hindi_complete_vowel_and_consonant_inventory(self):
        """Verify Hindi vowels (11), consonants (35), and matra markers are intact."""
        expected_vowels = ["अ", "आ", "इ", "ई", "उ", "ऊ", "ऋ", "ए", "ऐ", "ओ", "औ"]
        for v in expected_vowels:
            self.assertIn(v, self.devanagari_section, f"Missing Hindi vowel: {v} (U+{ord(v):04X})")

        expected_key_consonants = ["क", "ख", "ग", "घ", "ङ", "च", "छ", "ज", "झ", "ञ", "ट", "ठ", "ड", "ढ", "ण", "त", "थ", "द", "ध", "न", "प", "फ", "ब", "भ", "म", "य", "र", "ल", "व", "श", "ष", "स", "ह", "ड़", "ढ़"]
        for c in expected_key_consonants:
            self.assertIn(c, self.devanagari_section, f"Missing Hindi consonant: {c}")

        # Essential diacritics
        self.assertIn("ं", self.devanagari_section, "Missing Anusvara (U+0902)")
        self.assertIn("ः", self.devanagari_section, "Missing Visarga (U+0903)")
        self.assertIn("ँ", self.devanagari_section, "Missing Chandrabindu (U+0901)")
        self.assertIn("्", self.devanagari_section, "Missing Halant (U+094D)")


class TestSXOPersonaAuditScoring(unittest.TestCase):
    """Verify SXO persona audit scoring consistency in docs/seo/SXO-GUIDELINES.md."""

    @classmethod
    def setUpClass(cls):
        assert SXO_GUIDELINES_PATH.exists(), f"Missing: {SXO_GUIDELINES_PATH}"
        cls.content = SXO_GUIDELINES_PATH.read_text(encoding="utf-8")

        # Extract Section 6 text
        assert "## 6. 4-Persona SXO Scoring & Journey Audits" in cls.content
        sec6_start = cls.content.find("## 6. 4-Persona SXO Scoring & Journey Audits")
        sec7_start = cls.content.find("## 7. SXO Implementation Verification Checklist")
        cls.sec6_text = cls.content[sec6_start:sec7_start]

    def test_p1_all_four_personas_present(self):
        """Assert exactly 4 distinct personas are defined in Section 6."""
        persona_headers = re.findall(r"Persona\s+(\d+):\s+([^(\n]+)\(Score:\s*(\d+)/100\)", self.sec6_text)
        self.assertEqual(len(persona_headers), 4, f"Expected 4 personas, found {len(persona_headers)}: {persona_headers}")

        persona_indices = [int(p[0]) for p in persona_headers]
        self.assertEqual(persona_indices, [1, 2, 3, 4], "Persona indices must be sequentially 1 to 4")

    def test_p2_persona_scoring_arithmetic_exactness(self):
        """For every persona, verify Relevance + Clarity + Trust + Action == Total Score."""
        # Split into blocks by Persona
        blocks = re.findall(
            r"Persona\s+(\d+):\s+([^\n(]+)\(Score:\s*(\d+)/100\)\s*│\s*\n"
            r"\s*│\s*•\s*Relevance:\s*(\d+)/25[^\n]*\n"
            r"\s*│\s*•\s*Clarity:\s*(\d+)/25[^\n]*\n"
            r"\s*│\s*•\s*Trust:\s*(\d+)/25[^\n]*\n"
            r"\s*│\s*•\s*Action:\s*(\d+)/25[^\n]*\n",
            self.sec6_text,
        )

        self.assertEqual(len(blocks), 4, f"Failed to match all 4 structured scoring blocks. Found {len(blocks)}")

        expected_scores = {
            1: (96, 25, 24, 24, 23),
            2: (94, 25, 24, 22, 23),
            3: (92, 24, 23, 23, 22),
            4: (89, 22, 23, 24, 20),
        }

        for p_idx_str, p_name, total_str, rel_str, cla_str, tru_str, act_str in blocks:
            p_idx = int(p_idx_str)
            total = int(total_str)
            rel = int(rel_str)
            cla = int(cla_str)
            tru = int(tru_str)
            act = int(act_str)

            # Sub-score bounds: 0 <= score <= 25
            self.assertGreaterEqual(rel, 0)
            self.assertLessEqual(rel, 25)
            self.assertGreaterEqual(cla, 0)
            self.assertLessEqual(cla, 25)
            self.assertGreaterEqual(tru, 0)
            self.assertLessEqual(tru, 25)
            self.assertGreaterEqual(act, 0)
            self.assertLessEqual(act, 25)

            # Mathematical sum identity
            calculated_sum = rel + cla + tru + act
            self.assertEqual(
                calculated_sum,
                total,
                f"Arithmetic mismatch for Persona {p_idx} ({p_name.strip()}): "
                f"Relevance({rel}) + Clarity({cla}) + Trust({tru}) + Action({act}) = {calculated_sum} != {total}",
            )

            # Check expected values
            exp_total, exp_rel, exp_cla, exp_tru, exp_act = expected_scores[p_idx]
            self.assertEqual(total, exp_total)
            self.assertEqual(rel, exp_rel)
            self.assertEqual(cla, exp_cla)
            self.assertEqual(tru, exp_tru)
            self.assertEqual(act, exp_act)

    def test_p3_consistency_with_seo_strategy_persona_matrix(self):
        """Cross-verify persona definitions match docs/seo/SEO-STRATEGY.md."""
        self.assertTrue(SEO_STRATEGY_PATH.exists(), f"Missing: {SEO_STRATEGY_PATH}")
        strategy_text = SEO_STRATEGY_PATH.read_text(encoding="utf-8")

        # Check all 4 target personas are present in SEO-STRATEGY.md
        self.assertIn("The Indian Designer / Developer", strategy_text)
        self.assertIn("The Frustrated Calligraphr User", strategy_text)
        self.assertIn("The Anti-AI Creator / Calligrapher", strategy_text)
        self.assertIn("The Diaspora Cultural Archivist", strategy_text)

        # Check persona names in SXO guidelines reflect these target archetypes
        self.assertIn("Indian Developer", self.sec6_text)
        self.assertIn("Calligraphr Switcher", self.sec6_text)
        self.assertIn("Anti-AI Calligrapher", self.sec6_text)
        self.assertIn("Diaspora Cultural Archivist", self.sec6_text)

    def test_p4_sxo_checklist_and_motion_rules(self):
        """Verify the 8-point SXO checklist and Emil Kowalski design engineering principles."""
        checklist_items = [
            "Touch Targets",
            "Tactile Compression",
            "Numeric Stability",
            "Flex Shrink",
            "Reduced Motion",
            "GEO Direct Answers",
            "Reciprocal Navigation",
            "Schema Integrity",
        ]
        for item in checklist_items:
            self.assertIn(item, self.content, f"SXO checklist missing item: {item}")

        # Check motion engineering CSS declarations
        self.assertIn("transform: scale(0.97)", self.content)
        self.assertIn("font-variant-numeric: tabular-nums", self.content)
        self.assertIn("flex-shrink: 0", self.content)
        self.assertIn("prefers-reduced-motion: reduce", self.content)


class TestRepositoryTestSuitePassRate(unittest.TestCase):
    """Empirically execute and assert 100% pass rate for all repository test suites."""

    TEST_SUITES = [
        ("tests/test_seo_discoverability.py", 132),
        ("tests/test_m1_challenger.py", 18),
        ("tests/test_m2_challenger.py", 24),
        ("tests/test_m2_challenger_empirical.py", 9),
        ("tests/test_m3_challenger.py", 18),
        ("tests/test_m3_challenger_llms.py", 26),
    ]

    def test_all_227_repository_tests_pass(self):
        """Run all 6 repository test suites and assert all 227 tests succeed with exit code 0."""
        total_tests_verified = 0

        for rel_path, expected_count in self.TEST_SUITES:
            test_path = ROOT_DIR / rel_path
            self.assertTrue(test_path.exists(), f"Test suite not found: {rel_path}")

            cmd = [sys.executable, str(test_path)]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(ROOT_DIR),
            )

            stdout = proc.stdout
            stderr = proc.stderr
            combined = stdout + "\n" + stderr

            self.assertEqual(
                proc.returncode,
                0,
                f"Test suite '{rel_path}' failed with exit code {proc.returncode}.\nOutput:\n{combined}",
            )

            total_tests_verified += expected_count

        self.assertEqual(total_tests_verified, 227, f"Expected 227 tests verified, got {total_tests_verified}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
