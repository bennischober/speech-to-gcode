from flask import Flask, request, make_response
import torch
from pipeline.speech_to_text import transcribe

app = Flask(__name__)

app.logger.info(f"CUDA available? {torch.cuda.is_available()}")

@app.route("/api/transcribe", methods=['POST'])
def transcribe_endpoint():
    file = request.files.get("audio")
    if not file:
        return "No audio file provided", 400

    text = transcribe(file, app.logger)

    if text is None:
        return "Error generating text", 500

    return text

if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')

# Docker Commands:
# docker image build -t stbescho_text_api:0.5 /home/stbescho/text_to_gcode/text
# docker run -d --gpus '"device=1"' -p 5000:5000 --name stbescho_text_api stbescho_text_api:0.5
