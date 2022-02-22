"""
Root Perceptivo Object from which others inherit

"""
from typing import List, Type, Optional
from pathlib import Path
import subprocess
from logging import Logger
from perceptivo.data.logging import init_logger
from abc import ABC, abstractmethod
from perceptivo.prefs import Directories, Prefs

class Perceptivo_Object(ABC):
    @property
    def logger(self) -> Logger:
        if not hasattr(self, '_logger') or self._logger is None:
            self._logger = init_logger(self)

        return self._logger


class Runtime(Perceptivo_Object):
    """
    Root object for the various perceptivo runtime objects, :class:`~.patient.Patient`,
    and :class:`.clinician.Clinician`.

    (at the moment empty, but kept as a scaffold for shared functionality)

    """


    def __init__(self, prefs_file:Path=Directories.prefs_file):
        super(Runtime, self).__init__()
        self.prefs_file = prefs_file

        self.prefs = self.load_prefs()

        self._procs = [] # type: List[subprocess.Popen]

    @property
    def procs(self) -> List[subprocess.Popen]:
        """
        List of processes opened by this runtime agent!

        .. todo::

            kill all procs on exit

        Returns:
            typing.List[subprocess.Popen]
        """
        return self._procs

    @procs.setter
    def procs(self, procs: List[subprocess.Popen]):
        if not isinstance(procs, list) or not all([isinstance(p, subprocess.Popen) for p in procs]):
            raise ValueError(f'procs is a list of Popen objects! got {procs}')
        self._procs = procs

    @property
    @abstractmethod
    def prefs_class(self) -> Type[Prefs]:
        pass

    def load_prefs(self, prefs_file:Optional[Path] = None) -> Prefs:
        """
        Load prefs file. If defaults haven't already been dumped to a ``prefs.json`` file,
        do so.

        Args:
            prefs_file (Path): `prefs.json` file to load. if None, use :attr:`.Runtime.prefs_file`

        Returns:
            :class:`perceptivo.prefs.Prefs` a subtype of prefs, specified by :attr:`.Runtime.prefs_class`
        """
        if prefs_file is None:
            prefs_file = self.prefs_file

        prefs_file = Path(prefs_file)

        if not prefs_file.exists():
            prefs_class = self.prefs_class
            prefs = prefs_class()
            prefs.save(prefs_file)
        else:
            prefs = self.prefs_class.load(prefs_file)
        return prefs


