def taint_analysis(asm_code):
    """
    Perform taint analysis on the given assembly code.
    Annotate each line with the dependencies of variables and registers.
    """
    dependencies = {'x':"x",'y':"y","heap":""}  # Tracks dependencies for each register/variable
    annotated_lines = []
    list_inst=["mov","push","pop","add", "sub","mul", "div", "cmp"]

    # Initialize dependencies from the .data section
    in_data_section = False
    for line in asm_code.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith("section .data"):
            in_data_section = True
            continue
        if in_data_section:
            if stripped_line == "":
                break
            var_name = stripped_line.split(":")[0].strip()
            dependencies[var_name] = var_name


    for line in asm_code.splitlines():
        stripped_line = line.strip()
        parts= stripped_line.split()
        instruction = parts[0] if parts else None
        do=False
            
        if instruction in list_inst:
            do=True
            if instruction in ["push","pop"]:
                if instruction=="push":
                    dest="heap"
                    src= parts[1]
                elif instruction=="pop":
                    dest=parts[1]
                    src="heap"
            else:
                dest= parts[1].strip(",")
                src= parts[2]

            if src.startswith("[") and src.endswith("]"):
                src= src[1:-1]
            if dest.startswith("[") and dest.endswith("]"):
                dest= dest[1:-1]
            
            if instruction in ["push","pop","mov"]:
                if src in dependencies:
                    dependencies[dest] = dependencies[src]
                else:
                    dependencies[dest] = src
    
            elif instruction in ["add","sub","mul","div","cmp"]:
                if dependencies[dest] in dependencies and src in dependencies and dependencies[src] in dependencies:
                    dependencies[dest] = dependencies[dest]+','+dependencies[src]
                elif dependencies[dest] not in dependencies:
                    x=dependencies[dest]
                    y=None
                    if src in dependencies:
                        if dependencies[src] in dependencies:
                            dependencies[dest] = dependencies[src]
                        else: 
                            y=dependencies[src]
                    else:
                        y=src
                    if y!=None:
                        if instruction=="add":
                            dependencies[dest] = str(int(x)+int(y))
                        elif instruction=="sub":
                            dependencies[dest] = str(int(x)-int(y))
                        elif instruction=="mul":
                            dependencies[dest] = str(int(x)*int(y))
                        elif instruction=="div":
                            dependencies[dest] = str(int(x)/int(y))
                        elif instruction=="cmp":
                            dependencies[dest] = str(int(x)-int(y))

            annotated_lines.append(f"{line}  ; Teintes: {dependencies}")
        if not(do):
            annotated_lines.append(f"{line}  ; Teintes: {dependencies}")

    return "\n".join(annotated_lines)


if __name__ == "__main__":
    # Example usage
    example_asm = """
    extern printf, atoi
    section .data
    argv: dq 0
    y: dq 0
    c: dq 0
    z: dq 0
    x: dq 0

    fmt: db "%d", 10,0

    global main
    section .text
    main:
    mov rax, [x]
    add rax, 8
    push rax
    mov rax, [y]
    sub rax, 3
    pop [y]
    add [y], rax
    mov [c], 1
    ret"""
    annotated_code = taint_analysis(example_asm)
    print(annotated_code)
