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
        id='clinician:eyecam',
        socket_type = 'PULL',
        protocol='tcp',
        mode='bind',
        port=5500
    )
    control: Socket = Socket(
        id="clinician:control",
        socket_type = 'ROUTER',
        protocol='tcp',
        mode='bind',
        port=5600
    )



class Patient_Networking(BaseModel):
    ip: str = ''
    clinician_ip: str = ''
    eyecam: Socket = Socket(
        id='patient:eyecam',
        socket_type='PUSH',
        protocol='tcp',
        mode='connect',
        port=5500,
        ip=clinician_ip
    )
    control: Socket = Socket(
        id='patient:control',
        socket_type='DEALER',
        protocol='tcp',
        mode='connect',
        port=5600,
        ip=clinician_ip
    )
