print("Loading gui.py...")

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QInputDialog, QFileDialog, QMessageBox, QComboBox, QDialog, QLabel, QLineEdit,
    QHBoxLayout, QTextEdit, QKeySequenceEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence

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

        # Step 1: Shortcut combo input using QKeySequenceEdit
        layout.addWidget(QLabel("Enter shortcut key combination (e.g. Alt+C):"))
        self.combo_input = QKeySequenceEdit()
        layout.addWidget(self.combo_input)

        # Step 2: PNG file selector
        self.png_path = None
        btn_browse = QPushButton("Select PNG Image")
        btn_browse.clicked.connect(self.browse_png)
        layout.addWidget(btn_browse)

        self.png_label = QLabel("No file selected")
        layout.addWidget(self.png_label)

        # Step 3: Click type
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

    def on_create(self):
        combo = self.combo_input.keySequence().toString()  # Default format is NativeText
        if not logic.is_shortcut_valid(combo, [s["combo"] for s in self.existing_shortcuts]):
            QMessageBox.warning(self, "Invalid Shortcut", "Shortcut combo invalid, common, or already used.")
            return
        if not self.png_path:
            QMessageBox.warning(self, "No Image", "Please select a PNG image file.")
            return

        # Copy image to assets folder
        try:
            filename = os.path.basename(self.png_path)
            dest_path = functions.copy_image_to_assets(self.png_path, ASSETS_DIR, filename)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy image: {e}")
            return

        self.shortcut["combo"] = combo
        self.shortcut["name"] = functions.sanitize_filename(combo.replace("+", "_"))
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

        self.setLayout(layout)
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for sc in self.shortcuts:
            item = QListWidgetItem(f"{sc['combo']}:\n{functions.format_steps_for_display(sc.get('steps', []))}")
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
        shortcut_text = selected_item.text().split(":\n")[0]  # Extract combo
        shortcut = next((sc for sc in self.shortcuts if sc["combo"] == shortcut_text), None)

        if shortcut:
            dialog = CreateShortcutDialog(self.shortcuts, self)
            dialog.combo_input.setKeySequence(QKeySequence(shortcut["combo"]))
            dialog.png_path = os.path.join(ASSETS_DIR, shortcut["steps"][0]["target"])
            dialog.png_label.setText(dialog.png_path)
            dialog.click_combo.setCurrentText(shortcut["steps"][0]["action"])

            if dialog.exec():
                updated_shortcut = dialog.shortcut
                logic.save_shortcut(updated_shortcut)
                self.shortcuts = logic.load_all_shortcuts()  # Reload shortcuts
                self.refresh_list()
        else:
            QMessageBox.warning(self, "Error", "Could not find the selected shortcut.")


def launch_gui():
    app = QApplication(sys.argv)  # MUST be here, in main thread
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
