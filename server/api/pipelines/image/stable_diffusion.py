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
    """Generates an image using the StableDiffusionPipeline. Uses the given prompt and negative prompt.

    Args:
        pipe (StableDiffusionPipeline): The pipeline to use for generating the image.
        prompt (str): The prompt to use for generating the image.
        negative_prompt (str): The negative prompt to use for generating the image.
        width (int, optional): The with of the generated image. Defaults to 512.
        height (int, optional): The height of the generated image. Defaults to 512.
        num_inference_steps (int, optional): The number of inference steps to use for generating the image. Defaults to 15.
        guidance_scale (int, optional): The guidance scale to use for generating the image. Defaults to 9.
        num_images_per_prompt (int, optional): The number of images to generate per prompt. Defaults to 5.

    Returns:
        (Any | List | ndarray | None): The generated image or None, if an error occurred.
    """
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

        return images
    
    except Exception as e:
        logger.error("Error generating image: %s", e)

        return None
