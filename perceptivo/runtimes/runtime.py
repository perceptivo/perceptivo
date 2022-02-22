import subprocess
from abc import abstractmethod
from pathlib import Path
from typing import List, Type, Optional, Union

from perceptivo import Directories
from perceptivo.prefs import Prefs, Patient_Prefs
from perceptivo.root import Perceptivo_Object


class Runtime(Perceptivo_Object):
    """
    Root object for the various perceptivo runtime objects, :class:`~.patient.Patient`,
    and :class:`.clinician.Clinician`.

    (at the moment empty, but kept as a scaffold for shared functionality)

    """


    def __init__(self, **kwargs):
        super(Runtime, self).__init__()

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
    def prefs_class(self) -> Type['Prefs']:
        pass

    def load_prefs(self, prefs_file:Optional[Path] = None) -> Union[Prefs, Patient_Prefs]:
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


        if not Directories.user_dir.exists():

            for val in Directories().__dict__.values():
                print(val)
                if len(val.suffixes) == 0:
                    val.mkdir(parents=True, exist_ok=True)

        if not prefs_file.exists():
            prefs_class = self.prefs_class
            prefs = prefs_class()
            prefs.save(prefs_file)
        else:
            prefs = self.prefs_class.load(prefs_file)
        return prefs