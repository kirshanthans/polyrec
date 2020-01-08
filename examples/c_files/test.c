typedef struct node
{
    int x[10];
    struct node * l;
    struct node * r;
}Node;

void f1(int i, Node * n);
void f2(int i, Node * n);

void f1(int i, Node * n){
        if(i >= 10) return;
        f2(i, n);
        f1(i+1, n);
}

void f2(int i, Node * n){
        if (n == NULL) return;
        f2(i, n->l);
        f2(i, n->r);
        n->x[i] = n->x[i] + n->x[i+1];
}