from fastapi import FastAPI, WebSocket
from kubernetes import client, config
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_k8s_config():
    """Load Kubernetes configuration (in-cluster or local)."""
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

@app.get("/api/namespaces")
def list_namespaces():
    """List all available namespaces."""
    load_k8s_config()
    v1 = client.CoreV1Api()
    namespaces = [ns.metadata.name for ns in v1.list_namespace().items]
    return {"namespaces": namespaces}

@app.get("/api/pods")
def list_pods(namespace: str):
    """List all pods in a given namespace."""
    load_k8s_config()
    v1 = client.CoreV1Api()
    pods = [pod.metadata.name for pod in v1.list_namespaced_pod(namespace).items]
    return {"pods": pods}

@app.get("/api/containers")
def list_containers(namespace: str, pod: str):
    """List all containers in a given pod."""
    load_k8s_config()
    v1 = client.CoreV1Api()
    pod_obj = v1.read_namespaced_pod(name=pod, namespace=namespace)
    containers = [container.name for container in pod_obj.spec.containers]
    return {"containers": containers}

@app.get("/api/logs")
def get_logs(namespace: str, pod: str, container: str, tail: int = 100):
    """Fetch logs from a specified pod and container."""
    load_k8s_config()
    v1 = client.CoreV1Api()
    logs = v1.read_namespaced_pod_log(name=pod, namespace=namespace, container=container, tail_lines=tail)
    return {"logs": logs}

@app.websocket("/api/logs/stream")
async def stream_logs(websocket: WebSocket, namespace: str, pod: str, container: str):
    """WebSocket for real-time log streaming."""
    await websocket.accept()
    load_k8s_config()
    v1 = client.CoreV1Api()
    
    w = client.Watch()
    for event in w.stream(v1.read_namespaced_pod_log, name=pod, namespace=namespace, container=container, follow=True):
        await websocket.send_text(event)
        await asyncio.sleep(0.1)

    await websocket.close()
    
# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app)
