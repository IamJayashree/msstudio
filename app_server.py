from fastapi import FastAPI, Body
from autogenstudio import WorkflowManager

# Initialize the workflow manager with your exported JSON workflow
workflow_manager = WorkflowManager(
    workflow="./mydir/workflows/Core_Banking_Team.json"
)

app = FastAPI()

@app.post("/bfsi/{task}")
async def run_task_post(task: str, payload: dict = Body(...)):
    """
    Run a task on your workflow using the payload.
    'task' is descriptive, but WorkflowManager.run takes a 'message' string.
    You can either combine both or just pass payload.
    """
    message = payload.get("message") or f"{task}: {payload}"
    # Run synchronously — may not need 'await' depending on API implementation
    result = workflow_manager.run(message=message)
    return {"task": task, "result": result}
