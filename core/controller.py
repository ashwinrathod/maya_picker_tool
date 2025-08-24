# core/controller.py
import maya.cmds as cmds
from .model import PickerModel, SelectButton, ScriptButton, PoseButton, AttributeButton, Slider, Checkbox, RadiusButton, TextButton, Vector2, Color, ButtonType, ShapeType
from utils.undo import UndoRedoManager  # Add this import

class PickerController:
    def __init__(self):
        self.model = PickerModel()
        self.view = None
        self.undo_manager = None
        self.mirror_tools = None
        self.svg_utils = None
        self.hotkey_manager = None
        self.organizer = None
        
    def create_new_picker(self, name: str):
        return self.model.add_picker(name)
    
    def set_current_picker(self, name: str):
        if name in self.model.pickers:
            self.model.current_picker = self.model.pickers[name]
            if self.view:
                self.view.update_from_model()
    
    # core/controller.py - Update the add_button method's undo/redo operations
    def add_button(self, button_type, **kwargs):
        if not self.model.current_picker:
            cmds.warning("No current picker selected")
            return None
            
        # Store current state for undo
        import copy
        old_buttons = copy.deepcopy(self.model.current_picker.buttons)
        
        # Generate a unique ID
        button_id = f"button_{len(self.model.current_picker.buttons) + 1}"
        
        # Set default values for required parameters
        defaults = {
            'id': button_id,
            'position': Vector2(0, 0),
            'size': Vector2(50, 50),
            'color': Color(0.5, 0.5, 0.5),
            'label': f"Button {button_id}",
            'tooltip': "",
            'visible': True,
            'locked': False,
            'shape': ShapeType.RECTANGLE,
            'corner_radius': 10.0,
            'sides': 6
        }
        
        # Apply defaults
        for key, value in defaults.items():
            if key not in kwargs:
                kwargs[key] = value
        
        # Create the appropriate button type
        if button_type == "select":
            button = SelectButton(**kwargs)
        elif button_type == "script":
            button = ScriptButton(**kwargs)
        elif button_type == "pose":
            button = PoseButton(**kwargs)
        elif button_type == "attribute":
            button = AttributeButton(**kwargs)
        elif button_type == "slider":
            button = Slider(**kwargs)
        elif button_type == "checkbox":
            button = Checkbox(**kwargs)
        elif button_type == "radius":
            button = RadiusButton(**kwargs)
        elif button_type == "text":
            button = TextButton(**kwargs)
        else:
            return None
            
        self.model.current_picker.buttons.append(button)
        
        # Store new state for redo
        new_buttons = copy.deepcopy(self.model.current_picker.buttons)
        
        # Add to undo stack
        if self.undo_manager:
            self.undo_manager.begin_action("Add Button")
            self.undo_manager.add_operation(
                lambda b=old_buttons: self._set_buttons(b),
                lambda b=new_buttons: self._set_buttons(b)
            )
            self.undo_manager.end_action()
        
        return button

    def _set_buttons(self, buttons):
        """Set the current picker's buttons list"""
        if self.model.current_picker:
            self.model.current_picker.buttons = buttons
            if self.view:
                self.view.update_from_model()
    
    def execute_button(self, button_id: str):
        if not self.model.current_picker:
            return
            
        button = next((b for b in self.model.current_picker.buttons if b.id == button_id), None)
        if not button:
            return
            
        if isinstance(button, SelectButton):
            self._execute_select_button(button)
        elif isinstance(button, ScriptButton):
            self._execute_script_button(button)
        elif isinstance(button, PoseButton):
            self._execute_pose_button(button)
        elif isinstance(button, AttributeButton):
            self._execute_attribute_button(button)
        elif isinstance(button, Slider):
            self._execute_slider(button)
        elif isinstance(button, Checkbox):
            self._execute_checkbox(button)
        elif isinstance(button, RadiusButton):
            self._execute_radius_button(button)
        # Text buttons don't need execution
    
    def _execute_select_button(self, button: SelectButton):
        if not button.target_nodes:
            cmds.warning(f"Select button '{button.label}' has no target nodes")
            return
            
        # Clear selection first
        cmds.select(clear=True)
        
        selected_any = False
        # Select target nodes
        for node in button.target_nodes:
            if cmds.objExists(node):
                cmds.select(node, add=True)
                selected_any = True
        
        if not selected_any:
            cmds.warning(f"No valid target nodes found for button '{button.label}'")

    def _execute_script_button(self, button: ScriptButton):
        if not button.script:
            cmds.warning(f"Script button '{button.label}' has no script")
            return
            
        try:
            if button.language == "python":
                # Execute in global namespace to access maya.cmds
                exec(button.script, globals())
            elif button.language == "mel":
                mel_result = cmds.mel.eval(button.script)
            print(f"Executed script from button '{button.label}'")
        except Exception as e:
            cmds.warning(f"Script execution error in button '{button.label}': {str(e)}")

    def _execute_pose_button(self, button: PoseButton):
        if not button.target_nodes:
            cmds.warning(f"Pose button '{button.label}' has no target nodes")
            return
            
        applied_any = False
        for node in button.target_nodes:
            if cmds.objExists(node) and node in button.pose_data:
                for attr, value in button.pose_data[node].items():
                    attr_path = f"{node}.{attr}"
                    if cmds.objExists(attr_path):
                        try:
                            cmds.setAttr(attr_path, value)
                            applied_any = True
                        except Exception as e:
                            cmds.warning(f"Could not set {attr_path}: {str(e)}")
        
        if applied_any:
            print(f"Applied pose from button '{button.label}'")
        else:
            cmds.warning(f"Could not apply pose from button '{button.label}'")

    def _execute_attribute_button(self, button: AttributeButton):
        if not button.target_node or not button.attribute:
            cmds.warning(f"Attribute button '{button.label}' is missing target or attribute")
            return
            
        attr_path = f"{button.target_node}.{button.attribute}"
        if not cmds.objExists(attr_path):
            cmds.warning(f"Attribute button '{button.label}': {attr_path} does not exist")
            return
            
        try:
            if button.operation == "set":
                cmds.setAttr(attr_path, button.value)
                print(f"Set {attr_path} to {button.value}")
            elif button.operation == "toggle":
                current = cmds.getAttr(attr_path)
                cmds.setAttr(attr_path, not current)
                print(f"Toggled {attr_path} from {current} to {not current}")
            elif button.operation == "nudge":
                current = cmds.getAttr(attr_path)
                new_value = current + button.nudge_amount
                cmds.setAttr(attr_path, new_value)
                print(f"Nudged {attr_path} from {current} to {new_value}")
        except Exception as e:
            cmds.warning(f"Attribute operation failed for button '{button.label}': {str(e)}")

    def _execute_slider(self, button: Slider):
        # Sliders are typically controlled through UI, but we can set values if needed
        if button.target_node and button.attribute:
            attr_path = f"{button.target_node}.{button.attribute}"
            if cmds.objExists(attr_path):
                try:
                    cmds.setAttr(attr_path, button.current_value)
                except Exception as e:
                    cmds.warning(f"Slider operation failed: {str(e)}")
                    
        if button.is_2d and button.second_attribute and button.target_node:
            attr_path = f"{button.target_node}.{button.second_attribute}"
            if cmds.objExists(attr_path):
                try:
                    cmds.setAttr(attr_path, button.second_current_value)
                except Exception as e:
                    cmds.warning(f"Slider operation failed: {str(e)}")

    def _execute_checkbox(self, button: Checkbox):
        if not button.target_node or not button.attribute:
            cmds.warning(f"Checkbox button '{button.label}' is missing target or attribute")
            return
            
        attr_path = f"{button.target_node}.{button.attribute}"
        if not cmds.objExists(attr_path):
            cmds.warning(f"Checkbox button '{button.label}': {attr_path} does not exist")
            return
            
        try:
            # Toggle the checkbox state
            new_value = button.unchecked_value if button.is_checked else button.checked_value
            cmds.setAttr(attr_path, new_value)
            button.is_checked = not button.is_checked
            print(f"Checkbox {attr_path} set to {new_value}")
        except Exception as e:
            cmds.warning(f"Checkbox operation failed for button '{button.label}': {str(e)}")
    
    def _execute_radius_button(self, button: RadiusButton):
        if not button.target_node or not button.attribute:
            cmds.warning(f"Radius button '{button.label}' is missing target or attribute")
            return
            
        attr_path = f"{button.target_node}.{button.attribute}"
        if not cmds.objExists(attr_path):
            cmds.warning(f"Radius button '{button.label}': {attr_path} does not exist")
            return
            
        try:
            cmds.setAttr(attr_path, button.current_value)
            print(f"Radius {attr_path} set to {button.current_value}")
        except Exception as e:
            cmds.warning(f"Radius operation failed for button '{button.label}': {str(e)}")
    
    def save_picker(self, file_path: str):
        return self.model.save_to_file(file_path)
    
    def load_picker(self, file_path: str):
        return self.model.load_from_file(file_path)
    
    def get_button_by_id(self, button_id: str):
        """Get a button by its ID"""
        if not self.model.current_picker:
            return None
            
        return next((b for b in self.model.current_picker.buttons if b.id == button_id), None)
        
    def undo(self):
        """Perform undo operation"""
        self.undo_manager.undo()
        if self.view:
            self.view.update_from_model()

    def redo(self):
        """Perform redo operation"""
        self.undo_manager.redo()
        if self.view:
            self.view.update_from_model()