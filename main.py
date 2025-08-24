# main.py - Remove search tool import and creation
import sys
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

# Add current directory to path in a way that works in Maya
try:
    # This works when the file is executed directly
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # This works when executed via exec() in Maya
    current_dir = "C:/Users/Ashwin/Documents/maya/scripts/maya_picker_tool"

if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import all components
try:
    from core.controller import PickerController
    from core.model import PickerModel, ButtonType
    from ui.main_window import PickerMainWindow
    from utils.undo import EnhancedUndoRedoManager
    from utils.mirror_tools import MirrorTools
    from utils.svg_utils import SVGUtils
    from utils.hotkey_manager import HotkeyManager
    from core.organization import PickerOrganizer
    
    print("All imports successful")
except ImportError as e:
    print(f"Import error: {e}")
    # Try to import just the essentials
    try:
        from core.controller import PickerController
        from ui.main_window import PickerMainWindow
        print("Essential imports successful")
    except ImportError as e2:
        print(f"Critical import error: {e2}")
        raise

def maya_main_window():
    """Return the Maya main window widget"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is not None:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    return None

def show_picker_tool():
    """Show the picker tool window with all features"""
    # Check if window already exists
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, QtWidgets.QMainWindow) and widget.windowTitle() == "Maya Picker Tool":
            widget.close()
            widget.deleteLater()
            
    # Create new window
    main_window = maya_main_window()
    if main_window is None:
        print("Error: Could not find Maya main window")
        return None
        
    try:
        # Create controller with all utilities
        controller = PickerController()
        
        # Try to initialize optional utilities
        try:
            controller.undo_manager = EnhancedUndoRedoManager()
        except:
            print("Could not initialize undo manager")
            
        try:
            controller.mirror_tools = MirrorTools()
        except:
            print("Could not initialize mirror tools")
            
        try:
            controller.svg_utils = SVGUtils()
        except:
            print("Could not initialize SVG utils")
            
        try:
            controller.hotkey_manager = HotkeyManager(controller)
        except:
            print("Could not initialize hotkey manager")
            
        try:
            controller.organizer = PickerOrganizer()
        except:
            print("Could not initialize organizer")
        
        # Create main window
        window = PickerMainWindow(controller, main_window)
        
        # Try to add optional panels (removed search tool)
        try:
            from ui.mirror_panel import MirrorPanel
            mirror_panel = MirrorPanel(controller)
            window.addDockWidget(QtCore.Qt.RightDockWidgetArea, mirror_panel)
        except Exception as e:
            print(f"Could not load Mirror Panel: {e}")
            
        try:
            from ui.organization_panel import OrganizationPanel
            org_panel = OrganizationPanel(controller)
            window.addDockWidget(QtCore.Qt.RightDockWidgetArea, org_panel)
        except Exception as e:
            print(f"Could not load Organization Panel: {e}")
            
        window.show()
        
        # Make it dockable in Maya
        window.setProperty("saveWindowPref", True)
        
        print("Maya Picker Tool loaded successfully!")
        return window
        
    except Exception as e:
        print(f"Error creating Picker Tool window: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Run if executed directly
if __name__ == "__main__":
    show_picker_tool()