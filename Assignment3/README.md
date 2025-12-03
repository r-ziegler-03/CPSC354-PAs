# CPSC-354 2025: Assignment 3

## Author 
- Ross Zielger

## Installation

Requirements: `python` (`python3`) and `pip` (`pip3`).

Install with `source setup.sh. Then `python interpreter_test.py` should pass all tests. You can run your own program in `test.lc` with `python interpreter.py test.lc`. You can run the interpreter from the command line with, for example, `python interpreter.py "(\x.x)a"`

## Description
The purpose of the project is to put together what we learned from the calculator and 𝜆-calculus to create a small functional programming language.

We split the project into several milestones

- M1: lambda calculus + arithmetic. Order this ambiguous CFG
```
lam     	exp -> "\" NAME "." exp
app     	exp -> exp exp
var     	exp -> NAME
plus    	exp -> exp "+" exp
times   	exp -> exp "*" exp
minus   	exp -> exp "-" exp
neg     	exp -> "-" exp
num     	exp -> NUMBER
```
- M2: … + conditionals + let + let rec. Order this ambiguous Grammar
```
lam.        exp -> "\" NAME "." exp
app.        exp -> exp exp

plus.       exp -> exp "+" exp
minus.      exp -> exp "-" exp
times.      exp -> exp "*" exp
neg.        exp -> "-" exp

if.         exp -> "if" exp "then" exp "else" exp
leq.        exp -> exp "<=" exp
eq.         exp -> exp "==" exp

let.        exp -> "let" NAME "=" exp "in" exp 
rec.        exp -> "letrec" NAME "=" exp "in" exp
fix.        exp -> "fix" exp

num.        exp -> NUMBER
var.        exp -> NAME
paren.      exp -> "(" exp ")"
```
- M3: … + lists (#, :, hd, tl). The purpose of Milestone 3 is to extend Milestone 2 by an operation for sequencing and operations for constructing and destructing lists
```
prog.       exp -> exp ";;" exp
hd.         exp -> "hd" exp
tl.         exp -> "tl" exp 
nil.        exp -> "#"
cons.       exp -> exp ":" exp
```



