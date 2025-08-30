import autogen
import json

# The path to your workflow file.
# Make sure this path is correct.
workflow_path = "./mydir/workflows/Core_Banking_Team.json"

print(f"Attempting to load workflow from: {workflow_path}")

try:
    # Use autogen's built-in load function
    team, _ = autogen.load(workflow_path)
    
    # If successful, print the names of the agents that were loaded
    print("\n✅ SUCCESS: Workflow loaded without errors.")
    print("Agents found in team:")
    for agent in team.agents:
        print(f"- {agent.name}")

except Exception as e:
    # If there is any error, print it
    print(f"\n❌ FAILED: Found an error in the workflow file.")
    print("-------------------------------------------------")
    print(f"ERROR DETAILS: {e}")
    print("-------------------------------------------------")
    print("Please fix this error in your Core_Banking_Team.json file and try again.")