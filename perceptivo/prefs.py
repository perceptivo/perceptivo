"""
Preferences and configuration shared throughout the program.

Saves and loads to a prefs file (default is `~/.perceptivo/prefs.json` )
"""
import pdb
import typing
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
import shutil
import multiprocessing as mp
from pydantic import BaseModel

from perceptivo.types import sound, psychophys, video

_LOCK = mp.Lock()
"""
Lock read/write access to prefs to avoid corruption/races
"""

@dataclass
class Directories:
    user_dir: Path = Path().home() / '.perceptivo/'
    prefs_file: Path = user_dir / "prefs.json"
    log_dir: Path = user_dir / 'logs/'

class Runtimes(Enum):
    patient = 'patient'
    clinician = 'clinician'
    stimuli = 'stimuli'


class Prefs(BaseModel):

    runtime: Runtimes = 'patient'

    def save(self, file: Path = Directories.prefs_file):
        with open(file, 'w') as pfile:
            pfile.write(self.json())

    @classmethod
    def load(cls, file: Path = Directories.prefs_file) -> 'Prefs':
        with open(file, 'r') as pfile:
            prefs_raw = pfile.read()
        return cls.parse_raw(prefs_raw)

    @classmethod
    def get_runtime_prefs(cls, runtime:Runtimes) -> typing.Union['Patient_Prefs']:
        if runtime == Runtimes.patient.value:
            return Patient_Prefs()
        else:
            raise ValueError(f'Could not find prefs for {runtime}')

class Patient_Prefs(Prefs):
    runtime: Runtimes = 'patient'
    Audio_Config: sound.Audio_Config = sound.Audio_Config()
    Audiogram_Model: psychophys.Psychoacoustic_Model = psychophys.Psychoacoustic_Model(
                       'Gaussian_Process',
                       kwargs={'kernel': psychophys.Kernel()})
    Picamera_Params: video.Picamera_Params = video.Picamera_Params()
    picamera_process: bool = True
    """
    Run the picamera in 
    """


def get(field:str, file:Path=Directories.prefs_file):
    with _LOCK:
        prefs = Prefs.load(file)

    return prefs.dict()[field]















