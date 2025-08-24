# test_undo_redo.py
import maya.cmds as cmds
import sys
import os

# Add the path to your picker_tool directory
tool_path = "C:/Users/Ashwin/Documents/maya/scripts/maya_picker_tool"
if tool_path not in sys.path:
    sys.path.append(tool_path)

try:
    from core.controller import PickerController
    from core.model import Vector2, Color
    
    print("=== UNDO/REDO TEST ===")
    
    # Create a test controller
    controller = PickerController()
    
    # Create a new picker
    print("1. Creating new picker...")
    picker = controller.create_new_picker("TestUndoRedo")
    controller.set_current_picker("TestUndoRedo")
    
    # Create a button
    print("2. Creating button...")
    button = controller.add_button(
        "select",
        position=Vector2(50, 50),
        size=Vector2(80, 40),
        label="Test Button"
    )
    
    print(f"3. Buttons count: {len(controller.model.current_picker.buttons)}")
    
    # Undo the button creation
    print("4. Undoing button creation...")
    controller.undo()
    print(f"5. Buttons count after undo: {len(controller.model.current_picker.buttons)}")
    
    # Redo the button creation
    print("6. Redoing button creation...")
    controller.redo()
    print(f"7. Buttons count after redo: {len(controller.model.current_picker.buttons)}")
    
    # Test multiple operations
    print("8. Creating multiple buttons...")
    button2 = controller.add_button(
        "select",
        position=Vector2(150, 50),
        size=Vector2(80, 40),
        label="Button 2"
    )
    
    button3 = controller.add_button(
        "select",
        position=Vector2(250, 50),
        size=Vector2(80, 40),
        label="Button 3"
    )
    
    print(f"9. Buttons count after adding more: {len(controller.model.current_picker.buttons)}")
    
    # Undo multiple times
    print("10. Undoing multiple operations...")
    controller.undo()  # Undo button 3
    print(f"11. Buttons count after undo 1: {len(controller.model.current_picker.buttons)}")
    
    controller.undo()  # Undo button 2
    print(f"12. Buttons count after undo 2: {len(controller.model.current_picker.buttons)}")
    
    # Redo multiple times
    print("13. Redoing multiple operations...")
    controller.redo()  # Redo button 2
    print(f"14. Buttons count after redo 1: {len(controller.model.current_picker.buttons)}")
    
    controller.redo()  # Redo button 3
    print(f"15. Buttons count after redo 2: {len(controller.model.current_picker.buttons)}")
    
    print("=== UNDO/REDO TEST COMPLETED SUCCESSFULLY ===")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()