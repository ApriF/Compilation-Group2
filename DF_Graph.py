def data_flow_graph(asm_code):
    """
    Construct a data flow graph of the assembly code, indicating dependencies of each variable/register 
    before and after each instruction in the asm_code
    """
    registers=["r8","r9","r10","r11","r12","r13","r14","r15","rbx","rcx","heap","flg","rsi","rdi","fmt","rax","nid"]
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
        else:
            if section=="data" and line!="":
                truc=line.split(":")
                if len(truc)>1 and truc[0] not in false_variables:
                    variables.append("["+truc[0]+"]")
            elif section=="texte":
                pass
        i+=1
    debut_untouched=assembly_lines[:i-1]
    fin_untouched=assembly_lines[N-2:]
    to_analine=assembly_lines[i-1:N-2]
    M_naze=len(to_analine)
    to_analine_without_sautsdeligne = [line for line in to_analine if line.strip() != ""]
    to_analine= to_analine_without_sautsdeligne
    M=len(to_analine)


    #Verifs 

    print("Nombre de lignes de l'assembleur initial:",N)
    print("Nombre de lignes du début:", len(debut_untouched))
    print("Variables",variables)
    print("Nombre de lignes du corps:", M_naze)
    print("1ère instruction à analyser:", to_analine[0])
    print("Dernière instruction à analyser:", to_analine[-1])
    print("Nombre de lignes de la fin:", len(fin_untouched))
    print("Nombre de lignes à analyser:",M)
    assert N== len(debut_untouched) + M_naze + len(fin_untouched), "Total lines do not match!"

    #Pré-analyse

    if_else=False
    push=False
    printed=False
    fixed_registers=[]
    all_fixed_registers=["r8","r9","r10","r11","r12","r13","r14","r15","rbx"]

    for i in range(M):
        line=to_analine[i]
        if line.startswith("cmp"):
            if_else=True
        if line.startswith("call printf"):
            printed=True
        if line.startswith("pop") or line.startswith("push"):
            push=True
        if line.startswith(("mov","add","xor","sub","imul","mul","div")):
            parts=line.split()
            var1=parts[1].strip(",")
            if var1 in all_fixed_registers and var1 not in fixed_registers:
                fixed_registers.append(var1)
    


    Used_variables=variables+fixed_registers
    if push:
        Used_variables+=["rcx","heap"]
    if if_else:
        Used_variables+=["flg"]
    if printed:
        Used_variables+=["rsi","rdi","fmt","rax"]
    Used_variables+=["nid"]
    

    # Create a mapping of variables to their indices
    variable_to_index = {var: idx for idx, var in enumerate(Used_variables)}
    nb_var=len(Used_variables)
    # Initialize the data flow graph
    # Each line describe on what depend now the variables after previous instruction of the assembly code (like a graph)
    data_flow_graph=[[[] for _ in range(nb_var)] for _ in range(M+1)]
    # The first line is just the name of the variables
    data_flow_graph[0] = Used_variables
    
    no_push=True
    nid_index = variable_to_index.get("nid")
    flg_index = variable_to_index.get("flg")
    
    # Fill the data flow graph
    for i in range(1,M+1):
        line = to_analine[i-1]
        concerned_var=None
        balise=False
        chg_flg=False
        jmp=False

        if line.startswith(("jmp","jz")):
            jmp=True

        if ":" in line:
            # Remove label from the line
            line = line.split(":")[1].strip()
            balise=True

         # Simple assignment (mov, pop)
        if line.startswith(("mov","pop")):

            # Handle mov, push, and pop instructions
            if line.startswith("mov"):
                parts= line.split()
                dest = parts[1].strip(",")
                concerned_var=variable_to_index.get(dest)
                src = parts[2]
            elif line.startswith("pop"):
                parts = line.split()
                dest = parts[1]
                concerned_var = variable_to_index.get(dest)
                src = "heap"

            # Update the data flow graph based on the source
            if src.isdigit():
                data_flow_graph[i][concerned_var] = int(src)
            else:
                src_index= variable_to_index.get(src)
                data_flow_graph[i][concerned_var] = [(i-1,src_index)]

        # Handle push
        elif line.startswith("push"):
            parts = line.split()
            src = parts[1].strip(",")
            dest="heap"
            concerned_var = variable_to_index.get(dest)
            src_index = variable_to_index.get(src)
            if no_push:
                data_flow_graph[i][concerned_var] = [(i-1, src_index)]
                no_push=False
            else:
                data_flow_graph[i][concerned_var] = [(i-1, src_index), (i-1, concerned_var)]
        
        # Handle arithmetic and logical operations (add, sub, imul, mul, div, xor)
        elif line.startswith(("add", "sub", "imul","mul", "div", "xor","cmp")):
            parts = line.split()
            dest = parts[1].strip(",")
            concerned_var = variable_to_index.get(dest)
            src = parts[2]
            if src.isdigit():
                if line.startswith("cmp"):
                    chg_flg=True
                    data_flow_graph[i][flg_index] =[(i-1,concerned_var)]
                if type(data_flow_graph[i-1][concerned_var])!=list and data_flow_graph[i-1][concerned_var].isdigit():
                    result=0
                    if line.startswith("add"):
                        result = int(data_flow_graph[i-1][concerned_var][0]) + int(src)
                    elif line.startswith("sub"):
                        result = int(data_flow_graph[i-1][concerned_var][0]) - int(src)
                    elif line.startswith("mul"):
                        result = int(data_flow_graph[i-1][concerned_var][0]) * int(src)
                    elif line.startswith("imul"):
                        result== int(data_flow_graph[i-1][concerned_var][0]) * int(src)
                    elif line.startswith("div"):
                        result = int(data_flow_graph[i-1][concerned_var][0]) // int(src)
                    elif line.startswith("cmp"):
                        result = int(data_flow_graph[i-1][concerned_var][0]) - int(src)
                    elif line.startswith("xor"):
                        result = int(data_flow_graph[i-1][concerned_var][0]) ^ int(src)
                    data_flow_graph[i][concerned_var] = result
                else:    
                    data_flow_graph[i][concerned_var] = [(i-1, concerned_var)]
            else:
                if line.startswith("cmp"):                
                    chg_flg=True
                    data_flow_graph[i][flg_index] = [(i-1,concerned_var), (i-1, src)]
                if src==dest:
                    # Specific case for xor rax,rax
                    if line.startswith("xor"):
                        data_flow_graph[i][concerned_var] = 0
                    else:
                        data_flow_graph[i][concerned_var] = [(i-1, concerned_var)]
                else:
                    src_index = variable_to_index.get(src)
                    data_flow_graph[i][concerned_var] = [(i-1, src_index),(i-1,concerned_var)]
        
        # Handle call printf
        elif line.startswith("call printf"):
            # The printf call depends on rdi, rsi, and rax
            rdi_index = variable_to_index.get("rdi")
            rsi_index = variable_to_index.get("rsi")
            rax_index = variable_to_index.get("rax")
            concerned_var = variable_to_index.get("nid")

            # Add dependencies for nid (for needed)
            data_flow_graph[i][concerned_var] = [(i - 1, rdi_index),(i - 1, rsi_index),(i - 1, rax_index),]


        if balise or jmp:
            if line.startswith("jz"):
                data_flow_graph[i][nid_index] = [(i - 1,flg_index)]
            else:
                data_flow_graph[i][nid_index] = 42

        for j in range(nb_var):
            if j!= concerned_var and (j!=nid_index or (balise==False and jmp==False)) and (j!=flg_index or chg_flg==False):
                data_flow_graph[i][j] = [(i-1, j)]
            
    
    # Add a final row for "nid" depending on "r8"
    nid_index = variable_to_index.get("nid")
    r8_index = variable_to_index.get("r8")
    final_row = [[(M, j)] if j == nid_index else [(M, j)] for j in range(nb_var)]
    final_row[nid_index] = [(M, r8_index)]
    data_flow_graph.append(final_row)

    newasm=""
    for line in to_analine:
        newasm += line + "\n"
    return data_flow_graph,debut_untouched,newasm,fin_untouched

def visualize_data_flow_graph(data_flow_graph, plot=False):
    """
    Visualize the data flow graph and highlight the path(s) starting from nodes where
    the "nid" variable is modified without depending on its previous value.
    Return a matrix with highlighted nodes and their dependencies.
    """
    import matplotlib.pyplot as plt
    import networkx as nx

    G = nx.DiGraph()

    nb_var = len(data_flow_graph[0])
    M = len(data_flow_graph) - 1
    target_index = data_flow_graph[0].index("nid")  # Get the index of the target variable

    # Add nodes and edges to the graph
    for i in range(0, M + 1):
        for j in range(nb_var):
            if i == 0:
                G.add_node((i, j), label=data_flow_graph[0][j]) 
            else:
                G.add_node((i, j), label=str(data_flow_graph[i][j]))  # Add node with value as label
                if type(data_flow_graph[i][j]) is not int:
                    for dep in data_flow_graph[i][j]:
                        if isinstance(dep, tuple):
                            G.add_node(dep)
                            G.add_edge(dep, (i, j))
                        else:
                            G.add_node((i - 1, j))
                            G.add_edge((i - 1, j), (i, j))

    # Identify starting points for highlighting
    starting_points = []
    for i in range(1, M + 1):
        dep_nid = data_flow_graph[i][target_index]
        if dep_nid != [(i - 1, target_index)]:
            starting_points.append((i, target_index))

    # Add the final row for "nid" as a starting point
    starting_points.append((M, target_index))

    # Trace paths from the starting points
    paths_to_highlight = []
    stack = starting_points[:]
    highlighted_nodes = [["." for _ in range(nb_var)] for _ in range(M + 1)]  # Initialize the matrix
    while stack:
        current = stack.pop(0)
        if current in G.nodes and highlighted_nodes[current[0]][current[1]] == ".":
            highlighted_nodes[current[0]][current[1]] = data_flow_graph[current[0]][current[1]]  # Mark as highlighted
            for predecessor in G.predecessors(current):
                paths_to_highlight.append((predecessor, current))
                stack.append(predecessor)

    # Filter nodes to color based on highlighted_nodes
    nodes_to_color = [
        (i, j) for i in range(len(highlighted_nodes)) for j in range(len(highlighted_nodes[i]))
        if highlighted_nodes[i][j] != "."
    ]

    if plot: 
        print("Construction du graphe, veuillez patienter...")

        # Define a grid layout: x = variable index (j), y = instruction index (i)
        pos = {(i, j): (j, -i) for i in range(0, M + 1) for j in range(nb_var) if (i, j) in G.nodes}
        labels = {n: G.nodes[n]['label'] for n in G.nodes if 'label' in G.nodes[n]}
        # Draw the graph
        plt.figure(figsize=(12, 8))
        nx.draw(
            G, pos, with_labels=True, labels=labels, node_size=700, node_color='lightblue', font_size=10, font_color='black', arrows=True
        )
        # Highlight the path(s) starting from the identified nodes
        nx.draw_networkx_edges(
            G, pos, edgelist=paths_to_highlight, edge_color="red", width=2.5
        )
        nx.draw_networkx_nodes(
            G, pos, nodelist=nodes_to_color, node_color="orange", node_size=800
        )
        plt.title(f"Data Flow Graph (Highlighting Paths from {'nid'} Modifications)")
        plt.xlabel("Variables")
        plt.ylabel("Instructions")
        plt.show()

    return highlighted_nodes

def detect_dead_code(highlighted_nodes):
    """
    Detect dead instructions in the assembly code using the data flow graph.
    Dead instructions are those that do not modify the dependencies of useful nodes.
    """
    dead_instructions = []
    i=len(highlighted_nodes)-1
    while i>0:
        dead=True
        for j in range(len(highlighted_nodes[i])):
            if highlighted_nodes[i][j] != "." and highlighted_nodes[i][j] != [(i-1, j)]:
                dead=False
                break
        if dead:
            dead_instructions.append(i)
        i-=1
    dead_instructions.reverse()
    return dead_instructions

def optimise_assembly_code(asm_code):
    """
    Optimize the assembly code by removing dead code and unnecessary instructions.
    """
    DF_Graph = data_flow_graph(asm_code)
    debut_untouched = DF_Graph[1]
    analysed_code = DF_Graph[2]
    fin_untouched = DF_Graph[3]
    highlighted_nodes = visualize_data_flow_graph(DF_Graph[0], plot=False)
    dead_instructions = detect_dead_code(highlighted_nodes)

    # Remove dead instructions from the assembly code
    optimized_asm_code ="\n".join(debut_untouched) + "\n"
    for i in range(len(analysed_code.splitlines())):
        if i + 1 not in dead_instructions:
            optimized_asm_code += analysed_code.splitlines()[i] + "\n"
    optimized_asm_code += "\n" + "\n".join(fin_untouched)
    return optimized_asm_code

# Example usage
if __name__ == "__main__":

    asm_file="simple.asm"
    asm_analyzed_file=asm_file.replace(".asm","_analyzed.asm")
    asm_optimized_file=asm_file.replace(".asm","_optimized.asm")

    #Read the asm
    with open(asm_file, "r") as asm_file:
        asm_code = asm_file.read()
    
    # Construct the data flow graph
    DF_Graph_asm = data_flow_graph(asm_code)
    
    # Save the analyzed assembly code
    with open(asm_analyzed_file, "w") as f:
        f.write(DF_Graph_asm[2])

    # Visualize the data flow graph and highlight paths
    #highlighted_nodes = visualize_data_flow_graph(DF_Graph_asm[0], plot=False)
    highlighted_nodes = visualize_data_flow_graph(DF_Graph_asm[0],plot=True)
    
    # Detect dead code in the assembly code
    #dead_instructions = detect_dead_code(highlighted_nodes)
    #print("Dead instructions (indices):", dead_instructions)
    
    # Optimize the assembly code by removing dead code
    optimized_asm_code = optimise_assembly_code(asm_code)

    # Save the optimized assembly code
    with open(asm_optimized_file, "w") as f:
        f.write(optimized_asm_code)
