<a href="https://nihongoism.com"><img src="skills/brush-kanji/nihongoism-logo.svg" alt="Nihongoism" width="260"></a>

# brush-kanji

A Claude Code skill from [Nihongoism](https://nihongoism.com), the newsletter that explores Japanese one word at a time. It draws a kanji the way a brush writes it. Ask for a character "with a brush" and you get a self-contained HTML page that brushes it onto paper stroke by stroke, in standard script (楷書): angled entries, pressed stops, hooks, tapering sweeps, dry brush at the ends of sweeps, verticals heavier than horizontals.

The stroke centerlines come from [KanjiVG](https://kanjivg.tagaini.net/). Everything else, the width of each stroke along its length, the footprints where the brush presses, the dry-brush streaks and the timing, is simulated by a small canvas engine from rules drawn from calligraphy instruction. [`skills/brush-kanji/SKILL.md`](skills/brush-kanji/SKILL.md) spells the rules out.

Open [`examples/ki.html`](examples/ki.html) (木, 4 strokes) or [`examples/moya.html`](examples/moya.html) (靄, 24 strokes) in a browser to see the result.

## Install

As a Claude Code plugin:

```
/plugin marketplace add nihongoism/claude-plugins
/plugin install brush-kanji@nihongoism
```

Or as a plain skill, by copying `skills/brush-kanji/` to `~/.claude/skills/brush-kanji/`. Or, for claude.ai, zip the `skills/brush-kanji/` folder and upload it under Customize › Skills; the build step runs in the code-execution sandbox.

Python 3.8 or later is the only requirement.

## Use

In Claude Code, ask for a character with a brush, or type `/brush-kanji 永`. Claude runs the build script, checks the page in a browser and hands it over.

The script also works on its own:

```
python skills/brush-kanji/build.py 木 --reading ki --meaning tree
```

That downloads 木's KanjiVG file and writes `brush-木.html`. It also accepts a KanjiVG SVG file, or a JSON file with `character` and `svg` fields such as a stroke-order MCP server returns. Options:

| Option | Effect |
|---|---|
| `--out FILE` | Output path |
| `--base N` | Brush half-width in KanjiVG units. Defaults from the stroke count, 3.5 for 4 strokes down to 1.8 for 24. Lower it if strokes merge, raise it if they look wiry |
| `--speed N`, `--gap MS` | Animation speed in units per ms and pause between strokes |
| `--reading`, `--meaning` | Text for the subtitle |
| `--captions FILE` | HTML fragment placed under the sheet, such as a list describing each stroke |
| `--note TEXT` | Replaces the simulation disclaimer in the footer |

## Layout

```
.claude-plugin/        plugin manifest and icon
skills/brush-kanji/
  SKILL.md             the rules and the workflow Claude follows
  build.py             character or KanjiVG data in, finished page out
  brush-engine.js      the canvas renderer, inlined into every page
  template.html        the page shell, in Nihongoism colors and type
  nihongoism-logo.svg  the wordmark, inlined into the page footer
examples/              built pages for 木 and 靄
```

Shape changes belong in `brush-engine.js`, so every character benefits.

## License

The code is MIT licensed. The stroke data is KanjiVG's, copyright Ulrich Apel, [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); generated pages embed it and carry the attribution in their footer.
