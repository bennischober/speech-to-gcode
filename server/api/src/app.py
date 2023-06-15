import os
import io
import logging
import zipfile
from flask import Flask, request, make_response
from flask_cors import CORS
import torch
from pipelines.image.ImagePipeline import ImagePipeline
from pipelines.text.TextPipeline import TextPipeline


app = Flask(__name__)
CORS(app)

cache_dir = os.getenv('TRANSFORMERS_CACHE')

# setup logging
app.logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(cache_dir, "api.log"))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# setup pipelines
image_pipeline = ImagePipeline(cache_dir)
text_pipeline = TextPipeline(cache_dir)

# load an move to cpu => faster startup
image_pipeline.load()
image_pipeline.to_cpu()

# default: load text_pipeline on startup
text_pipeline.load()

@app.route('/api/images', methods=['POST'])
def image_endpoint():
    app.logger.info("Calling image_endpoint")

    # get params
    params = request.json

    prompt = params.get('prompt', None)
    negative_prompt = params.get('negative_prompt', None)
    width = params.get('width', 512)
    height = params.get('height', 512)
    num_inference_steps = params.get('num_inference_steps', 15)
    guidance_scale = params.get('guidance_scale', 9)

    # check, if text_pipeline is loaded
    if text_pipeline.is_loaded() == "cuda":
        text_pipeline.to_cpu()
    
    # check, if image pipeline is loaded
    image_pipeline.load()

    # generate images using the image pipeline
    images = image_pipeline.generate_images(prompt, negative_prompt, width=width, height=height, num_inference_steps=num_inference_steps, guidance_scale=guidance_scale)

    if images is None:
        app.logger.error(f"Error generating image.")
        return "Error generating image", 500

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
    
    return response


@app.route("/api/transcribe", methods=['POST'])
def transcribe_endpoint():
    app.logger.info("Calling transcribe_endpoint")

    file = request.files.get("audio")
    if not file:
        return "No audio file provided", 400

    # move image_pipeline to cpu
    if image_pipeline.is_loaded() == "cuda":
        image_pipeline.to_cpu()
    
    text_pipeline.load()

    text = text_pipeline.transcribe(file)

    if text is None:
        return "Error generating text", 500

    # move to cpu
    text_pipeline.to_cpu()

    # load image pipeline
    image_pipeline.load()

    return text
