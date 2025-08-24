# utils/svg_utils.py
import os
import tempfile
from PySide2 import QtWidgets, QtCore, QtGui, QtSvg

class SVGUtils:
    def __init__(self):
        self.svg_renderer = QtSvg.QSvgRenderer()
        
    def load_svg(self, file_path):
        """Load an SVG file"""
        return self.svg_renderer.load(file_path)
        
    def render_svg(self, file_path, size):
        """Render SVG to a pixmap at the given size"""
        if not self.svg_renderer.load(file_path):
            return None
            
        pixmap = QtGui.QPixmap(size)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        self.svg_renderer.render(painter)
        painter.end()
        
        return pixmap
        
    def svg_to_base64(self, file_path):
        """Convert SVG file to base64 string for embedding"""
        with open(file_path, 'rb') as f:
            return f.read().encode('base64')
            
    def base64_to_svg(self, base64_str, file_path=None):
        """Convert base64 string to SVG file"""
        svg_data = base64_str.decode('base64')
        
        if file_path:
            with open(file_path, 'wb') as f:
                f.write(svg_data)
            return file_path
        else:
            # Create temporary file
            fd, temp_path = tempfile.mkstemp(suffix='.svg')
            with os.fdopen(fd, 'wb') as f:
                f.write(svg_data)
            return temp_path
            
    def create_svg_button(self, svg_path, position, size):
        """Create a button from an SVG file"""
        from ..core.model import BaseButton, ButtonType
        
        button = BaseButton(
            id=f"svg_button_{hash(svg_path)}_{position.x}_{position.y}",
            type=ButtonType.SELECT,  # Default type
            position=position,
            size=size
        )
        
        button.svg_path = svg_path
        button.is_svg = True
        
        return button
        
    def extract_svg_paths(self, svg_content):
        """Extract individual paths from SVG content for editing"""
        # This is a simplified implementation
        # In a real implementation, you would use a proper SVG parser
        paths = []
        
        # Simple regex to find path elements
        import re
        path_pattern = r'<path[^>]*d="([^"]*)"[^>]*>'
        
        for match in re.finditer(path_pattern, svg_content):
            paths.append(match.group(1))
            
        return paths
        
    def create_svg_from_paths(self, paths, width, height):
        """Create SVG content from path data"""
        svg_template = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="black" stroke-width="2">
        {''.join(f'<path d="{path}"/>' for path in paths)}
    </g>
</svg>'''
        
        return svg_template