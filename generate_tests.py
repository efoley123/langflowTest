import subprocess
import requests
import os
import sys
import logging
import json
from pathlib import Path
from requests.exceptions import RequestException
from typing import List, Optional, Dict, Any
# Set up logging
logging.basicConfig(
   level=logging.INFO,
   format='%(asctime)s - %(levelname)s - %(message)s'
)
class TestGenerator:
   def __init__(self):
       self.api_key = os.getenv('OPENAI_API_KEY')
       self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
       try:
           self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
       except ValueError:
           logging.error("Invalid value for OPENAI_MAX_TOKENS. Using default value: 2000")
           self.max_tokens = 2000
       if not self.api_key:
           raise ValueError("OPENAI_API_KEY environment variable is not set")
   def get_changed_files(self) -> List[str]:
       """Retrieve list of changed files passed as command-line arguments."""
       if len(sys.argv) <= 1:
           return []
       return [f.strip() for f in sys.argv[1].split() if f.strip()]
   def detect_language(self, file_name: str) -> str:
       """Detect programming language based on file extension."""
       extensions = {
           '.py': 'Python',
           '.js': 'JavaScript',
           '.ts': 'TypeScript',
           '.java': 'Java',
           '.cpp':'C++',
           '.cs': 'C#'
       }
       _, ext = os.path.splitext(file_name)
       return extensions.get(ext.lower(), 'Unknown')
   def create_prompt(self, file_name: str) -> Optional[str]:
       """Create a language-specific prompt for test generation."""
       try:
           with open(file_name, 'r') as f:
               code_content = f.read()
               return code_content
       except Exception as e:
           logging.error(f"Error reading file {file_name}: {e}")
           return None
   def save_test_cases(self, file_name: str, test_cases: str, language: str):
       """Save generated test cases to appropriate directory structure."""
       # Ensure the tests directory exists
       tests_dir = Path('generated_tests')
       tests_dir.mkdir(exist_ok=True)
       # Create language-specific subdirectory
       lang_dir = tests_dir / language.lower()
       lang_dir.mkdir(exist_ok=True)
       # Check if the file name already begins with 'test_', if not, prepend it
       base_name = Path(file_name).stem
       if not base_name.startswith("test_"):
           base_name = f"test_{base_name}"
       extension = '.js' if language == 'JavaScript' else Path(file_name).suffix
       test_file = lang_dir / f"{base_name}{extension}"
       # Decide the mode - 'a' for append, 'w' for overwrite
       file_mode = 'w'  # Change to 'a' if you want to append to existing tests
       try:
           with open(test_file, file_mode, encoding='utf-8') as f:
               f.write(test_cases)
           logging.info(f"Test cases saved to {test_file}")
       except Exception as e:
           logging.error(f"Error saving test cases to {test_file}: {e}")
       if test_file.exists():
           logging.info(f"File {test_file} exists with size {test_file.stat().st_size} bytes.")
       else:
           logging.error(f"File {test_file} was not created.")
   def generate_tests_with_workflow(self, file_content):
        """Calls the generateTestsWorkflow.py file to generate test cases."""
        try:
            result = subprocess.run(
                ["python", "generateTestsWorkflow.py", file_content],
                capture_output=True,
                text=True,
                check=True
            )
            logging.info("Test workflow executed successfully.")
            return result.stdout  # Return the generated test cases
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to execute test workflow: {e.stderr}")
            return None
   def update_database(self, file_name, file_content):
        """Calls the updateDB.py file to update the database."""
        try:
            result = subprocess.run(
                ["python", "updateDB.py"],
                capture_output=True,
                text=True,
                check=True
            )
            logging.info(f"Database updated successfully for {file_name}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to update database for {file_name}: {e.stderr}")
   def run(self):
       """Main execution method."""
       changed_files = self.get_changed_files()
       if not changed_files:
           logging.info("No files changed.")
           return
       for file_name in changed_files:
           try:
               #get file content
               fileContent = self.create_prompt(file_name)
               language = self.detect_language(file_name)
               if fileContent:
                  #call the updateDB.py file
                  self.update_database(file_name, fileContent)
                  #call another file that will call the workflow that actually generates tests, send that file the fileContent variable as an argument-- still needs to be made
                  #the second file should return the tests made, make that equal to the test cases variable
                  test_cases = self.generate_tests_with_workflow(fileContent)
                  if test_cases:
                       test_cases = test_cases.replace("“", '"').replace("”", '"')
                       self.save_test_cases(file_name, test_cases, language)
                  else:
                       logging.error(f"Failed to generate test cases for {file_name}")
           except Exception as e:
               logging.error(f"Error processing {file_name}: {e}")
if __name__ == '__main__':
   try:
       generator = TestGenerator()
       generator.run()
   except Exception as e:
       logging.error(f"Fatal error: {e}")
       sys.exit(1)






