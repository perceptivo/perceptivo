import sys
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

from perceptivo.prefs import Directories

# make directories if they don't exist
# and dump a default version oif prefs
if not Directories.user_dir.exists():

    for val in Directories().__dict__.values():
        print(val)
        if len(val.suffixes) == 0:
            val.mkdir(parents=True,exist_ok=True)
