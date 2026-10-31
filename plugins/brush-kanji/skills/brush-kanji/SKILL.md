---
name: brush-kanji
description: >
  Draws a kanji (or kana) the way a brush writes it in standard script (楷書 kaisho): an animated
  page that brushes the character stroke by stroke onto paper, with angled entries, pressed stops,
  hooks, tapering sweeps and dry brush, built on KanjiVG stroke data. Use when the user asks to
  draw or write a character "with a brush", "in brush style", "like calligraphy", "as a
  calligrapher would", "brush-drawn", "in shodō style", or says "/brush-kanji". Also the
  reference for how brush strokes should look when any other rendering of kanji strokes is being
  judged or improved.
---
# Brush Kanji

Produces an HTML page that animates a character brushed onto hanshi paper, one stroke at a time, with a **Brush again** button and optional guide lines. The brushwork is simulated on top of KanjiVG centerlines; the rules below say what the simulation imitates and why. 木 (4 strokes) and 靄 (24 strokes) are the reference examples; both are in the plugin's `examples/` folder.

## Workflow

### 1. Build the page

```
python "${CLAUDE_SKILL_DIR}/build.py" 木 --out ki-brush.html --reading ki --meaning tree
```

Given a single character, the script downloads its KanjiVG file from GitHub. When there is no network, or a stroke-order MCP has already returned the data, pass a file instead: a KanjiVG SVG, or a JSON file with `character` and `svg` fields (the `svg` holds `<path>` elements in writing order, each with a `kvg:type` stroke symbol and a `d` centerline in a 109 × 109 square). Save MCP output verbatim to a file in the working folder and pass that path.

Options: `--base` (brush half-width, see Scale below), `--speed`, `--gap`, `--captions file.html` (an HTML fragment under the sheet: an `<ol>` describing each stroke for a simple character, or a `<dl>` naming the components and their stroke ranges for a dense one, as the 靄 example does), `--note` to replace the simulation disclaimer, `--ink #rrggbb` for a colored ink (`#b8321a` is vermilion; the edge bleed follows the color). The KanjiVG attribution in the footer always stays. The script inlines `template.html` and `brush-engine.js`, so the output is a single self-contained file.

### 2. Look at it only when there is reason to

The default brush size is a formula from the stroke count and has held from 4 to 24 strokes, so a routine character goes straight to delivery. Check the page in a browser first only when the character is unusually dense or unusual in shape (a long-tailed or heavily nested form), when `--base` was set by hand, or when the user asks for a check: open the file, wait for the animation to finish, screenshot it, and compare it with the Pitfalls table. Strokes merging means `--base` is too large, wiry strokes mean too small.

### 3. Deliver

Publish it as an artifact (title `<kanji> in Brush`, icon `brush`) or hand over the file. For a still image, screenshot the sheet with the animation complete and crop to the paper.

## Brush technique the renderer imitates

In standard script the brush tip always points toward the upper left, and almost every visible feature follows from that one fact. Each stroke has three phases: 起筆 *kihitsu* (entry), 送筆 *sōhitsu* (travel) and 収筆 *shūhitsu* (ending).

| Stroke | Entry | Travel | Ending |
|---|---|---|---|
| Horizontal 横 *yoko* | Tip lands at an angle, belly presses down-right: a slanted head | Lighter; thins slightly in the middle | とめ *tome*: press down-right, lift back, rounded end |
| Vertical 縦 *tate* | Same angled press, heavier | Heavier than horizontals | とめ stop, or a hook |
| Left sweep 左払い *hidari-harai* | Full press | Speeds up and lifts steadily | Tapers to a point, breaking into dry brush かすれ *kasure* |
| Right sweep 右払い *migi-harai* | Light, thin start | Presses down progressively | A flat-bottomed foot that flares out to a knife-edge tip |
| Dot 点 *ten* | Tip touches | Belly presses in | A short rounded press, not a seed shape |
| Hook はね *hane* (end of a vertical or turn) | | Stop and gather the brush | A short, fast flick that tapers off |
| Corner 折れ *ore* (inside a turning stroke) | | Slight lift before the turn | Re-press on the new direction, leaving an angled shoulder |

Three habits sell the look more than any single stroke:

- **Weight contrast.** Verticals carry more ink than horizontals.
- **Rhythm.** The brush slows at entries, corners and stops and speeds through sweeps, which is where dry brush appears.
- **Scale.** The brush is wide relative to the square for a simple character and must be set much finer for a dense one, or the strokes merge. Half-width 3.5 units suited 木 (4 strokes), 1.8 suited 靄 (24). `build.py` interpolates between them from the stroke count.

## How the engine draws a stroke

Each stroke is one filled outline around the KanjiVG centerline, plus brush footprints where the brush presses, with dry-brush streaks cut out of the ink. Never stamp circles along the path; that was the first version, and every lump and blob came from it.

1. **Sample the centerline** at 0.25 units per step and record the direction at each point.
2. **Classify the stroke** from its type symbol (the last one when two are given, as in `㇔/㇑`): ㇆ ㇚ ㇟ ㇂ are hooks; ㇔ a dot; ㇒ a left sweep; ㇏ a right sweep, or a dot when shorter than 12 units; everything else ends in a stop.
3. **Find corners and hooks.** A corner is a turn of more than 0.75 radians over a 1.4-unit window. A hook is the tail after the last change of direction, 1.5 to 8 units long.
4. **Width profile per family**, a half-width along the stroke times the page's brush size: stop or hook strokes run about 0.82 for horizontals up to 1.15 for verticals, horizontals thinning 5 to 13% in the middle; a left sweep starts at 1.06 and falls to a point over its last 85%; a right sweep starts at 0.32 and swells to 1.45 by 80%, then one edge stays flat while the other tapers fast; a dot runs 0.6 to 1.1 and is shortened to its pressed part; a 7% dip precedes each corner.
5. **Footprints**: ellipses on a 45° axis with the tip pulled toward the upper left, at the entry (body clipped behind a slanted edge so the head is not a round cap), at each corner, before a hook, and at a stop (pressed down-right).
6. **Dry brush**: about 14 bristle lines along the stroke, erased in streaks where dryness is high (the second half of a left sweep, the end of a right sweep, a hook's flick), with a faint grain everywhere so the ink is not flat.
7. **Timing**: base speed about 0.1 units per ms, half speed at entries, slower at corners, up to 2.5× through sweeps, short pauses at corners and hooks, 200 to 380 ms between strokes.
8. **Ink**: 97% opacity with a faint edge blur, so crossings darken a little and the edge bleeds into the paper. All randomness is seeded from the stroke index so a replay draws the same character.

These live in `brush-engine.js`; the comments name each rule (起筆, 折れ, はね, とめ, かすれ). Change a shape there, not in the generated pages, so every character benefits.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Lumpy, knobby joints and ends | Stamps pile up where the brush slows | One filled outline per stroke; footprints only where the brush presses |
| Round blobs at stroke starts | A circle has no direction | Angled footprint with the body clipped behind a slanted edge |
| Dots shaped like seeds | Symmetric taper at both ends | Tip-to-belly press: thin start, heavy rounded end, shortened stroke |
| Uniform, mechanical width | One width for every stroke | Per-type profiles, verticals heavier than horizontals |
| Strokes merging in dense characters | Brush sized for simple ones | Smaller `--base` |
| Dry brush that looks like noise | Random gaps everywhere | Gaps only where the brush runs dry, as long streaks along the stroke |

The result is a simulation over KanjiVG's centerlines, not a calligrapher's hand: proportions and spacing come from the font data. Say so in the page note and when describing it.

## Sources

- [Takase Shodokai, Learn Japanese Calligraphy, lesson 2](https://takase.com/learn-japanese-calligraphy/lesson-2/), with [lesson 5](https://takase.com/learn-japanese-calligraphy/lesson-5/) and [lesson 6](https://takase.com/learn-japanese-calligraphy/lesson-6/)
- [shodo-kanji.com on 折れ and はね](https://shodo-kanji.com/a3-4-6brush_stroke.html)
- [一禅堂 on とめ, はね and はらい](https://www.ichizenn.com/kanji/rules/tome-hane-harai.html)
- [30shikakuron on はね and はらい](https://30shikakuron.com/tomehane-tips3.html)
- [Eight Principles of Yong](https://en.wikipedia.org/wiki/Eight_Principles_of_Yong)
- Wikimedia Commons: 姚孟起's copy of 九成宮醴泉銘 and 永字八法 diagrams
- [KanjiVG](https://kanjivg.tagaini.net/), the stroke data (CC BY-SA 3.0)
- The write-up these rules came from: [Drawing Brush-Written Kanji from KanjiVG](https://claude.ai/artifact/6naPtAEswPWoLZZjok4JKW)
