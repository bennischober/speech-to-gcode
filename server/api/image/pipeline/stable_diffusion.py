from diffusers import StableDiffusionPipeline
import torch
from logging import Logger

device = "cuda" if torch.cuda.is_available() else "cpu"

model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, revision="fp16",torch_dtype=torch.float16)
pipe = pipe.to(device)

def generate_image(prompt: str,
                   negative_prompt: str,
                   width: int = 512,
                   height: int = 512,
                   num_inference_steps: int = 15,
                   guidance_scale: int = 9,
                   num_images_per_prompt: int = 5,
                   logger: Logger = None):
    if logger:
        logger.info("Calling generate_image")

    try:
        result = pipe(
            prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            num_images_per_prompt=num_images_per_prompt)
        
        images = result.images
        del result  # delete large variables as soon as possible
        torch.cuda.empty_cache()  # clear GPU memory

        if logger:
            logger.info(f"{len(images)} Image generated successfully!")

        return images
    
    except Exception as e:
        if logger:
            logger.error("Error generating image: %s", e)
        else:
            print(f"Error generating image: {e}")

        return None
