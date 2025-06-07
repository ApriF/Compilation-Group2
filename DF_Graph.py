def data_flow_graph(asm_code):
    """
    Construct a data flow graph of the assembly code, indicating dependencies of each variable/register 
    before and after each instruction in the asm_code
    """
    registers=["rax","rbx","rcx","r8","r9","r10","r11","r12","r13","r14","r15"]
    variables=[]
    false_variables=["argv","fmt"]
    assembly_lines = asm_code.splitlines()
    i=1
    N=len(assembly_lines)
    section="none"

    # Initialize the variables and select the relevant code
    while section!="corps":
        line = assembly_lines[i-1].strip()
        if line.startswith("section .data"):
            section="data"
        elif line.startswith("section .text"):
            section="text"
        elif section == "text" and line=="":
            section="corps"
            print("corps à partir de la ligne",i+1)
        else:
            if section=="data" and line!="":
                truc=line.split(":")
                if len(truc)>1 and truc[0] not in false_variables:
                    variables.append(truc[0])
            elif section=="texte":
                pass
        i+=1
    print(variables)

# Example usage
if __name__ == "__main__":
    asm_file_path = "/home/kakouzz/Desktop/lark_bark/Compilation-Group2/simple.asm"
    with open(asm_file_path, "r") as asm_file:
        asm_code = asm_file.read()
    DF_Graph_asm = data_flow_graph(asm_code)
