from e2b_code_interpreter import Sandbox

def run_code(code: str) -> str:
    """Run code in the e2b code interpreter"""
    with Sandbox() as sandbox:
        execute = sandbox.run_code(code)
        return execute.to_json()