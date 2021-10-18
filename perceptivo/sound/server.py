"""
Wrapper around autopilot's :class:`~autopilot.stim.sound.jackclient.JackClient`

* boot and kill the jackd daemon
* references to jackclient module
"""
import subprocess
import os
import typing
import signal
import atexit
from time import sleep

from autopilot import prefs
prefs.set('AUDIOSERVER', 'jack')
from autopilot.stim.sound import jackclient
from perceptivo.data.types import Jackd_Config

_jackd_proc: typing.Optional[subprocess.Popen] = None

def boot_jackd(config: Jackd_Config) -> subprocess.Popen:
    """
    Boot the jacked server given the configuration given by :class:`.types.Jackd_Config`

    Launches with ``shell = True`` and ``preexec_fn=os.setsid`` so that the process can be killed later.

    Registers the jackd sound server to be killed at exit.

    Thanks to https://stackoverflow.com/a/4791612/13113166 for information about how to kill a process with ``shell = True``

    Returns:
        :class:`subprocess.Popen` - opened subprocess
    """
    global _jackd_proc

    proc = subprocess.Popen(config.launch_str, stdout=subprocess.PIPE, shell=True,
                            preexec_fn=os.setsid)
    _jackd_proc = proc

    # register the process to be killed at exit
    atexit.register(lambda: kill_jackd(proc))

    # sleep to let the process start
    sleep(3)

    return proc


def kill_jackd(proc: typing.Optional[subprocess.Popen] = None):
    if proc is None:
        proc = globals()['_jackd_proc']

        # if proc is still None after getting from globals, then we haven't booted.
        if proc is None:
            raise RuntimeError(f'jackd was not booted, cant kill the process without first booting it!')

    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)