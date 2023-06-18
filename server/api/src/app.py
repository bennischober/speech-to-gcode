import os
import io
import json
import gc
import time
import logging
import zipfile
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
import torch
from pipelines.image.ImagePipeline import ImagePipeline
from pipelines.text.TextPipeline import TextPipeline


app = Flask(__name__)
CORS(app)

cache_dir = os.getenv('TRANSFORMERS_CACHE')
logs_dir = os.getenv('LOGS_DIR')

# setup logging
app.logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(logs_dir, "api.log"))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# setup pipelines
image_pipeline = ImagePipeline(cache_dir)
text_pipeline = TextPipeline(cache_dir)

# load an move to cpu => faster startup
image_pipeline.load()
# image_pipeline.to_cpu()

# default: load text_pipeline on startup
text_pipeline.load()

@app.route('/api/images', methods=['POST'])
def image_endpoint():
    start_time = time.time()

    app.logger.info("Calling image_endpoint")

    # get params
    params = request.json

    prompt = params.get('prompt', None)
    negative_prompt = params.get('negative_prompt', None)
    search_prompt = params.get('search_prompt', None)
    width = params.get('width', 512)
    height = params.get('height', 512)
    num_inference_steps = params.get('num_inference_steps', 15)
    guidance_scale = params.get('guidance_scale', 9)
    num_images_per_prompt = params.get('num_images_per_prompt', 10)

    # # check, if text_pipeline is loaded
    # if text_pipeline.is_loaded() == "cuda":
    #     text_pipeline.to_cpu()
    
    # check, if image pipeline is loaded
    image_pipeline.load()

    # generate images using the image pipeline
    images_with_scores = image_pipeline.generate_images(prompt,
                                                        negative_prompt,
                                                        search_prompt=search_prompt,
                                                        width=width,
                                                        height=height,
                                                        num_inference_steps=num_inference_steps, guidance_scale=guidance_scale,
                                                        num_images_per_prompt=num_images_per_prompt)

    if images_with_scores is None:
        app.logger.error(f"Error generating image.")
        return "Error generating image", 500
    
    images = [img for img, _ in images_with_scores]
    ratings = {f'image_{i}.jpg': score for i, (_, score) in enumerate(images_with_scores)}

    # Create ZIP archive of images and return
    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, mode='w') as zip_file:
        for i, image in enumerate(images):
            filename = f'image_{i}.jpg'
            img_data = io.BytesIO()
            image.save(img_data, 'JPEG')
            # Important to reset the stream position to the beginning
            img_data.seek(0)
            # Use `read()` instead of `getvalue()`
            zip_file.writestr(filename, img_data.read())
        
        # add rations as json
        ratings_filename = "ratings.json"
        ratings_data = io.BytesIO()
        ratings_data.write(json.dumps(ratings).encode('utf-8'))
        ratings_data.seek(0)
        zip_file.writestr(ratings_filename, ratings_data.read())

    # clear VRAM
    torch.cuda.empty_cache()

    # move back to cpu?
    # image_pipeline.to_cpu()

    # Return ZIP file
    zip_data.seek(0)
    response = make_response(zip_data.read())
    response.headers.set('Content-Type', 'application/zip')
    response.headers.set('Content-Disposition', 'attachment',
                         filename='generated_images.zip')
    
    end_time = time.time()
    app.logger.info(f"Image_Endpoint duration: {end_time - start_time} seconds")

    return response


@app.route("/api/transcribe", methods=['POST'])
def transcribe_endpoint():
    start_time = time.time()

    app.logger.info("Calling transcribe_endpoint")

    file = request.files.get("audio")
    if not file:
        return "No audio file provided", 400

    # # move image_pipeline to cpu
    # if image_pipeline.is_loaded() == "cuda":
    #     image_pipeline.to_cpu()

    # Only move whisper to cpu, keep all other models on gpu
    
    text_pipeline.load()

    prompt, search_prompt = text_pipeline.transcribe(file)

    if prompt is None or search_prompt is None:
        return "Error generating text", 500

    # # move to cpu
    # text_pipeline.to_cpu()

    # # load image pipeline
    # image_pipeline.load()

    end_time = time.time()
    app.logger.info(f"Transcribe_Endpoint duration: {end_time - start_time} seconds")

    return jsonify({"prompt": prompt, "search_prompt": search_prompt})

@app.route("/api/translate", methods=['POST'])
def translate_endpoint():
    app.logger.info("Calling translate_endpoint")

    # get params
    params = request.json

    text = params.get('text', None)

    # # move image_pipeline to cpu
    # if image_pipeline.is_loaded() == "cuda":
    #     image_pipeline.to_cpu()
    
    text_pipeline.load()

    prompt, search_prompt = text_pipeline.translate(text)

    if prompt is None or search_prompt is None:
        return "Error translating text", 500

    # # move to cpu
    # text_pipeline.to_cpu()

    # # load image pipeline
    # image_pipeline.load()

    return jsonify({"prompt": prompt, "search_prompt": search_prompt})

@app.route('/api/health', methods=['GET'])
def health_check():
    app.logger.info("Health check")
    return {"status": "UP"}, 200

@app.route('/api/state', methods=['GET'])
def get_state():
    app.logger.info("Getting state")
    return {"state": {
        "image_pipeline": image_pipeline.is_loaded(),
        "text_pipeline": text_pipeline.is_loaded()
    }}, 200
