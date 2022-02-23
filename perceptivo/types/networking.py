import typing
from dataclasses import field
from pydantic.dataclasses import dataclass
from pydantic import BaseModel

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
    ip: str = '*'


class Clinician_Networking(BaseModel):
    """
    Default networking properties for the Clinician computer
    """
    ip: str = ''
    patient_ip: str = ''
    eyecam: Socket = Socket(
        id='clinician_eyecam',
        socket_type = 'PULL',
        protocol='tcp',
        mode='bind',
        port=5500
    )


class Patient_Networking(BaseModel):
    ip: str = ''
    clinician_ip: str = ''
    eyecam: Socket = Socket(
        id='patient_eyecam',
        socket_type='PUSH',
        protocol='tcp',
        mode='connect',
        port=5500,
        ip=clinician_ip
    )
