def data_flow_analysis(asm_code):
    """
    Perform Data Flow Analysis on the given assembly code.
    Returns the assembly code with comments indicating variable and register dependencies and values.
    """
    dependencies = {}  # Dictionary to track dependencies for each variable/register
    values = {}  # Dictionary to track constant values for registers/variables
    heap = []  # Simulate the heap for push/pop operations
    commented_code = []

    for line in asm_code.splitlines():
        stripped_line = line.strip()
        print(f"Processing line: {stripped_line}")  # Debugging output
        if stripped_line.startswith("mov"):
            # Parse the instruction
            parts = stripped_line.split()
            dest = parts[1].strip(",")  # Destination register/variable
            src = parts[2]  # Source register/variable or constant

            # Handle constant initialization
            if src.isdigit():
                values[dest] = int(src)
                dependencies[dest] = set()
                commented_code.append(f"{line} ; {dest}={src}, {dest}:[]")
            else:
                # Update dependencies
                values.pop(dest, None)  # Clear constant value if overwritten
                if dest not in dependencies:
                    dependencies[dest] = set()
                if src in dependencies:
                    dependencies[dest].update(dependencies[src])
                dependencies[dest].add(src)
                commented_code.append(f"{line} ; {dest}:{list(dependencies[dest])}")

        elif stripped_line.startswith("push"):
            # Simulate push operation
            parts = stripped_line.split()
            src = parts[1]  # Source register/variable
            heap.append(src)
            if src in dependencies:
                heap.extend(dependencies[src])  # Track dependencies in the heap
            commented_code.append(f"{line} ; heap: {heap}")

        elif stripped_line.startswith("pop"):
            # Simulate pop operation
            parts = stripped_line.split()
            dest = parts[1]  # Destination register/variable
            if heap:
                src = heap.pop()
                values.pop(dest, None)  # Clear constant value if overwritten
                if dest not in dependencies:
                    dependencies[dest] = set()
                dependencies[dest].add(src)
                if src in dependencies:
                    dependencies[dest].update(dependencies[src])
            commented_code.append(f"{line} ; {dest}:{list(dependencies[dest])}")

        elif stripped_line.startswith(("add", "sub", "mul", "cmp")):
            # Handle arithmetic and comparison instructions
            parts = stripped_line.split()
            dest = parts[1].strip(",")  # Destination register/variable
            src = parts[2]  # Source register/variable or constant

            if src.isdigit():
                # Update constant value if dest is a constant
                if dest in values:
                    if stripped_line.startswith("add"):
                        values[dest] += int(src)
                    elif stripped_line.startswith("sub") or stripped_line.startswith("cmp"):
                        values[dest] -= int(src)
                    commented_code.append(f"{line} ; {dest}={values[dest]}, {dest}:[]")
                else:
                    commented_code.append(f"{line} ; {dest}:{list(dependencies.get(dest, []))}")
            else:
                # Update dependencies
                if dest in values and src in values:
                    # Both are constants, update value and dependencies
                    if stripped_line.startswith("add"):
                        values[dest] += values[src]
                    elif stripped_line.startswith("sub") or stripped_line.startswith("cmp"):
                        values[dest] -= values[src]
                    dependencies[dest] = {dest, src}
                    commented_code.append(f"{line} ; {dest}={values[dest]}, {dest}:{list(dependencies[dest])}")
                else:
                    # Update dependencies only
                    values.pop(dest, None)  # Clear constant value if overwritten
                    if dest not in dependencies:
                        dependencies[dest] = set()
                    if src in dependencies:
                        dependencies[dest].update(dependencies[src])
                    dependencies[dest].add(src)
                    commented_code.append(f"{line} ; {dest}:{list(dependencies[dest])}")

        else:
            # Preserve non-handled instructions as is
            commented_code.append(line)

    return "\n".join(commented_code)


# Example usage
if __name__ == "__main__":
    # Load the assembly code from the file
    asm_file_path = "/home/kakouzz/Desktop/lark_bark/Compilation-Group2/simple.asm"
    with open(asm_file_path, "r") as asm_file:
        asm_code = asm_file.read()

    # Perform Data Flow Analysis
    commented_asm = data_flow_analysis(asm_code)

    # Save the commented assembly code to a new file
    output_file_path = "/home/kakouzz/Desktop/lark_bark/Compilation-Group2/simple_commented.asm"
    with open(output_file_path, "w") as output_file:
        output_file.write(commented_asm)

    print(f"Commented assembly code saved to {output_file_path}")
