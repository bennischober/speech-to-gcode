from diffusers import StableDiffusionPipeline
import torch
from logging import Logger

# Load Model and generate Pipeline
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

def generate_image(prompt: str,
                   negative_prompt: str,
                   width: int = 512,
                   height: int = 512,
                   num_inference_steps: int = 15,
                   guidance_scale: int = 9,
                   logger: Logger = None):
    """Generate images from a prompt"""
    try:
        result = pipe(
            prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            num_images_per_prompt=1)
        
        image = result.images[0]

        if logger:
            logger.info(f"Image generated successfully")

        return image
    
    except Exception as e:
        if logger:
            logger.error("Error generating image: %s", e)
        else:
            print(f"Error generating image: {e}")

        return None
