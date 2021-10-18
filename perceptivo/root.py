"""
Root Perceptivo Object from which others inherit

"""
from typing import List
import subprocess
from logging import Logger
from perceptivo.data.logging import init_logger

class Perceptivo_Object(object):
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

    def __init__(self):
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
