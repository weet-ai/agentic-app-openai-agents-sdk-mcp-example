#!/usr/bin/env python3

import ast
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from security.pipeline import SecureCodePipeline

def test_serialization():
    print("Testing serialization...")
    
    pipeline = SecureCodePipeline()
    
    # Test the exact code that was causing issues
    test_code = """
df = polars.DataFrame({"a": [1, 2, 3]})
print(df)
"""
    
    print(f"Executing code:\n{test_code}")
    
    try:
        result = pipeline.run(test_code)
        print(f"Result: {result}")
        print(f"Result type: {type(result)}")
        
        # Let's also debug what's in the AST
        tree = ast.parse(test_code)
        print(f"\nAST dump:")
        print(ast.dump(tree, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serialization()
