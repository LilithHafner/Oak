'''This machine supports a two character tape alphabet (0 and 1), with 0 as the
blank character. Transitions is a nested tuple indexed by
[state_other_than_accept_state][tape_character] which produces a tuple
(new_state, new_tape_character, move_direction). The start state is 0, the
accept state is 1, right is 1, and left is -1'''
class Machine:
    def __init__(s, transitions):
        s.transitions = transitions#tuple(tuple(tuple(j) for j in i) for i in transitions)
        s.state = 0
        s.head_position = 0
        s.tape = []
        
    def tick(s):
        while s.head_position >= len(s.tape):
            s.tape.append(0)
        instruction = s.transitions[s.state][s.tape[s.head_position]]
        s.state, s.tape[s.head_position], move = instruction
        
        s.head_position += move
        if s.head_position < 0:
            s.head_position = 0

    def run(s, max_ticks=10**4):
        for i in range(max_ticks):
            if s.state == 1:
                s.tape = prune_tape(s.tape, 0)
                return True
            s.tick()
        return False

    def machine_as_strs(s, binary=False):
        out = ['State Write Move','Read: 0']
        for row in s.transitions:
            out.append(str(row[0]))
        out.append('Read: 1')
        for row in s.transitions:
            out.append(str(row[1]))
        return out
    def state_as_str(s):
        return str((s.tape,s.head_position,s.state))
    def show(s, max_ticks=100):
        out = []
        for i in range(max_ticks):
            out.append(s.state_as_str())
            if s.state == 1:
                s.tape = prune_tape(s.tape, 0)
                print('\n'.join(out + s.machine_as_strs()))
                return
            s.tick()
        print('Timeout')

    def reset(s, tape):
        s.tape = tape
        s.state = 0
        s.head_position = 0

def prune_tape(tape, blank):
    i = len(tape)-1
    while tape[i] == blank and i > 0:
        i -= 1
    return tape[:i+1]



unary_half_round_down = Machine(((
        (1,1,-1),
        (2,0,1)
    ),(
        None
    ),(
        (8,0,-1),
        (3,0,1)
    ),(
        (4,0,-1),
        (3,1,1)
    ),(
        (7,0,-1),
        (5,0,-1)
    ),(
        (6,1,-1),
        (5,1,-1)
    ),(
        (0,1,1),
        None
    ),(
        (8,1,1),
        None
    ),(
        (1,1,-1),
        None
)))



                                 
