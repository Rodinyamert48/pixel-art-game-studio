"""Shared helpers: import repository scripts by path (they are scripts, not an installed package)."""
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_SCRIPTS = REPO / ".claude" / "skills" / "pixel-art-game-studio" / "scripts"


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module
