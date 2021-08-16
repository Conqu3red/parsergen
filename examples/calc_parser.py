# Code @generated by parsergen; do not edit!
from parsergen.parser_utils import GeneratedParser, TokenStream, Node, Filler
from parsergen.parser_utils import memoize, memoize_left_rec
from functools import reduce
class CalcParser(GeneratedParser):
    @memoize
    def start(self):
        pos = self.mark()
        """
        e=expr EOF { e };
        """
        parts = []
        for _ in range(1):
            part = self.expr()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('EOF')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            e = parts[0]
            return e
        self.goto(pos)
        
        return None
        
    @memoize_left_rec
    def expr(self):
        pos = self.mark()
        """
        left=expr ADD right=term { left + right };
        """
        parts = []
        for _ in range(1):
            part = self.expr()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('ADD')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.term()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            left = parts[0]
            right = parts[2]
            return left + right
        self.goto(pos)
        
        """
        left=expr SUB right=term { left - right };
        """
        parts = []
        for _ in range(1):
            part = self.expr()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('SUB')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.term()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            left = parts[0]
            right = parts[2]
            return left - right
        self.goto(pos)
        
        """
        e=term { e };
        """
        parts = []
        for _ in range(1):
            part = self.term()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            e = parts[0]
            return e
        self.goto(pos)
        
        return None
        
    @memoize_left_rec
    def term(self):
        pos = self.mark()
        """
        left=term MUL right=factor { left * right };
        """
        parts = []
        for _ in range(1):
            part = self.term()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('MUL')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.factor()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            left = parts[0]
            right = parts[2]
            return left * right
        self.goto(pos)
        
        """
        left=term DIV right=factor { left / right };
        """
        parts = []
        for _ in range(1):
            part = self.term()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('DIV')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.factor()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            left = parts[0]
            right = parts[2]
            return left / right
        self.goto(pos)
        
        """
        e=factor { e };
        """
        parts = []
        for _ in range(1):
            part = self.factor()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            e = parts[0]
            return e
        self.goto(pos)
        
        return None
        
    @memoize_left_rec
    def factor(self):
        pos = self.mark()
        """
        left=item POW right=factor { left ** right };
        """
        parts = []
        for _ in range(1):
            part = self.item()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('POW')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.factor()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            left = parts[0]
            right = parts[2]
            return left ** right
        self.goto(pos)
        
        """
        e=item { e };
        """
        parts = []
        for _ in range(1):
            part = self.item()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            e = parts[0]
            return e
        self.goto(pos)
        
        return None
        
    @memoize_left_rec
    def item(self):
        pos = self.mark()
        """
        n=INT { int(n.value) };
        """
        parts = []
        for _ in range(1):
            part = self.expect('INT')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            n = parts[0]
            return int(n.value)
        self.goto(pos)
        
        """
        LPAREN e=expr RPAREN { e };
        """
        parts = []
        for _ in range(1):
            part = self.expect('LPAREN')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expr()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('RPAREN')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            e = parts[1]
            return e
        self.goto(pos)
        
        return None
        
