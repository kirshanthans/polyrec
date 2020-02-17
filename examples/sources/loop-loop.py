def work(i: int, j: int) -> None:
    pass

def f1(i: int, j: int) -> None:
    if i >= 10:
        return
    f2(i,   j)   
    f1(i+1, j)

def f2(i: int, j: int) -> None:
    if j >= 10:
        return
    work(i, j)
    f2(i, j+1)

## Loop-Skewing
def f1_(i: int, j: int) -> None:
    if i >= 10:
        return
    f2_(i, i+j)   
    f1_(i+1, j)

def f2_(i: int, j: int) -> None:
    if j >= i+10:
        return
    work(i, j)
    f2_(i, j+1)
    