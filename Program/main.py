import GUI
import engine
from math import copysign as float_copysign
from sys import stderr
import clock
print = clock.print
print('Welcome!')
print('Warning: example read, write, and move are not implemented.')
def copysign(x, y):
    return int(float_copysign(x,y))

engine.number_of_states = 6
engine.examples = {'first':{'memory':4, 'time':6},'second':{'memory':11,'time':10}}
engine.create_constraints()
  
gv = GUI.MyVar#lambda x: GUI.tk.IntVar(GUI.root, x)
ev = engine.Variable
timer_variable = gv()

def next_solution():#Untimed
    switch_solution_update(engine.solution.next())
def previous_solution():#Untimed
    switch_solution_update(engine.solution.previous())

def big_next_solution():#Untimed
    solution = engine.solution.next()
    while not semantically_different_from_old_solution(solution) and engine.solution.has_next():
        solution = engine.solution.next()
    switch_solution_update(solution)
def big_previous_solution():#Untimed
    solution = engine.solution.previous()
    while not semantically_different_from_old_solution(solution) and engine.solution.has_previous():
        solution = engine.solution.previous()
    switch_solution_update(solution)
    
last_solution = None
def semantically_different_from_old_solution(solution):
    for old,new in zip(last_solution,solution):
        if old != new:
            identifier = engine.identifier(old)
            if identifier is not None and identifier[0] not in ['M','Q']:
                return True
    return False
def switch_solution_update(solution):
    update_gui_vars(solution)
    GUI.update()
set_next_solution_switch_active = GUI.add_solution_selectors(big_previous_solution,big_next_solution,previous_solution,next_solution)

def solve():
    clock('Engine Start')
    out = engine.solve(engine.constraints)
    clock('Engine End')
    return out
def add_engine_constraint(engine_variable, sign):
    if (copysign(engine_variable, sign),) in engine.constraints:
        raise ValueError('Duplicate')
    if (copysign(engine_variable, -sign),) in engine.constraints:
        raise ValueError('Direct Contradiction')
    engine.constraints.append((copysign(engine_variable, sign),))
def remove_engine_constraint(engine_variable, sign):
    engine.constraints.remove((copysign(engine_variable, sign),))
def add_starting_constraint(engine_variable, sign):
    add_engine_constraint(engine_variable, sign)
    for pair in pairs:
        if pair[2] == engine_variable:
            pair[1] = sign*3
            pair[0].set(sign*3)
            return
    raise LookupError()

#pairs[i] = [gui variable, old gui variable, engine variable]
pairs = []
#failed_constraints is a dict of engine constraints from abs(constraint) to sign
failed_constraints = {}

def update(i):
    new, old = ([None, 0, 1, 1, -1, -1, 0][i] for i in [pairs[i][0].get(), pairs[i][1]])
    if new == old:
        return
    clock('Update Start')#This needs to come after the filter so that false alarms don't mess with the timer
    old_sign = copysign(1,pairs[i][1])
    pairs[i][1] = pairs[i][0].get()

    v = pairs[i][2]
    if old != 0:#Update constraints to reflect removed constraint
        if v in failed_constraints:#If it was a failed constraint,
            del failed_constraints[v]#Note its removal, and move on.
        else:
            remove_engine_constraint(v, old)
            if failed_constraints:#If some constraints have failed,
                for constraint in failed_constraints:
                    add_engine_constraint(constraint, failed_constraints[constraint])
                solution = solve()#Try to run with all constraints
                if isinstance(solution, list):#If succeessfull, rejoice.
                    update_gui_vars(solution)
                    failed_constraints.clear()
                else:#Otherwise, maintain the old solution.
                    #print('('+str(solution)+')', file=stderr)
                    for constraint in failed_constraints:
                        remove_engine_constraint(constraint, failed_constraints[constraint])
    if new != 0:#Update constraints to reflect introduced constraint
    #(a reversed constraint is modeled as a removal and then an introduction)
        add_engine_constraint(v, new)
        if old_sign != new:#If this breaks current solution
            solution = solve()#Try to run
            if isinstance(solution, list):#If succeessfull, rejoice.
                update_gui_vars(solution)
            else: #If fail, then flag as failed constraint, and move on.
                #print(solution, file=stderr)
                failed_constraints[v] = copysign(1,new)
                pairs[i][1] = copysign(2, old_sign)
                pairs[i][0].set(pairs[i][1])
                remove_engine_constraint(v, new)
    clock('Update -> GUI')
    GUI.update()
    clock('GUI End')
    total_time = clock.difference('Update Start', 'GUI End')
    GUI_time = clock.difference('Update -> GUI', 'GUI End')
    engine_time = clock.difference('Engine Start', 'Engine End')
    other_time = total_time-engine_time-GUI_time
    
    d = clock.times
    timer_variable.set(
        [total_time,
         GUI_time,
         engine_time,
         other_time,
         clock.average_print_time()])
    
    clock.clear()
    
##    print('\n\
##Total:\t{:5.1f} ms\n\
##GUI:\t{:5.1f} ms\n\
##Engine:\t{:5.1f} ms\n\
##Other:\t{:5.1f} ms\n\
##print:\t{:5.1f} ms\n'.format(
##    total_time*1000,
##    GUI_time*1000, 
##    engine_time*1000,
##    other_time*1000,
##    clock.average_print_time()*1000))
                
def update_gui_vars(solution):
    global last_solution
    last_solution = solution
    set_next_solution_switch_active(*(engine.solution.has_previous(), engine.solution.has_next())*2)
    
    solution = {abs(x):x for x in solution}
    for j in range(len(pairs)):
        constrained = abs(pairs[j][1]) > 1
        match = pairs[j][1] == copysign(pairs[j][1], solution[pairs[j][2]])
        if abs(pairs[j][1]) == 2:
            match = not match
        if constrained and match:
            pairs[j][1] = copysign(3, solution[pairs[j][2]])
        elif constrained and not match:
            pairs[j][1] = copysign(2, solution[pairs[j][2]])
        else:
            pairs[j][1] = copysign(1, solution[pairs[j][2]])
        pairs[j][0].set(pairs[j][1])


        

def register(engine_variable):
    positive = (engine_variable,) in engine.constraints
    negative = (-engine_variable,) in engine.constraints
    if positive and negative:
        raise ValueError()
    gui_variable_value = 3 if positive else -3 if negative else -1
    gui_variable = gv(gui_variable_value)
    ln = len(pairs)
    gui_variable.trace('w', lambda *args:update(ln))
    pairs.append([gui_variable, gui_variable_value, engine_variable])
    return gui_variable


def render_and_register_machine():
    statess = [[[register(ev('M',q,a,'Q',i))
                  for q in range(engine.number_of_states)]
                 for i in range(engine.log2_number_of_states)]
                for a in [0,1]]
    writess = [[register(ev('M',q,a,'W'))
                 for q in range(engine.number_of_states)]
                for a in [0,1]]
    movess = [[register(ev('M',q,a,'V'))
                 for q in range(engine.number_of_states)]
                for a in [0,1]]
    GUI.add_machine(statess, writess, movess)
def render_and_register_example(e,E):
    tape = [[register(ev('T',e,t,x))
             for t in range(E['time']+1)]
            for x in range(E['memory'])]
    positions = [[register(ev('P',e,t,x))
             for t in range(E['time']+1)]
            for x in range(E['memory'])]
    states = [[register(ev('Q',e,t,i))
             for t in range(E['time']+1)]
            for i in range(engine.log2_number_of_states)]
    read,write,move=[None]*3
    GUI.add_example(tape, positions, states, read, write, move, e, lambda x, y:resize(e,E,x,y))

def unregister_and_remove_example(e):
# MEMORY LEAK
#    pairs = [p for p in pairs if engine.identifier(p[-1]) is not None and engine.identifier(p[-1])[1] != e]
#    global pairs
    GUI.remove_example(e)
    
def apply_initial_constraints_to_machine():
    for a in [0,1]:
        for i in range(engine.log2_number_of_states-1):
            add_starting_constraint(ev('M',1,a,'Q',i),-1)
        add_starting_constraint(ev('M',1,a,'Q',engine.log2_number_of_states-1),1)
        add_starting_constraint(ev('M',1,a,'V'),-1)
        add_starting_constraint(ev('M',1,a,'W'),2*a-1)
def apply_initial_constraints_to_example(e, E):
    add_starting_constraint(ev('P',e,0,0),1)
    for i in range(engine.log2_number_of_states-1):
        add_starting_constraint(ev('Q',e,0,i),-1)
        add_starting_constraint(ev('Q',e,E['time'],i),-1)
    add_starting_constraint(ev('Q',e,0,engine.log2_number_of_states-1),-1)
    add_starting_constraint(ev('Q',e,E['time'],engine.log2_number_of_states-1),1)



def resize(e, E, axis, direction):
    E[axis] += direction
    engine.create_constraints()
    unregister_and_remove_example(e)
    render_and_register_example(e,E)
    if axis == 'time':
        print('time')
    elif axis == 'memory':
        print('memory')
    else:
        raise ValueError()

    update_gui_vars(solve())
    GUI.update()



GUI.add_instructions_panel()
GUI.add_timer_chart(timer_variable,['GUI', 'Engine', 'Other', 'A single print statement'])
render_and_register_machine()
for e in engine.examples:
    E = engine.examples[e]
    render_and_register_example(e,E)
    apply_initial_constraints_to_example(e, E)
apply_initial_constraints_to_machine()

update_gui_vars(solve())
GUI.update()

import sys
if "idlelib" not in sys.modules:
    GUI.tk.mainloop()
