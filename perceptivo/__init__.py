from importlib.metadata import version
from pathlib import Path
__version__ = version('perceptivo')

from perceptivo.prefs import Directories

# make directories if they don't exist
# and dump a default version oif prefs
if not Directories.user_dir.exists():

    for val in Directories().__dict__.values():
        print(val)
        if len(val.suffixes) == 0:
            val.mkdir(parents=True,exist_ok=True)
