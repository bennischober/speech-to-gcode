import os
import uuid
import gc
import time
from urllib.request import urlretrieve
import torch
import torch.nn as nn
import open_clip
from diffusers import StableDiffusionPipeline
from pipelines.image.stable_diffusion import generate_image
from pipelines.image.laion_prediction import predict_score
from pipelines.image.ObjectDetectionPipeline import ObjectDetectionPipeline
from lib.logger import get_logger


class ImagePipeline:
    def __init__(
            self,
            cache_dir: str,
            sd_model_name: str = "runwayml/stable-diffusion-v1-5",
            clip_model_name: str = "ViT-L-14",
            clip_pretrained_name: str = "openai",
            aesthetic_clip_model_name: str = "vit_l_14",
            sd_model_revision: str = "fp16",
            sd_model_torch_dtype: torch.dtype = torch.float16
        ):
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

        # load Stable Diffusion model
        start_time = time.time()

        self.pipe = StableDiffusionPipeline.from_pretrained(self.sd_model_name, revision=self.sd_model_revision,torch_dtype=self.sd_model_torch_dtype, cache_dir=self.cache_dir)
        self.pipe = self.pipe.to(self.device)

        end_time = time.time()
        self.logger.info(f"Time taken to load Stable Diffusion model: {end_time - start_time} seconds")


        # load LAION model
        start_time = time.time()

        self.predict_model = self._get_aesthetic_model(clip_model=self.aesthetic_clip_model_name)
        self.predict_model.eval()
        self.feature_model, _, self.feature_preprocess = open_clip.create_model_and_transforms(self.clip_model_name, pretrained=self.clip_pretrained_name, device=self.device, cache_dir=self.cache_dir)

        end_time = time.time()
        self.logger.info(f"Time taken to load Predictor models: {end_time - start_time} seconds")


        # load Object Detection model
        start_time = time.time()

        self.object_detection = ObjectDetectionPipeline(self.cache_dir)
        self.object_detection.load()

        end_time = time.time()
        self.logger.info(f"Time taken to load Object Detection model: {end_time - start_time} seconds")

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

    def generate_images(
            self,
            prompt: str,
            negative_prompt: str,
            search_prompt: str,
            amount: int = 2,
            width: int = 512,
            height: int = 512,
            num_inference_steps: int = 15,
            guidance_scale: int = 9,
            num_images_per_prompt: int = 5
        ):
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

        image_scores = self._get_image_score(all_images, search_prompt)

        # Sort the image scores in descending order by 'result'
        sorted_image_scores = sorted(image_scores, key=lambda x: x['result'], reverse=True)

        # Get top 4 images based on the 'result' score
        top_images = [all_images[score['index']] for score in sorted_image_scores[:4]]
        
        return top_images

    def _get_image_score(self, all_images, search_prompt: str):
        """Creates a score for each image in the list of images.

        Args:
            all_images (List): All images generated by the Stable Diffusion model.
            search_prompt (str): The prompt to search for. Looks like this ```"chair . person . dog . "```

        Returns:
            dict: A dictionary with the scores for each image. Looks like this:

            ```
            {
                0: {
                    'laion': 7.01102,
                    'dino': 4.2,
                    'result': 11.21102
                }
            }
            ```
        """
        
        result = []

        image_dir = os.getenv('IMAGE_DIR')
        # generate uuid
        tmp_img_path = os.path.join(image_dir, str(uuid.uuid4()))
        # create tmp_img_path
        os.makedirs(tmp_img_path, exist_ok=True)

        for i, image in enumerate(all_images):
            # get the score from the laion model
            laion_score = predict_score(image=image, feature_model=self.feature_model, predict_model=self.predict_model, feature_preprocess=self.feature_preprocess)

            # get the score from the dino model
            dino_score, _, _ = self.object_detection.predict(image=image, prompt=search_prompt, index=i, img_path=tmp_img_path)

            self.logger.info(f"SCORING IMAGE {i}: PROMPTS: {search_prompt} LAION: {laion_score} - DINO: {dino_score}")

            # calculate the result score
            result_score = laion_score + dino_score

            # add the score to the image

            result.append({
                'laion': laion_score,
                'dino': dino_score,
                'result': result_score,
                'index': i
            })

        # write result as json file to tmp_img_path
        json_file = os.path.join(tmp_img_path, str(uuid.uuid4()) + ".json")
        with open(json_file, 'w') as f:
            f.write(str(result))
        
        return result


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
