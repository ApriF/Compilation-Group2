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

    return(a);       
}

