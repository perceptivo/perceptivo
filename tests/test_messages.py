import pdb
from pydantic.main import ModelMetaclass
from perceptivo.networking import messages
from perceptivo.types.video import Frame
import numpy as np

def compare_dict(a, b):
    assert len(a) == len(b)
    for key, val in a.items():
        if isinstance(val, np.ndarray):
            np.testing.assert_array_equal(val, b[key])
        elif isinstance(type(val), ModelMetaclass):
            compare_dict(val.dict(), b[key].dict())
        else:
            assert val == b[key]

def test_serialization():
    """
    Test that serialization and deserialization of numpy arrays works!
    """

    test_msg = {
        'astring': 'valuestring',
        'alist': [1,2,'a',True],
        'anarray': np.random.randint(0,255,(1920,1080,3),'uint8')
    }

    msg = messages.Message(**test_msg)
    serialized = msg.serialize()

    msg2 = messages.Message.from_serialized(serialized)

    compare_dict(msg2.value, test_msg)


def test_serialize_types():
    """
    Test whether custom perceptivo types can be serialized or not
    """

    frame = Frame(frame=np.random.randint(0,255,(1920,1080,3),'uint8'))
    test_msg = {
        'frame': frame
    }

    msg = messages.Message(**test_msg)

    serialized = msg.serialize()

    msg2 = messages.Message.from_serialized(serialized)
    compare_dict(msg2.value, test_msg)


