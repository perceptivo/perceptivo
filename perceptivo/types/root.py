from pydantic import BaseModel
from datetime import datetime
from perceptivo.util import msgpack_dumps, msgpack_loads, pack_array
import numpy as np

class PerceptivoType(BaseModel):

    class Config:
        json_encoders = {
            np.ndarray: pack_array,
            datetime: lambda v: v.isoformat()
        }
        underscore_attrs_are_private = True