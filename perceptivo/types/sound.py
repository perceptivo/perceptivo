import shutil
from dataclasses import field
from pydantic import Field
from pydantic.dataclasses import dataclass
from pydantic import BaseModel
from pathlib import Path
import typing
import uuid
from datetime import datetime

from perceptivo.sound import sounds
# from autopilot.stim.sound.jackclient import JackClient
from autopilot.stim.sound.base import Sound


def _find_jackd() -> Path:
    jackd_location = shutil.which('jackd')
    if jackd_location is None:
        return Path('jackd')
    else:
        return Path(jackd_location)


@dataclass
class Audio_Config:
    """
    Base class for audio configuration

    Params:
        fs (int): Sampling rate in Hz, default 44100
    """
    fs: int = 44100


@dataclass
class Jackd_Config(Audio_Config):
    """
    Configure the jackd daemon used by the sound server, see https://linux.die.net/man/1/jackd

    Params:
        bin (:class:`pathlib.Path`): Path to the jackd binary
        priority (int): Priority to run the process (higher is better), default 75
        driver (str): Driver to use, default 'alsa'
        device_name (str, int): Device to use in alsa's parlance, default 'hw:sndrpihifiberry'.
            Also accepts ints for use with coreaudio
        nperiods (int): Number of periods per buffer cycle, default 3
        period (int): size of period, default 1024 samples.
        launch_str (str): launch string with arguments compiled from the other arguments
    """
    bin: Path = field(default_factory= _find_jackd)
    priority: int = 75
    driver: str = "alsa"
    device_name: typing.Union[str, int] = "hw:sndrpihifiberry"
    nperiods: int = 3
    period: int = 1024
    playback_only: bool = True
    outchannels: list = field(default_factory=lambda: [0,1])

    @property
    def launch_str(self) -> str:
        if self.playback_only:
            io_mode = '-P'
        else:
            io_mode = '-D'

        base_str = f'{str(self.bin)} -P{self.priority} -R -d{self.driver}'
        if self.driver == "alsa":
            launch_str: str =  ' '.join(
                [
                    base_str,
                    f'-d{self.device_name}',
                    io_mode,
                    f'-r{self.fs}',
                    f'-n{self.nperiods}',
                    f'-p{self.period}',
                    '-s &'
                ])
        elif self.driver == "coreaudio":
            launch_str = ' '.join([
                base_str,
                f'-P1 -C0 -r{self.fs} -p{self.period} -I{self.device_name} -s &'
                ])
        else:
            raise ValueError(f'dont know what to do with driver type {self.driver}')
        return launch_str




SOUND_TYPES = typing.Literal['Gammatone']


class Sound(BaseModel):
    """
    Parameterization of an abstract probe sound

    Args:
        frequency (float): Frequency in Hz
        amplitude (float): Amplitude in dbSPL
        duration (float): Duration of sound in seconds

    Attributes:
        uuid (str): Unique UUID to identify sounds
    """
    frequency: float
    amplitude: float
    duration: float = 0.5
    sound_type: SOUND_TYPES = "Gammatone"
    timestamp: typing.Optional[datetime] = None
    # jack_client: typing.Optional[JackClient] = None
    uuid: str = Field(default_factory=uuid.uuid4)

    class Config:
        arbitrary_types_allowed:bool = True

    def stamp_time(self):
        """
        Record the time that the sound is played in :attr:`.Sound.timestamp`
        """
        self.timestamp = datetime.now()

    @property
    def sound_kwargs(self) -> dict:
        """
        Sound kwargs that the sound class accepts

        (ie. filtering out ``sound_type`` and others the sound class doesn't take)

        Returns:
            dict of arguments
        """
        if not hasattr(self, 'jack_client'):
            self.jack_client = None

        return {
            'frequency': self.frequency,
            'amplitude': self.amplitude,
            'duration': self.duration,
            'jack_client': self.jack_client
        }

    @property
    def sound_class(self) -> Sound:
        """
        The sound class that corresponds to the :attr:`.sound_type` retrieved from
        the :mod:`perceptivo.sound.sounds` module.

        Returns:
            :class:`autopilot.stim.sound.sounds.Jack_Sound` - The sound class!
        """
        return getattr(sounds, self.sound_type)










