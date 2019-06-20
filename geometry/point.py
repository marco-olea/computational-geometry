class Point:
    
    def __init__(self, x: float, y: float, canvas_id: int=None):
        self.x = x
        self.y = y
        self.canvas_id = canvas_id
        
    def __str__(self) -> str:
        return f'{self.canvas_id}: ({self.x}, {self.y})'
