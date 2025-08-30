import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import autogen
import json
import os

# --- Define the request model for the API ---
class ChatRequest(BaseModel):
    prompt: str

# --- Create the FastAPI application ---
app = FastAPI()


# --- Enable Built-in CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------------


# --- Manually Load the Agent Team ---
# This function reads your JSON and builds the agents and team from scratch.
def load_team_manually(workflow_path: str):
    try:
        with open(workflow_path, 'r') as f:
            config = json.load(f)

        agent_list = []
        # Create each agent from the "participants" list in your JSON
        for agent_config in config["config"]["participants"]:
            agent = autogen.AssistantAgent(
                name=agent_config["config"]["name"],
                system_message=agent_config["config"]["system_message"],
                # Add other necessary configurations if needed
            )
            agent_list.append(agent)
        
        # Create the group chat configuration
        groupchat = autogen.GroupChat(
            agents=agent_list,
            messages=[],
            max_round=10
        )
        
        # Create the manager agent which orchestrates the team
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            name=config["config"]["admin_name"],
            # The manager also needs an LLM configuration
            llm_config={"config_list": [{"model": "gpt-4o-mini"}]}
        )
        
        print(f"✅ Team '{config['label']}' loaded manually with {len(agent_list)} agents.")
        return manager

    except Exception as e:
        print(f"❌ CRITICAL ERROR: Failed to manually load workflow from {workflow_path}.")
        print(f"   Error details: {e}")
        return None

# --- Correct file path with lowercase 'w' ---
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
       is_termination_msg=lambda x: True,
    )

    user_proxy.initiate_chat(team, message=request.prompt)
    
    final_message = team.chat_messages[user_proxy][-1]
    return {"response": final_message}

# --- This part makes the script runnable ---
if __name__ == "__main__":
    # Ensure your API key is set before running
    if not os.environ.get("OPENAI_API_KEY"):
        print("🔴 WARNING: OPENAI_API_KEY environment variable not set.")
    
    print("🚀 Starting API server for agent team...")
    uvicorn.run(app, host="0.0.0.0", port=8082)