import typing
from dataclasses import dataclass, field
from datetime import date
from pydantic import BaseModel

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


class Collection_Params(BaseModel):
    collection_wait: float = 5
    """
    Total duration to wait to collect pupil frames, starting when the sound does.
    """