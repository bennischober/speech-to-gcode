from logging import Logger
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import numpy as np

# Load Speech to Text model
# reference: https://huggingface.co/openai/whisper-large#english-to-english
stt_model_id = "openai/whisper-large-v2"
whisper_processor = WhisperProcessor.from_pretrained(stt_model_id)
whisper_model = WhisperForConditionalGeneration.from_pretrained(stt_model_id).to("cuda")

def transcribe(file, logger: Logger = None) -> str | None:
    try:
        data = np.frombuffer(file.read(), dtype=np.int16)

        inputs = whisper_processor.feature_extractor(data,  return_tensors="pt", sampling_rate=16_000).input_features.to("cuda")
        predicted_ids = whisper_model.generate(inputs, max_length=480_000)
        generated_text = whisper_processor.batch_decode(predicted_ids, skip_special_tokens=True, normalize=True)[0]

        if logger:
            logger.info(f"Text generated: {generated_text}")

        return generated_text
    
    except Exception as e:
        if logger:
            logger.error(f"Error generating text: {e}")
        else:
            print(f"Error generating text: {e}")

        return None
