# ImageFlow: A Scalable Image Processing Application

ImageFlow is a cloud-native application designed to handle scalable image processing tasks efficiently. The system leverages modern technologies like Kubernetes, Google Cloud Platform (GCP), and React to provide a seamless user experience for uploading, modifying, and retrieving images.

## Table of Contents
- [Getting Started](#getting-started)
- [Frontend Setup](#frontend-setup)
- [Backend Deployment](#backend-deployment)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Troubleshooting](#troubleshooting)

## Getting Started

This project consists of two main components:
1. **Frontend**: A React-based user interface for image uploads and retrievals
2. **Backend**: A set of containerized services orchestrated using Kubernetes for processing, storing, and notifying users about their images

### Prerequisites

- [Node.js](https://nodejs.org/) installed on your machine
- [Docker](https://www.docker.com/) for containerization
- [kubectl](https://kubernetes.io/docs/tasks/tools/) for managing Kubernetes clusters
- Access to a GCP project using service account with Pub/Sub, Cloud Storage, and Firestore enabled

## Frontend Setup

Navigate to the frontend directory `frontend/image-processing-frontend` and follow the steps below:

### Install Dependencies

```bash
 npm install
```

This command installs all required Node.js packages for the frontend application.

### Run the Development Server

```bash
 npm start
```

This launches the app in development mode. Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

## Backend Deployment

Navigate to the backend directory and deploy the backend services locally or on a Kubernetes cluster (e.g., Google Kubernetes Engine).

### Run Kubernetes Deployment Script

From the backend folder, run the following script:

```bash
 ./scripts.sh
```

This script automates the setup of the required Kubernetes pods and services for the application.

## System Architecture

The architecture consists of two primary APIs: POST for image uploads and GET for retrieving processed images. Here's a detailed breakdown of each component:

1. **Image Handler Pod**
    - Manages image uploads and interactions with Google Cloud Storage
    - Stores uploaded images in UUID/input folders
    - Generates unique identifiers (UUID) for each upload
    - Communicates with Interaction Pod for further processing

2. **Interaction Manager Pod**
    - Handles service-to-service interactions and queue management
    - Retrieves image details from specified folders
    - Pushes data to Google Cloud Pub/Sub for processing
    - Manages processed image updates
    - Triggers email notifications through Email Notification Pub/Sub

3. **Image Processor Pod**
    - Processes images based on user requirements
    - Listens to Pub/Sub messages
    - Retrieves images from Cloud Storage
    - Stores processed images in UUID/output folders
    - Notifies Interaction Pod upon completion

4. **Image Processing Pub/Sub**
    - Queues batch-uploaded images for processing
    - Implements timeout mechanism to prevent duplicate processing
    - Manages message distribution to processor pods

5. **Email Notification Pub/Sub**
    - Receives completion notifications from Interaction Pod
    - Triggers Email Notification Cloud Function
    - Manages email notification queue

6. **Email Notification Cloud Function**
    - Triggered by Email Notification Pub/Sub
    - Sends email notifications to users
    - Includes UUID-based access links for processed images

7. **Dynamic Scaling**
    - Utilizes KEDA (Kubernetes Event-driven Autoscaling)
    - Scales Image Processor Pods based on Pub/Sub message volume
    - Optimizes resource utilization
    - Ensures efficient handling of varying workloads

## Technologies Used

### Software Components

* **Cloud Platforms**
    * Google Cloud Platform (GCP)
    * Amazon Web Services (AWS)

* **Storage Solutions**
    * Google Cloud Storage: Image storage (input/output)
    * AWS S3: Static website hosting

* **Messaging and Database**
    * Google Cloud Pub/Sub: Asynchronous component communication
    * Cloud Firestore: Metadata storage

* **Container Orchestration**
    * Kubernetes: Microservices management
    * KEDA: Event-driven autoscaling

* **Serverless**
    * Google Cloud Functions: Email notification handling

* **Backend Framework**
    * Flask: API endpoint implementation

* **Frontend Framework**
    * React: User interface development

