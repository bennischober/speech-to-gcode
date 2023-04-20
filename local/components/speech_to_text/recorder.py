import json
import queue
import threading
from vosk import Model, KaldiRecognizer
import utils.logger as logger
import time
import sounddevice as sd

class Recorder:
    def __init__(self, channels=1, format="int16"):
        self.device_info = sd.query_devices(sd.default.device[0], 'input')
        self.rate = int(self.device_info['default_samplerate'])
        self.model = None
        self.recognizer = None
        self.channels = channels
        self.format = format
        self.transcription_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.recording = False
        self.log = logger.get_logger(__name__)

    def load_model(self, model_name = "vosk-model-de-0.21"):
        load_start = time.time()
        self.log.info("Loading model")

        self.model = Model(model_name=model_name)
        self.recognizer = KaldiRecognizer(self.model, self.rate)
        self.recognizer.SetWords(False)

        load_end = time.time() - load_start
        self.log.info(
            "Vosk model loaded in {} seconds".format(round(load_end, 2)))

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.input_queue.put(bytes(indata))

    def start_recording(self):
        if self.model is None:
            self.log.warning("Note: model not loaded yet. Aborting recording")
            return

        self.log.info("Starting recording")
        self.recording = True

        with sd.RawInputStream(
            dtype=self.format,
            channels=self.channels,
            callback=self.callback
        ):
            while self.recording:
                data = self.input_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    recognizer_result = self.recognizer.Result()
                    result: dict[str, str] = json.loads(recognizer_result)
                    if not result.get("text", "") == "":
                        self.transcription_queue.put(result["text"])
                        self.log.info(result)

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.log.info("Stopped recording")

        for th in threading.enumerate():
            if th.is_alive() and th.name == "start_recording":
                self.log.info("Found thread that is alive: {}. Trying to join.".format(th.name))
                th.join()

        self.log.info("All threads stopped")

recorder = Recorder()
