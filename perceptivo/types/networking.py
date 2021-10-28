import typing
from dataclasses import dataclass, field

ZMQ_SOCKET = typing.Literal['REQ', 'REP', 'PUB', 'SUB', 'PAIR', 'DEALER', 'ROUTER', 'PULL', 'PUSH']
ZMQ_PROTOCOL = typing.Literal['tcp', 'ipc', 'inproc']
ZMQ_MODE = typing.Literal['connect', 'bind']


@dataclass
class Socket:
    id: str
    socket_type: ZMQ_SOCKET
    protocol: ZMQ_PROTOCOL
    mode: ZMQ_MODE
    port: int
    ip: str = field(default='*')