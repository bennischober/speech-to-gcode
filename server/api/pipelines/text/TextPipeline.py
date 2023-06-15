import gc
import time
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import soundfile as sf
import librosa
from lib.logger import get_logger


class TextPipeline:
    def __init__(self, cache_dir: str, model_id: str = "openai/whisper-large-v2", sampling_rate: int = 16000, max_length: int =480000, return_tensors: str ="pt", skip_special_tokens: bool = True, normalize: bool = True):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.cache_dir = cache_dir
        self.logger = get_logger(__name__, "text_pipeline.log")
        # settings for models
        self.model_id = model_id
        self.sampling_rate = sampling_rate
        self.max_length = max_length
        self.return_tensors = return_tensors
        self.skip_special_tokens = skip_special_tokens
        self.normalize = normalize

        # set the loading state of the models
        self.loading_state = "unloaded"

    def load(self):
        # check, if models are already loaded on gpu/cpu
        if self.is_loaded() == "cuda":
            self.logger.info(f"Models are already loaded on GPU.")
            return
        elif self.is_loaded() == "cpu":
            self.logger.info(f"Models are loaded on CPU. Moving to GPU...")
            self.to_gpu()
            return

        self.logger.info(f"Loading state: {self.loading_state}. Device: {self.device}")

        start_time = time.time()

        # Load Speech to Text model
        # reference: https://huggingface.co/openai/whisper-large#english-to-english
        self.whisper_processor = WhisperProcessor.from_pretrained(self.model_id, cache_dir=self.cache_dir)
        self.whisper_model = WhisperForConditionalGeneration.from_pretrained(self.model_id, cache_dir=self.cache_dir).to("cuda")

        end_time = time.time()
        self.logger.info(f"Time taken to load Speech to Text model: {end_time - start_time} seconds")

        # set the loading state of the models
        self.loading_state = self.device

    def transcribe(self, file):
        if self.whisper_model is None or self.whisper_processor is None:
            # load models
            self.logger.info(f"Loading models...")
            self.load()
        
        # check, if models are at the right device
        if self.whisper_model.device.type != self.device:
            self.logger.info(f"Models are not at the right device. Moving models to {self.device}...")
            self.to_gpu()

        try:
            # audio file could have different sampling rate; resample to 16kHz
            audio, rate = sf.read(file.stream)
            if rate != 16000:
                audio = librosa.resample(audio, rate, 16000)
                self.logger.info("Audio resampled to 16kHz")

            inputs = self.whisper_processor.feature_extractor(audio, return_tensors=self.return_tensors, sampling_rate=self.sampling_rate).input_features.to(self.device)
            predicted_ids = self.whisper_model.generate(inputs, max_length=self.max_length)
            generated_text = self.whisper_processor.batch_decode(predicted_ids, skip_special_tokens=self.skip_special_tokens, normalize=self.normalize)[0]

            self.logger.info("Text generated: %s", generated_text)
            
            # Clear VRAM
            torch.cuda.empty_cache()

            return generated_text
        
        except Exception as e:
            self.logger.error("Error generating text: %s", e)

            return None
    
    def unload_models(self, strategy: str = 'cpu'):
        if strategy == 'complete':
            del self.whisper_model
            self.loading_state = "unloaded"
            torch.cuda.empty_cache()
        elif strategy == 'cpu':
            self.to_cpu()
            torch.cuda.empty_cache()
            gc.collect()
        else:
            raise ValueError("Strategy must be 'complete' or 'cpu'")
        self.logger.info(f"Models unloaded with {strategy} strategy.")

    def to_cpu(self):
        start_time = time.time()
        self.whisper_model = self.whisper_model.cpu()
        end_time = time.time()
        self.logger.info(f"Models moved to CPU. Time taken: {end_time - start_time} seconds.")

        # set the loading state of the models
        self.loading_state = "cpu"
    
    def to_gpu(self):
        start_time = time.time()
        self.whisper_model = self.whisper_model.cuda()
        end_time = time.time()
        self.logger.info(f"Models moved to GPU. Time taken: {end_time - start_time} seconds.")

        # set the loading state of the models
        self.loading_state = "cuda"

    def is_loaded(self):
        """
        Returns, if the model is loaded. Either returns 'cpu', 'gpu' or 'unloaded'.
        """
        return self.loading_state
