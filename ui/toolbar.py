# ui/toolbar.py
from PySide2 import QtWidgets, QtCore, QtGui
from core.model import ButtonType

class PickerToolbar(QtWidgets.QToolBar):
    toolChanged = QtCore.Signal(str)  # Emit tool type
    
    def __init__(self, controller, parent=None):
        super().__init__("Tools", parent)
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        self.setOrientation(QtCore.Qt.Vertical)
        
        # Button creation tools
        self.select_tool = QtWidgets.QAction("Select", self)
        self.select_tool.setCheckable(True)
        self.select_tool.setChecked(True)
        self.select_tool.triggered.connect(lambda: self.activate_tool("select"))
        
        self.rect_tool = QtWidgets.QAction("Rectangle", self)
        self.rect_tool.setCheckable(True)
        self.rect_tool.triggered.connect(lambda: self.activate_tool("rectangle"))
        
        self.circle_tool = QtWidgets.QAction("Circle", self)
        self.circle_tool.setCheckable(True)
        self.circle_tool.triggered.connect(lambda: self.activate_tool("circle"))
        
        self.text_tool = QtWidgets.QAction("Text", self)
        self.text_tool.setCheckable(True)
        self.text_tool.triggered.connect(lambda: self.activate_tool("text"))
        
        # Add tools to toolbar
        self.addAction(self.select_tool)
        self.addAction(self.rect_tool)
        self.addAction(self.circle_tool)
        self.addAction(self.text_tool)
        
        # Button group for exclusive selection
        self.tool_group = QtWidgets.QActionGroup(self)
        self.tool_group.addAction(self.select_tool)
        self.tool_group.addAction(self.rect_tool)
        self.tool_group.addAction(self.circle_tool)
        self.tool_group.addAction(self.text_tool)
        self.tool_group.setExclusive(True)
        
    def activate_tool(self, tool):
        self.toolChanged.emit(tool)