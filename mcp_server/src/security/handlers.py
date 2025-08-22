class PrintCollector:
    def __init__(self):
        self.output = []
    
    def write(self, text):
        self.output.append(str(text))
    
    def __call__(self, *args, **kwargs):
        # Handle print function calls
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        text = sep.join(str(arg) for arg in args) + end
        self.output.append(text)
    
    def get_output(self):
        return ''.join(self.output)

def print_handler(*args, **kwargs):
    # This is the old handler that raises an error
    raise RuntimeError(f"🚨 An attempt to run `print` was detected with args: {args} and kwargs: {kwargs}")