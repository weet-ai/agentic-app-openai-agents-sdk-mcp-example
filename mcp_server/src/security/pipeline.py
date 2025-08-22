from src.security.analyzer import ASTSafetyAnalyzer
from src.security.restricted_executor import RestrictedPythonExecutor
from src.security.serialization import ExecutionResultSerializer
import logging

class SecureCodePipeline:
    def __init__(self, allowed_imports=None, allowed_calls=None, allowed_globals=None):
        self.ast_analyzer = ASTSafetyAnalyzer(allowed_imports, allowed_calls)
        self.executor = RestrictedPythonExecutor(allowed_globals)
        self.serializer = ExecutionResultSerializer()

    def run(self, code_string, extra_globals=None):
        
        # Step 1: AST static analysis
        safe, issues = self.ast_analyzer.analyze(code_string)
        if not safe:
            raise ValueError(f"Unsafe code detected: {issues}")
        
        # Step 2 (optional): Execute in restricted environment
        #execution_result = self.executor.execute(code_string, extra_globals)
        #logging.info(f"Execution result: {execution_result}")

        # Execute the code and capture result
        execution_globals = self.executor.allowed_globals.copy()
        exec(code_string, execution_globals)
        
        # Get the last variable assignment as result (assuming last line is the result)
        result = None
        if code_string.strip().split('\n')[-1].strip() and not code_string.strip().split('\n')[-1].strip().startswith('#'):
            last_line = code_string.strip().split('\n')[-1].strip()
            if '=' not in last_line:  # If last line is just a variable name
                try:
                    result = eval(last_line, execution_globals)
                except:
                    result = None
        
        execution_result = {'result': result, 'globals': execution_globals}
        
        # Step 3: Serialize the execution results
        serialized_result = self.serializer.serialize_execution_result(code_string, execution_result)

        logging.info(f"Serialized result: {serialized_result}")
        
        return serialized_result