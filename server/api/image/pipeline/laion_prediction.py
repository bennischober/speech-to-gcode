import torch
import torch.nn as nn
import os
from urllib.request import urlretrieve
from os.path import expanduser
import open_clip

device = "cuda" if torch.cuda.is_available() else "cpu"

# create model to predict aesthetic score
def _get_aesthetic_model(clip_model="vit_l_14"):
    """load the aethetic model"""
    home = expanduser("~")
    cache_folder = home + "/.cache/emb_reader"
    path_to_model = cache_folder + "/sa_0_4_"+clip_model+"_linear.pth"
    if not os.path.exists(path_to_model):
        os.makedirs(cache_folder, exist_ok=True)
        url_model = (
            "https://github.com/LAION-AI/aesthetic-predictor/blob/main/sa_0_4_"+clip_model+"_linear.pth?raw=true"
        )
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
    m = m.to(device)
    return m

predict_model = _get_aesthetic_model(clip_model="vit_l_14")
predict_model.eval()

feature_model, _, feature_preprocess = open_clip.create_model_and_transforms('ViT-L-14', pretrained='openai', device=device)

# predict aesthetic score
def predict_score(image):
    print(device)

    img = feature_preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = feature_model.encode_image(img)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        aesthetic_score = predict_model(image_features)
        print(f"image aesthetic score: {aesthetic_score}")
    return aesthetic_score
