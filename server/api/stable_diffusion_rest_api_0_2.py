from flask import Flask, request, send_file, make_response
from PIL import Image
from diffusers import StableDiffusionPipeline
from transformers import pipeline, AutoProcessor, WhisperForConditionalGeneration
import torch
import io
import zipfile

app = Flask(__name__)

# Load Model and generate Pipeline
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

# Load Speech to Text model
# reference: https://huggingface.co/openai/whisper-large#english-to-english
stt_model_id = "openai/whisper-large-v2"
whisper_processor = AutoProcessor.from_pretrained(stt_model_id)
whisper_model = WhisperForConditionalGeneration.from_pretrained(stt_model_id)
# whisper_model.config.forced_decoder_ids = None


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

@app.route("/api/stt", methods=['POST'])
def stt():
    # get bytes send with request.post(, data=data)
    data = request.data
    
    # convert bytes to torch tensor
    input_features = torch.tensor(whisper_processor(data, return_tensors="pt").input_ids).to("cuda")

    # reference: https://huggingface.co/docs/transformers/main/en/model_doc/whisper#transformers.WhisperForConditionalGeneration.forward.example

    generated_ids = whisper_model.generate(input=input_features)
    generated_text = whisper_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # translate text
    result = pipeline("translation_de_to_en")(generated_text)
    # response = make_response(result)
    # return response
    return result


if __name__ == '__main__':
    app.run(port=5001, debug=True, host='0.0.0.0')

# Docker Commands:
# docker image build -t stligoeh_stable_diff_api:0.2 /home/stligoeh/text_to_gcode/text_to_image/docker_image
# docker run -d --gpus '"device=1"' --rm -p 5001:5001 --name stligoeh_stable_diff_multi stligoeh_stable_diff_api:0.2