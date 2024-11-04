# Search Tool

This repository contains a Streamlit-based search tool that allows users to index and search metadata outputs. The tool is containerized using Docker for ease of deployment.

## Table of Contents
- [Getting Started](#getting-started)
- [Running with Docker](#running-with-docker)
- [Deploying with Minikube](#deploying-with-minikube)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

To run this tool, you'll need [Docker](https://www.docker.com/) installed. This guide assumes basic familiarity with Docker and, optionally, Kubernetes with Minikube for local testing.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- (Optional) [Minikube](https://minikube.sigs.k8s.io/docs/start/)

### Clone the Repository

```bash
git clone https://github.com/migrants-and-the-state/search-tool.git
cd search-tool
```

## Running with Docker

The following instructions will guide you through building and running the Docker container locally.

### 1. Build the Docker Image

First, build the Docker image using the provided `Dockerfile`.

```bash
docker build -t search-tool .
```

### 2. Run the Docker Container

Once the image is built, you can run it with the following command:

```bash
docker run -p 8501:8501 search-tool
```

This will start the Streamlit app on port 8501. You can access it by navigating to `http://localhost:8501` in your web browser.

## Deploying with Minikube

If you prefer to deploy the app in a local Kubernetes cluster using Minikube, follow these steps.

### 1. Start Minikube and Set Docker Environment

Start Minikube and configure your terminal to use Minikube's Docker daemon.

```bash
minikube start
eval $(minikube docker-env)
```

### 2. Build the Docker Image in Minikube's Environment

While still in the Minikube Docker environment, build the Docker image:

```bash
docker build -t search-tool .
```

### 3. Deploy the App to Minikube

Apply the Kubernetes deployment and service configurations:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### 4. Access the App

Use the following command to access the app through Minikube:

```bash
minikube service streamlit-service
```

This command will open your default browser to the Streamlit app running on Minikube.

