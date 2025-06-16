print("Loading gui.py...")

import sys
import os
import uuid
import tempfile
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QInputDialog, QFileDialog, QMessageBox, QComboBox, QDialog, QLabel, QLineEdit,
    QHBoxLayout, QTextEdit, QKeySequenceEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QIcon
from PIL import ImageGrab

import logic
import functions
from constants import ASSETS_DIR


class CreateShortcutDialog(QDialog):
    def __init__(self, existing_shortcuts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create/Edit Shortcut")
        self.existing_shortcuts = existing_shortcuts
        self.shortcut = {
            "name": "",
            "combo": "",
            "steps": []
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Step 1: Shortcut name input
        layout.addWidget(QLabel("Enter shortcut name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Step 2: Shortcut combo input using QKeySequenceEdit
        layout.addWidget(QLabel("Enter shortcut key combination (e.g. Alt+C):"))
        self.combo_input = QKeySequenceEdit()
        layout.addWidget(self.combo_input)

        # Step 3: PNG file selector
        self.png_path = None
        btn_browse = QPushButton("Select PNG Image")
        btn_browse.clicked.connect(self.browse_png)
        layout.addWidget(btn_browse)

        self.png_label = QLabel("No file selected")
        layout.addWidget(self.png_label)

        # Step 4: Create PNG from Clipboard
        btn_clipboard = QPushButton("Create PNG from Clipboard")
        btn_clipboard.clicked.connect(self.create_png_from_clipboard)
        layout.addWidget(btn_clipboard)

        # Step 5: Click type
        layout.addWidget(QLabel("Select mouse click action:"))
        self.click_combo = QComboBox()
        self.click_combo.addItems(["left_click", "right_click"])
        layout.addWidget(self.click_combo)

        # Buttons
        btn_ok = QPushButton("Save Shortcut")
        btn_ok.clicked.connect(self.on_create)
        layout.addWidget(btn_ok)

        self.setLayout(layout)

    def browse_png(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select PNG file", "", "PNG Files (*.png)")
        if fname:
            if functions.validate_image_file(fname):
                self.png_path = fname
                self.png_label.setText(fname)
            else:
                QMessageBox.warning(self, "Invalid file", "Selected file is not a valid PNG image.")

    def create_png_from_clipboard(self):
        try:
            # Grab the image from the clipboard
            image = ImageGrab.grabclipboard()
            if image is None:
                QMessageBox.warning(self, "No Image", "No image found in clipboard.")
                return

            # Generate a unique filename for the clipboard snippet
            filename = f"clipboard_snippet_{uuid.uuid4().hex}.png"
            self.png_path = os.path.join(ASSETS_DIR, filename)

            # Ensure the assets directory exists
            os.makedirs(ASSETS_DIR, exist_ok=True)

            # Save the image to the assets directory
            image.save(self.png_path, "PNG")

            # Update the label to show the saved path
            self.png_label.setText(f"Saved: {self.png_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image: {e}")

    def on_create(self):
        name = self.name_input.text().strip()
        combo = self.combo_input.keySequence().toString()  # Default format is NativeText
        if not name:
            QMessageBox.warning(self, "No Name", "Please enter a name for the shortcut.")
            return
        if not logic.is_shortcut_valid(combo, [s["combo"] for s in self.existing_shortcuts]):
            QMessageBox.warning(self, "Invalid Shortcut", "Shortcut combo invalid, common, or already used.")
            return
        if not self.png_path:
            QMessageBox.warning(self, "No Image", "Please select a PNG image file.")
            return

        # Check if the image is already in the ASSETS_DIR
        filename = os.path.basename(self.png_path)
        if not self.png_path.startswith(ASSETS_DIR):
            try:
                dest_path = functions.copy_image_to_assets(self.png_path, ASSETS_DIR, filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy image: {e}")
                return
        else:
            dest_path = self.png_path  # Image is already in the ASSETS_DIR

        self.shortcut["name"] = name
        self.shortcut["combo"] = combo
        self.shortcut["steps"].append({
            "action": self.click_combo.currentText(),
            "target": filename
        })

        self.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shortcut Creator")
        self.shortcuts = logic.load_all_shortcuts()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.btn_create = QPushButton("Create New Shortcut")
        self.btn_create.clicked.connect(self.create_new_shortcut)
        layout.addWidget(self.btn_create)

        self.btn_edit = QPushButton("Edit Selected Shortcut")
        self.btn_edit.clicked.connect(self.edit_selected_shortcut)
        layout.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("Delete Selected Shortcut")
        self.btn_delete.clicked.connect(self.delete_selected_shortcut)
        layout.addWidget(self.btn_delete)

        self.setLayout(layout)
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for sc in self.shortcuts:
            item = QListWidgetItem()
            item.setText(f"{sc['name']} ({sc['combo']})")
            icon_path = os.path.join(ASSETS_DIR, sc["steps"][0]["target"])
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
            self.list_widget.addItem(item)

    def create_new_shortcut(self):
        dialog = CreateShortcutDialog(self.shortcuts, self)
        if dialog.exec():
            shortcut = dialog.shortcut
            logic.save_shortcut(shortcut)
            self.shortcuts.append(shortcut)
            self.refresh_list()

    def edit_selected_shortcut(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a shortcut to edit.")
            return

        selected_item = selected_items[0]
        # Extract the shortcut name and combo from the displayed text
        shortcut_text = selected_item.text()
        name, combo = shortcut_text.split(" (")
        combo = combo.rstrip(")")

        # Find the shortcut by name and combo
        shortcut = next((sc for sc in self.shortcuts if sc["name"] == name and sc["combo"] == combo), None)

        if shortcut:
            dialog = CreateShortcutDialog(self.shortcuts, self)
            dialog.name_input.setText(shortcut["name"])
            dialog.combo_input.setKeySequence(QKeySequence(shortcut["combo"]))
            dialog.png_path = os.path.join(ASSETS_DIR, shortcut["steps"][0]["target"])
            dialog.png_label.setText(dialog.png_path)
            dialog.click_combo.setCurrentText(shortcut["steps"][0]["action"])

            if dialog.exec():
                updated_shortcut = dialog.shortcut
                if not logic.is_shortcut_valid(updated_shortcut["combo"], [s["combo"] for s in self.shortcuts], shortcut):
                    QMessageBox.warning(self, "Invalid Shortcut", "Shortcut combo invalid, common, or already used.")
                    return

                # Handle name change: delete old shortcut file if name has changed
                if updated_shortcut["name"] != shortcut["name"]:
                    logic.delete_shortcut(shortcut)

                logic.save_shortcut(updated_shortcut)  # Save the updated shortcut
                self.shortcuts = logic.load_all_shortcuts()  # Reload shortcuts
                self.refresh_list()
        else:
            QMessageBox.warning(self, "Error", "Could not find the selected shortcut.")

    def delete_selected_shortcut(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a shortcut to delete.")
            return

        selected_item = selected_items[0]
        # Extract the shortcut name and combo from the displayed text
        shortcut_text = selected_item.text()
        name, combo = shortcut_text.split(" (")
        combo = combo.rstrip(")")

        # Find the shortcut by name and combo
        shortcut = next((sc for sc in self.shortcuts if sc["name"] == name and sc["combo"] == combo), None)

        if shortcut:
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete the shortcut '{shortcut['name']}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                logic.delete_shortcut(shortcut)
                self.shortcuts = logic.load_all_shortcuts()  # Reload shortcuts
                self.refresh_list()
        else:
            QMessageBox.warning(self, "Error", "Could not find the selected shortcut.")


def launch_gui():
    app = QApplication(sys.argv)  # MUST be here, in main thread
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
