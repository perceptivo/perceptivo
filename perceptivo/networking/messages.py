"""
Message classes for explicit typing and the sanity of clear expectations
"""
import typing
import msgpack
from perceptivo.root import Perceptivo_Object
from perceptivo.util import serialize, deserialize


class Message(Perceptivo_Object):
    """
    Message container implementing msgpack-based numpy array de/serialization.

    Subclass this to make specific message types!
    """
    def __init__(self, **kwargs):
        """
        Args:
            **kwargs (dict): key/value pairs stored in :attr:`.Message.value`

        Attrs:
            value (dict): (deserialized) dictionary of values passed from **kwargs

        """
        super(Message, self).__init__()

        self.value = dict(kwargs) # type: typing.Dict

    def serialize(self, msg:typing.Optional[dict]=None) -> bytes:
        if msg is None:
            msg = self.value
        return msgpack.packb(msg, default=serialize)

    @classmethod
    def _deserialize(cls, msg:bytes) -> dict:
        return msgpack.unpackb(msg, object_hook=deserialize)

    @classmethod
    def from_serialized(cls, msg:bytes) -> 'Message':
        """
        Create an instance of Message from a msgpack serialized bytestring
        """
        value = cls._deserialize(msg)
        return Message(**value)



