import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from fastapi.responses import FileResponse

from orchestrator.engine import OrchestrationEngine
from orchestrator.nodes import * # Import all our node classes



# --- Data Models for API requests ---
class WorkflowDefinition(BaseModel):
    name: str
    start_at: str
    nodes: dict

# --- In-Memory Storage (for simplicity in this MVP) ---
# A real system would use a database like PostgreSQL
workflow_definitions = {} 

# --- Node Registry ---
NODE_REGISTRY = {
    "StartNode": StartNode,
    "GetUserDataNode": GetUserDataNode,
    "RouteUserByTypeNode": RouteUserByTypeNode,
    "EscalateToPremiumSupportNode": EscalateToPremiumSupportNode,
    "ProcessStandardUserNode": ProcessStandardUserNode,
    "SendWelcomeEmailNode": SendWelcomeEmailNode,
    "EndNode": Endnode,
}
# --- Initialize FastAPI App ---
app = FastAPI(title="Agentic Orchestrator API")

# We need a single, long-running engine instance
engine = None

@app.on_event("startup")
async def startup_event():
    """On server startup, create the engine and a worker task."""
    global engine
    # A dummy workflow is needed to initialize the engine, it will be replaced
    dummy_workflow = {'name': 'dummy', 'start_at': '', 'nodes': {}}
    engine = OrchestrationEngine(dummy_workflow, NODE_REGISTRY)
    asyncio.create_task(engine.worker())

# --- API Endpoints ---

@app.post("/workflow")
async def create_workflow(workflow_def: WorkflowDefinition):
    """Saves a new workflow definition."""
    workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
    workflow_definitions[workflow_id] = workflow_def.dict()
    return {"workflow_id": workflow_id, "message": "Workflow saved successfully."}

@app.post("/workflow/{workflow_id}/run")
async def run_workflow(workflow_id: str):
    """Starts a new run of a defined workflow."""
    if workflow_id not in workflow_definitions:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    
    # Set the engine's definition to the one we want to run
    engine.workflow_def = workflow_definitions[workflow_id]
    engine.nodes = engine._initialize_nodes() # Re-initialize nodes for this workflow

    run_id = str(uuid.uuid4())
    await engine.start_workflow(run_id, {"source": "api_trigger"})
    return {"run_id": run_id}

@app.get("/run/{run_id}/status")
async def get_run_status(run_id: str):
    """Retrieves the current state of a workflow run."""
    state = engine.state_manager.get_state(run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found.")
    return state

@app.get("/")
async def read_index():
    """Serves the main HTML page."""
    return FileResponse('index.html')