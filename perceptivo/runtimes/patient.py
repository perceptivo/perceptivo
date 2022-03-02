"""
entrypoint for patient interface
"""
import sys
import typing
from typing import Optional
from time import sleep
from pathlib import Path
import threading
from datetime import datetime, timedelta
from queue import Empty

import soundcard as sc

from perceptivo.prefs import Patient_Prefs
from perceptivo import Directories
from perceptivo.runtimes.runtime import Runtime
from perceptivo.sound import server
from perceptivo.video.cameras import Picamera_Process
from perceptivo.video.pupil import Pupil_Extractors, EllipseExtractor_Params, get_extractor
from perceptivo.psychophys import model
from perceptivo.networking.node import Node
from perceptivo.networking.messages import Message

from perceptivo.types.sound import Jackd_Config, Audio_Config, Sound
from perceptivo.types.psychophys import Sample, Samples, Psychoacoustic_Model, Kernel
from perceptivo.types.video import Picamera_Params, Frame
from perceptivo.types.pupil import Pupil, Pupil_Params, Dilation
from perceptivo.types.patient import Collection_Params
from perceptivo.types.networking import Patient_Networking, Socket

from autopilot import prefs


class Patient(Runtime):
    """
    Runtime agent for the patient-facing Pi (see :ref:`SoftwareOverview`).

    Runs the

    * Sound Server
    * PiCamera
    * Processing stages including pupil extraction, psychoacoustic model, and stimulus manager

    On intialization, boot the sound server and rehydrate the psychoacoustic model from
    the parameterization passed in ``audiogram_model``. The patient runtime is parameterized
    by the :class:`perceptivo.prefs.Patient_Prefs` object, which creates and reads from
    a ``prefs.json`` file (located at :attr:`perceptivo.prefs.Directories.prefs_file` ).

    The basic operation of the Patient runtime is encapsulated in the :meth:`.trial` method,
    see that for further documentation.


    Args:
        audio_config (:class:`~.types.sound.Jackd_Config`): Configuration used to boot the jackd server
        audiogram_model (:class:`~.types.psychophys.Psychoacoustic_Model`): Model parameterization used to
            model the audiogram as well as generate optimal stimuli to sample
        oracle (callable): Optional, if present use an oracle to generate responses to stimuli rather than
            getting them from the pupil extraction method. Mostly for testing, takes a function
            that accepts a :class:`~.types.sound.Sound` object and returns a boolean response,
            typically generated by functions in :mod:`~.psychophys.oracle` like :func:`~.psychophys.oracle.reference_audiogram`
    """
    prefs_class = Patient_Prefs

    def __init__(self,
                 audio_config: Audio_Config = Audio_Config(),
                 audiogram_model: Optional[Psychoacoustic_Model] = None,
                 picamera_params: Optional[Picamera_Params] = None,
                 oracle: typing.Optional[callable]=None,
                 pupil_extractor: typing.Optional[Pupil_Extractors] = None,
                 pupil_extractor_params: typing.Optional[EllipseExtractor_Params] = None,
                 collection_params: typing.Optional[Collection_Params] = None,
                 networking: typing.Optional[Patient_Networking] = None,
                 prefs_file: Path = Directories.prefs_file,
                 **kwargs):

        self.prefs_file = prefs_file
        self.prefs = self.load_prefs(self.prefs_file) # type: Patient_Prefs

        super(Patient, self).__init__(**kwargs)


        if audio_config is None:
            self.audio_config = self.prefs.Audio_Config
        else:
            self.audio_config = audio_config

        if audiogram_model is None:
            self.audiogram_model = self.prefs.Audiogram_Model
        else:
            self.audiogram_model = audiogram_model

        if picamera_params is None:
            self.picamera_params = self.prefs.Picamera_Params
        else:
            self.picamera_params = picamera_params

        if pupil_extractor is None:
            self.pupil_extractor = self.prefs.pupil_extractor
        else:
            self.pupil_extractor = pupil_extractor

        if pupil_extractor_params is None:
            self.pupil_extractor_params = self.prefs.pupil_extractor_params
        else:
            self.pupil_extractor_params = pupil_extractor_params

        if collection_params is None:
            self.collection_params = self.prefs.collection_params
        else:
            self.collection_params = collection_params

        if networking is None:
            self.networking_prefs = self.prefs.networking
        else:
            self.networking_prefs = networking

        self.oracle = oracle

        # --------------------------------------------------
        # Private Attrs
        # --------------------------------------------------
        self._collecting = threading.Event()
        """Event that is set while the picam is collecting frames & they are being processed"""
        self._collecting_thread = None # type: typing.Optional[threading.Thread]
        self._frames = [] # type: typing.List[Frame]
        """Frames for the current sample"""
        self._pupils = [] # type: typing.List[Pupil]
        """Pupils for the current sample!"""
        self._trial_active = threading.Event()
        """Event that's set while a trial is running!"""

        # --------------------------------------------------
        # Networking callbacks
        # --------------------------------------------------
        self.callbacks = {
            ''
        }


        # --------------------------------------------------
        # Init Hardware/resources
        # --------------------------------------------------

        self.samples = Samples() # type: Samples

        self.server = self._init_audio() # type: typing.Union[server.jackclient.JackClient, sc.pulseaudio._Speaker]
        self.model = self._init_model(self.audiogram_model) # type: model.Audiogram_Model
        self.picam = self._init_picam(self.picamera_params, self.networking_prefs.eyecam)
        self.pupil_extractor = self._init_pupil_extractor(self.pupil_extractor, self.pupil_extractor_params)
        self.node = self._init_networking(self.prefs.networking.control)
        self.picam.start()
        self.quitting = threading.Event()
        self.quitting.clear()




    def trial(self):
        """
        One complete loop through a probe cycle. In order:

        * check if a previous trial is still running using the :attr:`._trial_active` event,
          if so, return, logging an exception
        * clear the lists that collect pupil samples: :attr:`._frames` and :attr:`._pupils`
        * :meth:`.next_sound` to parameterize the next sound, returning a :class:`.types.sound.Sound` object, based on the
          output of the :meth:`.Audiogram_Model.next` method
        * :meth:`.probe` to deliver the sound and collect the response. Within the probe method:

            * the :attr:`.Picamera_Process.collecting` flag is set to indicate that it should dump frames into its queue
            * the sound is played with :meth:`.play_sound`
            * the :meth:`.await_response` method spawns a :attr:`._collecting_thread`, which calls
              :meth:`._collect_frames` to pull frames from :attr:`.Picamera_Process.q` and process them with
              :attr:`.pupil_extractor` until the queue is empty. :class:`.types.video.Frame` s and
              :class:`.types.pupil.Pupil` s are appended to the :attr:`._frames` and :attr:`._pupils` collectors
            * once the thread finishes, the picamera's collection event is cleared, and the :class:`.types.pupil.Pupil_Params`, which set the threshold of dilation that
              constitutes a positive response to the sound is updated with :meth:`._update_pupil_params`
            * The :class:`~.types.pupil.Pupil_Params`, :class:`~.types.sound.Sound`, and list of
              :class:`~.types.pupil.Pupil` objects are collected into a :class:`~.types.pupil.Dilation` object and returned

        * the :meth:`.probe` method then combines the :class:`~.types.sound.Sound` and :class:`~.types.pupil.Dilation` objects into
          a :class:`~.types.psychophys.Sample` object, which is then appended to the :attr:`.samples` attr
        * Finally, the :attr:`.model` is updated with the :meth:`.update_model`

        Stores the :class:`~.types.psychophys.Samples` in :attr:`.samples`, which also
        include the parameterizations and timestamps of the presented sounds

        """
        if self._trial_active.is_set():
            self.logger.exception('Previous trial still running')
            return

        self.logger.debug('-------------------')
        self.logger.debug('new trial started')

        # clear trialwise collectors
        self._frames = []
        self._pupils = []

        self._trial_active.set()

        sound = self.next_sound()
        self.logger.debug('got next sound')

        sample = self.probe(sound)
        self.logger.debug('probed')

        if sample is not None:
            self.samples.append(sample)
            self.model.update(sample)
            self.logger.debug(f'Sample collected - {sample}')

        self._trial_active.clear()

    def next_sound(self) -> Sound:
        """
        Generate the next sound using the psychoacoustic :attr:`.model`

        Returns:
            :class:`~.types.sound.Sound` to play
        """
        sound = self.model.next()
        if isinstance(self.audio_config, Jackd_Config):
            sound.jack_client = self.server
        self.logger.debug(f'got next sound {sound}')
        return sound

    def probe(self, sound:Sound) -> typing.Union[Sample, None]:
        """
        One loop of

        * Presenting a sound stimulus
        * Signaling to the other Pi to present a visual stimulus
        * Estimating the Pupil Response

        Returns
            :class:`perceptivo.types.psychophys.Sample`
        """
        # start the picam capturing
        self.picam.collecting.set()
        self.logger.debug('Picamera started collecting')

        sound = self.play_sound(sound)
        self.logger.debug(f'played sound {sound}, awaiting response')
        dilation = self.await_response(sound)
        if dilation is None:
            return None
        else:
            self.logger.debug(f'got dilation {dilation} for sound {sound}')
            return Sample(dilation=dilation, sound=sound)

    def play_sound(self, sound: Sound) -> Sound:
        """
        Play a parameterized sound

        Args:
            sound ():

        Returns:
            :class:`~.types.sound.Sound`
        """
        # hydrate the sound, clean the kwargs
        sound_kwargs = sound.sound_kwargs
        # autopilot uses ms not seconds
        if sound_kwargs['duration'] < 25:
            sound_kwargs['duration'] *= 1000
        if not isinstance(self.audio_config, Jackd_Config):
            del sound_kwargs['jack_client']
            sound_kwargs['fs'] = self.audio_config.fs

        # instantiate sound from autopilot Gammatone class
        _sound = sound.sound_class(**sound_kwargs)

        # stamp time and play sound depending on method implied by audio_config
        sound.stamp_time()
        if isinstance(self.audio_config, Jackd_Config):
            _sound.play()
        else:
            self.server.play(_sound.table, samplerate=self.audio_config.fs)
        return sound

    def await_response(self, sound:Sound) -> typing.Union[Dilation, None]:
        """
        Wait until we are given a pupil from the picamera process

        Returns:
            bool
        """
        if self.oracle is not None:
            return self.oracle(sound)
        else:
            self._collecting.clear()
            self._collecting_thread = threading.Thread(
                target = self._collect_frames,
                args= (sound.timestamp,)
            )
            self._collecting_thread.start()
            self._collecting.wait()

            if len(self._pupils) == 0:
                self.logger.warning('No pupil detected! check collection parameters')
                return None

            # update the pupil_params from collected samples
            pupil_params = self._update_pupil_params(self._pupils)
            # collect pupils and frames into a Dilation
            dilation = Dilation(
                params=pupil_params,
                pupils = self._pupils.copy(),
                timestamps = [t.timestamp for t in self._frames]
            )
            return dilation


    def _collect_frames(self, start_time:datetime):
        """
        Collect frames from the picamera for one sample
        """
        self._pupils = []
        self._frame = []
        end_time = start_time + timedelta(seconds=self.collection_params.collection_wait)
        finished = False
        passed_wait_time = False
        try:
            while not finished:
                if datetime.now() > end_time:
                    passed_wait_time = True
                    self.picam.collecting.clear()

                # grab a frame
                try:
                    frame = self.picam.q.get_nowait()
                except Empty:
                    if passed_wait_time:
                        finished = True
                        break
                    else:
                        self.logger.debug('Queue was empty in collect_frames')
                        continue

                # process frame
                pupil = self.pupil_extractor.process(frame)
                if pupil is None:
                    self.logger.debug('No pupil detected')
                else:
                    self._frames.append(frame)
                    self._pupils.append(pupil)
                    self.logger.debug(f'processed {len(self._pupils)} frames')

        except Exception as e:
            self.logger.exception(f'Got exception processing frames, {e}')

        finally:
            self.logger.debug('Setting collection finished flag')
            self._collecting.set()


    def handle_message(self, message):
        """
        Handle a message by calling some method according to its ``key`` attribute

        Args:
            message (bytes): a serialized :class:`.networking.messages.Message` object
        """
        message = Message.from_serialized(message)




    def _update_pupil_params(self, pupils: typing.List[Pupil]) -> Pupil_Params:
        """

        .. todo::

            How to update pupil parameters?

        Args:
            pupils ():

        Returns:

        """
        params = Pupil_Params(threshold=10, max_diameter=20)
        return params


    def _init_audio(self) -> typing.Union[server.jackclient.JackClient, sc.pulseaudio._Speaker]:
        """
        Start the jackd process, connect a client to it!

        Returns:
            :class:`autopilot.stim.sound.jackclient.JackClient` - A booted jack client!
        """
        if isinstance(self.audio_config, Jackd_Config):
            self.logger.debug('Using jack audio server')
            proc = server.boot_jackd(self.audio_config)
            self.procs.append(proc)
            # prefs.set('OUTCHANNELS', [0])
            # sleep(1)
            client = server.jackclient.JackClient(outchannels=self.audio_config.outchannels)
            sleep(3)
            client.start()
            self.logger.info(f'Started jackd with pid: {proc.pid}, and also started jack client!')
        else:
            self.logger.debug('Using SoundCard-based audio system')
            prefs.set('AUDIOSERVER', 'dummy')
            client = sc.default_speaker()

        return client

    def _init_model(self, model_params: Psychoacoustic_Model) -> model.Audiogram_Model:
        # get model class
        model_class = getattr(model, model_params.model_type)
        return model_class(*model_params.args, **model_params.kwargs)

    def _init_picam(self, picam_params: Picamera_Params, networking:Socket) -> Picamera_Process:
        picam_proc = Picamera_Process(
            picam_params,
            networking,
            queue_size=self.prefs.picam_queue_size
        )
        return picam_proc

    def _init_pupil_extractor(
            self,
            pupil_extractor: Pupil_Extractors,
            pupil_extractor_params: typing.Union[EllipseExtractor_Params]):

        extractor = get_extractor(pupil_extractor)
        return extractor(**pupil_extractor_params.dict())

    def _init_networking(self, socket:Socket) -> Node:
        node = Node(
            socket,
            poll_mode=Node.Poll_Mode.IOLOOP,
            callback=self.handle_message
        )
        msg = Message(key='CONNECT', id=node.id)
        node.send(msg)


        return node




def main():
    try:
        patient = Patient()
        patient.quitting.wait()
    except KeyboardInterrupt:
        patient.quitting.set()
        sys.exit()