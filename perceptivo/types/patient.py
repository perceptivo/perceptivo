import typing
from dataclasses import dataclass, field
from datetime import date

from perceptivo.types.psychophys import Samples, Audiogram

@dataclass
class Biography:
    """
    Biographical details for a patient
    """
    name: str
    dob: date

@dataclass
class Patient:
    """
    Data for a given patient
    """
    biography: Biography
    samples: Samples
    audiogram: Audiogram