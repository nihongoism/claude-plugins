"""Build a brush-written kanji page from KanjiVG stroke data.

    python build.py 木 --reading ki --meaning tree
    python build.py 06728.svg --out ki-brush.html --base 3.0 --captions captions.html
    python build.py strokes.json --out ki-brush.html

The source is a single character (its KanjiVG file is downloaded from GitHub), a KanjiVG
SVG file, or a JSON file with "character" and "svg" fields such as a stroke-order MCP returns.

Brush size defaults from the stroke count (3.5 for 4 strokes, 1.8 for 24); override with --base
when the strokes merge (too big) or look wiry (too small). --captions takes an HTML fragment
(an <ol> of per-stroke lines or a <dl> of component labels) placed under the sheet.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
KANJIVG_URL = "https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/{:05x}.svg"
ATTRIBUTION = ('Stroke data from <a href="https://kanjivg.tagaini.net/">KanjiVG</a>, '
               '<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0</a>.')
DEFAULT_NOTE = ("A simulation: brush shape, pressure and dry-brush texture are modeled on the KanjiVG "
                "centerlines and stroke types, not traced from a calligrapher's work.")


def fetch_kanjivg(kanji: str) -> str:
    url = KANJIVG_URL.format(ord(kanji))
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.exit(f"KanjiVG has no file for {kanji} ({url})")
        raise


def read_source(source: str):
    """Return (character or None, SVG text) from a character, a JSON file or an SVG file."""
    path = Path(source)
    if len(source) == 1 and not path.exists():
        return source, fetch_kanjivg(source)
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("{"):
        data = json.loads(text)
        return data.get("character"), data["svg"]
    return None, text


def parse_strokes(svg: str):
    """KanjiVG <path> elements in writing order, as [type, d] pairs."""
    strokes = []
    for tag in re.findall(r"<path\b[^>]*>", svg):
        m_id = re.search(r'id="[^"]*-s(\d+)"', tag)
        m_d = re.search(r'\bd="([^"]*)"', tag)
        if not m_id or not m_d:
            continue
        m_type = re.search(r'kvg:type="([^"]*)"', tag)
        strokes.append((int(m_id.group(1)), m_type.group(1) if m_type else "㇐", m_d.group(1)))
    strokes.sort()
    return [[t, d] for _, t, d in strokes]


def default_base(n: int) -> float:
    # 3.5 looked right for 木 (4 strokes) and 1.8 for 靄 (24); a power law joins them.
    return round(min(4.5, 3.5 * (4 / n) ** 0.37), 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="a character, a KanjiVG SVG file, or a JSON file with character and svg")
    ap.add_argument("--out", type=Path, help="output page (default brush-<character>.html)")
    ap.add_argument("--kanji", help="override the character read from the data")
    ap.add_argument("--reading", default="", help="romanized reading for the subtitle, e.g. ki")
    ap.add_argument("--meaning", default="", help="gloss for the subtitle, e.g. tree")
    ap.add_argument("--base", type=float, help="brush half-width in KanjiVG units (default from stroke count)")
    ap.add_argument("--speed", type=float, help="units per ms (default .075 up to 8 strokes, else .1)")
    ap.add_argument("--gap", type=int, help="ms between strokes (default 380 up to 8 strokes, else 200)")
    ap.add_argument("--captions", type=Path, help="HTML fragment placed under the sheet")
    ap.add_argument("--note", help="replace the default simulation note (the KanjiVG attribution stays)")
    a = ap.parse_args()

    kanji, svg = read_source(a.source)
    strokes = parse_strokes(svg)
    if not strokes:
        sys.exit("no KanjiVG <path> elements found in " + a.source)
    if kanji is None:
        m = re.search(r'kvg:element="(.)"', svg)
        kanji = m.group(1) if m else "?"
    kanji = a.kanji or kanji
    n = len(strokes)
    base = a.base if a.base is not None else default_base(n)
    speed = a.speed if a.speed is not None else (0.075 if n <= 8 else 0.1)
    gap = a.gap if a.gap is not None else (380 if n <= 8 else 200)
    out = a.out or Path(f"brush-{kanji}.html")

    sub = ", ".join(x for x in (a.reading, a.meaning) if x)
    subtitle = f"{sub} · {n} strokes" if sub else f"{n} strokes"
    captions = a.captions.read_text(encoding="utf-8").rstrip() if a.captions else ""
    note = (a.note or DEFAULT_NOTE) + " " + ATTRIBUTION

    template = (HERE / "template.html").read_text(encoding="utf-8")
    engine = (HERE / "brush-engine.js").read_text(encoding="utf-8").rstrip()
    logo = (HERE / "nihongoism-logo.svg").read_text(encoding="utf-8")
    logo = re.sub(r"^<\?xml[^>]*\?>", "", logo).strip()
    strokes_js = "[\n" + ",\n".join(json.dumps(s, ensure_ascii=False) for s in strokes) + "\n]"
    page = (template
            .replace("{{KANJI}}", kanji)
            .replace("{{SUBTITLE}}", subtitle)
            .replace("{{CAPTIONS}}", captions)
            .replace("{{NOTE}}", note)
            .replace("{{LOGO}}", logo)
            .replace("{{STROKES}}", strokes_js)
            .replace("{{BASE}}", repr(base))
            .replace("{{SPEED}}", repr(speed))
            .replace("{{GAP}}", str(gap))
            .replace("{{ENGINE}}", engine))
    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"{kanji}: {n} strokes, base {base}, speed {speed}, gap {gap} -> {out}")


if __name__ == "__main__":
    main()
