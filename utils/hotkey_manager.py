# utils/hotkey_manager.py
from PySide2 import QtWidgets, QtCore, QtGui
import json
import os

class HotkeyManager:
    def __init__(self, controller):
        self.controller = controller
        self.hotkeys = {}  # key: (button_id, callback)
        self.config_file = os.path.join(os.path.dirname(__file__), "..", "config", "hotkeys.json")
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        self.load_hotkeys()
        
    def register_hotkey(self, key_sequence, button_id, callback):
        """Register a hotkey for a button"""
        # Convert to standard format
        key = self._normalize_key_sequence(key_sequence)
        
        if key in self.hotkeys:
            # Hotkey already registered
            return False
            
        self.hotkeys[key] = (button_id, callback)
        return True
        
    def unregister_hotkey(self, key_sequence):
        """Unregister a hotkey"""
        key = self._normalize_key_sequence(key_sequence)
        if key in self.hotkeys:
            del self.hotkeys[key]
            return True
        return False
        
    def _normalize_key_sequence(self, key_sequence):
        """Normalize key sequence to a standard format"""
        if isinstance(key_sequence, str):
            return key_sequence.upper().replace(" ", "")
        elif isinstance(key_sequence, QtGui.QKeySequence):
            return key_sequence.toString().upper().replace(" ", "")
        return str(key_sequence).upper().replace(" ", "")
        
    def handle_key_event(self, event):
        """Handle key events and trigger hotkeys"""
        key = self._event_to_key_string(event)
        
        if key in self.hotkeys:
            button_id, callback = self.hotkeys[key]
            callback()
            return True
            
        return False
        
    def _event_to_key_string(self, event):
        """Convert QKeyEvent to a normalized key string"""
        modifiers = []
        
        if event.modifiers() & QtCore.Qt.ControlModifier:
            modifiers.append("Ctrl")
        if event.modifiers() & QtCore.Qt.AltModifier:
            modifiers.append("Alt")
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            modifiers.append("Shift")
        if event.modifiers() & QtCore.Qt.MetaModifier:
            modifiers.append("Meta")
            
        key = QtGui.QKeySequence(event.key()).toString()
        
        if modifiers:
            return "+".join(modifiers + [key])
        return key
        
    def save_hotkeys(self):
        """Save hotkeys to config file"""
        # Convert to serializable format
        serializable = {}
        for key, (button_id, _) in self.hotkeys.items():
            serializable[key] = button_id
            
        with open(self.config_file, 'w') as f:
            json.dump(serializable, f, indent=4)
            
    def load_hotkeys(self):
        """Load hotkeys from config file"""
        if not os.path.exists(self.config_file):
            return
            
        try:
            with open(self.config_file, 'r') as f:
                serializable = json.load(f)
                
            # Reconstruct hotkeys from button IDs
            for key, button_id in serializable.items():
                button = self.controller.get_button_by_id(button_id)
                if button:
                    self.register_hotkey(key, button_id, lambda: self.controller.execute_button(button_id))
        except Exception as e:
            print(f"Error loading hotkeys: {e}")
            
    def get_hotkey_editor_dialog(self):
        """Create a hotkey editor dialog"""
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Hotkey Editor")
        dialog.resize(400, 300)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Hotkey list
        self.hotkey_list = QtWidgets.QListWidget()
        layout.addWidget(self.hotkey_list)
        
        # Refresh list
        self._refresh_hotkey_list()
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        add_btn = QtWidgets.QPushButton("Add Hotkey")
        add_btn.clicked.connect(self._add_hotkey)
        button_layout.addWidget(add_btn)
        
        edit_btn = QtWidgets.QPushButton("Edit Hotkey")
        edit_btn.clicked.connect(self._edit_hotkey)
        button_layout.addWidget(edit_btn)
        
        remove_btn = QtWidgets.QPushButton("Remove Hotkey")
        remove_btn.clicked.connect(self._remove_hotkey)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        return dialog
        
    def _refresh_hotkey_list(self):
        """Refresh the hotkey list widget"""
        self.hotkey_list.clear()
        
        for key, (button_id, _) in self.hotkeys.items():
            button = self.controller.get_button_by_id(button_id)
            label = button.label if button else f"Unknown Button ({button_id})"
            self.hotkey_list.addItem(f"{key}: {label}")
            
    def _add_hotkey(self):
        """Add a new hotkey"""
        # Implementation for adding hotkeys
        pass
        
    def _edit_hotkey(self):
        """Edit a selected hotkey"""
        # Implementation for editing hotkeys
        pass
        
    def _remove_hotkey(self):
        """Remove a selected hotkey"""
        current_item = self.hotkey_list.currentItem()
        if not current_item:
            return
            
        # Extract key from list item text
        key = current_item.text().split(":")[0].strip()
        
        if self.unregister_hotkey(key):
            self._refresh_hotkey_list()