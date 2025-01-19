"""
This file aims to parse all the functions or methods of various programming languages and 
return a list of them. This is for the purpose of creating a list of functions that can be 
helpful for writing documentation or for any other purpose.
"""

from dataclasses import dataclass
from typing import List
import logging
import os

FILE_PATH_REPLACEMENT_ID = "FILE_PATH"
LANG_NAME_REPLACEMENT_ID = "LANG_NAME"
FUNC_BODY_REPLACEMENT_ID = "FUNC_BODY"


MD_TEMPLATE_BASE = \
f'''## File: {FILE_PATH_REPLACEMENT_ID}

### Functions/Methods

'''

MD_TEMPLATE_FUNC = \
f'''```{LANG_NAME_REPLACEMENT_ID}
{FUNC_BODY_REPLACEMENT_ID}
```

'''


def __parse_python_methods(file_path: str) -> List[str]:
    """
    This function parses the methods from a Python file and returns a list of methods.

    :param file_path: The path of the Python file.
    :return: A list of methods.
    """

    methods = []
    try:
        with open(file_path, "r") as file:
            text = file.read()
        
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}")
        raise e
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise e
    
    defs_occurences = []
    start_offset = 0
    while True:
        start = text.find("def ", start_offset)
        if start == -1:
            break
        
        defs_occurences.append(start)
        start_offset = start + 1
    
    alone_defs_occurences = []
    for i in range(len(defs_occurences)):
        if text[defs_occurences[i] - 1] in [" ", "\n", "\t"]:
            alone_defs_occurences.append(defs_occurences[i])
    
    for i in range(len(alone_defs_occurences)):
        start = alone_defs_occurences[i]
        next_start = alone_defs_occurences[i + 1] if i + 1 < len(alone_defs_occurences) else len(text)

        # find the first parenthesis
        open_parenthesis_index = text.find("(", start)
        # more cannot be found
        if open_parenthesis_index == -1:
            break
        # skip the ones that are not function definitions
        if open_parenthesis_index > next_start:
            continue

        arg_index = open_parenthesis_index + 1
        par_count = 1
        while par_count != 0 and arg_index < next_start:
            if text[arg_index] == "(":
                par_count += 1
            elif text[arg_index] == ")":
                par_count -= 1
            arg_index += 1
        
        close_parenthesis_index = arg_index - 1

        semi_colon_index = text.find(":", close_parenthesis_index)
        # more cannot be found
        if semi_colon_index == -1:
            break
        # skip the ones that are not function definitions
        if semi_colon_index > next_start:
            continue

        # check for docstring
        docstring_start_index = text.find('"""', close_parenthesis_index, next_start)
        # more cannot be found
        if docstring_start_index == -1:
            methods.append(text[start:semi_colon_index + 1])
            continue
        # skip the ones that could belong to the next function
        if docstring_start_index > next_start:
            methods.append(text[start:semi_colon_index + 1])
            continue

        docstring_end_index = text.find('"""', docstring_start_index + 3, next_start)
        # more cannot be found
        if docstring_end_index == -1:
            methods.append(text[start:semi_colon_index + 1])
            continue
        # skip the ones that could belong to the next function
        if docstring_end_index > next_start:
            methods.append(text[start:semi_colon_index + 1])
            continue

        methods.append(text[start:docstring_end_index + 3])

    return methods


def __parse_go_functions(file_path: str) -> List[str]:
    """
    This function parses the functions from a Go file and returns a list of functions.

    :param file_path: The path of the Go file.
    :return: A list of functions.
    """

    functions = []
    try:
        with open(file_path, "r") as file:
            text = file.read()
        
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}")
        raise e
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise e
    
    func_occurences = []
    start_offset = 0
    while True:
        start = text.find("func ", start_offset)
        if start == -1:
            break
        
        func_occurences.append(start)
        start_offset = start + 1
    
    alone_func_occurences = []
    for i in range(len(func_occurences)):
        if text[func_occurences[i] - 1] in [" ", "\n", "\t"]:
            alone_func_occurences.append(func_occurences[i])
    
    for i in range(len(alone_func_occurences)):
        prev_start = alone_func_occurences[i - 1] if i - 1 >= 0 else 0
        header_start = alone_func_occurences[i]
        next_start = alone_func_occurences[i + 1] if i + 1 < len(alone_func_occurences) else len(text)

        # find the first curly brace
        open_curly_brace_index = text.find("{", header_start)
        # more cannot be found
        if open_curly_brace_index == -1:
            break
        # skip the ones that are not function definitions
        if open_curly_brace_index > next_start:
            continue

        # extract the function name
        # from the open_curly_brace_index, go backwards to find the first '('
        open_parenthesis_index = open_curly_brace_index
        while open_parenthesis_index >= header_start:
            if text[open_parenthesis_index] == "(":
                if text[open_parenthesis_index - 1] in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_":
                    break
            open_parenthesis_index -= 1
        
        if open_parenthesis_index < header_start:
            logging.error("Function definition is not correct.")
            continue

        # extract the function name (find the first ' ' from open_parenthesis_index)
        function_name_start_index = open_parenthesis_index - 1
        while function_name_start_index >= header_start:
            if text[function_name_start_index] == " ":
                break
            function_name_start_index -= 1

        if function_name_start_index < header_start:
            logging.error("Function definition is not correct.")
            continue

        function_name = text[function_name_start_index + 1:open_parenthesis_index]

        # check for docstring
        docstring_start_index = text.find(f"// {function_name}", prev_start, next_start)
        # more cannot be found
        if docstring_start_index == -1:
            functions.append(text[header_start:open_curly_brace_index])
            continue
        # will be in bounds
        functions.append(text[docstring_start_index:open_curly_brace_index])

    return functions


@dataclass
class ProgrammingLanguage:
    """
    This class is used to represent the programming language name and the file extension of the language.
    """

    name: str
    file_extension: str
    md_id: str
    parse_functions: callable


LANGUAGES_MAPPING = {
    '.py': ProgrammingLanguage('Python', '.py', 'python', __parse_python_methods),
    '.go': ProgrammingLanguage('Go', '.go', 'go', __parse_go_functions),
}

def extract_all_files_path_from_roots(initial_roots: List[str]):
    """
    Extracts all the file paths from the given roots.

    :param initial_roots: The initial roots to start the search from.
    :type initial_roots: List[str]
    :return: A list of all the file paths.
    """
    
    all_file_paths = []
    roots = initial_roots

    while len(roots) > 0:
        root = roots.pop(0)
        for _, dirnames, filenames in os.walk(root):
            for filename in filenames:
                all_file_paths.append(os.path.join(root, filename))
            for dirname in dirnames:
                roots.append(os.path.join(root, dirname))
            break
    
    return all_file_paths


def main():
    # test the function
    client_root = "client"
    server_root = "server"

    all_files_client = extract_all_files_path_from_roots([client_root])
    all_files_server = extract_all_files_path_from_roots([server_root])
    all_files_client = sorted(all_files_client, key=lambda p: (p.count('/') + p.count('\\'), p))
    all_files_server = sorted(all_files_server, key=lambda p: (p.count('/') + p.count('\\'), p))

    # client files
    res_path = 'client_methods.md'
    with open(res_path, 'w') as file:
        file.write("# Client files:\n\n")
        for file_path in all_files_client:
            _, file_extension = os.path.splitext(file_path)
            if file_extension in LANGUAGES_MAPPING:
                language = LANGUAGES_MAPPING[file_extension]
                functions = language.parse_functions(file_path)
                file.write(MD_TEMPLATE_BASE.replace(FILE_PATH_REPLACEMENT_ID, file_path))
                for function in functions:
                    file.write(MD_TEMPLATE_FUNC.replace(LANG_NAME_REPLACEMENT_ID, language.md_id).replace(FUNC_BODY_REPLACEMENT_ID, function.strip().replace("\t", "    ")))

    # server files
    res_path = 'server_functions.md'
    with open(res_path, 'w') as file:
        file.write("# Server files:\n\n")
        for file_path in all_files_server:
            _, file_extension = os.path.splitext(file_path)
            if file_extension in LANGUAGES_MAPPING:
                language = LANGUAGES_MAPPING[file_extension]
                functions = language.parse_functions(file_path)
                file.write(MD_TEMPLATE_BASE.replace(FILE_PATH_REPLACEMENT_ID, file_path))
                for function in functions:
                    file.write(MD_TEMPLATE_FUNC.replace(LANG_NAME_REPLACEMENT_ID, language.md_id).replace(FUNC_BODY_REPLACEMENT_ID, function.strip().replace("\t", "    ")))

if __name__ == "__main__":
    main()