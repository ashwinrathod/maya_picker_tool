# ui/shape_editor.py
from PySide2 import QtWidgets, QtCore, QtGui
from core.model import Vector2

class ShapeEditor(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Shape Editor")
        self.resize(800, 600)
        self.setup_ui()
        
        # Shape data
        self.points = []
        self.control_points = []  # For bezier curves
        self.current_tool = "select"  # select, pen, bezier, rectangle, ellipse
        
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Toolbar
        toolbar = QtWidgets.QToolBar()
        layout.addWidget(toolbar)
        
        # Tools
        self.select_tool = QtWidgets.QAction("Select", self)
        self.select_tool.setCheckable(True)
        self.select_tool.setChecked(True)
        self.select_tool.triggered.connect(lambda: self.set_tool("select"))
        
        self.pen_tool = QtWidgets.QAction("Pen", self)
        self.pen_tool.setCheckable(True)
        self.pen_tool.triggered.connect(lambda: self.set_tool("pen"))
        
        self.bezier_tool = QtWidgets.QAction("Bezier", self)
        self.bezier_tool.setCheckable(True)
        self.bezier_tool.triggered.connect(lambda: self.set_tool("bezier"))
        
        self.rect_tool = QtWidgets.QAction("Rectangle", self)
        self.rect_tool.setCheckable(True)
        self.rect_tool.triggered.connect(lambda: self.set_tool("rectangle"))
        
        self.ellipse_tool = QtWidgets.QAction("Ellipse", self)
        self.ellipse_tool.setCheckable(True)
        self.ellipse_tool.triggered.connect(lambda: self.set_tool("ellipse"))
        
        toolbar.addAction(self.select_tool)
        toolbar.addAction(self.pen_tool)
        toolbar.addAction(self.bezier_tool)
        toolbar.addAction(self.rect_tool)
        toolbar.addAction(self.ellipse_tool)
        
        # Canvas
        self.canvas = QtWidgets.QGraphicsView()
        self.scene = QtWidgets.QGraphicsScene()
        self.canvas.setScene(self.scene)
        layout.addWidget(self.canvas)
        
        # Button box
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def set_tool(self, tool):
        self.current_tool = tool
        self.select_tool.setChecked(tool == "select")
        self.pen_tool.setChecked(tool == "pen")
        self.bezier_tool.setChecked(tool == "bezier")
        self.rect_tool.setChecked(tool == "rectangle")
        self.ellipse_tool.setChecked(tool == "ellipse")
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pos = self.canvas.mapToScene(event.pos())
            
            if self.current_tool == "pen":
                self.points.append(Vector2(pos.x(), pos.y()))
                self.draw_preview()
            elif self.current_tool == "bezier":
                if len(self.control_points) < 4:  # Start point, control1, control2, end point
                    self.control_points.append(Vector2(pos.x(), pos.y()))
                    self.draw_preview()
            elif self.current_tool == "rectangle":
                if not self.points:
                    self.points.append(Vector2(pos.x(), pos.y()))
                else:
                    self.points.append(Vector2(pos.x(), pos.y()))
                    self.draw_preview()
            elif self.current_tool == "ellipse":
                if not self.points:
                    self.points.append(Vector2(pos.x(), pos.y()))
                else:
                    self.points.append(Vector2(pos.x(), pos.y()))
                    self.draw_preview()
                    
        super().mousePressEvent(event)
        
    def draw_preview(self):
        self.scene.clear()
        
        if self.current_tool == "pen" and len(self.points) > 1:
            path = QtGui.QPainterPath()
            path.moveTo(self.points[0].x, self.points[0].y)
            for point in self.points[1:]:
                path.lineTo(point.x, point.y)
            self.scene.addPath(path, QtGui.QPen(QtCore.Qt.red, 2))
            
        elif self.current_tool == "bezier":
            if len(self.control_points) == 4:
                path = QtGui.QPainterPath()
                path.moveTo(self.control_points[0].x, self.control_points[0].y)
                path.cubicTo(
                    self.control_points[1].x, self.control_points[1].y,
                    self.control_points[2].x, self.control_points[2].y,
                    self.control_points[3].x, self.control_points[3].y
                )
                self.scene.addPath(path, QtGui.QPen(QtCore.Qt.blue, 2))
                
            # Draw control points
            for i, point in enumerate(self.control_points):
                color = QtCore.Qt.red if i == 0 or i == 3 else QtCore.Qt.green
                self.scene.addEllipse(
                    point.x - 3, point.y - 3, 6, 6,
                    QtGui.QPen(color), QtGui.QBrush(color)
                )
                
        elif self.current_tool == "rectangle" and len(self.points) == 2:
            rect = QtCore.QRectF(
                self.points[0].x, self.points[0].y,
                self.points[1].x - self.points[0].x,
                self.points[1].y - self.points[0].y
            )
            self.scene.addRect(rect, QtGui.QPen(QtCore.Qt.green, 2))
            
        elif self.current_tool == "ellipse" and len(self.points) == 2:
            rect = QtCore.QRectF(
                self.points[0].x, self.points[0].y,
                self.points[1].x - self.points[0].x,
                self.points[1].y - self.points[0].y
            )
            self.scene.addEllipse(rect, QtGui.QPen(QtCore.Qt.magenta, 2))
            
    def get_svg_path(self):
        if self.current_tool == "pen" and len(self.points) > 1:
            path_data = f"M {self.points[0].x} {self.points[0].y}"
            for point in self.points[1:]:
                path_data += f" L {point.x} {point.y}"
            return path_data
            
        elif self.current_tool == "bezier" and len(self.control_points) == 4:
            return (
                f"M {self.control_points[0].x} {self.control_points[0].y} "
                f"C {self.control_points[1].x} {self.control_points[1].y} "
                f"{self.control_points[2].x} {self.control_points[2].y} "
                f"{self.control_points[3].x} {self.control_points[3].y}"
            )
            
        elif self.current_tool == "rectangle" and len(self.points) == 2:
            width = self.points[1].x - self.points[0].x
            height = self.points[1].y - self.points[0].y
            return f"M {self.points[0].x} {self.points[0].y} h {width} v {height} h {-width} Z"
            
        elif self.current_tool == "ellipse" and len(self.points) == 2:
            cx = (self.points[0].x + self.points[1].x) / 2
            cy = (self.points[0].y + self.points[1].y) / 2
            rx = abs(self.points[1].x - self.points[0].x) / 2
            ry = abs(self.points[1].y - self.points[0].y) / 2
            return f"M {cx} {cy - ry} a {rx} {ry} 0 1 0 0 {ry * 2} a {rx} {ry} 0 1 0 0 {-ry * 2} Z"
            
        return ""