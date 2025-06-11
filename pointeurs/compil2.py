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
initialisations_post_main = []

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



def asm_exp(e, available_registers=None):
    
    if available_registers is None:
        available_registers = ["r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15","rbx"]
    if e.data == "var":
        reg = available_registers[0]
        return f"mov {reg}, [{e.children[0].value}]", reg
    if e.data == "number" or e.data == "double": # peut ête à modifier pour gérer les doubles
        reg = available_registers[0]
        return f"mov {reg}, {e.children[0].value}", reg
    if e.data == "paren":
        return asm_exp(e.children[0], available_registers)
    

    if e.data == "allocation":
            reg1 = available_registers[0]
            code, reg2 = asm_exp(e.children[0]) 
            return f"""
{code}
mov rdi, {reg1}
call malloc
""", 'rdi'
    
    if e.data == "deref":
        reg = available_registers[0]
        code, base_reg = asm_exp(e.children[0], available_registers)
        return f"""{code}
mov {reg}, [{base_reg}]""", reg

    if e.data == "esperlu":
        reg = available_registers[0]
        return f"lea {reg}, [{e.children[0].value}]", reg

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

    # on lève une erreur pour les expressions non gérées
    raise ValueError(f"Unknown expression type: {e.data}")

compteur = 0

def asm_cmd(c):
    global compteur
    compteur += 1
    compteur_local = compteur

    if c.data == "declaration":
        return ""

    elif c.data == "affectation":
        lhs = c.children[0]
        rhs = c.children[1]

        rhs_code, rhs_reg = asm_exp(rhs, ["r8", "r9", "r10", "r11", "r12", "r13", "r14"])

        if lhs.data == "var":
            var_name = lhs.children[0].value
            return f"""{rhs_code}
mov [{var_name}], {rhs_reg}"""

        elif lhs.data == "deref":
            lhs_code, lhs_reg = asm_exp(lhs.children[0], ["r15", "r14", "r13", "r12"])
            return f"""{lhs_code}
{rhs_code}
mov [{lhs_reg}], {rhs_reg}"""

    elif c.data == "skip":
        return "nop"

    elif c.data == "sequence":
        if len(c.children) == 1:
            return asm_cmd(c.children[0])
        else:
            return f"""{asm_cmd(c.children[0])}
{asm_cmd(c.children[1])}"""

    elif c.data == "print":
        asm_code, result_reg = asm_exp(c.children[0], ["r8", "r9", "r10"])
        return f"""{asm_code}
mov rdi, fmt
mov rsi, {result_reg}
xor rax, rax
call printf"""

    elif c.data == "if":
        cond_code, cond_reg = asm_exp(c.children[0], ["r8", "r9"])
        then_block = asm_cmd(c.children[1])
        else_block = asm_cmd(c.children[2]) if len(c.children) > 2 else "nop"
        return f"""{cond_code}
cmp {cond_reg}, 0
jz else{compteur_local}
{then_block}
jmp endif{compteur_local}
else{compteur_local}:
{else_block}
endif{compteur_local}:"""

    elif c.data == "while":
        cond_code, cond_reg = asm_exp(c.children[0], ["r8", "r9"])
        body_code = asm_cmd(c.children[1])
        return f"""while{compteur_local}:
{cond_code}
cmp {cond_reg}, 0
jz endwhile{compteur_local}
{body_code}
jmp while{compteur_local}
endwhile{compteur_local}:"""


def declaration_variables():
    global liste_vars_global

    declarations = ""
    for var in liste_vars_global:
        declarations += f"{var}: dq 0\n"
    for i in range(2):
        declarations += f"p{i}: dq 0\n"
    
    return declarations

def initialisation_variable(var, type_var, compteur, niveau=0):
    #ici, on initialise une variable en particulier
    code = ""
    
    if type_var == "int":
        code += f"""mov rbx, [argv]
mov rdi, [rbx+{compteur * 8}]
call atoi
mov [{var}], rdi
"""
    
    elif "*" in type_var:
        code += f"""mov rdi, 8
call malloc
mov {var}, rdi
"""
        pointeur_temp = f"p{niveau}"
        code += f"mov {pointeur_temp}, rdi\n"
        next_var = f"[{pointeur_temp}]"
        next_type = type_var[:-1].strip() 
        code += initialisation_variable(next_var, next_type, compteur, niveau + 1)

    return code


    

def get_type(type_tree):
    #obtenir le type d'une variable à partir d'un arbre
    if type_tree.data == "type_prim":
        return type_tree.children[0].value  
    elif type_tree.data == "pointeur":
        return get_type(type_tree.children[0]) + "*"



def initialisation_variables(liste_vars):
    #ici, on initialise les variables qui sont dans main(int a, int* b)
    global liste_vars_global
    code = ""
    compteur = 0  

    for i in range(0, len(liste_vars.children), 2):
        type_var = get_type(liste_vars.children[i])    
        var_name = liste_vars.children[i + 1].value 

        liste_vars_global[var_name] = type_var

        code += initialisation_variable(var_name, type_var, compteur + 1)
        if type_var == "int":
            compteur += 1
    return code



def asm_prg(p):
    if p.data == "main":
        return f"""extern printf, atoi, malloc
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
{''.join(initialisations_post_main)}
{asm_cmd(p.children[1])}
{asm_exp(p.children[2])[0]}
mov rdi, fmt
mov rsi, r8
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
    #declaration : enregistrement des variables initialisées dans le programme
    if c.data == "declaration":
        var_name = c.children[1].value
        type_tree = c.children[0]

        if var_name in liste_vars_global:
            raise ValueError(f"Variable {var_name} already declared")
        
        liste_vars_global[var_name] = type_tree

        # Si c'est un pointeur, on alloue de la place avec malloc
        type_str = get_type(type_tree)
        if "*" in type_str:
            code = f"""mov rdi, 8
call malloc
mov [{var_name}], rdi
"""
            initialisations_post_main.append(code)

    
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

def optimize_asm(asm_code):
    return 0

if __name__ == "__main__":
    liste_vars_global = {}

    with open("simple.c", "r") as f:
        code = f.read()

    ast = g.parse(code)
    verif_type(ast)
    #for i in liste_vars_global:
    #    print(f"{i} : {liste_vars_global[i]}")
    


    asm = asm_prg(ast)
    print(asm)
    with open("new.asm", "w") as f:
        f.write(asm)
    #optimized_asm = optimize_asm(asm_code)
    #print(optimized_asm)
    

    # print(pp_programme(ast))

    # print(asm_exp(ast))
# print(ast.children)
# print(ast.children[0].type)
# print(ast.children[0].value)