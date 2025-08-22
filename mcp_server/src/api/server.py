from fastmcp import FastMCP
import glob
from typing import List
import os
from src.security.pipeline import SecureCodePipeline
import logging

logging.basicConfig(level = "DEBUG")

TRANSPORT = os.getenv("TRANSPORT", "http")
mcp = FastMCP("Data Analysis MCP Server")

@mcp.tool
async def get_file_context(path: str, extension: str = "csv") -> List[dict]:
    """
        Reads files with the target extension and tries to fetch its headers.

        Args:
            path (str): The file path to read.
            extension (str, optional): The file extension to filter by. Defaults to "csv".

        Returns:
            List[dict]: A list of dictionaries containing the file headers.
            Example:
                [
                    {"file": "employees.csv", "headers": ["name", "salary"]},
                    {"file": "weather.csv", "headers": ["location", "degrees", "date"]}
                ]
        Raises:
            FileNotFoundError: If the path is not found or has no files.
    """

    headers = []
    file_list = glob.glob(f"{path}/*.{extension}")

    if not file_list:
        raise FileNotFoundError(f"No files found in {path} with extension {extension}")
    
    for file in file_list:
        with open(file, "r") as f:
            headers = f.readline().strip().split(",")
            headers.append({"file": file, "headers": headers})

    return headers

@mcp.tool
async def code_executor(code: str):
    """
        Executes user-provided code in a restricted environment.

        Args:
            code (str): The user-provided code to execute.
        Returns:
            dict: The result of the executed code or an error message.
    """
    print(f"[DEBUG] code_executor called with code: {repr(code)}")
    
    try:
        pipeline = SecureCodePipeline()
        result = pipeline.run(code)
        logging.info(f"[DEBUG] Pipeline result: {result}")
        logging.info(f"[DEBUG] Pipeline result type: {type(result)}")
        return result
    except Exception as e:
        logging.info(f"[DEBUG] Exception in code_executor: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    mcp.run(transport=TRANSPORT, host="0.0.0.0", port=8000)

