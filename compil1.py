from lark import Lark
print("\n")

g=Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9]*/
NUMBER: /[1-9][0-9]*/ | "0"
OPERATOR: /[+\-*\/><]/ | "=="
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
def asm_exp(e, reg="rax"):
    if e.data == "var":
        return f"mov {reg}, [{e.children[0].value}]"
    if e.data == "number":
        return f"mov {reg}, {e.children[0].value}"
    if e.data == "paren":
        return asm_exp(e.children[0], reg)
    if e.data == "operation":
        left_reg = reg
        right_reg = "r8" if reg == "rax" else "rax"

        # x + x Optimised (only one mov)
        if e.children[0].data == "var" and e.children[2].data == "var" and e.children[0].children[0].value== e.children[2].children[0].value:
            var_name = e.children[0].children[0].value
            operation = op2asm[e.children[1].value]
            return f"""mov {left_reg}, [{var_name}]
{operation} {left_reg}, {left_reg}"""

        # x + y Optimised (no push/pop)
        asm_left = asm_exp(e.children[0], left_reg)
        asm_right = asm_exp(e.children[2], right_reg)
        operation = op2asm[e.children[1].value]
        return f"""{asm_left}
{asm_right}
{operation} {left_reg}, {right_reg}"""
    
    
compteur = 0
def asm_cmd(c):
    global compteur
    compteur += 1
    compteur_local = compteur

    if c.data == "affectation":
        return f"""{asm_exp(c.children[1])}
mov [{c.children[0].value}], rax"""
    if c.data == "skip":
        return "nop"
    if c.data == "sequence":
        if len(c.children) == 1:
            return asm_cmd(c.children[0])
        return f"""{asm_cmd(c.children[0])}
{asm_cmd(c.children[1])}"""
    if c.data == "print":
        return f"""{asm_exp(c.children[0])}
mov rdi, fmt
mov rsi, rax
xor rax, rax
call printf"""
    if c.data == "if":
        # Dead code elimination 1: if (x) {machin} else {chose} -> machin with x!=0
        if c.children[0].data == "number" and c.children[0].value!="0" or c.children[0].data=="var" and c.children[0].children[0].value != "0":
            return asm_cmd(c.children[1])
        # Dead code elimination 2: if (x) {machin} [else {chose}] -> nop if no chose, else chose with x == 0
        if c.children[0].data == "number" and c.children[0].value == "0" or c.children[0].data=="var" and c.children[0].children[0].value == "0":
            return asm_cmd(c.children[2]) if len(c.children) > 2 else "nop"
        return f"""{asm_exp(c.children[0])}
cmp rax, 0
jz at{compteur_local}
{asm_cmd(c.children[1])}
jmp end{compteur_local}
at{compteur_local}: {asm_cmd(c.children[2]) if len(c.children) > 2 else "nop"}
end{compteur_local}: nop"""
    if c.data == "while":
        return f"""loop{compteur_local}: {asm_exp(c.children[0])}
cmp rax, 0
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
{asm_exp(p.children[2])}
mov rdi, fmt
mov rsi, rax
xor rax, rax
call printf
pop rbp
ret"""


if __name__ == "__main__":
    with open("simple.c", "r") as f:
        code = f.read()
    ast = g.parse(code)
    print(asm_prg(ast))
    # ast = g.parse("8-4")
    # ast = g.parse(code)
    # print(asm_exp(ast))
# print(ast.children)
# print(ast.children[0].type)
# print(ast.children[0].value)