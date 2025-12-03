import sys
from lark import Lark, Transformer, Tree
import lark
import os

#print(f"Python version: {sys.version}")
#print(f"Lark version: {lark.__version__}")

#  run/execute/interpret source code
def interpret(source_code):
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    if ast[0] == 'prog':
        # Handle sequencing: evaluate each expression and join with ;;
        result_parts = []
        current = ast
        while current[0] == 'prog':
            expr = current[1]
            result_ast = evaluate(expr)
            result_parts.append(linearize(result_ast))
            current = current[2]
        # Last expression
        result_ast = evaluate(current)
        result_parts.append(linearize(result_ast))
        return ' ;; '.join(result_parts)
    else:
        result_ast = evaluate(ast)
        result = linearize(result_ast)
        return result

# convert concrete syntax to CST
parser = Lark(open("grammar.lark").read(), parser='lalr')

# convert CST to AST
class LambdaCalculusTransformer(Transformer):
    def lam(self, args):
        name, body = args
        return ('lam', str(name), body)

    def app(self, args):
        return ('app', *args)

    def var(self, args):
        token, = args
        return ('var', str(token))

    def num(self, args):
        token, = args
        return ('num', float(str(token)))

    def plus(self, args):
        return ('plus', *args)

    def minus(self, args):
        return ('minus', *args)

    def times(self, args):
        return ('times', *args)

    def neg(self, args):
        expr, = args
        return ('neg', expr)

    def leq(self, args):
        return ('leq', *args)

    def eq(self, args):
        return ('eq', *args)

    def if_expr(self, args):
        return ('if', *args)

    def let_expr(self, args):
        name, val, body = args
        return ('let', str(name), val, body)

    def letrec_expr(self, args):
        name, val, body = args
        return ('letrec', str(name), val, body)

    def fix_expr(self, args):
        expr, = args
        return ('fix', expr)

    def prog(self, args):
        return ('prog', *args)

    def nil(self, args):
        return ('nil',)

    def cons(self, args):
        return ('cons', *args)

    def hd(self, args):
        expr, = args
        return ('hd', expr)

    def tl(self, args):
        expr, = args
        return ('tl', expr)

    def NAME(self, token):
        return str(token)

# reduce AST to normal form
def evaluate(tree):
    if tree[0] == 'app':
        e1 = evaluate(tree[1])
        if e1[0] == 'lam':
            body = e1[2]
            name = e1[1]
            arg = tree[2]
            rhs = substitute(body, name, arg)
            result = evaluate(rhs)
            pass
        else:
            result = ('app', e1, tree[2])
            pass
    elif tree[0] == 'plus':
        e1 = evaluate(tree[1])
        e2 = evaluate(tree[2])
        if e1[0] == 'num' and e2[0] == 'num':
            result = ('num', e1[1] + e2[1])
        else:
            result = ('plus', e1, e2)
    elif tree[0] == 'minus':
        e1 = evaluate(tree[1])
        e2 = evaluate(tree[2])
        if e1[0] == 'num' and e2[0] == 'num':
            result = ('num', e1[1] - e2[1])
        else:
            result = ('minus', e1, e2)
    elif tree[0] == 'times':
        e1 = evaluate(tree[1])
        e2 = evaluate(tree[2])
        if e1[0] == 'num' and e2[0] == 'num':
            result = ('num', e1[1] * e2[1])
        else:
            result = ('times', e1, e2)
    elif tree[0] == 'neg':
        e1 = evaluate(tree[1])
        if e1[0] == 'num':
            result = ('num', -e1[1])
        else:
            result = ('neg', e1)
    elif tree[0] == 'leq':
        e1 = evaluate(tree[1])
        e2 = evaluate(tree[2])
        if e1[0] == 'num' and e2[0] == 'num':
            result = ('num', 1.0 if e1[1] <= e2[1] else 0.0)
        else:
            result = ('leq', e1, e2)
    elif tree[0] == 'eq':
        e1 = evaluate(tree[1])
        e2 = evaluate(tree[2])
        # Handle both numbers and lists for equality
        if e1[0] == 'num' and e2[0] == 'num':
            result = ('num', 1.0 if e1[1] == e2[1] else 0.0)
        elif e1[0] == 'nil' and e2[0] == 'nil':
            result = ('num', 1.0)
        elif e1[0] == 'nil' or e2[0] == 'nil':
            # One is nil, one is not - they're not equal
            result = ('num', 0.0)
        elif e1[0] == 'cons' and e2[0] == 'cons':
            # Compare cons cells structurally
            head_eq = evaluate(('eq', e1[1], e2[1]))
            tail_eq = evaluate(('eq', e1[2], e2[2]))
            if head_eq[0] == 'num' and tail_eq[0] == 'num':
                result = ('num', 1.0 if (head_eq[1] != 0 and tail_eq[1] != 0) else 0.0)
            else:
                result = ('eq', e1, e2)
        else:
            result = ('eq', e1, e2)
    elif tree[0] == 'if':
        cond = evaluate(tree[1])
        # Treat 0 as false, everything else (including lists) as true
        is_true = False
        if cond[0] == 'num':
            is_true = cond[1] != 0
        elif cond[0] == 'nil':
            is_true = False  # empty list is false
        else:
            is_true = True  # non-empty lists, lambdas, etc. are true
        
        if is_true:
            result = evaluate(tree[2])
        else:
            result = evaluate(tree[3])
    elif tree[0] == 'let':
        name = tree[1]
        val = tree[2]
        body = tree[3]
        # let x = e1 in e2 --> (\x.e2) e1
        lam_expr = ('lam', name, body)
        app_expr = ('app', lam_expr, val)
        result = evaluate(app_expr)
    elif tree[0] == 'letrec':
        name = tree[1]
        val = tree[2]
        body = tree[3]
        # let rec f = e1 in e2 --> let f = (fix (\f. e1)) in e2
        lam_expr = ('lam', name, val)
        fix_expr = ('fix', lam_expr)
        let_expr = ('let', name, fix_expr, body)
        result = evaluate(let_expr)
    elif tree[0] == 'fix':
        f = evaluate(tree[1])
        if f[0] == 'lam':
            # fix F --> F (fix F)
            fix_f = ('fix', f)
            app_expr = ('app', f, fix_f)
            result = evaluate(app_expr)
        else:
            result = ('fix', f)
    elif tree[0] == 'nil':
        result = ('nil',)
    elif tree[0] == 'cons':
        e1 = evaluate(tree[1])
        e2 = evaluate(tree[2])
        result = ('cons', e1, e2)
    elif tree[0] == 'hd':
        e = evaluate(tree[1])
        if e[0] == 'cons':
            result = e[1]  # head of a:b is a
        else:
            result = ('hd', e)
    elif tree[0] == 'tl':
        e = evaluate(tree[1])
        if e[0] == 'cons':
            result = e[2]  # tail of a:b is b
        else:
            result = ('tl', e)
    else:
        result = tree
        pass
    return result

# generate a fresh name 
# needed eg for \y.x [y/x] --> \z.y where z is a fresh name)
class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        # user defined names start with lower case (see the grammar), thus 'Var' is fresh
        return 'Var' + str(self.counter)

name_generator = NameGenerator()

# for beta reduction (capture-avoiding substitution)
# 'replacement' for 'name' in 'tree'
def substitute(tree, name, replacement):
    # tree [replacement/name] = tree with all instances of 'name' replaced by 'replacement'
    if tree[0] == 'var':
        if tree[1] == name:
            return replacement # n [r/n] --> r
        else:
            return tree # x [r/n] --> x
    elif tree[0] == 'num':
        return tree  # numbers are unchanged
    elif tree[0] == 'lam':
        if tree[1] == name:
            return tree # \n.e [r/n] --> \n.e
        else:
            fresh_name = name_generator.generate()
            return ('lam', fresh_name, substitute(substitute(tree[2], tree[1], ('var', fresh_name)), name, replacement))
            # \x.e [r/n] --> (\fresh.(e[fresh/x])) [r/n]
    elif tree[0] == 'app':
        return ('app', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'plus':
        return ('plus', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'minus':
        return ('minus', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'times':
        return ('times', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'neg':
        return ('neg', substitute(tree[1], name, replacement))
    elif tree[0] == 'leq':
        return ('leq', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'eq':
        return ('eq', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'if':
        return ('if', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement), substitute(tree[3], name, replacement))
    elif tree[0] == 'let':
        # let x = e1 in e2: need to handle shadowing
        var_name = tree[1]
        val = tree[2]
        body = tree[3]
        if var_name == name:
            
            return ('let', var_name, substitute(val, name, replacement), body)
        else:
            return ('let', var_name, substitute(val, name, replacement), substitute(body, name, replacement))
    elif tree[0] == 'letrec':
        var_name = tree[1]
        val = tree[2]
        body = tree[3]
        if var_name == name:
            
            return ('letrec', var_name, val, body)
        else:
            return ('letrec', var_name, substitute(val, name, replacement), substitute(body, name, replacement))
    elif tree[0] == 'fix':
        return ('fix', substitute(tree[1], name, replacement))
    elif tree[0] == 'nil':
        return ('nil',)
    elif tree[0] == 'cons':
        return ('cons', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'hd':
        return ('hd', substitute(tree[1], name, replacement))
    elif tree[0] == 'tl':
        return ('tl', substitute(tree[1], name, replacement))
    elif tree[0] == 'prog':
        return ('prog', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    else:
        raise Exception('Unknown tree', tree)

def linearize(ast):
    if ast[0] == 'var':
        return ast[1]
    elif ast[0] == 'num':
        return str(ast[1])
    elif ast[0] == 'lam':
        return "(" + "\\" + ast[1] + "." + linearize(ast[2]) + ")"
    elif ast[0] == 'app':
        return "(" + linearize(ast[1]) + " " + linearize(ast[2]) + ")"
    elif ast[0] == 'plus':
        return "(" + linearize(ast[1]) + " + " + linearize(ast[2]) + ")"
    elif ast[0] == 'minus':
        return "(" + linearize(ast[1]) + " - " + linearize(ast[2]) + ")"
    elif ast[0] == 'times':
        return "(" + linearize(ast[1]) + " * " + linearize(ast[2]) + ")"
    elif ast[0] == 'neg':
        return "(" + "-" + linearize(ast[1]) + ")"
    elif ast[0] == 'leq':
        return "(" + linearize(ast[1]) + " <= " + linearize(ast[2]) + ")"
    elif ast[0] == 'eq':
        return "(" + linearize(ast[1]) + " == " + linearize(ast[2]) + ")"
    elif ast[0] == 'if':
        return "(if " + linearize(ast[1]) + " then " + linearize(ast[2]) + " else " + linearize(ast[3]) + ")"
    elif ast[0] == 'let':
        return "(let " + ast[1] + " = " + linearize(ast[2]) + " in " + linearize(ast[3]) + ")"
    elif ast[0] == 'letrec':
        return "(letrec " + ast[1] + " = " + linearize(ast[2]) + " in " + linearize(ast[3]) + ")"
    elif ast[0] == 'fix':
        return "(fix " + linearize(ast[1]) + ")"
    elif ast[0] == 'nil':
        return "#"
    elif ast[0] == 'cons':
        return "(" + linearize(ast[1]) + " : " + linearize(ast[2]) + ")"
    elif ast[0] == 'hd':
        return "(hd " + linearize(ast[1]) + ")"
    elif ast[0] == 'tl':
        return "(tl " + linearize(ast[1]) + ")"
    elif ast[0] == 'prog':
        return linearize(ast[1]) + " ;; " + linearize(ast[2])
    else:
        return ast

def main():
    if len(sys.argv) != 2:
        #print("Usage: python interpreter.py <filename or expression>", file=sys.stderr)
        sys.exit(1)

    input_arg = sys.argv[1]

    if os.path.isfile(input_arg):
        # If the input is a valid file path, read from the file
        with open(input_arg, 'r') as file:
            expression = file.read()
    else:
        # Otherwise, treat the input as a direct expression
        expression = input_arg

    result = interpret(expression)
    print(f"\033[95m{result}\033[0m")

if __name__ == "__main__":
    main()
