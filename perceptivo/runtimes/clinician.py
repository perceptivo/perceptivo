"""
entrypoint for clinician interface
"""
import sys
import typing
from typing import Optional, Union, Tuple, List, Dict
if sys.version_info.minor >= 8:
    from typing import Literal
else:
    from typing_extensions import Literal

import argparse
from pathlib import Path
from PySide6.QtWidgets import QApplication

from perceptivo import Directories
from perceptivo.gui.main import Perceptivo_Clinician
from perceptivo.runtimes.runtime import Runtime, base_args
from perceptivo.prefs import Clinician_Prefs
from perceptivo.networking.node import Node

from perceptivo.types.networking import Clinician_Networking

def clinician_parser(manual_args:Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser('Perceptivo Clinician Runtime')
    parser = base_args(parser)

    if manual_args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(manual_args)
    return args


class Clinician(Runtime):
    prefs_class = Clinician_Prefs

    def __init__(
            self,
            networking: Optional[Clinician_Networking] = None,
            prefs_file: Path = Directories.prefs_file,
            **kwargs
        ):
        super(Clinician, self).__init__()
        self.prefs_file = prefs_file
        self.prefs = self.load_prefs(self.prefs_file) # type: Clinician_Prefs

        if networking is None:
            self.networking_prefs = self.prefs.networking
        else:
            self.networking_prefs = networking


    def init_gui(self):
        app = QApplication(sys.argv)
        gui = Perceptivo_Clinician(
            prefs=self.prefs,
            networking=self.networking_prefs
        )
        sys.exit(app.exec_())

def main():
    args = clinician_parser()
    prefs_file = args.prefs

    clin = Clinician(prefs_file=prefs_file)
    clin.init_gui()

