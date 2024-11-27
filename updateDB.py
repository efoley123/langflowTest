import os
import subprocess
import json
import asyncio
from langflow.load import run_flow_from_json
from astrapy import DataAPIClient, AsyncCollection

# Set the tweaks for the flow (if necessary)
TWEAKS = {
    "GitLoader-9r3EU": {},  # Customize with relevant tweaks if needed
    "SplitText-pzSeX": {},
    "OpenAIEmbeddings-ZcvG7": {},
    "AstraDB-u1Mqb": {
        "session_id": "1234",
        "sender": "User",
        "sender_name": "User"
    },
    "ChatInput-5fjVm": {}
}

# Initialize the Astra DB client
client = DataAPIClient("Your_TOKEN_HERE")
db = client.get_database_by_api_endpoint(
    "https://bc670507-0f48-475e-a77f-ba441d664131-us-east-2.apps.astra.datastax.com"
)

# Collection name
COLLECTION_NAME = "mydb"

# Function to get the Git repository path
def get_repo_path():
    try:
        # Get the current working directory
        cwd = os.getcwd()
        # Check if this directory is a Git repository
        repo_path = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'], cwd=cwd
        ).strip().decode('utf-8')
        return repo_path
    except subprocess.CalledProcessError:
        raise ValueError("This is not a Git repository.")

# Main function
async def main():
    try:
        # Delete everything inside the collection
        collection = AsyncCollection(database=db, name=COLLECTION_NAME)
        await collection.delete_many({})  # Use an empty filter to delete all documents
        # Get the repository path
        repo_path = get_repo_path()
        
        # Run the flow and send the repository path as input
        response = run_flow_from_json(
            flow="createVectordb.json",  # Path to your flow definition
            input_value=repo_path,  # Send the repository path as input
            fallback_to_env_vars=True,  # Use environment variables if necessary
            tweaks=TWEAKS  # Optional tweaks to customize flow components
        )
        
        # Print the response from the flow
        print(json.dumps(response, indent=2))
    except ValueError as e:
        print(f"Error: {e}")

# Run the script
if __name__ == "__main__":
    asyncio.run(main())