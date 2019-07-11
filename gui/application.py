import tkinter as tk
from tkinter import ttk
from math import pi
from geometry.plane import Point, Line, Circle
from geometry.algorithms import convex_hull, delaunay_triangulation, voronoi_diagram


class Plane(tk.Canvas):
    
    POINT_RADIUS = 2.5
    CURSOR_TEXT_SETTINGS = (
        0, 0, {'text': '0, 0', 'anchor': 'nw', 'tag': 'all', 'font': ('Times New Roman', 18)})
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, highlightthickness=0, **kwargs)
        OptionPanel(master=self)
        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.master = master
        self.points, self.point_ids = [], []
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
        self.points.append(Point(x, self.convert_y(y)))
        self.point_ids.append(canvas_id)
        self.tag_raise(self.cursor_text)
        
    def remove_point(self, _event):
        if self.points:
            self.delete(self.point_ids[-1])
            del self.points[-1]
            del self.point_ids[-1]
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
                           text=f'{event.x}, {self.convert_y(event.y)}')
        
    def reset(self):
        self.master.resizable(True, True)
        self.delete('current_algorithm')
        self.delete('point')
        self.points, self.point_ids = [], []
        
    def convert_y(self, y: int) -> int:
        return abs(self.master.winfo_height() - y)


class OptionPanel(tk.Toplevel):
    
    ALGORITHM_NAMES = [
        'Select an algorithm...', 'Convex Hull', 'Delaunay triangulation',
        'Delaunay triangulation with circumcircles', 'Voronoi Diagram']
    CONVEX_HULL_SETTINGS = {'fill': '#DDDDDD', 'tags': ['current_algorithm', 'all']}
    TRIANGLE_SETTINGS = {
        'outline': '#000000', 'fill': '#FFFFFF', 'tags': ['current_algorithm', 'all']}
    CIRCLE_SETTINGS = {'outline': '#FF0000', 'tags': ['circle', 'current_algorithm', 'all']}
    
    def __init__(self, master=None):
        super().__init__(master)
        self.canvas = master
        self.protocol('WM_DELETE_WINDOW', lambda: self.canvas.master.destroy())
        self.algorithm_combobox = ttk.Combobox(self, values=self.ALGORITHM_NAMES)
        self.reset = tk.Button(self, text='Reset', command=self.reset)
        self.quit = tk.Button(self, text='Quit', command=lambda: self.canvas.master.destroy())
        self._setup_window()
    
    def _setup_window(self):
        self.algorithm_combobox.bind("<<ComboboxSelected>>", self.execute_algorithm)
        self.algorithm_combobox.config(state='readonly')
        self.algorithm_combobox.current(0)
        self.algorithm_combobox.pack(side='top')
        self.reset.pack(side='top')
        self.quit.pack(side='top')
        
    def reset(self):
        self.algorithm_combobox.set(self.ALGORITHM_NAMES[0])
        self.canvas.reset()
        
    def execute_algorithm(self, _event):
        option = self.algorithm_combobox.get()
        if not self.canvas.points or option == self.ALGORITHM_NAMES[0]:
            return
        self.canvas.delete('current_algorithm')
        if option == self.ALGORITHM_NAMES[1]:
            c_hull = convex_hull(self.canvas.points)
            self.canvas.create_polygon(
                *[(p.x, self.canvas.convert_y(p.y)) for p in c_hull],
                self.CONVEX_HULL_SETTINGS)
        elif option == self.ALGORITHM_NAMES[2] or option == self.ALGORITHM_NAMES[3]:
            triangles, circles = delaunay_triangulation(self.canvas.points), []
            for triangle in triangles:
                triangle_points = [
                    (int(p.x), int(self.canvas.convert_y(p.y)))
                    for p in [triangle.p1, triangle.p2, triangle.p3]]
                self.canvas.create_polygon(*triangle_points, self.TRIANGLE_SETTINGS)
                circles.append(Circle.from_triangle(triangle))
            for circle in circles:
                self.canvas.create_oval(
                    int(circle.h - circle.r), int(self.canvas.convert_y(circle.k + circle.r)),
                    int(circle.h + circle.r), int(self.canvas.convert_y(circle.k - circle.r)),
                    self.CIRCLE_SETTINGS)
        elif option == self.ALGORITHM_NAMES[4]:
            voronoi = voronoi_diagram(self.canvas.points)
            segments, rays = voronoi[0], voronoi[1]
            for segment in segments:
                p1, p2 = segment.p1, segment.p2
                self.canvas.create_line(
                    int(p1.x), int(self.canvas.convert_y(p1.y)),
                    int(p2.x), int(self.canvas.convert_y(p2.y)),
                    tags=['current_algorithm', 'all'])
            top_line, bottom_line = Line(0, 1, -self.canvas.winfo_height()), Line(0, 1, 0)
            left_line, right_line = Line(1, 0, 0), Line(1, 0, -self.canvas.winfo_width())
            for ray in rays:
                p, angle, ray_line = ray.p, ray.angle, Line.from_ray(ray)
                intersection1 = ray_line.intersection(top_line if 0 <= angle < pi else bottom_line)
                intersection2 = ray_line.intersection(
                    left_line if pi / 2 <= angle < 3 * pi / 2 else right_line)
                if intersection1 and intersection2:
                    endpoint = (intersection1
                                if p.distance_to(intersection1) < p.distance_to(intersection2)
                                else intersection2)
                else:
                    endpoint = intersection1 or intersection2
                self.canvas.create_line(
                    int(p.x), int(self.canvas.convert_y(p.y)),
                    int(endpoint.x), int(self.canvas.convert_y(endpoint.y)),
                    tags=['current_algorithm', 'all'])
        if option == self.ALGORITHM_NAMES[2]:
            self.canvas.delete('circle')
        self.canvas.tag_lower('current_algorithm')


if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title('Euclidean plane')
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f'{screen_width // 2}x{screen_height // 2}'
                  f'+{screen_width // 4}+{screen_height // 4}')
    app = Plane(master=root)
    app.mainloop()

