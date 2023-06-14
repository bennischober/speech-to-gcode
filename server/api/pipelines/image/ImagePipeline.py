import os
import gc
import time
from urllib.request import urlretrieve
import torch
import torch.nn as nn
import open_clip
from diffusers import StableDiffusionPipeline
from pipelines.image.stable_diffusion import generate_image
from pipelines.image.laion_prediction import predict_score
from lib.logger import get_logger


class ImagePipeline:
    def __init__(self, cache_dir: str, sd_model_name: str = "runwayml/stable-diffusion-v1-5", sd_model_revision: str = "fp16", sd_model_torch_dtype: torch.dtype = torch.float16, clip_model_name: str = "ViT-L-14", clip_pretrained_name: str = "openai", aesthetic_clip_model_name: str = "vit_l_14"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.cache_dir = cache_dir
        self.logger = get_logger(__name__)
        # settings for models
        self.sd_model_name = sd_model_name
        self.aesthetic_clip_model_name = aesthetic_clip_model_name
        self.clip_model_name = clip_model_name
        self.clip_pretrained_name = clip_pretrained_name
        self.sd_model_revision = sd_model_revision
        self.sd_model_torch_dtype = sd_model_torch_dtype
        self.loading_state = "unloaded"
        self.logger.info("Image Pipeline initialized.")

    def load(self):
        # check, if models are already loaded on gpu/cpu
        if self.is_loaded() == "cuda":
            self.logger.info(f"Image Models are already loaded on GPU.")
            return
        elif self.is_loaded() == "cpu":
            self.logger.info(f"Image Models are loaded on CPU. Moving to GPU...")
            self.to_gpu()
            return
        
        self.logger.info(f"Loading state: {self.loading_state}. Device: {self.device}")

        start_time = time.time()
        self.pipe = StableDiffusionPipeline.from_pretrained(self.sd_model_name, revision=self.sd_model_revision,torch_dtype=self.sd_model_torch_dtype, cache_dir=self.cache_dir)
        self.pipe = self.pipe.to(self.device)
        end_time = time.time()
        self.logger.info(f"Time taken to load Stable Diffusion model: {end_time - start_time} seconds")

        start_time = time.time()
        self.predict_model = self._get_aesthetic_model(clip_model=self.aesthetic_clip_model_name)
        self.predict_model.eval()
        self.feature_model, _, self.feature_preprocess = open_clip.create_model_and_transforms(self.clip_model_name, pretrained=self.clip_pretrained_name, device=self.device, cache_dir=self.cache_dir)
        end_time = time.time()
        self.logger.info(f"Time taken to load Predictor models: {end_time - start_time} seconds")

        # set the loading state of the models
        self.loading_state = self.device
    
    def _get_aesthetic_model(self, clip_model="vit_l_14"):
        path_to_model = os.path.join(self.cache_dir, "sa_0_4_"+clip_model+"_linear.pth")
        if not os.path.exists(path_to_model):
            os.makedirs(self.cache_dir, exist_ok=True)
            url_model = ("https://github.com/LAION-AI/aesthetic-predictor/blob/main/sa_0_4_"+clip_model+"_linear.pth?raw=true")
            urlretrieve(url_model, path_to_model)
        if clip_model == "vit_l_14":
            m = nn.Linear(768, 1)
        elif clip_model == "vit_b_32":
            m = nn.Linear(512, 1)
        else:
            raise ValueError()
        s = torch.load(path_to_model)
        m.load_state_dict(s)
        m.eval()
        m = m.to(self.device)
        return m

    def generate_images(self, prompt: str, negative_prompt: str, amount: int = 2, width: int = 512, height: int = 512, num_inference_steps: int = 15, guidance_scale: int = 9, num_images_per_prompt: int = 5):
        # since we only have 24GB of VRAM, and the other the text pipeline needs about 6GB in idle, while this one needs around 10, we need to clear the VRAM before generating the image. Also, we are only able to create a smaller batch of images, since we are running out of memory otherwise. Thats why generate_images is called twice to generate 10 images.

        # models could be unloaded, load them again
        if self.pipe is None or self.predict_model is None or self.feature_model is None:
            # load models
            self.logger.info(f"Loading Image models...")
            self.load()

        # check, if models are at the right device
        if self.pipe.device.type != self.device:
            self.logger.info(f"Image Models are not at the right device. Moving models to {self.device}...")
            self.to_gpu()


        all_images = generate_image(self.pipe, prompt, negative_prompt, width=width,
                                    height=height, num_inference_steps=num_inference_steps, guidance_scale=guidance_scale, num_images_per_prompt=10)

        if all_images is None or len(all_images) == 0:
            return None

        self.logger.info(f"{len(all_images)} images generated successfully!")

        # gets top 4 images
        sorte_img = sorted(
            all_images, key=lambda x: predict_score(image=x, feature_model=self.feature_model, predict_model=self.predict_model, feature_preprocess=self.feature_preprocess), reverse=True)

        # get top 4 images
        images = sorte_img[:4]
        return images

    def unload_models(self, strategy: str = 'cpu'):
        if strategy == 'complete':
            del self.pipe
            del self.predict_model
            del self.feature_model

            # set the loading state of the models
            self.loading_state = "unloaded"
            torch.cuda.empty_cache()
        elif strategy == 'cpu':
            self.to_cpu()
            torch.cuda.empty_cache()
            gc.collect()
        else:
            raise ValueError("Strategy must be 'complete' or 'cpu'")
        self.logger.info(f"Image Models unloaded with {strategy} strategy.")

    def to_cpu(self):
        start_time = time.time()
        self.pipe = self.pipe.to("cpu")
        self.predict_model = self.predict_model.cpu()
        self.feature_model = self.feature_model.cpu()
        end_time = time.time()
        self.logger.info(f"Image Models moved to CPU. Time taken: {end_time - start_time} seconds.")

        # set the loading state of the models
        self.loading_state = "cpu"
    
    def to_gpu(self):
        start_time = time.time()
        self.pipe = self.pipe.to(self.device)
        self.predict_model = self.predict_model.cuda()
        self.feature_model = self.feature_model.cuda()
        end_time = time.time()
        self.logger.info(f"Image Models moved to GPU. Time taken: {end_time - start_time} seconds.")

        # set the loading state of the models
        self.loading_state = "cuda"
    
    # returns the state wether the models are loaded (on gpu or cpu) or not
    def is_loaded(self):
        """
        Returns, if the model is loaded. Either returns 'cpu', 'gpu' or 'unloaded'.
        """
        return self.loading_state
