import os
import queue
import threading
from utils.config import STT_ENDPOINT
import utils.logger as logger
import sounddevice as sd
import soundfile as sf
import requests
import numpy as np
import librosa


class Recorder:
    def __init__(self, channels=1, format="int16"):
        self.device_info = sd.query_devices(sd.default.device[0], 'input')
        self.rate = int(self.device_info['default_samplerate'])
        self.channels = channels
        self.format = format
        self.input_queue = queue.Queue()
        self.recording = False
        self.log = logger.get_logger(__name__)

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
                pass

    def stop_recording(self):
        if self.recording:
            self.recording = False
            sd.stop()
            self.log.info("Stopped recording")

        for th in threading.enumerate():
            if th.is_alive() and th.name == "start_recording":
                self.log.info(
                    "Found thread that is alive: {}. Trying to join.".format(th.name))
                try:
                    th.join()
                except Exception as e:
                    self.log.error(
                        "Error while joining thread {}: {}".format(th.name, e))

        self.log.info("All threads stopped")

        raw_audio = np.frombuffer(b"".join(list(self.input_queue.queue)), dtype=np.int16)
        converted_audio = raw_audio.astype(np.float32)
        audio = librosa.resample(converted_audio, orig_sr=self.rate, target_sr=16000)

        file_path = os.path.join(os.path.dirname(__file__), "audio.wav")

        sf.write(file_path, audio, 16000, subtype='PCM_16')

        # clear the queue
        self.input_queue.queue.clear()

        # make request
        with open(file_path, "rb") as f:
            self.log.info("Sending audio data to STT endpoint: %s", STT_ENDPOINT)
            response = requests.post(STT_ENDPOINT, files={"audio": f})
            self.log.info("Response: {}".format(response.text))

        return response.text

recorder = Recorder()
