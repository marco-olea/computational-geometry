import tkinter as tk
from tkinter import ttk
from platform import system
from math import pi
from geometry.plane import Point, Triangle, Line, Circle
from geometry.algorithms import convex_hull, delaunay_triangulation, voronoi_diagram


class Canvas(tk.Canvas):
    """Canvas for adding or removing points on the plane."""
    
    POINT_RADIUS = 2.5
    """The points are actually circles with this radius."""
    
    CURSOR_TEXT_SETTINGS = (
        0, 0, {'text': '0, 0', 'anchor': 'nw', 'tag': 'all', 'font': ('Times New Roman', 18)})
    """Coordinates text font and initial text."""
    
    POINT_SETTINGS = {'fill': 'black', 'tags': ['point', 'all']}
    """Change the color of the points."""
    
    def __init__(self, master=None, *args, **kwargs):
        """Initialize class attributes, bind functions, create control panel window, create text."""
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.points, self.point_ids = [], []
        self.width, self.height = self.winfo_reqwidth(), self.winfo_reqheight()
        self.cursor_text = self.create_text(*self.CURSOR_TEXT_SETTINGS)
        self.bind('<Button-1>', self.add_point)
        self.bind('<Button-2>', self.remove_point)
        self.bind("<Configure>", self.on_resize)
        self.bind('<Motion>', self.update_cursor)
        self.panel = ControlPanel(master=self)
        s_width, s_height = root.winfo_screenwidth(), root.winfo_screenheight()
        self.panel.geometry(f'+{5 * s_width // 8}+{s_height // 4}')

    def set_resizable(self, b: bool):
        """Enable or disable resizing."""
        self.master.resizable(b, b)

    def on_resize(self, event):
        """Scale points, lines, and/or polygons."""
        # Point information is effectively lost if there's been a resizing and an execution.
        if self.panel.algorithm_executed:
            self.panel.disable()
        # Determine the ratio of old width/height to new width/height.
        wscale = event.width / self.width
        hscale = event.height / self.height
        self.width, self.height = event.width, event.height
        # Resize the canvas.
        self.config(width=self.width, height=self.height)
        # Rescale all the objects tagged with the "all" tag.
        self.scale("all", 0, 0, wscale, hscale)
    
    def add_point(self, event):
        """Draw a point and save the object and its returned ID.
        
        If it's the first point added, this method disables window resizing.
        """
        self.set_resizable(False)
        x, y = event.x, event.y
        canvas_id = self.create_oval(
            x - self.POINT_RADIUS, y - self.POINT_RADIUS,
            x + self.POINT_RADIUS, y + self.POINT_RADIUS,
            self.POINT_SETTINGS)
        self.points.append(Point(x, self.convert_ordinate(y)))
        self.point_ids.append(canvas_id)
        self.tag_raise(self.cursor_text)
    
    def remove_point(self, _event):
        """Delete a point from the canvas and its saved information.
        
        If there are no more points, enable window resizing again.
        """
        if self.points:
            self.delete(self.point_ids[-1])
            del self.points[-1]
            del self.point_ids[-1]
        if not self.points:
            self.set_resizable(True)
            self.panel.algorithm_executed = False  # Permit executions.
            
    def update_cursor(self, event):
        """Update the coordinates shown at the top left part of the canvas."""
        self.itemconfigure(self.cursor_text, text=f'{event.x}, {self.convert_ordinate(event.y)}')
    
    def clear(self):
        """Delete everything on the canvas except the coordinates, and enable resizing."""
        self.set_resizable(True)
        self.delete('current_algorithm')
        self.delete('point')
        self.points, self.point_ids = [], []
    
    def convert_ordinate(self, y: int) -> int:
        """Convert a window ordinate to a Euclidean plane ordinate and viceversa."""
        return self.master.winfo_height() - y

    def create_line(self, p1: Point, p2: Point, *args, **kwargs) -> int:
        """Create a line more easily given two point objects."""
        return super().create_line(int(p1.x), int(self.convert_ordinate(p1.y)),
                                   int(p2.x), int(self.convert_ordinate(p2.y)), *args, **kwargs)

    def create_triangle(self, triangle: Triangle, *args, **kwargs) -> int:
        """Create a triangle more easily given a triangle object."""
        p1, p2, p3 = triangle.p1, triangle.p2, triangle.p3
        return self.create_polygon(
            *[(int(p.x), int(self.convert_ordinate(p.y))) for p in [p1, p2, p3]], *args, **kwargs)
    
    def create_circle(self, circle: Circle, *args, **kwargs) -> int:
        """Create a circle more easily given a circle object."""
        h, k, r = int(circle.h), int(circle.k), int(circle.r)
        return self.create_oval(int(h - r), int(self.convert_ordinate(k + r)),
                                int(h + r), int(self.convert_ordinate(k - r)), *args, **kwargs)
    

class ControlPanel(tk.Toplevel):
    """Panel for selecting an algorithm, clearing the canvas, or exiting the program."""
    
    LABEL_TEXT = (
        'Suggestion: Try not to add three or more collinear\n'
        'points. Also, it\'s easier to resize the canvas with\n'
        'the top corners than the bottom ones.\n'
        'Note: You cannot resize the canvas after a point\n'
        'has been added unless an algorithm has been executed,\n'
        'then you can resize only until you add another point.')
    """Suggestions."""
    
    ALGORITHM_NAMES = [
        'Select an algorithm...', 'Convex Hull', 'Delaunay triangulation',
        'Delaunay triangulation with circumcircles', 'Voronoi Diagram']
    """All options."""
    
    CONVEX_HULL_SETTINGS = {
        'fill': '#DDDDDD', 'tags': ['current_algorithm', 'all']}
    """Convex polygon fill color."""
    
    TRIANGLE_SETTINGS = {
        'outline': '#000000', 'fill': '#FFFFFF', 'tags': ['current_algorithm', 'all']}
    """Triangle outlines and fills."""
    
    CIRCLE_SETTINGS = {
        'outline': '#FF0000', 'tags': ['circle', 'current_algorithm', 'all']}
    """Circle outlines and fills."""
    
    def __init__(self, master=None, *args, **kwargs):
        """Create combobox and buttons."""
        super().__init__(master, *args, **kwargs)
        self.canvas = master
        self.algorithm_executed = False
        self.wm_title('Control panel')
        self.protocol('WM_DELETE_WINDOW', lambda: self.canvas.master.destroy())
        label = tk.Label(self, text=self.LABEL_TEXT, justify=tk.LEFT)
        label.pack(side=tk.TOP, expand=tk.YES)
        self.algorithm_combobox = ttk.Combobox(self, values=self.ALGORITHM_NAMES)
        self.algorithm_combobox.bind("<<ComboboxSelected>>", self.execute_algorithm)
        self.algorithm_combobox.config(state='readonly', width='30')
        self.algorithm_combobox.current(0)
        self.algorithm_combobox.pack(side=tk.TOP, fill=tk.X)
        self.update_button = tk.Button(
            self, text='Update', command=lambda: self.execute_algorithm(0))
        self.update_button.pack(side=tk.TOP)
        tk.Button(self, text='Clear', command=self.clear).pack(side=tk.TOP)
        tk.Button(self, text='Quit', command=lambda: self.canvas.master.destroy()).pack(side='top')
    
    def disable(self):
        """Prevent further execution of the algorithms."""
        self.algorithm_combobox.config(state='disabled')
        self.update_button.config(state='disabled')
    
    def clear(self):
        """Reset combobox, clear canvas, and permit algorithm executions."""
        self.algorithm_executed = False
        self.algorithm_combobox.config(state='readonly')
        self.algorithm_combobox.set(self.ALGORITHM_NAMES[0])
        self.update_button.config(state='normal')
        self.canvas.clear()
    
    def execute_algorithm(self, _event):
        """Draw the result of executing the currently selected algorithm."""
        # Do nothing or clear previous algorithm.
        option = self.algorithm_combobox.get()
        if not self.canvas.points or option == self.ALGORITHM_NAMES[0]:
            return
        self.canvas.delete('current_algorithm')
        # Convex hull.
        if option == self.ALGORITHM_NAMES[1]:
            c_hull = convex_hull(self.canvas.points)
            self.canvas.create_polygon(
                *[(p.x, self.canvas.convert_ordinate(p.y)) for p in c_hull],
                self.CONVEX_HULL_SETTINGS)
        # Delaunay triangulation with or without circumcircles.
        elif option == self.ALGORITHM_NAMES[2] or option == self.ALGORITHM_NAMES[3]:
            triangles, circles = delaunay_triangulation(self.canvas.points), []
            for triangle in triangles:
                self.canvas.create_triangle(triangle, self.TRIANGLE_SETTINGS)
                circles.append(Circle.from_triangle(triangle))
            for circle in circles:
                self.canvas.create_circle(circle, self.CIRCLE_SETTINGS)
            if option == self.ALGORITHM_NAMES[2]:
                self.canvas.delete('circle')
        # Voronoi diagram.
        elif option == self.ALGORITHM_NAMES[4]:
            voronoi = voronoi_diagram(self.canvas.points)
            segments, rays = voronoi[0], voronoi[1]
            for segment in segments:
                p1, p2 = segment.p1, segment.p2
                self.canvas.create_line(p1, p2, tags=['current_algorithm', 'all'])
            # Line equations for the canvas's borders.
            top_line, bottom_line = Line(0, 1, -self.canvas.winfo_height()), Line(0, 1, 0)
            left_line, right_line = Line(1, 0, 0), Line(1, 0, -self.canvas.winfo_width())
            # Get the ray's line equation and draw a line from the ray's point to the first border
            # it intersects, depending on the direction the ray's pointing toward.
            for ray in rays:
                p, angle, ray_line = ray.p, ray.angle, Line.from_ray(ray)
                intersection1 = ray_line.intersection(top_line if 0 <= angle < pi else bottom_line)
                intersection2 = ray_line.intersection(
                    left_line if pi / 2 <= angle < 3 * pi / 2 else right_line)
                if intersection1 and intersection2:
                    endpoint = (
                        intersection1
                        if p.distance_to(intersection1) < p.distance_to(intersection2)
                        else intersection2)
                else:
                    endpoint = intersection1 or intersection2
                self.canvas.create_line(p, endpoint, tags=['current_algorithm', 'all'])
        self.canvas.tag_lower('current_algorithm')
        self.canvas.set_resizable(True)
        self.algorithm_executed = True


if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title('Plane')
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f'{screen_width // 2}x{screen_height // 2}'
                  f'+{screen_width // 8}+{screen_height // 4}')
    app = Canvas(master=root, highlightthickness=0)
    if system() == 'Darwin':
        from os import getpid
        from subprocess import check_call
        script = ('tell application "System Events" to set frontmost of every '
                  'process whose unix id is {} to true').format(getpid())
        output = check_call(['/usr/bin/osascript', '-e', script])
    root.after(0, lambda: root.attributes('-topmost', False))
    root.mainloop()
