# KubeFlare Backend

A FastAPI-based backend service for the KubeFlare Kubernetes log viewer application.

## Features

- List Kubernetes namespaces, pods, and containers
- Fetch container logs
- Real-time log streaming via WebSocket
- CORS support for frontend integration
- Automatic Kubernetes configuration detection (in-cluster or local)

## Prerequisites

- Python 3.8 or higher
- Access to a Kubernetes cluster (local or remote)
- `kubectl` configured with proper cluster access

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/MacOS
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/MacOS
```

3. Install required packages:
```bash
pip install fastapi kubernetes uvicorn websockets
```

4. Create requirements.txt:
```bash
pip freeze > requirements.txt
```

Alternatively, install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Configuration

The application automatically detects and loads Kubernetes configuration:
- In-cluster configuration when running inside Kubernetes
- Local configuration (`~/.kube/config`) when running locally

## API Endpoints

- `GET /api/namespaces` - List all available namespaces
- `GET /api/pods?namespace={namespace}` - List all pods in a namespace
- `GET /api/containers?namespace={namespace}&pod={pod}` - List containers in a pod
- `GET /api/logs?namespace={namespace}&pod={pod}&container={container}&tail={tail}` - Fetch container logs
- `WebSocket /api/logs/stream` - Stream real-time logs

## Running the Application

Start the FastAPI server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Development

- The application uses FastAPI's automatic API documentation
- Access the API docs at `http://localhost:8000/docs`
- Access the alternative API docs at `http://localhost:8000/redoc`

## Security Notes

- The current CORS configuration allows all origins (`*`)
- For production, configure specific allowed origins in the CORS middleware
- Ensure proper Kubernetes RBAC permissions are set up

## License

This project is licensed under the MIT License.