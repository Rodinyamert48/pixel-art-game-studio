# Pixel Art Game Studio

[← Haupt-README](../../README.md) · Deutsch · Maschinell unterstützte Übersetzung, eine Prüfung durch Muttersprachler steht noch aus.

<!-- section: overview -->
## Überblick

Pixel Art Game Studio ist ein Skill für Claude Code mit einem Team aus acht spezialisierten
Subagenten, mit dem sich eigene 2D-Pixel-Art-Spiele entwickeln lassen. Sie beschreiben das Spiel, das
Ihnen vorschwebt, was Ihnen am aktuellen Stand nicht gefällt und was als Nächstes geändert werden soll.
Claude plant die Arbeit, schreibt den Code, erzeugt die Grafiken, führt die Tests aus, behebt
reproduzierbare Fehler und berichtet nur, was tatsächlich überprüft wurde.

Gedacht ist es für gemütliche Erzählabenteuer, Lebens- und Farmsimulationen, dialoglastige
Rollenspiele, Erkundungsspiele aus der Draufsicht und Rätselspiele, aber auch für andere eigene
2D-Ideen. Vier Teile bleiben getrennt: der **Skill** (Anweisungen), die **Agenten** (Spezialisten), die
**Skripte** (deterministische Werkzeuge) und **Ihr Spiel** (ein eigenes Projektverzeichnis).

<!-- section: features -->
## Funktionen

- Ein Game-Director-Ablauf, der aus einer losen Idee ein kurzes Design und eine minimal spielbare
  Schleife macht.
- Acht Spezialisten mit klarer Zuständigkeit, begrenzten Werkzeuglisten und strukturierten Berichten.
- Prozedurale Pixel-Art: JSON-Spezifikationen werden zu echten PNG-Spritesheets, Metadaten und
  Vorschauen. Dieselbe Spezifikation erzeugt immer dieselben Bytes.
- Ein Datenvertrag für Karten, Dekoration, Dialoge, Quests, Gegenstände und Übersetzungen, dazu ein
  Validator, der unerreichbare Ausgänge, unmögliche Dialogzweige und fehlende Textschlüssel findet.
- Qualitätssicherung mit Schweregraden, reproduzierbaren Fehlerberichten und überprüften Korrekturen
  samt Regressionstests.
- Ein sicherer Installer mit Probelauf, Konflikterkennung, Sicherungskopien und vorsichtiger
  Deinstallation.

<!-- section: agents -->
## Das Agententeam

Es gibt neun Rollen. Der **Game Director** ist der Skill selbst und läuft in Ihrer Haupt-Sitzung von
Claude Code: Er pflegt das Design, schreibt Aufgabenbeschreibungen, prüft jedes Ergebnis und
entscheidet, wann etwas fertig ist. Die acht Subagenten sind:

| Agent | Aufgabe |
| --- | --- |
| `pixel-artist` | Art Direction, Asset-Spezifikationen, erzeugte Sprites und Tiles |
| `npc-story-engineer` | Figuren, verzweigte Dialoge, Flags, Quests |
| `world-builder-level-design` | Kartenaufbau, Kollision, Startpunkte, Ausgänge |
| `world-builder-environmental-content` | Dekoration, interessante Orte, Atmosphäre der Regionen |
| `ui-engineer` | Menüs, HUD, Dialogfenster, Inventar- und Speicherbildschirme |
| `gameplay-engineer` | Bewegung, Spielzustand, Inventar, Quests, Speichern |
| `qa-tester` | Tests, Testläufe, Fehlerberichte |
| `bug-fixer` | Korrekturen an der Ursache mit Regressionstests |

Mehr dazu: [AGENTS.md](../AGENTS.md).

<!-- section: architecture -->
## Architektur

Der Director ist der Skill und kein Subagent, weil er Ihre Anfragen sehen und eine einzige Quelle der
Wahrheit führen muss (`design/GAME_DESIGN.md`, `ART_DIRECTION.md` und fünf weitere kurze Dokumente).
Spezialisten erhalten Aufgabenbeschreibungen, arbeiten an den Dateien, für die sie zuständig sind, und
berichten zurück; sie können keine weiteren Agenten starten. Spielinhalte liegen in einem
engine-unabhängigen Ordner `data/`, sodass Story, Leveldesign und Umgebung parallel entstehen und ohne
Start der Engine geprüft werden können. Stehen keine Subagenten zur Verfügung, erledigt der Director
dieselben Schritte nacheinander selbst. Siehe [ARCHITECTURE.md](../ARCHITECTURE.md).

<!-- section: prerequisites -->
## Voraussetzungen

- Claude Code (geprüft mit Version 2.1.312).
- Python 3.9 oder neuer; zusätzliche Pakete sind nicht nötig.
- Für echte Spiele die gewünschte Engine, etwa Godot 4 oder das .NET SDK für MonoGame. Der Skill
  prüft, was installiert ist, und fragt, bevor er etwas installiert.

<!-- section: installation -->
## Installation

Am einfachsten installieren Sie es als Plugin direkt in Claude Code. Der Skill heißt dann `/pixel-art-game-studio:pixel-art-game-studio`, und die Agenten erhalten das Präfix `pixel-art-game-studio:`:

```text
/plugin marketplace add Rodinyamert48/pixel-art-game-studio
/plugin install pixel-art-game-studio@pixel-art-game-studio
```

Oder ohne das Plugin-System: Klonen Sie das Repository und wählen Sie dann die Installationsart. Sehen Sie sich jede Änderung zuerst
mit `--dry-run` an:

```bash
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game
python scripts/install.py --scope user
```

Der Projektbereich schreibt nach `<project>/.claude/`, der Benutzerbereich nach `~/.claude/`.
Vorhandene Dateien, die nicht vom Installer stammen, werden nie ersetzt. Mit `--update` aktualisieren
Sie eine Installation (alte Dateien werden gesichert), mit `--uninstall` entfernen Sie nur unveränderte
Dateien, die der Installer selbst angelegt hat. Sie können Claude Code auch direkt in diesem
Repository starten oder die Ordner von Hand kopieren. Alle Möglichkeiten stehen in
[INSTALLATION.md](../INSTALLATION.md).

<!-- section: quick-start -->
## Schnellstart

Öffnen Sie Claude Code in Ihrem Projektordner und geben Sie ein:

```text
/pixel-art-game-studio Erstelle ein eigenes gemütliches Pixel-Art-Spiel in Draufsicht mit einer kleinen Stadt, einem Wald, drei NPCs, verzweigten Dialogen, Tag-Nacht-Wechsel und Speicherfunktion.
```

Der Director wählt sinnvolle Standardwerte, schreibt ein kurzes Design und baut zuerst eine kleine
spielbare Version. Einen einzelnen Spezialisten rufen Sie direkt auf, indem Sie ihn erwähnen, zum
Beispiel `@agent-qa-tester`.

<!-- section: examples -->
## Beispielanfragen

```text
/pixel-art-game-studio Füge eine neblige Sumpfregion mit zwei NPCs und einer Quest mit zwei Enden hinzu.
/pixel-art-game-studio Die Stadt wirkt leer. Ergänze Details und kleine Entdeckungen, aber halte die Wege frei.
/pixel-art-game-studio Untersuche dieses Spiel, führe alle verfügbaren Tests aus und behebe reproduzierbare Fehler.
```

Anfragen können Sie in jeder Sprache schreiben. Ein vollständiges Beispiel finden Sie unter
[examples](../../examples/example-game-idea.md).

<!-- section: workflows -->
## Arbeitsabläufe

- **Spiel erstellen**: in 14 Stufen von der Idee bis zur Auslieferung, beginnend mit einer minimal
  spielbaren Schleife.
- **Spiel erweitern**: das vorhandene Projekt untersuchen, die kleinste stimmige Änderung vornehmen,
  auf Regressionen prüfen.
- **Testen und korrigieren**: echte Tests ausführen, Fehler melden, bestätigte Fehler mit begrenzter
  Zahl an Versuchen beheben.
- **Assets erzeugen**: zuerst die Art Direction, dann Spezifikationen, PNG-Dateien und Vorschauen.
- **Release-Prüfung**: ein belegtes Urteil: bereit, bereit mit bekannten Problemen oder nicht bereit.

Überblick: [WORKFLOWS.md](../WORKFLOWS.md).

<!-- section: testing -->
## Testen und Fehlerbehebung

Der QA-Tester ermittelt, welche Werkzeuge das Spiel wirklich hat, macht aus Abnahmekriterien Tests,
führt sie aus und schreibt Fehlerberichte mit Schweregrad, Schritten und Belegen. Der Bug-Fixer
reproduziert jeden Fehler, behebt die Ursache, ergänzt einen Regressionstest und führt die Prüfungen
erneut aus. Tests abzuschwächen oder zu löschen ist nie erlaubt. So testen Sie dieses Repository
selbst:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Einzelheiten: [TESTING.md](../TESTING.md).

<!-- section: limitations -->
## Grenzen

- Es erzeugt keine fertigen kommerziellen Spiele von allein; rechnen Sie mit einer funktionierenden
  Basis, die mit Ihrem Feedback wächst.
- Ohne installierte Engine lassen sich nur Daten, Assets und engine-freie Logik überprüfen.
- Strukturelle Prüfungen können nicht beurteilen, ob Grafik gut aussieht oder ein Spiel Spaß macht;
  dafür braucht es einen Menschen.
- Die Übersetzungen sind maschinell unterstützt und warten auf eine Prüfung durch Muttersprachler.

<!-- section: troubleshooting -->
## Fehlersuche

Erscheint der Skill nicht, prüfen Sie, ob `SKILL.md` in `.claude/skills/pixel-art-game-studio/` liegt.
Werden die Agenten nicht gefunden, starten Sie Claude Code neu, nachdem `.claude/agents/` angelegt
wurde. Beendet sich der Installer mit Code 2, hat er eine Datei gefunden, die nicht von ihm stammt;
lesen Sie den ausgegebenen Plan. Weitere Antworten stehen in
[TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

<!-- section: contributing -->
## Mitwirken

Beiträge sind willkommen, besonders Prüfungen dieser Übersetzungen durch Muttersprachler. Lesen Sie
[CONTRIBUTING.md](../CONTRIBUTING.md) und den [Verhaltenskodex](../CODE_OF_CONDUCT.md), bevor Sie
einen Pull Request öffnen.

<!-- section: license -->
## Lizenz

Pixel Art Game Studio steht unter einer [reinen Nutzungslizenz](../../LICENSE): Sie dürfen es kostenlos
nutzen, aber nicht verkaufen, verändern oder weiterverbreiten. Die Spiele, die Sie damit erstellen,
gehören Ihnen.
