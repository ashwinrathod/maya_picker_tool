# core/model.py - Add all button types and shapes
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class ButtonType(Enum):
    SELECT = "select"
    SCRIPT = "script"
    POSE = "pose"
    ATTRIBUTE = "attribute"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    RADIUS = "radius"
    TEXT = "text"

class ShapeType(Enum):
    RECTANGLE = "rectangle"
    ROUND_RECTANGLE = "round_rectangle"
    CIRCLE = "circle"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"
    HEXAGON = "hexagon"
    POLYGON = "polygon"

@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0

@dataclass
class Color:
    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0

@dataclass
class BaseButton:
    id: str
    type: ButtonType
    position: Vector2 = field(default_factory=Vector2)
    size: Vector2 = field(default_factory=lambda: Vector2(50, 50))
    color: Color = field(default_factory=lambda: Color(0.5, 0.5, 0.5))
    label: str = ""
    tooltip: str = ""
    visible: bool = True
    locked: bool = False
    shape: ShapeType = ShapeType.RECTANGLE
    corner_radius: float = 10.0  # For round rectangles
    sides: int = 6  # For polygons
    points: List[Vector2] = field(default_factory=list)  # For custom polygons

class SelectButton(BaseButton):
    def __init__(self, **kwargs):
        # Extract subclass-specific arguments
        self.target_nodes = kwargs.pop('target_nodes', [])
        self.hierarchical = kwargs.pop('hierarchical', False)
        self.mirror = kwargs.pop('mirror', False)
        self.mirror_axis = kwargs.pop('mirror_axis', "X")
        
        # Set the type and call parent constructor with remaining kwargs
        kwargs['type'] = ButtonType.SELECT
        super().__init__(**kwargs)

class ScriptButton(BaseButton):
    def __init__(self, **kwargs):
        # Extract subclass-specific arguments
        self.script = kwargs.pop('script', '')
        self.language = kwargs.pop('language', 'python')
        
        # Set the type and call parent constructor with remaining kwargs
        kwargs['type'] = ButtonType.SCRIPT
        super().__init__(**kwargs)

class PoseButton(BaseButton):
    def __init__(self, **kwargs):
        # Extract subclass-specific arguments
        self.target_nodes = kwargs.pop('target_nodes', [])
        self.pose_data = kwargs.pop('pose_data', {})
        
        # Set the type and call parent constructor with remaining kwargs
        kwargs['type'] = ButtonType.POSE
        super().__init__(**kwargs)

class AttributeButton(BaseButton):
    def __init__(self, **kwargs):
        # Extract subclass-specific arguments
        self.target_node = kwargs.pop('target_node', '')
        self.attribute = kwargs.pop('attribute', '')
        self.operation = kwargs.pop('operation', 'set')
        self.value = kwargs.pop('value', 0.0)
        self.nudge_amount = kwargs.pop('nudge_amount', 1.0)
        
        # Set the type and call parent constructor with remaining kwargs
        kwargs['type'] = ButtonType.ATTRIBUTE
        super().__init__(**kwargs)

class Slider(BaseButton):
    def __init__(self, **kwargs):
        # Extract subclass-specific arguments
        self.target_node = kwargs.pop('target_node', '')
        self.attribute = kwargs.pop('attribute', '')
        self.range_min = kwargs.pop('range_min', 0.0)
        self.range_max = kwargs.pop('range_max', 100.0)
        self.current_value = kwargs.pop('current_value', 0.0)
        self.is_2d = kwargs.pop('is_2d', False)
        self.second_attribute = kwargs.pop('second_attribute', '')
        self.second_range_min = kwargs.pop('second_range_min', 0.0)
        self.second_range_max = kwargs.pop('second_range_max', 100.0)
        self.second_current_value = kwargs.pop('second_current_value', 0.0)
        self.orientation = kwargs.pop('orientation', 'horizontal')  # horizontal or vertical
        
        # Set the type and call parent constructor with remaining kwargs
        kwargs['type'] = ButtonType.SLIDER
        super().__init__(**kwargs)

class Checkbox(BaseButton):
    def __init__(self, **kwargs):
        # Extract subclass-specific arguments
        self.target_node = kwargs.pop('target_node', '')
        self.attribute = kwargs.pop('attribute', '')
        self.checked_value = kwargs.pop('checked_value', 1.0)
        self.unchecked_value = kwargs.pop('unchecked_value', 0.0)
        self.is_checked = kwargs.pop('is_checked', False)
        
        # Set the type and call parent constructor with remaining kwargs
        kwargs['type'] = ButtonType.CHECKBOX
        super().__init__(**kwargs)

class RadiusButton(BaseButton):
    def __init__(self, **kwargs):
        # Extract subclass-specific arguments
        self.target_node = kwargs.pop('target_node', '')
        self.attribute = kwargs.pop('attribute', '')
        self.min_value = kwargs.pop('min_value', 0.0)
        self.max_value = kwargs.pop('max_value', 10.0)
        self.current_value = kwargs.pop('current_value', 1.0)
        
        # Set the type and call parent constructor with remaining kwargs
        kwargs['type'] = ButtonType.RADIUS
        super().__init__(**kwargs)

class TextButton(BaseButton):
    def __init__(self, **kwargs):
        # Extract subclass-specific arguments
        self.font_size = kwargs.pop('font_size', 12)
        self.is_bold = kwargs.pop('is_bold', False)
        self.is_italic = kwargs.pop('is_italic', False)
        self.text_alignment = kwargs.pop('text_alignment', 'center')  # left, center, right
        
        # Set the type and call parent constructor with remaining kwargs
        kwargs['type'] = ButtonType.TEXT
        super().__init__(**kwargs)

@dataclass
class Picker:
    name: str = "New Picker"
    buttons: List[BaseButton] = field(default_factory=list)
    background_image: Optional[str] = None
    canvas_size: Vector2 = field(default_factory=lambda: Vector2(800, 600))
    view_center: Vector2 = field(default_factory=Vector2)
    view_zoom: float = 1.0

class PickerModel:
    def __init__(self):
        self.pickers: Dict[str, Picker] = {}
        self.current_picker: Optional[Picker] = None
        
    def add_picker(self, name: str) -> Picker:
        picker = Picker(name=name)
        self.pickers[name] = picker
        return picker
        
    def remove_picker(self, name: str):
        if name in self.pickers:
            del self.pickers[name]
            
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pickers": {
                name: self._picker_to_dict(picker) 
                for name, picker in self.pickers.items()
            }
        }
    
    def _picker_to_dict(self, picker: Picker) -> Dict[str, Any]:
        return {
            "name": picker.name,
            "buttons": [self._button_to_dict(button) for button in picker.buttons],
            "background_image": picker.background_image,
            "canvas_size": {"x": picker.canvas_size.x, "y": picker.canvas_size.y},
            "view_center": {"x": picker.view_center.x, "y": picker.view_center.y},
            "view_zoom": picker.view_zoom
        }
    
    def _button_to_dict(self, button: BaseButton) -> Dict[str, Any]:
        base_data = {
            "id": button.id,
            "type": button.type.value,
            "position": {"x": button.position.x, "y": button.position.y},
            "size": {"x": button.size.x, "y": button.size.y},
            "color": {"r": button.color.r, "g": button.color.g, "b": button.color.b, "a": button.color.a},
            "label": button.label,
            "tooltip": button.tooltip,
            "visible": button.visible,
            "locked": button.locked
        }
        
        if isinstance(button, SelectButton):
            base_data.update({
                "target_nodes": button.target_nodes,
                "hierarchical": button.hierarchical,
                "mirror": button.mirror,
                "mirror_axis": button.mirror_axis
            })
        elif isinstance(button, ScriptButton):
            base_data.update({
                "script": button.script,
                "language": button.language
            })
        elif isinstance(button, PoseButton):
            base_data.update({
                "target_nodes": button.target_nodes,
                "pose_data": button.pose_data
            })
        elif isinstance(button, AttributeButton):
            base_data.update({
                "target_node": button.target_node,
                "attribute": button.attribute,
                "operation": button.operation,
                "value": button.value,
                "nudge_amount": button.nudge_amount
            })
        elif isinstance(button, Slider):
            base_data.update({
                "target_node": button.target_node,
                "attribute": button.attribute,
                "range_min": button.range_min,
                "range_max": button.range_max,
                "current_value": button.current_value,
                "is_2d": button.is_2d,
                "second_attribute": button.second_attribute,
                "second_range_min": button.second_range_min,
                "second_range_max": button.second_range_max,
                "second_current_value": button.second_current_value
            })
        elif isinstance(button, TextButton):
            base_data.update({
                "font_size": button.font_size,
                "is_bold": button.is_bold,
                "is_italic": button.is_italic
            })
            
        return base_data
    
    # core/model.py - Update save_to_file and load_from_file methods
    def save_to_file(self, file_path: str):
        """Save all pickers to a file"""
        try:
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
        
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            print(f"Picker saved successfully to: {file_path}")
            return True
        except Exception as e:
            print(f"Error saving picker: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def load_from_file(self, file_path: str):
        """Load pickers from a file"""
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.pickers.clear()
        
            for name, picker_data in data.get("pickers", {}).items():
                picker = Picker(name=picker_data.get("name", name))
                picker.background_image = picker_data.get("background_image")
            
                # Load canvas properties
                canvas_size = picker_data.get("canvas_size", {"x": 800, "y": 600})
                picker.canvas_size = Vector2(canvas_size["x"], canvas_size["y"])
            
                view_center = picker_data.get("view_center", {"x": 0, "y": 0})
                picker.view_center = Vector2(view_center["x"], view_center["y"])
            
                picker.view_zoom = picker_data.get("view_zoom", 1.0)
            
                # Load buttons
                for button_data in picker_data.get("buttons", []):
                    self._create_button_from_data(button_data, picker)
            
                self.pickers[name] = picker
        
            # Set the first picker as current if available
            if self.pickers:
                first_picker_name = list(self.pickers.keys())[0]
                self.current_picker = self.pickers[first_picker_name]
        
            print(f"Picker loaded successfully from: {file_path}")
            return True
        except Exception as e:
            print(f"Error loading picker: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _create_button_from_data(self, button_data, picker):
        """Create a button from serialized data"""
        button_type = ButtonType(button_data.get("type", "select"))
    
        position_data = button_data.get("position", {"x": 0, "y": 0})
        position = Vector2(position_data["x"], position_data["y"])
    
        size_data = button_data.get("size", {"x": 50, "y": 50})
        size = Vector2(size_data["x"], size_data["y"])
    
        color_data = button_data.get("color", {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0})
        color = Color(color_data["r"], color_data["g"], color_data["b"], color_data["a"])
    
        if button_type == ButtonType.SELECT:
            button = SelectButton(
                id=button_data.get("id", ""),
                position=position,
                size=size,
                color=color,
                label=button_data.get("label", ""),
                tooltip=button_data.get("tooltip", ""),
                target_nodes=button_data.get("target_nodes", []),
                hierarchical=button_data.get("hierarchical", False),
                mirror=button_data.get("mirror", False),
                mirror_axis=button_data.get("mirror_axis", "X")
            )
        elif button_type == ButtonType.SCRIPT:
            button = ScriptButton(
                id=button_data.get("id", ""),
                position=position,
                size=size,
                color=color,
                label=button_data.get("label", ""),
                tooltip=button_data.get("tooltip", ""),
                script=button_data.get("script", ""),
                language=button_data.get("language", "python")
            )
        elif button_type == ButtonType.TEXT:
            button = TextButton(
                id=button_data.get("id", ""),
                position=position,
                size=size,
                color=color,
                label=button_data.get("label", ""),
                tooltip=button_data.get("tooltip", ""),
                font_size=button_data.get("font_size", 12),
                is_bold=button_data.get("is_bold", False),
                is_italic=button_data.get("is_italic", False)
            )
        else:
            return
        
        picker.buttons.append(button)