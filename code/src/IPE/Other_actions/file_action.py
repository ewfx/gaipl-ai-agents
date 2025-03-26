from typing import Dict
import shutil
import os
from pathlib import Path
import logging
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileCopyTool:
    @staticmethod
    def copy_file(source: str, destination: str) -> Dict[str, str]:
        """Copy file from source to destination"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)

            # Validate source file exists
            if not source_path.is_file():
                return {"status": "failed", "message": f"Source file does not exist: {source_path}"}

            # Create destination directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            return {
                "status": "success", 
                "message": f"File copied successfully from {source_path} to {dest_path}"
            }
        
        except Exception as e:
            logger.error(f"File copy error: {str(e)}")
            return {"status": "failed", "message": f"Error copying file: {str(e)}"}

class FileOperationAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("groq_api_key"),
            model="llama3-70b-8192",
            temperature=0
        )
        self.copy_tool = FileCopyTool()

    def extract_paths_from_llm(self, text: str) -> Dict[str, str]:
        """Use LLM to extract source and destination paths from text"""
        try:
            prompt = f"""
            Extract the source and destination paths from this command.
            Respond ONLY with the two full paths separated by a pipe symbol (|).
            Include the filename in both paths.
            Do not include any other text or explanations.

            Example command:
            "copy and paste the test.txt file from location C:\\path1 to C:\\path2"
            Example response:
            C:\\path1\\test.txt|C:\\path2\\test.txt

            Command: {text}
            """
            
            response = self.llm.invoke(prompt)
            paths = response.content.strip().split('|')
            
            if len(paths) != 2:
                return {
                    "status": "failed", 
                    "message": "Could not extract valid source and destination paths"
                }

            source = paths[0].strip()
            destination = paths[1].strip()

            # Basic validation of extracted paths
            if not source or not destination:
                return {"status": "failed", "message": "Empty paths extracted"}

            return {
                "status": "success",
                "source": source,
                "destination": destination
            }

        except Exception as e:
            logger.error(f"LLM path extraction failed: {str(e)}")
            return {"status": "failed", "message": f"Error extracting paths: {str(e)}"}

    def process_command(self, command: str) -> str:
        """Process the command and execute file operation"""
        try:
            # Validate command format
            if not command.startswith("[run]:"):
                return "Invalid command format. Use: [run]: <your command>"

            # Extract the actual text after [run]:
            text = command[6:].strip()

            # Get paths from LLM
            paths_result = self.extract_paths_from_llm(text)
            if paths_result["status"] == "failed":
                return paths_result["message"]

            logger.info(f"Extracted source: {paths_result['source']}")
            logger.info(f"Extracted destination: {paths_result['destination']}")

            # Execute file copy
            copy_result = self.copy_tool.copy_file(
                paths_result["source"],
                paths_result["destination"]
            )

            return copy_result["message"]

        except Exception as e:
            logger.error(f"Command processing failed: {str(e)}")
            return f"Error processing command: {str(e)}"
