from interpreter import interpret, substitute, evaluate, LambdaCalculusTransformer, parser, linearize
from colorama import Fore, Style

# convert concrete syntax to AST
def ast(source_code):
    return LambdaCalculusTransformer().transform(parser.parse(source_code))

def test_parse():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    assert ast(r"x") == ('var', 'x')
    print(f"AST {MAGENTA}x{RESET} == ('var', 'x')")
    
    assert ast(r"(((x)) ((y)))") == ('app', ('var', 'x'), ('var', 'y'))
    print(f"AST {MAGENTA}(((x)) ((y))){RESET} == ('app', ('var', 'x'), ('var', 'y'))")
    
    assert ast(r"x y") == ('app', ('var', 'x'), ('var', 'y'))
    print(f"AST {MAGENTA}x y{RESET} == ('app', ('var', 'x'), ('var', 'y'))")
    
    assert ast(r"x y z") == ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z'))
    print(f"AST {MAGENTA}x y z{RESET} == ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z'))")
    
    assert ast(r"\x.y") == ('lam', 'x', ('var', 'y'))
    print(f"AST {MAGENTA}\\x.y{RESET} == ('lam', 'x', ('var', 'y'))")
    
    assert ast(r"\x.x y") == ('lam', 'x', ('app', ('var', 'x'), ('var', 'y')))
    print(f"AST {MAGENTA}\\x.x y{RESET} == ('lam', 'x', ('app', ('var', 'x'), ('var', 'y')))")
    
    assert ast(r"\x.x y z") == ('lam', 'x', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))
    print(f"AST {MAGENTA}\\x.x y z{RESET} == ('lam', 'x', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))")
    
    assert ast(r"\x. \y. \z. x y z") == ('lam', 'x', ('lam', 'y', ('lam', 'z', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))))
    print(f"AST {MAGENTA}\\x. \\y. \\z. x y z{RESET} == ('lam', 'x', ('lam', 'y', ('lam', 'z', ('app', ('app', ('var', 'x'), ('var', 'y')), ('var', 'z')))))")
    
    assert ast(r"\x. x a") == ('lam', 'x', ('app', ('var', 'x'), ('var', 'a')))
    print(f"AST {MAGENTA}\\x. x a{RESET} == ('lam', 'x', ('app', ('var', 'x'), ('var', 'a')))")
    
    assert ast(r"\x. x (\y. y)") == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('var', 'y'))))
    print(f"AST {MAGENTA}\\x. x (\\y. y){RESET} == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('var', 'y'))))")
    
    assert ast(r"\x. x (\y. y (\z. z z2))") == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('app', ('var', 'y'), ('lam', 'z', ('app', ('var', 'z'), ('var', 'z2')))))))
    print(f"AST {MAGENTA}\\x. x (\\y. y (\\z. z z2)){RESET} == ('lam', 'x', ('app', ('var', 'x'), ('lam', 'y', ('app', ('var', 'y'), ('lam', 'z', ('app', ('var', 'z'), ('var', 'z2')))))))")
    
    assert ast(r"\x. y z (\a. b (\c. d e f))") == ('lam', 'x', ('app', ('app', ('var', 'y'), ('var', 'z')), ('lam', 'a', ('app', ('var', 'b'), ('lam', 'c', ('app', ('app', ('var', 'd'), ('var', 'e')), ('var', 'f')))))))
    print(f"AST {MAGENTA}\\x. y z (\\a. b (\\c. d e f)){RESET} == ('lam', 'x', ('app', ('app', ('var', 'y'), ('var', 'z')), ('lam', 'a', ('app', ('var', 'b'), ('lam', 'c', ('app', ('app', ('var', 'd'), ('var', 'e')), ('var', 'f')))))))")
    
    print("\nParser: All tests passed!\n")

def test_substitute():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # x [y/x] = y
    assert substitute(('var', 'x'), 'x', ('var', 'y')) == ('var', 'y')
    print(f"SUBST {MAGENTA}x [y/x]{RESET} == ('var', 'y')")
    
    # \x.x [y/x] = (\x.x)
    assert substitute(('lam', 'x', ('var', 'x')), 'x', ('var', 'y')) == ('lam', 'x', ('var', 'x'))
    print(f"SUBST {MAGENTA}\\x.x [y/x]{RESET} == ('lam', 'x', ('var', 'x'))")
    
    # (x x) [y/x] = y y
    assert substitute(('app', ('var', 'x'), ('var', 'x')), 'x', ('var', 'y')) == ('app', ('var', 'y'), ('var', 'y'))
    print(f"SUBST {MAGENTA}(x x) [y/x]{RESET} == ('app', ('var', 'y'), ('var', 'y'))")
    
    # (\y. x ) [y/x] = (\Var1. y)
    assert substitute(('lam', 'y', ('var', 'x')), 'x', ('var', 'y')) == ('lam', 'Var1', ('var', 'y'))
    print(f"SUBST {MAGENTA}\\y. x [y/x]{RESET} == ('lam', 'Var1', ('var', 'y'))")

    print("\nsubstitute(): All tests passed!\n")

def test_evaluate():
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    
    # EVAL x == x
    assert linearize(evaluate(ast(r"x"))) == "x"
    print(f"EVAL {MAGENTA}x{RESET} == x")
    
    # EVAL x y == (x y)
    assert linearize(evaluate(ast(r"x y"))) == "(x y)"
    print(f"EVAL {MAGENTA}x y{RESET} == (x y)")
    
    # EVAL x y z == ((x y) z)
    assert linearize(evaluate(ast(r"x y z"))) == "((x y) z)"
    print(f"EVAL {MAGENTA}x y z{RESET} == ((x y) z)")
    
    # EVAL x (y z) == (x (y z))
    assert linearize(evaluate(ast(r"x (y z)"))) == "(x (y z))"
    print(f"EVAL {MAGENTA}x (y z){RESET} == (x (y z))")
    
    # EVAL \x.y == \x.y
    assert linearize(evaluate(ast(r"\x.y"))) == r"(\x.y)"
    print(f"EVAL {MAGENTA}\\x.y{RESET} == \\x.y")
    
    # EVAL (\x.x) y == y
    assert linearize(evaluate(ast(r"(\x.x) y"))) == "y"
    print(f"EVAL {MAGENTA}(\\x.x) y{RESET} == y")

    print("\nevaluate(): All tests passed!\n")

def test_interpret():
    print(f"Testing x --> {interpret('x')}")
    print(f"Testing x y --> {interpret('x y')}")
    input=r"\x.x"; output = interpret(input); print(f"Testing {input} --> {output}")
    input=r"(\x.x) y"; output = interpret(input); print(f"Testing {input} --> {output}")
    input=r"(\x.\y.x y) y"; output = interpret(input); print(f"Testing {input} --> {output}")

    print("\ninterpret(): All tests passed!\n")

def test_arithmetic():
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    assert interpret("1+2") == "3.0"
    print(f"ARITH {BLUE}1+2{RESET} == 3.0")
    
    assert interpret("3*4") == "12.0"
    print(f"ARITH {BLUE}3*4{RESET} == 12.0")
    
    assert interpret("2+3*4") == "14.0"
    print(f"ARITH {BLUE}2+3*4{RESET} == 14.0")
    
    assert interpret("(2+3)*4") == "20.0"
    print(f"ARITH {BLUE}(2+3)*4{RESET} == 20.0")
    
    assert interpret("-5") == "-5.0"
    print(f"ARITH {BLUE}-5{RESET} == -5.0")
    
    print("\narithmetic(): All tests passed!\n")

def test_lambda_arith():
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    assert interpret(r"(\x.x + 1) 5") == "6.0"
    print(f"LAMBDA {BLUE}(\\x.x + 1) 5{RESET} == 6.0")
    
    assert interpret(r"(\x.\y.x + y) 3 4") == "7.0"
    print(f"LAMBDA {BLUE}(\\x.\\y.x + y) 3 4{RESET} == 7.0")
    
    assert interpret(r"(\x.x * x) 3") == "9.0"
    print(f"LAMBDA {BLUE}(\\x.x * x) 3{RESET} == 9.0")
    
    assert interpret(r"\x.(\y.y)x") == r"(\x.((\y.y) x))"
    print(f"LAMBDA {BLUE}\\x.(\\y.y)x{RESET} == (\\x.((\\y.y) x)) [lazy]")

    print("\nlambda_arith(): All tests passed!\n")

def test_if_let_letrec():
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    assert interpret("if 1 then 5 else 6") == "5.0"
    print(f"IF {BLUE}if 1 then 5 else 6{RESET} == 5.0")
    
    assert interpret("if 0 == 0 then 5 else 6") == "5.0"
    print(f"IF {BLUE}if 0 == 0 then 5 else 6{RESET} == 5.0")
    
    assert interpret("if 0 <= 1 then 6 else 7") == "6.0"
    print(f"IF {BLUE}if 0 <= 1 then 6 else 7{RESET} == 6.0")
    
    assert interpret("let x = 1 in x") == "1.0"
    print(f"LET {BLUE}let x = 1 in x{RESET} == 1.0")
    
    assert interpret(r"let f = \x.x+1 in f 10") == "11.0"
    print(f"LET {BLUE}let f = \\x.x+1 in f 10{RESET} == 11.0")
    
    assert interpret(r"letrec f = \n. if n==0 then 1 else n*f(n-1) in f 5") == "120.0"
    print(f"LETREC {BLUE}letrec f = \\n. if n==0 then 1 else n*f(n-1) in f 5{RESET} == 120.0")

    print("\nif_let_letrec(): All tests passed!\n")

def test_sequencing_lists():
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    assert interpret("1 ;; 2") == "1.0 ;; 2.0"
    print(f"PROG {BLUE}1 ;; 2{RESET} == 1.0 ;; 2.0")
    
    assert interpret("#") == "#"
    print(f"LIST {BLUE}#{RESET} == #")
    
    assert interpret("1:#") == "(1.0 : #)"
    expr = "1:#"
    print(f"LIST {BLUE}{expr}{RESET} == (1.0 : #)")
    
    assert interpret("1:2:3:#") == "(1.0 : (2.0 : (3.0 : #)))"
    expr = "1:2:3:#"
    print(f"LIST {BLUE}{expr}{RESET} == (1.0 : (2.0 : (3.0 : #)))")
    
    assert interpret("hd (1:2:#)") == "1.0"
    print(f"LIST {BLUE}hd (1:2:#){RESET} == 1.0")
    
    assert interpret("tl (1:2:#)") == "(2.0 : #)"
    print(f"LIST {BLUE}tl (1:2:#){RESET} == (2.0 : #)")
    
    assert interpret("1:2 == 1:2") == "1.0"
    print(f"LIST {BLUE}1:2 == 1:2{RESET} == 1.0")

    print("\nsequencing_lists(): All tests passed!\n")

def test_higher_order():
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    assert interpret(
        r"letrec map = \f. \xs. if xs==# then # else (f (hd xs)) : (map f (tl xs)) in "
        r"(map (\x.x+1) (1:2:3:#))"
    ) == "(2.0 : (3.0 : (4.0 : #)))"
    print(f"MAP {BLUE}letrec map = ... in (map (\\x.x+1) (1:2:3:#)){RESET} == (2.0 : (3.0 : (4.0 : #)))")

    print("\nhigher_order(): All tests passed!\n")

if __name__ == "__main__":
    print(Fore.GREEN + "\nTEST PARSING\n" + Style.RESET_ALL)
    test_parse()
    print(Fore.GREEN + "TEST SUBSTITUTION\n" + Style.RESET_ALL)
    test_substitute()
    print(Fore.GREEN + "TEST EVALUATION\n" + Style.RESET_ALL)
    test_evaluate()
    print(Fore.GREEN + "\nTEST INTERPRETATION\n" + Style.RESET_ALL)
    test_interpret()
    print(Fore.GREEN + "TEST ARITHMETIC\n" + Style.RESET_ALL)
    test_arithmetic()
    print(Fore.GREEN + "TEST LAMBDA ARITHMETIC\n" + Style.RESET_ALL)
    test_lambda_arith()
    print(Fore.GREEN + "TEST IF/LET/LETREC\n" + Style.RESET_ALL)
    test_if_let_letrec()
    print(Fore.GREEN + "TEST SEQUENCING & LISTS\n" + Style.RESET_ALL)
    test_sequencing_lists()
    print(Fore.GREEN + "TEST HIGHER-ORDER FUNCTIONS\n" + Style.RESET_ALL)
    test_higher_order()
    
