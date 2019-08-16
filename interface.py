import sys, os, copy
from polyrec.transformations import Transformation
from polyrec.witnesstuples import WitnessTuple
from polyrec.completion import Completion
from polyrec.dependencetest import Dependence

class Interface:
    def __init__(self):
        self.self = self

    def manual_user_prompt(self):
        print ("----Manual User Prompt----\n")
        correctness = True
        accepted_type = {'il', 'ic', 'cm', 'sm', 'cancel'}
        il_calls_used = []

        while (correctness):
            xform_type = input("Welcome, please enter a transformation type. Enter 'cm', 'il', 'ic', or 'sm'. If you would like to halt execution, enter 'cancel'.\n")
            if xform_type in accepted_type:
                correctness = False
            else:
                print ("Incorrect string entered, please enter a transformation of the type indicated\n")
        
        if xform_type == 'il':
            print ("------------Inlining-----------\n")
            
            print ("------------Dimension Number-----------\n")
            correctness = True
            while (correctness):
                in_dim = input("Please enter the number of dimensions\n")
                try:
                    in_dim = int(in_dim)
                    correctness = False
                except ValueError:
                    print ("This is not a suitable input for the number of dimensions. Please enter an integer value\n")
            
            out_dim = in_dim

            print ("------------Dimensions types-----------\n")
            in_dim_type = []
            for i in range(in_dim):
                correctness = True
                while (correctness):
                    num_recurse = input("For dim " + str(i) + ", enter the number of recursive calls as an integer\n")
                    try:
                        num_recurse = int(num_recurse)
                        correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the number of recursive calls in a dimensions. Please enter an integer value\n")
                in_dim_type.append(num_recurse)
            
            print ("------------Alphabet-----------\n")
            in_alp = []
            for i in range(in_dim):
                current = True
                current_dim_alp = ['e']
                current_dim_type = 0
                while (current):
                    if (i != (in_dim - 1)):
                        new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                        if (new_item == 'next'):
                            #make sure they have entered the correct minimum number of recursive calls
                            current = False
                            in_alp.append(current_dim_alp)
                            print ("Moving to next dimension. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                        elif (new_item[0] == 'r'):
                            current_dim_type += 1
                            if (current_dim_type > in_dim_type[i]):
                                print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                            else:
                                current_dim_alp.append(new_item)
                                print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                        elif (new_item in current_dim_alp):
                            print ("You cannot enter the same label twice\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                    else:
                        new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                        if (new_item == 'done'):
                            current = False
                            in_alp.append(current_dim_alp)
                            print ("Exiting. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                        elif (new_item[0] == 'r'):
                            current_dim_type += 1
                            if (current_dim_type > in_dim_type[i]):
                                print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                            else:
                                current_dim_alp.append(new_item)
                                print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                        elif (new_item in current_dim_alp):
                            print ("You cannot enter the same label twice\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
            
            #here, we print the input alphabet, to allow the user to see the entirety of their entered labels
            print ("The input alphabet is as follows: " + str(in_alp) + "\n")

            #here, we will have the user enter in the order of their labels. It will verify that each item is contained within the alphabet for the dimension
            print ("------------In Order-----------\n")
            in_alp_dup = copy.deepcopy(in_alp)
            in_ord = []
            for i in range(in_dim):
                current = True
                current_dim_ord = ['e']
                in_alp_dup[i].remove('e')
                while (current):
                    if (i != (in_dim - 1)):
                        new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                        if (new_item == 'next'):
                            #do not let them move on until they have entered all labels.
                            if (len(in_alp_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                            else:
                                current = False
                                in_ord.append(current_dim_ord)
                                print ("Moving to next dimension. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_alp_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_alp_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")
                    else:
                        new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                        if (new_item == 'done'):
                            #do not let them move on until they have entered all labels for the dim
                            if (len(in_alp_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                            else:
                                current = False
                                in_ord.append(current_dim_ord)
                                print ("Exiting. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_alp_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_alp_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")

            #here we print the order in its entirety to the user
            print ("The input order is as follows: " + str(in_ord) + "\n")

            print ("--------Dimension Inline-------\n")
            correctness = True
            while (correctness):
                dim_inline = input("Please enter the dimension within which you would like to inline a call\n")
                try:
                    dim_inline = int(dim_inline)
                    if ((dim_inline < 0) or (dim_inline > (in_dim -1))):
                        print ("This is not a valid dimension\n")
                    else:
                        correctness = False
                except ValueError:
                    print ("This is not a suitable input for the dimension to inline. Please enter an integer value\n")
            
            print ("--------Call Inline-------\n")
            correctness = True
            while (correctness):
                call_inline = input("Please enter the call within the dimension which you would like to inline. Enter a number between 1 and " + str(in_dim_type[dim_inline]) + " inclusive.\n")
                try:
                    call_inline = int(call_inline)
                    if ((call_inline < 1) or (call_inline > (in_dim_type[dim_inline]))):
                        print ("This is not a valid call\n")
                    else:
                        correctness = False
                except ValueError:
                    print ("This is not a suitable input for the dimension to inline. Please enter an integer value\n")
            
            print ("------Label-------\n")

            label = input("Please enter the label for the call which you have specified to inline\n")
            il_calls_used.append(label)

            xform = Transformation(
            name        = 'il',
            in_dim      = in_dim,
            out_dim     = out_dim,
            in_dim_type = in_dim_type,
            in_alp      = in_alp,
            in_ord      = in_ord,
            dim_inline  = dim_inline,
            call_inline = call_inline,
            label       = label)

            xform.input_program()
            print("\nTransformation: ", xform.name)
            xform.output_program()
            
        elif xform_type == 'ic':
            print ("------------Interchange-----------\n")
            
            print ("------------Dimension Number-----------\n")
            correctness = True
            while (correctness):
                in_dim = input("Please enter the number of dimensions\n")
                try:
                    in_dim = int(in_dim)
                    correctness = False
                except ValueError:
                    print ("This is not a suitable input for the number of dimensions. Please enter an integer value\n")
            
            out_dim = in_dim

            print ("------------Dimensions types-----------\n")
            in_dim_type = []
            for i in range(in_dim):
                correctness = True
                while (correctness):
                    num_recurse = input("For dim " + str(i) + ", enter the number of recursive calls as an integer\n")
                    try:
                        num_recurse = int(num_recurse)
                        correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the number of recursive calls in a dimensions. Please enter an integer value\n")
                in_dim_type.append(num_recurse)
            
            print ("------------Alphabet-----------\n")
            in_alp = []
            for i in range(in_dim):
                current = True
                current_dim_alp = ['e']
                current_dim_type = 0
                while (current):
                    if (i != (in_dim - 1)):
                        new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                        if (new_item == 'next'):
                            #make sure they have entered the correct minimum number of recursive calls
                            current = False
                            in_alp.append(current_dim_alp)
                            print ("Moving to next dimension. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                        elif (new_item[0] == 'r'):
                            current_dim_type += 1
                            if (current_dim_type > in_dim_type[i]):
                                print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                            else:
                                current_dim_alp.append(new_item)
                                print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                        elif (new_item in current_dim_alp):
                            print ("You cannot enter the same label twice\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                    else:
                        new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                        if (new_item == 'done'):
                            current = False
                            in_alp.append(current_dim_alp)
                            print ("Exiting. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                        elif (new_item[0] == 'r'):
                            current_dim_type += 1
                            if (current_dim_type > in_dim_type[i]):
                                print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                            else:
                                current_dim_alp.append(new_item)
                                print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                        elif (new_item in current_dim_alp):
                            print ("You cannot enter the same label twice\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
            
            #here, we print the input alphabet, to allow the user to see the entirety of their entered labels
            print ("The input alphabet is as follows: " + str(in_alp) + "\n")

            #here, we will have the user enter in the order of their labels. It will verify that each item is contained within the alphabet for the dimension
            print ("------------In Order-----------\n")
            in_alp_dup = copy.deepcopy(in_alp)
            in_ord = []
            for i in range(in_dim):
                current = True
                current_dim_ord = ['e']
                in_alp_dup[i].remove('e')
                while (current):
                    if (i != (in_dim - 1)):
                        new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                        if (new_item == 'next'):
                            #do not let them move on until they have entered all labels.
                            if (len(in_alp_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                            else:
                                current = False
                                in_ord.append(current_dim_ord)
                                print ("Moving to next dimension. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_alp_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_alp_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")
                    else:
                        new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                        if (new_item == 'done'):
                            #do not let them move on until they have entered all labels for the dim
                            if (len(in_alp_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                            else:
                                current = False
                                in_ord.append(current_dim_ord)
                                print ("Exiting. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_alp_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_alp_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")

            #here we print the order in its entirety to the user
            print ("The input order is as follows: " + str(in_ord) + "\n")

            print ("------Interchange dimension 1-------")

            correctness = True
            while (correctness):
                dim_i1 = input("Please enter one of the dimensions you would like to interchange.\n")
                try:
                    dim_i1 = int(dim_i1)
                    if ((dim_i1 < 0) or (dim_i1 >= (in_dim -1))):
                        print ("This is not a valid dimension\n")
                    else:
                        correctness = False
                except ValueError:
                    print ("This is not a suitable input for the dimension to inline. Please enter an integer value\n")

            print ("------Interchange dimension 2-------")

            correctness = True
            while (correctness):
                dim_i2 = input("Please enter the other of the dimensions you would like to interchange.\n")
                try:
                    dim_i2 = int(dim_i2)
                    if ((dim_i2 < 0) or (dim_i2 > (in_dim -1)) or (dim_i2 <= dim_i1)):
                        print ("This is not a valid dimension\n")
                    else:
                        correctness = False
                except ValueError:
                    print ("This is not a suitable input for the dimension to inline. Please enter an integer value\n")

            xform = Transformation(
            name         ='ic',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            dim_i1       = dim_i1,
            dim_i2       = dim_i2)

            xform.input_program()
            print("\nTransformation: ", xform.name)
            xform.output_program()
        
        elif xform_type == 'cm':
            #the below code is for a code motion transformation
            #below we will prompt the user for the number of dimensions
            print ("------------Code Motion-----------\n")
            
            print ("------------Dimension Number-----------\n")
            correctness = True
            while (correctness):
                in_dim = input("Please enter the number of dimensions\n")
                try:
                    in_dim = int(in_dim)
                    correctness = False
                except ValueError:
                    print ("This is not a suitable input for the number of dimensions. Please enter an integer value\n")
            
            #the number of dimensions following the transformation must be the same as the input
            out_dim = in_dim

            #below we are collecting the number of recursive calls per dimension from the user
            print ("------------Dimensions types-----------\n")
            in_dim_type = []
            for i in range(in_dim):
                correctness = True
                while (correctness):
                    num_recurse = input("For dim " + str(i) + ", enter the number of recursive calls as an integer\n")
                    try:
                        num_recurse = int(num_recurse)
                        correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the number of recursive calls in a dimensions. Please enter an integer value\n")
                in_dim_type.append(num_recurse)
            
            #here, for each dimension, we prompt the user to enter in call labels, one at a time, to verify the user never exceeds the number of recursive calls per dimension
            #specified previously. The user can enter as many as they want per dimension, and switch dimensions at will
            print ("------------Alphabet-----------\n")
            in_alp = []
            for i in range(in_dim):
                current = True
                current_dim_alp = ['e']
                current_dim_type = 0
                while (current):
                    if (i != (in_dim - 1)):
                        new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                        if (new_item == 'next'):
                            #make sure they have entered the correct minimum number of recursive calls
                            current = False
                            in_alp.append(current_dim_alp)
                            print ("Moving to next dimension. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                        elif (new_item[0] == 'r'):
                            current_dim_type += 1
                            if (current_dim_type > in_dim_type[i]):
                                print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                            else:
                                current_dim_alp.append(new_item)
                                print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                        elif (new_item in current_dim_alp):
                            print ("You cannot enter the same label twice\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                    else:
                        new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                        if (new_item == 'done'):
                            current = False
                            in_alp.append(current_dim_alp)
                            print ("Exiting. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                        elif (new_item[0] == 'r'):
                            current_dim_type += 1
                            if (current_dim_type > in_dim_type[i]):
                                print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                            else:
                                current_dim_alp.append(new_item)
                                print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                        elif (new_item in current_dim_alp):
                            print ("You cannot enter the same label twice\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
            
            #here, we print the input alphabet, to allow the user to see the entirety of their entered labels
            print ("The input alphabet is as follows: " + str(in_alp) + "\n")

            #here, we will have the user enter in the order of their labels. It will verify that each item is contained within the alphabet for the dimension
            print ("------------In Order-----------\n")
            in_alp_dup = copy.deepcopy(in_alp)
            in_ord = []
            for i in range(in_dim):
                current = True
                current_dim_ord = ['e']
                in_alp_dup[i].remove('e')
                while (current):
                    if (i != (in_dim - 1)):
                        new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                        if (new_item == 'next'):
                            #do not let them move on until they have entered all labels.
                            if (len(in_alp_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                            else:
                                current = False
                                in_ord.append(current_dim_ord)
                                print ("Moving to next dimension. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_alp_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_alp_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")
                    else:
                        new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                        if (new_item == 'done'):
                            #do not let them move on until they have entered all labels for the dim
                            if (len(in_alp_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                            else:
                                current = False
                                in_ord.append(current_dim_ord)
                                print ("Exiting. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_alp_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_alp_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")

            #here we print the order in its entirety to the user
            print ("The input order is as follows: " + str(in_ord) + "\n")
            
            #here we will have the user enter in the output order of the code. It will verify that every item entered is within the input order
            #it will also verify that no label is entered more than is alotted
            in_ord_dup = copy.deepcopy(in_ord)
            out_ord = []
            print ("------------Out Order-----------\n")
            for i in range(in_dim):
                current = True
                current_dim_ord = ['e']
                in_ord_dup[i].remove('e')
                while (current):
                    if (i != (in_dim - 1)):
                        new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                        if (new_item == 'next'):
                            #dont let them move on until all labels have been entered
                            if (len(in_ord_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels from the given input order are as follows: " + str(in_ord_dup[i]))
                            else:
                                current = False
                                out_ord.append(current_dim_ord)
                                print ("Moving to next dimension. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_ord_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension, or you have exceeded the alotted number of this label as specified by your input order. Please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_ord_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")
                    else:
                        new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                        if (new_item == 'done'):
                            #dont let them move on until all labels have been entered
                            if (len(in_ord_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels from the given input order are as follows: " + str(in_ord_dup[i]))
                            else:
                                current = False
                                out_ord.append(current_dim_ord)
                                print ("Exiting. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_ord_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension, or you have exceeded the alotted number of this label as specified by your input order. Please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_ord_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")

            #here we print the order in its entirety to the user
            print ("The output order is as follows: " + str(out_ord) + "\n")

            xform = Transformation(
            name         = 'cm',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            out_ord      = out_ord)

            xform.input_program()
            print("\nTransformation: ", xform.name)
            xform.output_program()

        elif xform_type == 'sm':
            
            print ("------------Strip Mining-----------\n")
            
            print ("------------Dimension Number-----------\n")
            correctness = True
            while (correctness):
                in_dim = input("Please enter the number of dimensions\n")
                try:
                    in_dim = int(in_dim)
                    correctness = False
                except ValueError:
                    print ("This is not a suitable input for the number of dimensions. Please enter an integer value\n")
            
            out_dim = in_dim + 1

            print ("------------Dimensions types-----------\n")
            in_dim_type = []
            for i in range(in_dim):
                correctness = True
                while (correctness):
                    num_recurse = input("For dim " + str(i) + ", enter the number of recursive calls as an integer\n")
                    try:
                        num_recurse = int(num_recurse)
                        correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the number of recursive calls in a dimensions. Please enter an integer value\n")
                in_dim_type.append(num_recurse)
            
            print ("------------Alphabet-----------\n")
            in_alp = []
            for i in range(in_dim):
                current = True
                current_dim_alp = ['e']
                current_dim_type = 0
                while (current):
                    if (i != (in_dim - 1)):
                        new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                        if (new_item == 'next'):
                            #make sure they have entered the correct minimum number of recursive calls
                            current = False
                            in_alp.append(current_dim_alp)
                            print ("Moving to next dimension. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                        elif (new_item[0] == 'r'):
                            current_dim_type += 1
                            if (current_dim_type > in_dim_type[i]):
                                print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                            else:
                                current_dim_alp.append(new_item)
                                print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                        elif (new_item in current_dim_alp):
                            print ("You cannot enter the same label twice\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                    else:
                        new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                        if (new_item == 'done'):
                            current = False
                            in_alp.append(current_dim_alp)
                            print ("Exiting. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                        elif (new_item[0] == 'r'):
                            current_dim_type += 1
                            if (current_dim_type > in_dim_type[i]):
                                print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                            else:
                                current_dim_alp.append(new_item)
                                print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                        elif (new_item in current_dim_alp):
                            print ("You cannot enter the same label twice\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
            
            #here, we print the input alphabet, to allow the user to see the entirety of their entered labels
            print ("The input alphabet is as follows: " + str(in_alp) + "\n")

            #here, we will have the user enter in the order of their labels. It will verify that each item is contained within the alphabet for the dimension
            print ("------------In Order-----------\n")
            in_alp_dup = copy.deepcopy(in_alp)
            in_ord = []
            for i in range(in_dim):
                current = True
                current_dim_ord = ['e']
                in_alp_dup[i].remove('e')
                while (current):
                    if (i != (in_dim - 1)):
                        new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                        if (new_item == 'next'):
                            #do not let them move on until they have entered all labels.
                            if (len(in_alp_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                            else:
                                current = False
                                in_ord.append(current_dim_ord)
                                print ("Moving to next dimension. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_alp_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_alp_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")
                    else:
                        new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                        if (new_item == 'done'):
                            #do not let them move on until they have entered all labels for the dim
                            if (len(in_alp_dup[i]) != 0):
                                print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                            else:
                                current = False
                                in_ord.append(current_dim_ord)
                                print ("Exiting. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                        elif (new_item not in in_alp_dup[i]):
                            print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                        else:
                            current_dim_ord.append(new_item)
                            in_alp_dup[i].remove(new_item)
                            print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")

            #here we print the order in its entirety to the user
            print ("The input order is as follows: " + str(in_ord) + "\n")

            print ("--------Dimension Strip-------\n")
            correctness = True
            while (correctness):
                strip_dim = input("Please enter the dimension which you would like to strip mine. It must have only 1 recursive call. 0 Corresponds to the first dimension\n")
                #THIS CHECK FOR IN_DIM_TYPE SHOULD BE VERY SOON WITHIN THE STRIP MINING 
                try:
                    strip_dim = int(strip_dim)
                    if ((strip_dim < 0) or (strip_dim > (in_dim -1)) or (in_dim_type[strip_dim] != 1)):
                        print ("This is not a valid dimension\n")
                    else:
                        correctness = False
                except ValueError:
                    print ("This is not a suitable input for the dimension to strip mine. Please enter an integer value\n")
            
            print ("--------Strip size-------\n")
            correctness = True
            while (correctness):
                strip_size = input("Please enter the strip size.\n")
                try:
                    strip_size = int(strip_size)
                    if (strip_size < 1):
                        print ("This is not a valid call\n")
                    else:
                        correctness = False
                except ValueError:
                    print ("This is not a suitable input for the dimension to strip mine. Please enter an integer value\n")
            
            

            xform = Transformation(
            name        = 'sm',
            in_dim      = in_dim, 
            out_dim     = out_dim, 
            in_dim_type = in_dim_type, 
            in_alp      = in_alp, 
            in_ord      = in_ord, 
            dim_strip   = strip_dim, 
            strip_size  = strip_size)

            xform.input_program()
            print("\nTransformation: ", xform.name)
            xform.output_program()
        
        else:
            print ("Exiting\n")
            sys.exit()


        #####HERE WE ENTER THE INFINITE LOOP OF TRANSFORMATIONS#####
        repeat = True
        while (repeat):
            correctness = True

            while (correctness):
                xform_type = input("If you would like to enter a successive transformation, enter the transformation from the valid entries. Enter 'cm', 'il', 'ic', or 'sm'. If you would like to halt execution, enter 'cancel'.\n")
                if xform_type in accepted_type:
                    correctness = False
                else:
                    print ("Incorrect string entered, please enter a transformation of the type indicated\n")
        
            if xform_type == 'il':

                print ("--------Dimension Inline-------\n")
                correctness = True
                while (correctness):
                    dim_inline = input("Please enter the dimension within which you would like to inline a call\n")
                    try:
                        dim_inline = int(dim_inline)
                        if ((dim_inline < 0) or (dim_inline > (xform.out_dim -1))):
                            print ("This is not a valid dimension\n")
                        else:
                            correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the dimension to inline. Please enter an integer value\n")
            
                print ("--------Call Inline-------\n")
                correctness = True
                while (correctness):
                    call_inline = input("Please enter the call within the dimension which you would like to inline. Enter a number between 1 and " + str(xform.out_dim_type[dim_inline]) + " inclusive.\n")
                    try:
                        call_inline = int(call_inline)
                        if ((call_inline < 1) or (call_inline > (xform.out_dim_type[dim_inline]))):
                            print ("This is not a valid call\n")
                        else:
                            correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the dimension to inline. Please enter an integer value\n")
            
                print ("------Label-------\n")
                correctness = True
                while (correctness):
                    label = input("Please enter the label for the call which you have specified to inline\n")
                    if (label in il_calls_used):
                        print ("Please enter an inlining label that has not been used yet\n")
                    else:
                        correctness = False

                #can i make reference to a previous object of type transformation with the same name as the object I am now creating?
                #very unsure of this
                xform = Transformation(
                name        = 'il',
                in_dim      = xform.out_dim,
                out_dim     = xform.out_dim,
                in_dim_type = xform.out_dim_type,
                in_alp      = xform.out_alp,
                in_ord      = xform.out_ord,
                dim_inline  = dim_inline,
                call_inline = call_inline,
                label       = label)

                xform.input_program()
                print("\nTransformation: ", xform.name)
                xform.output_program()
            
            elif xform_type == 'ic':

                print ("------Interchange dimension 1-------")

                correctness = True
                while (correctness):
                    dim_i1 = input("Please enter one of the dimensions you would like to interchange.\n")
                    try:
                        dim_i1 = int(dim_i1)
                        if ((dim_i1 < 0) or (dim_i1 >= (xform.out_dim -1))):
                            print ("This is not a valid dimension\n")
                        else:
                            correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the dimension to inline. Please enter an integer value\n")

                print ("------Interchange dimension 2-------")

                correctness = True
                while (correctness):
                    dim_i2 = input("Please enter the other of the dimensions you would like to interchange.\n")
                    try:
                        dim_i2 = int(dim_i2)
                        if ((dim_i2 < 0) or (dim_i2 > (xform.out_dim -1)) or (dim_i2 <= dim_i1)):
                            print ("This is not a valid dimension\n")
                        else:
                            correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the dimension to inline. Please enter an integer value\n")

                xform = Transformation(
                name         ='ic',
                in_dim       = xform.out_dim,
                out_dim      = xform.out_dim,
                in_dim_type  = xform.out_dim_type,
                in_alp       = xform.out_alp,
                in_ord       = xform.out_ord,
                dim_i1       = dim_i1,
                dim_i2       = dim_i2)

                xform.input_program()
                print("\nTransformation: ", xform.name)
                xform.output_program()

            elif xform_type == 'cm':
                #here we will have the user enter in the output order of the code. It will verify that every item entered is within the input order
                #it will also verify that no label is entered more than is alotted
                in_ord_dup = copy.deepcopy(xform.out_ord)
                out_ord = []
                print ("------------Out Order-----------\n")
                for i in range(xform.out_dim):
                    current = True
                    current_dim_ord = ['e']
                    in_ord_dup[i].remove('e')
                    while (current):
                        if (i != (xform.out_dim - 1)):
                            new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                            if (new_item == 'next'):
                                #dont let them move on until all labels have been entered
                                if (len(in_ord_dup[i]) != 0):
                                    print ("You have not entered enough labels. Unaccounted for labels from the given input order are as follows: " + str(in_ord_dup[i]))
                                else:
                                    current = False
                                    out_ord.append(current_dim_ord)
                                    print ("Moving to next dimension. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                            elif (new_item not in in_ord_dup[i]):
                                print ("The labeled enter is not in the alphabet for the corresponding dimension, or you have exceeded the alotted number of this label as specified by your input order. Please enter another\n")
                            else:
                                current_dim_ord.append(new_item)
                                in_ord_dup[i].remove(new_item)
                                print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")
                        else:
                            new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                            if (new_item == 'done'):
                                #dont let them move on until all labels have been entered
                                if (len(in_ord_dup[i]) != 0):
                                    print ("You have not entered enough labels. Unaccounted for labels from the given input order are as follows: " + str(in_ord_dup[i]))
                                else:
                                    current = False
                                    out_ord.append(current_dim_ord)
                                    print ("Exiting. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                            elif (new_item not in in_ord_dup[i]):
                                print ("The labeled enter is not in the alphabet for the corresponding dimension, or you have exceeded the alotted number of this label as specified by your input order. Please enter another\n")
                            else:
                                current_dim_ord.append(new_item)
                                in_ord_dup[i].remove(new_item)
                                print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")

                #here we print the order in its entirety to the user
                print ("The output order is as follows: " + str(out_ord) + "\n")        
                
                xform = Transformation(
                name         = 'cm',
                in_dim       = xform.out_dim,
                out_dim      = xform.out_dim,
                in_dim_type  = xform.out_dim_type,
                in_alp       = xform.out_alp,
                in_ord       = xform.out_ord,
                out_ord      = out_ord)

                xform.input_program()
                print("\nTransformation: ", xform.name)
                xform.output_program()

            elif xform_type == 'sm':
                
                print ("--------Dimension Strip-------\n")
                correctness = True
                while (correctness):
                    strip_dim = input("Please enter the dimension which you would like to strip mine. It must have only 1 recursive call. 0 Corresponds to the first dimension\n")
                    #THIS CHECK FOR IN_DIM_TYPE SHOULD BE VERY SOON WITHIN THE STRIP MINING 
                    try:
                        strip_dim = int(strip_dim)
                        if ((strip_dim < 0) or (strip_dim > (xform.out_dim -1)) or (xform.out_dim_type[strip_dim] != 1)):
                            print ("This is not a valid dimension\n")
                        else:
                            correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the dimension to strip mine. Please enter an integer value\n")
            
                print ("--------Strip size-------\n")
                correctness = True
                while (correctness):
                    strip_size = input("Please enter the strip size.\n")
                    try:
                        strip_size = int(strip_size)
                        if (strip_size < 1):
                            print ("This is not a valid call\n")
                        else:
                            correctness = False
                    except ValueError:
                        print ("This is not a suitable input for the dimension to strip mine. Please enter an integer value\n")            
                
                xform = Transformation(
                name        = 'sm',
                in_dim      = xform.out_dim, 
                out_dim     = xform.out_dim + 1, 
                in_dim_type = xform.out_dim_type, 
                in_alp      = xform.out_alp, 
                in_ord      = xform.out_ord, 
                dim_strip   = strip_dim, 
                strip_size  = strip_size)

                xform.input_program()
                print("\nTransformation: ", xform.name)
                xform.output_program()

            else:
                repeat = False
                print ("Exiting\n")
                sys.exit()

    def suggested_user_prompt(self):
        print ("------Suggested User Prompt-----\n")
        
        print ("------------Dimension Number-----------\n")
        correctness = True
        while (correctness):
            in_dim = input("Please enter the number of dimensions\n")
            try:
                in_dim = int(in_dim)
                correctness = False
            except ValueError:
                print ("This is not a suitable input for the number of dimensions. Please enter an integer value\n")

        print ("------------Dimensions types-----------\n")
        in_dim_type = []
        for i in range(in_dim):
            correctness = True
            while (correctness):
                num_recurse = input("For dim " + str(i) + ", enter the number of recursive calls as an integer\n")
                try:
                    num_recurse = int(num_recurse)
                    correctness = False
                except ValueError:
                    print ("This is not a suitable input for the number of recursive calls in a dimensions. Please enter an integer value\n")
            in_dim_type.append(num_recurse)
            
        print ("------------Alphabet-----------\n")
        in_alp = []
        for i in range(in_dim):
            current = True
            current_dim_alp = ['e']
            current_dim_type = 0
            while (current):
                if (i != (in_dim - 1)):
                    new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. Alphabet labels should begin with 'r' for a recursive call, 't' for a transfer call, and 's' for a statement. If you wish to begin entering for the next dimension, type 'next'\n")
                    if (new_item == 'next'):
                        #make sure they have entered the correct minimum number of recursive calls
                        current = False
                        in_alp.append(current_dim_alp)
                        print ("Moving to next dimension. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                    elif (new_item[0] == 'r'):
                        current_dim_type += 1
                        if (current_dim_type > in_dim_type[i]):
                            print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                    elif (new_item in current_dim_alp):
                        print ("You cannot enter the same label twice\n")
                    else:
                        current_dim_alp.append(new_item)
                        print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                else:
                    new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                    if (new_item == 'done'):
                        current = False
                        in_alp.append(current_dim_alp)
                        print ("Exiting. Alphabet of dimension just entered is " + str(current_dim_alp) + "\n")
                    elif (new_item[0] == 'r'):
                        current_dim_type += 1
                        if (current_dim_type > in_dim_type[i]):
                            print ("You have exceeded the number of recursive calls you specified for this dimension. Please enter an appropriate input\n")
                        else:
                            current_dim_alp.append(new_item)
                            print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
                    elif (new_item in current_dim_alp):
                        print ("You cannot enter the same label twice\n")
                    else:
                        current_dim_alp.append(new_item)
                        print ("Item appended. Alphabet of current dimension is as follows " + str(current_dim_alp) + "\n")
            
        #here, we print the input alphabet, to allow the user to see the entirety of their entered labels
        print ("The input alphabet is as follows: " + str(in_alp) + "\n")

        #here, we will have the user enter in the order of their labels. It will verify that each item is contained within the alphabet for the dimension
        print ("------------In Order-----------\n")
        in_alp_dup = copy.deepcopy(in_alp)
        in_ord = []
        for i in range(in_dim):
            current = True
            current_dim_ord = ['e']
            in_alp_dup[i].remove('e')
            while (current):
                if (i != (in_dim - 1)):
                    new_item = input("You are in dim " + str(i) + ", please enter another label for this dimension. If you wish to begin entering for the next dimension, type 'next'\n")
                    if (new_item == 'next'):
                        #do not let them move on until they have entered all labels.
                        if (len(in_alp_dup[i]) != 0):
                            print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                        else:
                            current = False
                            in_ord.append(current_dim_ord)
                            print ("Moving to next dimension. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                    elif (new_item not in in_alp_dup[i]):
                        print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                    else:
                        current_dim_ord.append(new_item)
                        in_alp_dup[i].remove(new_item)
                        print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")
                else:
                    new_item = input("You are in the final dimension, if you are finished entering labels, type 'done'\n")
                    if (new_item == 'done'):
                        #do not let them move on until they have entered all labels for the dim
                        if (len(in_alp_dup[i]) != 0):
                            print ("You have not entered enough labels. Unaccounted for labels for the alphabet given are " + str(in_alp_dup[i]))
                        else:
                            current = False
                            in_ord.append(current_dim_ord)
                            print ("Exiting. Order of dimension just entered is " + str(current_dim_ord) + "\n")
                    elif (new_item not in in_alp_dup[i]):
                        print ("The labeled enter is not in the alphabet for the corresponding dimension or you have entered a label twice, please enter another\n")
                    else:
                        current_dim_ord.append(new_item)
                        in_alp_dup[i].remove(new_item)
                        print ("Item appended. Order of current dimension is as follows " + str(current_dim_ord) + "\n")

        #here we print the order in its entirety to the user
        print ("The input order is as follows: " + str(in_ord) + "\n")
        
        print ("----Partial Order Entry----\n")
        print ("You may enter as many labels as you like per dimension. Please only enter 'r', 's', or 't'. We will output valid transformations given your input program.\n")
        valid_partial_alp = ['r', 's', 't']
        partial_ord = []
        for i in range(in_dim):
            current = True
            current_dim_partial_ord = []
            while (current):
                if (i == (in_dim - 1)):
                    new_item = input("You are in the final dimension. Please enter a label. If you are finished entering labels, please enter 'done'.\n")
                    if (new_item == 'done'):
                        current = False
                        partial_ord.append(current_dim_partial_ord)
                        print ("Exiting. Order of dimension just entered is " + str(current_dim_partial_ord) + "\n")
                    elif (new_item not in valid_partial_alp):
                        print ("This is not a valid input. Please enter 'r', 's', or 't'.\n")
                    else:
                        current_dim_partial_ord.append(new_item)
                        print ("Item appended. Partial order of current dimension is as follows " + str(current_dim_partial_ord) + "\n")


                else:
                    new_item = input("You are in dimension " + str(i) + ". Please enter a label. If you are finished entering labels for this dimension, please enter 'next'.\n")
                    if (new_item == 'next'):
                        current = False
                        partial_ord.append(current_dim_partial_ord)
                        print ("Moving to next dimension. Order of dimension just entered is " + str(current_dim_partial_ord) + "\n")
                    elif (new_item not in valid_partial_alp):
                        print ("This is not a valid input. Please enter 'r', 's', or 't'.\n")
                    else:
                        current_dim_partial_ord.append(new_item)
                        print ("Item appended. Partial order of current dimension is as follows " + str(current_dim_partial_ord) + "\n")
            
        #the partial order is stored.
        print ("The input partial order is as follows: " + str(partial_ord) + "\n")
            
        #here we will implement completion
        #FIRST WE NEED THE WITNESS TUPLES
        print ("---Witness Tuples---\n")
        #I NEED HELP HERE WITH THE CREATION OF WITNESS TUPLES
        rgx1 = [['t1'], ['s1']]
        rgx2 = [['r1', '(r1)*', 't1'], ['s1']]
        wtuple = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx1, rgx2)
        wtuple.set_fsa()

        #partial1 = [['t', 'r'], ['s', 'r', 'r']] # potential cm

        #I want to be able to store potential and valid transforms
        print ("---Options---\n")
        comp = Completion(in_dim, in_dim_type, in_alp, in_ord, partial_ord, [Dependence(wtuple)])
        comp.checks()
        comp.print_report()
        comp.completion_search()

        #do i even need to store this info?
        #should tell which dependence is violated, so the user can alter their code
        potentials = comp.pxforms

        comp.print_pxforms()
        comp.completion_valid()

        valids = comp.vxforms

        comp.print_vxforms()
        
        if (len(valids) != 0):
            current = True
            while (current):
                xform_choice = input("Please enter the number of the valid xform corresponding to the transformation you would like to do.")
                if ((xform_choice >= 0) and (xform_choice <= (len(valids) - 1))):
                    current = False
                else :
                    print ("Invalid choice. Please enter a number between 0 and " + str(len(valids) - 1) + ".\n")
        else:
            #SHOULD I ALLOW THE USER TO CHOOSE FROM A NON-VALID AKA POTENTIAL OPTION?
            print("There are no valid options to choose from. Exiting.\n")
            sys.exit()
        
        #HERE WE WILL PERFORM THE OPERATIONS
        #I will need to create xforms. I do not know how many there might be.
        #it is a list of objects
        

    def flow_control(self):
        correctness = True
        accepted_choices = {'manual', 'suggested', 'cancel'}

        while (correctness):
            preference = input("If you would like to transform your code manually, enter 'manual'. If you would like to be provided a series of suggested transformations based on parameters you provide, please enter 'suggested'. If you would like to exit, please enter 'cancel'.\n")
            if preference in accepted_choices:
                correctness = False
            else:
                print ("Incorrect string entered, please enter one of the options indicated\n")

        if (preference == 'manual'):
            operator.manual_user_prompt()
        
        elif (preference == 'suggested'):
            operator.suggested_user_prompt()
        
        else:
            print ("Exiting\n")
            sys.exit()

if __name__ == "__main__":
    operator = Interface()
    operator.flow_control()