main(int** a,double b) {
    int c;
    c = **a+b;
    int* p;
    int i;
    i=4;
    p = &i;
    i = *p + 4;
    int* q;
    q = &p;
    *p = i;
    **q = i;
    p = p+i;
    p = malloc(8);
    double x;
    x = 3.14;
    x = 3.e14;
    return(c);
}