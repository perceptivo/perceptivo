import perceptivo.types.psychophys
from perceptivo.root import Perceptivo_Object
from abc import abstractmethod
import numpy as np
import typing
from perceptivo import types
import warnings

PLOTTING = False
try:
    import matplotlib.pyplot as plt
    from matplotlib.cm import ScalarMappable
    PLOTTING=True
except ImportError:
    pass


from sklearn.gaussian_process.kernels import Kernel
from perceptivo.psychophys.gaussian import IterativeGPC


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

    Args:
        freq_range (tuple): Tuple of two floats indicating min/max frequency (default: (125, 8500))
        amplitude_range (tuple): Tuple of two floats indicating min/max amplitude in dbSPL (default: (5,60))

    Attributes:
        audiogram (:class:`.types.psychophys.Audiogram`): Audiogram of model
        samples (:class:`.types.psychophys.Samples`): Individual samples of frequency/amplitude and whether a sound was detected.
    """

    def __init__(self, freq_range:typing.Tuple[float,float]=(125,8500),
                 amplitude_range:typing.Tuple[float,float]=(5,60),
                 *args, **kwargs):
        super(Audiogram_Model, self).__init__(*args, **kwargs)

        self._audiogram = None
        self._samples = None

        self.audiogram: perceptivo.types.psychophys.Audiogram
        self.samples: perceptivo.types.psychophys.Samples

        self.freq_range = freq_range
        self.amplitude_range = amplitude_range


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
    * Covariance Function: Squared Exponent (RBF)

    **Process:**
    * Convert sampled frequency to bark with :func:`.f_to_bark`
    * Update model
    * Generate next stimulus
    * Convert back to freq

    Examples:

        .. plot::

            from perceptivo.psychophys.oracle import reference_audiogram
            from perceptivo.psychophys.model import Gaussian_Process
            from perceptivo.types.psychophys import Sample

            oracle = reference_audiogram(scale=3)
            model = Gaussian_Process(amplitude_range=(5,35))

            for i in range(100):
                sound = model.next()
                sample = Sample(response=oracle(sound), sound=sound)
                model.update(sample)

            model.plot()


    References:
        * :cite:p:`coxBayesianBinaryClassification2016`
        * :cite:p:`gardnerBayesianActiveModel2015`
        * :cite:p:`malkomesBayesianOptimizationAutomated2016`
        * :cite:p:`ActiveModelSelection2021`

    """

    def __init__(self, kernel:typing.Optional[Kernel]=None,
                 *args, **kwargs):
        super(Gaussian_Process, self).__init__(*args, **kwargs)

        self._kernel = kernel
        self._samples = [] # type: typing.List[types.psychophys.Sample]
        self._started_fitting = False

        self.model: IterativeGPC = IterativeGPC(
            kernel=self.kernel, warm_start=True, n_restarts_optimizer=5, max_iter_predict=100
        )

        self._plotted = False

        self._xx, self._yy = np.meshgrid(
            np.arange(self.freq_range[0], self.freq_range[1], 100),
            np.arange(self.amplitude_range[0], self.amplitude_range[1], 1),
        )

        self._y = np.c_[self._xx.ravel(), self._yy.ravel()]

    @property
    def kernel(self) -> Kernel:
        """
        Kernel used in the gaussian process model. If ``None`` is given on init,
        use the :class:`.types.psychophys.Kernel`

        Returns:
            :class:`sklearn.gaussian_process.kernels.Kernel`
        """
        if self._kernel is None:
            self._kernel = types.psychophys.Kernel().kernel
        return self._kernel

    @property
    def samples(self) -> types.psychophys.Samples:
        """
        Stored samples from updates

        Returns:
            :class:`~.types.psychophys.Samples`
        """
        return types.psychophys.Samples(self._samples)

    def update(self, sample:types.psychophys.Sample):
        """

        Args:
            sample ():

        Returns:

        """
        if isinstance(sample, list):
            self._samples.extend(sample)
        else:
            self._samples.append(sample)

        df = self.samples.to_df()

        x = np.column_stack([df.frequency, df.amplitude])
        self.model.fit(x, df.response)

    def next(self) -> types.sound.Sound:
        """
        Generate parameters for the next sound to present

        Returns:
            :class:`~.types.sound.Sound`
        """
        if len(self._samples) < 10:
            freq = np.random.rand()*(self.freq_range[1]-self.freq_range[0])+self.freq_range[0]
            amp = np.random.rand()*(self.amplitude_range[1]-self.amplitude_range[0])+self.amplitude_range[0]
            return types.sound.Sound(
                frequency=freq,
                amplitude=amp)

        Z = self.model.predict_proba(self._y)
        Z = Z[:,1]
        uncertain = np.argmin(np.abs(0.5-Z))
        return types.sound.Sound(
            frequency=self._y[uncertain,0],
            amplitude=self._y[uncertain,1]
        )



    def plot(self, mesh_resolution: int= 5):
            """

            References:
                https://scikit-learn.org/stable/auto_examples/gaussian_process/plot_gpc_iris.html#sphx-glr-auto-examples-gaussian-process-plot-gpc-iris-py

            Returns:

            """
            if not PLOTTING:
                warnings.warn('matplotlib was not found')
                return
            xx, yy = np.meshgrid(
                np.arange(self.freq_range[0], self.freq_range[1], mesh_resolution),
                np.arange(self.amplitude_range[0], self.amplitude_range[1], mesh_resolution),
            )

            Z = self.model.predict_proba(np.c_[xx.ravel(), yy.ravel()])

            # Put the result into a color plot
            Z = Z.reshape((xx.shape[0], xx.shape[1], 2))
            # only need the first index, which is "yes response"
            Z = Z[:,:,1]

            plt.figure(num=1,figsize=(12,8))
            plt.gcf().clear()
            im = plt.imshow(Z, extent=(self.freq_range[0], self.freq_range[1], self.amplitude_range[0], self.amplitude_range[1] ),
                       cmap="RdGy", origin="lower", aspect="auto")

            # Plot also the training points
            samples = self.samples.to_df()

            plt.scatter(samples.frequency, samples.amplitude, c=np.array(["r", "k"])[samples.response.values.astype(int)], edgecolors=(1,1,1))
            plt.xlabel("Frequency")
            plt.ylabel("Amplitude")
            plt.xlim(xx.min(), xx.max())
            plt.ylim(yy.min(), yy.max())
            # plt.xticks(())
            # plt.yticks(())
            # if not self._plotted:
            self._cbar = plt.colorbar(ScalarMappable(cmap="RdGy"))
            self._plotted = True


            plt.title(
                "Estimated Audiogram, n={}, LML: {:.3f}".format(
                    samples.shape[0],
                    self.model.log_marginal_likelihood(self.model.kernel_.theta))
            )

            plt.show()











