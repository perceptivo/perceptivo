"""
Messenger objects for communication intra, interprocess and intercomputer
"""

from typing import Dict, Callable, Optional
from enum import Enum, auto
from collections import deque
import threading

import zmq
from zmq.eventloop.zmqstream import ZMQStream
from tornado.ioloop import IOLoop

from perceptivo.root import Perceptivo_Object
from perceptivo.data.types import Socket

class Node(Perceptivo_Object):

    class Poll_Mode(Enum):
        IOLOOP = auto()
        DEQUE = auto()
        NONE = auto()

    def __init__(self,
                 socket:Socket,
                 poll_mode:Poll_Mode = Poll_Mode.IOLOOP,
                 callback:Optional[Callable]=None,
                 deque_size: int  = 256):
        """
        Wrapper around zmq sockets to send and receive messages


        Args:
            socket (:class:`.types.Socket`): Socket descriptor (see :class:`~.types.Socket`)
            poll_mode (:class:`.Poll_Mode`): Strategy for polling messages.

                * ``IOLOOP`` - uses tornado's IOloop and ZMQStreams to poll for messages.
                    Needs to be given ``callback`` as well, which will be called with the received message as the only argument
                * ``DEQUE`` - a thread is spawned to poll the socket and add any message to ``deque``
                * ``NONE`` - interact with the socket manually

            callback (typing.Callable): A callable object that will be called with a received
                message as its only argument if ``poll_mode == IOLOOP``
        """
        self.id = socket.id
        self.socket_type = socket.socket_type
        self.protocol = socket.protocol
        self.mode = socket.mode
        self.port = socket.port
        self.ip = socket.ip
        self.poll_mode = poll_mode
        self.callback = callback
        self.deque = deque(maxlen=deque_size)

        super(Node, self).__init__()

        self._stopping = threading.Event()

        self.socket: zmq.Socket = self._init_socket()

        self.logger.info(f'Socket initialized - id: {self.id}')

    def _init_socket(self) -> zmq.Socket:
        ctx = zmq.Context.instance()
        socket = ctx.socket(getattr(zmq, self.socket_type))
        socket.setsockopt_string(zmq.IDENTITY, self.id)

        if self.mode == 'bind':
            socket.bind(self.address)
        elif self.mode == 'connect':
            socket.connect(self.address)
        else:
            raise ValueError(f'mode needs to be one of types.ZMQ_MODE, got {self.mode}')

        if self.poll_mode == self.Poll_Mode.IOLOOP:
            socket = ZMQStream(socket)
            if not callable(self.callback):
                raise ValueError(f'Must provide a callback for poll_mode == IOLoop, got {self.callback}')
            socket.on_recv(self.callback)
            loop = IOLoop.current()
            threading.Thread(target=self._start_ioloop, args=(loop,), daemon=True).start()

        elif self.poll_mode == self.Poll_Mode.DEQUE:
            threading.Thread(target=self._start_polling, daemon=True).start()

        return socket

    @property
    def address(self) -> str:
        """
        The full address, including protocol, ip, port, or endpoint, depending on
        the protocol

        Returns:
            str
        """
        if self.mode == 'tcp':
            return f"tcp://{self.ip}:{self.port}"
        elif self.mode == 'ipc':
            return f"ipc:///tmp/{self.port}"
        else:
            raise NotImplementedError('Only tcp and ipc modes are implemented!')

    def send(self, msg, *args, **kwargs):
        """for now just wrapping the socket"""
        self.socket.send(msg, *args, **kwargs)

    def _start_ioloop(self, loop:IOLoop):
        """spawn a tornado ioloop"""
        try:
            loop.start()
        except RuntimeError:
            # loop already started
            pass

    def _start_polling(self):
        """spawn a thread to poll the socket and add incoming messages to the queue"""
        while not self._stopping.is_set():
            msg = self.socket.recv()
            self.deque.append(msg)

    def release(self):
        self._stopping.set()
        self.socket.close()
