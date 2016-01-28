import numpy as np
import matplotlib.colors as col
import matplotlib.pyplot as plt
from numbers import Number

class GridPlot:
    """GridPlot with fast refresh using matplotlib.matshow()

    Creates rectangular grid and allows for changing its cells colors. 
    Cell indexing starts in top left corner
    Cells are indexed from 0 do span[0]-1 in width and to span[1]-1 in height
    """
    
    def __init__(self, A, colors=["black", "red", "lime"], title="GridPlot"):
        """Initializes GridPlot

        Arguments:
            A        - the grid (2D numpy array, matrix)
            colors   - colors for cells
            title    - title of plot window, GridPlot by default

        Once initialized the window will not be drawn.
        Use plot() to force drawing.
        """
        self.cmap = col.ListedColormap(colors)
        self.cdict = dict(zip(self.cmap.colors,
                              range(len(self.cmap.colors))))
        self.A = A
        self.fig = plt.figure(figsize=plt.figaspect(self.A))
        self.fig.canvas.set_window_title(title)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_axis_off()
        self.im = self.ax.matshow(self.A, cmap = self.cmap, vmax = len(self.cmap.colors))
        self.fig.canvas.draw()
        self.fig.show()

    def plot(self, A = None):
        """Forces repaint of the plot and shows it"""
        if A is not None: self.A = A
        self.im.set_data(self.A)
        self.ax.draw_artist(self.im)
        self.fig.canvas.blit(self.ax.bbox)

    def title(self, new_title):
        """Changes window title"""
        self.fig.canvas.set_window_title(new_title)

    def kill(self):
        """Destroys plot. It will not be possible to access it after this."""
        plt.close(self.fig)
    
    def reset(self):
        """Reset all cells to default color"""
        self.A = np.zeros(self.A.shape)

    def paint_cell(self, col, row, color):
        """Changes color of a single cell (row, col) to color. Cells are indexed from 0."""
        if isinstance(color, Number):
            self.A[row, col] = color
        else:
            self.A[row, col] = self.cdict[color]
        self.plot()
            
    def paint_cells(self, data):
        """Changes color of cells. Data is a dictionary mapping (x,y) coordinates 
        (keys) to colors (values). Cells are indexed from 0."""
        if len(data) == 0: return
        col, row =  zip(*data.keys())
        colors = tuple(data.values())
        if not isinstance(colors[0], Number):
            colors = [self.cdict[color] for color in colors]        
        self.A[row, col] = colors
        self.plot()
