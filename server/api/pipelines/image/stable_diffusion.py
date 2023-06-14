from diffusers import StableDiffusionPipeline
import torch
from lib.logger import get_logger

# Create a logger for the module
logger = get_logger(__name__)

def generate_image(pipe: StableDiffusionPipeline,
                   prompt: str,
                   negative_prompt: str,
                   width: int = 512,
                   height: int = 512,
                   num_inference_steps: int = 15,
                   guidance_scale: int = 9,
                   num_images_per_prompt: int = 5):
    logger.info("Calling generate_image!")

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

        logger.info(f"{len(images)} Image generated successfully!")

        return images
    
    except Exception as e:
        logger.error("Error generating image: %s", e)

        return None
