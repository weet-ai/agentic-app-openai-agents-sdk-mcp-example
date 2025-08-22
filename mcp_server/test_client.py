#!/usr/bin/env python3
"""Simple test to simulate the MCP server code_executor function"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.security.pipeline import SecureCodePipeline

def simulate_code_executor(code: str):
    """Simulate what the code_executor function should do"""
    
    print(f"[DEBUG] code_executor called with code: {repr(code)}")
    
    try:
        pipeline = SecureCodePipeline()
        result = pipeline.run(code)
        print(f"[DEBUG] Pipeline result: {result}")
        print(f"[DEBUG] Pipeline result type: {type(result)}")
        return result
    except Exception as e:
        print(f"[DEBUG] Exception in code_executor: {e}")
        return {"status": "error", "message": str(e)}

def test_code_executor():
    """Test the code_executor function simulation"""
    
    test_code = '''df = polars.DataFrame({"a": [1, 2, 3]})
df'''
    
    print(f"Testing code_executor with: {repr(test_code)}")
    print("-" * 50)
    
    result = simulate_code_executor(test_code)
    print(f"Final result: {result}")
    print(f"Final result type: {type(result)}")
    print(f"Result as JSON:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_code_executor())
