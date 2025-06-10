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

