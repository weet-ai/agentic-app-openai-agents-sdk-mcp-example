from fastmcp import FastMCP
from typing import List
import os
from src.security.pipeline import SecureCodePipeline
import logging
import pathlib
import os



logging.basicConfig(level = "DEBUG")

MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "http")

mcp = FastMCP("Data Analysis MCP Server")

@mcp.tool
async def get_file_context(path: str = "./data", extension: str = "csv") -> List[dict]:
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

    file_headers = []
    path = pathlib.Path(path)
    logging.info(f"Looking for files in {path} with extension {extension}")
    file_list = [f for f in os.listdir(path) if f.endswith(f".{extension}")]
    logging.info(f"Found files: {file_list}")

    if len(file_list) == 0:
        logging.warning(f"No files found in {path} with extension {extension}")

    for file in file_list:
        with open(os.path.join(path, file), "r") as f:
            headers = f.readline().strip().split(",")
            file_headers.append({"file": file, "headers": headers})

    logging.info(f"File headers found: {file_headers}")
    return file_headers

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
    
    # Simply run without the middleware for now
    # The ProxyHeadersMiddleware is mainly needed when behind a reverse proxy
    # Since we're handling TLS termination at NGINX level, we can skip this
    mcp.run(transport=MCP_TRANSPORT, host="0.0.0.0", port=8000)

