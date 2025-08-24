# utils/mirror_tools.py
import maya.cmds as cmds
import re

class MirrorTools:
    def __init__(self):
        self.mirror_patterns = [
            (r'^L_', 'R_'),
            (r'^R_', 'L_'),
            (r'_L$', '_R'),
            (r'_R$', '_L'),
            (r'Left', 'Right'),
            (r'Right', 'Left'),
            (r'left', 'right'),
            (r'right', 'left'),
        ]
        
    def mirror_node_name(self, node_name, axis='X'):
        """Mirror a node name based on naming conventions"""
        for pattern, replacement in self.mirror_patterns:
            if re.search(pattern, node_name):
                return re.sub(pattern, replacement, node_name)
                
        # If no pattern matched, try to add/remove L/R prefix
        if node_name.startswith('L_'):
            return 'R_' + node_name[2:]
        elif node_name.startswith('R_'):
            return 'L_' + node_name[2:]
        elif node_name.startswith('Left'):
            return 'Right' + node_name[4:]
        elif node_name.startswith('Right'):
            return 'Left' + node_name[5:]
        elif node_name.startswith('left'):
            return 'right' + node_name[4:]
        elif node_name.startswith('right'):
            return 'left' + node_name[5:]
            
        return node_name
        
    def mirror_position(self, position, axis='X', center=0.0):
        """Mirror a position across an axis"""
        if axis == 'X':
            return Vector2(2 * center - position.x, position.y)
        elif axis == 'Y':
            return Vector2(position.x, 2 * center - position.y)
        elif axis == 'XY':
            return Vector2(2 * center - position.x, 2 * center - position.y)
        return position
        
    def mirror_button(self, button, axis='X', center=0.0):
        """Create a mirrored version of a button"""
        from core.model import SelectButton, PoseButton, AttributeButton
        
        # Create a copy of the button
        mirrored = button.__class__.__new__(button.__class__)
        mirrored.__dict__ = button.__dict__.copy()
        
        # Mirror position
        mirrored.position = self.mirror_position(button.position, axis, center)
        
        # Mirror target nodes for select and pose buttons
        if isinstance(button, (SelectButton, PoseButton)):
            mirrored.target_nodes = [
                self.mirror_node_name(node, axis) for node in button.target_nodes
            ]
            
        # Mirror attribute targets for attribute buttons
        if isinstance(button, AttributeButton):
            mirrored.target_node = self.mirror_node_name(button.target_node, axis)
            
        return mirrored