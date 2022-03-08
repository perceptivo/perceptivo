"""
Utility functions! everyone's favorite!
"""
import sys
import typing
from typing import Union
from pathlib import Path
from datetime import datetime
import importlib
import pdb
import cv2

import numpy as np
from tqdm import tqdm
import msgpack
from pydantic.main import ModelMetaclass

import requests

def download(url:str, file_name:typing.Union[Path,str]) -> bool:
    """
    Download a file with a progress bar

    Returns:
        bool: ``True`` if nothing happened and its probs good, ``False`` otherwise

    References:
        https://gist.github.com/yanqd0/c13ed29e29432e3cf3e7c38467f42f51
    """

    response = requests.get(url, stream=True)
    size = int(response.headers.get('content-length', 0))
    with open(file_name, 'wb') as ofile, tqdm(
                desc=str(file_name),
                total=size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = ofile.write(data)
            pbar.update(size)
    return True


def pack_array(array) -> dict:
    return {
        '__numpy__': True,
        'shape': array.shape,
        'dtype': str(array.dtype),
        'array': array.data
    }

def unpack_array(shape:tuple, dtype:np.dtype, array:bytes) -> np.ndarray:
    return np.ndarray(
        shape,
        dtype,
        array
    )

def serialize(array: typing.Union[np.ndarray, typing.Any]) -> typing.Union[dict, typing.Any]:
    """
    Serialization for use with ``msgpack.packb`` as ``default``

    Returns:
        dict like::

            {
                '__numpy__': True,
                'shape': array.shape,
                'dtype': str(array.dtype),
                'array': array.data
            }

    """
    if isinstance(array, np.ndarray):
        # return pack_array(array)
        # return {'__numpy__':blosc2.pack(array, 5)}
        _, jpg_buf = cv2.imencode('.jpg', array)
        return {'__numpy__':jpg_buf}
    elif isinstance(array, np.dtype):
        return {
            '__dtype__': str(array)
        }
    elif isinstance(type(array), ModelMetaclass):
        # pdb.set_trace()
        return {
            '__perceptivo_type__': True,
            'module': type(array).__module__,
            'type': type(array).__name__,
            'value':array.dict()
        }
    elif isinstance(array, datetime):
        return {
            '__datetime__': True,
            'value': array.isoformat()
        }
    else:
        return array


def deserialize(obj):
    if b'__numpy__' in obj:
        pass
        # return unpack_array(
        #     obj[b'shape'],
        #     np.dtype(obj[b'dtype'].decode('utf-8')),
        #     obj[b'array']
        # )
        # return blosc2.unpack(obj[b'__numpy__'])

    elif '__numpy__' in obj:
        # return unpack_array(
        #     obj['shape'],
        #     np.dtype(obj['dtype']),
        #     obj['array']
        # )
        # return blosc2.unpack(obj['__numpy__'])
        arr = np.frombuffer(obj['__numpy__'], dtype='uint8')
        return cv2.imdecode(arr, -1)
    elif '__dtype__' in obj:
        return np.dtype(obj['__dtype__'])
    elif '__datetime__' in obj:
        return datetime.fromisoformat(obj['value'])
    elif '__perceptivo_type__' in obj:
        # make sure it's imported
        if obj['module'] not in sys.modules:
            spec = importlib.util.find_spec(obj['module'])
            module = importlib.util.module_from_spec(spec)
            sys.modules[obj['module']] = module
            spec.loader.exec_module(module)
        type_class = getattr(sys.modules[obj['module']], obj['type'])
        return type_class(**obj['value'])
    else:
        return obj


def msgpack_loads(msg):
    """Wrapper of the msgpack """
    return msgpack.unpackb(msg, object_hook=deserialize)


def msgpack_dumps(msg, *, default=None):
    return msgpack.packb(msg, default=serialize).decode('utf-8')