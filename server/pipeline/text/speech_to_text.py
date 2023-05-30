from logging import Logger
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import numpy as np
import soundfile as sf
import librosa

# Load Speech to Text model
# reference: https://huggingface.co/openai/whisper-large#english-to-english
stt_model_id = "openai/whisper-large-v2"
whisper_processor = WhisperProcessor.from_pretrained(stt_model_id)
whisper_model = WhisperForConditionalGeneration.from_pretrained(stt_model_id).to("cuda")

def transcribe(file, logger: Logger = None):
    try:
        audio, rate = sf.read(file.stream)
        if rate != 16000:
            audio = librosa.resample(audio, rate, 16000)

        inputs = whisper_processor.feature_extractor(audio, return_tensors="pt", sampling_rate=16000).input_features.to("cuda")
        predicted_ids = whisper_model.generate(inputs, max_length=480000)
        generated_text = whisper_processor.batch_decode(predicted_ids, skip_special_tokens=True, normalize=True)[0]

        if logger:
            logger.info("Text generated: %s", generated_text)

        return generated_text
    
    except Exception as e:
        if logger:
            logger.error(f"Error generating text: {e}")
        else:
            print(f"Error generating text: {e}")

        return None
