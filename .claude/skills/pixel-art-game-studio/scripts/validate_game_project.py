#!/usr/bin/env python3
"""Validate a game project against the Pixel Art Game Studio data contract.

Checks (see references/game-systems.md):
  - source-of-truth documents in design/ (or the project root)
  - data/maps: structure, spawns, exits -> existing map + spawn, flood-fill reachability
  - data/decor: placements in bounds, not covering spawns/exits/NPCs/interactables, not blocking paths
  - data/dialogue: start node, links, dead ends, unreachable nodes, impossible flag conditions
  - data/quests.json, data/items.json: references to maps, items, NPCs, flags
  - data/locale: every used key exists in en.json; other locales report missing keys
  - assets/**/*.meta.json: PNG exists, dimensions match frames, no clipped drawing

Usage: python validate_game_project.py <project-dir> [--strict] [--json]
Exit codes: 0 valid, 1 errors found (or warnings with --strict), 2 bad arguments.
Read-only: this script never modifies the project.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import deque
from pathlib import Path

DESIGN_DOCS = ["GAME_DESIGN.md", "TECHNICAL_ARCHITECTURE.md", "ART_DIRECTION.md", "PROJECT_CONVENTIONS.md",
               "IMPLEMENTATION_ROADMAP.md", "ACCEPTANCE_CRITERIA.md", "KNOWN_ISSUES.md"]
OBJECTIVE_TYPES = {"reach", "collect", "talk", "flag"}
REFERENCE_LOCALE = "en"


class Report:
    def __init__(self, root: Path):
        self.root = root
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def _add(self, bucket, area, path, msg):
        try:
            rel = str(Path(path).relative_to(self.root)) if path else ""
        except ValueError:
            rel = str(path)
        bucket.append({"area": area, "file": rel.replace("\\", "/"), "message": msg})

    def error(self, area, path, msg):
        self._add(self.errors, area, path, msg)

    def warn(self, area, path, msg):
        self._add(self.warnings, area, path, msg)


def load_json(path: Path, report: Report, area: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        report.error(area, path, f"cannot parse JSON: {exc}")
        return None


def as_pos(value):
    if isinstance(value, list) and len(value) == 2 and all(isinstance(v, int) and not isinstance(v, bool) for v in value):
        return value[0], value[1]
    return None


def str_list(value) -> list[str]:
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def neighbors(x, y):
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))


# ---------------------------------------------------------------- documents

def check_docs(root: Path, r: Report):
    for name in DESIGN_DOCS:
        if not (root / "design" / name).is_file() and not (root / name).is_file():
            r.warn("docs", None, f"missing source-of-truth document design/{name}")


# ---------------------------------------------------------------- maps and decor

def load_maps(data: Path, r: Report) -> dict:
    maps = {}
    for path in sorted((data / "maps").glob("*.json")):
        m = load_json(path, r, "maps")
        if not isinstance(m, dict):
            if m is not None:
                r.error("maps", path, "map file must be a JSON object")
            continue
        mid = m.get("id")
        if not isinstance(mid, str) or not mid:
            r.error("maps", path, "missing string 'id'")
            continue
        if mid != path.stem:
            r.warn("maps", path, f"id '{mid}' does not match file name '{path.stem}'")
        if mid in maps:
            r.error("maps", path, f"duplicate map id '{mid}'")
            continue
        tiles = m.get("tiles")
        if not (isinstance(tiles, list) and tiles and all(isinstance(t, str) for t in tiles)):
            r.error("maps", path, "'tiles' must be a non-empty list of strings")
            continue
        width = len(tiles[0])
        if width == 0 or any(len(t) != width for t in tiles):
            r.error("maps", path, "all 'tiles' rows must have the same non-zero length")
            continue
        walkable = m.get("walkable", ".")
        if not isinstance(walkable, str) or not walkable:
            r.error("maps", path, "'walkable' must be a non-empty string of tile characters")
            continue
        info = {"id": mid, "path": path, "tiles": tiles, "w": width, "h": len(tiles), "walkable": set(walkable),
                "spawns": {}, "exits": [], "npcs": {}, "interactables": {}}

        def in_bounds(p):
            return 0 <= p[0] < info["w"] and 0 <= p[1] < info["h"]

        def walk(p):
            return in_bounds(p) and tiles[p[1]][p[0]] in info["walkable"]

        spawns = m.get("spawns", {})
        if not isinstance(spawns, dict) or not spawns:
            r.error("maps", path, "'spawns' must be a non-empty object of name -> [x, y]")
            spawns = {}
        for name, raw in spawns.items():
            p = as_pos(raw)
            if p is None or not in_bounds(p):
                r.error("maps", path, f"spawn '{name}' must be an in-bounds [x, y]")
            elif not walk(p):
                r.error("maps", path, f"spawn '{name}' at {list(p)} is not on a walkable tile")
            else:
                info["spawns"][name] = p
        for i, ex in enumerate(m.get("exits", []) if isinstance(m.get("exits", []), list) else []):
            p = as_pos(ex.get("at")) if isinstance(ex, dict) else None
            if p is None or not in_bounds(p):
                r.error("maps", path, f"exits[{i}] needs an in-bounds 'at' [x, y]")
                continue
            if not walk(p):
                r.error("maps", path, f"exits[{i}] at {list(p)} is not on a walkable tile")
            if not isinstance(ex.get("to"), str) or not isinstance(ex.get("spawn"), str):
                r.error("maps", path, f"exits[{i}] needs string 'to' and 'spawn'")
                continue
            info["exits"].append({"at": p, "to": ex["to"], "spawn": ex["spawn"]})
        for key in ("npcs", "interactables"):
            entries = m.get(key, [])
            for i, ent in enumerate(entries if isinstance(entries, list) else []):
                p = as_pos(ent.get("at")) if isinstance(ent, dict) else None
                eid = ent.get("id") if isinstance(ent, dict) else None
                if not isinstance(eid, str) or p is None or not in_bounds(p):
                    r.error("maps", path, f"{key}[{i}] needs a string 'id' and an in-bounds 'at' [x, y]")
                    continue
                if eid in info[key]:
                    r.error("maps", path, f"duplicate {key[:-1]} id '{eid}' in this map")
                info[key][eid] = p
        maps[mid] = info
    return maps


def reachable_from_spawns(info: dict, extra_blocked: set) -> set:
    blocked = set(info["npcs"].values()) | set(info["interactables"].values()) | extra_blocked
    seen, queue = set(), deque()
    for p in info["spawns"].values():
        if p not in blocked:
            seen.add(p)
            queue.append(p)
    while queue:
        x, y = queue.popleft()
        for nx, ny in neighbors(x, y):
            if (nx, ny) in seen or (nx, ny) in blocked:
                continue
            if 0 <= nx < info["w"] and 0 <= ny < info["h"] and info["tiles"][ny][nx] in info["walkable"]:
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def unreachable_targets(info: dict, reach: set) -> list[str]:
    missing = [f"exit to '{e['to']}' at {list(e['at'])}" for e in info["exits"] if e["at"] not in reach]
    for key in ("npcs", "interactables"):
        for eid, p in info[key].items():
            if not any(n in reach for n in neighbors(*p)):
                missing.append(f"{key[:-1]} '{eid}' at {list(p)}")
    return missing


def load_decor(data: Path, maps: dict, asset_names: set | None, r: Report) -> dict:
    """Return map_id -> set of blocking decor positions."""
    blocking = {}
    for path in sorted((data / "decor").glob("*.json")):
        d = load_json(path, r, "decor")
        if not isinstance(d, dict):
            if d is not None:
                r.error("decor", path, "decor file must be a JSON object")
            continue
        mid = d.get("map")
        if mid not in maps:
            r.error("decor", path, f"decor refers to unknown map '{mid}'")
            continue
        info = maps[mid]
        protected = {p: f"spawn '{n}'" for n, p in info["spawns"].items()}
        protected.update({e["at"]: f"exit to '{e['to']}'" for e in info["exits"]})
        for key in ("npcs", "interactables"):
            protected.update({p: f"{key[:-1]} '{eid}'" for eid, p in info[key].items()})
        placements = d.get("placements", [])
        for i, pl in enumerate(placements if isinstance(placements, list) else []):
            p = as_pos(pl.get("at")) if isinstance(pl, dict) else None
            if p is None or not (0 <= p[0] < info["w"] and 0 <= p[1] < info["h"]):
                r.error("decor", path, f"placements[{i}] needs an in-bounds 'at' [x, y]")
                continue
            asset = pl.get("asset")
            if not isinstance(asset, str):
                r.error("decor", path, f"placements[{i}] needs a string 'asset'")
            elif asset_names is not None and asset not in asset_names:
                r.warn("decor", path, f"placements[{i}] asset '{asset}' has no PNG under assets/")
            if p in protected:
                r.error("decor", path, f"placements[{i}] at {list(p)} covers {protected[p]}")
            if pl.get("blocking"):
                blocking.setdefault(mid, set()).add(p)
    return blocking


def check_maps(maps: dict, decor_blocking: dict, r: Report):
    for info in maps.values():
        for ex in info["exits"]:
            target = maps.get(ex["to"])
            if target is None:
                r.error("maps", info["path"], f"exit at {list(ex['at'])} leads to unknown map '{ex['to']}'")
            elif ex["spawn"] not in target["spawns"]:
                r.error("maps", info["path"], f"exit at {list(ex['at'])} uses unknown spawn '{ex['spawn']}' in '{ex['to']}'")
        base = unreachable_targets(info, reachable_from_spawns(info, set()))
        for item in base:
            r.error("maps", info["path"], f"unreachable from spawns: {item} (Level Design)")
        blocked = decor_blocking.get(info["id"], set())
        if blocked:
            for item in unreachable_targets(info, reachable_from_spawns(info, blocked)):
                if item not in base:
                    r.error("decor", info["path"], f"blocking decor makes {item} unreachable (Environmental Content)")


# ---------------------------------------------------------------- items, quests, dialogue

def load_items(data: Path, r: Report) -> dict:
    items = {}
    path = data / "items.json"
    if not path.is_file():
        return items
    d = load_json(path, r, "items")
    entries = d.get("items") if isinstance(d, dict) else None
    if not isinstance(entries, list):
        if d is not None:
            r.error("items", path, "expected {\"items\": [...]}")
        return items
    for i, it in enumerate(entries):
        iid = it.get("id") if isinstance(it, dict) else None
        if not isinstance(iid, str):
            r.error("items", path, f"items[{i}] needs a string 'id'")
            continue
        if iid in items:
            r.error("items", path, f"duplicate item id '{iid}'")
        ms = it.get("max_stack", 1)
        if not isinstance(ms, int) or isinstance(ms, bool) or ms < 1:
            r.error("items", path, f"item '{iid}' max_stack must be an integer >= 1")
        items[iid] = it
    return items


def iter_effects(effects):
    return effects if isinstance(effects, dict) else {}


def load_dialogues(data: Path, r: Report) -> list[dict]:
    out, ids = [], set()
    for path in sorted((data / "dialogue").glob("*.json")):
        d = load_json(path, r, "dialogue")
        if not isinstance(d, dict) or not isinstance(d.get("nodes"), dict):
            if d is not None:
                r.error("dialogue", path, "dialogue needs an object 'nodes'")
            continue
        if d.get("id") in ids:
            r.error("dialogue", path, f"duplicate dialogue id '{d.get('id')}'")
        ids.add(d.get("id"))
        d["_path"] = path
        out.append(d)
    return out


def load_quests(data: Path, r: Report) -> list[dict]:
    path = data / "quests.json"
    if not path.is_file():
        return []
    d = load_json(path, r, "quests")
    qs = d.get("quests") if isinstance(d, dict) else None
    if not isinstance(qs, list):
        if d is not None:
            r.error("quests", path, "expected {\"quests\": [...]}")
        return []
    return [q for q in qs if isinstance(q, dict)]


def collect_set_flags(dialogues, quests, data: Path, r: Report) -> set:
    flags = set()
    for d in dialogues:
        for node in d["nodes"].values():
            if not isinstance(node, dict):
                continue
            flags.update(str_list(iter_effects(node.get("effects")).get("set_flags")))
            for ch in node.get("choices", []) if isinstance(node.get("choices"), list) else []:
                if isinstance(ch, dict):
                    flags.update(str_list(iter_effects(ch.get("effects")).get("set_flags")))
    for q in quests:
        flags.update(str_list(iter_effects(q.get("rewards")).get("set_flags")))
    path = data / "flags.json"
    if path.is_file():
        d = load_json(path, r, "flags")
        if isinstance(d, dict):
            flags.update(str_list(d.get("flags")))
    return flags


def check_effects(effects, where, path, ctx, r: Report):
    if effects is None:
        return
    if not isinstance(effects, dict):
        r.error("dialogue", path, f"{where}: 'effects' must be an object")
        return
    q = effects.get("start_quest")
    if q is not None and q not in ctx["quest_ids"]:
        r.error("dialogue", path, f"{where}: start_quest '{q}' is not defined in quests.json")
    for key in ("give_items", "take_items"):
        for item in (effects.get(key) or {}):
            if item not in ctx["items"]:
                r.error("dialogue", path, f"{where}: {key} refers to unknown item '{item}'")
    for npc in (effects.get("relationship") or {}):
        if npc not in ctx["npcs"]:
            r.warn("dialogue", path, f"{where}: relationship with '{npc}', who is not placed on any map")


def check_dialogues(dialogues, ctx, r: Report):
    for d in dialogues:
        path, nodes = d["_path"], d["nodes"]
        if d.get("npc") is not None and d["npc"] not in ctx["npcs"]:
            r.warn("dialogue", path, f"npc '{d['npc']}' is not placed on any map")
        start = d.get("start")
        if start not in nodes:
            r.error("dialogue", path, f"start node '{start}' does not exist")
        edges = {}
        for nid, node in nodes.items():
            where = f"node '{nid}'"
            if not isinstance(node, dict):
                r.error("dialogue", path, f"{where} must be an object")
                continue
            ctx["keys"].append((node.get("text"), path, where))
            kinds = [k for k in ("next", "choices") if k in node] + (["end"] if node.get("end") else [])
            if len(kinds) != 1:
                r.error("dialogue", path, f"{where} must have exactly one of 'next', 'choices', 'end': true")
            targets = []
            if "next" in node:
                targets.append(node["next"])
            choices = node.get("choices", [])
            if "choices" in node and (not isinstance(choices, list) or not choices):
                r.error("dialogue", path, f"{where}: 'choices' must be a non-empty list")
                choices = []
            for i, ch in enumerate(choices):
                cw = f"{where} choice {i}"
                if not isinstance(ch, dict):
                    r.error("dialogue", path, f"{cw} must be an object")
                    continue
                ctx["keys"].append((ch.get("text"), path, cw))
                targets.append(ch.get("next"))
                for flag in str_list(ch.get("requires_flags")):
                    if flag not in ctx["flags"]:
                        r.error("dialogue", path, f"{cw} requires flag '{flag}' that nothing sets (impossible branch)")
                check_effects(ch.get("effects"), cw, path, ctx, r)
            check_effects(node.get("effects"), where, path, ctx, r)
            for t in targets:
                if t not in nodes:
                    r.error("dialogue", path, f"{where} links to missing node '{t}'")
            edges[nid] = [t for t in targets if t in nodes]
        if start in nodes:
            seen, queue = {start}, deque([start])
            while queue:
                for t in edges.get(queue.popleft(), []):
                    if t not in seen:
                        seen.add(t)
                        queue.append(t)
            for nid in nodes:
                if nid not in seen:
                    r.warn("dialogue", path, f"node '{nid}' is unreachable from start '{start}'")


def check_quests(quests, ctx, data: Path, r: Report):
    path, ids = data / "quests.json", set()
    for i, q in enumerate(quests):
        qid = q.get("id")
        if not isinstance(qid, str):
            r.error("quests", path, f"quests[{i}] needs a string 'id'")
            continue
        if qid in ids:
            r.error("quests", path, f"duplicate quest id '{qid}'")
        ids.add(qid)
        ctx["keys"].append((q.get("title"), path, f"quest '{qid}' title"))
        for flag in str_list(q.get("requires_flags")):
            if flag not in ctx["flags"]:
                r.error("quests", path, f"quest '{qid}' requires flag '{flag}' that nothing sets")
        objectives = q.get("objectives")
        if not isinstance(objectives, list) or not objectives:
            r.error("quests", path, f"quest '{qid}' needs a non-empty 'objectives' list")
            objectives = []
        for j, ob in enumerate(objectives):
            where = f"quest '{qid}' objective {j}"
            if not isinstance(ob, dict) or ob.get("type") not in OBJECTIVE_TYPES:
                r.error("quests", path, f"{where}: type must be one of {sorted(OBJECTIVE_TYPES)}")
                continue
            t, target = ob["type"], ob.get("target")
            known = {"reach": ctx["maps"], "collect": ctx["items"], "talk": ctx["npcs"], "flag": ctx["flags"]}[t]
            if target not in known:
                r.error("quests", path, f"{where}: {t} target '{target}' does not exist")
            count = ob.get("count", 1)
            if not isinstance(count, int) or isinstance(count, bool) or count < 1:
                r.error("quests", path, f"{where}: count must be an integer >= 1")
        for item in (iter_effects(q.get("rewards")).get("items") or {}):
            if item not in ctx["items"]:
                r.error("quests", path, f"quest '{qid}' rewards unknown item '{item}'")


def check_locale(data: Path, ctx, r: Report):
    for it_id, it in ctx["items"].items():
        ctx["keys"].append((it.get("name"), data / "items.json", f"item '{it_id}' name"))
    locale_dir = data / "locale"
    ref_path = locale_dir / f"{REFERENCE_LOCALE}.json"
    used = [(k, p, w) for k, p, w in ctx["keys"]]
    for key, path, where in used:
        if not isinstance(key, str) or not key:
            r.error("locale", path, f"{where}: missing locale key")
    keys = {k for k, _, _ in used if isinstance(k, str) and k}
    if not keys:
        return
    if not ref_path.is_file():
        r.warn("locale", None, f"no reference locale data/locale/{REFERENCE_LOCALE}.json; {len(keys)} keys unchecked")
        return
    ref = load_json(ref_path, r, "locale")
    if not isinstance(ref, dict):
        return
    for key, path, where in used:
        if isinstance(key, str) and key and key not in ref:
            r.error("locale", path, f"{where}: key '{key}' missing from {REFERENCE_LOCALE}.json")
    for other in sorted(locale_dir.glob("*.json")):
        if other == ref_path:
            continue
        loc = load_json(other, r, "locale")
        if isinstance(loc, dict):
            missing = sorted(k for k in ref if k not in loc)
            if missing:
                r.warn("locale", other, f"{len(missing)} keys missing (first: {missing[0]})")


# ---------------------------------------------------------------- assets

def png_size(path: Path):
    with path.open("rb") as fh:
        head = fh.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def check_assets(root: Path, r: Report):
    assets = root / "assets"
    for meta_path in sorted(assets.rglob("*.meta.json")):
        meta = load_json(meta_path, r, "assets")
        if not isinstance(meta, dict):
            continue
        png = meta_path.with_name(meta_path.name[: -len(".meta.json")] + ".png")
        if not png.is_file():
            r.error("assets", meta_path, f"PNG {png.name} is missing")
            continue
        size = png_size(png)
        if size is None:
            r.error("assets", png, "file is not a valid PNG")
            continue
        try:
            scale = meta.get("scale", 1)
            expected = (meta["frame"]["w"] * meta["frames"] * scale, meta["frame"]["h"] * scale)
        except (KeyError, TypeError):
            r.error("assets", meta_path, "meta needs frame.w, frame.h, frames")
            continue
        if tuple(size) != expected:
            r.error("assets", png, f"size {size[0]}x{size[1]} does not match meta (expected {expected[0]}x{expected[1]})")
        for i, n in enumerate(meta.get("clipped_pixels", [])):
            if n:
                r.warn("assets", meta_path, f"frame {i} clipped {n} pixels at the frame edge")


# ---------------------------------------------------------------- main

def validate(root: Path) -> Report:
    r = Report(root)
    check_docs(root, r)
    data = root / "data"
    assets = root / "assets"
    asset_names = {p.name[:-4] for p in assets.rglob("*.png")} if assets.is_dir() else None
    if data.is_dir():
        maps = load_maps(data, r)
        decor = load_decor(data, maps, asset_names, r)
        check_maps(maps, decor, r)
        items = load_items(data, r)
        dialogues = load_dialogues(data, r)
        quests = load_quests(data, r)
        ctx = {
            "maps": set(maps), "items": items, "keys": [],
            "npcs": {n for m in maps.values() for n in m["npcs"]},
            "quest_ids": {q.get("id") for q in quests},
            "flags": collect_set_flags(dialogues, quests, data, r),
        }
        check_dialogues(dialogues, ctx, r)
        check_quests(quests, ctx, data, r)
        check_locale(data, ctx, r)
    else:
        r.warn("data", None, "no data/ directory; content contract checks skipped")
    if assets.is_dir():
        check_assets(root, r)
    return r


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")  # Windows consoles may not encode every script
    ap = argparse.ArgumentParser(description="Validate a game project against the Pixel Art Game Studio data contract.")
    ap.add_argument("project", type=Path)
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    args = ap.parse_args(argv)
    root = args.project.resolve()
    if not root.is_dir():
        print(f"error: {args.project} is not a directory", file=sys.stderr)
        return 2
    r = validate(root)
    if args.json:
        print(json.dumps({"errors": r.errors, "warnings": r.warnings}, indent=2))
    else:
        for level, items in (("ERROR", r.errors), ("WARN", r.warnings)):
            for it in items:
                loc = f" {it['file']}:" if it["file"] else ""
                print(f"{level:5} [{it['area']}]{loc} {it['message']}")
        print(f"{len(r.errors)} error(s), {len(r.warnings)} warning(s)")
    return 1 if r.errors or (args.strict and r.warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
