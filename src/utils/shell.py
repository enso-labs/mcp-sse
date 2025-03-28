import subprocess

def tool_shell_command(command: str) -> str:
    """Execute a shell command"""
    return subprocess.check_output(command, shell=True).decode()