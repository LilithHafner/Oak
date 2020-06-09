import tkinter as tk
import tkinter.font as font
from enum import Enum, auto
from PIL import Image, ImageTk#pip3 install pillow
from subprocess import check_output
from math import ceil, floor, log10, copysign as copysign_float
def copysign(x,y):
    return int(copysign_float(x,y))

class MyVar:#Like tkinter's, but polymorphic and without loop protection
    def __init__(self, value=None):
        self.value = value
        self.read_traces = []
        self.write_traces = []
    def trace(self, mode, callback):
        if mode == 'r':
            self.read_traces.append(callback)
        elif mode == 'w':
            self.write_traces.append(callback)
        else:
            raise ValueError()
    def get(self):
        for callback in self.read_traces:
            callback()
        return self.value
    def set(self, value):
        self.value = value
        for callback in self.write_traces:
            callback()
            
root = tk.Tk()
root.title('Oak   |   Turing Machine Synthesis')
frame = tk.Frame(root, bg='grey')
examples = tk.Frame(frame, bg='grey')
tk.Label(frame,text='Examples',bg='grey',font=font.Font(size=20)).grid(row=0,column=1,columnspan=4)
examples.grid(row=1,column=1,columnspan=4,padx=30)
tk.Label(frame,text='Transition Table',bg='grey',font=font.Font(size=20)).grid(row=2,column=1,columnspan=2,pady=(10,0))
black = tk.Frame(frame, bg='black')
black.grid(row=3,column=1,rowspan=4,padx=10,pady=(0,10))
white = tk.Frame(frame, bg='white')
white.grid(row=3,column=2,rowspan=4,padx=10,pady=(0,10))
for white,White,fg,bg in [[black,'Black','white','black'],[white,'White','black','white']]:    
    tk.Label(white,text='When read '+White,fg=fg,bg=bg).grid(row=0,column=0,columnspan=4)
    tk.Label(white,text='From state',fg=fg,bg=bg).grid(row=1,column=0)
    tk.Label(white,text='000\n001\n010\n'+chr(8942),font=font.Font(size=28),fg=fg,bg=bg).grid(row=2,column=0,sticky='n')
    tk.Label(white,text='To state',fg=fg,bg=bg).grid(row=1,column=1)
    tk.Label(white,text='Write',fg=fg,bg=bg).grid(row=1,column=2)
    tk.Label(white,text='Move',fg=fg,bg=bg).grid(row=1,column=3)

def add_solution_selectors(*commands):
    buttons = []
    buttons.append(tk.Button(frame,text='/ Previous\n\\ Solution',justify='left',bg='grey',command=commands[0]))
    buttons.append(tk.Button(frame,text='Next \\\n Solution /',justify='right',bg='grey',command=commands[1]))
    buttons.append(tk.Button(frame,text='/ Previous\n\\ Solution',justify='left',bg='grey',command=commands[2]))
    buttons.append(tk.Button(frame,text='Next \\\n Solution /',justify='right',bg='grey',command=commands[3]))
    tk.Label(frame,text='Semantic Change',bg='grey').grid(row=3,column=3,columnspan=2,sticky='s')
    buttons[0].grid(row=4,column=3,sticky='n')
    buttons[1].grid(row=4,column=4,padx=10,sticky='n')
    tk.Label(frame,text='Snytactic Change',bg='grey').grid(row=5,column=3,columnspan=2,sticky='s')
    buttons[2].grid(row=6,column=3,sticky='n')
    buttons[3].grid(row=6,column=4,padx=10,sticky='n')
    def set_active(*active):
        for a,b in zip(active,buttons):
            b.configure(state='normal' if a else 'disabled')
    return set_active

##tk.Label(black,text='When read Black',fg='white',bg='black').grid(row=0,column=0,columnspan=4)
##tk.Label(black,text='From\nstate',fg='white',bg='black').grid(row=1,column=0,columnspan=1)
##tk.Label(black,text='To\nstate',fg='white',bg='black').grid(row=1,column=1,columnspan=1)
##tk.Label(black,text='Write',fg='white',bg='black').grid(row=1,column=2,columnspan=1)
##tk.Label(black,text='Move',fg='white',bg='black').grid(row=1,column=3,columnspan=1)
##tk.Label(white,text='When read White',fg='black',bg='white').grid(row=0,column=0,columnspan=4)
##tk.Label(black,text='From\nstate\n00\n01\n10\b11',fg='black',bg='white').grid(row=1,column=0,columnspan=1,rowspan=2)
##tk.Label(black,text='To\nstate',fg='black',bg='white').grid(row=1,column=1,columnspan=1)
##tk.Label(black,text='Write',fg='black',bg='white').grid(row=1,column=2,columnspan=1)
##tk.Label(black,text='Move',fg='black',bg='white').grid(row=1,column=3,columnspan=1)

frame.grid()

image_path = 'gui_icons'
images = {
    (file_name.split('.')[0],):
    Image.open(image_path+'/'+file_name) for file_name in
    check_output(['ls',image_path]).decode().split('\n') if file_name
}
def image(names):
    names = tuple(names)
    if names not in images:
        img = images[(names[0],)].copy()
        img.paste(image(names[1:]), (0,0), image(names[1:]))
        images[names] = img
    return images[names]
    

class Grid_Style(Enum):
    STATE = auto()
    WRITE = auto()
    MOVE = auto()
    TAPE = auto()
class Cell(tk.Label):
    '''integer either 3, or -3 for constrained true or false;
    or 1 or -1 for synthesized true or false. 2 and -2 are failed constaints.
    2 is constrained false, but actually true.
    '''
    def __init__(self, root, style, variable, position_variables=None):
        super().__init__(root, bg='grey',borderwidth=0,padx=1,pady=1)#padx=(1 if style!=Grid_Style.TAPE else 0),pady=(1 if style!=Grid_Style.TAPE else 0))
        self.style = style
        
        def change_variable(var, num):
            if var.get() in [-1, 1]:
                var.set(3*(3-num*2))
            else:
                var.set(copysign(1,var.get()))
        def click(event):
            if event.state == 0:
                change_variable(variable, event.num)
            elif event.state == 1 and position_variables:
                change_variable(position_variables[2][1], event.num)
                
        self.bind("<Button-1>",click)
        self.bind("<Button-2>",click)

        def get_position():
            position = [None, None, None]##
            for y in range(3):
                if position_variables[2][y] is not None:
                    for dx in [0, 1, -1, 2, -2]:
                        if position_variables[dx+2][y] is not None and position_variables[dx+2][y].get() > 0:
                            position[y] = dx
                            break
            return position

        def update(*args):
            value = variable.get()##
            
            imgs = []
            if self.style == Grid_Style.STATE:
                imgs.append('state_1' if value > 0 else 'state_0')
                if abs(value) == 2:
                    imgs.append('failed_constraint_rectangle')
                elif abs(value) == 3:
                    imgs.append('constrained_rectangle')
            elif self.style in [Grid_Style.WRITE, Grid_Style.TAPE]:
                imgs.append('black_tape' if value > 0 else 'white_tape')
            elif self.style == Grid_Style.MOVE:
                imgs.append('move_right' if value > 0 else 'move_left')
            else:
                raise ValueError()

            if self.style in [Grid_Style.WRITE, Grid_Style.MOVE, Grid_Style.TAPE]:
                if abs(value) == 2:
                    imgs.append('failed_constraint_square')
                elif abs(value) == 3:
                    imgs.append('constrained_square')

            if self.style == Grid_Style.TAPE:
                position = get_position()
                try:
                    constraint = abs(position_variables[2][1].get())##
                except:
                    global db
                    db = locals(), globals()
                    raise
                path = None
                if position in [[1,0,-1], [1,0,0], [None,0,0], [1,0,None]]:
                    path = 'left_continue'
                elif position in [[-1,0,1], [0,0,1], [None,0,1]]:
                    path = 'right_continue'
                elif position in [[-1,0,-1], [0,0,0], [-1,0,None], [0,0,None], [-1,0,0], [0,0,-1]]:
                    path = 'left_turn'
                elif position == [1,0,1]:
                    path = 'right_turn'
                elif position[1] == 0:
                    path = 'stray_presence'
                if path is not None:
                    constrained = 'move_constrained_' if constraint == 3 else 'move_'
                    imgs.append(constrained+path)

                if (position[0] == 0 and position[1] == -1) or position == [None,-1,-1]:
                    imgs.append('below_move_left')
                if position[0] == 0 and position[1] == 1:
                    imgs.append('below_move_right')
                if position[2] == 0 and position[1] == -1:
                    imgs.append('above_move_right')
                if (position[2] == 0 and position[1] == 1) or (position[2] == None and position[1] == 1):
                    imgs.append('above_move_left')

                if position[1] != 0 and constraint == 3:
                    imgs.append('constrained_not_move')
                elif position[1] != 0 and constraint == 2:
                    imgs.append('move_failed_constraint')
                elif position[1] == 0 and constraint == 2:
                    imgs.append('failed_constrained_not_move')
            
            self.image = ImageTk.PhotoImage(image(imgs))
            self.configure(image=self.image)

        def get_state():
            return (variable.get(), (tuple(get_position()), position_variables[2][1].get()) if self.style == Grid_Style.TAPE else None)
        last_state = None
        def maybe_update():
            nonlocal last_state
            #print(last_state, get_state())
            if last_state != get_state():
                last_state = get_state()
                update()
            
        self.update = maybe_update

class Grid_of_cells(tk.Frame):
    '''Source is a list of lists of integers such that source[column][row]
    points to the cell's value.'''
    def __init__(self, root, source, style, position_source=None):
        super().__init__(root, bg='grey',highlightthickness=0)
        self.cells = [[self.create_cell(x, y, style, variable, position_source)
                       for y, variable in enumerate(column)]
                      for x, column in enumerate(source)]
        
    def create_cell(self, x, y, style, variable, position_source):
        position_variables = [[position_source[x][y]
                if x >= 0 and x < len(position_source) and y >= 0 and y < len(position_source[x]) else None
                for y in [y-1, y, y+1]]
                for x in [x-2, x-1, x, x+1, x+2]] \
            if style == Grid_Style.TAPE else None
            
        out = Cell(self, style, variable, position_variables)
        out.grid(row=y,column=x)
        return out

    def update(self):
        for column in cells:
            for cell in column:
                cell.update()

example_dict = {}
def add_example(tape, positions, states, read, write, move, name, callback):

    if len(tape) != len(positions):
        raise IndexError()
    for i in range(len(tape)):
        if len(tape[i]) != len(positions[i]):
            raise IndexError()
    
    column = 0
    while examples.grid_slaves(0,column):
        column+=1

    f = tk.Frame(examples, bg='grey')
    example_dict[name] = f    
    f.grid(row=0,column=column)
    Grid_of_cells(f, tape, Grid_Style.TAPE, positions).grid(row=0,column=0)
    Grid_of_cells(f, states, Grid_Style.STATE).grid(row=0,column=1)

    tk.Button(f, text='/\\   Less time   /\\', bg='grey',command=lambda: callback('time',-1)).grid(row=1,column=0,columnspan=2,sticky='ew')
    tk.Button(f, text='\\/   More time   \\/', bg='grey',command=lambda: callback('time',1)).grid(row=2,column=0,columnspan=2,sticky='ew')
    tk.Button(f, text='<\n\nLess\n\ntime\n\n<', wraplength=1, bg='grey',command=lambda: callback('memory',-1)).grid(row=0,column=3,sticky='ns')
    tk.Button(f, text='>\n\nMore\n\ntime\n\n>', wraplength=1, bg='grey',command=lambda: callback('memory',1)).grid(row=0,column=4,sticky='ns')

def remove_example(name):
    example_dict[name].destroy()
    del example_dict[name]

def add_machine(statess, writess, movess):
    if len(black.winfo_children() + white.winfo_children()) > 20:
        raise ValueError()##Wrong error type
    sides = [white,black]
    for i in range(2):
        Grid_of_cells(sides[i], statess[i], Grid_Style.STATE).grid(row=2,column=1,padx=(0,5),pady=(0,10))
        Grid_of_cells(sides[i], [writess[i]], Grid_Style.WRITE).grid(row=2,column=2,padx=5,pady=(0,10))
        Grid_of_cells(sides[i], [movess[i]], Grid_Style.MOVE).grid(row=2,column=3,padx=(5,10),pady=(0,10))

class Multi_bar_chart(tk.Canvas):
    def __init__(self, root, variable, names, min_val, max_val, conversion=log10):
        super().__init__(root, bg='grey',highlightthickness=0)
        bars = len(names)
        spacing = 0
        margin = 4
        bar_width = 20
        label_width = 20
        width = label_width+margin*3-spacing+(bar_width+spacing)*bars
        self.configure(width = width)

        
        line_count = 7
        xvals = [0] + [label_width+margin*2+(bar_width+spacing)*i
                       for i in range(bars)]
        widths = [width] + [bar_width]*bars
        colors = ['white']+['black']*bars
        markers = [(self.create_text((0,0),text=str(i)),i) for i in range(ceil(min_val), floor(max_val)+1)]
        labels = [self.create_text((xvals[i+1]+bar_width/2, margin), anchor="w", angle=-90, text=names[i]) for i in range(len(names))]
        lines = [[
            self.create_line((xvals[i],0,xvals[i]+widths[i],0),fill=colors[i])
            for j in range(line_count)] for i in range(bars+1)]
        
        data = None
        def trace(*args):
            nonlocal data
            value = variable.get()
            if data is None:
                data = [[v] for v in value]
                analytics = [[v]*7 for v in value]
            else:
                analytics = []
                for i,v in enumerate(value):
                    d = data[i]
                    d.append(v)
                    d.sort()
                    l = len(d)-1
                    if l > 10**4:
                        print('I\'m a slow squeaky wheel! Speed me up.')
                    analytics.append([v, sum(d)/len(d), d[0], d[l//4], d[l//2], d[ceil(l*3/4)], d[-1]])
            height = self.winfo_height()
            def get_y(l10val):
                return round(height*(max_val-l10val)/(max_val-min_val))
            for marker,val in markers:
                self.coords(marker,(label_width/2+margin,get_y(val)))
            for bar in range(bars+1):
                for i in range(line_count):
                    val = analytics[bar][i]
                    y = get_y(log10(val) if val > 0 else min_val+.5)
                    self.coords(lines[bar][i],(xvals[bar],y,xvals[bar]+widths[bar],y))

        variable.trace('w',trace)
        self.update = lambda *args:None
            

def add_timer_chart(variable, names):
    Multi_bar_chart(frame, variable, names, -5.5, 1.5).grid(row=0,column=0,rowspan=100,sticky='ns')

def update():
    def update_r(wigit):
        if wigit.winfo_children():
            for w in wigit.winfo_children():
                update_r(w)
        else:
            wigit.update()
    update_r(root)
    root.update()

def add_instructions_panel():
    fr = tk.Frame(frame,bg='light grey')
    fr.grid(column=101,row=0,rowspan=7,sticky='ns')
    def image_label(*image_id, **grid_args):
        img = ImageTk.PhotoImage(image(image_id))
        label = tk.Label(fr, image=img,borderwidth=0,padx=0,pady=1,bg='light grey')
        label.image = img
        label.grid(**grid_args)
    def text_label(text, font_size=None, justify=None, **grid_args):
        label = tk.Label(fr, text=text, bg='light grey')
        if font_size is not None:
            label.configure(font=font.Font(size=font_size))
        if justify is not None:
            label.configure(justify=justify)
        label.grid(**grid_args)
    
    text_label('Legend', font_size=30, row=0, column=0, columnspan=10)
    image_label('black_tape', row=1, column=0)
    image_label('white_tape', row=1, column=1)
    text_label('The two tape cell values', row=1, column=2, columnspan=10, sticky='w')
    image_label('move_left', row=2, column=0)
    image_label('move_right', row=2, column=1)
    text_label('Move left or right', row=2, column=2, columnspan=10, sticky='w')
    image_label('state_0', row=3, column=0)
    image_label('state_1', row=3, column=1)
    text_label('Binary digits in the representation of a state', row=3, column=2, columnspan=10, sticky='w')

    image_label('constrained_square', row=4, column=0)
    image_label('constrained_rectangle', row=4, column=1)
    text_label('Satisfied constraint on a value', row=4, column=2, columnspan=10, sticky='w')
    image_label('failed_constraint_square', row=5, column=0)
    image_label('failed_constraint_rectangle', row=5, column=1)
    text_label('Unsatisfied constraint on a value', row=5, column=2, columnspan=10, sticky='w')

    image_label('move_left_turn', row=6, column=0)
    image_label('move_left_continue', row=6, column=1)
    image_label('move_right_turn', row=6, column=2)
    image_label('move_right_continue', row=6, column=3)
    text_label('Machine movement path', row=6, column=4, columnspan=10, sticky='w')
    
    image_label('move_constrained_left_turn', row=7, column=0)
    image_label('move_constrained_left_continue', row=7, column=1)
    image_label('move_constrained_right_turn', row=7, column=2)
    image_label('move_constrained_right_continue', row=7, column=3)
    text_label('Satisfied constraint to be present', row=7, column=4, columnspan=10, sticky='w')
    
    image_label('move_left_turn', 'failed_constrained_not_move', row=8, column=0)
    image_label('move_left_continue', 'failed_constrained_not_move', row=8, column=1)
    image_label('move_right_turn', 'failed_constrained_not_move', row=8, column=2)
    image_label('move_right_continue', 'failed_constrained_not_move', row=8, column=3)
    text_label('Unsatisfied constraint to be absent', row=8, column=4, columnspan=10, sticky='w')

    image_label('constrained_not_move', row=9, column=0)
    text_label('Satisfied constraint to be absent', row=9, column=1, columnspan=10, sticky='w')
    image_label('move_failed_constraint', row=10, column=0)
    text_label('Unsatisfied constraint to be present', row=10, column=1, columnspan=10, sticky='w')
    
    text_label('Short Instructions', font_size=30, row=20, column=0, columnspan=10)
    text_label('\
This synthesizes Turing machines to satisfy constraints!\n\n\
The top panel(s) show the synthesized machine running on\n\
example(s), with time on the vertical axis, and position\n\
on the horizontal axis. The pair of bottom panels shows\n\
the machine\'s transition table, with the starting state\n\
on the vertical axis.\n\n\n\
Almost any component can be constrained either true or\n\
false, or left up to the syntehsizer.\n\n\
Click to constrain true, right click to constrain false.\n\n\
Shift+click to constrain machine movement.\n\n\
Unsatisfied constraints (red) are ignored in future\n\
computations until they can be satisfied.\n\n\n\
There are often many solutions. You may cycle through them\n\
with the buttons on the botom right. "Semantic change"\n\
referrs to a change in machine opperation on the given\n\
examples while a "Syntactic change" may simply alter the\n\
internal workings of the machine.', justify='left', row=21, column=0, columnspan=10)
##\n\n\n\
##The figure on the far left shows the time taken by various\n\
##components on a log10 scale. There is a line for\n\
##min, max, average, most recent, Q1, Q2, and Q3.\n\
##The white lines represent total time.
if __name__ == '__main__':
    print('Run main.py for full experience')
    from random import randint
    def random_magnitude():
        return 1 if randint(0,7) else 3 if randint(0,10) else 2
    def random(width,height):
        return [[tk.IntVar(root,random_magnitude()*(randint(0,1)*2-1)) for i in range(height)] for j in range(width)]
    def rpositions(width,height):
        pos = [0]
        for i in range(height-1):
            pos.append(max(min(width-1,pos[-1]+(randint(0,1)*2-1)),0))
        return [[tk.IntVar(root,random_magnitude()*(1 if pos[y]==x else -1)) for y in range(height)] for x in range(width)]


    add_example(random(5,7), rpositions(5,7), random(3,7), None, None, None,print)
    add_machine((random(3,8),random(3,8)), (random(1,8)[0],random(1,8)[0]), (random(1,8)[0],random(1,8)[0]))
    add_solution_selectors(*[print]*4)
    add_instructions_panel()
    var = MyVar()
    add_timer_chart(var,['GUI', 'Engine', 'Other'])
    root.update()
    var.set([3,.8,1,1.2,1.5])
    update()
##    e1t = Grid_of_cells(examples, random(5,12), Grid_Style.TAPE, rpositions(5,12))
##    e1t.grid(row=0,column=0)
##    e1s = Grid_of_cells(examples, random(3,12), Grid_Style.STATE)
##    e1s.grid(row=0,column=1)
##    for read in [black, white]:
##        states = Grid_of_cells(read, random(3,8), Grid_Style.STATE)
##        writes = Grid_of_cells(read, random(1,8), Grid_Style.WRITE)
##        moves = Grid_of_cells(read, random(1,8), Grid_Style.MOVE)
##        states.grid(row=0,column=0,padx=5,pady=5,sticky='')
##        writes.grid(row=0,column=1,padx=5,pady=5,sticky='')
##        moves.grid(row=0,column=2,padx=5,pady=5,sticky='')
