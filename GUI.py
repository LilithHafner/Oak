import tkinter as tk
from enum import Enum, auto

root = tk.Tk()
frame = tk.Frame(bg='grey')
frame.pack()

class Grid_Style(Enum):
    STATE = auto()
    TAPE = auto()
    MOVE = auto()
    POSITION = auto()
class Grid_of_cells(tk.Canvas):
    '''Source is a list of lists of integers such that source[column][row]
    points to an integer either 2, or -2 for constrained true or false;
    or 1 or -1 for synthesized true or false. Default is -1.
    Style is one of 'State', 'Tape', 'Move, or 'Position'.'''
    def __init__(self, source, style, height = 300):
        super().__init__(frame, bg='red', highlightthickness=0)
        self.source = source
        self.cell_aspect_ratio = .8 if style == Grid_Style.STATE else 1
        self.aspect_ratio = self.cell_aspect_ratio*len(source)/max(map(len,source))
        self.height = height
        self.width = self.height*self.aspect_ratio
        self.config(width=self.width, height=self.height)

        self.cells = tuple(tuple(
            self.create_cell(x, y, value) for y, value in enumerate(column))
            for x, column in enumerate(source)
        )

    def f(x):
        if self.style == Grid_Style.STATE:
           w.create_rectangle(x0, y0, x1, y1, fill='white')
           w.

    def create_cell(x, y, value):
        return tuple(
    def update_cell(self, x, y):
        

g1 = Grid_of_cells([[0]*8 for i in range(3)], Grid_Style.STATE)
g2 = Grid_of_cells([[0]*4 for i in range(3)], Grid_Style.STATE, height=150)
g1.grid(row=0,column=0,padx=5,pady=5)
g2.grid(row=0,column=1,sticky='n',padx=5,pady=5)
