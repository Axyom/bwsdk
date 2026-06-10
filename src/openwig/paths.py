"""openwig.paths - filesystem locations shared by the SDK and the controller.

The controller script resolves the same directory in JS (_resolveLogPath); the two
implementations MUST stay in lockstep, or `openwig install` would drop the symbol data
file where the controller never looks.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def data_dir() -> Path:
    """openwig data dir (symbol data file, per-build symbol cache, bridge log).

      Windows : %LOCALAPPDATA%/openwig
      macOS   : ~/Library/Logs/openwig
      Linux   : ${XDG_STATE_HOME:-~/.local/state}/openwig
    """
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "openwig"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Logs" / "openwig"
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "openwig"
