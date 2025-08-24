# ui/mirror_panel.py
from PySide2 import QtWidgets, QtCore, QtGui
from utils.mirror_tools import MirrorTools

class MirrorPanel(QtWidgets.QDockWidget):
    def __init__(self, controller, parent=None):
        super().__init__("Mirror Tools", parent)
        self.controller = controller
        self.mirror_tools = MirrorTools()
        self.setup_ui()
        
    def setup_ui(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Mirror axis selection
        axis_group = QtWidgets.QGroupBox("Mirror Axis")
        axis_layout = QtWidgets.QHBoxLayout(axis_group)
        
        self.axis_x = QtWidgets.QRadioButton("X")
        self.axis_x.setChecked(True)
        self.axis_y = QtWidgets.QRadioButton("Y")
        self.axis_xy = QtWidgets.QRadioButton("XY")
        
        axis_layout.addWidget(self.axis_x)
        axis_layout.addWidget(self.axis_y)
        axis_layout.addWidget(self.axis_xy)
        layout.addWidget(axis_group)
        
        # Center point
        center_group = QtWidgets.QGroupBox("Center Point")
        center_layout = QtWidgets.QFormLayout(center_group)
        
        self.center_x = QtWidgets.QDoubleSpinBox()
        self.center_x.setRange(-10000, 10000)
        self.center_x.setValue(0.0)
        
        self.center_y = QtWidgets.QDoubleSpinBox()
        self.center_y.setRange(-10000, 10000)
        self.center_y.setValue(0.0)
        
        center_layout.addRow("X:", self.center_x)
        center_layout.addRow("Y:", self.center_y)
        layout.addWidget(center_group)
        
        # Mirror options
        options_group = QtWidgets.QGroupBox("Options")
        options_layout = QtWidgets.QVBoxLayout(options_group)
        
        self.mirror_position = QtWidgets.QCheckBox("Mirror Position")
        self.mirror_position.setChecked(True)
        
        self.mirror_nodes = QtWidgets.QCheckBox("Mirror Node Names")
        self.mirror_nodes.setChecked(True)
        
        self.create_new = QtWidgets.QCheckBox("Create New Buttons")
        self.create_new.setChecked(True)
        
        self.replace_existing = QtWidgets.QCheckBox("Replace Existing")
        self.replace_existing.setChecked(False)
        
        options_layout.addWidget(self.mirror_position)
        options_layout.addWidget(self.mirror_nodes)
        options_layout.addWidget(self.create_new)
        options_layout.addWidget(self.replace_existing)
        layout.addWidget(options_group)
        
        # Mirror button
        self.mirror_btn = QtWidgets.QPushButton("Mirror Selection")
        self.mirror_btn.clicked.connect(self.execute_mirror)
        layout.addWidget(self.mirror_btn)
        
        # Auto-detect center
        self.auto_center_btn = QtWidgets.QPushButton("Auto-Detect Center")
        self.auto_center_btn.clicked.connect(self.auto_detect_center)
        layout.addWidget(self.auto_center_btn)
        
        layout.addStretch()
        self.setWidget(widget)
        
    def get_axis(self):
        if self.axis_x.isChecked():
            return "X"
        elif self.axis_y.isChecked():
            return "Y"
        else:
            return "XY"
            
    def get_center(self):
        return (self.center_x.value(), self.center_y.value())
        
    def auto_detect_center(self):
        if not self.controller.model.current_picker:
            return
            
        # Calculate center based on all buttons
        buttons = self.controller.model.current_picker.buttons
        if not buttons:
            return
            
        min_x = min(button.position.x for button in buttons)
        max_x = max(button.position.x + button.size.x for button in buttons)
        min_y = min(button.position.y for button in buttons)
        max_y = max(button.position.y + button.size.y for button in buttons)
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        self.center_x.setValue(center_x)
        self.center_y.setValue(center_y)
        
    def execute_mirror(self):
        if not self.controller.model.current_picker:
            return
            
        axis = self.get_axis()
        center_x, center_y = self.get_center()
        
        # Get selected buttons
        selected_ids = self.controller.view.canvas.get_selected_button_ids()
        selected_buttons = [
            button for button in self.controller.model.current_picker.buttons
            if button.id in selected_ids
        ]
        
        if not selected_buttons:
            # If nothing selected, mirror all buttons
            selected_buttons = self.controller.model.current_picker.buttons
            
        # Begin undo action
        self.controller.undo_manager.begin_action("Mirror Buttons")
        
        # Store original state for undo
        original_buttons = self.controller.model.current_picker.buttons.copy()
        
        # Mirror buttons
        new_buttons = []
        for button in selected_buttons:
            mirrored = self.mirror_tools.mirror_button(
                button, axis, (center_x, center_y))
            new_buttons.append(mirrored)
            
            if self.replace_existing.isChecked():
                # Replace original button
                index = self.controller.model.current_picker.buttons.index(button)
                self.controller.model.current_picker.buttons[index] = mirrored
                
        if self.create_new.isChecked() and not self.replace_existing.isChecked():
            # Add new mirrored buttons
            self.controller.model.current_picker.buttons.extend(new_buttons)
            
        # Add to undo stack
        self.controller.undo_manager.add_operation(
            lambda: setattr(self.controller.model.current_picker, 'buttons', original_buttons),
            lambda: setattr(self.controller.model.current_picker, 'buttons', 
                           self.controller.model.current_picker.buttons)
        )
        self.controller.undo_manager.end_action()
        
        # Update view
        if self.controller.view:
            self.controller.view.update_from_model()