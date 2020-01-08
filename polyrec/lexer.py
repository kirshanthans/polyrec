from rply import LexerGenerator

class Lexer():
    def __init__(self):
        self.lg = LexerGenerator()

    def _add_tokens(self):
        # Operators
        self.lg.add('SUM', r'\+')
        # Number
        self.lg.add('NUMBER', r'\d+')
        # Ignore spaces
        self.lg.ignore('\s+')
    
    def get_lexer(self):
        self._add_tokens()
        return self.lg.build()