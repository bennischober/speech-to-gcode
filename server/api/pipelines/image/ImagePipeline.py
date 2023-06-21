import os
import json
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
            sd_model_name: str = "stabilityai/stable-diffusion-2-1-base", # "runwayml/stable-diffusion-v1-5",
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

        # state of the models
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

        self.pipe = StableDiffusionPipeline.from_pretrained(self.sd_model_name, torch_dtype=self.sd_model_torch_dtype, cache_dir=self.cache_dir)
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
            width: int = 512,
            height: int = 512,
            num_inference_steps: int = 15,
            guidance_scale: int = 9,
            num_images_per_prompt: int = 5,
            amount_of_images: int = 4,
            max_iterations: int = 3,
            score_threshold: float = None,
            laion_score_threshold: float = None,
        ):
        """Generates images using the Stable Diffusion model and scores them using the LAION model and the GroundingDINO model.

        The iterative image generation works as follows:
        1. Generate images using the Stable Diffusion model.
        2. Score the images using the LAION model and the GroundingDINO model.
        3. Check, if the score of the top ``amount_of_images`` images is higher than the score threshold.
        4. If not, generate new images using the Stable Diffusion model and repeat from step 2.
        
        When ``max_iterations`` is reached, or the score threshold is reached, the process stops and returns the top ``amount_of_images`` images.


        Args:
            prompt (str): The prompt to use for generating the image.
            negative_prompt (str): The negative prompt to use for generating the image.
            search_prompt (str): The prompt to search for. Looks like this ```"chair . person . dog . "```
            width (int, optional): The with of the generated image. Defaults to 512.
            height (int, optional): The height of the generated image. Defaults to 512.
            num_inference_steps (int, optional): The number of inference steps to use for generating the image. Defaults to 15.
            guidance_scale (int, optional): The guidance scale to use for generating the image. Defaults to 9.
            num_images_per_prompt (int, optional): The number of images to generate per prompt. Defaults to 5.
            amount_of_images (int, optional): The amount of images to return. Defaults to 4.
            max_iterations (int, optional): The maximum number of iterations to use for generating the image. Defaults to 3.
            score_threshold (float, optional): The score threshold to use for the image. Defaults to None.
            laion_score_threshold (float, optional): The score threshold to use for the LAION model. Defaults to None.

        Returns:
            list[tuple]: The generated images with their scores.
        """
        # models could be unloaded, load them again
        if self.pipe is None or self.predict_model is None or self.feature_model is None:
            # load models
            self.logger.info(f"Loading Image models...")
            self.load()

        # check, if models are at the right device
        if self.pipe.device.type != self.device:
            self.logger.info(f"Image Models are not at the right device. Moving models to {self.device}...")
            self.to_gpu()

        # setup base directory
        image_dir = os.getenv('IMAGE_DIR')
        tmp_img_path = os.path.join(image_dir, str(uuid.uuid4()))
        os.makedirs(tmp_img_path, exist_ok=True)

        # setup thresholds
        laion_score_threshold = laion_score_threshold or 6.5
        score_threshold = score_threshold or ((len(search_prompt.split(' . ')) - 1) * 0.6) + laion_score_threshold

        all_images = []
        all_scores = []

        # get the image index for each iteration
        index_offset = [i * num_images_per_prompt for i in range(max_iterations)]

        self.logger.info(f"Starting image generation with {max_iterations} iterations. Prefered score: {score_threshold}")

        for i in range(max_iterations):
            # create a new folder for this iteration
            iteration_img_path = os.path.join(tmp_img_path, f"iteration-{i+1}")
            os.makedirs(iteration_img_path, exist_ok=True)

            # generate and score images
            images = generate_image(self.pipe,
                                    prompt,
                                    negative_prompt,
                                    width=width,
                                    height=height,
                                    num_inference_steps=num_inference_steps,
                                    guidance_scale=guidance_scale,
                                    num_images_per_prompt=num_images_per_prompt)

            image_scores = self._get_image_score(images, search_prompt, iteration_img_path, index_offset[i])

            all_images.extend(images)
            all_scores.extend(image_scores)

            self.logger.info(f"ITERATION {i}: HIGH SCORE IMAGES: {len([score for score in image_scores if score['result'] >= score_threshold])}. Results wrote to path: {iteration_img_path}")

            # break if we already have {amount_of_images} high score images
            if len([score for score in all_scores if score['result'] >= score_threshold]) >= amount_of_images:
                break

        # sort all_scores by score and select top four images with scores
        all_scores = sorted(all_scores, key=lambda x: x['result'], reverse=True)
        top_images_with_scores = [(all_images[score['index']], score) for score in all_scores[:amount_of_images]]
            
        return top_images_with_scores
    

    def _get_image_score(self, all_images, search_prompt: str, image_path: str, index_offset: int):
        """Creates a score for each image in the list of images.

        Args:
            all_images (List): All images generated by the Stable Diffusion model.
            search_prompt (str): The prompt to search for. Looks like this ```"chair . person . dog . "```
            image_path (str): The path to the folder, where the images are stored.

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

        for i, image in enumerate(all_images):
            image_index = i + index_offset

            # get the score from the laion model
            laion_score = predict_score(image=image, feature_model=self.feature_model, predict_model=self.predict_model, feature_preprocess=self.feature_preprocess)

            # get the score from the dino model
            dino_score, _, _ = self.object_detection.predict(image=image, prompt=search_prompt, index=image_index, img_path=image_path)

            # calculate the result score
            result_score = laion_score + dino_score

            self.logger.info(f"SCORING IMAGE {image_index}: PROMPTS: {search_prompt} LAION: {round(laion_score, 3)} - DINO: {round(dino_score, 3)} - RESULT: {round(result_score, 3)}")

            result.append({
                'laion': laion_score,
                'dino': dino_score,
                'result': result_score,
                'index': image_index
            })

        # write result as json file to image_path
        with open(os.path.join(image_path, "ratings.json"), "w") as file:
            file.write(json.dumps(result))

        return result


    # FUNCTIONS FOR MEMORY MANAGEMENT

    def unload_models(self, strategy: str = 'cpu'):
        if strategy == 'complete':
            del self.pipe
            del self.predict_model
            del self.feature_model
            del self.object_detection

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
        # self.object_detection.cpu()
        end_time = time.time()
        self.logger.info(f"Image Models moved to CPU. Time taken: {end_time - start_time} seconds.")

        # set the loading state of the models
        self.loading_state = "cpu"
    
    def to_gpu(self):
        start_time = time.time()
        self.pipe = self.pipe.to(self.device)
        self.predict_model = self.predict_model.cuda()
        self.feature_model = self.feature_model.cuda()
        # self.object_detection.cuda()
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
