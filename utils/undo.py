# utils/undo.py
import maya.cmds as cmds
from typing import List, Callable, Any, Tuple

class MayaUndoChunk:
    """Context manager for Maya undo chunks"""
    def __enter__(self):
        cmds.undoInfo(openChunk=True)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(closeChunk=True)

class UndoRedoManager:
    def __init__(self, max_history=50):
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = max_history
        self.current_action = None
        
    def begin_action(self, name: str):
        """Begin a new undoable action"""
        if self.current_action is not None:
            self.end_action()
            
        self.current_action = {
            "name": name,
            "undo_ops": [],
            "redo_ops": []
        }
        
    def end_action(self):
        """End the current action and add it to the undo stack"""
        if self.current_action and self.current_action["undo_ops"]:
            self.undo_stack.append(self.current_action)
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
            self.redo_stack.clear()
            
        self.current_action = None
        
    def add_operation(self, undo_func, redo_func, *args):
        """Add an operation to the current action"""
        if self.current_action is not None:
            self.current_action["undo_ops"].append((undo_func, args))
            self.current_action["redo_ops"].append((redo_func, args))
        
    def undo(self):
        """Undo the last action"""
        if not self.undo_stack:
            return
        
        with MayaUndoChunk():
            action = self.undo_stack.pop()
            for undo_func, args in reversed(action["undo_ops"]):
                try:
                    undo_func(*args)
                except Exception as e:
                    print(f"Undo operation failed: {e}")
                
        self.redo_stack.append(action)
    
    def redo(self):
        """Redo the last undone action"""
        if not self.redo_stack:
            return
        
        with MayaUndoChunk():
            action = self.redo_stack.pop()
            for redo_func, args in action["redo_ops"]:
                try:
                    redo_func(*args)
                except Exception as e:
                    print(f"Redo operation failed: {e}")
                
        self.undo_stack.append(action)
        
    def get_undo_label(self) -> str:
        """Get the label for the next undo operation"""
        if self.undo_stack:
            return f"Undo {self.undo_stack[-1]['name']}"
        return "Undo"
        
    def get_redo_label(self) -> str:
        """Get the label for the next redo operation"""
        if self.redo_stack:
            return f"Redo {self.redo_stack[-1]['name']}"
        return "Redo"

class EnhancedUndoRedoManager:
    def __init__(self, max_history=50):
        self.undo_stack: List[Tuple[str, Callable, Tuple]] = []
        self.redo_stack: List[Tuple[str, Callable, Tuple]] = []
        self.max_history = max_history
        self.current_action = None
        
    def begin_action(self, name: str):
        """Begin a new undoable action"""
        if self.current_action is not None:
            self.end_action()
            
        self.current_action = {
            "name": name,
            "undo_ops": [],
            "redo_ops": []
        }
        
    def end_action(self):
        """End the current action and add it to the undo stack"""
        if self.current_action and self.current_action["undo_ops"]:
            # Only add to undo stack if there are operations
            self.undo_stack.append((
                self.current_action["name"],
                self._execute_undo_ops,
                (self.current_action["undo_ops"],)
            ))
            
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
                
            self.redo_stack.clear()
            
        self.current_action = None
        
    def add_operation(self, undo_func: Callable, redo_func: Callable, *args):
        """Add an operation to the current action"""
        if self.current_action is not None:
            self.current_action["undo_ops"].append((undo_func, args))
            self.current_action["redo_ops"].append((redo_func, args))
        
    def _execute_undo_ops(self, ops):
        """Execute a list of undo operations"""
        with MayaUndoChunk():
            for undo_func, args in reversed(ops):
                undo_func(*args)
                
    def _execute_redo_ops(self, ops):
        """Execute a list of redo operations"""
        with MayaUndoChunk():
            for redo_func, args in ops:
                redo_func(*args)
                
    def undo(self):
        """Undo the last action"""
        if not self.undo_stack:
            return
            
        name, undo_func, args = self.undo_stack.pop()
        undo_func(*args)
        
        # Add to redo stack
        self.redo_stack.append((name, self._execute_redo_ops, args))
        
    def redo(self):
        """Redo the last undone action"""
        if not self.redo_stack:
            return
            
        name, redo_func, args = self.redo_stack.pop()
        redo_func(*args)
        
        # Add back to undo stack
        self.undo_stack.append((name, self._execute_undo_ops, args))
        
    def clear(self):
        """Clear the undo/redo history"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_action = None
        
    def get_undo_label(self) -> str:
        """Get the label for the next undo operation"""
        if self.undo_stack:
            return f"Undo {self.undo_stack[-1][0]}"
        return "Undo"
        
    def get_redo_label(self) -> str:
        """Get the label for the next redo operation"""
        if self.redo_stack:
            return f"Redo {self.redo_stack[-1][0]}"
        return "Redo"

# Example usage in the controller:
class PickerController:
    def __init__(self):
        self.model = PickerModel()
        self.view = None
        self.undo_manager = UndoRedoManager()
        
    def add_button(self, button_type, **kwargs):
        if not self.model.current_picker:
            cmds.warning("No current picker selected")
            return None
            
        # Generate a unique ID
        button_id = f"button_{len(self.model.current_picker.buttons) + 1}"
        
        # Store current state for undo
        old_buttons = self.model.current_picker.buttons.copy()
        
        if button_type == "select":
            button = SelectButton(id=button_id, **kwargs)
        elif button_type == "script":
            button = ScriptButton(id=button_id, **kwargs)
        elif button_type == "pose":
            button = PoseButton(id=button_id, **kwargs)
        elif button_type == "attribute":
            button = AttributeButton(id=button_id, **kwargs)
        elif button_type == "slider":
            button = Slider(id=button_id, **kwargs)
        elif button_type == "text":
            button = TextButton(id=button_id, **kwargs)
        else:
            return None
            
        self.model.current_picker.buttons.append(button)
        
        # Add to undo stack
        self.undo_manager.begin_action("Add Button")
        self.undo_manager.add_operation(
            lambda: setattr(self.model.current_picker, 'buttons', old_buttons),
            lambda: setattr(self.model.current_picker, 'buttons', self.model.current_picker.buttons)
        )
        self.undo_manager.end_action()
        
        return button