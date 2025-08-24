# ui/alignment_tools.py
from PySide2 import QtWidgets, QtCore, QtGui

class AlignmentTools:
    def __init__(self, canvas):
        self.canvas = canvas
        self.snapping_enabled = True
        self.snap_threshold = 5.0
        self.grid_enabled = False
        self.grid_size = 10.0
        
    def align_left(self, items):
        if not items:
            return
            
        min_x = min(item.x() for item in items)
        for item in items:
            item.setX(min_x)
            
    def align_right(self, items):
        if not items:
            return
            
        max_x = max(item.x() + item.rect().width() for item in items)
        for item in items:
            item.setX(max_x - item.rect().width())
            
    def align_top(self, items):
        if not items:
            return
            
        min_y = min(item.y() for item in items)
        for item in items:
            item.setY(min_y)
            
    def align_bottom(self, items):
        if not items:
            return
            
        max_y = max(item.y() + item.rect().height() for item in items)
        for item in items:
            item.setY(max_y - item.rect().height())
            
    def align_center_h(self, items):
        if not items:
            return
            
        centers = [item.y() + item.rect().height() / 2 for item in items]
        avg_center = sum(centers) / len(centers)
        for item in items:
            item.setY(avg_center - item.rect().height() / 2)
            
    def align_center_v(self, items):
        if not items:
            return
            
        centers = [item.x() + item.rect().width() / 2 for item in items]
        avg_center = sum(centers) / len(centers)
        for item in items:
            item.setX(avg_center - item.rect().width() / 2)
            
    def distribute_horizontal(self, items):
        if len(items) < 3:
            return
            
        items.sort(key=lambda item: item.x())
        left = items[0].x()
        right = items[-1].x() + items[-1].rect().width()
        total_width = right - left
        gap = total_width / (len(items) - 1)
        
        for i, item in enumerate(items[1:-1], 1):
            target_x = left + i * gap - item.rect().width() / 2
            item.setX(target_x)
            
    def distribute_vertical(self, items):
        if len(items) < 3:
            return
            
        items.sort(key=lambda item: item.y())
        top = items[0].y()
        bottom = items[-1].y() + items[-1].rect().height()
        total_height = bottom - top
        gap = total_height / (len(items) - 1)
        
        for i, item in enumerate(items[1:-1], 1):
            target_y = top + i * gap - item.rect().height() / 2
            item.setY(target_y)
            
    def snap_to_grid(self, pos):
        if not self.grid_enabled:
            return pos
            
        x = round(pos.x() / self.grid_size) * self.grid_size
        y = round(pos.y() / self.grid_size) * self.grid_size
        return QtCore.QPointF(x, y)
        
    def snap_to_items(self, pos, items):
        if not self.snapping_enabled:
            return pos
            
        for item in items:
            rect = item.rect().translated(item.pos())
            
            # Check for snapping to edges and centers
            edges = [
                rect.left(), rect.right(), 
                rect.top(), rect.bottom(),
                rect.left() + rect.width() / 2,  # center x
                rect.top() + rect.height() / 2   # center y
            ]
            
            for edge in edges:
                if abs(pos.x() - edge) < self.snap_threshold:
                    pos.setX(edge)
                if abs(pos.y() - edge) < self.snap_threshold:
                    pos.setY(edge)
                    
        return pos