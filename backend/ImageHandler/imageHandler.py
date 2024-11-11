import uuid
import logging
from google.cloud import storage, firestore
from flask import Flask, request, jsonify
import requests
import json
from io import BytesIO
from PIL import Image
from datetime import timedelta
import os

# Get the absolute path to the credentials file
current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)
credentials_path = os.path.join(current_dir, "dcsc-project-440602-9412462c618e.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./dcsc-project-440602-9412462c618e.json"
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
storage_client = storage.Client(project="dcsc-project-440602")
firestore_client = firestore.Client(project="dcsc-project-440602")
image_port = int(os.getenv("IMAGE_PORT", 5000))

# Configuration
BUCKET_NAME = 'cu-image-flow'
INTERACTION_POD_URL = 'http://interaction-pod-service/api/v1/metadata'

# Configure logging
logging.basicConfig(level=logging.INFO)

logging.info(f"pod is running")

# Helper function to upload image to Google Cloud Storage
def upload_to_gcs(image_file, batch_uuid, image_name):
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{batch_uuid}/input/{image_name}")
        blob.upload_from_file(image_file)
        public_url = blob.public_url
        logging.info(f"Image uploaded to GCS: {public_url}")
        return public_url
    except Exception as e:
        logging.error(f"Failed to upload image to GCS: {e}")
        raise


# Function to save data to Firestore
def save_to_firestore(table_name, data):
    try:
        doc_ref = firestore_client.collection(table_name).document(data["UUID"])
        doc_ref.set(data)
        logging.info(f"Data saved to Firestore: {table_name} - {data}")
    except Exception as e:
        logging.error(f"Failed to save data to Firestore: {e}")
        raise

# Function to save data to Firestore with support for custom document IDs
def save_to_firestore(table_name, data, doc_id=None):
    try:
        if doc_id:
            doc_ref = firestore_client.collection(table_name).document(doc_id)
        else:
            doc_ref = firestore_client.collection(table_name).document(data["UUID"])
        doc_ref.set(data)
        logging.info(f"Data saved to Firestore: {table_name} - {data}")
    except Exception as e:
        logging.error(f"Failed to save data to Firestore: {e}")
        raise


@app.route('/get-processed-images', methods=['GET'])
def get_output_urls():
    # Extract the UUID from the request arguments
    uuid = request.args.get('UUID')
    if not uuid:
        return jsonify({"error": "UUID is required"}), 400

    try:
        # Define folder paths for input and output images within the specified UUID
        input_folder = f"{uuid}/input/"
        output_folder = f"{uuid}/output/"

        # Initialize the bucket and list blobs (files) in the input and output folders
        bucket = storage_client.bucket(BUCKET_NAME)

        # Create dictionaries to map file names to URLs for both input and output folders
        input_urls = {}
        output_urls = {}

        # List blobs in input folder and store URLs with file names
        input_blobs = bucket.list_blobs(prefix=input_folder)
        for blob in input_blobs:
            if blob.name.endswith("/"):
                continue  # Skip folder paths
            file_name = os.path.basename(blob.name)
            input_urls[file_name] = blob.generate_signed_url(expiration=timedelta(hours=1))

        # List blobs in output folder and store URLs with file names
        output_blobs = bucket.list_blobs(prefix=output_folder)
        for blob in output_blobs:
            if blob.name.endswith("/"):
                continue  # Skip folder paths
            file_name = os.path.basename(blob.name)
            output_urls[file_name] = blob.generate_signed_url(expiration=timedelta(hours=1))

        # Pair images by file name and prepare the response format expected by UI
        image_pairs = []
        for file_name, input_url in input_urls.items():
            if file_name in output_urls:
                image_pairs.append({
                    "file_name": file_name,
                    "before_url": input_url,
                    "after_url": output_urls[file_name]
                })

        # Check if any pairs were found, if not, return an error message
        if not image_pairs:
            return jsonify({"error": "No matching image pairs found for the given UUID"}), 404

        return jsonify({"UUID": uuid, "image_pairs": image_pairs}), 200

    except Exception as e:
        logging.error(f"Failed to retrieve output URLs for UUID {uuid}: {e}")
        return jsonify({"error": f"Failed to retrieve output URLs: {e}"}), 500

@app.route('/get-images-by-status', methods=['GET'])
def get_images_by_status():
    uuid = request.args.get('UUID')
    is_processed = request.args.get('IsProcessed')

    # Ensure both UUID and IsProcessed are provided
    if uuid is None or is_processed is None:
        return jsonify({"error": "UUID and IsProcessed parameters are required"}), 400

    # Convert is_processed to boolean since Firestore expects a boolean value
    try:
        is_processed = is_processed.lower() == 'true'
    except ValueError:
        return jsonify({"error": "IsProcessed must be 'true' or 'false'"}), 400

    try:
        # Query Firestore for documents with matching UUID and IsProcessed status
        image_metadata_ref = firestore_client.collection("ImageMetadata")
        query = image_metadata_ref.where("UUID", "==", uuid).where("IsProcessed", "==", is_processed)
        results = query.stream()

        # Prepare the response data
        images = []
        for doc in results:
            images.append(doc.to_dict())

        # Check if any documents were found, return appropriate message
        if not images:
            return jsonify({"error": "No images found matching the criteria"}), 404

        return jsonify({"UUID": uuid, "IsProcessed": is_processed, "images": images}), 200

    except Exception as e:
        logging.error(f"Failed to retrieve images with UUID {uuid} and IsProcessed {is_processed}: {e}")
        return jsonify({"error": f"Failed to retrieve images: {e}"}), 500



@app.route('/upload-images', methods=['POST'])
def upload_images():
    if 'files' not in request.files or 'metadata' not in request.form:
        logging.error("Files and metadata are required")
        return jsonify({"error": "Files and metadata are required"}), 400

    # Retrieve image files and metadata
    files = request.files.getlist('files')
    metadata = json.loads(request.form['metadata'])
    email = metadata.get("email")
    images_metadata = metadata.get("imagesMetadata", [])

    # Ensure metadata and files have matching lengths
    if len(files) != len(images_metadata):
        logging.error("Number of files does not match number of metadata entries")
        return jsonify({"error": "Mismatched files and metadata entries"}), 400

    # Generate a unique batch UUID for this upload request
    batch_uuid = str(uuid.uuid4())
    logging.info(f"Generated Batch UUID: {batch_uuid} for the image upload")

    # Store batch-level metadata in table1 (BatchUploads)
    firestore_data_table1 = {
        "UUID": batch_uuid,
        "JobStatus": "Pending",
        "emailSent": False,
        "imagesCount": len(files),  # Set to total number of images in the batch
        "email": email  # Add email to table1 metadata
    }
    save_to_firestore("BatchUploads", firestore_data_table1, doc_id=batch_uuid)  # Use batch_uuid as the PK

    response_data = []
    for image_file, image_metadata in zip(files, images_metadata):
        try:
            image_name = image_metadata.get('image_name', image_file.filename)
            filters = image_metadata.get('filters', [])

            # Upload each image to Google Cloud Storage
            image_url = upload_to_gcs(image_file, batch_uuid, image_name)

            # Save individual image metadata to Firestore table2 (ImageMetadata)
            doc_id = f"{batch_uuid}_{image_name}"  # Composite key (UUID + image_name)
            firestore_data_table2 = {
                "doc_id":doc_id,
                "UUID": batch_uuid,
                "ImageName": image_name,
                "FilterJson": filters,
                "IsProcessed": False
            }
            save_to_firestore("ImageMetadata", firestore_data_table2, doc_id=doc_id)  # Use composite key as the PK
            # save_to_firestore("ImageMetadata", firestore_data_table2)

            # Prepare response for each image upload
            response_data.append({
                "image_name": image_name,
                "uuid": batch_uuid,
                "status": "success",
                "image_url": image_url  # Optionally include the image URL
            })

        except Exception as e:
            logging.error(f"Error processing {image_file.filename}: {e}")
            response_data.append({
                "image_name": image_name,
                "uuid": batch_uuid,
                "status": "error"
            })

    return jsonify(response_data), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=image_port)
