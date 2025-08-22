import ast

class ASTSafetyAnalyzer(ast.NodeVisitor):
    def __init__(self, allowed_imports=None, allowed_calls=None):

        self.allowed_imports = allowed_imports or {'polars'}
        self.allowed_calls = allowed_calls or {
            'print', 'len', 'sum', 'min', 'max', 'abs', 'range',
            'read_csv',
            'DataFrame', 'select', 'filter', 'groupby', 'agg', 'join',
            'with_column', 'drop', 'sort', 'collect', 'to_pandas', 'to_numpy',
            'mean', 'median', 'std', 'var'
        }
        self.unsafe = []

    def visit_import(self, node):
        for alias in node.names:
            if alias.name not in self.allowed_imports:
                self.unsafe.append(f"Prohibited import: {alias.name}")

    def visit_importFrom(self, node):
        if node.module not in self.allowed_imports:
            self.unsafe.append(f"Prohibited import from module: {node.module}")

    def visit_call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in self.allowed_calls:
                self.unsafe.append(f"Prohibited function call: {func_name}")
        self.generic_visit(node)

    def analyze(self, code_string):
        self.unsafe = []
        tree = ast.parse(code_string)
        self.visit(tree)
        return not self.unsafe, self.unsafe