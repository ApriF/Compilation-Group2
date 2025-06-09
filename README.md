# Compilation-Group2

## Description
Ce compilateur transforme un sous-ensemble simplifié du langage C en code assembleur NASM pour architecture x86-64. Il a été développé à des fins pédagogiques pour illustrer les principes de base de la compilation.

## Fonctionnalités

### Types Supportés
| Type       | Exemple      | Description                     |
|------------|--------------|---------------------------------|
| `int`      | `42`, `0`    | Entiers signés                  |
| `double`   | `3.14`, `2.e-5` | Nombres flottants (ne pas oublié le . , notament pour les puissances de 10)     |
| `type*`    | `int*`, `double**` | Pointeurs (le parsing et l'analyse de type et générale mais seules les pointeurs vers des entiers sont implémentés)  |

### Syntaxe du Langage
```c
// Chaque instruction finit par un ;

// Déclaration de variables
int x;
double y;
int* ptr;
// On ne peut pas déclarer et assigner à la fois (pas de int i = 0;)

// Assignation de variables
x = 12;
y=3.14;
ptr = &x;


// Structures if-then-else
// on exécute ce qu'il y a dans le premier scope si x est non nul, on exécute le scope du else sinon.
if (x) {
    printf(x);
} else {
    printf(y);
}

// on exécute ce qu'il y a dans le scope tant que x est non nul.
while (x) {
    x = x - 1;
}

// Fonction principale : la forme que doit avoir le fichier simple.c
main(int arg1, double arg2) {
    // ... code ...
    return (0);//<- ne pas oublier le ; après le return aussi
}
```


### Opérations Implémentées
- **Arithmétiques** : `+`, `-`, `*` (et `/` pour les doubles uniquement)
  
  (il n'y a pas de priorité des opérations : si on ne met pas de parenthèses, elles sont exécutées de gauche à droite)
- **Pointeurs** : `&` (adresse), `*` (déréférencement)
- **Allocation mémoire** : `malloc()` (syntaxe seulement)

La prise en compte des pointeurs, des doubles ou l'optimisation de code sont dans 3 branches distinctes et ne fonctionnent pas ensemble.

## Comment l'utiliser

1. Écrire votre programme le fichier `simple.c` qui doit se trouver au même endroit que le fichier `compil1.py`
2. Exécuter ces trois lignes de bash :
   ```bash
   python compil1.py > simple.asm   |  ou simplement exécuter le code python, cela dépend des branches.
   nasm -f elf64 simple.asm
   gcc -no-pie simple.o
   ```
3. Lancer votre code compilé avec ./a.out [éventuelles arguments de la fonction main]

4. Le compilateur génère :
   - Le code assembleur du programme simple.c dans le fichier `simple.asm`
   - l'exécutable du code, dans le fichier `a.out`
   - le compilateur fait également une vérification du typage de l'ensemble du code, ainsi que des optimisations de code lorsque l'on ne travail que sur des entiers.

## Fonctionnement Interne

### Pipeline de Compilation
1. **Analyse Syntaxique** : Utilisation de Lark pour le parsing
2. **Vérification de Types** :
   - Compatibilité des opérations
   - Déclaration des variables
3. **Génération de Code** :
   - Registres utilisés : `r8-r15`, `rbx`, `xmm0-xmm1`
   - Optimisations basiques si le code ne traite que des entiers (pour maximiser l'utilisation des registres en minimiser les push/pop dans la mémoire et supprimer du code mort))

## Limitations Connues
- Pas de support des opérateurs de comparaison (<, >, ==, !=) ni de division pour les entiers.
- Les pointeurs ne fonctionnent que sur les entiers.
- Pas de conversion de type de int en double (et réciproquement)
- Pas de déclaration et d'assignation simultanés des variables (ex: `int x=0;`)

## Exemple
**Entrée (programme.c)** :
```c
main(int x,int y,int z){
    int c;
    c=0;
    int d;
    d=0;
    int e;
    e=5;
    if (c){
        x=x+1;
    }
    else{
        x=x+x;
    }
    if (d){
        z=10;
        printf(z);
    }
    while(x){
        x=x-1;
        y=y+3;
        z=z+z;
        c=c+5;
        d=d-1;
    }
    z=x+y+z+(d+d+d);
    y=y+e;
    return(z);
}


```

**Sortie ASM** :
```nasm
extern printf, atoi, malloc
section .data
argv: dq 0
x: dq 0
y: dq 0
z: dq 0
c: dq 0
d: dq 0
e: dq 0

fmt: db "%d", 10,0

global main
section .text
main:
push rbp
mov [argv], rsi
mov rbx, [argv]
mov rdi, [rbx+8]
call atoi
mov [x], rax
mov rbx, [argv]
mov rdi, [rbx+16]
call atoi
mov [y], rax
mov rbx, [argv]
mov rdi, [rbx+24]
call atoi
mov [z], rax


mov r8, 0
mov [c], r8

mov r8, 0
mov [d], r8

mov r8, 5
mov [e], r8
mov r8, [c]
cmp r8, 0
jz at15
mov r8, [x]
mov r9, 1
add r8, r9
mov [x], r8
jmp end15
at15: mov r8, [x]
add r8, [x]
mov [x], r8
end15: nop
mov r8, [d]
cmp r8, 0
jz at19
mov r8, 10
mov [z], r8
mov r8, [z]
mov rdi, fmt
mov rsi, r8
xor rax, rax
call printf
jmp end19
at19: nop
end19: nop
loop23: mov r8, [x]
cmp r8, 0
jz end23
mov r8, [x]
mov r9, 1
sub r8, r9
mov [x], r8
mov r8, [y]
mov r9, 3
add r8, r9
mov [y], r8
mov r8, [z]
add r8, [z]
mov [z], r8
mov r8, [c]
mov r9, 5
add r8, r9
mov [c], r8
mov r8, [d]
mov r9, 1
sub r8, r9
mov [d], r8
jmp loop23
end23: nop
mov r8, [x]
add r8, [y]
mov r9, [z]
add r8, r9
mov r9, [d]
add r9, [d]
mov r10, [d]
add r9, r10
add r8, r9
mov [z], r8
mov r8, [y]
add r8, [e]
mov [y], r8
mov r8, [z]
mov rdi, fmt
mov rsi, r8
xor rax, rax
call printf
pop rbp
ret
```
