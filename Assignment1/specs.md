# CPSC 354 - Programming Assignment 1
### Authors
- Alex Cannizzaro (Section 3) - acannizzaro@chapman.edu
- Ross Ziegler (Section 1) - rziegler@chapman.edu

### Files included
- `calculator_cfg.py`
- `grammar.lark`
- `setup.sh`
- `testing-data.txt`
- `testing.py`
- `specs.md`

## Instructions for running
To run this program, first install and setup with:
```
source setup.sh
```
Then, run the program with:
```
python calculator_cfg.py "1+1"
```

*(The "1+1" can be replaced with whatever expression is to be evaluated. Syntax depends on the version of python used.)*

## Program Description

### Methods in `CalcTransformer` class
- `plus(self, items)`
    - Defines the parsing of the addition operation as `CalcTransformer` converts a CST to an AST
    - Returns the string 'plus' and the first two nodes in `items`
- `minus(self, items)`
    - Defines the parsing of the subtraction operation as `CalcTransformer` converts a CST to an AST
    - Returns the string 'minus' and the first two nodes in `items`
- `times(self, items)`
    - Defines the parsing of the multiplication operation as `CalcTransformer` converts a CST to an AST
    - Returns the string 'times' and the first two nodes in `items`
- `power(self, items)`
    - Defines the parsing of the exponent operation as `CalcTransformer` converts a CST to an AST
    - Returns the string 'power' and the first two nodes in `items`
- `negative(self, items)`
    - Defines the parsing of a negative symbol as `CalcTransformer` converts a CST to an AST
    - Returns the string 'negative' and the first node in `items`
- `log_base(self, items)`
    - Refines the parsing of the logarithm operation as `CalcTransformer` converts a CST to an AST
    - Returns the string 'log_base' and the first two nodes in `items`
- `num(self, items)`
    - Defines the parsing of a number as `CalcTransformer` converts a CST to an AST
    - Returns the string 'num' and the first node in `items` as a float

### Other methods in `calculator_cfg.py`
- `evaluate(ast)`
    - Recursively evaluates an AST (determined by the `CalcTransformer` methods above)
    - Based on the string at `ast[0]`, a different operation is carried out between the next two nodes
    - The string 'num' triggers the base case. At this point, `ast[1]` is a float, as a result of the `CalcTransformer` method `num` 

### Program flow
- The input string is converted to a concrete syntax tree (CST) using the Lark parser
- This CST is trnasformed into an AST using the methods in the `CalcTransformer` class
- The resulting AST is evaluted (with the `evaluate(ast)` method), and the result is printed

## Additional remarks
### Context-free grammar
In the file `grammar.lark`, a context-free grammar specifies the rules for the operations supported by this calculator program. In traditional CFG notation, the grammar is as follows:
```
Exp -> Exp '+' Exp1
Exp -> Exp '-' Exp1
Exp1 -> Exp1 '*' Exp2
Exp2 -> '-' Exp2
Exp3 -> Exp3 '^' Exp2
Exp3 -> 'log' Exp4 'base' Exp4
Exp4 -> Number
Exp4 -> '(' Exp ')'
Exp -> Exp1
Exp1 -> Exp2
Exp2 -> Exp3
Exp3 -> Exp4
```
In the grammar, the order of operations is enforced with levels of precedence for each rule. Operations that are meant to be evaluated last (addition and subtraction) are only possible on expressions in the form `Exp`, and the higher precedence levels are represented by `Exp1` < `Exp2` and so on. Because `Exp4` is the only expression that can be rewritten as a number, evaluation must begin at the highest precendence level and proceed through descending levels; this structure is conducive to the program's recursive evaluation of trees in the `evaluate(ast)` method. Precendence levels allow the CFG to avoid ambiguity because there is only one possible parse tree for any expression; this enforces the order of operations in the grammar.

### Top-down approach
A top-down approach was used in the creation of this program. Code for a functioning calculator with only addition and multiplication (provided by the instructors) was used as a reference for the general structure of `calculator_cfg.py`, and the Copilot LLM was used for guidance on the initial creation of a parser/calculator. LLMs were used in a way that prioritized learning and understanding, asking for step-by-step tutorials, offering corrections, and seeking clarification throughout the process. 