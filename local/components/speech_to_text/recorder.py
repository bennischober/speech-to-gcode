import json
import queue
import threading
from vosk import Model, KaldiRecognizer
import utils.logger as logger
import time
import sounddevice as sd


class Recorder:
    def __init__(self, model_name="vosk-model-de-0.21", channels=1, format="int16"):
        load_start = time.time()

        # -------
        self.device_info = sd.query_devices(sd.default.device[0], 'input')
        self.rate = int(self.device_info['default_samplerate'])
        self.model = Model(model_name=model_name)
        self.recognizer = KaldiRecognizer(self.model, self.rate)
        self.recognizer.SetWords(False)
        self.channels = channels
        self.format = format
        self.transcription_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.recording = False
        self.log = logger.get_logger(__name__)
        # -------

        load_end = time.time() - load_start
        self.log.info("vosk model loaded in {} seconds".format(load_end))

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.input_queue.put(bytes(indata))

    def start_recording(self):
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
                    result = json.loads(recognizer_result)
                    if not result.get("text", "") == "":
                        self.transcription_queue.put(result["text"])
                        self.log.info(result)

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.log.info("Stopped recording")

            for th in threading.enumerate():
                if th.is_alive() and th.name == "start_recording":
                    self.log.info(th.name)
                    th.join()
            
            self.log.info("All threads stopped")

recorder = Recorder()
