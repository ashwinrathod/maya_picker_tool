# ui/properties.py
from PySide2 import QtWidgets, QtCore, QtGui  # Add QtGui import
from core.model import Vector2, Color

class PropertiesPanel(QtWidgets.QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.current_button = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Picker properties
        self.picker_name = QtWidgets.QLineEdit()
        layout.addWidget(QtWidgets.QLabel("Picker Name:"))
        layout.addWidget(self.picker_name)
        
        # Button properties (initially hidden)
        self.button_properties = QtWidgets.QGroupBox("Button Properties")
        button_layout = QtWidgets.QFormLayout(self.button_properties)
        
        self.button_label = QtWidgets.QLineEdit()
        button_layout.addRow("Label:", self.button_label)
        
        self.button_position_x = QtWidgets.QDoubleSpinBox()
        self.button_position_x.setRange(-10000, 10000)
        self.button_position_y = QtWidgets.QDoubleSpinBox()
        self.button_position_y.setRange(-10000, 10000)
        position_layout = QtWidgets.QHBoxLayout()
        position_layout.addWidget(self.button_position_x)
        position_layout.addWidget(self.button_position_y)
        button_layout.addRow("Position:", position_layout)
        
        self.button_size_x = QtWidgets.QDoubleSpinBox()
        self.button_size_x.setRange(1, 1000)
        self.button_size_y = QtWidgets.QDoubleSpinBox()
        self.button_size_y.setRange(1, 1000)
        size_layout = QtWidgets.QHBoxLayout()
        size_layout.addWidget(self.button_size_x)
        size_layout.addWidget(self.button_size_y)
        button_layout.addRow("Size:", size_layout)
        
        # Color picker
        self.color_button = QtWidgets.QPushButton()
        self.color_button.clicked.connect(self.pick_color)
        button_layout.addRow("Color:", self.color_button)
        
        # Target nodes for select buttons
        self.target_nodes = QtWidgets.QTextEdit()
        button_layout.addRow("Target Nodes:", self.target_nodes)
        
        # Script for script buttons
        self.script_text = QtWidgets.QTextEdit()
        button_layout.addRow("Script:", self.script_text)
        
        layout.addWidget(self.button_properties)
        self.button_properties.setVisible(False)
        
        # Update button
        self.update_btn = QtWidgets.QPushButton("Update")
        self.update_btn.clicked.connect(self.update_properties)
        layout.addWidget(self.update_btn)
        
        layout.addStretch()
        
    def update_from_model(self):
        """Update properties based on current model state"""
        if self.controller.model.current_picker:
            self.picker_name.setText(self.controller.model.current_picker.name)
        
    def set_current_button(self, button_id):
        """Set the current button for property editing"""
        if not self.controller.model.current_picker:
            return
            
        button = self.controller.get_button_by_id(button_id)
        if button:
            self.current_button = button
            self.update_properties_from_button()
            
    def update_properties_from_button(self):
        """Update the UI from the current button's properties"""
        if not self.current_button:
            return
            
        # Update position
        self.button_position_x.setValue(self.current_button.position.x)
        self.button_position_y.setValue(self.current_button.position.y)
        
        # Update size
        self.button_size_x.setValue(self.current_button.size.x)
        self.button_size_y.setValue(self.current_button.size.y)
        
        # Update label
        self.button_label.setText(self.current_button.label)
        
        # Update color - This is where the error was occurring
        color = QtGui.QColor(
            int(self.current_button.color.r * 255),
            int(self.current_button.color.g * 255),
            int(self.current_button.color.b * 255),
            int(self.current_button.color.a * 255)
        )
        self.color_button.setStyleSheet(f"background-color: {color.name()}")
        
        # Update button-specific properties
        if hasattr(self.current_button, 'target_nodes'):
            self.target_nodes.setPlainText("\n".join(self.current_button.target_nodes))
            
        if hasattr(self.current_button, 'script'):
            self.script_text.setPlainText(self.current_button.script)
            
        # Show the properties panel
        self.button_properties.setVisible(True)
        
    def clear_selection(self):
        """Clear the current selection"""
        self.current_button = None
        self.button_properties.setVisible(False)
        
    def pick_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
            
    def update_properties(self):
        if not self.current_button:
            return
            
        # Update button properties from UI
        self.current_button.label = self.button_label.text()
        self.current_button.position.x = self.button_position_x.value()
        self.current_button.position.y = self.button_position_y.value()
        self.current_button.size.x = self.button_size_x.value()
        self.current_button.size.y = self.button_size_y.value()
        
        # Update color from button style
        style = self.color_button.styleSheet()
        # Parse color from style - this is a simplified approach
        if "background-color:" in style:
            color_str = style.split("background-color:")[1].split(";")[0].strip()
            color = QtGui.QColor(color_str)
            self.current_button.color.r = color.red() / 255.0
            self.current_button.color.g = color.green() / 255.0
            self.current_button.color.b = color.blue() / 255.0
            
        if hasattr(self.current_button, 'target_nodes'):
            self.current_button.target_nodes = self.target_nodes.toPlainText().split("\n")
            
        if hasattr(self.current_button, 'script'):
            self.current_button.script = self.script_text.toPlainText()
            
        # Update the view
        if self.controller.view:
            self.controller.view.update_from_model()