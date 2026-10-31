"""Tests for build.py's option handling. Run: python plugins/brush-kanji/tests/test_build.py"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1] / "skills" / "brush-kanji" / "build.py"

# Two strokes in KanjiVG's shape, enough for the parser; no network needed.
FIXTURE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:kvg="http://kanjivg.tagaini.net"
 viewBox="0 0 109 109"><g id="kvg:StrokePaths_04e8c"><g id="kvg:04e8c" kvg:element="二">
<path id="kvg:04e8c-s1" kvg:type="㇐" d="M30,40h50"/>
<path id="kvg:04e8c-s2" kvg:type="㇐" d="M20,70h70"/>
</g></g></svg>
"""


def build(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    svg = tmp / "ni.svg"
    svg.write_text(FIXTURE_SVG, encoding="utf-8")
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(BUILD), str(svg), "--out", str(tmp / "out.html"), *args],
        capture_output=True, text=True, encoding="utf-8",
    )


class InkOption(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def page(self) -> str:
        return (self.tmp / "out.html").read_text(encoding="utf-8")

    def test_default_ink_is_near_black(self):
        r = build(self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('ink:"#141414"', self.page())

    def test_ink_is_lowercased_into_cfg(self):
        r = build(self.tmp, "--ink", "#5B2A86")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('ink:"#5b2a86"', self.page())
        self.assertNotIn("#5B2A86", self.page())

    def test_non_hex_ink_is_rejected(self):
        r = build(self.tmp, "--ink", "red")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--ink must be a six-digit hex color", r.stderr)
        self.assertFalse((self.tmp / "out.html").exists())

    def test_cfg_is_declared_before_the_engine(self):
        # The engine reads CFG.ink at load time, so the page must declare CFG first.
        build(self.tmp)
        page = self.page()
        self.assertLess(page.index("const CFG="), page.index("INK=CFG.ink"))
        self.assertNotIn("{{", page)


if __name__ == "__main__":
    unittest.main()
