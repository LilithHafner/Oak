import tkinter as tk
from enum import Enum, auto
from PIL import Image, ImageTk#pip3 install pillow
from subprocess import check_output

root = tk.Tk()
frame = tk.Frame(root, bg='grey')
examples = tk.Frame(frame, bg='grey')
examples.grid(columnspan=100)
black = tk.Frame(frame, bg='black')
black.grid(row=1,column=0)
white = tk.Frame(frame, bg='white')
white.grid(row=1,column=1)

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
    def __init__(self, root, style):
        super().__init__(root, bg='grey',borderwidth=0,padx=1,pady=1)#padx=(1 if style!=Grid_Style.TAPE else 0),pady=(1 if style!=Grid_Style.TAPE else 0))
        self.style = style

    def update(self, value, position=None):
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

        if self.style in [Grid_Style.WRITE, Grid_Style.MOVE]:
            if abs(value) == 2:
                imgs.append('failed_constraint_square')
            elif abs(value) == 3:
                imgs.append('constrained_square')

        if self.style == Grid_Style.TAPE:

            position, constraint = position
            path = None
            if position in [[1,0,-1], [1,0,0], [None,0,0], [1,0,None]]:
                path = 'left_continue'
            elif position in [[-1,0,1], [0,0,1], [None,0,1]]:
                path = 'right_continue'
            elif position in [[-1,0,-1], [0,0,0], [-1,0,None], [0,0,None], [-1,0,0], [0,0,-1]]:
                path = 'left_turn'
            elif position == [1,0,1]:
                path = 'right_turn'
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

class Grid_of_cells(tk.Frame):
    '''Source is a list of lists of integers such that source[column][row]
    points to the cell's value.'''
    def __init__(self, root, source, style, position_source=None):
        super().__init__(root, bg='grey',highlightthickness=0)
        self.source = source
        self.position_source = position_source
        self.style = style
        #self.cell_aspect_ratio = .8 if style == Grid_Style.STATE else 1
        #self.aspect_ratio = self.cell_aspect_ratio*len(source)/max(map(len,source))
        #self.height = height
        #self.width = self.height*self.aspect_ratio
        #self.config(width=self.width, height=self.height)

        self.width = len(source)
        self.height = len(source[0])
        self.cells = tuple(tuple(
            self.create_cell(x, y) for y in range(self.height)) for x in range(self.width))
        for x in range(self.width):
            for y in range(self.height):
                self.update_cell(x,y)
  
    def create_cell(self, x, y):
        out = Cell(self, self.style)
        out.grid(row=y,column=x)
        return out
    def update_cell(self, x, y):
        position = None
        if self.style == Grid_Style.TAPE:
            position = [None, None, None]
            for i,yi in [(0,y-1),(1,y),(2,y+1)]:
                if yi >= 0 and yi < self.height:
                    for dx in [0, 1, -1, 2, -2]:
                        if x+dx >= 0 and x+dx < self.width and self.position_source[x+dx][yi] > 0:
                            position[i] = dx
                            break
            position = position, abs(self.position_source[x][y])
        self.cells[x][y].update(self.source[x][y], position = position)
        

from random import randint
def random_magnitude():
    return 1 if randint(0,7) else 3 if randint(0,10) else 2
def random(width,height):
    return [[random_magnitude()*(randint(0,1)*2-1) for i in range(height)] for j in range(width)]
def rpositions(width,height):
    pos = [0]
    for i in range(height-1):
        pos.append(max(min(width-1,pos[-1]+(randint(0,1)*2-1)),0))
    return [[random_magnitude()*(1 if pos[y]==x else -1) for y in range(height)] for x in range(width)]


e1t = Grid_of_cells(examples, random(5,12), Grid_Style.TAPE, rpositions(5,12))
e1t.grid(row=0,column=0)
e1s = Grid_of_cells(examples, random(3,12), Grid_Style.STATE)
e1s.grid(row=0,column=1)
for read in [black, white]:
    states = Grid_of_cells(read, random(3,8), Grid_Style.STATE)
    writes = Grid_of_cells(read, random(1,8), Grid_Style.WRITE)
    moves = Grid_of_cells(read, random(1,8), Grid_Style.MOVE)
    states.grid(row=0,column=0,padx=5,pady=5,sticky='')
    writes.grid(row=0,column=1,padx=5,pady=5,sticky='')
    moves.grid(row=0,column=2,padx=5,pady=5,sticky='')
