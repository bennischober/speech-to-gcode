from flask import Flask, request, make_response
import torch
import io
import zipfile
from pipeline.image.stable_diffusion import generate_image
from pipeline.image.laion_prediction import predict_score
from pipeline.text.speech_to_text import transcribe

app = Flask(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ToDo: add segment_anything (test in separate docker container first); add continuous learning (see ChatGPT)

@app.route('/stable_diff', methods=['POST'])
def image_endpoint():
    # get params
    params = request.json

    prompt = params.get('prompt', None)
    negative_prompt = params.get('negative_prompt', None)
    width = params.get('width', 512)
    height = params.get('height', 512)
    num_inference_steps = params.get('num_inference_steps', 15)
    guidance_scale = params.get('guidance_scale', 9)
    num_images_per_prompt = params.get('num_images_per_prompt', 1)

    images = []

    while len(images) < 4:
        # run stable_diffusion pipeline
        image = generate_image(prompt, negative_prompt, width, height, num_inference_steps, guidance_scale)

        if image is None:
            app.logger.error(f"Error generating image. Going to next iteration.")
            continue

        # run aesthetic score prediction
        score = predict_score(image)

        if score > 0.7:
            images.append(image)

    print(len(images))

    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, mode='w') as zip_file:
        for i, image in enumerate(images):
            filename = f'image_{i}.jpg'
            img_data = io.BytesIO()
            image.save(img_data, 'JPEG')
            img_data.seek(0)  # Important to reset the stream position to the beginning
            zip_file.writestr(filename, img_data.read())  # Use `read()` instead of `getvalue()`

    # Return ZIP file
    zip_data.seek(0)
    response = make_response(zip_data.read())
    response.headers.set('Content-Type', 'application/zip')
    response.headers.set('Content-Disposition', 'attachment', filename='generated_images.zip')
    return response

@app.route("/api/transcribe", methods=['POST'])
def transcribe_endpoint():
    file = request.files.get("audio")
    if not file:
        return "No audio file provided", 400

    text = transcribe(file, app.logger)

    if text is None:
        return "Error generating text", 500

    return text

# @app.route("/api/translate", methods=['POST'])
# def translate_endpoint():
#     params = request.json
#     text = params.get('text', None)

#     if text is None:
#         return "No text provided", 400

#     output = translate(text, app.logger)

#     if output is None:
#         return "Error translating text", 500

#     return output


if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')

# Docker Commands:
# docker image build -t stbescho_rest_apis:0.4 /home/stbescho/text_to_gcode/
# docker run -d --gpus '"device=1"' -p 5000:5000 --name stbescho_rest_apis stbescho_rest_apis:0.4
