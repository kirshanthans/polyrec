from typing import List

class Node:
    def __init__(self):
        self.x: List[int] = list(range(10))
        self.l: Node      = None
        self.r: Node      = None