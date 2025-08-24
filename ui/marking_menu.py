# ui/marking_menu.py
from PySide2 import QtWidgets, QtCore, QtGui

class MarkingMenu(QtWidgets.QMenu):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setup_actions()
        
    def setup_actions(self):
        # Create actions
        self.select_action = QtWidgets.QAction("Select", self)
        self.move_action = QtWidgets.QAction("Move", self)
        self.rotate_action = QtWidgets.QAction("Rotate", self)
        self.scale_action = QtWidgets.QAction("Scale", self)
        self.duplicate_action = QtWidgets.QAction("Duplicate", self)
        self.delete_action = QtWidgets.QAction("Delete", self)
        self.properties_action = QtWidgets.QAction("Properties", self)
        
        # Add actions to menu
        self.addAction(self.select_action)
        self.addAction(self.move_action)
        self.addAction(self.rotate_action)
        self.addAction(self.scale_action)
        self.addSeparator()
        self.addAction(self.duplicate_action)
        self.addAction(self.delete_action)
        self.addSeparator()
        self.addAction(self.properties_action)
        
        # Connect actions
        self.select_action.triggered.connect(self.handle_select)
        self.move_action.triggered.connect(self.handle_move)
        self.rotate_action.triggered.connect(self.handle_rotate)
        self.scale_action.triggered.connect(self.handle_scale)
        self.duplicate_action.triggered.connect(self.handle_duplicate)
        self.delete_action.triggered.connect(self.handle_delete)
        self.properties_action.triggered.connect(self.handle_properties)
        
    def show_at_position(self, pos):
        self.exec_(self.canvas.mapToGlobal(pos))
        
    def handle_select(self):
        # Handle select action
        pass
        
    def handle_move(self):
        # Handle move action
        pass
        
    def handle_rotate(self):
        # Handle rotate action
        pass
        
    def handle_scale(self):
        # Handle scale action
        pass
        
    def handle_duplicate(self):
        # Handle duplicate action
        pass
        
    def handle_delete(self):
        # Handle delete action
        pass
        
    def handle_properties(self):
        # Handle properties action
        pass

# Update the canvas to use marking menus
class PickerCanvas(QtWidgets.QGraphicsView):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        # ... existing code ...
        self.marking_menu = MarkingMenu(self)
        
    def contextMenuEvent(self, event):
        # Show marking menu at cursor position
        self.marking_menu.show_at_position(event.pos())
        event.accept()