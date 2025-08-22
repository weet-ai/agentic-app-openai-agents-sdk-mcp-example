from RestrictedPython import compile_restricted, safe_globals
import polars as pl

    

class RestrictedPythonExecutor:
    def __init__(self, allowed_globals=None):

        self.allowed_globals = allowed_globals or {
            'print': print,
            '_print_': print,
            '_getattr_': getattr,
            '_getitem_': lambda obj, key: obj[key],
            '_getiter_': iter,
            'polars': pl,
            'pl': pl,  # Add pl alias as well
        }

    def execute(self, code_string, extra_globals=None):
        
        # Reset print collector for each execution
        
        byte_code = compile_restricted(code_string, '<user_code>', 'exec')
        restricted_globals = safe_globals.copy()
        restricted_globals.update(self.allowed_globals)
        if extra_globals:
            restricted_globals.update(extra_globals)
        
        try:
            exec(byte_code, restricted_globals)
        except Exception as e:
            raise RuntimeError(f"Restricted code execution error: {e}")
        
        # Return both the globals and captured print output
        return {
            'globals': restricted_globals
        }