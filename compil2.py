from lark import Lark
print("\n")

g=Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9]*/
NUMBER: /[1-9][0-9]*/ | "0"
OPERATOR: /[+\-*\/><]/ | "==" | "!="
liste_var:                                                               -> vide
    | IDENTIFIER ("," IDENTIFIER)*                                       -> vars
expression: IDENTIFIER                                                   -> var
    | expression OPERATOR expression                                     -> operation
    | "(" expression ")"                                                 -> paren
    | NUMBER                                                             -> number
commande: commande (commande)*                                     -> sequence
    | "while" "(" expression ")" "{" commande "}"                          -> while
    | IDENTIFIER "=" expression ";"                                     -> affectation
    | "if" "(" expression ")" "{" commande "}"  ("else" "{" commande "}")? -> if
    | "printf" "(" expression ")" ";"                                           -> print
    | "skip" ";"                                                            -> skip

programme: "main" "(" liste_var ")" "{" commande "return" "(" expression ")" ";" "}"                        -> main

%import common.WS
%ignore WS
""", start='programme')

tabu="    "

def pp_expression(e):
    if e.data in ("var","number"):
        return f"{e.children[0].value}"
    elif e.data == "operation":
        return f"{pp_expression(e.children[0])} {e.children[1].value} {pp_expression(e.children[2])}"
    elif e.data == "paren":
        return f"({pp_expression(e.children[0])})"
    else:
        raise ValueError(f"Unknown expression type: {e.data}")

def pp_commande(c, indent=0):
    if c.data == "affectation":
        return f"{tabu*indent}{c.children[0].value} = {pp_expression(c.children[1])};"
    elif c.data == "print":
        return f"{tabu*indent}printf({pp_expression(c.children[0])});"
    elif c.data == "skip":
        return f"{tabu*indent}skip;"
    elif c.data == "while":
        return f"{tabu*indent}while ({pp_expression(c.children[0])}) {{ \n{pp_commande(c.children[1],indent+1)} \n{tabu*indent}}}"
    elif c.data == "sequence":
        if len(c.children) == 1:
            return f"{pp_commande(c.children[0],indent)}"
        return f"{pp_commande(c.children[0],indent)} \n{pp_commande(c.children[1],indent)}"
    elif c.data == "if":
        return f"{tabu*indent}if ({pp_expression(c.children[0])}) {{\n{pp_commande(c.children[1],indent+1)} \n{tabu*indent}}} \n{tabu*indent}else {{ \n{pp_commande(c.children[2],indent+1)} \n{tabu*indent}}}"
    
def pp_programme(p):
    if p.data=="main":
        return f"main({','.join([v.value for v in p.children[0].children])}) {{\n{pp_commande(p.children[1],1)} \n{tabu}return ({pp_expression(p.children[2])});\n}}"

op2asm = {"+": "add", "-": "sub", "*": "mul", "/": "div", ">": "cmp", "<": "cmp", "==": "cmp"}

def asm_exp(e, available_registers=None):
    
    if available_registers is None:
        available_registers = ["rax", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15","rbx"]

    if e.data == "var":
        reg = available_registers[0]
        return f"mov {reg}, [{e.children[0].value}]", reg
    if e.data == "number":
        reg = available_registers[0]
        return f"mov {reg}, {e.children[0].value}", reg
    if e.data == "paren":
        return asm_exp(e.children[0], available_registers)
    if e.data == "operation":
        # Optimisation de type x+x
        if e.children[0].data == "var" and e.children[2].data == "var":
            reg = available_registers[0]
            var_name1 = e.children[0].children[0].value
            var_name2 = e.children[2].children[0].value
            operation = op2asm[e.children[1].value]
            return f"""mov {reg}, [{var_name1}]
{operation} {reg}, [{var_name2}]""", reg

        # Cas où 1 seul reg dispo: on utilise rcx avec du push/pop sur rbx (le dernier dispo)
        if len(available_registers) < 2:
            assert(available_registers== ["rbx"])
            asm_left,_ = asm_exp(e.children[0], available_registers)
            asm_right, _ = asm_exp(e.children[2], available_registers)
            return f"""{asm_left}
push rbx
{asm_right}
mov rcx, rbx
pop rbx
{op2asm[e.children[1].value]} rbx, rcx""", available_registers
        
        # Cas où on a au moins 2 regs dispos : on les utilise
        left_reg = available_registers[0]
        right_reg = available_registers[1]
        asm_left, _ = asm_exp(e.children[0], available_registers)
        asm_right, _ = asm_exp(e.children[2], available_registers[1:])
        operation = op2asm[e.children[1].value]
        return f"""{asm_left}
{asm_right}
{operation} {left_reg}, {right_reg}""", left_reg

compteur = 0

def asm_cmd(c):
    global compteur
    compteur += 1
    compteur_local = compteur

    if c.data == "affectation":
        asm_code, result_reg = asm_exp(c.children[1])
        return f"""{asm_code}
mov [{c.children[0].value}], {result_reg}"""
    if c.data == "skip":
        return "nop"
    
    if c.data == "sequence":
        if len(c.children) == 1:
            return asm_cmd(c.children[0])
        return f"""{asm_cmd(c.children[0])}
{asm_cmd(c.children[1])}"""
    
    if c.data == "print":
        asm_code, result_reg = asm_exp(c.children[0])
        return f"""{asm_code}
mov rdi, fmt
mov rsi, {result_reg}
xor rax, rax
call printf"""
    
    if c.data == "if":
        asm_code, result_reg = asm_exp(c.children[0])
        return f"""{asm_code}
cmp {result_reg}, 0
jz at{compteur_local}
{asm_cmd(c.children[1])}
jmp end{compteur_local}
at{compteur_local}: {asm_cmd(c.children[2]) if len(c.children) > 2 else "nop"}
end{compteur_local}: nop"""
    
    if c.data == "while":
        asm_code, result_reg = asm_exp(c.children[0])
        return f"""loop{compteur_local}: {asm_code}
cmp {result_reg}, 0
jz end{compteur_local}
{asm_cmd(c.children[1])}
jmp loop{compteur_local}
end{compteur_local}: nop"""

def get_vars_expression(e):
    if e.data == "var":
        return {e.children[0].value}
    else:
        vars = set()
        for child in e.children:
            try:
                if child.data == "var":
                    vars.add(child.children[0].value)
                else:
                    vars.update(get_vars_expression(child))
            except:
                pass
        return vars

def get_vars_commande(c):
    if c.data == "affectation":
        return set(c.children[0].value).union(get_vars_expression(c.children[1]))
    elif c.data == "print":
        return get_vars_expression(c.children[0])
    elif c.data == "skip":
        return set()
    elif c.data == "sequence":
        if len(c.children) == 1:
            return get_vars_commande(c.children[0])
        return get_vars_commande(c.children[0]).union(get_vars_commande(c.children[1]))
    elif c.data == "if":
        vars_if = get_vars_commande(c.children[1])
        vars_else = get_vars_commande(c.children[2]) if len(c.children) > 2 else set()
        return get_vars_expression(c.children[0]).union(vars_if).union(vars_else)
    elif c.data == "while":
        return get_vars_expression(c.children[0]).union(get_vars_commande(c.children[1]))

def declaration_variables(vars=set()):
    declarations = ""
    for i,var in enumerate(vars):
        declarations += f"{var}: dq 0\n"
    return declarations

def initialisation_variable(var, compteur):
    return f"""mov rbx, [argv]
mov rdi, [rbx+{compteur*8}]
call atoi
mov [{var}], rax
"""

def initialisation_variables(liste_vars):
    n = len(liste_vars.children)
    compteur=0
    if n==0:
        return ""
    else:
        code = ""
        for i in range(n):
            code += initialisation_variable(liste_vars.children[i].value, compteur+1+i)
        return code


def asm_prg(p):
    if p.data == "main":
        return f"""extern printf, atoi
section .data
argv: dq 0
{declaration_variables(get_vars_commande(p.children[1]))}
fmt: db "%d", 10,0

global main
section .text
main:
push rbp
mov [argv], rsi
{initialisation_variables(p.children[0])}
{asm_cmd(p.children[1])}
{asm_exp(p.children[2])[0]}
mov rdi, fmt
mov rsi, rax
xor rax, rax
call printf
pop rbp
ret"""

def optimize_asm(asm_code):
    return 0

if __name__ == "__main__":
    with open("testopti.c", "r") as f:
        code = f.read()
    ast = g.parse(code)
    asm_code = asm_prg(ast)
    print(asm_code)
    #optimized_asm = optimize_asm(asm_code)
    #print(optimized_asm)
    # ast = g.parse("8-4")
    # ast = g.parse(code)  # Deuxième ligne : mov depuis [x]
    # print(asm_exp(ast))
# print(ast.children)
# print(ast.children[0].type)
# print(ast.children[0].value)