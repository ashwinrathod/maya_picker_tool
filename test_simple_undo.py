# test_simple_undo.py
import maya.cmds as cmds
import sys
import os
import copy

# Add the path to your picker_tool directory
tool_path = "C:/Users/Ashwin/Documents/maya/scripts/maya_picker_tool"
if tool_path not in sys.path:
    sys.path.append(tool_path)

try:
    from core.controller import PickerController
    from core.model import Vector2, Color
    
    print("=== SIMPLE UNDO TEST ===")
    
    # Create a test controller
    controller = PickerController()
    
    # Create a new picker
    print("1. Creating new picker...")
    picker = controller.create_new_picker("TestSimpleUndo")
    controller.set_current_picker("TestSimpleUndo")
    
    print(f"2. Initial buttons count: {len(controller.model.current_picker.buttons)}")
    
    # Create a button
    print("3. Creating button...")
    button = controller.add_button(
        "select",
        position=Vector2(50, 50),
        size=Vector2(80, 40),
        label="Test Button"
    )
    
    print(f"4. Buttons count after creation: {len(controller.model.current_picker.buttons)}")
    print(f"5. Button ID: {button.id if button else 'None'}")
    
    # Test undo
    print("6. Testing undo...")
    controller.undo()
    print(f"7. Buttons count after undo: {len(controller.model.current_picker.buttons)}")
    
    # Test redo
    print("8. Testing redo...")
    controller.redo()
    print(f"9. Buttons count after redo: {len(controller.model.current_picker.buttons)}")
    
    # Test button execution after redo
    if controller.model.current_picker.buttons:
        button_id = controller.model.current_picker.buttons[0].id
        print(f"10. Testing button execution after redo...")
        controller.execute_button(button_id)
    
    print("=== SIMPLE UNDO TEST COMPLETED ===")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()