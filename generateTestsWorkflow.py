# file content input
#output the generated tests which should be the same one in generated tests. py

#generate tests workflow script: from langflow.load import run_flow_from_json
import sys
import logging
from langflow.load import run_flow_from_json
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
def generate_tests(file_content: str):
    """
    Run the LangFlow workflow using the provided file content as input.
    Args:
        file_content (str): The content of the file to be processed by the LangFlow workflow.
    Returns:
        str: The result of the LangFlow workflow execution.
    """
    # Define your tweaks
    TWEAKS = { # adjust as needed
  "ChatInput-2TMlO": {},
  "OpenAIEmbeddings-i7380": {},
  "AstraDB-mWWFP": {},
  "ParseData-WW2yc": {},
  "OpenAIModel-e95ZS": {},
  "ChatOutput-1FgzW": {},
  "Prompt-UULHU": {}
}
    try:
        # Run the workflow
        result = run_flow_from_json(flow="GenerateTests.json", # Path to your LangFlow workflow JSON file
                            input_value=file_content,  # Use file content as input for the workflow
                            session_id="", # Optional: provide a session ID if needed
                            fallback_to_env_vars=True, # Default: False
                            tweaks=TWEAKS)  # Pass the tweaks dictionary
        return result
    except Exception as e:
        logging.error(f"Error running LangFlow workflow: {e}")
        return None
if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("No file content provided as argument.")
        sys.exit(1)
    # Get the file content from command-line arguments
    file_content = sys.argv[1]
    # Run the workflow and print the result
    result = generate_tests(file_content)
    if result is not None:
        print(result)  # Output the result for the calling script
    else:
        sys.exit(1)