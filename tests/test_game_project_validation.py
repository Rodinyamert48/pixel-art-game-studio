"""Game-project validator tests on a small fixture project built in a temporary directory."""
import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from _util import SKILL_SCRIPTS, load

vgp = load(SKILL_SCRIPTS / "validate_game_project.py")
gen = load(SKILL_SCRIPTS / "generate_sample_asset.py")

TOWN = {
    "id": "town",
    "tiles": ["#######",
              "#.....#",
              "#.....>",
              "#######"],
    "walkable": ".>",
    "spawns": {"default": [1, 1], "from_forest": [5, 2]},
    "exits": [{"at": [6, 2], "to": "forest", "spawn": "from_town"}],
    "npcs": [{"id": "mira", "at": [3, 1]}],
    "interactables": [{"id": "notice_board", "at": [1, 2]}],
}
FOREST = {
    "id": "forest",
    "tiles": ["<...", "...."],
    "walkable": ".<",
    "spawns": {"from_town": [1, 0]},
    "exits": [{"at": [0, 0], "to": "town", "spawn": "from_forest"}],
}
DIALOGUE = {
    "id": "mira_intro", "npc": "mira", "start": "greet",
    "nodes": {
        "greet": {"text": "dlg.greet", "next": "ask"},
        "ask": {"text": "dlg.ask", "choices": [
            {"text": "dlg.help", "next": "end", "effects": {"set_flags": ["agreed"], "start_quest": "lost_cat",
                                                             "relationship": {"mira": 1}}},
            {"text": "dlg.bell", "next": "end", "requires_flags": ["has_bell"], "effects": {"take_items": {"bell": 1}}}]},
        "end": {"text": "dlg.end", "end": True},
    },
}
QUESTS = {"quests": [{
    "id": "lost_cat", "title": "quest.lost_cat",
    "objectives": [{"type": "reach", "target": "forest"}, {"type": "collect", "target": "bell"},
                   {"type": "talk", "target": "mira"}, {"type": "flag", "target": "agreed"}],
    "rewards": {"items": {"bell": 1}, "set_flags": ["has_bell"]}}]}
ITEMS = {"items": [{"id": "bell", "name": "item.bell", "max_stack": 1}]}
LOCALE = {k: k for k in ["dlg.greet", "dlg.ask", "dlg.help", "dlg.bell", "dlg.end", "quest.lost_cat", "item.bell"]}


def quiet(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args)


class GameProjectValidationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.files = {
            "data/maps/town.json": copy.deepcopy(TOWN), "data/maps/forest.json": copy.deepcopy(FOREST),
            "data/dialogue/mira_intro.json": copy.deepcopy(DIALOGUE), "data/quests.json": copy.deepcopy(QUESTS),
            "data/items.json": copy.deepcopy(ITEMS), "data/locale/en.json": dict(LOCALE),
            "data/decor/town.json": {"map": "town", "placements": [{"asset": "demo_tree_oak", "at": [5, 1], "blocking": True}]},
        }
        for doc in vgp.DESIGN_DOCS:
            p = self.root / "design" / doc
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# doc\n", encoding="utf-8")
        for spec in gen.DEMO_SPECS:
            gen.generate(spec, self.root / "assets" / "sprites")

    def tearDown(self):
        self.tmp.cleanup()

    def run_validator(self):
        for rel, data in self.files.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data), encoding="utf-8")
        r = vgp.validate(self.root)
        return [e["message"] for e in r.errors], [w["message"] for w in r.warnings]

    def assertError(self, fragment):
        errors, _ = self.run_validator()
        self.assertTrue(any(fragment in e for e in errors), f"expected error containing {fragment!r}, got {errors}")

    def test_valid_fixture_passes_cleanly(self):
        errors, warnings = self.run_validator()
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(quiet(vgp.main, [str(self.root)]), 0)

    def test_exit_to_unknown_map_and_spawn(self):
        self.files["data/maps/town.json"]["exits"][0]["to"] = "castle"
        self.assertError("unknown map 'castle'")
        self.files["data/maps/town.json"]["exits"][0].update(to="forest", spawn="nowhere")
        self.assertError("unknown spawn 'nowhere'")

    def test_walled_off_npc_is_level_design_error(self):
        self.files["data/maps/town.json"]["tiles"] = ["#######", "#.#.#.#", "#.#####", "#.....>"]
        self.files["data/maps/town.json"]["npcs"] = [{"id": "mira", "at": [3, 1]}]
        self.files["data/maps/town.json"]["interactables"] = []
        self.files["data/maps/town.json"]["spawns"] = {"default": [1, 1], "from_forest": [5, 3]}
        self.files["data/maps/town.json"]["exits"][0]["at"] = [6, 3]
        self.files["data/decor/town.json"]["placements"] = []
        self.assertError("npc 'mira' at [3, 1] (Level Design)")

    def test_blocking_decor_cuts_path(self):
        self.files["data/maps/town.json"]["tiles"] = ["#######", "#..#..#", "#.....>", "#######"]
        self.files["data/maps/town.json"]["spawns"] = {"default": [1, 1], "from_forest": [1, 2]}
        self.files["data/maps/town.json"]["npcs"] = [{"id": "mira", "at": [5, 1]}]
        self.files["data/maps/town.json"]["interactables"] = []
        self.files["data/decor/town.json"]["placements"] = [{"asset": "demo_tree_oak", "at": [3, 2], "blocking": True}]
        self.assertError("blocking decor makes")

    def test_decor_covering_exit(self):
        self.files["data/decor/town.json"]["placements"] = [{"asset": "demo_tree_oak", "at": [6, 2]}]
        self.assertError("covers exit to 'forest'")

    def test_dialogue_missing_node_and_impossible_branch(self):
        self.files["data/dialogue/mira_intro.json"]["nodes"]["greet"]["next"] = "gone"
        self.files["data/quests.json"]["quests"][0]["rewards"]["set_flags"] = []
        errors, warnings = self.run_validator()
        self.assertTrue(any("missing node 'gone'" in e for e in errors))
        self.assertTrue(any("'has_bell' that nothing sets" in e for e in errors))
        self.assertTrue(any("unreachable from start" in w for w in warnings))

    def test_node_must_have_exactly_one_continuation(self):
        self.files["data/dialogue/mira_intro.json"]["nodes"]["end"] = {"text": "dlg.end"}
        self.assertError("exactly one of")

    def test_unknown_quest_item_and_locale_key(self):
        self.files["data/dialogue/mira_intro.json"]["nodes"]["ask"]["choices"][0]["effects"]["start_quest"] = "nope"
        self.assertError("start_quest 'nope'")
        self.files["data/quests.json"]["quests"][0]["objectives"][1]["target"] = "sword"
        self.assertError("collect target 'sword'")
        del self.files["data/locale/en.json"]["dlg.end"]
        self.assertError("key 'dlg.end' missing")

    def test_asset_meta_mismatch(self):
        meta = self.root / "assets/sprites/demo_tile_grass.meta.json"
        data = json.loads(meta.read_text(encoding="utf-8"))
        data["frames"] = 3
        meta.write_text(json.dumps(data), encoding="utf-8")
        self.assertError("does not match meta")

    def test_invalid_json_and_missing_docs(self):
        self.run_validator()
        (self.root / "data/items.json").write_text("{", encoding="utf-8")
        (self.root / "design/KNOWN_ISSUES.md").unlink()
        r = vgp.validate(self.root)
        self.assertTrue(any("cannot parse JSON" in e["message"] for e in r.errors))
        self.assertTrue(any("KNOWN_ISSUES.md" in w["message"] for w in r.warnings))
        self.assertEqual(quiet(vgp.main, [str(self.root)]), 1)

    def test_not_a_directory(self):
        self.assertEqual(quiet(vgp.main, [str(self.root / "missing")]), 2)


if __name__ == "__main__":
    unittest.main()
