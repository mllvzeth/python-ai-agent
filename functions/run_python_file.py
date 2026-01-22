import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python files",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to run the python file",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="list of arguments",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)


def run_python_file(working_directory, file_path, args=None):
    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
    valid_target_file = (
        os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
    )

    if not valid_target_file:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not a regular file'

    if not target_file.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'

    command = ["python", target_file]

    if args:
        command.extend(args)
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, cwd=working_directory, timeout=30
        )
        return build_output_string(result)
    except subprocess.TimeoutExpired:
        return (
            "Process timed out after 30 seconds\nSTDERR: Timeout: Script exceeded limit"
        )
    except Exception as e:
        return f"Error: executing Python file: {e}"


def build_output_string(result):
    parts = []
    if result.returncode != 0:
        parts.append(f"Process exited with code {result.returncode}")
    if not result.stdout and not result.stderr:
        parts.append("No output produced")
    else:
        if result.stdout:
            parts.append(f"STDOUT: {result.stdout.rstrip()}")
        if result.stderr:
            parts.append(f"STDERR: {result.stderr.rstrip()}")
    return "\n".join(parts)
