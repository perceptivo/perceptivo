"""
Preferences and configuration shared throughout the program.

Saves and loads to a prefs file (default is `~/.perceptivo/prefs.json` )

Each runtime has its own set of preferences. When first run, if there is not
prefs file detected it populates with defaults (though defaults can be populated at
any time by instantiating the object with no arguments and using save, eg.::

    prefs = Patient_Prefs()
    prefs.save()


"""
import typing
from enum import Enum
from pathlib import Path
import multiprocessing as mp
from pydantic import BaseModel
import json

from perceptivo import Directories
from perceptivo.types import sound, psychophys, video, patient
from perceptivo.types.networking import Clinician_Networking, Patient_Networking
from perceptivo.video.pupil import Pupil_Extractors, EllipseExtractor_Params
from perceptivo.types.gui import GUI_Params

_LOCK = mp.Lock()
"""
Lock read/write access to prefs to avoid corruption/races
"""

_PREFS = None # type: typing.Optional['Prefs']


class Runtimes(Enum):
    patient = 'patient'
    clinician = 'clinician'
    stimuli = 'stimuli'

LOGLEVELS = typing.Literal['DEBUG', 'INFO', 'WARNING', 'ERROR']

def json_dumps_pretty(v, *, default):
    return json.dumps(v, indent=4,separators=(',', ": "), default=default)

class Prefs(BaseModel):

    loglevel:LOGLEVELS = 'DEBUG'

    class Config:
        json_dumps = json_dumps_pretty

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
    Audiogram_Model: psychophys.Psychoacoustic_Model = psychophys.Psychoacoustic_Model('Gaussian_Process')
    Picamera_Params: video.Picamera_Params = video.Picamera_Params()
    picamera_process: bool = True
    """
    Run the picamera in a separate Process (using :class:`.cameras.Picamera_Process` . Only True supported for now!
    """
    picam_queue_size:int = 1024
    pupil_extractor: str = 'simple'
    pupil_extractor_params: typing.Union[EllipseExtractor_Params] = EllipseExtractor_Params()
    collection_params : patient.Collection_Params = patient.Collection_Params()
    networking: Patient_Networking = Patient_Networking()

    class Config:
        use_enum_values = True

# --------------------------------------------------
# Clinician prefs
# --------------------------------------------------

class Clinician_Prefs(Prefs):
    networking: Clinician_Networking = Clinician_Networking()
    gui: GUI_Params = GUI_Params()
    update_period:float = 0.05


def get(field:str, file:Path= Directories.prefs_file):
    with _LOCK:
        prefs = Prefs.load(file)

    return prefs.dict()[field]


def set_global(prefs:Prefs):
    globals()['_PREFS'] = prefs

def get_global() -> Prefs:
    return globals()['_PREFS']













