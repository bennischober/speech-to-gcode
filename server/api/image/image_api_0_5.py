from flask import Flask, request, make_response
import torch
import io
import zipfile
from pipeline.stable_diffusion import generate_image
from pipeline.laion_prediction import predict_score

app = Flask(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

    # since we only have 24GB of VRAM, and the other the text pipeline needs about 6GB in idle, while this one needs around 10, we need to clear the VRAM before generating the image. Also, we are only able to create a smaller batch of images, since we are running out of memory otherwise. Thats why generate_images is called twice to generate 10 images.

    # generate first 5 images
    all_images = generate_image(prompt, negative_prompt, width,
                                height, num_inference_steps, guidance_scale, logger=app.logger)
    # generate next 5 images
    all_images = all_images + generate_image(prompt, negative_prompt, width,
                                             height, num_inference_steps, guidance_scale, logger=app.logger)

    if all_images is None:
        app.logger.error(f"Error generating image.")
        return "Error generating image", 500

    app.logger.info(f"Image generated successfully. {len(all_images)}")

    sorte_img = sorted(
        all_images, key=lambda x: predict_score(x), reverse=True)

    # get top 4 images
    images = sorte_img[:4]

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

    # Return ZIP file
    zip_data.seek(0)
    response = make_response(zip_data.read())
    response.headers.set('Content-Type', 'application/zip')
    response.headers.set('Content-Disposition', 'attachment',
                         filename='generated_images.zip')
    return response


if __name__ == '__main__':
    app.run(port=5001, debug=True, host='0.0.0.0')

# Docker Commands:
# docker image build -t stbescho_image_api:0.5 /home/stbescho/text_to_gcode/image
# docker run -d --gpus '"device=1"' -p 5001:5001 --name stbescho_image_api stbescho_image_api:0.5
