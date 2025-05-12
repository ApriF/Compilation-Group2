## 28/04
En mémoire, l'exécutable est en 3 blocs : 
- header : pour lancer le programme
- text : contient les instructions (lecture et exécution seulement)
- data : contient les variables gobales (lecture et écriture)

Un segmentation fault arrive si on tente d'écrire dans la partie text par exemple.

- db: byte (1 octet)
- dw: word (2 octets)
- dd: digit (4 octets)
- dq: quad-word (8 octets)

On suit la convention ABI V. On donne les arguments via les registres.

Objectif : Après compilation, le registre rax contient la valeur de l'expression compilée.

- E=n : gamma(E)= "mov rax, n"
- E=X : gamma(E)= "mov rax, [X]"
- E=E1+E2 : gamma(E) = "g(E1) | 
                        push rax | 
                        g(E2) |
                        mov rbx, rax | 
                        pop rax | 
                        add rax, rbx"

- C= X=E : g(C)= "g(E) | mov [X], rax"
- C= skip : g(C)= ""
- C= C1;C2 : g(C)= "g(C1) | g(C2)"
- C= print(E) : g(C)= "g(E) |
                       mov rsi, fmt |
                       mov rdi, rax |
                       xor rax, rax |
                       call printf"
- C= if(E){C1} else{C2} : g(C)= "g(E) | 
                                 cmp rax, 0 | 
                                 jz at0 |
                                 g(C2) |
                                 jmp end0 |
                            at0: g(C1) |
                           end0: nop"
- C= while(E){C'} : g(C)= "at0: g(E) |
                               cmp rax, 0 |
                               jz end0 |
                               g(C') |
                               jmp at0 |
                        end0:  nop"
- P= main(X1,...,Xk){C;return(E)} : g(P)= "section .data |
                                           X1: qd 0 |
                                           .
                                           .
                                           .
                                           Xk: dq 0 |
                                           Z: dq 0 |
                                           fmt db "%d",10,0 |

                                           section .text |
                                           // initialisation des variables X1...Xk ~ argc, argv en C |
                                           push rbp |
                                           g(C) |
                                           g(E) |
                                           mov rdi, fmt |
                                           mov rsi, rax |
                                           xor rax, rax |
                                           call printf |
                                           pop rbp |
                                           ret"

## 5/05
nasm -f elf64 hum.nasm
gcc -no-pie hum.o

les arguments de argc sont dans rdi, ceux de argv dans rsi (char**)
pour transformer le char* en long*, fonction atoi de la librairie c (atoi: char* -> int (long))

## Projet
typage : 
-     soit typage statique (comme en c) : par exemple 
      float main(int x, float r){
          int pi=3;
      }

Un code mal typé doit retourner un warning ou une erreur
   
-     soit un typage dynamique (comme en c++ ou python) : à chaque étape, une variable a un type associé.
        pi = 3;
        pi = 3.14;

double (8 octets) : 
     
    On veut pouvoir gérer des trucs du genre 
    x=3.14;
    y=3.0e-5; 
    z=3.e14; 
    z=(float) i (un int/long); 
    i=(int) z + k

voir godbolt


pointeurs vers des entiers seulement:

    p = &i; (où i est un int)
    i = *p+4;
    q = &p;
    *p = i;
    **q = i;
    p = malloc(4); (sous entendu malloc(8*4))
    p = p+i;

optimisations :
    
    x=0;             | -> on doit remplacer cela par machin uniquement
    if(x){machin}    |        (détection de code mort)
    else {chose}     |

    x+y        -> enlever les push/pop rax en utilisant d'autres registres (r8,r9,rdx...)

    x+x     -> faire en sorte qu'il n'y ait qu'un seul mov rax, [x]


## Debugger
Instructions pour gdb :

    set args 1 2
    r (run; utilisable si breakpoint présent)
    b main (définit un breakpoint à main)
    ni (next instruction)
    disas (affiche l'assembleur)
    si (étape suivante, en rentrant de les fonctions)
    print $rax (affiche le contenu du registre rax)
    info registers (affiche l'état de tous les registres)
    c (continue)
    x/nc (n entier; affiche n caractères)
    apropos word (doc autour du mot word)
    q (quit)

Autre possibilité : Cutter ou peda (+gdb)