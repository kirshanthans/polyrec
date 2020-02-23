typedef struct _Node{
        int x[10];
        struct _Node * l;
        struct _Node * r;
} Node;

void f1(int i, Node * n);
void f2(int i, Node * n);

void f1(int i, Node * n){
    if (i >= 10) return;
    f2(i, n);
    f1(i+1, n);
}

void f2(int i, Node * n){
    if (!n) return;
    f2(i, n->l);
    f2(i, n->r);
    n->x[i] = n->x[i+1] + 1;
}