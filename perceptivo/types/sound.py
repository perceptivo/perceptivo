import shutil
from dataclasses import dataclass, field
from pathlib import Path
import typing


def _find_jackd() -> Path:
    jackd_location = shutil.which('jackd')
    if jackd_location is None:
        return Path('jackd')
    else:
        return Path(jackd_location)


@dataclass
class Jackd_Config:
    """
    Configure the jackd daemon used by the sound server, see https://linux.die.net/man/1/jackd

    Params:
        bin (:class:`pathlib.Path`): Path to the jackd binary
        priority (int): Priority to run the process (higher is better), default 75
        driver (str): Driver to use, default 'alsa'
        device_name (str): Device to use in alsa's parlance, default 'hw:sndrpihifiberry'
        fs (int): Sampling rate in Hz, default 44100
        nperiods (int): Number of periods per buffer cycle, default 3
        period (int): size of period, default 1024 samples.
        launch_str (str): launch string with arguments compiled from the other arguments
    """
    bin: Path = field(default_factory= _find_jackd)
    priority: int = 75
    driver: str = "alsa"
    device_name: str = "hw:sndrpihifiberry"
    fs: int = 44100
    nperiods: int = 3
    period: int = 1024
    launch_str: str = f'{bin} -P{priority} -R -d{driver} -d{device_name} -D -r{fs} -n{nperiods} -p{period} -s &'

SOUND_TYPES = typing.Literal['Gammatone']

@dataclass
class Sound:
    """
    Parameterization of an abstract probe sound

    Args:
        frequency (float): Frequency in Hz
        amplitude (float): Amplitude in dbSPL
        duration (float): Duration of sound in seconds
    """
    frequency: float
    amplitude: float
    duration: typing.Optional[float] = None
    sound_type: SOUND_TYPES = "Gammatone"




