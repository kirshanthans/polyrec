import copy, ast

class ReplaceVar(ast.NodeTransformer):
    def __init__(self, oname: str, nname: str):
        self.oname = oname
        self.nname = nname

    def visit_Name(self, node: ast.Name):
        if node.id == self.oname:
            result = copy.deepcopy(node)
            result.id = self.nname
            return result
        return node

class ChangeStride(ast.NodeTransformer):
    def __init__(self, stride: int):
        self.stride = stride

    def visit_BinOp(self, node: ast.BinOp):
        result = copy.deepcopy(node)
        if isinstance(node.right, ast.Num):
            result.right.n = self.stride
        return result

class CallAddArg(ast.NodeTransformer):
    def __init__(self, id, dim):
        self.dim = dim
        self.newarg = ast.Name(id=id, ctx=ast.Load())
    
    def visit_Call(self, node: ast.Call):
        result = copy.deepcopy(node)
        result.args.insert(self.dim, self.newarg)
        return result

class ChangeCallee(ast.NodeTransformer):

    def __init__(self, oname:str, nname: str):
        self.oname = oname
        self.nname = nname

    def visit_Call(self, node: ast.Call):
        if node.func.id == self.oname:
            result = copy.deepcopy(node)
            result.func.id = self.nname
            return result
        return node

class InterchangeArg(ast.NodeTransformer):

    def __init__(self, pos1: int, pos2: int):
        self.pos1 = pos1
        self.pos2 = pos2

    def visit_Call(self, node: ast.Call):
        result = copy.deepcopy(node)
        result.args[self.pos1], result.args[self.pos2] = result.args[self.pos2], result.args[self.pos1] 
        return result

def cleanup(d, new_dim):
    ret = {}
    for k in d:
        ret[k[0]+str(new_dim)+k[2:]] = d[k]
    return ret

def shift(d, dim):
    ret = {}
    for k in d:
        if k <= dim:
            ret[k] = d[k]
        else:
            ret[k+1] = d[k]
    return ret
