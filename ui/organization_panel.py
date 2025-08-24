# ui/organization_panel.py
from PySide2 import QtWidgets, QtCore, QtGui
from core.organization import OrganizationLevel

class OrganizationPanel(QtWidgets.QDockWidget):
    def __init__(self, controller, parent=None):
        super().__init__("Organization", parent)
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Tree view for organizational hierarchy
        self.tree_view = QtWidgets.QTreeWidget()
        self.tree_view.setHeaderLabel("Picker Organization")
        self.tree_view.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.tree_view)
        
        # Add unit buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.add_panel_btn = QtWidgets.QPushButton("Add Panel")
        self.add_panel_btn.clicked.connect(lambda: self.add_unit(OrganizationLevel.PANEL))
        button_layout.addWidget(self.add_panel_btn)
        
        self.add_tab_btn = QtWidgets.QPushButton("Add Tab")
        self.add_tab_btn.clicked.connect(lambda: self.add_unit(OrganizationLevel.TAB))
        button_layout.addWidget(self.add_tab_btn)
        
        self.add_section_btn = QtWidgets.QPushButton("Add Section")
        self.add_section_btn.clicked.connect(lambda: self.add_unit(OrganizationLevel.SECTION))
        button_layout.addWidget(self.add_section_btn)
        
        self.add_group_btn = QtWidgets.QPushButton("Add Group")
        self.add_group_btn.clicked.connect(lambda: self.add_unit(OrganizationLevel.GROUP))
        button_layout.addWidget(self.add_group_btn)
        
        layout.addLayout(button_layout)
        
        # Remove button
        self.remove_btn = QtWidgets.QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        layout.addWidget(self.remove_btn)
        
        # Properties panel
        self.properties_group = QtWidgets.QGroupBox("Properties")
        properties_layout = QtWidgets.QFormLayout(self.properties_group)
        
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.textChanged.connect(self.update_properties)
        properties_layout.addRow("Name:", self.name_edit)
        
        self.visible_check = QtWidgets.QCheckBox("Visible")
        self.visible_check.stateChanged.connect(self.update_properties)
        properties_layout.addRow("Visible:", self.visible_check)
        
        self.locked_check = QtWidgets.QCheckBox("Locked")
        self.locked_check.stateChanged.connect(self.update_properties)
        properties_layout.addRow("Locked:", self.locked_check)
        
        layout.addWidget(self.properties_group)
        
        self.setWidget(widget)
        self.refresh_tree()
        
    def refresh_tree(self):
        """Refresh the organization tree view"""
        self.tree_view.clear()
        
        # Check if organizer exists and has root_units
        if not hasattr(self.controller, 'organizer') or not hasattr(self.controller.organizer, 'root_units'):
            return
            
        # Create root items
        items = {}
        for unit_id in self.controller.organizer.root_units:
            unit = self.controller.organizer.units[unit_id]
            item = QtWidgets.QTreeWidgetItem([unit.name])
            item.setData(0, QtCore.Qt.UserRole, unit_id)
            self.tree_view.addTopLevelItem(item)
            items[unit_id] = item
            
            # Recursively add children
            self._add_children(unit_id, item, items)
            
        self.tree_view.expandAll()
        
    def _add_children(self, unit_id, parent_item, items):
        """Recursively add children to the tree"""
        unit = self.controller.organizer.units[unit_id]
        
        for child_id in unit.children:
            child_unit = self.controller.organizer.units[child_id]
            child_item = QtWidgets.QTreeWidgetItem([child_unit.name])
            child_item.setData(0, QtCore.Qt.UserRole, child_id)
            parent_item.addChild(child_item)
            items[child_id] = child_item
            
            # Recursively add children
            self._add_children(child_id, child_item, items)
            
    # Rest of the methods remain the same...
            
    def on_selection_changed(self):
        """Handle selection changes in the tree"""
        selected_items = self.tree_view.selectedItems()
        if not selected_items:
            self.properties_group.setEnabled(False)
            return
            
        self.properties_group.setEnabled(True)
        unit_id = selected_items[0].data(0, QtCore.Qt.UserRole)
        unit = self.controller.organizer.units[unit_id]
        
        # Update properties panel
        self.name_edit.setText(unit.name)
        self.visible_check.setChecked(unit.properties.get("visible", True))
        self.locked_check.setChecked(unit.properties.get("locked", False))
        
    def update_properties(self):
        """Update properties of the selected unit"""
        selected_items = self.tree_view.selectedItems()
        if not selected_items:
            return
            
        unit_id = selected_items[0].data(0, QtCore.Qt.UserRole)
        unit = self.controller.organizer.units[unit_id]
        
        unit.name = self.name_edit.text()
        unit.properties["visible"] = self.visible_check.isChecked()
        unit.properties["locked"] = self.locked_check.isChecked()
        
        # Update tree item text
        selected_items[0].setText(0, unit.name)
        
    def add_unit(self, level):
        """Add a new organizational unit"""
        # Get selected unit for parent
        selected_items = self.tree_view.selectedItems()
        parent_id = None
        
        if selected_items:
            parent_id = selected_items[0].data(0, QtCore.Qt.UserRole)
            
        # Create new unit
        name = f"New {level.value.capitalize()}"
        unit_id = self.controller.organizer.create_unit(name, level, parent_id)
        
        # Refresh tree
        self.refresh_tree()
        
    def remove_selected(self):
        """Remove the selected unit"""
        selected_items = self.tree_view.selectedItems()
        if not selected_items:
            return
            
        unit_id = selected_items[0].data(0, QtCore.Qt.UserRole)
        self.controller.organizer.delete_unit(unit_id)
        
        # Refresh tree
        self.refresh_tree()