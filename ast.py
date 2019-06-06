#!/usr/bin/python
class ASTNode:
    def __init__(self):
        self.tag = None

    def tag(self, tg):
        self.tag = tg

class Program(ASTNode):
    def __init__(self, fs):
        self.funcs = fs

    def codegen(self):
        program_string = ''
        if self.funcs != None:
            for f in self.funcs:
                program_string += f.codegen() + '\n'
        
        return program_string

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
            body_string = '\t' + self.stmts[0].codegen()
            if body_string[-1] != '}':
                body_string += ';'
            for s in self.stmts[1:]:
                body_string += '\n\t' + s.codegen()
                if body_string[-1] != '}':
                    body_string += ';'
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
        if_string = 'if (' + cond_string + ') ' + then_string 
        
        if self.els != None:
            if_string = 'if (' + cond_string + '){\n\t' + then_string + ';\n}'
            els_string = self.els.codegen()
            if_string += 'else {\n\t' + els_string + ';\n}' 

        return if_string

class ReturnStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr
    
    def codegen(self):
        return_string = 'return'
        if self.expr != None:
            return_string += ' ' + self.expr.codegen() 
        
        return return_string

class Assignment(Stmt):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def codegen(self):
        assign_string = self.lhs.codegen() + ' = ' + self.rhs.codegen()
        
        return assign_string

class Expr(Stmt):
    def __init__(self):
        pass

class CallExpr(Expr):
    def __init__(self, callee, args):
        self.callee = callee
        self.args   = args
    
    def codegen(self):
        name_string = self.callee
        arg_string  = ''
        if self.args != None:
            arg_string = self.args[0].codegen() 
            for a in self.args[1:]:
                arg_string += ', ' + a.codegen()
        
        call_string = name_string + '(' + arg_string + ')'

        return call_string

class Number(Expr):
    def __init__(self, value):
        self.value = value
    
    def codegen(self):
        num_string = self.value

        return str(num_string)

class Const(Expr):
    def __init__(self, val):
        self.value = val
    
    def codegen(self):
        return self.value

class Array(Expr):
    def __init__(self, var, index):
        self.var   = var 
        self.index = index
    
    def codegen(self):
        arry_string = self.var.codegen() + '[' + self.index.codegen() + ']'

        return arry_string

class BinOp(Expr):
    def __init__(self, op, lhs, rhs):
        self.op  = op
        self.lhs = lhs
        self.rhs = rhs
    
    def codegen(self):
        binop_string = self.lhs.codegen() + self.op + self.rhs.codegen()

        return binop_string

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

def ast_test():
    # function 1
    g1 = IfStmt(BinOp("<=", Var('i'), Var('N')), ReturnStmt(None), None)
    g1.tag('g1')
    r1 = CallExpr('f1', [BinOp('+', Var('i'), Number(1)), Var('n')])
    r1.tag('r1')
    t1 = CallExpr('f2', [Var('i'), Var('n')])
    t1.tag('t1')
    ss1 = [g1, t1, r1]
    f1  = Function('void', 'f1', [Param('int', Var('i')), Param('Node *', Var('n'))], [g1, t1, r1])
    f1.tag('f1')
    # function 2
    g2 = IfStmt(BinOp("==", Var('n'), Const('NULL')), ReturnStmt(None), None)
    g2.tag('g2')
    r2l = CallExpr('f2', [Var('i'), BinOp('->', Var('n'), Field('l'))])
    r2l.tag('r2l')
    r2r = CallExpr('f2', [Var('i'), BinOp('->', Var('n'), Field('r'))])
    r2r.tag('r2r')
    s1 = Assignment(BinOp('->', Var('n'), Array(Var('x'),Var('i'))), BinOp('+', BinOp('->', Var('n'), Array(Var('x'),Var('i'))),Number(1)))
    s1.tag('s1')
    f2 = Function('void', 'f2', [Param('int', Var('i')), Param('Node *', Var('n'))], [g2, r2l, r2r, s1])
    f2.tag('f2')
    # program (nest)
    p = Program([f1, f2])

    print p.codegen()

if __name__ == "__main__":
    ast_test()