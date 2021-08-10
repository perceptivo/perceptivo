from datetime import date
from dataclasses import dataclass

@dataclass
class Patient_Data:
    """
    Container for patient-specific data
    """

    name: str
    dob: date