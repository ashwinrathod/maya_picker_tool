# core/organization.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class OrganizationLevel(Enum):
    PANEL = "panel"
    TAB = "tab"
    SECTION = "section"
    GROUP = "group"

@dataclass
class OrganizationalUnit:
    id: str
    name: str
    level: OrganizationLevel
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)  # IDs of child units
    button_ids: List[str] = field(default_factory=list)  # IDs of buttons in this unit
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties
    
    def add_child(self, child_id: str):
        if child_id not in self.children:
            self.children.append(child_id)
            
    def add_button(self, button_id: str):
        if button_id not in self.button_ids:
            self.button_ids.append(button_id)
            
    def remove_button(self, button_id: str):
        if button_id in self.button_ids:
            self.button_ids.remove(button_id)

class PickerOrganizer:
    def __init__(self):
        self.units: Dict[str, OrganizationalUnit] = {}
        self.root_units: List[str] = []  # IDs of units with no parent
        
    def create_unit(self, name: str, level: OrganizationLevel, parent_id: Optional[str] = None) -> str:
        """Create a new organizational unit"""
        unit_id = f"{level.value}_{len(self.units) + 1}"
        
        unit = OrganizationalUnit(
            id=unit_id,
            name=name,
            level=level,
            parent_id=parent_id
        )
        
        self.units[unit_id] = unit
        
        if parent_id:
            self.units[parent_id].add_child(unit_id)
        else:
            self.root_units.append(unit_id)
            
        return unit_id
        
    def delete_unit(self, unit_id: str):
        """Delete an organizational unit and all its children"""
        if unit_id not in self.units:
            return
            
        # Recursively delete children
        for child_id in self.units[unit_id].children:
            self.delete_unit(child_id)
            
        # Remove from parent's children list
        if self.units[unit_id].parent_id:
            parent = self.units[self.units[unit_id].parent_id]
            if unit_id in parent.children:
                parent.children.remove(unit_id)
        else:
            if unit_id in self.root_units:
                self.root_units.remove(unit_id)
                
        # Remove the unit
        del self.units[unit_id]
        
    def move_unit(self, unit_id: str, new_parent_id: Optional[str]):
        """Move a unit to a new parent"""
        if unit_id not in self.units:
            return
            
        unit = self.units[unit_id]
        old_parent_id = unit.parent_id
        
        # Remove from old parent
        if old_parent_id:
            old_parent = self.units[old_parent_id]
            if unit_id in old_parent.children:
                old_parent.children.remove(unit_id)
        else:
            if unit_id in self.root_units:
                self.root_units.remove(unit_id)
                
        # Add to new parent
        unit.parent_id = new_parent_id
        if new_parent_id:
            self.units[new_parent_id].add_child(unit_id)
        else:
            self.root_units.append(unit_id)
            
    def get_unit_path(self, unit_id: str) -> List[str]:
        """Get the path to a unit as a list of unit IDs"""
        path = []
        current_id = unit_id
        
        while current_id:
            if current_id not in self.units:
                break
                
            path.insert(0, current_id)
            current_id = self.units[current_id].parent_id
            
        return path
        
    def get_buttons_in_unit(self, unit_id: str, recursive: bool = True) -> List[str]:
        """Get all button IDs in a unit, optionally recursively"""
        if unit_id not in self.units:
            return []
            
        buttons = list(self.units[unit_id].button_ids)
        
        if recursive:
            for child_id in self.units[unit_id].children:
                buttons.extend(self.get_buttons_in_unit(child_id, True))
                
        return buttons
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert organizer to serializable dict"""
        return {
            "units": {unit_id: {
                "id": unit.id,
                "name": unit.name,
                "level": unit.level.value,
                "parent_id": unit.parent_id,
                "children": unit.children,
                "button_ids": unit.button_ids,
                "properties": unit.properties
            } for unit_id, unit in self.units.items()},
            "root_units": self.root_units
        }
        
    def from_dict(self, data: Dict[str, Any]):
        """Load organizer from dict"""
        self.units.clear()
        self.root_units.clear()
        
        for unit_id, unit_data in data.get("units", {}).items():
            unit = OrganizationalUnit(
                id=unit_data["id"],
                name=unit_data["name"],
                level=OrganizationLevel(unit_data["level"]),
                parent_id=unit_data["parent_id"],
                children=unit_data["children"],
                button_ids=unit_data["button_ids"],
                properties=unit_data["properties"]
            )
            self.units[unit_id] = unit
            
        self.root_units = data.get("root_units", [])