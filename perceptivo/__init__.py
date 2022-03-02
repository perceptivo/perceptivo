import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info.minor >= 8:
    from importlib.metadata import version
else:
    from importlib_metadata import version

    # monkeypatch typing
    import typing
    from typing_extensions import Literal
    typing.Literal = Literal


__version__ = version('perceptivo')


# fix prefs multiprocessing errors?
import os
os.environ['AUTOPILOT_NO_PREFS_MANAGER'] = '1'

try:
    import pyqtgraph
    pyqtgraph.setConfigOption('useOpenGL', True)
except ImportError:
    pass

@dataclass
class Directories:
    user_dir: Path = Path().home() / '.perceptivo/'
    prefs_file: Path = user_dir / "prefs.json"
    log_dir: Path = user_dir / 'logs/'