# Pixel Art Game Studio

[← Main README](../../README.md) · Naijá (Nigerian Pidgin) · Machine don help write dis translation; e still dey wait make person wey sabi Naijá well-well check am.

<!-- section: overview -->
## Wetin dis tin be

Pixel Art Game Studio na one skill for Claude Code plus one team of eight special subagents wey dey
help build 2D pixel-art game wey be your own original idea. Na you go talk di kain game wey dey your
mind, wetin no sweet you for di one wey dem don make, and wetin you wan make dem change next. Claude go
plan di work, write di code, draw di graphics, run di tests, fix di bugs wey e fit show again, and e go
only report wetin e don check true-true.

Dem make am for cozy story adventure, life and farm simulation game, RPG wey get plenty talk-talk,
game wey you dey waka look am from top, and puzzle game, but e fit work for oda original 2D idea too.
Four tins dey separate: di **skill** (di instructions), di **agents** (di specialists), di **scripts**
(tools wey dey do di same tin every time) and **your game** (e get im own project folder).

<!-- section: features -->
## Wetin e fit do

- Game Director way of working wey dey turn rough idea to short design plus di smallest game loop wey
  person fit play.
- Eight specialists, each one get im own work clear, small list of tools, and report wey get correct
  shape.
- Pixel art wey code dey draw: JSON spec go turn real PNG sprite sheet, metadata and preview. Di same
  spec go always bring di same bytes.
- One data agreement for maps, decor, dialogue, quests, items and translations, plus validator wey
  dey catch exit wey nobody fit reach, dialogue branch wey no fit happen, and text key wey dey miss.
- QA wey get severity levels, bug report wey person fit follow repeat, and fixes wey dem confirm with
  regression tests.
- Safe installer wey get dry run, e dey check conflict, e dey keep backup, and e dey remove only wetin
  e install.

<!-- section: agents -->
## Di agent team

Nine roles dey. Di **Game Director** na di skill itself, e dey run for your main Claude Code session:
e dey hold di design, write task brief, check every result, and na im dey decide when work don finish.
Di eight subagents na:

| Agent | Im work |
| --- | --- |
| `pixel-artist` | art direction, asset specs, sprites and tiles wey dem generate |
| `npc-story-engineer` | characters, dialogue wey get branches, flags, quests |
| `world-builder-level-design` | how map take arrange, collision, spawn points, exits |
| `world-builder-environmental-content` | decoration, places wey get interest, di feeling of each area |
| `ui-engineer` | menus, HUD, dialogue box, inventory and save screens |
| `gameplay-engineer` | waka-waka, game state, inventory, quests, saving |
| `qa-tester` | tests, test runs, bug reports |
| `bug-fixer` | fixes wey reach di root of di wahala, plus regression tests |

More gist dey [AGENTS.md](../AGENTS.md).

<!-- section: architecture -->
## How di tin take arrange

Di Director na di skill, e no be subagent, because e must see wetin you dey ask and e must hold one
single source of truth (`design/GAME_DESIGN.md`, `ART_DIRECTION.md` plus five oda short documents).
Specialists dey collect brief, dem dey work only for di files wey belong to dem, den dem go bring
report; dem no fit start oda agents. Game content dey inside one `data/` folder wey no depend on any
engine, so story, level and environment work fit waka at di same time, and person fit check dem
without starting di engine. If subagents no dey available, di Director go do di same steps by imsef,
one after di oda. Check [ARCHITECTURE.md](../ARCHITECTURE.md).

<!-- section: prerequisites -->
## Wetin you need first

- Claude Code (dem check am with version 2.1.312).
- Python 3.9 or newer one; you no need any extra package.
- For real game, di engine wey you choose, like Godot 4 or .NET SDK for MonoGame. Di skill go check
  wetin don dey your system, and e go ask you before e install anytin.

<!-- section: installation -->
## How to install am

Clone di repository, den choose how you wan install. Use `--dry-run` first make you see every change:

```bash
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game
python scripts/install.py --scope user
```

Project scope dey write enter `<project>/.claude/`, user scope dey write enter `~/.claude/`. Any file
wey don dey before and no be di installer create am, e no go ever replace am. Use `--update` to
refresh di install (e go keep backup of di old files) and `--uninstall` to comot only di files wey e
install wey nobody don change. You fit also run Claude Code straight inside dis repository, or copy di
folders by hand. All di options dey [INSTALLATION.md](../INSTALLATION.md).

<!-- section: quick-start -->
## Quick start

Open Claude Code for your project folder, den type:

```text
/pixel-art-game-studio Make one original cozy pixel-art game wey person go dey look from top, e go get small town, one forest, three NPCs, dialogue wey get branches, day and night, and save.
```

Di Director go choose sensible defaults, write short design, and e go first build small version wey
person fit play. To call one specialist directly, mention am, like `@agent-qa-tester`.

<!-- section: examples -->
## Example of wetin you fit ask

```text
/pixel-art-game-studio Add one swamp area wey get mist, two NPCs and one quest wey get two endings.
/pixel-art-game-studio Di town dey look empty. Add small-small details and tins wey person go discover, but make road still dey clear.
/pixel-art-game-studio Check dis game, run all di tests wey dey, and fix di bugs wey person fit repeat.
```

You fit write your request for any language. Full example dey [examples](../../examples/example-game-idea.md).

<!-- section: workflows -->
## Di ways of working

- **Create game**: from idea reach delivery for 14 stages, e go start with di smallest loop wey person
  fit play.
- **Extend game**: check di project wey don dey, make di smallest change wey make sense, den check say
  nothing wey dey work before don spoil.
- **Test and fix**: run real tests, report bugs, fix di ones wey dem confirm, but e get limit for how
  many times dem go try.
- **Generate assets**: art direction first, den specs, PNG files and previews.
- **Release check**: one decision wey get evidence: ready, ready but get known wahala, or never ready.

Overview dey [WORKFLOWS.md](../WORKFLOWS.md).

<!-- section: testing -->
## Testing and how dem dey fix bug

Di QA tester go find out which tools di game really get, e go turn di acceptance criteria to tests, run
dem, and write bug report wey get severity, steps and evidence. Di bug fixer go first make each bug
happen again, fix di real cause, add regression test, den run di checks again. Dem no dey ever allow
person make test weak or delete test. To test dis repository by imsef:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Details dey [TESTING.md](../TESTING.md).

<!-- section: limitations -->
## Wetin e no fit do

- E no dey make finished commercial game by imsef; expect one base wey dey work and wey go grow as you
  dey give feedback.
- If no engine dey your system, na only data, assets and logic wey no need engine dem fit check.
- Structure checks no fit talk whether di art fine or whether di game sweet; na human being go judge
  dat one.
- Na machine help write di translations, and dem still dey wait make native speakers check dem.

<!-- section: troubleshooting -->
## If wahala show

If di skill no show, check say `SKILL.md` dey inside `.claude/skills/pixel-art-game-studio/`. If dem no
see di agents, restart Claude Code after you don create `.claude/agents/`. If di installer stop with
code 2, e mean say e see one file wey no be im create am; read di plan wey e print. More answers dey
[TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

<!-- section: contributing -->
## How you fit join hand

We dey welcome contributions, especially if una wey sabi di language fit check dis translations. Read
[CONTRIBUTING.md](../CONTRIBUTING.md) and di [Code of Conduct](../CODE_OF_CONDUCT.md) before you open
pull request.

<!-- section: license -->
## License

Pixel Art Game Studio dey under di [MIT License](../../LICENSE). Di games wey you make with am na your
own.
