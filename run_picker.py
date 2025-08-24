# run_picker.py
import sys
import os

# Add the path to your picker_tool directory
tool_path = "C:/Users/Ashwin/Documents/maya/scripts/maya_picker_tool"
if tool_path not in sys.path:
    sys.path.append(tool_path)

try:
    from main import show_picker_tool
    show_picker_tool()
except Exception as e:
    print(f"Error loading Picker Tool: {str(e)}")
    import traceback
    traceback.print_exc()