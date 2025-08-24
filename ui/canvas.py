# ui/canvas.py - Fix panning to move items exactly with mouse
from PySide2 import QtWidgets, QtCore, QtGui
from core.model import ButtonType, Vector2
import math

class PickerCanvas(QtWidgets.QGraphicsView):
    # Tool types
    SELECT_TOOL = "select"
    RECTANGLE_TOOL = "rectangle"
    ROUND_RECT_TOOL = "round_rect"
    CIRCLE_TOOL = "circle"
    TRIANGLE_TOOL = "triangle"
    DIAMOND_TOOL = "diamond"
    HEXAGON_TOOL = "hexagon"
    SLIDER_TOOL = "slider"
    CHECKBOX_TOOL = "checkbox"
    RADIUS_TOOL = "radius"
    TEXT_TOOL = "text"
    
    selectionChanged = QtCore.Signal(str)
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.current_tool = self.SELECT_TOOL
        self.setup_canvas()
        
        self.scene.selectionChanged.connect(self.handle_selection_changed)
    
    def setup_canvas(self):
        # Create scene with reasonable bounds
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.setScene(self.scene)
        
        # Set up view properties
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        
        # Remove scrollbars for clean look
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # Background
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(50, 50, 50)))
        
        # Zoom factors
        self.zoom_factor = 1.15
        self.zoom_level = 0
        self.max_zoom_level = 50
        self.min_zoom_level = -50
        
        # Panning state
        self.panning = False
        self.pan_start = QtCore.QPoint()
        self.pan_origin = QtCore.QPointF()
    
    def set_current_tool(self, tool):
        """Set the current tool"""
        self.current_tool = tool
        
        if tool == self.SELECT_TOOL:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self.setCursor(QtCore.Qt.ArrowCursor)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.setCursor(QtCore.Qt.CrossCursor)
    
    def handle_selection_changed(self):
        """Handle selection changes in the scene"""
        selected_items = self.scene.selectedItems()
        if selected_items:
            # Get the first selected item
            button_id = selected_items[0].data(0)
            self.selectionChanged.emit(button_id)
        else:
            self.selectionChanged.emit(None)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.current_tool != self.SELECT_TOOL:
                # Create a new button if we're in a creation tool
                scene_pos = self.mapToScene(event.pos())
                self.create_button(scene_pos)
            else:
                # In select mode, handle normally
                super().mousePressEvent(event)
                
        elif event.button() == QtCore.Qt.MiddleButton:
            # Start Maya-style panning with middle mouse
            self.panning = True
            self.pan_start = event.pos()
            self.pan_origin = self.mapToScene(self.pan_start)
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.panning:
            # Get current mouse position in scene coordinates
            current_pos = event.pos()
            current_scene_pos = self.mapToScene(current_pos)
            
            # Calculate the delta movement in scene coordinates
            delta = current_scene_pos - self.pan_origin
            
            if delta.manhattanLength() > 0:
                # Move the view to follow the mouse exactly
                self.centerOn(self.mapToScene(self.viewport().rect().center()) - delta)
                
                # Update the origin for next movement
                self.pan_origin = self.mapToScene(current_pos)
            
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self.panning and event.button() == QtCore.Qt.MiddleButton:
            # Stop panning
            self.panning = False
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel (Maya style)
        zoom_in = event.angleDelta().y() > 0
        self.zoom(zoom_in)
        event.accept()
    
    def zoom(self, zoom_in):
        """Zoom in or out with center preservation"""
        # Store the current center before zooming
        old_center = self.mapToScene(self.viewport().rect().center())
        
        factor = self.zoom_factor if zoom_in else 1 / self.zoom_factor
        
        # Check zoom limits
        if zoom_in and self.zoom_level < self.max_zoom_level:
            self.scale(factor, factor)
            self.zoom_level += 1
        elif not zoom_in and self.zoom_level > self.min_zoom_level:
            self.scale(factor, factor)
            self.zoom_level -= 1
        else:
            return
            
        # Get the new center after zooming
        new_center = self.mapToScene(self.viewport().rect().center())
        
        # Calculate the displacement caused by zooming
        displacement = new_center - old_center
        
        # Adjust the view to compensate for the displacement
        self.centerOn(old_center)
    
    def create_button(self, position):
        """Create a button at the specified position"""
        if not self.controller or not self.controller.model.current_picker:
            print("No picker selected. Please create a new picker first.")
            return
        
        shape_mapping = {
            self.RECTANGLE_TOOL: (ShapeType.RECTANGLE, "select"),
            self.ROUND_RECT_TOOL: (ShapeType.ROUND_RECTANGLE, "select"),
            self.CIRCLE_TOOL: (ShapeType.CIRCLE, "select"),
            self.TRIANGLE_TOOL: (ShapeType.TRIANGLE, "select"),
            self.DIAMOND_TOOL: (ShapeType.DIAMOND, "select"),
            self.HEXAGON_TOOL: (ShapeType.HEXAGON, "select"),
            self.SLIDER_TOOL: (ShapeType.RECTANGLE, "slider"),
            self.CHECKBOX_TOOL: (ShapeType.RECTANGLE, "checkbox"),
            self.RADIUS_TOOL: (ShapeType.CIRCLE, "radius"),
            self.TEXT_TOOL: (ShapeType.RECTANGLE, "text")
        }
        
        if self.current_tool in shape_mapping:
            shape_type, button_type = shape_mapping[self.current_tool]
            
            button = self.controller.add_button(
                button_type,
                position=Vector2(position.x(), position.y()),
                size=Vector2(80, 40),
                label=f"{self.current_tool.capitalize()}",
                shape=shape_type
            )
        
        if button:
            self.update_from_model()
            self.set_current_tool(self.SELECT_TOOL)
    
    def update_from_model(self):
        """Update the canvas based on the current model state"""
        self.scene.clear()
        
        if not self.controller.model.current_picker:
            return
            
        picker = self.controller.model.current_picker
        
        # Draw all buttons
        for button in picker.buttons:
            self.draw_button(button)
    
    def draw_button(self, button):
        """Draw a button based on its shape type"""
        if button.shape == ShapeType.RECTANGLE:
            self.draw_rectangle_button(button)
        elif button.shape == ShapeType.ROUND_RECTANGLE:
            self.draw_round_rectangle_button(button)
        elif button.shape == ShapeType.CIRCLE:
            self.draw_circle_button(button)
        elif button.shape == ShapeType.TRIANGLE:
            self.draw_triangle_button(button)
        elif button.shape == ShapeType.DIAMOND:
            self.draw_diamond_button(button)
        elif button.shape == ShapeType.HEXAGON:
            self.draw_hexagon_button(button)
        elif button.shape == ShapeType.POLYGON:
            self.draw_polygon_button(button)
    
    def draw_select_button(self, button):
        rect = QtCore.QRectF(
            button.position.x, 
            button.position.y, 
            button.size.x, 
            button.size.y
        )
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsRectItem(rect)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.black))
        
        # Make the item selectable and movable
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Add text label
        if button.label:
            text = QtWidgets.QGraphicsTextItem(button.label, item)
            text.setPos(button.position.x + 5, button.position.y + 5)
            text.setDefaultTextColor(QtGui.QColor(255, 255, 255))
            
        # Store button ID for interaction
        item.setData(0, button.id)
        
        self.scene.addItem(item)

    def draw_rectangle_button(self, button):
        """Draw a rectangular button"""
        rect = QtCore.QRectF(
            button.position.x, 
            button.position.y, 
            button.size.x, 
            button.size.y
        )
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsRectItem(rect)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.black))
        
        self._setup_button_item(item, button)
        self._add_button_label(item, button)
    
    def draw_round_rectangle_button(self, button):
        """Draw a round rectangle button"""
        rect = QtCore.QRectF(
            button.position.x, 
            button.position.y, 
            button.size.x, 
            button.size.y
        )
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsRectItem(rect)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.black))
        
        # Make it round
        item.setPen(QtGui.QPen(QtCore.Qt.black))
        
        self._setup_button_item(item, button)
        self._add_button_label(item, button)

    def draw_circle_button(self, button):
        """Draw a circular button"""
        radius = min(button.size.x, button.size.y) / 2
        center_x = button.position.x + button.size.x / 2
        center_y = button.position.y + button.size.y / 2
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsEllipseItem(
            center_x - radius,
            center_y - radius,
            radius * 2,
            radius * 2
        )
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.black))
        
        self._setup_button_item(item, button)
        self._add_button_label(item, button)
    
    def draw_triangle_button(self, button):
        """Draw a triangular button"""
        path = QtGui.QPainterPath()
        path.moveTo(button.position.x + button.size.x / 2, button.position.y)
        path.lineTo(button.position.x + button.size.x, button.position.y + button.size.y)
        path.lineTo(button.position.x, button.position.y + button.size.y)
        path.closeSubpath()
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsPathItem(path)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.black))
        
        self._setup_button_item(item, button)
        self._add_button_label(item, button)
    
    def draw_diamond_button(self, button):
        """Draw a diamond-shaped button"""
        path = QtGui.QPainterPath()
        path.moveTo(button.position.x + button.size.x / 2, button.position.y)
        path.lineTo(button.position.x + button.size.x, button.position.y + button.size.y / 2)
        path.lineTo(button.position.x + button.size.x / 2, button.position.y + button.size.y)
        path.lineTo(button.position.x, button.position.y + button.size.y / 2)
        path.closeSubpath()
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsPathItem(path)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.black))
        
        self._setup_button_item(item, button)
        self._add_button_label(item, button)
    
    def draw_hexagon_button(self, button):
        """Draw a hexagonal button"""
        path = QtGui.QPainterPath()
        center_x = button.position.x + button.size.x / 2
        center_y = button.position.y + button.size.y / 2
        radius = min(button.size.x, button.size.y) / 2
        
        for i in range(6):
            angle = 2 * math.pi * i / 6
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsPathItem(path)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.black))
        
        self._setup_button_item(item, button)
        self._add_button_label(item, button)
    
    def draw_text_button(self, button):
        """Draw text button"""
        item = QtWidgets.QGraphicsTextItem(button.label)
        
        # Set font properties
        font = QtGui.QFont()
        font.setPointSize(button.font_size)
        font.setBold(button.is_bold)
        font.setItalic(button.is_italic)
        item.setFont(font)
        
        # Set text color
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        item.setDefaultTextColor(color)
        
        item.setPos(button.position.x, button.position.y)
        
        # Make text item selectable and movable
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Store button ID for interaction
        item.setData(0, button.id)
        
        self.scene.addItem(item)

    # Update all other drawing methods similarly
    def draw_script_button(self, button):
        # Similar to select button but with different visual style
        rect = QtCore.QRectF(
            button.position.x, 
            button.position.y, 
            button.size.x, 
            button.size.y
        )
    
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
    
        item = QtWidgets.QGraphicsRectItem(rect)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.blue, 2))
    
        # Make the item selectable
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
    
        # Add script icon or indicator
        if button.label:
            text = QtWidgets.QGraphicsTextItem(button.label, item)
            text.setPos(button.position.x + 5, button.position.y + 5)
        
        # Store button ID for interaction
        item.setData(0, button.id)
    
        self.scene.addItem(item)

    # Update other drawing methods similarly...
    
    def draw_pose_button(self, button):
        # Draw with a special style, maybe a star icon
        rect = QtCore.QRectF(
            button.position.x, 
            button.position.y, 
            button.size.x, 
            button.size.y
        )
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsRectItem(rect)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.yellow, 2))
        
        # Add pose icon (star)
        path = QtGui.QPainterPath()
        path.moveTo(button.position.x + button.size.x / 2, button.position.y + 5)
        for i in range(5):
            angle = 2 * 3.14159 * i / 5 - 3.14159 / 2
            x = button.position.x + button.size.x / 2 + 0.4 * button.size.x * math.cos(angle)
            y = button.position.y + button.size.y / 2 + 0.4 * button.size.y * math.sin(angle)
            path.lineTo(x, y)
        path.closeSubpath()
        
        star_item = QtWidgets.QGraphicsPathItem(path, item)
        star_item.setBrush(QtGui.QBrush(QtCore.Qt.white))
        star_item.setPen(QtGui.QPen(QtCore.Qt.black))
        
        if button.label:
            text = QtWidgets.QGraphicsTextItem(button.label, item)
            text.setPos(button.position.x + 5, button.position.y + 5)
        
        # Make the item selectable
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)

        item.setData(0, button.id)

        self.scene.addItem(item)

    def draw_attribute_button(self, button):
        # Draw with a special style, maybe a gear icon
        rect = QtCore.QRectF(
            button.position.x, 
            button.position.y, 
            button.size.x, 
            button.size.y
        )
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsRectItem(rect)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.cyan, 2))
        
        # Add gear icon
        if button.operation == "toggle":
            # Draw toggle icon
            pass
        elif button.operation == "nudge":
            # Draw nudge icon
            pass
        else:
            # Draw set icon
            pass
            
        if button.label:
            text = QtWidgets.QGraphicsTextItem(button.label, item)
            text.setPos(button.position.x + 5, button.position.y + 5)
            
        item.setData(0, button.id)
        self.scene.addItem(item)

    def draw_slider(self, button):
        # Draw a slider UI
        rect = QtCore.QRectF(
            button.position.x, 
            button.position.y, 
            button.size.x, 
            button.size.y
        )
        
        color = QtGui.QColor(
            int(button.color.r * 255),
            int(button.color.g * 255),
            int(button.color.b * 255),
            int(button.color.a * 255)
        )
        
        item = QtWidgets.QGraphicsRectItem(rect)
        item.setBrush(QtGui.QBrush(color))
        item.setPen(QtGui.QPen(QtCore.Qt.darkGreen, 2))
        
        # Draw slider track
        track_rect = QtCore.QRectF(
            button.position.x + 5,
            button.position.y + button.size.y / 2 - 2,
            button.size.x - 10,
            4
        )
        track_item = QtWidgets.QGraphicsRectItem(track_rect, item)
        track_item.setBrush(QtGui.QBrush(QtCore.Qt.gray))
        track_item.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        
        # Draw slider thumb
        if button.is_2d:
            # Draw 2D slider thumb
            thumb_x = button.position.x + 5 + (button.current_value - button.range_min) / (button.range_max - button.range_min) * (button.size.x - 10)
            thumb_y = button.position.y + 5 + (button.second_current_value - button.second_range_min) / (button.second_range_max - button.second_range_min) * (button.size.y - 10)
            
            thumb_rect = QtCore.QRectF(
                thumb_x - 5,
                thumb_y - 5,
                10,
                10
            )
            thumb_item = QtWidgets.QGraphicsEllipseItem(thumb_rect, item)
            thumb_item.setBrush(QtGui.QBrush(QtCore.Qt.red))
            thumb_item.setPen(QtGui.QPen(QtCore.Qt.black))
        else:
            # Draw 1D slider thumb
            thumb_pos = button.position.x + 5 + (button.current_value - button.range_min) / (button.range_max - button.range_min) * (button.size.x - 10)
            
            thumb_rect = QtCore.QRectF(
                thumb_pos - 5,
                button.position.y + 5,
                10,
                button.size.y - 10
            )
            thumb_item = QtWidgets.QGraphicsRectItem(thumb_rect, item)
            thumb_item.setBrush(QtGui.QBrush(QtCore.Qt.red))
            thumb_item.setPen(QtGui.QPen(QtCore.Qt.black))
            
        if button.label:
            text = QtWidgets.QGraphicsTextItem(button.label, item)
            text.setPos(button.position.x + 5, button.position.y + 5)
            
        item.setData(0, button.id)
        self.scene.addItem(item)

    def _setup_button_item(self, item, button):
        """Common setup for all button items"""
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        item.setData(0, button.id)
        self.scene.addItem(item)
    
    def _add_button_label(self, item, button):
        """Add label to button"""
        if button.label:
            text = QtWidgets.QGraphicsTextItem(button.label, item)
            text.setDefaultTextColor(QtGui.QColor(255, 255, 255))
            
            # Center the text
            text_rect = text.boundingRect()
            text.setPos(
                button.position.x + (button.size.x - text_rect.width()) / 2,
                button.position.y + (button.size.y - text_rect.height()) / 2
            )
    
    def zoom_in(self):
        """Zoom in programmatically"""
        self.zoom(True)
    
    def zoom_out(self):
        """Zoom out programmatically"""
        self.zoom(False)
    
    def reset_zoom(self):
        """Reset zoom to default"""
        self.resetTransform()
        self.zoom_level = 0
    
    def start_rectangle(self, pos):
        """Start drawing a rectangle"""
        scene_pos = self.mapToScene(pos)
        # Implementation for rectangle tool
        pass
    
    def start_circle(self, pos):
        """Start drawing a circle"""
        scene_pos = self.mapToScene(pos)
        # Implementation for circle tool
        pass
    
    def start_text(self, pos):
        """Start adding text"""
        scene_pos = self.mapToScene(pos)
        # Implementation for text tool
        pass
    
    def start_move(self, pos):
        """Start moving selected items"""
        scene_pos = self.mapToScene(pos)
        # Implementation for move tool
        pass
    
    def align_selected_left(self):
        """Align selected items to the left"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return
            
        min_x = min(item.x() for item in selected_items)
        for item in selected_items:
            item.setX(min_x)
    
    def align_selected_right(self):
        """Align selected items to the right"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return
            
        max_x = max(item.x() + item.boundingRect().width() for item in selected_items)
        for item in selected_items:
            item.setX(max_x - item.boundingRect().width())
    
    def align_selected_top(self):
        """Align selected items to the top"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return
            
        min_y = min(item.y() for item in selected_items)
        for item in selected_items:
            item.setY(min_y)
    
    def align_selected_bottom(self):
        """Align selected items to the bottom"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return
            
        max_y = max(item.y() + item.boundingRect().height() for item in selected_items)
        for item in selected_items:
            item.setY(max_y - item.boundingRect().height())