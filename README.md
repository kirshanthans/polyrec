# Composable, Sound Transformations of Nested Recursion and Loops

[![MIT license](http://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/kirshanthans/polyrec.svg?branch=master)](https://travis-ci.org/kirshanthans/polyrec)

## Contents
* [Introduction](#introduction)
* [Usage](#usage)
    * [Writing Transformations](#writing-transformations)
    * [Witness Tuple Generation](#witness-tuple-generation)
    * [Legality Checking](#legality-checking)
    * [Completion](#completion)
    * [Code Generation](#code-generation)
* [Demo](#demo)

## Introduction

Code in this repository implements the *PolyRec* framework described in the [paper](10.1145/3314221.3314592) titled **Composable, Sound Transformations of Nested Recursion and Loops**. This implementation encapsulates,

* Representation of dynamic instances in perfectly nested recursion.
* Representation of basic transformations for perfectly nested recursion.
* Composition of these transformations.
* Representing dependences.
* Checking the legality of transformations.
* Completion of a partial transformation.
* Application of transformation (Code generation).

## Usage

### Writing Transformations
*Importing Module*
```python
from polyrec.transformations import Transformation
```
A transformation object is defined as shown below.
```python
xf = Transformation(
     in_dim      = in_dim,   # size of input nest
     out_dim     = out_dim,  # size of output nest
     in_dim_type = dim_type, # a list, ith element is #calls in ith dimension
     in_alp      = in_alp,   # input labels
     in_ord      = in_ord,   # input label order
     ...)                    # other parameters for different transformations
```

Other parameters differ between basic transformations and shown in the table below.

| Transformation | Parameters |
| --- | --- |
| Code Motion | Order (ord) |
| Interchange | Dimensions (d1, d2) |
| Inlining | Dimension, Call, Label (d, c, l) |
| Strip Mining | Dimension, Size (d, s) |

The most important functionality of the transformation object is composition.

``xf = xf1.compose(xf2)``

Above piece of code composes ``xf1`` with ``xf2`` and returns a composed transformation object

### Witness Tuple Generation
*Importing Module*
```python
from polyrec.witnesstuples import WitnessTuple
```
A witness tuple is defined as shown below.
```python
wt = WitnessTuple(
    dims     = dims,     # size of the nest
    dim_type = dim_type, # a list, ith element is #calls in ith dimension
    alphabet = alphabet, # labels of the input program
    order    = order,    # program order of labels
    regex1   = regex1,   # suffix1 as multi-tape regular expression
    regex2   = regex2)   # suffix2 as multi-tape regular expression

wt.set_fsa() # setting up the automata from regular expressions
```
A primitive multi-tape regular expression parser takes the regex1 and regex2. It supports '|' and '*' operators and single level of nesting with parentheses.

For instance, the suffixes [t1, s1] and [r1+t1, s1] must be written as a list of list as follows, [[t1], [s1]] and [[r1, (r1)*, t1], [s1]].

The ``set_fsa`` function will setup the automata that accept these regular expressions.

### Legality Checking 
*Importing Module*
```python
from polyrec.dependencetest import Dependence 
```
A dependence object is created as shown below.
```python
dp = Dependence(wt) # creating a dependence object with a witness tuple

if dp.test(xf): # checking the dependence on a transformation object
    ...
```
The ``test(xf)`` function takes a tranformation object as an argument and check whether the dependence is broken by it or not. ``False`` implies a broken dependence and ``True`` implies otherwise.

### Completion
*Importing Module*
```python
from polyrec.completion import Completion 
```
A completion object is constructed and used as shown below.
```python
cp = Completion(
    in_dim      = in_dim,      # size of the input nest
    in_dim_type = in_dim_type, # a list of #calls in a dimension
    in_alphabet = in_alphabet, # labels for input nest
    in_order    = in_order,    # program order of the labels
    partial     = partial,     # partial order (similar to input order)
    deps        = deps)        # list of witness tuple objects

cp.checks()             # checking possibility of usage
cp.print_report()       # print diagnostics
cp.completion_search()  # search for potential transform completion
cp.print_pxforms()      # print potential completions
cp.completion_valid()   # check the legality of the potential completions
cp.print_vxforms()      # print the legal completions 
```
A partial order is written by specifying an order between the kind of statements we want in the output program.
There are three kinds of statements recursive calls ('r'), transfer calls ('t') and computations ('s').
For instance [['r', 't'],['r', 'r', 's']] is a partial order.

``cp.pxforms`` gives a list of transformation object chains (list of basic transformations) that could arrive arrive at the partial order.

``cp.vxforms`` gives a list of transformation object chains that are legal and complete the partial order.

### Code Generation
*Importing Modules*
```python
from polyrec.astxform import ASTXform
from polyrec.ast import *
```
An AST transformation object is constructed as shown below.
```python
p = ...             # tagged recursion nest ast
xform = ASTXform(p) # creating an ast transform object

print xform.codegen() # input recursion nest code
xform.transform(xf)   # applying the ast transformation
print xform.codegen() # code for recusion nest after the transform
```
The ``transform(xf)`` function takes a basic transformation object as input and performs the necessary AST modifications to realize the transformation.

The ``codegen()`` function returns the source code to current AST held by ASTXform as string.

### Demo
* ``python3 -m examples.demo``

    Print info about an AST (dimensions, dimension types, order) and generates the code. 

* ``python3 -m examples.demo transform``

    Takes an input order of labels, performs composition of basic transforms and prints out the output order of labels

* ``python3 -m examples.demo deptest``
    
    Constructs a witness tuple from multi-tape regular expressions, create a Dependence object and check whether this dependence is preserved or not by a transformation. 

* ``python3 -m examples.demo complete``

    Constructs a completion object with dependence and a partial transformation, prints potential transformations and valid transformations.

* ``python3 -m examples.demo codegen``

    Takes an input AST, performs chain of basic AST transformations and generates the code.

