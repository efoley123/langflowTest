import os
import subprocess
import json
from langflow.load import run_flow_from_json
from astrapy import DataAPIClient
# Set the tweaks for the flow (if necessary)
TWEAKS = {
  "GitLoader-9r3EU": {}, #customize with relevent tweaks if needed
  "SplitText-pzSeX": {},
  "OpenAIEmbeddings-ZcvG7": {},
  "AstraDB-u1Mqb": {},
  "ChatInput-5fjVm": {}
}
# Initialize the Astra DB client
client = DataAPIClient("TOKEN")
db = client.get_database_by_api_endpoint(
    "https://bc670507-0f48-475e-a77f-ba441d664131-us-east-2.apps.astra.datastax.com"
)
# Collection name
COLLECTION_NAME = "mydb"
# Function to recreate the collection
def recreate_collection(collection_name: str):
    """
    Recreate the collection by deleting it if it exists and then creating a new one.
    """
    # Check if the collection exists
    if collection_name in db.list_collection_names():
        db.delete_collection(collection_name)
        print(f"Collection '{collection_name}' deleted.")
    else:
        print(f"Collection '{collection_name}' does not exist. Skipping deletion.")
    # Recreate the collection
    db.create_collection(collection_name)
    print(f"Recreated collection: {collection_name}. Ready to store updated data.")
# Function to get the Git repository path
def get_repo_path():
    try:
        # Get the current working directory
        cwd = os.getcwd()
        # Check if this directory is a Git repository by running 'git rev-parse --show-toplevel'
        repo_path = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=cwd).strip().decode('utf-8')
        return repo_path
    except subprocess.CalledProcessError:
        raise ValueError("This is not a Git repository.")
def main():
    try:
        # Recreate the collection in Astra DB
        recreate_collection(COLLECTION_NAME)
        # Get the repository path
        repo_path = get_repo_path()
        # Run the flow and send the repository path as input
        response = run_flow_from_json(flow="createVectordb.json", # Path to your flow definition
                            input_value=repo_path,# Send the repository path as input
                            session_id="", # Optional session ID
                            fallback_to_env_vars=True, # Use environment variables if necessary
                            tweaks=TWEAKS) # Optional tweaks to customize flow components
        # Print the response from the flow
        print(json.dumps(response, indent=2))
    except ValueError as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    main()