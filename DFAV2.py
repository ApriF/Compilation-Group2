def backward_data_flow_analysis(assembly_code):
    """
    Perform backward data flow analysis on the given assembly code.
    Adds comments indicating dependencies between variables, registers, and the heap.
    """
    lines = assembly_code.splitlines()
    dependencies = {}  # Dictionary to track dependencies for each variable/register
    commented_code = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("mov"):
            # Parse the destination and source
            parts = stripped_line.split()
            dest = parts[1].strip(",")
            src = parts[2]

            # Handle constant initialization
            if src.isdigit():  # If the source is a constant
                dependencies[dest] = set()  # Reset dependencies for the destination
            else:
                if dest not in dependencies:
                    dependencies[dest] = set()
                if src in dependencies:
                    dependencies[dest].update(dependencies[src])
                else:
                    dependencies[dest].add(src)

            # Add a comment about the dependencies
            comment = f" ; {dest}: {', '.join(dependencies[dest])}"
            commented_code.append(line + comment)

        elif stripped_line.startswith("push"):
            # Treat push as mov [heap], src
            parts = stripped_line.split()
            src = parts[1]
            if "heap" not in dependencies:
                dependencies["heap"] = set()
            if src in dependencies:
                dependencies["heap"].update(dependencies[src])
            else:
                dependencies["heap"].add(src)
            comment = f" ; heap: {', '.join(dependencies['heap'])}"
            commented_code.append(line + comment)

        elif stripped_line.startswith("pop"):
            # Skip commenting on pop rbp
            if "rbp" in stripped_line:
                commented_code.append(line)
                continue

            # Treat pop as mov dest, [heap]
            parts = stripped_line.split()
            dest = parts[1]
            if dest not in dependencies:
                dependencies[dest] = set()
            if "heap" in dependencies:
                dependencies[dest].update(dependencies["heap"])
            dependencies[dest].add("heap")
            comment = f" ; {dest}: {', '.join(dependencies[dest])}"
            commented_code.append(line + comment)

        elif stripped_line.startswith(("add", "sub", "mul", "cmp", "xor")):
            # Handle arithmetic operations, cmp (treated as sub), and xor (treated as add)
            parts = stripped_line.split()
            dest = parts[1].strip(",")
            src = parts[2]

            if dest not in dependencies:
                dependencies[dest] = set()
            if src in dependencies:
                dependencies[dest].update(dependencies[src])
            elif not src.isdigit():  # Skip constants like "0" from being added as dependencies
                dependencies[dest].add(src)

            # Add a comment about the dependencies
            comment = f" ; {dest}: {', '.join(dependencies[dest])}"
            commented_code.append(line + comment)

        elif stripped_line.startswith("call") and "printf" in stripped_line:
            # Highlight the dependencies of rax at the time of printf
            rax_dependencies = dependencies.get("rax", set())
            comment = f" ; printf: {', '.join(rax_dependencies) if rax_dependencies else 'rax'}"
            commented_code.append(line + comment)

        elif stripped_line.startswith("ret"):
            # Add a comment indicating ret returns the content of rax
            comment = " ; returns rax"
            commented_code.append(line + comment)

        else:
            # Preserve non-handled instructions without modification
            commented_code.append(line)

    return "\n".join(commented_code)


# Example usage
if __name__ == "__main__":
    with open("/home/kakouzz/Desktop/lark_bark/Compilation-Group2/simple.asm", "r") as f:
        assembly_code = f.read()

    commented_assembly = backward_data_flow_analysis(assembly_code)

    with open("/home/kakouzz/Desktop/lark_bark/Compilation-Group2/simple_commented.asm", "w") as f:
        f.write(commented_assembly)
