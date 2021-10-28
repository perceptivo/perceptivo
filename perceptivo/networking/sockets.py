"""
Abstract description of socket topology.

Each entry in each dict is a set of sockets to be run in an independent process.
"""

from perceptivo.types.networking import Socket

CLINICIAN_IP = "192.168.0.100"
EXAMINER_IP = "192.168.0.101"
STIM_IP = "192.168.0.102"

CLINICIAN = {
    'gui': (
        Socket('clinician.command', 'PUB', 'tcp', 'bind', 5000),
        Socket('clinician.data', 'ROUTER', 'tcp', 'bind', 5001)
    )
}
"""
Sockets used by the clinician object

* ``clinician.command`` - ``PUB`` socket for dispersing control commands to subordinate computers
* ``clincian.data`` - ``ROUTER`` for receiving data from subordinate computers
"""

EXAMINER = {
    'manager':(
        Socket('examiner.manager.command', 'SUB', 'tcp', 'connect', 5000, CLINICIAN_IP),
        Socket('examiner.manager.process', 'ROUTER', 'ipc', 'bind', 5002),
        Socket('examiner.manager.data_out', 'DEALER', 'ipc', 'connect', 5003, 'localhost')
    ),
    'picamera': (
        Socket('examiner.picamera.data_out', 'DEALER', 'ipc', 'connect', 5002),
    ),
    'data':(
        Socket('examiner.data_in', 'ROUTER', 'ipc', 'bind', 5003),
        Socket('examiner.data_out', 'DEALER', 'tcp', 'connect', 5001, CLINICIAN_IP),
    )
}
"""
Sockets used by the 'examiner' machine responsible for managing the exam -
measuring the pupil, presenting sounds, and maintaining the psychoacoustic model

Processes:

**manager**

* ``examiner.manager.command`` - ``SUB`` - subscriber to clinician commands
* ``examiner.manager.process`` - ``ROUTER`` - receives data from picamera
* ``examiner.manager.data_out`` - ``DEALER`` - sends data to the ``data`` process to forward to clinician

**picamera**

* ``examiner.picamera.data_out`` - ``DEALER`` - sends frames to the ``process`` socket

**data**

* ``examiner.data.data_in`` - ``ROUTER`` - receives data from ``process``
* ``examiner.data.data_out`` - ``DEALER`` - sends data to clinician
"""

STIM = {
    'stim': (
        Socket('stim.command', 'SUB', 'tcp', 'connect', 5000, CLINICIAN_IP),
        Socket('stim.manager', 'DEALER', 'tcp', 'connect', 5002, EXAMINER_IP)
    )
}
"""
Sockets used by the stimulus delivery machine

* ``stim.command`` - ``SUB`` - subscriber to clinician commands
* ``stim.manager`` - ``DEALER`` - subscriber to the ``process`` socket of the examiner, receives commands
  to present stimuli, etc.
"""