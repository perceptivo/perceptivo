import shutil
from dataclasses import dataclass, field
from pathlib import Path
import typing
import uuid
from datetime import datetime

from perceptivo.sound import sounds


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
        device_name (str, int): Device to use in alsa's parlance, default 'hw:sndrpihifiberry'.
            Also accepts ints for use with coreaudio
        fs (int): Sampling rate in Hz, default 44100
        nperiods (int): Number of periods per buffer cycle, default 3
        period (int): size of period, default 1024 samples.
        launch_str (str): launch string with arguments compiled from the other arguments
    """
    bin: Path = field(default_factory= _find_jackd)
    priority: int = 75
    driver: str = "alsa"
    device_name: typing.Union[str, int] = "hw:sndrpihifiberry"
    fs: int = 44100
    nperiods: int = 3
    period: int = 1024
    outchannels: list = field(default_factory=lambda: [0,1])

    @property
    def launch_str(self) -> str:
        base_str = f'{str(self.bin)} -P{self.priority} -R -d{self.driver}'
        if self.driver == "alsa":
            launch_str: str =  ' '.join(
                [
                    base_str,
                    f'-d{self.device_name} -D -r{self.fs} -n{self.nperiods} -p{self.period} -s &'
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

@dataclass
class Sound:
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
    jack_client: typing.Optional['autopilot.stim.sound.jackclient.JackClient'] = None
    uuid: str = field(default_factory=uuid.uuid4)

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
        return {
            'frequency': self.frequency,
            'amplitude': self.amplitude,
            'duration': self.duration,
            'jack_client': self.jack_client
        }

    @property
    def sound_class(self) -> 'autopilot.stim.sound.sounds.Jack_Sound':
        """
        The sound class that corresponds to the :attr:`.sound_type` retrieved from
        the :mod:`perceptivo.sound.sounds` module.

        Returns:
            :class:`autopilot.stim.sound.sounds.Jack_Sound` - The sound class!
        """
        return getattr(sounds, self.sound_type)







