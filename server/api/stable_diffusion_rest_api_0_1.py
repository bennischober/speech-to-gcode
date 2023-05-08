from flask import Flask, request, send_file, make_response
from PIL import Image
from diffusers import StableDiffusionPipeline
import torch
from io import BytesIO

app = Flask(__name__)

# Load Model and generate Pipeline
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

# Generate Rest API
@app.route('/api', methods=['POST'])
def generate_image():
    prompt = request.json['prompt']
    print('recieved promt:', prompt)

    # Generate Image
    diff_img = pipe(prompt).images[0]  
    print('generated image for prompt:', prompt)

    # Return Image
    diff_img.save('stable_diff_image.jpg')
    return send_file('stable_diff_image.jpg', mimetype='image/jpeg')

# @app.route('/api', methods=['POST'])
# def generate_image():
#     prompt = request.json['prompt']
#     print('recieved promt:', prompt)

#     # Generate Image
#     images = pipe(prompt).images 
#     print('generated images for prompt:', prompt)

#     # Return Image
#     # Return Images
#     response = make_response()
#     for image in images:
#         img_io = BytesIO()
#         image.save(img_io, 'JPEG')
#         img_io.seek(0)
#         response.data += img_io.getvalue()

#     response.headers.set('Content-Type', 'image/jpeg')
#     response.headers.set('Content-Disposition', 'attachment', filename='generated_images.zip')
#     return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# Docker Commands:
# docker image build -t stligoeh_stable_diff_api:0.1 /home/stligoeh/text_to_gcode/text_to_image/docker_image
# docker run -d --gpus '"device=1"' --rm -p 5000:5000 --name stligoeh_stable_diff stligoeh_stable_diff_api:0.1