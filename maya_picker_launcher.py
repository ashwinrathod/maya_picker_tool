# maya_picker_launcher.py
import sys
import os
import maya.cmds as cmds

# Add the path to your picker_tool directory
tool_path = "C:/Users/Ashwin/Documents/maya/scripts/maya_picker_tool"
if tool_path not in sys.path:
    sys.path.append(tool_path)

def launch_picker():
    """Launch the picker tool with minimal imports"""
    try:
        # Import Maya UI components
        import maya.OpenMayaUI as omui
        from PySide2 import QtWidgets, QtCore, QtGui
        from shiboken2 import wrapInstance
        
        # Import our custom components
        from core.controller import PickerController
        from ui.main_window import PickerMainWindow
        
        # Get Maya main window
        main_window_ptr = omui.MQtUtil.mainWindow()
        maya_main_window = wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
        
        # Create controller and window
        controller = PickerController()
        window = PickerMainWindow(maya_main_window)
        window.show()
        
        return window
    except Exception as e:
        cmds.warning(f"Failed to launch picker tool: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Create shelf button
def create_shelf_button():
    """Create a shelf button for the picker tool"""
    shelf = cmds.shelfTabLayout("ShelfLayout", query=True, selectTab=True)
    
    # Check if button already exists
    buttons = cmds.shelfLayout(shelf, query=True, childArray=True) or []
    for btn in buttons:
        if cmds.shelfButton(btn, query=True, annotation=True) == "Maya Picker Tool":
            cmds.deleteUI(btn)
    
    # Create new button
    cmds.shelfButton(
        parent=shelf,
        annotation="Maya Picker Tool",
        label="Picker",
        image="pythonFamily.png",
        command="import maya.cmds as cmds\n"
                "try:\n"
                "    import sys\n"
                "    tool_path = 'C:/Users/Ashwin/Documents/maya/scripts/maya_picker_tool'\n"
                "    if tool_path not in sys.path:\n"
                "        sys.path.append(tool_path)\n"
                "    from maya_picker_launcher import launch_picker\n"
                "    launch_picker()\n"
                "except Exception as e:\n"
                "    cmds.warning('Error: ' + str(e))"
    )
    print("Picker Tool shelf button created!")

# Run the tool directly
if __name__ == "__main__":
    launch_picker()