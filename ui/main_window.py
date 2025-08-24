# ui/main_window.py
from PySide2 import QtWidgets, QtCore, QtGui
from core.controller import PickerController
from ui.canvas import PickerCanvas
from ui.properties import PropertiesPanel

class PickerMainWindow(QtWidgets.QMainWindow):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.controller.view = self
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Maya Picker Tool")
        self.resize(1000, 700)
        
        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Left sidebar for tools
        self.toolbar = QtWidgets.QToolBar("Tools")
        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)
        
        # Add tools
        self.select_tool = QtWidgets.QAction("Select", self)
        self.rect_tool = QtWidgets.QAction("Rectangle", self)
        self.circle_tool = QtWidgets.QAction("Circle", self)
        self.text_tool = QtWidgets.QAction("Text", self)
        
        self.toolbar.addAction(self.select_tool)
        self.toolbar.addAction(self.rect_tool)
        self.toolbar.addAction(self.circle_tool)
        self.toolbar.addAction(self.text_tool)
        
        # Canvas area
        self.canvas = PickerCanvas(self.controller)
        main_layout.addWidget(self.canvas)
        
        # Right sidebar for properties
        self.properties_panel = QtWidgets.QDockWidget("Properties", self)
        self.properties_panel.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        
        self.properties_widget = PropertiesPanel(self.controller)
        self.properties_panel.setWidget(self.properties_widget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.properties_panel)
        
        # Connect toolbar to canvas
        self.select_tool.triggered.connect(lambda: self.canvas.set_current_tool("select"))
        self.rect_tool.triggered.connect(lambda: self.canvas.set_current_tool("rectangle"))
        self.circle_tool.triggered.connect(lambda: self.canvas.set_current_tool("circle"))
        self.text_tool.triggered.connect(lambda: self.canvas.set_current_tool("text"))
        
        # Menu bar
        self.setup_menus()
        
    def setup_menus(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QtWidgets.QAction("New Picker", self)
        new_action.triggered.connect(self.new_picker)
        file_menu.addAction(new_action)
        
        open_action = QtWidgets.QAction("Open", self)
        open_action.triggered.connect(self.open_picker)
        file_menu.addAction(open_action)
        
        save_action = QtWidgets.QAction("Save", self)
        save_action.triggered.connect(self.save_picker)
        file_menu.addAction(save_action)
        
        save_as_action = QtWidgets.QAction("Save As", self)
        save_as_action.triggered.connect(self.save_picker_as)
        file_menu.addAction(save_as_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        self.undo_action = QtWidgets.QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.undo)
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QtWidgets.QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.redo)
        edit_menu.addAction(self.redo_action)
        
    def new_picker(self):
        name, ok = QtWidgets.QInputDialog.getText(
            self, "New Picker", "Enter picker name:"
        )
        if ok and name:
            self.controller.create_new_picker(name)
            self.controller.set_current_picker(name)
            
    def open_picker(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Picker", "", "Picker Files (*.picker *.json)"
        )
        if file_path:
            self.controller.load_picker(file_path)
            
    def save_picker(self):
        if hasattr(self.controller.model.current_picker, 'file_path'):
            self.controller.save_picker(self.controller.model.current_picker.file_path)
        else:
            self.save_picker_as()
            
    def save_picker_as(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Picker", "", "Picker Files (*.picker *.json)"
        )
        if file_path:
            self.controller.save_picker(file_path)
            self.controller.model.current_picker.file_path = file_path
            
    def undo(self):
        """Handle undo action"""
        self.controller.undo()
        self._update_undo_redo_actions()
        
    def redo(self):
        """Handle redo action"""
        self.controller.redo()
        self._update_undo_redo_actions()
        
    def _update_undo_redo_actions(self):
        """Update the undo/redo action labels"""
        if self.controller.undo_manager:
            self.undo_action.setText(self.controller.undo_manager.get_undo_label())
            self.redo_action.setText(self.controller.undo_manager.get_redo_label())
        
    def update_from_model(self):
        """Update the UI based on the current model state"""
        self.canvas.update_from_model()
        self.properties_widget.update_from_model()
        self._update_undo_redo_actions()