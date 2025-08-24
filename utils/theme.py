# utils/theme.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Theme:
    name: str
    background_color: str
    button_color: str
    text_color: str
    highlight_color: str
    border_color: str
    
class ThemeManager:
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: str = "default"
        
        # Initialize built-in themes
        self._initialize_themes()
        
    def _initialize_themes(self):
        # Default theme
        self.themes["default"] = Theme(
            name="Default",
            background_color="#323232",
            button_color="#505050",
            text_color="#FFFFFF",
            highlight_color="#1E90FF",
            border_color="#202020"
        )
        
        # Dark theme
        self.themes["dark"] = Theme(
            name="Dark",
            background_color="#1E1E1E",
            button_color="#2D2D30",
            text_color="#CCCCCC",
            highlight_color="#007ACC",
            border_color="#3E3E42"
        )
        
        # Light theme
        self.themes["light"] = Theme(
            name="Light",
            background_color="#F0F0F0",
            button_color="#FFFFFF",
            text_color="#000000",
            highlight_color="#0066FF",
            border_color="#CCCCCC"
        )
        
    def set_theme(self, theme_name: str):
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            
    def get_theme(self) -> Theme:
        """Get the current theme"""
        return self.themes.get(self.current_theme, self.themes["default"])
        
    def add_theme(self, theme: Theme):
        """Add a custom theme"""
        self.themes[theme.name.lower()] = theme
        
    def remove_theme(self, theme_name: str):
        """Remove a theme (cannot remove built-in themes)"""
        if theme_name not in ["default", "dark", "light"]:
            self.themes.pop(theme_name, None)

# Update the main window to use themes
class PickerMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = PickerController()
        self.controller.view = self
        self.theme_manager = ThemeManager()
        self.setup_ui()
        self.apply_theme()
        
    def apply_theme(self):
        """Apply the current theme to the UI"""
        theme = self.theme_manager.get_theme()
        
        # Set stylesheet
        stylesheet = f"""
            QMainWindow, QWidget {{
                background-color: {theme.background_color};
                color: {theme.text_color};
            }}
            QToolBar {{
                background-color: {theme.button_color};
                border: 1px solid {theme.border_color};
            }}
            QDockWidget {{
                background-color: {theme.background_color};
                color: {theme.text_color};
                titlebar-close-icon: url(none);
                titlebar-normal-icon: url(none);
            }}
            QDockWidget::title {{
                background-color: {theme.button_color};
                padding: 5px;
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {theme.button_color};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
            }}
            QPushButton {{
                background-color: {theme.button_color};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {theme.highlight_color};
            }}
        """
        
        self.setStyleSheet(stylesheet)
        
        # Update canvas background
        if hasattr(self, 'canvas'):
            self.canvas.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(theme.background_color)))