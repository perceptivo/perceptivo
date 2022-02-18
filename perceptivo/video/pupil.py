"""
Process and extract pupil

Sketch of default strategy:

* Track to find approximate position of eyes with :class:`.processors.Haar_Tracker`
* Mask image around both eyes, split processing in parallel L/R (if present)
* Use white of eyes to mask cornea and pupil
* Sigmoid filter images to separate cornea and pupil
* Blob detection to find center mass of pupil
* Compare blob vs. edge detection of pupil.
* Use Kalman filter on :class:`perceptivo.types.units.Ellipse` properties to avoid
  jumps and all that

"""

import typing
from abc import abstractmethod
from typing import Union, Optional, List, Dict

import numpy as np

from skimage import exposure, morphology, filters, measure, draw

from perceptivo.root import Perceptivo_Object
from perceptivo.video import processors
from perceptivo.types.video import Frame
from perceptivo.types.pupil import Pupil
from perceptivo.types.units import Ellipse
import autopilot


class PupilExtractor(Perceptivo_Object):
    """
    Base class for pupil extraction strategies.
    """

    def __init__(self,
                 preprocessor:typing.Optional['Preprocessor']=None,
                 filter:typing.Optional['PupilFilter']=None,
                 **kwargs):
        super(PupilExtractor, self).__init__(**kwargs)
        self.preprocessor = preprocessor
        self.filter = filter

    def process(self, frame:Frame) -> Pupil:
        """
        Call :meth:`.preprocess` and then :meth:`._process`, returning a Pupil estimate

        Args:
            frame (:class:`.types.video.Frame`): Frame to process

        Returns:
            :class:`.types.pupil.Pupil` Pupil Estimate
        """
        if self.preprocessor is not None:
            frame = self.preprocessor.process(frame)

        pupil = self._process(frame)

        if self.filter is not None:
            pupil = self.filter.process(pupil)

        return pupil


    @abstractmethod
    def _process(self, frame:Frame) -> Pupil:
        """
        Given a frame, extract a pupil estimate

        Args:
            frame (:class:`.types.video.Frame`): Frame to process!

        Returns:
            :class:`.types.pupil.Pupil` : Estimated Pupil!
        """


class PupilFilter(Perceptivo_Object):
    """
    Base class for filtering pupil tracks -- for example by
    using a Kalman filter to filter erroneous pupil detections from a :class:`.PupilExtractor` .

    PupilFilters should be given to the :class:`.PupilExtractor` as its `filter` argument,
    and should be called last in the :meth:`.PupilExtractor.process` method.

    Each subclass should implement a ``_process`` method that takes and returns a
    :class:`.Pupil` object.
    """
    def __init__(self, **kwargs):
        super(PupilFilter, self).__init__(**kwargs)
        self.last_pupil = None # type: typing.Optional[Pupil]

    def process(self, pupil:Pupil) -> Pupil:
        pupil = self._process(pupil)
        self.last_pupil = pupil
        return pupil

    @abstractmethod
    def _process(self, pupil:Pupil) -> Pupil:
        pass


class Preprocessor(Perceptivo_Object):
    """
    Base class for preprocessing images before they reach the main :meth:`.PupilExtractor.process` method.

    Each subclass should implement a ``process`` method that takes and returns
    a :class:`.Frame` object.
    """

    def __init__(self, **kwargs):
        super(Preprocessor, self).__init__(**kwargs)

    @abstractmethod
    def process(self, frame: Frame) -> Frame:
        pass


# --------------------------------------------------
# Extractors
# --------------------------------------------------

class EllipseExtractor(PupilExtractor):
    """
    Very simple extractor that estimates an ellipse from the edges of a pupil.
    This extractor assumes that the :class:`.Frame` given to it has very high contrast,
    ie. that the rest of the face is essentially white and the pupil and cornea are the only
    colored things in the image.

    In order

    * Median Filter to smooth image - :func:`skimage.filters.rank.median`
    * Scharr Filter to detect edges - :func:`skimage.filters.scharr`
    * Get the otsu threshold on the scharr filtered image - :func:`skimage.filters.threshold_otsu`
    * Skeletonize the pixels above the threshold - :func:`skimage.morphology.skeletonize`
    * Label the independent edges - :func:`skimage.measure.label`
    * If present, use the :class:`.types.units.Ellipse` from  :attr:`PupilExtractor.filter.last_pupil` to
      select only those edges within the ellipse (scaled by :attr:`.search_scale` )
    * Estimate ellipses from remaining edges - :class:`skimage.measure.EllipseModel`
    * Keep the ellipses with the lowest median pixel value (presumably the pupil is dark)
    * Return a :class:`.Pupil` object.

    .. todo::

        I could add in a few other quality metrics, like the proportion of the circumference
        of the ellipse that's supported by edge points, or the similarity to the previous
        ellipse... or we could fit all the ellipses and take the mean of the parameters.
        Keeping it simple for now for the purposes of prototyping


    References:

        * Read a few years ago, might be worth revisiting: https://cdn.intechopen.com/pdfs/33559/InTech-Methods_for_ellipse_detection_from_edge_maps_of_real_images.pdf

    """

    def __init__(
            self,
            footprint_size:int=5,
            search_scale:float=1.5,
            **kwargs):
        """

        Args:
            footprint_size (int): Diameter of footprint (a :func:`skimage.morphology.disk` )
                used in the median filter :func:`skimage.filters.rank.median` . This should be roughly
                the size of the pupil.
            search_scale (float): If present, how much to scale the :attr:`PupilExtractor.filter.last_pupil` to
                select edges before fitting ellipses. Eg. ``1.5`` enlarges the last ellipse by 1.5 and rejects all
                edges outside of that radius.
            **kwargs ():
        """
        super(EllipseExtractor, self).__init__(**kwargs)
        self._footprint_size = None
        self.footprint_size = footprint_size
        self.search_scale = search_scale
        self.footprint = morphology.disk(self.footprint_size)
        self._mask_arr = None

    @property
    def footprint_size(self) -> int:
        """
        As described in the ``attr`` docstring. When setting a footprint size,
        remake the :attr:`.footprint`

        Returns:
            int
        """
        return self._footprint_size

    @footprint_size.setter
    def footprint_size(self, footprint_size: int):
        self._footprint_size = footprint_size
        self.footprint = morphology.disk(self._footprint_size)



    def _process(self, frame:Frame) -> Pupil:

        # make a local copy of the grayscale image to process
        frame_proc = frame.gray.copy()

        # median filter
        frame_proc = filters.rank.median(frame_proc, footprint=self.footprint, out=frame_proc)

        # scharr to detect edges, then filter and skeletonize to 1px wide
        edges = filters.scharr(frame_proc)
        thresh = filters.threshold_otsu(edges)
        edges = morphology.skeletonize(edges>thresh)
        edges = morphology.label(edges)

        # if we have a previous ellipse, then use it to remove extraneous edges
        edges = self.filter_edges(edges)

        ellipse = self.choose_ellipse(edges, frame_proc)

        # create and return our pupil object
        pupil = Pupil(
            ellipse= Ellipse(
                x=ellipse.params[1],
                y=ellipse.params[0],
                a=ellipse.params[3],
                b=ellipse.params[2],
                t=ellipse.params[4]
            ),
            frame=frame
        )
        return pupil


    def filter_edges(self, edges:np.ndarray) -> np.ndarray:
        """
        Set all edges outside of a search radius, given our previous ellipse, to zero
        """
        if self.filter is not None and self.filter.last_pupil is not None:
            mask = self.filter.last_pupil.ellipse.mask(self.search_scale)
            # make coordinates of mask into boolean array. preallocate...
            if self._mask_arr is None:
                self._mask_arr = np.zeros((edges.shape[0], edges.shape[1]), dtype=bool)
            else:
                self._mask_arr[:] = False
            self._mask_arr[mask[0], mask[1]] = True

            # set everything outside our mask to 0
            edges[~self._mask_arr] = 0
        else:
            self.logger.debug('No filter or no previous pupil to filter with')

        return edges

    def choose_ellipse(self, edges:np.ndarray, frame:np.ndarray) -> 'measure.EllipseModel':
        """
        Given an array of edge labels (from :func:`skimage.morphology.label`), usually
        from :meth:`._process`, return an :class:`skimage.measure.EllipseModel` , choose
        the one that is the pupil

        .. todo::

            For now we just select based on the lowest median pixel value, but this should
            probably be better. Separating into a separate method to keep it clean in case
            that needs to happen.

        Args:
            edges (): An array of image labels, ie. an array of ints where background == 0, edge 1 == 1, and so on.
            frame (): The original or filtered image frame (the array, not the :class:`.Frame` object)

        Returns:
            :class:`skimage.measure.EllipseModel` : the most pupil-like ellipse
        """
        n_labels = np.unique(edges)
        ells = []
        med_values = []
        for i in n_labels:
            if i == 0:
                continue

            # Estimate ellipse from edge points
            pts = np.where(edges==i)
            pts = np.column_stack(pts[1], pts[0])
            model = measure.EllipseModel()
            ok = model.estimate(pts)
            if not ok:
                continue

            # compute median value inside ellipse
            rr, cc = draw.ellipse(
                model.params[1], model.params[0],
                model.params[2], model.params[3],
                rotation=model.params[4])
            # clip to avoid indexing errors
            rr, cc = np.clip(rr, 0, edges.shape[0]-1), np.clip(cc, 0, edges.shape[1]-1)

            # take median of points within ellipse and stash
            med_values.append(np.median(np.ravel(frame[rr,cc])))
            ells.append(model)

        # pick the one with the lowest median value!
        lowest_idx = np.argmin(med_values)
        return ells[lowest_idx]
















class EnsembleExtractor_NonIR(PupilExtractor):
    """
    Extractor that uses an ensemble of techniques to track a pupil.

    Written before realizing the trakcing problem was much easier using IR! Kept to mine parts from before discontinuing

    * Track to find approximate position of eyes with :class:`.processors.Haar_Tracker`
    * Mask image around both eyes, split processing in parallel L/R (if present)
    * Use white of eyes to mask cornea and pupil
    * Sigmoid filter images to separate cornea and pupil
    * Blob detection to find center mass of pupil
    * Compare blob vs. edge detection of pupil.
    * Use Kalman filter on :class:`perceptivo.types.units.Ellipse` properties to avoid
      jumps and all that
    """

    def __init__(self,
                 sigmoid = (0.5, 5),
                 canny_kwargs: Optional[dict] = None,
                 hough_kwargs: Optional[dict] = None,
                 *args, **kwargs):
        super(EnsembleExtractor, self).__init__(*args, **kwargs)

        self._eye_position = None
        self._smoothed_eye = None
        self._eyes = None # eyes detected by haar filter
        self._num_detections = None # number of neighbors detected for each eye
        self._filtered_circle = None
        self._sig_cutoff, self._sig_gain = sigmoid
        if canny_kwargs is None:
            canny_kwargs = {}
        if hough_kwargs is None:
            hough_kwargs = {}

        self.eyemask_kalman = autopilot.get('transform', 'Kalman')(
            dim_state = 4) # type: 'autopilot.transform.timeseries.Kalman'


        self.haar = processors.Haar_Tracker()
        self.canny = processors.Canny(**canny_kwargs)
        self.hough = processors.Filtered_Hough(**hough_kwargs)
        self.circle_filter = processors.Filter_Circles()

    def preprocess(self, frame:Frame) -> Frame:
        return frame

    def _process(self, frame:Frame):
        self._frame = frame
        frame = self.preprocess(frame)

        # detect eyes with haar detector
        self._eyes, self._num_detections = self.haar.process(frame)

        # filter with kalman filter
        if len(self._num_detections)>0:
            best_eye = self._eyes[np.argmax(self._num_detections)]
            self._smoothed_eye = self.eyemask_kalman.process(best_eye)

        if self._smoothed_eye is None:
            self._smoothed_eye = [0,0,1,1]

        # crop to eye
        bbox = self._bbox_from_circle(self._smoothed_eye)
        self._cropped = frame.crop(bbox)
        self._cropped.set_color(False)
        self._cropped.norm()

        # adjust exposure
        self._cropped.frame = exposure.equalize_hist(self._cropped.frame)
        self._cropped.frame = exposure.adjust_sigmoid(self._cropped.frame, self._sig_cutoff, self._sig_gain)

        self._canny_edges = self.canny.process(self._cropped)

        if self._filtered_circle:
            hough_radii = [*self.hough.radii]
            hough_radii = hough_radii[0:-1]
            hough_radii.append(self._filtered_circle[2])


        self._circles = self.hough.process(self._canny_edges)
        self._filtered_circle = self.circle_filter.process(self._cropped, self._circles, self._filtered_circle)
        if self._filtered_circle is False:
            self._filtered_circle = (0,0,1)

        return frame

    def _bbox_from_circle(self, circle:typing.List[int]):
        """convert opencv's circles to a bounding box (top, bottom, left, right)"""
        # top = int(np.round(circle[1] - (circle[3] / 2)))
        # bottom  = int(np.round(circle[1] + (circle[3] / 2)))
        # left = int(np.round(circle[0] - (circle[2] / 2)))
        # right  = int(np.round(circle[0] + (circle[2] / 2)))

        top = int(circle[1])
        bottom = top + int(circle[3])
        left = int(circle[0])
        right = left + int(circle[2])


        bbox = [
            max([0, top]),
            min([self._frame.frame.shape[0], bottom]),
            max([0, left]),
            min([self._frame.frame.shape[1], right]),
        ]
        return bbox

    def _circle_mask(self, frame, ix, iy, rad):
        # get a boolean mask from circular parameters
        nx, ny = frame.shape[0:2]
        pmask_x, pmask_y = np.ogrid[-iy:nx - iy, -ix:ny - ix]
        pmask = pmask_x ** 2 + pmask_y ** 2 <= rad ** 2

        return pmask