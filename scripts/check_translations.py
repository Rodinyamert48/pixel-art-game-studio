#!/usr/bin/env python3
"""Structural quality gate for the 16 documentation translations.

Checks, driven by docs/i18n/manifest.json:
  - exactly the required language set, each code and file listed once, every file present
  - every required section marker (<!-- section: id -->) present, each with substantive prose
  - prose (code removed) is mostly in the expected writing system
  - language marker words are present (separates e.g. Modern Standard Arabic from Egyptian Arabic)
  - non-English files are not English: limited English function-word ratio, few lines identical to en.md
  - each translation links back to the root README; the root README links every translation

This is a minimum gate. It cannot judge translation accuracy or fluency; human review is still needed.
Usage: python scripts/check_translations.py [--root DIR]    Exit codes: 0 pass, 1 problems found.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_CODES = ["en", "zh-CN", "hi", "es", "ar", "fr", "bn", "pt", "id", "ur", "ru", "de", "ja", "pcm", "arz", "tr"]
SECTION_RE = re.compile(r"<!--\s*section:\s*([a-z0-9-]+)\s*-->")
SCRIPTS = {
    "latin": [(0x0041, 0x024F)],
    "han": [(0x4E00, 0x9FFF), (0x3400, 0x4DBF)],
    "japanese": [(0x3040, 0x30FF), (0x4E00, 0x9FFF), (0x31F0, 0x31FF)],
    "devanagari": [(0x0900, 0x097F)],
    "arabic": [(0x0600, 0x06FF), (0x0750, 0x077F), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
    "bengali": [(0x0980, 0x09FF)],
    "cyrillic": [(0x0400, 0x04FF)],
}
ENGLISH_FUNCTION_WORDS = {"the", "and", "is", "are", "to", "of", "with", "you", "this", "that", "for", "it",
                          "your", "when", "what", "which", "be", "from", "can", "an", "or", "not", "will"}


def prose(text: str) -> str:
    """Strip code blocks, inline code, HTML comments, URLs, and link targets."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"https?://\S+", " ", text)
    return text


def sections(text: str) -> dict[str, str]:
    parts = SECTION_RE.split(text)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def in_ranges(ch: str, ranges) -> bool:
    o = ord(ch)
    return any(a <= o <= b for a, b in ranges)


def script_ratio(text: str, script: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(in_ranges(c, SCRIPTS[script]) for c in letters) / len(letters)


# Split on whitespace and punctuation only: Python's \w misses combining vowel signs (Devanagari, Bengali).
TOKEN_SPLIT_RE = re.compile(r"[\s\d.,;:!?()\[\]{}\"'«»“”‘’|*/\<>=+\-—–…،؛؟।#_`~]+")


def words(text: str) -> list[str]:
    return [w for w in TOKEN_SPLIT_RE.split(text.lower()) if w]


def english_ratio(text: str) -> float:
    ws = words(text)
    return sum(w in ENGLISH_FUNCTION_WORDS for w in ws) / len(ws) if ws else 0.0


def marker_hits(text: str, markers: list[str], substring: bool) -> int:
    if substring:
        return sum(1 for m in markers if m in text)
    tokens = set(words(text))
    return sum(1 for m in markers if m.lower() in tokens)


def prose_lines(text: str) -> set[str]:
    return {ln.strip() for ln in prose(text).splitlines() if len(ln.strip()) > 30}


def check(root: Path = REPO_ROOT) -> list[str]:
    problems: list[str] = []
    i18n = root / "docs" / "i18n"
    try:
        manifest = json.loads((i18n / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read docs/i18n/manifest.json: {exc}"]

    langs = manifest.get("languages", [])
    codes = [l.get("code") for l in langs]
    files = [l.get("file") for l in langs]
    for dup in sorted({c for c in codes if codes.count(c) > 1}):
        problems.append(f"manifest lists language '{dup}' more than once")
    for dup in sorted({f for f in files if files.count(f) > 1}):
        problems.append(f"manifest lists file '{dup}' more than once")
    if sorted(set(codes)) != sorted(REQUIRED_CODES):
        missing = sorted(set(REQUIRED_CODES) - set(codes))
        extra = sorted(set(codes) - set(REQUIRED_CODES))
        problems.append(f"manifest language set mismatch; missing {missing}, unexpected {extra}")

    required_sections = manifest.get("sections", [])
    min_chars = manifest.get("min_chars", 2500)
    min_section = manifest.get("min_section_chars", 60)
    source = manifest.get("source", "en")
    src_lang = next((l for l in langs if l.get("code") == source), None)
    src_lines: set[str] = set()
    if src_lang and (i18n / src_lang["file"]).is_file():
        src_lines = prose_lines((i18n / src_lang["file"]).read_text(encoding="utf-8"))

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    if not readme:
        problems.append("README.md missing or empty")

    for lang in langs:
        code, fname = lang.get("code"), lang.get("file")
        if not fname or not re.fullmatch(r"[A-Za-z0-9-]+\.md", fname):
            problems.append(f"{code}: invalid file name {fname!r}")
            continue
        path = i18n / fname
        tag = f"{code} ({fname})"
        if f"docs/i18n/{fname}" not in readme:
            problems.append(f"README language selector has no link to docs/i18n/{fname}")
        if lang.get("native_name") and lang["native_name"] not in readme:
            problems.append(f"README language selector does not show native name '{lang['native_name']}'")
        if not path.is_file():
            problems.append(f"{tag}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        body = prose(text)
        lang_min = lang.get("min_chars", min_chars)
        if len(body.strip()) < lang_min:
            problems.append(f"{tag}: only {len(body.strip())} prose characters (minimum {lang_min})")
        found = sections(text)
        for sec in required_sections:
            if sec not in found:
                problems.append(f"{tag}: missing section marker '{sec}'")
            elif len(prose(found[sec]).strip()) < lang.get("min_section_chars", min_section):
                problems.append(f"{tag}: section '{sec}' has too little prose")
        if "../../README.md" not in text:
            problems.append(f"{tag}: no link back to the root README (../../README.md)")
        script = lang.get("script", "latin")
        if script not in SCRIPTS:
            problems.append(f"{tag}: unknown script '{script}' in manifest")
        elif script_ratio(body, script) < lang.get("min_script_ratio", 0.5):
            problems.append(f"{tag}: prose is only {script_ratio(body, script):.0%} {script} script")
        markers = lang.get("markers", [])
        need = lang.get("min_markers", 3)
        if marker_hits(body, markers, script in ("han", "japanese")) < need:
            problems.append(f"{tag}: fewer than {need} of the language marker words {markers} found")
        if code != source:
            ratio = english_ratio(body)
            if ratio > lang.get("max_english_ratio", 0.04):
                problems.append(f"{tag}: English function words make up {ratio:.0%} of prose; looks untranslated")
            lines = prose_lines(text)
            if lines:
                same = len(lines & src_lines) / len(lines)
                if same > 0.15:
                    problems.append(f"{tag}: {same:.0%} of prose lines are identical to the English source")
        if lang.get("rtl") and 'dir="rtl"' not in text:
            problems.append(f"{tag}: right-to-left language without a dir=\"rtl\" wrapper")
    return problems


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")  # Windows consoles may not encode every script
    ap = argparse.ArgumentParser(description="Check documentation translations.")
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    args = ap.parse_args(argv)
    problems = check(args.root)
    for p in problems:
        print(f"FAIL {p}")
    print(f"translations: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
