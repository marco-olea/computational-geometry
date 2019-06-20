import tkinter as tk
from tkinter import ttk
from geometry.point import Point


class Plane(tk.Canvas):
    
    POINT_RADIUS = 2.5
    CURSOR_TEXT_SETTINGS = (
        0, 0, {'text': '0, 0', 'anchor': 'nw', 'tag': 'all', 'font': ('Times New Roman', 18)})
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, highlightthickness=0, **kwargs)
        OptionPanel(master=self)
        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.master = master
        self.points = []
        self.width, self.height = self.winfo_reqwidth(), self.winfo_reqheight()
        self.cursor_text = self.create_text(*self.CURSOR_TEXT_SETTINGS)
        self.bindings()
        
    def bindings(self):
        self.bind('<Button-1>', self.add_point)
        self.bind('<Button-2>', self.remove_point)
        self.bind("<Configure>", self.on_resize)
        self.bind('<Motion>', self.update_cursor)
        
    def add_point(self, event):
        if not self.points:
            self.master.resizable(False, False)
        x, y = event.x, event.y
        canvas_id = self.create_oval(
            x - self.POINT_RADIUS, y - self.POINT_RADIUS,
            x + self.POINT_RADIUS, y + self.POINT_RADIUS, fill='black', tags=['point', 'all'])
        self.points.append(Point(x, self._convert_y(y), canvas_id))
        self.tag_raise(self.cursor_text)
        
    def remove_point(self, _event):
        if self.points:
            self.delete(self.points[-1].canvas_id)
            del self.points[-1]
        if not self.points:
            self.master.resizable(True, True)
    
    def on_resize(self, event):
        # Determine the ratio of old width/height to new width/height.
        wscale = event.width / self.width
        hscale = event.height / self.height
        self.width, self.height = event.width, event.height
        # Resize the canvas.
        self.config(width=self.width, height=self.height)
        # Rescale all the objects tagged with the "all" tag.
        self.scale("all", 0, 0, wscale, hscale)
        
    def update_cursor(self, event):
        self.itemconfigure(self.cursor_text,
                           text=f'{event.x}, {self._convert_y(event.y)}')
        
    def _convert_y(self, y: int) -> int:
        return abs(self.master.winfo_height() - y)


class OptionPanel(tk.Toplevel):
    
    ALGORITHM_NAMES = ['Voronoi Diagram']
    
    def __init__(self, master=None):
        super().__init__(master)
        self.plane = master
        self.protocol('WM_DELETE_WINDOW', lambda: self.plane.master.destroy())
        self.algorithms = ttk.Combobox(self, values=self.ALGORITHM_NAMES)
        self.execute = tk.Button(self, text='Execute', command=self.execute_algorithm)
        self.quit = tk.Button(self, text='Quit', command=lambda: self.plane.master.destroy())
        self._setup_window()
    
    def _setup_window(self):
        self.algorithms.current(0)
        self.algorithms.pack(side='top')
        self.execute.pack(side='top')
        self.quit.pack(side='bottom')
        
    def execute_algorithm(self):
        for point in self.plane.points:
            print(point)
        

if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title('Euclidean plane')
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f'{screen_width // 2}x{screen_height // 2}'
                  f'+{screen_width // 4}+{screen_height // 4}')
    app = Plane(master=root)
    app.mainloop()
