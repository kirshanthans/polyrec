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

### Legality Checking 
*Importing Module*
```python
from dependencetest import Dependence 
```

### Completion
*Importing Module*
```python
from completion import Completion 
```

### Code Generation
*Importing Modules*
```python
from astxform import ASTXform
from ast import *
```

### Demo

