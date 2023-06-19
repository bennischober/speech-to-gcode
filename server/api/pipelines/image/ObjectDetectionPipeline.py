import os
from typing import Tuple
from PIL import Image
import torch
import numpy as np
import cv2
import groundingdino
from groundingdino.util.inference import load_model, predict, annotate
import groundingdino.config.GroundingDINO_SwinT_OGC
import groundingdino.datasets.transforms as T
from lib.logger import get_logger

BOX_TRESHOLD = 0.35
TEXT_TRESHOLD = 0.25

class ObjectDetectionPipeline:
    def __init__(self, cache_dir: str):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.cfg_path = groundingdino.config.GroundingDINO_SwinT_OGC.__file__
        self.cache_dir = cache_dir
        self.root_dir = os.path.join(cache_dir, "groundingdino")
        self.logger = get_logger(__name__)
    
    def load(self):
        """
        Downloads the model and its weights and loads them into memory. If the model is already downloaded, it will be loaded from the cache_dir.
        """
        weights_path = os.path.join(self.root_dir, "weights")
        weights_file_path = os.path.join(weights_path, "groundingdino_swint_ogc.pth")
        if not os.path.exists(weights_path):
            os.makedirs(weights_path)
        if not os.path.isfile(weights_file_path):
            # download weights
            self.logger.info("Weights not found. Downloading.")
            import requests
            url = "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"
            response = requests.get(url)
            with open(weights_file_path, 'wb') as f:
                f.write(response.content)
        self.weights = weights_file_path
        self.model = load_model(self.cfg_path, self.weights)

    def load_image(self, image) -> Tuple[np.array, torch.Tensor]:
        transform = T.Compose(
            [
                T.RandomResize([800], max_size=1333),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )
        if isinstance(image, np.ndarray):
            # Convert numpy array to PIL Image
            image = Image.fromarray((image * 255).astype(np.uint8)).convert("RGB")  # The * 255 is necessary if the image's values range from 0 to 1
        
        image_transformed, _ = transform(image, None)
        return np.asarray(image), image_transformed


    def predict(self, image, prompt: str, index: int, img_path: str):
        """Predicts the bounding boxes and phrases for the given image and prompt.

        Image scoring with groundingdino works as follows:
        1. The image is passed through the object detection model.
        2. The resulting bounding boxes are passed through the text model.
        3. The resulting phrases are passed through the text model.
        4. The logits of the phrases are summed up and multiplied with the number of key words in the prompt

        Args:
            image (Image|ndarray): PIL Image or numpy array 
            prompt (str): The prompt to use for the prediction. Note, that the prompt might look like this: ```"chair . person . dog ."```
            index (int): The index of the image in the batch.
            img_path (str): The path to the image.

        Returns:
            Tuple[float, Tensor, List[str]]: The final rating value, logits and phrases for the given image and prompt.
        """

        # split prompt into nouns
        if prompt is None:
            prompt = ""
        nouns = prompt.split(" . ")

        image_source, img = self.load_image(image)

        boxes, logits, phrases = predict(
            model=self.model,
            image=img,
            caption=prompt,
            box_threshold=BOX_TRESHOLD,
            text_threshold=TEXT_TRESHOLD,
            device=self.device,
        )

        
        tmp_img_path = os.path.join(img_path, f"image_{index}.jpg")

        annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases)
        cv2.imwrite(tmp_img_path, annotated_frame)

        # clear cache
        torch.cuda.empty_cache()

        # get the logits for the nouns
        result = {}
        for element, value in zip(phrases, logits):
            result[element] = max(result.get(element, float('-inf')), value.item())
        result = {key: value for key, value in result.items() if key in nouns}

        # calculate final score
        final_score = 0.0
        for value in result.values():
            final_score += value

        return final_score, logits, phrases
    
    def to(self, device):
        """Moves the model to the given device.

        Args:
            device (str|device): The device to move the model to. Can be either "cpu", "cuda" or a torch.device.
        """
        self.model = self.model.to(device)
        self.device = device

    def cpu(self):
        self.model = self.model.to("cpu")
        self.device = "cpu"

    def cuda(self):
        self.model = self.model.to("cuda")
        self.device = "cuda"
