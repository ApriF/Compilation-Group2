# Compilation-Group2

## Description
Ce compilateur transforme un sous-ensemble simplifié du langage C en code assembleur NASM pour architecture x86-64. Il a été développé à des fins pédagogiques pour illustrer les principes de base de la compilation.

## Fonctionnalités

### Types Supportés
| Type       | Exemple      | Description                     |
|------------|--------------|---------------------------------|
| `int`      | `42`, `0`    | Entiers signés                  |
| `double`   | `3.14`, `2.e-5` | Nombres flottants (ne pas oublié le . , notament pour les puissances de 10)     |

### Syntaxe du Langage
```c
// Chaque instruction finit par un ;

// Déclaration de variables
int x;
double y;
// On ne peut pas déclarer et assigner à la fois (pas de int i = 0;)

// Assignation de variables
x = 12;
y=3.14;


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
- **Arithmétiques** : `+`, `-`, `*`, `/`
  
  (il n'y a pas de priorité des opérations : si on ne met pas de parenthèses, elles sont exécutées de gauche à droite)

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

Attention : Ne pas mettre de double en argument ni essayer de return un double n'étant pas une variable du programme sinon le programme ne compile pas.

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
- Pas de conversion de type de int en double (et réciproquement)
- Pas de déclaration et d'assignation simultanés des variables (ex: `int x=0;`)