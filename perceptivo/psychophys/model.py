import perceptivo.types.psychophys
from perceptivo.root import Perceptivo_Object
from perceptivo import types
from abc import abstractmethod
import numpy as np


def f_to_bark(frequency: float) -> float:
    """
    Convert frequency to Bark using :cite:p:`wangAuditoryDistortionMeasure1991`

    Args:
        frequency (float): Frequency to convert

    Returns:
        (float) Bark
    """
    return 6 * np.arcsinh(frequency/600)


def bark_to_f(bark: float) -> float:
    """
    Convert bark to frequency using inverted :cite:p:`wangAuditoryDistortionMeasure1991`

    Args:
        bark (float): bark to convert

    Returns:
        (float) frequency
    """
    return 600 * np.sinh(bark/6)


class Audiogram_Model(Perceptivo_Object):
    """
    Metaclass for Audiogram models and estimators.

    These classes are used to estimate the audiogram, as well as
    control the order of the presentation of probe sounds.

    .. note::

        This class may be split into an experimental runner class and
        an audiogram model, but since the choice of the next stimulus
        should ideally be based on the current audiogram model,
        they are built together for now.
    """

    def __init__(self):
        self.audiogram: perceptivo.types.psychophys.Audiogram

    @abstractmethod
    def update(self, sample:types.psychophys.Sample):
        """
        Update the model with a new :class:`~.types.psychophys.Sample
        """

    @abstractmethod
    def next(self) -> types.sound.Sound:
        """
        Generate parameters for the next :class:`~.types.sound.Sound` to be presented
        """

class Bayesian_Process(Audiogram_Model):
    """
    Bayesian process model based on :cite:p:`coxBayesianBinaryClassification2016`

    **Model:**
    * Bayesian Process Classifier, predicting binary audibility as a function of frequency and amplitude
    * Kernel:
    * Covariance Function: Squared Exponent

    **Process:**
    * Convert sampled frequency to bark with :func:`.f_to_bark`
    * Update model
    * Generate next stimulus
    * Convert back to freq

    References:
        * :cite:p:`coxBayesianBinaryClassification2016`
        * :cite:p:`gardnerBayesianActiveModel2015`
        * :cite:p:`malkomesBayesianOptimizationAutomated2016`
        * :cite:p:`ActiveModelSelection2021`

    """





