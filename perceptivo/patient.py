"""
entrypoint for patient interface
"""
import typing
from time import sleep

from perceptivo.root import Runtime
from perceptivo.sound import server

from perceptivo.types.sound import Jackd_Config, Sound
from perceptivo.types.psychophys import Sample, Samples, Psychoacoustic_Model, Default_Kernel
from perceptivo.psychophys import model
from dataclasses import asdict


from autopilot import prefs


class Patient(Runtime):
    """
    Runtime agent for the patient-facing Pi (see :ref:`SoftwareOverview`)

    Runs the

    * Session Manager -- controls the logic of the exam
    * Sound Server
    * PiCamera
    * Processing stages including pupil extraction, psychoacoustic model, and stimulus manager

    On intialization, boot the sound server and rehydrate the psychoacoustic model from
    the parameterization passed in ``audiogram_model``

    Args:
        jackd_config (:class:`~.types.sound.Jackd_Config`): Configuration used to boot the jackd server
        audiogram_model (:class:`~.types.psychophys.Psychoacoustic_Model`): Model parameterization used to
            model the audiogram as well as generate optimal stimuli to sample
        oracle (callable): Optional, if present use an oracle to generate responses to stimuli rather than
            getting them from the pupil extraction method. Mostly for testing, takes a function
            that accepts a :class:`~.types.sound.Sound` object and returns a boolean response,
            typically generated by functions in :mod:`~.psychophys.oracle` like :func:`~.psychophys.oracle.reference_audiogram`
    """

    def __init__(self,
                 jackd_config: Jackd_Config = Jackd_Config(),
                 audiogram_model: Psychoacoustic_Model =
                   Psychoacoustic_Model(
                       'Gaussian_Process',
                       kwargs={'kernel': Default_Kernel()}),
                 oracle: typing.Optional[callable]=None):
        super(Patient, self).__init__()
        self.jackd_config = jackd_config
        self.audiogram_model = audiogram_model
        self.oracle = oracle

        self.samples = Samples() # type: Samples

        self.server = self._init_audio() # type: server.jackclient.JackClient
        self.model = self._init_model(self.audiogram_model) # type: model.Audiogram_Model

    def loop(self):
        """
        One complete loop through a probe cycle

        Calls:

        * :meth:`.next_sound` to parameterize the next sound
        * :meth:`.probe` to deliver the sound and collect the response
        * :meth:`.update_model` to update the psychoacoutic model for stimulus generation

        Stores the :class:`~.types.psychophys.Samples` in :attr:`.samples`, which also
        include the parameterizations and timestamps of the presented sounds

        """
        sound = self.next_sound()
        sample = self.probe(sound)
        self.samples.append(sample)
        self.model.update(sample)

        self.logger.debug(f'Sample collected - {sample}')

    def next_sound(self) -> Sound:
        """
        Generate the next sound using the psychoacoustic :attr:`.model`

        Returns:
            :class:`~.types.sound.Sound` to play
        """
        sound = self.model.next()
        self.logger.debug(f'got next sound {sound}')
        return sound

    def probe(self, sound:Sound) -> Sample:
        """
        One loop of

        * Presenting a sound stimulus
        * Signaling to the other Pi to present a visual stimulus
        * Estimating the Pupil Response

        Returns
            :class:`perceptivo.types.psychophys.Sample`
        """
        sound = self.play_sound(sound)
        self.logger.debug(f'played sound {sound}, awaiting response')
        response = self.await_response(sound)
        self.logger.debug(f'got response {response} for sound {sound}')
        return Sample(response=response, sound=sound)

    def play_sound(self, sound: Sound) -> Sound:
        """
        Play a parameterized sound

        Args:
            sound ():

        Returns:
            :class:`~.types.sound.Sound`
        """
        # hydrate the sound
        _sound = sound.sound_class(**sound.sound_kwargs)
        _sound.play()
        sound.stamp_time()
        return sound

    def await_response(self, sound:Sound) -> bool:
        """
        Wait until we are given a pupil from the picamera process

        Returns:
            bool
        """
        if self.oracle is not None:
            return self.oracle(sound)
        else:
            # TODO: implement picamera pupil extraction
            pass


    def _init_audio(self) -> server.jackclient.JackClient:
        """
        Start the jackd process, connect a client to it!

        Returns:
            :class:`autopilot.stim.sound.jackclient.JackClient` - A booted jack client!
        """
        proc = server.boot_jackd(self.jackd_config)
        self.procs.append(proc)
        # prefs.set('OUTCHANNELS', [0])
        # sleep(1)
        client = server.jackclient.JackClient()
        sleep(3)
        client.start()
        self.logger.info(f'Started jackd with pid: {proc.pid}, and also started jack client!')
        return client

    def _init_model(self, model_params: Psychoacoustic_Model) -> model.Audiogram_Model:
        # get model class
        model_class = getattr(model, model_params.model_type)
        return model_class(*model_params.args, jack_client=self.server, **model_params.kwargs)





def main():
    print('hey what up')