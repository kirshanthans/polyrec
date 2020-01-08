from rply import ParserGenerator
from polyrec.ast import BinOp, Number

class Parser():
    def __init__(self):
        self.pg = ParserGenerator(
            ['NUMBER', 'SUM']
            )

    def parse(self):
        @self.pg.production('expression : expression SUM expression')
        def expression(p):
            lhs = p[0]
            rhs = p[2]
            return BinOp(p[1].value, lhs, rhs)
        
        @self.pg.production('expression : NUMBER')
        def number(p):
            return Number(p[0].value)

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()