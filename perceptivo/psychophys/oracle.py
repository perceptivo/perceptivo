"""
Oracle functions for testing model
"""
import typing
import numpy as np
import pdb

from perceptivo import types
from perceptivo.root import Perceptivo_Object
from perceptivo import types

def piecewise_probabilistic(points:np.ndarray, scale:float=5) -> callable:
    """
    Make a piecewise function along a series of (frequency, amplitude) points
    with some gaussian error

    Args:
        points (np.ndarray): n x 2 array of x/y (frequency, amplitude) coordinates that make up an audiogram
        scale (float): Scale parameter of noise in amplitude domain to get answers "wrong"

    Returns:

    """
    # resort points based on first column
    order = np.argsort(points[:,0])
    points = points[order,:]


    def _piecewise(sample: types.sound.Sound):
        # check ends
        if sample.frequency < np.min(points[:,0]):
            y = points[0,1]
        elif sample.frequency > np.max(points[:,0]):
            y = points[-1,1]
        else:
            # somewhere in the range
            l_idx = np.argwhere(sample.frequency>=points[:,0])[-1]
            r_idx = np.argwhere(sample.frequency<=points[:,0])[0]

            # compute y from line between points
            slope = (points[r_idx,1]-points[l_idx,1])/(points[r_idx,0]-points[l_idx,0])
            intercept = points[l_idx,1] - (slope*points[l_idx,0])

            y = sample.frequency*slope + intercept

        # add noise to the threshold to simulate error
        y += np.random.normal(loc=0, scale=scale)

        if isinstance(y, np.ndarray) and y.shape  == (1,):
            y = y[0]

        return sample.amplitude > y

    return _piecewise



def reference_audiogram(scale:float=2) -> callable:
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
        scale (float): amount of randomness to multiply the noise of the pseudo-response threshold by

    Returns:
        callable made by :func:`.piecewise_probabilistic` that works as an oracle function
    Args:
        scale ():

    Returns:
        A numpy piecewise function that returns Sample objects for a given input frequency and amplitude
    """
    points = np.array(
        ((500 ,      10),
        (1000,      10),
        (2000,      10),
        (3000,      10),
        (4000,      15),
        (6000,      20),
        (8000,      20))
    )

    return piecewise_probabilistic(points, scale=scale)


def generate_samples(n_samples:int, scale:float=2, freqs=None, amplitudes=None, randomize=False, freq_range=(500,8000), amplitude_range=(0,50),
                     oracle:typing.Optional[callable] = None) -> types.psychophys.Samples:
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

    Examples:

        .. plot::

            from perceptivo.psychophys.oracle import generate_samples

            samples = generate_samples(n_samples=1000, scale=10)
            samples.plot()


    Args:
        n_samples (int): number of samples to generate
        scale (float): amount of randomness to multiply the noise of the pseudo-response threshold by
        freqs (arraylike): (Optional) - predetermined array of frequencies (of length n_samples) to test
        amplitudes (arraylike): (Optional) - predetermined array of amplitudes (of length n_samples) to test
        randomize (bool): Randomize order of samples before returning, (default ``False``)

    Returns:
        :class:`.types.psychophys.Samples`
    """

    # generate freqs and amplitudes
    if freqs is None:
        freqs = np.sort((np.random.random(n_samples)*(freq_range[1]-freq_range[0])) + freq_range[0])
    if amplitudes is None:
        amplitudes = np.random.random(n_samples)*(amplitude_range[1]-amplitude_range[0]) + amplitude_range[0]

    if oracle is None:
        oracle = reference_audiogram(scale=scale)

    responses = []
    for i in range(n_samples):
        responses.append(oracle(types.sound.Sound(frequency=freqs[i], amplitude=amplitudes[i])))

    responses = np.array(responses)


    if randomize:
        reorder = list(range(n_samples))
        np.random.shuffle(reorder)
        responses = responses[reorder]
        freqs = freqs[reorder]
        amplitudes = amplitudes[reorder]

    return types.psychophys.Samples(responses=responses.astype(bool).tolist(),
                                    frequencies=freqs.tolist(),
                                    amplitudes=amplitudes.tolist())