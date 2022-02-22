import typing
from dataclasses import field, InitVar
from pydantic.dataclasses import dataclass
from pydantic import Field, BaseModel, PrivateAttr
from datetime import datetime
from sklearn.gaussian_process.kernels import RBF
import pandas as pd
MATPLOTLIB = False
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB = True
except ImportError:
    pass

from perceptivo.types.sound import Sound
from perceptivo.types.pupil import Dilation


@dataclass
class Sample:
    """
    A single sample of a psychophysical response to a sound

    Attributes:
        dilation (:class:`.types.pupil.Dilation`): Pupil object storing dilation for a given sample
        sound (:class:`.types.sound.Sound`): Sound presented to elicit Pupil response
        timestamp (:class:`datetime.datetime`): Timestamp at which the response was elicited

    Properties:
        response (bool): Sub/Subtrathreshold response from :attr:`.Pupil.response`

    """
    dilation: Dilation
    sound: Sound
    timestamp: datetime = field(default_factory=datetime.now)
    response: InitVar[bool] = None

    def __post_init__(self, response):
        self._response = response

    @property
    def response(self) -> bool:
        if self._response is not None:
            # we were passed a manual response object
            return self._response
        else:
            return self.dilation.response

@dataclass(init=False)
class Samples:
    """
    Multiple Samples!

    Convenience class to init samples from numpy arrays and convert to pandas dataframe
    """
    samples: typing.List[Sample]
    responses: typing.List[bool]
    frequencies: typing.List[float]
    amplitudes: typing.List[float]

    def __init__(self, samples:typing.Optional[typing.List[Sample]]=None,
                 dilations:typing.Optional[typing.List[Dilation]]=None,
                 frequencies:typing.Optional[typing.List[float]]=None,
                 amplitudes:typing.Optional[typing.List[float]]=None,
                 responses:typing.Optional[typing.List[bool]]=None):
        if samples is not None and all([isinstance(s, Sample) for s in samples]):
            self.samples = samples
            self.responses = [s.response for s in samples]
            self.frequencies = [s.sound.frequency for s in samples]
            self.amplitudes = [s.sound.amplitude for s in samples]

        elif all([x is not None for x in (dilations, frequencies, amplitudes)]):
            samples = []
            for dilation, freq, amplitude in zip(dilations, frequencies, amplitudes):
                samples.append(Sample(
                    dilation=dilation,
                    sound=Sound(
                        frequency=freq,
                        amplitude=amplitude
                    )))
            self.samples = samples
            self.responses = [s.response for s in self.samples]
            self.frequencies = frequencies
            self.amplitudes = amplitudes

        elif all([x is not None for x in (responses, frequencies, amplitudes)]):
            self.responses = responses
            self.frequencies = frequencies
            self.amplitudes = amplitudes

        elif all([x is None for x in (samples, dilations, frequencies, amplitudes)]):
            # If we're initialized as an empty container, just initialize as empty
            self.samples = []
            self.responses = []
            self.frequencies = []
            self.amplitudes = []

        else:
            raise ValueError(f"Not sure how to init Samples from {samples, dilations, frequencies, amplitudes}")

    def append(self, sample: Sample):
        """
        Add a sample to the collection

        Args:
            sample (:class:`~.types.psychophys.Sample`): A New Sample!

        """
        if not isinstance(sample, Sample):
            raise ValueError(f'Can only append a sample to a Samples object! got {sample}')

        self.samples.append(sample)
        self.responses.append(sample.response)
        self.frequencies.append(sample.sound.frequency)
        self.frequencies.append(sample.sound.amplitude)

    def to_df(self) -> pd.DataFrame:
        """Make a dataframe with sound parameterization flattened out"""
        return pd.DataFrame({
            'response': self.responses,
            'frequency': self.frequencies,
            'amplitude': self.amplitudes
        })

    def plot(self, show=True):
        """
        Plot a collection of samples as points,
        with blue meaning the sample was audible and red meaning inaudible

        Examples:

            .. plot::

                from perceptivo.psychophys.oracle import generate_samples

                samples = generate_samples(n_samples=1000, scale=10)
                samples.plot()


        Args:
            show (bool): If ``True`` (default), call plt.show()

        """
        if not MATPLOTLIB:
            raise ImportError("matplotlib was not found!")

        df = self.to_df()
        colors = ['r' if response == False else 'b' for response in df.response]
        df.plot.scatter(x='frequency', y='amplitude', c=colors)
        if show:
            plt.show()

    def __getitem__(self, item):
        return self.samples[item]


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


# --------------------------------------------------
# Model types
# --------------------------------------------------

class Kernel(BaseModel):
    """
    Default kernel to use with :class:`.psychophys.model.Gaussian_Process`

    Uses a kernel with a short length scale for frequency, but a longer length scale for amplitude,
    which should be smoother/monotonic where frequency can have an unpredictable shape
    """
    length_scale: typing.Tuple[float, float] = (100.0, 200.0)
    length_scale_bounds: typing.Tuple[float, float] = (1, 1e5)
    _kernel: typing.Optional[RBF] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._kernel = None

    @property
    def kernel(self) -> RBF:
        if self._kernel is None:
            self._kernel = RBF(length_scale=self.length_scale,
                               length_scale_bounds=self.length_scale_bounds)
        return self._kernel


    class Config:
        arbitrary_types_allowed = True

MODEL_TYPES = typing.Literal["Gaussian_Process"]

@dataclass
class Psychoacoustic_Model:
    """
    Parameterization of a psychoacoustic model to use to estimate audiograms and
    control the presentation of stimuli
    """
    model_type: MODEL_TYPES = "Gaussian_Process"
    args:typing.Optional[list] = field(default_factory=list)
    kwargs:typing.Optional[dict] = field(default_factory=dict)


