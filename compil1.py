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
commande: commande (commande)*                                            -> sequence
    | "while" "(" expression ")" "{" commande "}"                         -> while
    | identifier_bis "=" expression ";"                -> affectation
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
        #Si ajout de la syntaxe double x = (int) 5;
        if len(c.children) == 3:
            return f"{tabu*indent}{pp_expression(c.children[0])} = ({c.children[1].value}) {pp_expression(c.children[2])};"
        else:
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
opFloat = {"+": "addsd", "-": "subsd", "*": "mulsd", "/": "divsd", ">": "ucomisd", "<": "ucomisd", "==": "ucomisd"}
def asm_exp(e, available_registers=None):
    if available_registers is None:
        available_registers = ["r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15","rbx"]

    if e.data == "var":
        if liste_vars_global[e.children[0].value].children[0] == "int":
            reg = available_registers[0]
            return f"mov {reg}, [{e.children[0].value}]", reg
        if liste_vars_global[e.children[0].value].children[0] == "double":
            return f"movsd xmm0, [{e.children[0].value}]", "xmm0"
        
    if e.data == "number":
        reg = available_registers[0]
        return f"mov {reg}, {e.children[0].value}", reg
    
    if e.data == "double":
        val = f"__float64__({str(e.children[0].value)})"
        label = f"float_{str(e.children[0].value).replace('.', '_').replace('-', 'm')}"
        double_literals.add((label, val))
        return f"movsd xmm0, [{label}]", "xmm0"
    
    if e.data == "paren":
        return asm_exp(e.children[0], available_registers)
    
    if e.data == "allocation":
        asm_code, result_reg = asm_exp(e.children[0])
        return "nop", result_reg # à modifier pour gérer les mallocs

    if e.data == "deref": # à modifier pour gérer les pointeurs
        return asm_exp(e.children[0], available_registers)
    if e.data == "esperlu": #  à modifier pour gérer les pointeurs
        newe = Tree('var', [Token('IDENTIFIER', e.children[0].value)])
        return asm_exp(newe, available_registers)

    if e.data == "operation":
        number_of_double = is_double_expression(e)
        if number_of_double == 0:
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
        
        #à optimiser, la conversion ne support pas les registres r8
        if number_of_double == 1:
            if is_double_expression(e.children[0]):
                return f"""mov rax, [{e.children[2].children[0].value}]
cvtsi2sd xmm0, rax
movsd xmm1, xmm0
{asm_exp(e.children[0])[0]}
{opFloat[e.children[1].value]} xmm0, xmm1""", "xmm0"
            else:
                return f"""
{asm_exp(e.children[2])[0]}
movsd xmm1, xmm0
mov rax, [{e.children[0].children[0].value}]
cvtsi2sd xmm0, rax
{opFloat[e.children[1].value]} xmm0, xmm1""", "xmm0"
            
        if number_of_double == 2:
            return f"""{asm_exp(e.children[0])[0]}
movsd xmm1, xmm0
{asm_exp(e.children[2])[0]}
{opFloat[e.children[1].value]} xmm0, xmm1""", "xmm0"
        # on lève une erreur pour les expressions non gérées
        raise ValueError(f"Unknown expression type: {e.data}")

#retourne 0, 1 ou 2 en fonction du nombre de double dans l'opération 
def is_double_expression(e):
    if e.data == "double":
        return 1
    if e.data == "var":
        if liste_vars_global[e.children[0].value].children[0] == "double":
            return 1
        else:
            return 0
    if e.data == "number":
        return 0
    if e.data == "operation":
        number_of_double = 0
        number_of_double = is_double_expression(e.children[0]) + is_double_expression(e.children[2])
    return number_of_double

#Permet de déclarer les doubles dans .rdata afin de placer la valeur du double dans les registres xmm0, xmm1...
def declaration_double_statique(ast):
    global double_literals
    init_double_literals_in_cmd(ast.children[1])
    init_double_literals_in_expr(ast.children[2])
    out = ""
    for label, val in double_literals:
        out += f"{label}: dq {val}\n"
    return out

def init_double_literals_in_expr(e):
    if e.data == "double":
        val = str(e.children[0].value)
        label = f"float_{val.replace('.', '_').replace('-', 'm')}"
        double_literals.add((label, f"__float64__({val})"))

    if e.data == "operation":
        init_double_literals_in_expr(e.children[0])
        init_double_literals_in_expr(e.children[2])

    if e.data == "paren":
        init_double_literals_in_expr(e.children[0])

    if e.data == "deref" or e.data == "esperlu" or e.data == "allocation":
        init_double_literals_in_expr(e.children[0])

    if e.data == "var" or e.data == "number":
        pass  # pas de double ici
    else:
        pass

def init_double_literals_in_cmd(c):
    if c.data == "affectation":
        init_double_literals_in_expr(c.children[1])

    if c.data == "print":
        init_double_literals_in_expr(c.children[0])

    if c.data == "while":
        init_double_literals_in_expr(c.children[0])
        init_double_literals_in_cmd(c.children[1])

    if c.data == "if":
        init_double_literals_in_expr(c.children[0])
        init_double_literals_in_cmd(c.children[1])
        if len(c.children) > 2:
            init_double_literals_in_cmd(c.children[2])

    if c.data == "sequence":
        for child in c.children:
            init_double_literals_in_cmd(child)

    if c.data == "declaration":
        pass

    if c.data == "skip":
        pass
    else:
        pass

compteur = 0

def asm_cmd(c):
    global compteur
    compteur += 1
    compteur_local = compteur
    if c.data == "declaration":
        return ""
    #à optimiser pour les doubles
    if c.data == "affectation":
        if liste_vars_global[c.children[0].children[0].value].children[0] == "int":
            asm_code, result_reg = asm_exp(c.children[1])
            return f"""{asm_code}
mov [{c.children[0].children[0]}], {result_reg}
"""
        if liste_vars_global[c.children[0].children[0].value].children[0] == "double":
            asm_code, result_reg = asm_exp(c.children[1])
            return f"""{asm_code}
movsd [{c.children[0].children[0].value}], xmm0
"""
        
    
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
end{compteur_local}: nop
"""

def declaration_variables():
    global liste_vars_global
    declarations = ""
    for var in liste_vars_global:
        if liste_vars_global[var].children[0] == "double":
            declarations += f"{var}: dq __float64__(0.0)\n"
        else:
            declarations += f"{var}: dq 0\n"
    return declarations

def initialisation_variable(var, compteur):
    if liste_vars_global[var].children[0] == "double" :
        return f"""mov rbx, [argv]
mov rdi, [rbx+{compteur*8}]
call atoi
mov [{var}], xmm0
"""
    else:
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

def type_return(variable):
    if variable[1] == "xmm0":
        return f"""{variable[0]}
lea rdi, [rel fmtf]
mov rax, 1"""
    else:
        return f"""{variable[0]}
mov rdi, fmt
mov rsi,r8
xor rax, rax"""

def asm_prg(p):
    if p.data == "main":
        return f"""extern printf, atoi
section .data
argv: dq 0
{declaration_variables()}
fmt: db "%d", 10,0
fmtf: db "%f", 10,0

section .rdata
{declaration_double_statique(p)}

global main
section .text
main:
push rbp
mov [argv], rsi
{initialisation_variables(p.children[0])}
{asm_cmd(p.children[1])}
{type_return(asm_exp(p.children[2]))}
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
            type_double=Tree('type_prim', [Token('TYPE_PRIM', 'double')])
            if not ((left_type == type_int and right_type.data == "pointeur") or (right_type == type_int and left_type.data == "pointeur") or (left_type == type_int and right_type == type_double) or (left_type == type_double and right_type == type_int)):
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
    double_literals = set()
    with open("simple.c", "r") as f:
        code = f.read()
    ast = g.parse(code)
    verif_type(ast)

    #print(ast.children[1])
    #print(f"\n\n{ast.children[2]}")
    #print(f"\n\n{asm_exp(ast.children[2])}")
    
    # for i in liste_vars_global:
    #     print(f"{i} : {liste_vars_global[i]}")
    
    asm = asm_prg(ast)
    print(asm)

    #optimized_asm = optimize_asm(asm_code)
    #print(optimized_asm)
    

    # print(pp_programme(ast))

    # print(asm_exp(ast))
# print(ast.children)
# print(ast.children[0].type)
# print(ast.children[0].value)