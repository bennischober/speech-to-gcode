import torch
from lib.logger import get_logger

device = "cuda" if torch.cuda.is_available() else "cpu"
logger = get_logger(__name__)

# predict aesthetic score
def predict_score(image, feature_model, predict_model, feature_preprocess):
    img = feature_preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = feature_model.encode_image(img)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        aesthetic_score = predict_model(image_features)
        logger.info(f"image aesthetic score: {aesthetic_score}")
    return aesthetic_score
