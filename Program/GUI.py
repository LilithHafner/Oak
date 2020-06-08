import tkinter as tk
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
frame = tk.Frame(root, bg='grey')
examples = tk.Frame(frame, bg='grey')
examples.grid(row=0,column=1,columnspan=100)
black = tk.Frame(frame, bg='black')
black.grid(row=1,column=1)
white = tk.Frame(frame, bg='white')
white.grid(row=1,column=2)

frame.pack()

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
                position = [None, None, None]##
                for y in range(3):
                    if position_variables[2][y] is not None:
                        for dx in [0, 1, -1, 2, -2]:
                            if position_variables[dx+2][y] is not None and position_variables[dx+2][y].get() > 0:
                                position[y] = dx
                                break
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

        self.lazy_updated=False
        def lazy_update():
            self.lazy_updated=True
        def lazy_trigger():
            if self.lazy_updated:
                update()
                self.lazy_updated = False
        variable.trace("w", lazy_update)
        if self.style == Grid_Style.TAPE:
            for column in position_variables:
                if column is not None:
                    for var in column:
                        if var is not None:
                            var.trace("w", lazy_update)
        update()
        
        self.update = lazy_trigger

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

def add_example(tape, positions, states, read, write, move):
    print('Warning: example read, write, and move are not implemented.')
    if len(tape) != len(positions):
        raise IndexError()
    for i in range(len(tape)):
        if len(tape[i]) != len(positions[i]):
            raise IndexError()
    Grid_of_cells(examples, tape, Grid_Style.TAPE, positions).grid(row=0,column=len(examples.winfo_children()))
    Grid_of_cells(examples, states, Grid_Style.STATE).grid(row=0,column=len(examples.winfo_children()))

def add_machine(statess, writess, movess):
    if black.winfo_children() or white.winfo_children():
        raise ValueError()##Wrong error type
    sides = [white,black]
    for i in range(2):
        Grid_of_cells(sides[i], statess[i], Grid_Style.STATE).grid(row=0,column=0,padx=5,pady=5)
        Grid_of_cells(sides[i], [writess[i]], Grid_Style.WRITE).grid(row=0,column=1,padx=5,pady=5)
        Grid_of_cells(sides[i], [movess[i]], Grid_Style.MOVE).grid(row=0,column=2,padx=5,pady=5)

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
    Multi_bar_chart(frame, variable, names, -5.5, 1.5).grid(row=0,column=0,rowspan=2,sticky='ns')

def update():
    def update_r(wigit):
        if wigit.winfo_children():
            for w in wigit.winfo_children():
                update_r(w)
        else:
            wigit.update()
    update_r(root)
    root.update()
    

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


    add_example(random(5,12), rpositions(5,12), random(3,12), None, None, None)
    add_machine((random(3,8),random(3,8)), (random(1,8)[0],random(1,8)[0]), (random(1,8)[0],random(1,8)[0]))
    var = MyVar()
    add_timer_chart(var,['GUI', 'Engine', 'Other'])
    root.update()
    var.set([3,.8,1,1.2,1.5])
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
