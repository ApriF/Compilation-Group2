from lark import Lark
from lark import Tree, Token
print("\n")

g=Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9]*/
NUMBER: /[1-9][0-9]*/ | "0"
OPERATOR: /[+\-*\/><]/ | "=="
TYPE_PRIM : "int" | "double"
type: TYPE_PRIM   ->  type_prim
    | type"*"     ->  pointeur 
DOUBLE : /[0-9][0-9]*[.0-9][0-9]*/ | /[0-9][0-9]*[.][0-9]*[e][\-]*[0-9][0-9]*/
liste_var:                                                               -> vide
    | type " " IDENTIFIER ("," type " " IDENTIFIER)*                     -> vars
expression: IDENTIFIER                                                   -> var
    | expression OPERATOR expression                                     -> operation
    | "(" expression ")"                                                 -> paren
    |NUMBER                                                              -> number
    | "&" IDENTIFIER                                                     -> esperlu
    | "*" expression                                                     -> deref
    | "malloc(" expression ")"                                           -> allocation
    |DOUBLE                                                              -> double
commande: commande (commande)*                                           -> sequence
    | "while" "(" expression ")" "{" commande "}"                        -> while
    | identifier_bis "=" expression ";"                                  -> affectation
    | type IDENTIFIER ";"                                                -> declaration
    | "if" "(" expression ")" "{" commande "}"  ("else" "{" commande "}")?  -> if
    | "printf" "(" expression ")" ";"                                       -> print
    | "skip" ";"                                                            -> skip
identifier_bis: IDENTIFIER                                               -> var
    | "*" identifier_bis                                                 -> deref


programme: "main" "(" liste_var ")" "{" commande "return" "(" expression ")" ";" "}"                        -> main

%import common.WS
%ignore WS
""", start='programme')



tabu="    "

def pp_expression(e):
    if e.data in ("number", "double"):
        return f"{e.children[0].value}"
    elif e.data == "var":
        return f"{e.children[0].value}"
    elif e.data == "operation":
        return f"{pp_expression(e.children[0])} {e.children[1].value} {pp_expression(e.children[2])}"
    elif e.data == "paren":
        return f"({pp_expression(e.children[0])})"
    elif e.data == "esperlu":
        return f"&{e.children[0].value}"
    elif e.data == "deref":
        return f"*{pp_expression(e.children[0])}"
    elif e.data == "allocation":
        return f"malloc({pp_expression(e.children[0])})"        
    else:
        raise ValueError(f"Unknown expression type: {e.data}")

def pp_type(t):
    if t.data == "type_prim":
        return f"{t.children[0].value}"
    elif t.data == "pointeur":
        return f"{pp_type(t.children[0])}*"
    else:
        raise ValueError(f"Unknown type: {t.data}")

def pp_commande(c, indent=0):
    if c.data == "declaration":
        return f"{tabu*indent}{pp_type(c.children[0])} {c.children[1].value};"
    if c.data == "affectation":
        return f"{tabu*indent}{pp_expression(c.children[0])} = {pp_expression(c.children[1])};"
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
        ret = ""
        ret += "main("
        for i in range(0,len(p.children[0].children),2):
            if p.children[0].children[i].data == "type_prim":
                ret += f"{p.children[0].children[i].children[0].value} {p.children[0].children[i+1].value}, "
            if p.children[0].children[i].data == "pointeur":
                depth = 0
                child = p.children[0].children[i]
                while child.data == "pointeur":
                    depth += 1
                    child = child.children[0]
                ret += f"{child.children[0].value}{depth*"*"} {p.children[0].children[i+1].value}, "
        ret = ret[:-2] + ") {\n"
        ret += f"{pp_commande(p.children[1],1)} \n"
        ret += f"{tabu}return ({pp_expression(p.children[2])});\n"
        ret += "}"
        return ret

op2asm = {"+": "add", "-": "sub", "*": "mul", "/": "div", ">": "cmp", "<": "cmp", "==": "cmp"}
def asm_exp(e):
    if e.data == "var":
        return f"mov rax, [{e.children[0].value}]"
    if e.data == "number":
        return f"mov rax, {e.children[0].value}"
    if e.data == "operation":
        return f"""{asm_exp(e.children[0])}
push rax
{asm_exp(e.children[2])}
mov rbx, rax
pop rax
{op2asm[e.children[1].value]} rax, rbx"""
    if e.data == "paren":
        return asm_exp(e.children[0])

compteur = 0
def asm_cmd(c):
    global compteur
    compteur += 1
    compteur_local = compteur

    if c.data == "declaration":
        return ""
    if c.data == "affectation":
        return f"""{asm_exp(c.children[1])}
mov [{c.children[0].children[0]}], rax"""
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
        asm_code, result_reg = asm_exp(c.children[0])
        return f"""{asm_code}
cmp {result_reg}, 0
jz at{compteur_local}
{asm_cmd(c.children[1])}
jmp end{compteur_local}
at{compteur_local}: {asm_cmd(c.children[2]) if len(c.children) > 2 else "nop"}
end{compteur_local}: nop

    if c.data == "while":
        return f"""loop{compteur_local}: nop
{asm_exp(c.children[0])}
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

def declaration_variables():# ne gère que les entiers -> à upgrade avec les versions float et ptr
    global liste_vars_global
    declarations = ""
    for var in liste_vars_global:
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
        for i in range(0,len(liste_vars.children),2):
            code += initialisation_variable(liste_vars.children[i+1].value, compteur+1+i//2)
        return code


def asm_prg(p):
    if p.data == "main":
        return f"""extern printf, atoi
section .data
argv: dq 0
{declaration_variables()}
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

def verif_type(ast):

    # enregistrement des types des arguments de la fonction main
    list_vars = ast.children[0]
    for i in range(0,len(list_vars.children),2):
        liste_vars_global[list_vars.children[i+1].value] = list_vars.children[i]

    verif_type_cmd(ast.children[1])
    verif_type_exp(ast.children[2])


def verif_type_cmd(c):
    if c.data == "declaration":
        if c.children[1].value in liste_vars_global:
            raise ValueError(f"Variable {c.children[1].value} already declared")
        liste_vars_global[c.children[1].value] = c.children[0]

    elif c.data == "affectation":
        var = c.children[0]
        while(var.data == 'deref' or var.data == "esperlu"):
            var = var.children[0]
        if var.children[0] not in liste_vars_global:
            raise ValueError(f"Variable {var.children[0]} not declared")
        var_type = verif_type_exp(c.children[0]) 
        expr_type = verif_type_exp(c.children[1])
        if var_type != expr_type and expr_type != "malloc":
            raise ValueError(f"Type mismatch: {var_type} != {expr_type}")


    elif c.data == "if":
        expr_type = verif_type_exp(c.children[0])
        if expr_type.children[0] != "int":
            raise ValueError(f"Type mismatch: {expr_type} != Tree('type_prim', [Token('TYPE_PRIM', 'int')])")
        verif_type_cmd(c.children[1])
        if len(c.children) > 2:
            verif_type_cmd(c.children[2])

    elif c.data == "while":
        expr_type = verif_type_exp(c.children[0])
        if expr_type.children[0] != "int":
            raise ValueError(f"Type mismatch: {expr_type} != Tree('type_prim', [Token('TYPE_PRIM', 'int')])")
        verif_type_cmd(c.children[1])

    elif c.data == "sequence":
        if len(c.children) == 1:
            verif_type_cmd(c.children[0])
        else:
            verif_type_cmd(c.children[0])
            verif_type_cmd(c.children[1])
    
def verif_type_exp(e):
    if e in liste_vars_global:
        return liste_vars_global[e]
    if e.data == "var":
        if e.children[0].value not in liste_vars_global:
            raise ValueError(f"Variable {e.children[0].value} not declared")
        return liste_vars_global[e.children[0].value]
    elif e.data == "number":
        return Tree('type_prim', [Token('TYPE_PRIM', 'int')])
    elif e.data == "double":
        return Tree('type_prim', [Token('TYPE_PRIM', 'double')])

    elif e.data == "operation":
        left_type = verif_type_exp(e.children[0])
        right_type = verif_type_exp(e.children[2])
        if left_type != right_type:
            type_int=Tree('type_prim', [Token('TYPE_PRIM', 'int')])
            if not ((left_type == type_int and right_type.data == "pointeur") or (right_type == type_int and left_type.data == "pointeur")):
                raise ValueError(f"Type mismatch: {left_type} != {right_type}")
        return left_type

    elif e.data == "paren":
        return verif_type_exp(e.children[0])
    
    elif e.data == "esperlu":
        type = verif_type_exp(e.children[0])
        if type.data == "number":
            raise ValueError(f"Cannot take address of a number")
        if type.data == "double":
            raise ValueError(f"Cannot take address of a double")
        else:
            return Tree('pointeur', [type])
    
    elif e.data == "deref":
        type = verif_type_exp(e.children[0])
        if type.data == "pointeur":
            return type.children[0]
        else:
            raise ValueError(f"Cannot dereference a {type}")
    elif e.data == "allocation":
        type = verif_type_exp(e.children[0])
        if type.children[0] == "int":
            return "malloc"
        else:
            raise ValueError(f"malloc function can't take argument of type {type}")
    else:
        raise ValueError(f"Unknown expression type: {e.data}")



if __name__ == "__main__":
    liste_vars_global = {}
    with open("simple.c", "r") as f:
        code = f.read()
    ast = g.parse(code)
    verif_type(ast)
    
    for i in liste_vars_global:
        print(f"{i} : {liste_vars_global[i]}")
    

    # asm = asm_prg(ast)
    # print(asm)

    # print(pp_programme(ast))

    # print(asm_exp(ast))
# print(ast.children)
# print(ast.children[0].type)
# print(ast.children[0].value)