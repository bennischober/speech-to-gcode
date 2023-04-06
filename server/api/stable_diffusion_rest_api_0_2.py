from flask import Flask, request, send_file, make_response
from PIL import Image
from diffusers import StableDiffusionPipeline
import torch
import io
import zipfile

app = Flask(__name__)

# Load Model and generate Pipeline
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

@app.route('/api_multi', methods=['POST'])
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
    images = pipe(prompt, num_images_per_prompt=num_images_per_prompt).images 
    print('amount Images', len(images))
    print('generated images for prompt:', prompt)

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


if __name__ == '__main__':
    app.run(port=5001, debug=True, host='0.0.0.0')

# Docker Commands:
# docker image build -t stligoeh_stable_diff_api:0.2 /home/stligoeh/text_to_gcode/text_to_image/docker_image
# docker run -d --gpus '"device=1"' --rm -p 5001:5001 --name stligoeh_stable_diff_multi stligoeh_stable_diff_api:0.2