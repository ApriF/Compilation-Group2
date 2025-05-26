main(x,y,z){
    c=0;
    d=0;
    if (c){x=x+1;}
    else{x=x+x;}
    if (d){z=10;}
    while(x){
        x=x-1;
        y=y+3;
        z=z+z;
        c=c+5;
        d=d-1;
        }
    z=x+y+z+(d+d+d);
    return(z);
}