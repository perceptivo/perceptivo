"""
Types for controlling the administration of the examination
"""
import typing
from typing import Tuple, Dict, List, Union, Optional

from perceptivo.types.root import PerceptivoType

class Completion_Metric(PerceptivoType):
    """
    A means of deciding whether the exam is completed or not
    """
    log_likelihood: Optional[float] = -70
    """
    End exam when log likelihood of model is below this value
    """
    n_trials: Optional[int] = None
    """
    End exam after n trials
    """
    duration: Optional[float] = None
    """
    End exam after n minutes
    """

    use: str = 'any'
    """
    Name of which (non-None) metric to use. Default ``any`` for ending exam if any
    of the criteria are met
    """


class Exam_Params(PerceptivoType):
    frequencies: Tuple[float]
    """Frequencies (Hz) to test in exam"""
    amplitudes: Tuple[float]
    """Amplitudes (dbSPL) to test in exam"""
    iti: float
    """Seconds between each trial"""
    iti_jitter: float = 0.1
    """
    Amount to jitter trials as a proportion of the ITI (eg. 0.1 for an iti of 5s would be maximum 0.5s of jitter)
    """
    completion_metric:Completion_Metric = Completion_Metric()
    """
    Metric that decides when the exam is over.
    """
    allow_repeats: bool = False
    """
    Allow repeated sounds
    """


