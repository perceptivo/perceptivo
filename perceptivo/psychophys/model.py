import perceptivo.types.psychophys
from perceptivo.root import Perceptivo_Object
from perceptivo import types
from abc import abstractmethod
import numpy as np
import typing
import pandas as pd
from perceptivo import types


from sklearn.gaussian_process.kernels import Kernel, RBF


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

class Gaussian_Process(Audiogram_Model):
    """
    Gaussian process model based on :cite:p:`coxBayesianBinaryClassification2016`

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

    def __init__(self, kernel:typing.Optional[Kernel]=None):

        self._kernel = kernel



    @property
    def kernel(self) -> Kernel:
        """
        Kernel used in the gaussian process model. If ``None`` is given on init,
        use the :class:`.types.psychophys.Default_Kernel`

        Returns:
            :class:`sklearn.gaussian_process.kernels.Kernel`
        """
        if self._kernel is None:
            self._kernel = types.psychophys.Default_Kernel().kernel
        return self._kernel





    def next(self) -> types.sound.Sound:
        pass


def generate_samples(n_samples:int, scale:float=5, freqs=None, amplitudes=None) -> types.psychophys.Samples:
    """
    Generate fake audiometry samples using median threshold values obtained from the NHANES dataset:
    https://wwwn.cdc.gov/Nchs/Nhanes/2015-2016/AUX_I.htm

    The median rates make a piecewise linear function:

    ========= =========
    Frequency Threshold
    ========= =========
    500       10
    1000      10
    2000      10
    3000      10
    4000      15
    6000      20
    8000      20
    ========= =========

    Args:
        n_samples (int): number of samples to generate
        scale (float): amount of randomness to multiply the noise of the pseudo-response threshold by
        freqs (arraylike): (Optional) - predetermined array of frequencies (of length n_samples) to test
        amplitudes (arraylike): (Optional) - predetermined array of amplitudes (of length n_samples) to test

    Returns:
        :class:`.types.psychophys.Samples`
    """

    # generate freqs and amplitudes
    if freqs is None:
        freqs = np.sort((np.random.random(n_samples)*7500) + 500)
    if amplitudes is None:
        amplitudes = np.random.random(n_samples)*50

    responses = np.zeros((n_samples,))

    # piecewise estimate responses given frequency and amplitude
    # for each section, generate random number, scaled by scale param, then boolean whether above or below
    slope_start_idx = np.where(freqs>3000)[0][0]
    slope_end_idx = np.where(freqs>6000)[0][0]

    responses[0:slope_start_idx] = ((np.random.rand(slope_start_idx)*scale)+10-(scale/2))<amplitudes[0:slope_start_idx]
    responses[slope_end_idx:] = ((np.random.rand(n_samples-slope_end_idx)*scale)+20-(scale/2))<amplitudes[slope_end_idx:]

    threshes = (freqs[slope_start_idx:slope_end_idx]-3000)*(10/3000)+10
    responses[slope_start_idx:slope_end_idx] = (np.random.rand(slope_end_idx-slope_start_idx)*scale) + threshes - (scale/2) < amplitudes[slope_start_idx:slope_end_idx]

    return types.psychophys.Samples(responses=responses.astype(bool).tolist(),
                                    frequencies=freqs.tolist(),
                                    amplitudes=amplitudes.tolist())











