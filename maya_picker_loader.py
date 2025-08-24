# maya_picker_loader.py
import sys
import os
import maya.cmds as cmds

def load_picker_tool():
    """Load the Maya Picker Tool"""
    try:
        # Path to your picker tool directory
        tool_path = "C:/Users/Ashwin/Documents/maya/scripts/maya_picker_tool"
        
        # Add to Python path if not already there
        if tool_path not in sys.path:
            sys.path.append(tool_path)
        
        # Import using absolute imports
        from main import show_picker_tool
        
        # Show the tool
        window = show_picker_tool()
        if window:
            print("Maya Picker Tool loaded successfully!")
            return window
        else:
            print("Failed to load Maya Picker Tool")
            return None
            
    except Exception as e:
        print(f"Error loading Picker Tool: {str(e)}")
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
        command=(
            "import sys\n"
            "import os\n"
            "tool_path = 'C:/Users/Ashwin/Documents/maya/scripts/maya_picker_tool'\n"
            "if tool_path not in sys.path:\n"
            "    sys.path.append(tool_path)\n"
            "try:\n"
            "    from main import show_picker_tool\n"
            "    show_picker_tool()\n"
            "except Exception as e:\n"
            "    print('Error: ' + str(e))\n"
        )
    )
    print("Picker Tool shelf button created!")

# Run the tool directly
if __name__ == "__main__":
    load_picker_tool()