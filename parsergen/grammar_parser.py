# Code @generated by parsergen; do not edit!
from parsergen.parser_utils import GeneratedParser, TokenStream, Node, Filler
from parsergen.parser_utils import memoize, memoize_left_rec
from functools import reduce

from .grammar_utils import *

class GrammarParser(GeneratedParser):
    @memoize
    def parser_definition(self):
        pos = self.mark()
        """
        s=section* EOF { ParserDefinition(s) };
        """
        parts = []
        for _ in range(1):
            part = self._loop_0()
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
            s = parts[0]
            return ParserDefinition(s)
        self.goto(pos)
        
        return None
        
    def _loop_0(self):
        """
        section*
        """
        children = []
        while True:
            pos = self.mark()
            part = self.section()
            if self.match(part): children.append(part)
            else:
                self.goto(pos)
                break
        return children
    @memoize
    def section(self):
        pos = self.mark()
        """
        s=statement { s };
        """
        parts = []
        for _ in range(1):
            part = self.statement()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            s = parts[0]
            return s
        self.goto(pos)
        
        """
        s=configuration { s };
        """
        parts = []
        for _ in range(1):
            part = self.configuration()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            s = parts[0]
            return s
        self.goto(pos)
        
        return None
        
    @memoize
    def configuration(self):
        pos = self.mark()
        """
        AT name=ID EQ value=STRING { ConfigurationCall(name.value, value.value) };
        """
        parts = []
        for _ in range(1):
            part = self.expect('AT')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('ID')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('EQ')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('STRING')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            name = parts[1]
            value = parts[3]
            return ConfigurationCall(name.value, value.value)
        self.goto(pos)
        
        return None
        
    @memoize
    def statement(self):
        pos = self.mark()
        """
        n=(ID? COLON)? es=expr* a=ACTION? TERMINATE { Statement(
            n[0].value if not isinstance(n, Filler) and not isinstance(n[0], Filler) else "<>", 
            es, 
            action=a.value if not isinstance(a, Filler) else None
        ) };
        """
        parts = []
        for _ in range(1):
            part = self._maybe_1()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self._loop_2()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self._maybe_3()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('TERMINATE')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            n = parts[0]
            es = parts[1]
            a = parts[2]
            return Statement(
                n[0].value if not isinstance(n, Filler) and not isinstance(n[0], Filler) else "<>", 
                es, 
                action=a.value if not isinstance(a, Filler) else None
            )
        self.goto(pos)
        
        return None
        
    def _maybe_1(self):
        """
        (ID? COLON)?
        """
        pos = self.mark()
        part = self._expr_list_4()
        if self.match(part): return part
        self.goto(pos)
        return Filler()
    def _expr_list_4(self):
        """
        (ID? COLON)
        """
        pos = self.mark()
        parts = []
        for _ in range(1):
            part = self._maybe_5()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('COLON')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            return parts
        self.goto(pos)
        return None
    def _maybe_5(self):
        """
        ID?
        """
        pos = self.mark()
        part = self.expect('ID')
        if self.match(part): return part
        self.goto(pos)
        return Filler()
    def _loop_2(self):
        """
        expr*
        """
        children = []
        while True:
            pos = self.mark()
            part = self.expr()
            if self.match(part): children.append(part)
            else:
                self.goto(pos)
                break
        return children
    def _maybe_3(self):
        """
        ACTION?
        """
        pos = self.mark()
        part = self.expect('ACTION')
        if self.match(part): return part
        self.goto(pos)
        return Filler()
    @memoize_left_rec
    def expr_list(self):
        pos = self.mark()
        """
        es=expr* { ExprList(es) };
        """
        parts = []
        for _ in range(1):
            part = self._loop_6()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            es = parts[0]
            return ExprList(es)
        self.goto(pos)
        
        return None
        
    def _loop_6(self):
        """
        expr*
        """
        children = []
        while True:
            pos = self.mark()
            part = self.expr()
            if self.match(part): children.append(part)
            else:
                self.goto(pos)
                break
        return children
    @memoize_left_rec
    def expr(self):
        pos = self.mark()
        """
        name=(ID EQ)? v=or_op { NamedItem(name[0].value, v) if not isinstance(name, Filler) else v };
        """
        parts = []
        for _ in range(1):
            part = self._maybe_7()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.or_op()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            name = parts[0]
            v = parts[1]
            return NamedItem(name[0].value, v) if not isinstance(name, Filler) else v
        self.goto(pos)
        
        return None
        
    def _maybe_7(self):
        """
        (ID EQ)?
        """
        pos = self.mark()
        part = self._expr_list_8()
        if self.match(part): return part
        self.goto(pos)
        return Filler()
    def _expr_list_8(self):
        """
        (ID EQ)
        """
        pos = self.mark()
        parts = []
        for _ in range(1):
            part = self.expect('ID')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expect('EQ')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            return parts
        self.goto(pos)
        return None
    @memoize_left_rec
    def or_op(self):
        pos = self.mark()
        """
        v=star_op others=(OR star_op)* { OrOp(exprs=[v]+[o[1] for o in others]) if len(others) > 0 else v };
        """
        parts = []
        for _ in range(1):
            part = self.star_op()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self._loop_9()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            v = parts[0]
            others = parts[1]
            return OrOp(exprs=[v]+[o[1] for o in others]) if len(others) > 0 else v
        self.goto(pos)
        
        return None
        
    def _loop_9(self):
        """
        (OR star_op)*
        """
        children = []
        while True:
            pos = self.mark()
            part = self._expr_list_10()
            if self.match(part): children.append(part)
            else:
                self.goto(pos)
                break
        return children
    def _expr_list_10(self):
        """
        (OR star_op)
        """
        pos = self.mark()
        parts = []
        for _ in range(1):
            part = self.expect('OR')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.star_op()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            return parts
        self.goto(pos)
        return None
    @memoize_left_rec
    def star_op(self):
        pos = self.mark()
        """
        v=plus_op s=STAR? { ZeroOrMore(v) if not isinstance(s, Filler) else v };
        """
        parts = []
        for _ in range(1):
            part = self.plus_op()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self._maybe_11()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            v = parts[0]
            s = parts[1]
            return ZeroOrMore(v) if not isinstance(s, Filler) else v
        self.goto(pos)
        
        return None
        
    def _maybe_11(self):
        """
        STAR?
        """
        pos = self.mark()
        part = self.expect('STAR')
        if self.match(part): return part
        self.goto(pos)
        return Filler()
    @memoize_left_rec
    def plus_op(self):
        pos = self.mark()
        """
        v=qmark_op s=PLUS? { OneOrMore(v) if not isinstance(s, Filler) else v };
        """
        parts = []
        for _ in range(1):
            part = self.qmark_op()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self._maybe_12()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            v = parts[0]
            s = parts[1]
            return OneOrMore(v) if not isinstance(s, Filler) else v
        self.goto(pos)
        
        return None
        
    def _maybe_12(self):
        """
        PLUS?
        """
        pos = self.mark()
        part = self.expect('PLUS')
        if self.match(part): return part
        self.goto(pos)
        return Filler()
    @memoize_left_rec
    def qmark_op(self):
        pos = self.mark()
        """
        v=term s=QMARK? { ZeroOrOne(v) if not isinstance(s, Filler) else v };
        """
        parts = []
        for _ in range(1):
            part = self.term()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self._maybe_13()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            v = parts[0]
            s = parts[1]
            return ZeroOrOne(v) if not isinstance(s, Filler) else v
        self.goto(pos)
        
        return None
        
    def _maybe_13(self):
        """
        QMARK?
        """
        pos = self.mark()
        part = self.expect('QMARK')
        if self.match(part): return part
        self.goto(pos)
        return Filler()
    @memoize_left_rec
    def term(self):
        pos = self.mark()
        """
        AND f=factor { AndPredicate(f) };
        """
        parts = []
        for _ in range(1):
            part = self.expect('AND')
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
            f = parts[1]
            return AndPredicate(f)
        self.goto(pos)
        
        """
        NOT f=factor { NotPredicate(f) };
        """
        parts = []
        for _ in range(1):
            part = self.expect('NOT')
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
            f = parts[1]
            return NotPredicate(f)
        self.goto(pos)
        
        """
        f=factor { f };
        """
        parts = []
        for _ in range(1):
            part = self.factor()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            f = parts[0]
            return f
        self.goto(pos)
        
        return None
        
    @memoize_left_rec
    def factor(self):
        pos = self.mark()
        """
        i=item { i };
        """
        parts = []
        for _ in range(1):
            part = self.item()
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            i = parts[0]
            return i
        self.goto(pos)
        
        """
        LPAREN es=expr_list RPAREN { es };
        """
        parts = []
        for _ in range(1):
            part = self.expect('LPAREN')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            part = self.expr_list()
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
            es = parts[1]
            return es
        self.goto(pos)
        
        return None
        
    @memoize
    def item(self):
        pos = self.mark()
        """
        i=ID { StatementPointer(i.value) };
        """
        parts = []
        for _ in range(1):
            part = self.expect('ID')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            i = parts[0]
            return StatementPointer(i.value)
        self.goto(pos)
        
        """
        i=TOKEN { TokenPointer(i.value) };
        """
        parts = []
        for _ in range(1):
            part = self.expect('TOKEN')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            i = parts[0]
            return TokenPointer(i.value)
        self.goto(pos)
        
        """
        i=STRING { ConstantString(i.value) };
        """
        parts = []
        for _ in range(1):
            part = self.expect('STRING')
            if not self.match(part):
                self.fail()
                break
            parts.append(part)
            # match:
            i = parts[0]
            return ConstantString(i.value)
        self.goto(pos)
        
        return None
        
