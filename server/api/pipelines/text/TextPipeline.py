import os
import gc
import time
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
import soundfile as sf
import librosa
from lib.logger import get_logger


class TextPipeline:
    def __init__(
            self,
            cache_dir: str,
            model_id: str = "openai/whisper-large-v2",
            translate_model_id: str = "Helsinki-NLP/opus-mt-de-en",
            sampling_rate: int = 16000,
            max_length: int = 480000,
            return_tensors: str = "pt",
            skip_special_tokens: bool = True,
            normalize: bool = True,
            max_new_tokens: int = 40,
            do_sample: bool = True,
            top_k: int = 30,
            top_p: float = 0.95
    ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.cache_dir = cache_dir
        self.logger = get_logger(__name__, "text_pipeline.log")
        # settings for whisper model
        self.model_id = model_id
        self.sampling_rate = sampling_rate
        self.max_length = max_length
        self.return_tensors = return_tensors
        self.skip_special_tokens = skip_special_tokens
        self.normalize = normalize
        # settings for translation model
        self.translate_model_id = translate_model_id
        self.max_new_tokens = max_new_tokens
        self.do_sample = do_sample
        self.top_k = top_k
        self.top_p = top_p

        # download nltk model
        nltk.download('universal_tagset', download_dir=os.path.join(cache_dir, "nltk_data"))
        nltk.download('punkt', download_dir=os.path.join(cache_dir, "nltk_data"))
        nltk.download('averaged_perceptron_tagger', download_dir=os.path.join(cache_dir, "nltk_data"))

        # set the loading state of the models
        self.loading_state = "unloaded"
        self.logger.info("Text Pipeline initialized.")

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

        # Load SpeechToText model
        # reference: https://huggingface.co/openai/whisper-large#english-to-english
        self.whisper_processor = WhisperProcessor.from_pretrained(self.model_id, cache_dir=self.cache_dir)
        self.whisper_model = WhisperForConditionalGeneration.from_pretrained(self.model_id, cache_dir=self.cache_dir).to(self.device)

        end_time = time.time()
        self.logger.info(f"Time taken to load SpeechToText model: {end_time - start_time} seconds")

        # Load Translation model
        start_time = time.time()

        # reference: https://huggingface.co/Helsinki-NLP/opus-mt-de-en
        self.translate_model = AutoModelForSeq2SeqLM.from_pretrained(self.translate_model_id, cache_dir=self.cache_dir).to(self.device)
        self.translate_tokenizer = AutoTokenizer.from_pretrained(self.translate_model_id, cache_dir=self.cache_dir)

        end_time = time.time()
        self.logger.info(f"Time taken to load Translation model: {end_time - start_time} seconds")

        # set the loading state of the models
        self.loading_state = self.device

    def transcribe(self, file):
        start_time = time.time()

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

            end_time = time.time()
            self.logger.info(f"Time taken to generate/transcribe text: {end_time - start_time} seconds")

            # translate text
            translated_text = self.translate(generated_text)

            return translated_text
        
        except Exception as e:
            self.logger.error("Error generating text: %s", e)

            return None
    
    def translate(self, text):
        start_time = time.time()

        if self.translate_model is None or self.translate_tokenizer is None:
            # load models
            self.logger.info(f"Loading models...")
            self.load()
        
        # check, if models are at the right device
        if self.translate_model.device.type != self.device:
            self.logger.info(f"Models are not at the right device. Moving models to {self.device}...")
            self.to_gpu()

        try:
            # translate text
            inputs = self.translate_tokenizer(text, return_tensors=self.return_tensors).input_ids.to(self.device)

            outputs = self.translate_model.generate(inputs, max_new_tokens=self.max_new_tokens, do_sample=self.do_sample, top_k=self.top_k, top_p=self.top_p)

            translated_text = self.translate_tokenizer.decode(outputs[0], skip_special_tokens=self.skip_special_tokens, clean_up_tokenization_spaces=True)


            self.logger.info("Text translated: %s", translated_text)
            
            # Clear VRAM
            torch.cuda.empty_cache()

            end_time = time.time()

            self.logger.info(f"Time taken to translate text: {end_time - start_time} seconds")

            # get keywords
            keywords = self.extract_nouns(translated_text)

            return translated_text, keywords
        
        except Exception as e:
            self.logger.error("Error translating text: %s", e)

            return None
        
    def extract_nouns(self, text: str):
        nouns = []
        words = nltk.word_tokenize(text)
        tagged_words = nltk.pos_tag(words, tagset='universal')

        for word, tag in tagged_words:
            if tag == 'NOUN' and word.lower() not in {'a', 'an', 'the'}:
                nouns.append(word)

        text_prompt = ""

        for noun in nouns: 
            text_prompt += noun + " . "

        return text_prompt
    
    def unload_models(self, strategy: str = 'cpu'):
        if strategy == 'complete':
            del self.whisper_model
            del self.translate_model
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
        self.translate_model = self.translate_model.to("cpu")
        end_time = time.time()
        self.logger.info(f"Models moved to CPU. Time taken: {end_time - start_time} seconds.")

        # set the loading state of the models
        self.loading_state = "cpu"
    
    def to_gpu(self):
        start_time = time.time()
        self.whisper_model = self.whisper_model.cuda()
        self.translate_model = self.translate_model.to("cuda")
        end_time = time.time()
        self.logger.info(f"Models moved to GPU. Time taken: {end_time - start_time} seconds.")

        # set the loading state of the models
        self.loading_state = "cuda"

    def is_loaded(self):
        """
        Returns, if the model is loaded. Either returns 'cpu', 'gpu' or 'unloaded'.
        """
        return self.loading_state
