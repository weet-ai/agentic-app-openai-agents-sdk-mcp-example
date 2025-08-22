import ast
from typing import Any, Dict

class ExecutionResultSerializer:
    """
    Simple serializer that follows Jupyter notebook behavior:
    - If the last line is a variable name, return its value
    - Otherwise, return None
    """
    
    def serialize_execution_result(self, code: str, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the executed code and return the result like Jupyter notebooks.
        
        Args:
            code: The original code that was executed
            execution_result: The execution result containing globals
            
        Returns:
            Dictionary containing the execution result
        """
        try:
            global_scope = execution_result['globals']
            print(f"[DEBUG SERIALIZER] Code: {repr(code)}")
            
            # Parse the code to get the last statement
            tree = ast.parse(code.strip())
            print(f"[DEBUG SERIALIZER] AST body length: {len(tree.body)}")
            
            # Check if the last statement is a simple variable name
            last_value = None
            if tree.body:
                last_stmt = tree.body[-1]
                print(f"[DEBUG SERIALIZER] Last statement type: {type(last_stmt)}")
                
                # If the last statement is an expression with a single Name node
                if isinstance(last_stmt, ast.Expr) and isinstance(last_stmt.value, ast.Name):
                    var_name = last_stmt.value.id
                    print(f"[DEBUG SERIALIZER] Found variable name: {var_name}")
                    if var_name in global_scope:
                        raw_value = global_scope[var_name]
                        print(f"[DEBUG SERIALIZER] Raw value type: {type(raw_value)}")
                        print(f"[DEBUG SERIALIZER] Raw value: {raw_value}")
                        last_value = self._serialize_value(raw_value)
                        print(f"[DEBUG SERIALIZER] Serialized value: {last_value}")
                    else:
                        print(f"[DEBUG SERIALIZER] Variable {var_name} not found in globals")
                else:
                    print(f"[DEBUG SERIALIZER] Last statement is not a simple variable name")
            
            result = {
                "status": "success",
                "result": last_value
            }
            print(f"[DEBUG SERIALIZER] Final result: {result}")
            return result
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
    
    def _serialize_value(self, value: Any) -> Any:
        """
        Convert a value to a JSON-serializable format.
        """
        print(f"[DEBUG SERIALIZER] _serialize_value called with type: {type(value)}")
        print(f"[DEBUG SERIALIZER] Value string representation: {str(value)[:200]}...")
        
        try:
            # Handle polars DataFrames
            if hasattr(value, '__class__') and 'polars' in str(type(value)):
                print(f"[DEBUG SERIALIZER] Detected polars DataFrame")
                if hasattr(value, 'to_dict'):
                    print(f"[DEBUG SERIALIZER] DataFrame has to_dict method")
                    data_dict = value.to_dict(as_series=False)
                    shape = value.shape
                    result = {
                        "type": "polars.DataFrame",
                        "data": data_dict,
                        "shape": shape
                    }
                    print(f"[DEBUG SERIALIZER] Serialized DataFrame: {result}")
                    return result
                else:
                    print(f"[DEBUG SERIALIZER] DataFrame missing to_dict method")
            else:
                print(f"[DEBUG SERIALIZER] Not a polars DataFrame")
            
            # Fallback for other types
            result = {
                "type": str(type(value).__name__),
                "value": str(value)
            }
            print(f"[DEBUG SERIALIZER] Fallback serialization: {result}")
            return result
            
        except Exception as e:
            print(f"[DEBUG SERIALIZER] Exception in _serialize_value: {e}")
            # Fallback to string representation
            return str(value)
