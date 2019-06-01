#!/usr/bin/python
class ASTNode:
    def __init__(self):
        pass

class Function(ASTNode):
    def __init__(self, typ, name, params, stmts):
        self.typ    = typ
        self.name   = name
        self.params = params
        self.stmts  = stmts

    def codegen(self):
        param_string = ''
        if self.params != None:
            param_string = self.params[0].codegen() 
            for p in self.params[1:]:
                param_string += ', ' + p.codegen()
        
        body_string = ''
        if self.stmts != None:
            body_string = self.stmts[0].codegen() + ';'
            for s in self.stmts[1:]:
                body_string += '\n' + s.codegen() + ';'
            body_string += '\n'
        
        func_string  = self.typ + ' ' + self.name + '(' + param_string + ')\n'
        func_string += '{\n'
        func_string += body_string + '}\n'
        
        return func_string

class Param(ASTNode):
    def __init__(self, typ, var):
        self.typ = typ
        self.var = var 
    
    def codegen(self):
        param_string = self.typ + ' ' + self.var.codegen()

        return param_string

class Stmt(ASTNode):
    def __init__(self):
        pass

class IfStmt(Stmt):
    def __init__(self, cond, then, els):
        self.cond = cond
        self.then = then
        self.els  = els
    
    def codegen(self):
        cond_string = self.cond.codegen()
        then_string = self.then.codegen()
        if_string = 'if ( ' + cond_string + ' ){\n\t' + then_string + ';\n}'
        
        if self.els != None:
            els_string = self.els.codegen()
            if_string += 'else {\n\t' + els_string + '\n}' 

        return if_string

class Return(Stmt):
    def __init__(self, expr):
        self.expr = expr
    
    def codegen(self):
        return_string = 'return ' + self.expr.codegen()
        
        return return_string

class CallStmt(Stmt):
    def __init__(self, callee, exprs):
        self.callee = callee
        self.exprs  = exprs 
    
    def codegen(self):
        pass

class Assignment(Stmt):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def codegen(self):
        pass

class Expr(Stmt):
    def __init__(self):
        pass

    def codegen(self):
        return ''

class Number(Expr):
    def __init__(self, value):
        self.value = value
    
    def codegen(self):
        pass

class Array(Expr):
    def __init__(self, var, index):
        self.var   = var 
        self.index = index
    
    def codegen(self):
        pass

class BinOp(Expr):
    def __init__(self, op, lhs, rhs):
        self.op  = op
        self.lhs = rhs
        self.rhs = rhs
    
    def codegen(self):
        pass

class Var(Expr):
    def __init__(self, name):
        self.name = name
    
    def codegen(self):
        return self.name

class Field(Expr):
    def __init__(self, label):
        self.label = label 
    
    def codegen(self):
        return self.label

def main():
    ps = [Param('int', Var('i')), Param('Node *', Var('n'))]
    ss = [IfStmt(Expr(), Return(Expr()), None)]
    f  = Function('void', 'f1', ps, ss)
    print f.codegen()


if __name__ == "__main__":
    main()