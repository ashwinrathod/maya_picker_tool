# utils/documentation.py
import os
import json
from pathlib import Path

class Documentation:
    def __init__(self):
        self.docs_path = os.path.join(os.path.dirname(__file__), "..", "docs")
        self.examples_path = os.path.join(os.path.dirname(__file__), "..", "examples")
        
        # Create directories if they don't exist
        os.makedirs(self.docs_path, exist_ok=True)
        os.makedirs(self.examples_path, exist_ok=True)
        
    def get_doc(self, topic):
        """Get documentation for a specific topic"""
        doc_path = os.path.join(self.docs_path, f"{topic}.md")
        if os.path.exists(doc_path):
            with open(doc_path, 'r') as f:
                return f.read()
        return f"Documentation for {topic} not found."
        
    def get_example(self, name):
        """Get an example picker by name"""
        example_path = os.path.join(self.examples_path, f"{name}.picker")
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                return json.load(f)
        return None
        
    def list_examples(self):
        """List all available examples"""
        examples = []
        for file in os.listdir(self.examples_path):
            if file.endswith(".picker"):
                examples.append(file[:-7])  # Remove .picker extension
        return examples
        
    def create_example(self, name, picker_data):
        """Create a new example picker"""
        example_path = os.path.join(self.examples_path, f"{name}.picker")
        with open(example_path, 'w') as f:
            json.dump(picker_data, f, indent=4)
            
    def create_doc(self, topic, content):
        """Create documentation for a topic"""
        doc_path = os.path.join(self.docs_path, f"{topic}.md")
        with open(doc_path, 'w') as f:
            f.write(content)

# Create some basic documentation
def create_basic_documentation():
    docs = Documentation()
    
    # Create getting started guide
    getting_started = """
# Getting Started with Maya Picker Tool

## Installation
1. Copy the picker tool folder to your Maya scripts directory
2. In Maya, run: `import picker_tool.main; picker_tool.main.show_picker_tool()`

## Creating Your First Picker
1. Click "File > New Picker" to create a new picker
2. Use the tools on the left to add buttons
3. Configure button properties in the right panel
4. Save your picker with "File > Save"

## Button Types
- **Select Buttons**: Select Maya objects when clicked
- **Script Buttons**: Execute Python or MEL scripts
- **Pose Buttons**: Store and apply character poses
- **Attribute Buttons**: Modify object attributes
- **Slider Buttons**: Create interactive sliders
- **Text Buttons**: Add labels and annotations

## Advanced Features
- Use the shape editor to create custom button shapes
- Enable snapping for precise alignment
- Use mirroring to create symmetrical layouts
- Add debug overlays to visualize connections
    """
    
    docs.create_doc("getting_started", getting_started)
    
    # Create API documentation
    api_docs = """
# API Documentation

## PickerController
The main controller class that manages picker data and operations.

### Methods
- `create_new_picker(name)`: Create a new picker
- `add_button(button_type, **kwargs)`: Add a button to the current picker
- `execute_button(button_id)`: Execute a button's action
- `save_picker(file_path)`: Save the current picker to a file
- `load_picker(file_path)`: Load a picker from a file

## Custom Button Development
To create custom button types, subclass `BaseButton` and implement:
- `__init__()`: Initialize button properties
- `execute()`: Define the button's action
- `draw()`: Define how the button is rendered

Example:
```python
class CustomButton(BaseButton):
    def __init__(self, id, position, size, custom_property):
        super().__init__(id, ButtonType.CUSTOM, position, size)
        self.custom_property = custom_property
        
    def execute(self):
        # Custom execution logic
        print(f"Custom button {self.id} executed!")
        
    def draw(self, painter):
        # Custom drawing logic
        painter.drawText(self.position.x, self.position.y, self.label)