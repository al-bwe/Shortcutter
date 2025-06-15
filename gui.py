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
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap
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

        # Shortcut name input
        layout.addWidget(QLabel("Enter shortcut name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Key combo input
        layout.addWidget(QLabel("Enter key combo trigger:"))
        self.combo_input = QKeySequenceEdit()
        layout.addWidget(self.combo_input)

        # Steps list
        layout.addWidget(QLabel("Steps:"))
        self.steps_list = QListWidget()
        self.steps_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.steps_list)

        # Add step options
        step_layout = QHBoxLayout()

        # Add delay step
        self.delay_input = QLineEdit()
        self.delay_input.setPlaceholderText("Delay (seconds)")
        step_layout.addWidget(self.delay_input)
        btn_add_delay = QPushButton("Add Delay")
        btn_add_delay.clicked.connect(self.add_delay_step)
        step_layout.addWidget(btn_add_delay)

        # Add move to image step
        btn_add_image = QPushButton("Move to Image")
        btn_add_image.clicked.connect(self.add_image_step)
        step_layout.addWidget(btn_add_image)

        # Add move to origin step
        btn_add_origin = QPushButton("Move to Origin")
        btn_add_origin.clicked.connect(self.add_origin_step)
        step_layout.addWidget(btn_add_origin)

        # Add check duplicates step
        btn_add_duplicates = QPushButton("Check Duplicates")
        btn_add_duplicates.clicked.connect(self.add_duplicates_step)
        step_layout.addWidget(btn_add_duplicates)

        # Add left click step
        btn_add_left_click = QPushButton("Left Click")
        btn_add_left_click.clicked.connect(self.add_left_click_step)
        step_layout.addWidget(btn_add_left_click)

        # Add right click step
        btn_add_right_click = QPushButton("Right Click")
        btn_add_right_click.clicked.connect(self.add_right_click_step)
        step_layout.addWidget(btn_add_right_click)

        layout.addLayout(step_layout)

        # Reorder and delete steps
        reorder_layout = QHBoxLayout()

        btn_move_up = QPushButton("Move Up")
        btn_move_up.clicked.connect(self.move_step_up)
        reorder_layout.addWidget(btn_move_up)

        btn_move_down = QPushButton("Move Down")
        btn_move_down.clicked.connect(self.move_step_down)
        reorder_layout.addWidget(btn_move_down)

        btn_delete_step = QPushButton("Delete Step")
        btn_delete_step.clicked.connect(self.delete_step)
        reorder_layout.addWidget(btn_delete_step)

        layout.addLayout(reorder_layout)

        # Save button
        btn_ok = QPushButton("Save Shortcut")
        btn_ok.clicked.connect(self.on_create)
        layout.addWidget(btn_ok)

        self.setLayout(layout)

    def add_delay_step(self):
        delay = self.delay_input.text()
        if delay.isdigit():
            self.steps_list.addItem(f"Delay: {delay}s")
            self.shortcut["steps"].append({"action": "delay", "duration": int(delay)})
            self.delay_input.clear()
        else:
            QMessageBox.warning(self, "Invalid Input", "Delay must be a number.")

    def add_image_step(self):
        """
        Add a step to move the cursor to an image.
        Allows users to select an image via file explorer, snippet tool, or clipboard.
        Moves the selected image into the icon assets directory.
        """
        options = QMessageBox()
        options.setWindowTitle("Select Image Source")
        options.setText("Choose how to provide the image:")
        options.setStandardButtons(QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Cancel)
        options.addButton("Use Snippet Tool", QMessageBox.ButtonRole.ActionRole)
        options.addButton("Use Clipboard", QMessageBox.ButtonRole.ActionRole)

        choice = options.exec()

        if choice == QMessageBox.StandardButton.Open:
            # File explorer option
            fname, _ = QFileDialog.getOpenFileName(self, "Select PNG file", "", "PNG Files (*.png)")
            if fname:
                filename = os.path.basename(fname)
                dest_path = functions.copy_image_to_assets(fname, ASSETS_DIR, filename)
                self.display_step_with_image(f"Move cursor to image: {filename}", dest_path)
                self.shortcut["steps"].append({"action": "move_to_image", "target": filename})

        elif choice == 0:  # Snippet Tool
            snippet = ImageGrab.grab()  # Capture a screenshot using the snippet tool
            filename = f"snippet_{int(time.time())}.png"
            dest_path = os.path.join(ASSETS_DIR, filename)
            snippet.save(dest_path)
            self.display_step_with_image(f"Move cursor to image: {filename}", dest_path)
            self.shortcut["steps"].append({"action": "move_to_image", "target": filename})

        elif choice == 1:  # Clipboard
            clipboard_image = QApplication.clipboard().pixmap()
            if clipboard_image.isNull():
                QMessageBox.warning(self, "Clipboard Error", "No image found in clipboard.")
            else:
                filename = f"clipboard_{int(time.time())}.png"
                dest_path = os.path.join(ASSETS_DIR, filename)
                clipboard_image.save(dest_path, "PNG")  # Save clipboard image as PNG
                self.display_step_with_image(f"Move cursor to image: {filename}", dest_path)
                self.shortcut["steps"].append({"action": "move_to_image", "target": filename})

    def display_step_with_image(self, description: str, image_path: str):
        """
        Display the step description along with the image in the step list.
        """
        step_item = QListWidgetItem(description)
        pixmap = QPixmap(image_path)
        icon = QIcon(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        step_item.setIcon(icon)
        self.steps_list.addItem(step_item)

    def add_origin_step(self):
        self.steps_list.addItem("Move to Origin")
        self.shortcut["steps"].append({"action": "move_to_origin"})

    def add_duplicates_step(self):
        """
        Add a step to check for duplicate icons.
        Allows users to select an image via file explorer, snippet tool, or clipboard.
        """
        options = QMessageBox()
        options.setWindowTitle("Select Image Source")
        options.setText("Choose how to provide the image:")
        options.setStandardButtons(QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Cancel)
        options.addButton("Use Snippet Tool", QMessageBox.ButtonRole.ActionRole)
        options.addButton("Use Clipboard", QMessageBox.ButtonRole.ActionRole)

        choice = options.exec()

        if choice == QMessageBox.StandardButton.Open:
            # File explorer option
            fname, _ = QFileDialog.getOpenFileName(self, "Select PNG file", "", "PNG Files (*.png)")
            if fname:
                filename = os.path.basename(fname)
                dest_path = functions.copy_image_to_assets(fname, ASSETS_DIR, filename)
                self.steps_list.addItem(f"Check Duplicates: {filename}")
                self.shortcut["steps"].append({"action": "check_duplicates", "target": filename})

        elif choice == 0:  # Snippet Tool
            snippet = ImageGrab.grab()  # Capture a screenshot using the snippet tool
            filename = f"snippet_{int(time.time())}.png"
            dest_path = os.path.join(ASSETS_DIR, filename)
            snippet.save(dest_path)
            self.steps_list.addItem(f"Check Duplicates: {filename}")
            self.shortcut["steps"].append({"action": "check_duplicates", "target": filename})

        elif choice == 1:  # Clipboard
            clipboard_image = QApplication.clipboard().image()
            if clipboard_image.isNull():
                QMessageBox.warning(self, "Clipboard Error", "No image found in clipboard.")
            else:
                filename = f"clipboard_{int(time.time())}.png"
                dest_path = os.path.join(ASSETS_DIR, filename)
                clipboard_image.save(dest_path)
                self.steps_list.addItem(f"Check Duplicates: {filename}")
                self.shortcut["steps"].append({"action": "check_duplicates", "target": filename})

    def add_left_click_step(self):
        self.steps_list.addItem("Left Click")
        self.shortcut["steps"].append({"action": "left_click"})

    def add_right_click_step(self):
        self.steps_list.addItem("Right Click")
        self.shortcut["steps"].append({"action": "right_click"})

    def move_step_up(self):
        current_row = self.steps_list.currentRow()
        if current_row > 0:
            current_item = self.steps_list.takeItem(current_row)
            self.steps_list.insertItem(current_row - 1, current_item)
            self.steps_list.setCurrentRow(current_row - 1)
            self.shortcut["steps"].insert(current_row - 1, self.shortcut["steps"].pop(current_row))

    def move_step_down(self):
        current_row = self.steps_list.currentRow()
        if current_row < self.steps_list.count() - 1:
            current_item = self.steps_list.takeItem(current_row)
            self.steps_list.insertItem(current_row + 1, current_item)
            self.steps_list.setCurrentRow(current_row + 1)
            self.shortcut["steps"].insert(current_row + 1, self.shortcut["steps"].pop(current_row))

    def delete_step(self):
        current_row = self.steps_list.currentRow()
        if current_row >= 0:
            self.steps_list.takeItem(current_row)
            del self.shortcut["steps"][current_row]

    def on_create(self):
        name = self.name_input.text().strip()
        combo = self.combo_input.keySequence().toString()
        if not name or not combo:
            QMessageBox.warning(self, "Missing Input", "Please enter a name and key combo for the shortcut.")
            return
        if not self.shortcut["steps"]:
            QMessageBox.warning(self, "No Steps", "Please add at least one step to the shortcut.")
            return

        self.shortcut["name"] = name
        self.shortcut["combo"] = combo
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
            for step in shortcut["steps"]:
                if step["action"] == "shortcut":
                    dialog.steps_list.addItem(f"Shortcut: {step['combo']}")
                elif step["action"] == "wait":
                    dialog.steps_list.addItem(f"Wait: {step['duration']}s")
                elif step["action"] == "wait_for_symbol":
                    dialog.steps_list.addItem(f"Wait for Symbol: {step['target']}")

            if dialog.exec():
                updated_shortcut = dialog.shortcut
                logic.save_shortcut(updated_shortcut)
                self.shortcuts = logic.load_all_shortcuts()
                self.refresh_list()
        else:
            QMessageBox.warning(self, "Error", "Could not find the selected shortcut.")


def launch_gui():
    app = QApplication(sys.argv)  # MUST be here, in main thread
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
