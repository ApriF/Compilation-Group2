La branche pointeurs implémente ces fonctionnalités :
 - Opérateur esperluette
 - Opérateur déreferencement pour affecter ou pour initialiser (a= *n ou *n = 8)
 - Allocation avec malloc()


Voici un exemple qui marche et qui renvoie 101
main(int b, int c) {
    int a;
    int* p;
    int* q;

    a = 42;         
    p = &a;         
    *p = 99;        

    q = malloc(8);  
    *q = *p + 1;    

    a = *q;         

    a = a + 1;

    return(a);       
}

Pour éxecuter cela, faire les commandes suivantes
nasm -f elf64 new.asm -o new.o
gcc -no-pie new.o -o main
./main 0 0 

Important : il y a un bug dans la récupération des entiers en entrée, il ne sert donc à rien de 
mettre des arguments dans la dernière ligne, cela ne marchera pas. 
Il faut donc tout initialiser dans le code directement.

Autres remarques : on écrit return(a) avec des parenthèses, on écrit directement main(int a, int b) et 
pas int main ..
