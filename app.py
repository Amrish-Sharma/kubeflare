from fastapi import FastAPI, WebSocket, HTTPException, Query
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import asyncio
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="KubeFlare API",
    description="API for viewing Kubernetes logs",
    version="1.0.0"
)

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
        logger.info("Loaded in-cluster configuration")
    except config.ConfigException:
        config.load_kube_config()
        logger.info("Loaded local kube configuration")

@app.get("/")
def welcome():
    return {"message": "Welcome to KubeFlare API"}

@app.get("/api/namespaces", tags=["kubernetes"])
async def list_namespaces():
    """List all available namespaces."""
    try:
        load_k8s_config()
        v1 = client.CoreV1Api()
        namespaces = [ns.metadata.name for ns in v1.list_namespace().items]
        return {"namespaces": namespaces}
    except ApiException as e:
        logger.error(f"Error fetching namespaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pods", tags=["kubernetes"])
async def list_pods(namespace: str = Query(..., description="Kubernetes namespace")):
    """List all pods in a given namespace."""
    try:
        load_k8s_config()
        v1 = client.CoreV1Api()
        pods = [pod.metadata.name for pod in v1.list_namespaced_pod(namespace).items]
        return {"pods": pods}
    except ApiException as e:
        logger.error(f"Error fetching pods: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/containers", tags=["kubernetes"])
async def list_containers(
    namespace: str = Query(..., description="Kubernetes namespace"),
    pod: str = Query(..., description="Pod name")
):
    """List all containers in a given pod."""
    try:
        load_k8s_config()
        v1 = client.CoreV1Api()
        pod_obj = v1.read_namespaced_pod(name=pod, namespace=namespace)
        containers = [container.name for container in pod_obj.spec.containers]
        return {"containers": containers}
    except ApiException as e:
        logger.error(f"Error fetching containers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs", tags=["kubernetes"])
async def get_logs(
    namespace: str = Query(..., description="Kubernetes namespace"),
    pod: str = Query(..., description="Pod name"),
    container: str = Query(..., description="Container name"),
    tail: Optional[int] = Query(100, description="Number of lines to return")
):
    """Fetch logs from a specified pod and container."""
    try:
        load_k8s_config()
        v1 = client.CoreV1Api()
        logs = v1.read_namespaced_pod_log(
            name=pod,
            namespace=namespace,
            container=container,
            tail_lines=tail
        )
        return {"logs": logs}
    except ApiException as e:
        logger.error(f"Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/api/logs/stream")
async def stream_logs(
    websocket: WebSocket,
    namespace: str,
    pod: str,
    container: str
):
    """WebSocket for real-time log streaming."""
    try:
        await websocket.accept()
        load_k8s_config()
        v1 = client.CoreV1Api()
        
        w = watch.Watch()
        for event in w.stream(
            v1.read_namespaced_pod_log,
            name=pod,
            namespace=namespace,
            container=container,
            follow=True
        ):
            await websocket.send_text(event)
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in websocket connection: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        port=8000,
        reload=True,
        log_level="info"
    )