FROM python:3.9-slim

RUN pip install --no-cache-dir google-cloud-storage google-cloud-firestore Flask requests pillow flask-cors

WORKDIR /app

COPY imageHandler.py /app/

EXPOSE 5000

ENTRYPOINT ["python", "-u", "imageHandler.py"]