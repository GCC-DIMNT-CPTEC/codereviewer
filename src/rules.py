import os

def check_implicit_none(node,line_number) -> str:
    content = node.get('content', '').lower()
    print(content)
    if 'implicit none' in content:
        return None
    return "'implicit none' is missing in line \n'."

def check_lowercase(node,line_number) -> str:
    content = node.get('content', '')
    if content != content.lower():
       if "mod" not in content:
          return f"Uppercase found in line '{line_number}'\n.: '{content}\n'."
    return None

def check_variable_declaration(node,line_number) -> str:
    content = node.get('content', '').lower()
    if ('real' in content or 'integer' in content) and '::' not in content:
        return f"Missing '::' in variable declaration in line '{line_number}'\n." #: '{node.get('content', '')}'."
    return None

def check_obsolete_clauses(node,line_number) -> str:
    content = node.get('content', '').lower()
    obsolete_clauses = ['common', 'equivalence', 'dimension']
    for  line_number, clause in enumerate(obsolete_clauses, start=1):
        if clause in content:
            return f" '{clause}' found in line '{line_number}'\n."#: '{node.get('content', '')}'."
    return None

def check_undeclared_variables(nodes,line_number) -> str:
    declared_vars = set()
    used_vars = set()

    for line_number, node in enumerate(nodes, start=1):
        content = node.get('content', '').lower()
        if '::' in content:
            parts = content.split('::')
            if len(parts) > 1:
                vars_declared = parts[1].split(',')
                for var in vars_declared:
                    declared_vars.add(var.strip())
        else:
            words = content.split()
            for word in words:
                if word.isidentifier() and word not in declared_vars: 
                    used_vars.add(word)

    undeclared_vars = used_vars - declared_vars
    if undeclared_vars:
        return f"Undeclared variables found in line '{line_number}'\n." #: {', '.join(undeclared_vars)}"
    return None

def check_file_extension(file_path) -> str:
    valid_extensions = ['.f90', '.f95', '.f03', '.f08', '.f', '.for', '.f77']
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in valid_extensions:
        return f"Invalid file extension: '{ext}'. Valid extensions are: {', '.join(valid_extensions)}"
    return None

def check_indentation(fortran_code) -> str:
    lines = fortran_code.split("\n")
    line_n = 1
    n_spaces = 4
    errors=""
    for line in lines:    
        #print (f"'{line.strip()}")
        # print (f"'{line.strip()}'")
        line_without_spaces = line.replace(" ", "")
        if line.startswith(" ") and f"'{line_without_spaces}'" != "''" and (len(line) - len(line.lstrip(" "))) % n_spaces != 0:
            #print (f"'{line.strip()} '-' {line_n}")
            # print (f"'{line_without_spaces}'")
            errors = errors + f"Indentation error in line '{line_n}' \n "
        line_n = line_n + 1
    if errors != "":
        #print(errors)
        return errors
    return None
