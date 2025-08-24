# ui/debug_overlay.py
from PySide2 import QtWidgets, QtCore, QtGui

class DebugOverlay(QtWidgets.QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Overlay data
        self.connections = []
        self.highlighted_nodes = []
        self.debug_text = []
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw connections
        for connection in self.connections:
            painter.setPen(QtGui.QPen(QtCore.Qt.yellow, 2, QtCore.Qt.DashLine))
            painter.drawLine(connection['start'], connection['end'])
            
            # Draw arrowhead
            if 'arrow' in connection and connection['arrow']:
                self.draw_arrowhead(painter, connection['start'], connection['end'])
                
        # Draw highlighted nodes
        for node in self.highlighted_nodes:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 3))
            painter.drawRect(node['rect'])
            
        # Draw debug text
        painter.setPen(QtGui.QPen(QtCore.Qt.white))
        for i, text in enumerate(self.debug_text):
            painter.drawText(10, 20 + i * 15, text)
            
    def draw_arrowhead(self, painter, start, end):
        # Calculate arrowhead points
        angle = QtCore.QLineF(start, end).angle()
        
        arrow_size = 10
        arrow_p1 = end - QtCore.QPointF(
            arrow_size * QtCore.QMath.cos((angle + 150) * 3.14159 / 180),
            arrow_size * QtCore.QMath.sin((angle + 150) * 3.14159 / 180)
        )
        arrow_p2 = end - QtCore.QPointF(
            arrow_size * QtCore.QMath.cos((angle - 150) * 3.14159 / 180),
            arrow_size * QtCore.QMath.sin((angle - 150) * 3.14159 / 180)
        )
        
        # Draw arrowhead
        painter.drawLine(end, arrow_p1)
        painter.drawLine(end, arrow_p2)
        
    def add_connection(self, start, end, arrow=True):
        self.connections.append({
            'start': start,
            'end': end,
            'arrow': arrow
        })
        self.update()
        
    def add_highlight(self, rect):
        self.highlighted_nodes.append({
            'rect': rect
        })
        self.update()
        
    def add_text(self, text):
        self.debug_text.append(text)
        self.update()
        
    def clear(self):
        self.connections = []
        self.highlighted_nodes = []
        self.debug_text = []
        self.update()