from lark import Lark, Transformer
import sys
import math

# Load the grammar from grammar.lark
with open("grammar.lark", "r") as grammar_file:
    grammar = grammar_file.read()

# Create a Lark parser from the grammar
parser = Lark(grammar, parser='lalr')

# Transform CST to AST
class CalcTransformer(Transformer):
    def plus(self, items):
        return ('plus', items[0], items[1])
    
    def minus(self, items):
        return ('minus', items[0], items[1])
    
    def times(self, items):
        return ('times', items[0], items[1])
    
    def power(self, items):
        return ('power', items[0], items[1])
    
    def negative(self, items):
        return ('negative', items[0])
    
    def log_base(self, items):
        return ('log_base', items[0], items[1])
    
    def num(self, items):
        return ('num', float(items[0]))

# Evaluate the AST
def evaluate(ast):
    if ast[0] == 'plus':
        return evaluate(ast[1]) + evaluate(ast[2])
    elif ast[0] == 'minus':
        return evaluate(ast[1]) - evaluate(ast[2])
    elif ast[0] == 'times':
        return evaluate(ast[1]) * evaluate(ast[2])
    elif ast[0] == 'power':
        return pow(evaluate(ast[1]), evaluate(ast[2]))
    elif ast[0] == 'negative':
        return evaluate(ast[1]) * -1
    elif ast[0] == 'log_base':
        return math.log(evaluate(ast[1]), evaluate(ast[2]))
    elif ast[0] == 'num':
        return ast[1]
    else:
        raise ValueError(f"Unknown operation: {ast}")

# Main execution
if __name__ == "__main__":
    calc_transformer = CalcTransformer() 
    input_string = sys.argv[1]
    cst = parser.parse(input_string)
    #print(cst)
    ast = calc_transformer.transform(cst)
    #print(ast)
    result = evaluate(ast)
    print(result)