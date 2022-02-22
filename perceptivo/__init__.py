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

# make directories if they don't exist
# and dump a default version oif prefs


from perceptivo import types
