"""
entrypoint for patient interface
"""

from perceptivo.root import Runtime
from perceptivo import sound

from perceptivo.types.sound import Jackd_Config


class Patient(Runtime):
    """
    Runtime agent for the patient-facing Pi (see :ref:`SoftwareOverview`)

    Runs the

    * Session Manager -- controls the logic of the exam
    * Sound Server
    * PiCamera
    * Processing stages including pupil extraction, psychoacoustic model, and stimulus manager
    """

    def __init__(self, jackd_config: Jackd_Config = Jackd_Config()):
        super(Patient, self).__init__()
        self.jackd_config = jackd_config

        self.server = self._init_audio() # type: sound.server.jackclient.JackClient

    def _init_audio(self) -> sound.server.jackclient.JackClient:
        """
        Start the jackd process, connect a client to it!

        Returns:
            :class:`autopilot.stim.sound.jackclient.JackClient` - A booted jack client!
        """
        proc = sound.server.boot_jackd(self.jackd_config)
        self.procs.append(proc)
        client = sound.server.jackclient.JackClient()
        client.start()
        self.logger.info(f'Started jackd with pid: {proc.pid}, and also started jack client!')
        return client





def main():
    print('hey what up')