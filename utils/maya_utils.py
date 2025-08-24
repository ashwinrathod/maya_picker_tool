# utils/maya_utils.py
import maya.cmds as cmds
import re

class NamespaceManager:
    def __init__(self):
        self.current_namespace = ":"
        
    def set_current_namespace(self, namespace: str):
        """Set the current namespace for operations"""
        if namespace and cmds.namespace(exists=namespace):
            self.current_namespace = namespace
        else:
            self.current_namespace = ":"
            
    def resolve_name(self, node_name: str) -> str:
        """Resolve a node name with the current namespace"""
        if not node_name:
            return node_name
            
        # If already has a namespace, return as is
        if ":" in node_name and not node_name.startswith(":"):
            return node_name
            
        # If starts with :, it's absolute
        if node_name.startswith(":"):
            return node_name
            
        # Otherwise, prepend current namespace
        if self.current_namespace == ":":
            return node_name
        else:
            return f"{self.current_namespace}:{node_name}"
            
    def get_namespaces(self) -> List[str]:
        """Get all namespaces in the scene"""
        return cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        
    def get_nodes_in_namespace(self, namespace: str) -> List[str]:
        """Get all nodes in a namespace"""
        if not cmds.namespace(exists=namespace):
            return []
            
        current_ns = cmds.namespaceInfo(currentNamespace=True)
        try:
            cmds.namespace(set=namespace)
            nodes = cmds.namespaceInfo(listOnlyDependencyNodes=True)
            return nodes
        finally:
            cmds.namespace(set=current_ns)

# Update the controller to use namespace management
class PickerController:
    def __init__(self):
        self.model = PickerModel()
        self.view = None
        self.undo_manager = UndoRedoManager()
        self.namespace_manager = NamespaceManager()
        
    def _execute_select_button(self, button: SelectButton):
        if not button.target_nodes:
            return
            
        # Clear selection first
        cmds.select(clear=True)
        
        # Select target nodes with namespace resolution
        for node in button.target_nodes:
            resolved_node = self.namespace_manager.resolve_name(node)
            if cmds.objExists(resolved_node):
                cmds.select(resolved_node, add=True)