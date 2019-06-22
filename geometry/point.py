class Point:
    
    def __init__(self, x: float, y: float, canvas_id: int=None):
        self.x = x
        self.y = y
        self.canvas_id = canvas_id
        
    def __str__(self) -> str:
        return (f'{self.canvas_id}: ' if self.canvas_id else '') + f'({self.x}, {self.y})'
    
    def __repr__(self):
        return self.__str__()
