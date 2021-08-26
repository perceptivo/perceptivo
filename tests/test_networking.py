
import zmq

def test_zmq_capabilities():
    assert zmq.has('ipc')