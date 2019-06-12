#!/usr/bin/python
class ASTNode:
    def __init__(self):
        self.tag = None
        self.children = []

    def set_tag(self, tg):
        self.tag = tg

class Program(ASTNode):
    def __init__(self, fs):
        self.funcs = fs
        self.children = fs

    def codegen(self):
        program_string = ''
        if self.funcs != None:
            for f in self.funcs:
                program_string += f.codegen() + '\n'
        
        return program_string

    def getdim(self):
        return len(self.funcs)

    def getdimtype(self):
        mdim = {}
        dim = len(self.funcs)

        for f in self.funcs:
            mdim[f.tag] = f.getdimtype()

        dim_type = []
        for i in xrange(dim):
            dim_type.append(mdim['d'+str(i+1)])
        
        return dim_type

    def getord(self):
        mf = {}
        dim = len(self.funcs)

        for f in self.funcs:
            mf[f.tag] = f.getord()

        order = []
        for i in xrange(dim):
            order.append(mf['d'+str(i+1)])

        return order

    def getalp(self):
        mf = {}
        dim = len(self.funcs)

        for f in self.funcs:
            mf[f.tag] = f.getalp()

        alph = []
        for i in xrange(dim):
            alph.append(mf['d'+str(i+1)])

        return alph 

class Function(ASTNode):
    def __init__(self, typ, name, params, stmts):
        self.typ    = typ
        self.name   = name
        self.params = params
        self.stmts  = stmts
        self.children = stmts
    
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

    def getord(self):

        order = ['e']
        for s in self.stmts:
            t = s.tag
            if t[0] == 'g':
                continue
            order.append(t)

        return order
    
    def getalp(self):

        alph = ['e']
        rec = []
        trs = []
        for s in self.stmts:
            t = s.tag
            if t[0] == 'g':
                continue
            elif t[0] == 'r':
                rec.append(t)
            elif t[0] == 't' or t[0] == 's':
                trs.append(t)

        alph = alph + rec + trs
        return alph

    def getdimtype(self):

        c = 0
        for s in self.stmts:
            t = s.tag
            if t[0] == 'r':
                c += 1

        return c

class Param(ASTNode):
    def __init__(self, typ, var):
        self.typ = typ
        self.var = var 
    
    def codegen(self):
        param_string = self.typ + ' ' + self.var.codegen()

        return param_string

class Stmt(ASTNode):
    pass

class IfStmt(Stmt):
    def __init__(self, cond, then, els):
        self.cond = cond
        self.then = then
        self.els  = els
        self.children = [cond, then, els]
    
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
        self.children = [expr]
    
    def codegen(self):
        return_string = 'return'
        if self.expr != None:
            return_string += ' ' + self.expr.codegen() 
        
        return return_string

class Assignment(Stmt):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.children = [lhs, rhs]

    def codegen(self):
        assign_string = self.lhs.codegen() + ' = ' + self.rhs.codegen()
        
        return assign_string

class Expr(Stmt):
    pass

class CallExpr(Expr):
    def __init__(self, callee, args):
        self.callee = callee
        self.args   = args
        self.children = args
    
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
        self.children = []
    
    def codegen(self):
        num_string = self.value

        return str(num_string)

class Const(Expr):
    def __init__(self, val):
        self.value = val
        self.children = []
    
    def codegen(self):
        return self.value

class Array(Expr):
    def __init__(self, var, index):
        self.var   = var 
        self.index = index
        self.children = [var, index]
    
    def codegen(self):
        arry_string = self.var.codegen() + '[' + self.index.codegen() + ']'

        return arry_string

class BinOp(Expr):
    def __init__(self, op, lhs, rhs):
        self.op  = op
        self.lhs = lhs
        self.rhs = rhs
        self.children = [lhs, rhs]
    
    def codegen(self):
        binop_string = self.lhs.codegen() + self.op + self.rhs.codegen()

        return binop_string

class UnOp(Expr):
    def __init__(self, op, expr):
        self.op   = op
        self.expr = expr 
        self.children = [expr]
    
    def codegen(self):
        unop_string = self.op + '(' + self.expr.codegen() + ')'

        return unop_string

class Var(Expr):
    def __init__(self, name):
        self.name = name
        self.children = []
    
    def __eq__(self, other):
        if isinstance(other, Var):
            return self.name == other.name
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def codegen(self):
        return self.name

class Field(Expr):
    def __init__(self, label):
        self.label = label 
        self.children = []
    
    def __eq__(self, other):
        if isinstance(other, Field):
            return self.label == other.label
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def codegen(self):
        return self.label

def nest():
    p1 = Param('int', Var('i')) 
    p1.set_tag('d1')
    p2 = Param('Node *', Var('n'))
    p1.set_tag('d1')
    prms = [p1, p2]
    # function 1
    g1 = IfStmt(BinOp(">=", Var('i'), Var('N')), ReturnStmt(None), None)
    g1.set_tag('g1')
    # argumets
    a1r1 = BinOp('+', Var('i'), Number(1))
    a1r1.set_tag('d1')
    a2r1 = Var('n')
    a2r1.set_tag('d2')
    # rec call expr
    r1 = CallExpr('f1', [a1r1, a2r1])
    r1.set_tag('r1')
    # argumets
    a1t1 = Var('i')
    a1t1.set_tag('d1')
    a2t1 = Var('n')
    a2t1.set_tag('d2')
    # trs call expr
    t1 = CallExpr('f2', [a1t1, a2t1])
    t1.set_tag('t1')
    # functions
    ss1 = [g1, t1, r1]
    f1  = Function('void', 'f1', prms, ss1)
    f1.set_tag('d1')
    
    # function 2
    g2 = IfStmt(BinOp("==", Var('n'), Const('NULL')), ReturnStmt(None), None)
    g2.set_tag('g2')
    # arguments
    a1r2l = Var('i')
    a1r2l.set_tag('d1')
    a2r2l = BinOp('->', Var('n'), Field('l'))
    a2r2l.set_tag('d2')
    # rec call expr left
    r2l = CallExpr('f2', [a1r2l,a2r2l])
    r2l.set_tag('r2l')
    # arguments
    a1r2r = Var('i')
    a1r2r.set_tag('d1')
    a2r2r = BinOp('->', Var('n'), Field('r'))
    a2r2r.set_tag('d1')
    # rec call expr right
    r2r = CallExpr('f2', [a1r2r,a2r2r])
    r2r.set_tag('r2r')
    # computation
    s1 = Assignment(BinOp('->', Var('n'), Array(Var('x'),Var('i'))), BinOp('+', BinOp('->', Var('n'), Array(Var('x'),Var('i'))),Number(1)))
    s1.set_tag('s1')
    # function
    ss2 = [g2, r2l, r2r, s1]
    f2 = Function('void', 'f2', prms, ss2)
    f2.set_tag('d2')
    
    # program (nest)
    p = Program([f1, f2])
    return p

def ast_test():
    p = nest()
    print p.codegen()
    print p.getdim()
    print p.getdimtype()
    print p.getalp()
    print p.getord()

if __name__ == "__main__":
    ast_test()