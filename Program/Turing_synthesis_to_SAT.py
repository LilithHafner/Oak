
#Notation
# [(a, -b, c), (-d, c)] means
# (a or not b or c) and (not d or c)
# tape characters are 0 and 1.

#Implementation of the notation section

variable_identifiers_to_Variables = {}#Variable is implemented as int, as is conventional.
__variable_identifier_counter = 0
def Variable(*identifier):
    global __variable_identifier_counter
    
    if identifier == (None,):
        __variable_identifier_counter += 1
        return __variable_identifier_counter
        
    if identifier not in variable_identifiers_to_Variables:
        __variable_identifier_counter += 1
        variable_identifiers_to_Variables[identifier] = __variable_identifier_counter
    
    return variable_identifiers_to_Variables[identifier]

V = Variable #Alias

##class Variable:
##    def __init__(self, identifier, negation=1):
##        self.identifier = identifier
##        if negation not in [-1, 1]:
##            raise ValueError()
##        self.negation = negation
##    def negated(self):
##        Variable(self.identifier, -self.negation)

def implies(hypothoses, conclusions):
    return tuple(-h for h in hypothoses) + conclusions

#Call Variable(None) for a unique variable
##__unique_variable_counter = 0
##def unique_variable():
##    global __unique_variable_counter
##    __unique_variable_counter += 1
##    return Variable('__unique_variable', __unique_variable_counter)

#This, which matches the theory, is balogna
##def equal(rest_of_conjunction, variables_to_be_equal):
##    k = Variable(None)
##    return [(rest_of_conjunction + (k,) + variables_to_be_equal), (rest_of_conjunction + (-k,) + variables_to_be_equal)]

def equal_2(rest_of_conjunction, x, y):
    return [rest_of_conjunction+(x,-y), rest_of_conjunction+(-x,y)] 

def equal(rest_of_conjunction, variables_to_be_equal):
    return sum((equal_2(rest_of_conjunction, variables_to_be_equal[0], var) for var in variables_to_be_equal[1:]), [])

def multi_equal(rest_of_conjunction, equalities_to_be_satisfied):
    return sum([equal(rest_of_conjunction, equality) for equality in equalities_to_be_satisfied], start=[])


#Specification
log2_number_of_states = 2 # log base 2 of the number of states (must be an integer)
number_of_states = 2**log2_number_of_states # the number of states
##examples = {'2->1':{'memory':3, 'time':6, 'input':[1,1], 'output':[1]},
##            #'3->1':{'memory':5, 'time':10, 'input':[1,1,1], 'output':[1]},
##            '4->2':{'memory':5, 'time':10, 'input':[1,1,1,1], 'output':[1,1]},
##            #'5->2':{'memory':5, 'time':10, 'input':[1,1,1,1,1], 'output':[1,1]},
##            '6->3':{'memory':7, 'time':15, 'input':[1,1,1,1,1,1], 'output':[1,1,1]}}
examples = {'first':{'memory':8, 'time':10, 'input':[1,1,1,1,1,1], 'output':[0,1,1,1,1,1,1]}}



#Creation of primary variables
#implementation of the "There are the following variables..." section

# Variable(('M',q,a)) refers to M_{q,a})
# Variable(('T',e,t,x)) refers to T_{e,t,x})
# etc.
# See theory for meanings (lol, this crossref is unacceptable in quality publishable work,
# but this aint publishable so...)
# state is most significant bits first

#lol, no implementation needed :)
# 'M',state,tape,'Q',index
# 'M',state,tape,'W'
# 'M',state,tape,'V'


#Creation of constraints
#Implementation of "We now introduce some constant constraints." section
#and assorted assertions such as "The machine’s start state is 0 and its accept state is 1."

constraints = []


#...and its accept state is 1. In the accept state,
#the machine writes the same tape value it reads,
#moves left (decreasing index),
#and remains in the same state.
constraints += sum(
    ([
        (-Variable('M', 1, tape, 'Q', index),)
        for index in range(log2_number_of_states-1)
    ] + [
        (Variable('M', 1, tape, 'Q', log2_number_of_states-1),),
         (Variable('M', 1, tape, 'W') if tape else -Variable('M', 1, tape, 'W'),),
         (-Variable('M', 1, tape, 'V'),),
    ]
    for tape in [0,1])
, start = [])


for e in examples:#e is the identifier (e.g Variable('P', e, t, x))
    E = examples[e]#E is the object (e.g. E['time'])
    
    #The machine's start state is 0
    constraints += [
        (-Variable('Q', e, 0, i),)
        for i in range(log2_number_of_states)
    ]
    #The machine accepts its input
    constraints += [
        (-Variable('Q', e, E['time'], i),)
        for i in range(log2_number_of_states-1)
    ] + [(Variable('Q', e, E['time'], log2_number_of_states-1),)]


    #Constraints on proper tape values (does not match theory. Theory was wrong)
    for t in range(E['time']):
        for x in range(E['memory']):
            #Present implies tape value matches what is read
            constraints += equal((-Variable('P', e, t, x),),
                                 (Variable('T', e, t, x),
                                  Variable('R', e, t)))
            #Present implies tape value will match what is written
            constraints += equal((-Variable('P', e, t, x),),
                                 (Variable('T', e, t+1, x),
                                  Variable('W', e, t)))
            #Not present implies no change in tape value
            constraints += equal((Variable('P', e, t, x),),
                                 (Variable('T', e, t, x),
                                  Variable('T', e, t+1, x)))


    #Constraints on proper machine opperation (State management, reading, writing (not to tape, thoguh))
    for t in range(E['time']):#Odd that this is different than above, but following the theory doc
        for q in range(number_of_states):
            for a in [0,1]:
                #if the state and tape character match, than the behavior stuff must match.
                #  \/
                #the state and tape characther mustnt match or the behavior must match
                #  \/
                #state0 mustnt match or state1 mustnt match ... or the tape characher mustnt match
                #    or the behavior must match.

                tape_characher_match = Variable('R', e, t) if a else -Variable('R', e, t)
                tape_characher_not_match = -tape_characher_match

                state_not_match = tuple(
                        -Variable('Q', e, t, i) if (q>>(log2_number_of_states-1-i))%2 else Variable('Q', e, t, i)
                        for i in range(log2_number_of_states)
                    )

                input_not_match = state_not_match+(tape_characher_not_match,)

                constraints += multi_equal(input_not_match, [
                        (Variable('M', q, a, 'V'), Variable('V', e, t)),
                        (Variable('M', q, a, 'W'), Variable('W', e, t))
                    ]+[
                        (Variable('M', q, a, 'Q', i), Variable('Q', e, t+1, i))
                         for i in range(log2_number_of_states)
                    ])


    #Constraints on unique machine position
    for t in range(E['time']+1):
        for x in range(E['memory']):
            for y in range(E['memory']):
                if x != y:
                    #At least one of these two distinct positions must be empty
                    constraints += [(-Variable('P', e, t, x), -Variable('P', e, t, y))]
    
    #Constraints on proper machine movement
    for t in range(E['time']):
        for x in range(E['memory']):
            constraints += [
                #If we are here and move right, we need to get there
                implies((Variable('P',e,t,x),  Variable('V',e,t)), (Variable('P', e,t+1,x+1),)),
                #If we are there and move left, we need to get here
                implies((Variable('P',e,t,x+1), -Variable('V',e,t)), (Variable('P', e,t+1,x),))
            ]
        constraints += [
            #If we are at left and move left, we need to stay put
            implies((Variable('P',e,t,0), -Variable('V',e,t)), (Variable('P', e,t+1,0),)),
            #If we are at right we need to move left
            implies((Variable('P',e,t,E['memory']-1),), (-Variable('V',e,t),))
        ]
    #Starts at the left most cell5
    constraints += [(Variable('P',e,0,0),)]


    #Input and output
    if len(E['input']) > E['memory'] or len(E['output']) > E['memory']:
        raise ValueError()
    for x in range(E['memory']):
        constraints += [(Variable('T',e,0,x) if x < len(E['input']) and E['input'][x] else -Variable('T',e,0,x),)]
        constraints += [(Variable('T',e,E['time'],x) if x < len(E['output']) and E['output'][x] else -Variable('T',e,E['time'],x),)]

import random
def mus(constraints, removal=1):
    print('         '+str(len(constraints)))
    order = list(range(len(constraints)))
    random.shuffle(order)
    remove = order[:removal]
    for e in order[removal:removal+2]:
        remove = remove[1:]+[e]
        c = [con for i,con in enumerate(constraints) if i not in remove]
        if solve(c) == 'UNSAT':
            return mus(c, 1+removal)
        print('fail', removal)
    return final_mus(constraints) if removal == 1 else mus(constraints, removal-1)

def final_mus(constraints, needed=0):
    print('     final' + str(len(constraints)))
    for i in range(needed, len(constraints)):
        c = constraints[:i]+constraints[i+1:]
        if solve(c) == 'UNSAT':
            return final_mus(c,needed=i)
        print('fail')
    return constraints

def trim_to_solluble():
    global constraints, trimmed
    while solve(constraints) == 'UNSAT':
        #print('Trim', len(constraints), len(trimmed))
        index = random.randint(0,len(constraints)-1)
        trimmed.append(constraints[index])
        constraints = constraints[:index]+constraints[index+1:]
    untrimmed = []
    for i in range(len(trimmed)):
        #print('Trim', len(constraints), len(trimmed)-len(untrimmed))
        if solve(constraints+[trimmed[i]]) != 'UNSAT':
            constraints = constraints+[trimmed[i]]
            untrimmed.append(trimmed[i])
    trimmed = [i for i in trimmed if i not in untrimmed]
    

from pycosat import solve

if __name__ == '__main__':
    trimmed = []
    trim_to_solluble()
    solve_result = solve(constraints)
    if solve_result == 'UNSAT':
        print('No can do. That\'s impossible!')
        print(mus(constraints))
        solution = None
    elif solve_result == 'UNKNOWN':
        print('Sorry bud. That\'s a stumper.')
        solution = None
    else:
        solution = {abs(x):x>0 for x in solve_result}

    def value(*identifier):
        try:
            return solution[Variable(*identifier)]
        except:
            print(identifier)
            raise

    def bits_to_int(bits):
        return ((1 if bits[-1] else 0) + 2*bits_to_int(bits[:-1])) if bits else 0

    def machine_row(state, tape_character):
        return bits_to_int([value('M', state, tape_character, 'Q', i) for i in range(log2_number_of_states)]), \
            1 if value('M', state, tape_character, 'W') else 0, \
            1 if value('M', state, tape_character, 'V') else -1,

    def bin_val(*identifier):
        return '1' if value(*identifier) else '0'

    def show_tape():
        for t in range(E['time']+1):
            print(' '.join(bin_val('T', e, t, x)  for x in range(E['memory'])))

    def show():
        for t in range(E['time']+1):
            print(' '.join(bin_val('T', e, t, x) for x in range(E['memory'])),' | ',
                  ' '.join(bin_val('P', e, t, x) for x in range(E['memory'])),' | ',
                  ' '.join(bin_val('Q', e, t, i) for i in range(log2_number_of_states)) if True or t != E['time'] else 'N/A')

        for a in [0,1]:
            print()
            for state in range(number_of_states):
                print(' '.join('1' if value('M', state, a, 'Q', i) else '0' for i in range(log2_number_of_states)),' | ',
                      '1' if value('M', state, a, 'W') else '0', ' | ', '1' if value('M', state, a, 'V') else '0')

    Variables_to_identifiers = {variable_identifiers_to_Variables[identifier]:identifier for identifier in variable_identifiers_to_Variables}
    def identifier(variable):
        return Variables_to_identifiers.get(variable,None)

    def deep_identifier(constraints):
        if isinstance(constraints, int):
            return ('-' if constraints < 0 else '')+str(identifier(abs(constraints)))
        return [deep_identifier(i) for i in constraints]
        

    from Turing_machine import Machine
    from sat_gen import save
        
    if solution:
        machine = Machine(tuple(tuple(machine_row(state, char) for char in [0,1]) for state in range(number_of_states)))
        machine.reset(list(E['input']))
        #machine.run()
        machine.show()
        print(machine.tape == E['output'])
        print(deep_identifier(trimmed))
        #show()

    else:
        save(constraints)
