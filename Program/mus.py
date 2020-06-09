import random

def mus(constraints, removal=1):
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
    for i in range(needed, len(constraints)):
        c = constraints[:i]+constraints[i+1:]
        if solve(c) == 'UNSAT':
            return final_mus(c,needed=i)
        print('fail')
    return constraints
