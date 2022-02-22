"""
Individual transformation operations for video frames.

To be used with the :class:`perceptivo.video.pupil.PupilExtractor` subclasses

"""
import pdb
import typing
from typing import Union, Optional, List, Dict
from abc import abstractmethod
from types import MethodType
from pathlib import Path
from skimage.transform import hough_circle, hough_circle_peaks

import numpy as np
np.seterr(divide='ignore')
np.seterr(invalid='ignore')
import cv2
from scipy.ndimage import sum as ndisum
from scipy.ndimage import label


from perceptivo.root import Perceptivo_Object
from perceptivo.types.video import Frame
from perceptivo.types.units import Ellipse
from perceptivo import Directories
from perceptivo.util import download



class Processor(Perceptivo_Object):
    """
    Individual processing stage, can be added together to make a processing chain

    ``__add__`` method based on :class:`autopilot.transform.transforms.Transform`

    """

    def __init__(self, **kwargs):
        super(Processor, self).__init__(**kwargs)

        self._child = None
        self._parent = None

    @property
    def parent(self) -> Optional['Processor']:
        """
        If this Transform is in a chain of transforms, the transform that precedes it

        Returns:
            :class:`.Transform`, ``None`` if no parent.
        """
        return self._parent

    @parent.setter
    def parent(self, parent:'Processor'):
        if not issubclass(type(parent), Processor):
            raise TypeError('parents must be subclasses of Transform')
        self._parent = parent


    @abstractmethod
    def process(self, input: Union[Frame, Ellipse]) -> Union[Frame, Ellipse]:
        """
        Process a frame!

        Typically you want a chain of processors to end up outputting an Ellipse,
        but this is not enforced

        .. todo::

            Implement input and output types, check before making!

        Returns:

        """

    def __add__(self, other):
        """
        Add another Transformation in the chain to make a processing pipeline
        Args:
            other (:class:`Transformation`): The transformation to be chained
        """
        if not issubclass(type(other), Processor):
            raise RuntimeError('Can only add subclasses of Transform to other Transforms!')

        if self._child is None:
            # if we haven't been chained at all yet, claim the child
            # first check if it aligns

            #if not self.check_compatible(other):
            #    raise ValueError(f'Incompatible transformation formats: \nOutput: {self.format_out},\nInput: {other.format_in}')

            self._child = other
            self._child.parent = self

            # override our process method with one that calls recursively
            # back it up first
            self._process = self.process

            def new_process(self, input: Union[Frame, Ellipse]) -> Union[Frame, Ellipse]:
                return self._child.process(self._process(input))

            self.process = MethodType(new_process, self)

        else:
            # we already have a child,
            # add it to our child instead (potentially recursively)
            self._child = self._child + other

        return self


class Canny(Processor):
    """
    Canny edge detection.

    Slight modification of :func:`skimage.feature.canny`, but using opencv and
    Scharr kernel rather than sobel for better orientation invariance, and
    also using the eigenvectors of the structure tensor rather than the simple
    hypotenuse

    The source for this class is really blippy because it is optimized for speed!

    Attributes:
        blur_sigma (float): Amount of blurring to use in the initial smoothing step
        low_thresh (float): Low threshold for canny edge detection
        high_thresh (float): High threshold for canny edge detection

    References:

        * :cite:`weickertSchemeCoherenceEnhancingDiffusion2002`
        * :cite:`baghaieStructureTensorBased2015`
        * :cite:`zhangStructureTensorBased2016`

    """

    def __init__(self, blur_sigma:float=1, low_thresh:float=0.2, high_thresh:float=0.5):
        self.blur_sigma = blur_sigma
        self.low_thresh = low_thresh
        self.high_thresh = high_thresh

    def process(self, frame:Frame) -> Frame:
        # else:
        low_thresh = self.low_thresh
        high_thresh = self.high_thresh


        isobel = cv2.GaussianBlur(cv2.Scharr(frame.frame, ddepth=-1, dx=0, dy=1), ksize=(0, 0), sigmaX=self.blur_sigma)
        jsobel = cv2.GaussianBlur(cv2.Scharr(frame.frame, ddepth=-1, dx=1, dy=0), ksize=(0, 0), sigmaX=self.blur_sigma)

        abs_isobel = np.abs(isobel)
        abs_jsobel = np.abs(jsobel)

        Axx = jsobel * jsobel
        Axy = jsobel * isobel
        Ayy = isobel * isobel

        e1 = 0.5 * (Ayy + Axx - np.sqrt((Ayy - Axx) ** 2 + 4 * (Axy ** 2)))
        e2 = 0.5 * (Ayy + Axx + np.sqrt((Ayy - Axx) ** 2 + 4 * (Axy ** 2)))

        magnitude = e2 - e1

        eroded_mask = np.zeros(frame.frame.shape, dtype=np.bool)
        eroded_mask[1:-1, 1:-1] = True

        # --------- Find local maxima --------------
        #
        # Assign each point to have a normal of 0-45 degrees, 45-90 degrees,
        # 90-135 degrees and 135-180 degrees.
        #
        local_maxima = np.zeros(frame.frame.shape, bool)
        # ----- 0 to 45 degrees ------
        pts_plus = (isobel >= 0) & (jsobel >= 0) & (abs_isobel >= abs_jsobel)
        pts_minus = (isobel <= 0) & (jsobel <= 0) & (abs_isobel >= abs_jsobel)
        pts = pts_plus | pts_minus
        pts = eroded_mask & pts
        # Get the magnitudes shifted left to make a matrix of the points to the
        # right of pts. Similarly, shift left and down to get the points to the
        # top right of pts.
        c1 = magnitude[1:, :][pts[:-1, :]]
        c2 = magnitude[1:, 1:][pts[:-1, :-1]]
        m = magnitude[pts]
        w = abs_jsobel[pts] / abs_isobel[pts]
        c_plus = c2 * w + c1 * (1 - w) <= m
        c1 = magnitude[:-1, :][pts[1:, :]]
        c2 = magnitude[:-1, :-1][pts[1:, 1:]]
        c_minus = c2 * w + c1 * (1 - w) <= m
        local_maxima[pts] = c_plus & c_minus
        # ----- 45 to 90 degrees ------
        # Mix diagonal and vertical
        #
        pts_plus = (isobel >= 0) & (jsobel >= 0) & (abs_isobel <= abs_jsobel)
        pts_minus = (isobel <= 0) & (jsobel <= 0) & (abs_isobel <= abs_jsobel)
        pts = pts_plus | pts_minus
        pts = eroded_mask & pts
        c1 = magnitude[:, 1:][pts[:, :-1]]
        c2 = magnitude[1:, 1:][pts[:-1, :-1]]
        m = magnitude[pts]
        w = abs_isobel[pts] / abs_jsobel[pts]
        c_plus = c2 * w + c1 * (1 - w) <= m
        c1 = magnitude[:, :-1][pts[:, 1:]]
        c2 = magnitude[:-1, :-1][pts[1:, 1:]]
        c_minus = c2 * w + c1 * (1 - w) <= m
        local_maxima[pts] = c_plus & c_minus
        # ----- 90 to 135 degrees ------
        # Mix anti-diagonal and vertical
        #
        pts_plus = (isobel <= 0) & (jsobel >= 0) & (abs_isobel <= abs_jsobel)
        pts_minus = (isobel >= 0) & (jsobel <= 0) & (abs_isobel <= abs_jsobel)
        pts = pts_plus | pts_minus
        pts = eroded_mask & pts
        c1a = magnitude[:, 1:][pts[:, :-1]]
        c2a = magnitude[:-1, 1:][pts[1:, :-1]]
        m = magnitude[pts]
        w = abs_isobel[pts] / abs_jsobel[pts]
        c_plus = c2a * w + c1a * (1.0 - w) <= m
        c1 = magnitude[:, :-1][pts[:, 1:]]
        c2 = magnitude[1:, :-1][pts[:-1, 1:]]
        c_minus = c2 * w + c1 * (1.0 - w) <= m
        local_maxima[pts] = c_plus & c_minus
        # ----- 135 to 180 degrees ------
        # Mix anti-diagonal and anti-horizontal
        #
        pts_plus = (isobel <= 0) & (jsobel >= 0) & (abs_isobel >= abs_jsobel)
        pts_minus = (isobel >= 0) & (jsobel <= 0) & (abs_isobel >= abs_jsobel)
        pts = pts_plus | pts_minus
        pts = eroded_mask & pts
        c1 = magnitude[:-1, :][pts[1:, :]]
        c2 = magnitude[:-1, 1:][pts[1:, :-1]]
        m = magnitude[pts]
        w = abs_jsobel[pts] / abs_isobel[pts]
        c_plus = c2 * w + c1 * (1 - w) <= m
        c1 = magnitude[1:, :][pts[:-1, :]]
        c2 = magnitude[1:, :-1][pts[:-1, 1:]]
        c_minus = c2 * w + c1 * (1 - w) <= m
        local_maxima[pts] = c_plus & c_minus

        #
        # ---- Create two masks at the two thresholds.
        #
        high_mask = local_maxima & (magnitude >= high_thresh)
        low_mask = local_maxima & (magnitude >= low_thresh)
        #
        # Segment the low-mask, then only keep low-segments that have
        # some high_mask component in them
        #
        strel = np.ones((3, 3), bool)
        labels, count = label(low_mask, strel)
        if count == 0:
            return low_mask

        sums = (np.array(ndisum(high_mask, labels,
                                 np.arange(count, dtype=np.int32) + 1),
                         copy=False, ndmin=1))
        good_label = np.zeros((count + 1,), bool)
        good_label[1:] = sums > 0
        output_mask = good_label[labels]

        # skeletonize to reduce thick pixels we mighta missed
        # output_mask = morphology.skeletonize(output_mask)

        return output_mask


class Haar_Tracker(Processor):
    """
    Download and use a haar cascade to track.

    Many trained cascade .xml files are available at https://github.com/opencv/opencv/tree/master/data/haarcascades

    References:

        * `OpenCV Cascade Classifier Tutorial <https://docs.opencv.org/4.5.5/db/d28/tutorial_cascade_classifier.html>`_


    """

    XML_URLS = {
        'eye': 'https://raw.githubusercontent.com/opencv/opencv/415a42f327104653604fc99314eb215cd938d6d7/data/haarcascades/haarcascade_eye.xml',
        'face_default': 'https://raw.githubusercontent.com/opencv/opencv/415a42f327104653604fc99314eb215cd938d6d7/data/haarcascades/haarcascade_frontalface_default.xml',
    }

    def __init__(self,
                 tracker_type:str='eye',
                 min_neighbors:int=20,
                 adaptive_neighbors:bool=True,
                 **kwargs):
        super(Haar_Tracker, self).__init__(**kwargs)

        self.min_neighbors = min_neighbors
        self.tracker_type = tracker_type
        self.adaptive_neighbors = adaptive_neighbors
        self.tracker = cv2.CascadeClassifier()
        filename = str(self.filename)
        self.logger.debug(f'using filename {filename}')
        self.tracker.load(filename)


    @property
    def url(self) -> str:
        return self.XML_URLS[self.tracker_type]

    @property
    def filename(self) -> Path:
        filename = Directories.user_dir / Path(self.url).name
        if not filename.exists():
            self.logger.warning(
                f'Could not find haar cascade file for tracker {self.tracker_type}, downloading to {str(filename)}')

            success = download(self.url, filename)
        return filename

    def process(self, frame:Frame) -> typing.Tuple[typing.List[tuple], typing.List[int]]:
        """

        Args:
            frame (Frame):

        Returns:
            list of tuples  corresponding to (x,y,width,height)
        """
        eyes, numDetections = self.tracker.detectMultiScale2(
            frame.frame, minNeighbors=self.min_neighbors)
        if len(eyes) == 0:
            self.min_neighbors -= 1
        elif len(eyes) > 2:
            self.min_neighbors += 1

        return eyes, numDetections


class Filtered_Hough(Processor):
    """
    A hough transform to detect circles, returning the one that bounds
    the darkest area in the image
    """

    def __init__(self,
                 radii=(15,30,100),
                 max_considered = 3,
                 peaks_kwargs: typing.Optional[dict]= None):
        self.radii = radii
        self.max_considered = max_considered
        if peaks_kwargs is None:
            self.peaks_kwargs = {}
        else:
            self.peaks_kwargs = peaks_kwargs



    def process(self, edges:np.ndarray):
        """
        Frame to process, along with edges from canny edge detection
        """
        circs = hough_circle(edges, self.radii)
        accum, cx, cy, crad = hough_circle_peaks(
            circs,
            self.radii,
            num_peaks = self.max_considered,
            **self.peaks_kwargs
        )
        circs = [(x, y, rad) for x, y, rad in zip(cx, cy, crad)]

        return circs


class Filter_Circles(Processor):
    """
    Filter Circles!
    """

    def __init__(self, prior_bias = 0.5):
        """

        Args:
            prior_bias (float): how strongly to weight the similarity to the prior circle, if given
        """
        self.prior_bias = prior_bias

    def process(self, frame:Frame,circles, prev_eye=None):
        # find the darkest one
        values = []
        for x, y, rad in circles:
            mean_val = np.mean(
                frame.frame[
                    circle_to_mask(frame.frame, x, y, rad)
                ])
            if prev_eye:
                diff = np.mean(np.abs(np.array([x, y, rad]) - prev_eye))*self.prior_bias
            else:
                diff = 1

            values.append(
                mean_val * diff
            )

        if len(values) == 0:
            return False

        which = np.argmin(values)
        return circles[which]


def circle_to_mask(frame, ix, iy, rad):
    nx, ny = frame.shape
    pmask_x, pmask_y = np.ogrid[-iy:nx - iy, -ix:ny - ix]
    pmask = pmask_x ** 2 + pmask_y ** 2 <= rad ** 2
    return pmask


