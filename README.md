# Composable, Sound Transformations of Nested Recursion and Loops

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

* Represention of dynamic instances in perfectly nested recursion.
* Represention of basic transformations for perfectly nested recursion.
* Composition of these transformations.
* Representing dependences.
* Checking the legality of transformations.
* Completion of a partial transformation.
* Application of transformation (Code generation).

## Usage

### Writing Transformations
*Importing Module*
```python
from transformations import Transformation
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

Other parameters differ between transformation and shown in the table below.

| Transformation | Parameters |
| --- | --- |
| Code Motion | Order (ord) |
| Interchange | Dimensions (d1, d2) |
| Inlining | Dimension, Call, Label (d, c, l) |
| Strip Mining | Dimension, Size (d, s) |

### Witness Tuple Generation
*Importing Module*
```python
from witnesstuples import WitnessTuple
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

### Legality Checking 
*Importing Module*
```python
from dependencetest import Dependence 
```

```python
dp = Dependence(wt) # creating a dependence object with a witness tuple

if dp.test(xf): # checking the dependence on a transformation object
    ...
```


### Completion
*Importing Module*
```python
from completion import Completion 
```
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
cp.print_vxforms()       # print the legal completions 
```

### Code Generation
*Importing Modules*
```python
from astxform import ASTXform
from ast import *
```
```python
p = ...             # tagged recursion nest ast
xform = ASTXform(p) # creating an ast transform object

print xform.codegen() # input recursion nest code
xform.transform(xf)   # applying the ast transformation
print xform.codegen() # code for recusion nest after the transform
```
### Demo

