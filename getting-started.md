# Getting Started

## Wie wird kann das Projekt gestartet werden?

### Lokale UI

Falls ein Windows-PC verwendet wird, kann die requierments.txt Datei verwendet werden, um die benötigten Python-Pakete zu installieren. Ansonsten müssen die Pakete manuell installiert werden. Die UI kann dann mit dem Befehl `python app.py` gestartet werden.

**Hinweis:** In dem Ordner `/components` sind alle UI Komponenten definiert. In `/utils` werden der Logger und die Config geladen.

### Server

Zunächst muss der Hochschul-VPN verwendet werden, damit auf das GPU-Cluster zugegriffen werden kann. Anschließend muss per SSH auf den Server zugegriffen werden. Hier kann dann der Port 5000 freigegeben werden, damit die API von außerhalb des Clusters erreichbar ist. Dies kann z.B. mit dem Befehl `ssh -L 5000:localhost:5000 <HS_NAME>@<SERVER_IP>` gemacht werden.

> Empfehlung: Statt den Befehl von oben zu verwenden, kann die SSH-Verbindung mit VS Code gestartet und die Ports automatisch im Port-Tab weitergeleitet werden!

Der Server kann mit dem Befehl `docker compose up --build -d` gestartet werden.

**Hinweis:** Damit die Shelldatei `entrypoint.sh` ausgeführt werden kann, muss diese Datei vorher mit dem Befehl `chmod +x entrypoint.sh` ausführbar gemacht werden.

**Hinweis:** Die Konsole sollte sich im korrekten Ordner befinden, damit die Docker-Compose Datei und die entrypoint Datei gefunden werden kann.

Bevor der Server gestartet werden kann, muss zunächst die docker-compose Datei angepasst werden. Hierbei wurden die zu ändernden Teile mit `<>` markiert.

```docker-compose
version: '3.8'

services:
  <HS_NAME>_apis:
    build: 
      context: /home/<HS_NAME>/text_to_gcode/api/
      dockerfile: Dockerfile
    image: <HS_NAME>_apis:<VERSION>
    environment:
      - CUDA_HOME=/usr/local/cuda-11.7/
      - TRANSFORMERS_CACHE=/models
      - NLTK_DATA=/models/nltk_data
      - LOGS_DIR=/logs
      - API_PORT=5000
      - IMAGE_DIR=/images
    volumes:
      - /home/<HS_NAME>/models:/models
      - /home/<HS_NAME>/logs:/logs
      - /home/<HS_NAME>/images:/images
    ports:
      - "5000:5000"
    deploy:
      resources:
        reservations:
          devices:
          - driver: nvidia
            device_ids: ['1'] # binds to GPU 1 => select correct GPU on cluster!
            capabilities: [gpu]

```

> **Hinweis zu den Volumes:** Zum einen werden die Modelle auf persistentem Speicher gespeichert, damit diese nicht bei jedem Neustart des Containers neu heruntergeladen werden müssen. Zum anderen werden die Logs und Bilder auf persistentem Speicher gespeichert, damit diese nicht verloren gehen, falls der Container neu gestartet wird. Diese können helfen, Probleme zu identifizieren.

Um zu testen, ob der Container korrekt gestartet wurde, kann der Befehl `docker ps` verwendet werden. Falls der Container nicht in der Liste auftaucht, dann kann der Befehl `docker ps -a` verwendet werden. Hier kann nach dem Container gesucht werden und mit dem Befehl `docker logs <CONTAINER_ID>` können die Logs des Containers angezeigt werden.

Ist der Container erfolgreich gestartet, ist die API unter `localhost:5000` erreichbar.

## Wie können andere Modelle verwendet werden?

Zunächst müssen die bestehenden Pipelines bearbeitet werden. Hierzu müssen die Dateien [``TextPipeline.py``](./server/api/pipelines/text/TextPipeline.py) und [``ImagePipeline.py``](./server/api/pipelines/image/ImagePipeline.py) bearbeitet werden. In diesen Dateien werden die Modelle geladen und die Pipeline definiert. Die Modelle können dann in den entsprechenden Funktionen verwendet werden. Bei der Image Pipeline müssen zusätzlich die anderen Dateien in dem Ordner [``image``](./server/api/pipelines/image/) bearbeitet werden, da die Funktionalität auf diese Dateien aufgeteilt ist.

Zusätzlich muss die Datei [``Dockerfile``](./server/api/Dockerfile) bearbeitet werden. Hierbei können die gewünschten packages für die Modelle geändert werden.

Sollte GroundingDINO entfernt werden, können viele Parts des Dockerfiles entfernt werden. Zusätzlich muss angemerkt werden, dass der Dockercontainer nur das Image `FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel` verwendet, da GroundingDINO auf Cuda zugreifen muss (im Container!). Das Image kann also geändert werden, falls GroundingDINO nicht mehr verwendet wird. Zusätzlich kann der entrypoint geändert werden. Aktuell wird die Datei `entrypoint.sh` verwendet, damit die für GroundingDINO benötigten C++ Dateien gebuildet werden. Statt ``CMD ["/usr/app/src/entrypoint.sh"]`` könnte also z.B. ``CMD ["python", "app.py"]`` verwendet werden.

## Configs

Das lokale Projekt wird über die Datei [``config.ini``](./local/config.ini) konfiguriert. Hier werden die URLs der API Endpoints definiert, sowie die default prompts. Zusätzlich werden die Standardwerte für die GCODE Generierung festgelegt.
