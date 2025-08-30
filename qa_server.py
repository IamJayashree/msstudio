import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import autogen
import json
import os


# --- DEBUG: Print the API key to see what the container is receiving ---
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    # For security, we only print the start and end of the key
    print(f"✅ Found OPENAI_API_KEY. Starts with: '{api_key[:5]}', Ends with: '{api_key[-4:]}'")
else:
    print("❌ CRITICAL: OPENAI_API_KEY environment variable was not found inside the container.")
# -------------------------------------------------------------------


# --- Define the request model for the API ---
class ChatRequest(BaseModel):
    prompt: str

# --- Create the FastAPI application ---
app = FastAPI()

# --- NEW: Serve the index.html file ---
@app.get("/")
async def get_index():
    return FileResponse('index.html')

# --- Manually Load the Agent Team ---
def load_team_manually(workflow_path: str):
    try:
        with open(workflow_path, 'r') as f:
            config = json.load(f)

        # --- THIS IS THE CRITICAL FIX ---
        # Define the LLM configuration that will be given to each agent
        llm_config = {"config_list": [{"model": "gpt-4o-mini"}]}
        # --------------------------------

        agent_list = []
        for agent_config in config["config"]["participants"]:
            agent = autogen.AssistantAgent(
                name=agent_config["config"]["name"],
                system_message=agent_config["config"]["system_message"],
                llm_config=llm_config  # Give each agent a "brain"
            )
            agent_list.append(agent)
        
        groupchat = autogen.GroupChat(
            agents=agent_list,
            messages=[],
            max_round=12  # Increased max_round slightly for safety
        )
        
        # The manager also needs the LLM config to think
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            name=config["config"]["admin_name"],
            llm_config=llm_config
        )
        
        print(f"✅ Team '{config['label']}' loaded manually with {len(agent_list)} agents.")
        return manager

    except Exception as e:
        print(f"❌ CRITICAL ERROR: Failed to manually load workflow from {workflow_path}.")
        print(f"   Error details: {e}")
        return None

workflow_path = "./mydir/workflows/Core_Banking_Team.json"
team = load_team_manually(workflow_path)


# --- Define the API Endpoint ---
@app.post("/run")
async def run_chat(request: ChatRequest):
    if not team:
        return {"error": "The agent team is not loaded. Check server logs for errors."}

    user_proxy = autogen.UserProxyAgent(
       name="user_proxy",
       code_execution_config=False,
       human_input_mode="NEVER",
       # This new termination message check is more robust
       is_termination_msg=lambda x: "TERMINATE" in x.get("content", "").upper()
    )

    user_proxy.initiate_chat(team, message=request.prompt)
    
    # Get the second to last message, which is the final summary before "TERMINATE"
    final_message = team.groupchat.messages[-2]
    return {"response": final_message}

# --- This part makes the script runnable ---
if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("🔴 WARNING: OPENAI_API_KEY environment variable not set.")
    
    print("🚀 Starting single server for UI and API...")
    uvicorn.run(app, host="0.0.0.0", port=8082)