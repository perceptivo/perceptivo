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
import pdb
import typing
from abc import abstractmethod
from typing import Union, Optional, List, Dict

import numpy as np

from skimage import exposure

from perceptivo.root import Perceptivo_Object
from perceptivo.video import processors
from perceptivo.types.video import Frame
from perceptivo.video.processors import Processor
from perceptivo.types.pupil import Pupil
import autopilot


class PupilExtractor(Perceptivo_Object):
    """
    Base class for pupil extraction strategies.
    """

    def __init__(self,  **kwargs):
        super(PupilExtractor, self).__init__(**kwargs)



    @abstractmethod
    def process(self, frame:Frame) -> Pupil:
        """
        Given a frame, extract a pupil estimate

        Args:
            Frame ():

        Returns:

        """


class EnsembleExtractor(PupilExtractor):
    """
    Extractor that uses an ensemble of techniques to track a pupil

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

    def process(self, frame:Frame):
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