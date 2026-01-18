import os

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    working_dir_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
    valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs

    if  not valid_target_dir:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'

    files_list = []

    try:

        with os.scandir(target_dir) as entries:
            for entry in entries:
                size = os.path.getsize(entry.path)
                check_dir = entry.is_dir()
                files_list.append(f'- {entry.name}: file_size={size} bytes, is_dir={check_dir}')
        return '\n'.join(files_list)

    except Exception as e:
        print(f'Error: {e}') 


