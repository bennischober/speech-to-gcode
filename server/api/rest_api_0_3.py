from flask import Flask, request, send_file, make_response
from PIL import Image
from diffusers import StableDiffusionPipeline
from transformers import WhisperProcessor, WhisperForConditionalGeneration, WhisperFeatureExtractor, pipeline
import torch
import io
import zipfile
import numpy as np

app = Flask(__name__)

# Load Model and generate Pipeline
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

# Load Speech to Text model
# reference: https://huggingface.co/openai/whisper-large#english-to-english
stt_model_id = "openai/whisper-large-v2"
whisper_processor = WhisperProcessor.from_pretrained(stt_model_id)
whisper_model = WhisperForConditionalGeneration.from_pretrained(stt_model_id).to("cuda")

@app.route('/stable_diff', methods=['POST'])
def generate_image():
    # get params
    params = request.json

    prompt = params.get('prompt', None)
    negative_prompt = params.get('negative_prompt', None)
    width = params.get('width', 512)
    height = params.get('height', 512)
    num_inference_steps = params.get('num_inference_steps', 15)
    guidance_scale = params.get('guidance_scale', 9)
    num_images_per_prompt = params.get('num_images_per_prompt', 1)


    print('received prompt:', prompt)

    # Generate Images
    images = pipe(
        prompt, 
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        num_images_per_prompt=num_images_per_prompt).images 

    print(f'generated {len(images)} images for prompt: {prompt}')

    # Create ZIP file
    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, mode='w') as zip_file:
        for i, image in enumerate(images):
            filename = f'image_{i}.jpg'
            img_data = io.BytesIO()
            image.save(img_data, 'JPEG')
            zip_file.writestr(filename, img_data.getvalue())

    # Return ZIP file
    zip_data.seek(0)
    response = make_response(zip_data.getvalue())
    response.headers.set('Content-Type', 'application/zip')
    response.headers.set('Content-Disposition', 'attachment', filename='generated_images.zip')
    return response

@app.route("/api/stt", methods=['POST'])
def stt():
    file = request.files.get("audio")
    if not file:
        return "No audio file provided", 400

    data = np.frombuffer(file.read(), dtype=np.int16)

    inputs = whisper_processor.feature_extractor(data,  return_tensors="pt", sampling_rate=16_000).input_features.to("cuda")
    predicted_ids = whisper_model.generate(inputs, max_length=480_000)
    generated_text = whisper_processor.batch_decode(predicted_ids, skip_special_tokens=True, normalize=True)[0]

    app.logger.info(f"Text generated: {generated_text}")

    return generated_text


if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')

# Docker Commands:
# docker image build -t stbescho_rest_apis:0.3 /home/stbescho/text_to_gcode/
# docker run -d --gpus '"device=1"' --rm -p 5000:5000 --name stbescho_rest_apis stbescho_rest_apis:0.3
