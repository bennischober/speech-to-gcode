import io
import os
import queue
import threading
from utils.config import STT_ENDPOINT
import utils.logger as logger
import sounddevice as sd
import soundfile as sf
import tempfile
import requests



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

        data, _ = sf.read(io.BytesIO(b"".join(list(self.input_queue.queue))), dtype=self.format,
                          samplerate=self.rate, channels=self.channels, format="RAW", subtype='PCM_16')

        # Write audio data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            sf.write(tmp_file.name, data, self.rate)

            self.log.info(
                "Wrote audio data to temporary file {}".format(tmp_file.name))

            with open(tmp_file.name, "rb") as f:
                response = requests.post(STT_ENDPOINT, files={"file": f})
                self.log.info("Response: {}".format(response.text))

        # cleanup temporary file
        tmp_file.close()
        os.remove(tmp_file.name)
        self.log.info("Closed temporary file {}".format(tmp_file.name))

        return response.text

recorder = Recorder()
