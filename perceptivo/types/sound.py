import shutil
import typing
from dataclasses import dataclass, field
from pathlib import Path


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


@dataclass
class Threshold:
    """
    The audible threshold for a particular frequency

    Args:
        frequency (float): Frequency of threshold in Hz
        threshold (float): Audible threshold in dbSPL
        confidence (float): Confidence of threshold, units vary depending on estimation type
    """
    frequency: float
    threshold: float
    confidence: float = 0


@dataclass
class Audiogram:
    """
    A collection of :class:`.Threshold`s that represent a patient's audiogram.

    Thresholds can be accessed like a dictionary, using frequencies as keys, eg::

        >>> agram = Audiogram([Threshold(1000, 10), Threshold(2000, 20)])
        >>> agram[1000]
        Threshold(frequency=1000, threshold=10, confidence=0)
        >>> agram[3000] = Threshold(3000, 30)
        >>> agram[3000]
        Threshold(frequency=1000, threshold=10, confidence=0)

    """
    thresholds: typing.List[Threshold]

    @property
    def frequencies(self) -> typing.List[float]:
        """List of frequencies in :attr:`.thresholds`"""
        return [thresh.frequency for thresh in self.thresholds]

    def to_dict(self) -> typing.Dict[float, float]:
        """
        Return audiogram thresholds as a {frequency:threshold} dictionary, eg.::

            >>> agram = Audiogram([Threshold(1000, 10), Threshold(2000, 20)])
            >>> agram.to_dict()
            {1000: 10, 2000: 20}

        """
        return {thresh.frequency:thresh.threshold for thresh in self.thresholds}

    def __getitem__(self, key:float) -> Threshold:
        thresh = [thresh for thresh in self.thresholds if thresh.frequency == key]
        if len(thresh) == 0:
            raise KeyError(f'No threshold found with frequency {key}')
        elif len(thresh) == 1:
            return thresh[0]
        else:
            raise KeyError(f'Got multiple thresholds for frequency {key}: {thresh}')

    def __setitem__(self, key:float, value:Threshold):
        # quick consistency check
        if key != value.frequency:
            raise ValueError(f"the assigned key: {key} does not match the frequency of the given Threshold object: {Threshold}")
        # check if we already have one
        thresh = [thresh for thresh in self.thresholds if thresh.frequency == key]
        if len(thresh) == 0:
            # new threshold!
            self.thresholds.append(value)
        elif len(thresh) == 1:
            # we have one! replace it!
            self.thresholds[self.thresholds.index(thresh[0])] = value
        else:
            raise KeyError(f'Already have multiple thresholds for frequency {key}: {thresh} \n something has gone wrong with the way thresholds are being constructed')