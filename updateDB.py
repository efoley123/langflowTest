import os
import subprocess
import json
import asyncio
from langflow.load import run_flow_from_json
from astrapy import DataAPIClient, AsyncCollection
import logging
import sys
import nest_asyncio
nest_asyncio.apply() #this helped with an error for loop is already
# Set the tweaks for the flow (if necessary)
TWEAKS = {
    "GitLoader-9r3EU": {},  # Customize with relevant tweaks if needed
    "SplitText-pzSeX": {},
    "OpenAIEmbeddings-ZcvG7": {},
    "AstraDB-u1Mqb": {
        "session_id": "1234",  # Random numbers
        "sender": "User",
        "sender_name": "User"
    },
    "ChatInput-5fjVm": {}
}

# Initialize the Astra DB client
client = DataAPIClient("TOKEN")
db = client.get_database_by_api_endpoint("https://c245e63a-73a2-45c6-96ab-862eaacf7f2d-us-east-2.apps.astra.datastax.com")

COLLECTION_NAME = "collection1"  # Collection name

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
        #await collection.delete_all()  # Deletes all in the collection
        await collection.delete_many({})
        # Get the repository path
        repo_path = get_repo_path()

        print(f"Repository Path: {repo_path}")
        logging.info(f"Here it is {repo_path}")
        
        # Run the flow and send the repository path as input
        response = await run_flow_from_json(
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
    try:
        # Check if there's an already running event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # If loop is already running (e.g., interactive environments), use `asyncio.ensure_future`
        if loop.is_running():
            task = asyncio.ensure_future(main())
            # Await the task using `add_done_callback` to handle it properly
            task.add_done_callback(lambda fut: print("Task finished!"))
        else:
            # Run the main coroutine
            loop.run_until_complete(main())
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)