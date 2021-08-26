"""
Preferences and configuration shared throughout the program
"""
import typing
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Directories:
    user_dir: Path = Path().home() / '.perceptivo/'
    prefs_file: Path = user_dir / "prefs.json"
    log_dir: Path = user_dir / 'logs/'







