from logging import Logger
from transformers import T5Tokenizer, T5ForConditionalGeneration

# reference:
# https://ai.googleblog.com/2020/02/exploring-transfer-learning-with-t5.html
# https://huggingface.co/t5-11b
# https://arxiv.org/pdf/1910.10683.pdf

# recommended: https://github.com/google-research/t5x

tokenizer = T5Tokenizer.from_pretrained('t5-11b')
model = T5ForConditionalGeneration.from_pretrained('t5-11b', return_dict=True)

def translate(text: str, logger: Logger = None) -> str | None:
    """Using Googles T5 model to translate text to English"""
    try:
        input_ids = tokenizer("translate to English: "+ text, return_tensors="pt").input_ids
        outputs = model.generate(input_ids)
        result: str = tokenizer.decode(outputs[0], skip_special_tokens=True)

        if logger:
            logger.info("Text translated successfully! Result: %s", result)

        return result
    
    except Exception as e:
        if logger:
            logger.error("Error translating text: %s", e)
        else:
            print(f"Error translating text: {e}")

        return None