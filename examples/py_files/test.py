from typing import List

class Node:
    def __init__(self):
        self.x: List[int] = list(range(10))
        self.l: Node      = None
        self.r: Node      = None

def f1(i: int, n: Node) -> None:
    if i >= 10:
        return
    f2(i, n)
    f1(i+1, n)

def f2(i: int, n: Node) -> None:
    if n == None:
        return
    f2(i, n.l)
    f2(i, n.r)
    n.x[i] = n.x[i] + n.x[i+1]