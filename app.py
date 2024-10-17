import json
import os
import sys
import socket

from functools import partial
from typing import Dict, Optional, List

from PyQt6.QtGui import (
    QAction,
    QIcon,
    QDragEnterEvent,
    QDropEvent,
    QKeySequence,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QPlainTextEdit,
    QTabWidget,
    QMessageBox,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QLabel,
    QStatusBar,
    QMenu,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QActionGroup


class FindReplaceDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.find_layout = QHBoxLayout()
        self.find_input = QLineEdit()
        self.find_button = QPushButton("Find")
        self.find_layout.addWidget(QLabel("Find:"))
        self.find_layout.addWidget(self.find_input)
        self.find_layout.addWidget(self.find_button)

        self.replace_layout = QHBoxLayout()
        self.replace_input = QLineEdit()
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")
        self.replace_layout.addWidget(QLabel("Replace:"))
        self.replace_layout.addWidget(self.replace_input)
        self.replace_layout.addWidget(self.replace_button)
        self.replace_layout.addWidget(self.replace_all_button)

        self.layout.addLayout(self.find_layout)
        self.layout.addLayout(self.replace_layout)

        self.replace_input.hide()
        self.replace_button.hide()
        self.replace_all_button.hide()


class Notepad(QMainWindow):
    def __init__(self) -> None:
        """Initialize the Notepad application."""
        super().__init__()
        self.setWindowTitle("CNB Notepad")
        self.setGeometry(100, 100, 800, 600)

        icon_path = os.path.join(os.path.dirname(__file__), "app.ico")
        self.setWindowIcon(QIcon(icon_path))

        hostname = socket.gethostname().split(".")[0]
        self.settings_file = f"settings-{hostname}.json"
        self.settings = self.load_settings()
        self.max_recent_files = max(
            0, min(int(self.settings.get("max_recent_files", 5)), 10)
        )
        self.tabs = QTabWidget()
        self.tabs.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCentralWidget(self.tabs)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.last_file_path: Optional[str] = self.settings.get("last_session")
        self.word_wrap_enabled: bool = self.settings.get("word_wrap", False)
        self.reopen_last_enabled: bool = self.settings.get("reopen_last", True)
        self.recent_files: List[str] = self.settings.get("recent_files", [])
        self.max_recent_files = int(self.settings.get("max_recent_files", 5))
        self.dark_mode: bool = self.settings.get("dark_mode", True)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.word_count_label = QLabel("Words: 0")
        self.word_count_label.hide()
        self.statusBar.addPermanentWidget(self.word_count_label)

        self.char_count_label = QLabel("Characters: 0")
        self.char_count_label.hide()
        self.statusBar.addPermanentWidget(self.char_count_label)

        self.file_status_label = QLabel("Status: No File")
        self.statusBar.addPermanentWidget(self.file_status_label)

        self.update_word_count_timer = QTimer()
        self.update_word_count_timer.timeout.connect(self.update_counts)
        self.update_word_count_timer.start(1000)

        self.file_menu = None
        self.recent_menu = None
        self.edit_menu = None
        self.create_menu()
        self.update_menu_state()

        if self.reopen_last_enabled and self.last_file_path:
            self.open_file(self.last_file_path)

        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.find_button.clicked.connect(self.find_text)
        self.find_replace_dialog.replace_button.clicked.connect(
            self.replace_text
        )
        self.find_replace_dialog.replace_all_button.clicked.connect(
            self.replace_all_text
        )

        self.setAcceptDrops(True)

        self.addAction(
            self.create_action(
                "Close Tab",
                self.close_current_tab,
                QKeySequence.StandardKey.Close,
            )
        )

    def create_menu(self) -> None:
        """Create the application menu with keyboard shortcuts."""
        self.file_menu = self.menuBar().addMenu("File")
        self.file_menu.addAction(
            self.create_action(
                "New", self.new_file, QKeySequence.StandardKey.New
            )
        )

        self.recent_menu = QMenu("Recent", self)
        self.recent_menu_action = self.file_menu.addMenu(self.recent_menu)

        self.file_menu.addAction(
            self.create_action(
                "Open", self.open_file_dialog, QKeySequence.StandardKey.Open
            )
        )
        self.file_menu.addAction(
            self.create_action(
                "Open Read-Only", self.open_file_readonly_dialog
            )
        )

        self.save_action = self.create_action(
            "Save", self.save_file, QKeySequence.StandardKey.Save
        )
        self.file_menu.addAction(self.save_action)

        self.save_as_action = self.create_action(
            "Save As", self.save_file_as, QKeySequence.StandardKey.SaveAs
        )
        self.file_menu.addAction(self.save_as_action)

        self.file_menu.addSeparator()

        self.close_tab_action = self.create_action(
            "Close Tab",
            self.close_current_tab,
            QKeySequence.StandardKey.Close,
        )
        self.file_menu.addAction(self.close_tab_action)

        self.close_all_action = self.create_action(
            "Close All", self.close_all_tabs
        )
        self.file_menu.addAction(self.close_all_action)

        self.file_menu.addSeparator()
        self.file_menu.addAction(
            self.create_action(
                "Exit", self.close, QKeySequence.StandardKey.Quit
            )
        )

        self.edit_menu = self.menuBar().addMenu("Edit")
        self.edit_menu.addAction(
            self.create_action(
                "Undo", self.undo, QKeySequence.StandardKey.Undo
            )
        )
        self.edit_menu.addAction(
            self.create_action(
                "Redo", self.redo, QKeySequence.StandardKey.Redo
            )
        )
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(
            self.create_action(
                "Cut", self.cut_text, QKeySequence.StandardKey.Cut
            )
        )
        self.edit_menu.addAction(
            self.create_action(
                "Copy", self.copy_text, QKeySequence.StandardKey.Copy
            )
        )
        self.edit_menu.addAction(
            self.create_action(
                "Paste", self.paste_text, QKeySequence.StandardKey.Paste
            )
        )
        self.edit_menu.addAction(
            self.create_action(
                "Select All",
                self.select_all_text,
                QKeySequence.StandardKey.SelectAll,
            )
        )
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(
            self.create_action(
                "Find", self.show_find, QKeySequence.StandardKey.Find
            )
        )
        self.edit_menu.addAction(
            self.create_action(
                "Find and Replace",
                self.show_find_replace,
                QKeySequence.StandardKey.Replace,
            )
        )

        options_menu = self.menuBar().addMenu("Options")
        word_wrap_action = self.create_action(
            "Word Wrap", self.toggle_word_wrap, checkable=True
        )
        word_wrap_action.setChecked(self.word_wrap_enabled)
        options_menu.addAction(word_wrap_action)

        reopen_last_action = self.create_action(
            "Reopen Last", self.toggle_reopen_last, checkable=True
        )
        reopen_last_action.setChecked(self.reopen_last_enabled)
        options_menu.addAction(reopen_last_action)

        dark_mode_action = self.create_action(
            "Dark Mode", self.toggle_theme, checkable=True
        )
        dark_mode_action.setChecked(self.dark_mode)
        options_menu.addAction(dark_mode_action)

        recent_files_menu = options_menu.addMenu("Max Recent Files")
        self.recent_files_action_group = QActionGroup(self)
        self.recent_files_action_group.setExclusive(True)
        for i in range(11):
            action = self.create_action(
                str(i),
                partial(self.set_max_recent_files, i),
                checkable=True,
            )
            action.setChecked(i == self.max_recent_files)
            self.recent_files_action_group.addAction(action)
            recent_files_menu.addAction(action)

        self.update_recent_files_menu()

    def toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        self.dark_mode = not self.dark_mode
        self.settings["dark_mode"] = self.dark_mode
        self.save_settings()
        self.set_theme()

    def set_theme(self) -> None:
        """Set the application theme (dark or light)."""
        if self.dark_mode:
            self.setStyleSheet(
                """
                QWidget { background-color: 
                QPlainTextEdit { background-color: 
                QMenuBar { background-color: 
                QMenu { background-color: 
                QMenu::item:selected { background-color: 
            """
            )
        else:
            self.setStyleSheet("")

    def create_action(
        self,
        name: str,
        slot: callable,
        shortcut: QKeySequence = None,
        checkable: bool = False,
    ) -> QAction:
        """Create a QAction with the given name, slot, and shortcut."""
        action = QAction(name, self)
        action.triggered.connect(slot)
        if shortcut:
            action.setShortcut(shortcut)
        action.setCheckable(checkable)
        return action

    def new_file(self) -> None:
        """Create a new file tab."""
        editor = self.create_editor()
        self.tabs.addTab(editor, "Untitled")
        self.tabs.setCurrentWidget(editor)
        self.update_title()
        self.update_menu_state()
        self.update_counts()

    def open_file_dialog(self) -> None:
        """Open a file dialog to select a file to open."""
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*)", options=options
        )
        if file_path:
            self.open_file(file_path, read_only=False)

    def open_file_readonly_dialog(self) -> None:
        """Open a file dialog to select a file to open in read-only mode."""
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File (Read-Only)", "", "All Files (*)", options=options
        )
        if file_path:
            self.open_file(file_path, read_only=True)

    def open_file(self, file_path: str, read_only: bool = False) -> None:
        """Open the specified file and create a new tab for it."""
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                content = file.read()
                editor = self.create_editor(content)
                editor.setReadOnly(read_only)
                self.tabs.addTab(editor, os.path.basename(file_path))
                self.tabs.setCurrentWidget(editor)
                self.last_file_path = file_path
                self.settings["last_session"] = file_path
                self.add_recent_file(file_path)
                self.save_settings()
        self.update_title()
        self.update_file_status()
        self.update_counts()

    def save_file(self) -> None:
        """Save the current file."""
        editor = self.tabs.currentWidget()
        if editor:
            file_path = self.last_file_path
            if not file_path:
                self.save_file_as()
            else:
                self.write_to_file(file_path, editor.toPlainText())
                self.set_tab_saved(self.tabs.currentIndex())

    def save_file_as(self) -> None:
        """Save the current file with a new name."""
        editor = self.tabs.currentWidget()
        if editor:
            options = QFileDialog.Option.DontUseNativeDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save As",
                "",
                "Text Files (*.txt);;All Files (*)",
                options=options,
            )
            if file_path:
                if not os.path.splitext(file_path)[1]:
                    file_path += ".txt"
                self.write_to_file(file_path, editor.toPlainText())
                self.last_file_path = file_path
                self.settings["last_session"] = file_path
                self.add_recent_file(file_path)
                self.save_settings()
                self.set_tab_saved(self.tabs.currentIndex())

    def write_to_file(self, file_path: str, content: str) -> None:
        """Write the given content to the specified file."""
        with open(file_path, "w") as file:
            file.write(content)
        self.tabs.setTabText(
            self.tabs.currentIndex(), os.path.basename(file_path)
        )
        self.update_title()

    def close_tab(self, index: int) -> bool:
        """Close the tab at the given index."""
        if self.maybe_save(index):
            widget = self.tabs.widget(index)
            if widget:
                widget.deleteLater()
                self.tabs.removeTab(index)
            self.on_tab_changed()
            self.update_menu_state()
            if self.tabs.count() == 0:
                self.update_counts()
            return True
        return False

    def close_current_tab(self) -> None:
        """Close the current tab."""
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            self.close_tab(current_index)

    def close_all_tabs(self) -> None:
        """Close all open tabs."""
        while self.tabs.count() > 0:
            if not self.close_tab(0):
                break

    def maybe_save(self, index: int) -> bool:
        """Check if the document needs saving and ask the user if necessary."""
        editor = self.tabs.widget(index)
        if editor and editor.document().isModified():
            ret = QMessageBox.warning(
                self,
                "Application",
                "The document has been modified.\nDo you want to save your changes?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if ret == QMessageBox.StandardButton.Save:
                return self.save_file()
            elif ret == QMessageBox.StandardButton.Cancel:
                return False
        return True

    def closeEvent(self, event):
        """Handle the window close event."""
        for i in range(self.tabs.count()):
            if not self.maybe_save(i):
                event.ignore()
                return
        event.accept()

    def cut_text(self) -> None:
        """Cut the selected text in the current editor."""
        self.get_current_editor().cut()

    def copy_text(self) -> None:
        """Copy the selected text in the current editor."""
        self.get_current_editor().copy()

    def paste_text(self) -> None:
        """Paste text from the clipboard into the current editor."""
        self.get_current_editor().paste()

    def select_all_text(self) -> None:
        """Select all text in the current editor."""
        self.get_current_editor().selectAll()

    def show_find_replace(self) -> None:
        """Show the find and replace dialog."""
        self.find_replace_dialog.show()
        self.find_replace_dialog.replace_input.show()
        self.find_replace_dialog.replace_button.show()
        self.find_replace_dialog.replace_all_button.show()

    def find_text(self) -> None:
        """Find the specified text in the current editor."""
        editor = self.get_current_editor()
        if editor:
            text = self.find_replace_dialog.find_input.text()
            if editor.find(text):
                self.statusBar().showMessage(f"Found '{text}'", 2000)
            else:
                self.statusBar().showMessage(f"'{text}' not found", 2000)

    def replace_text(self) -> None:
        """Replace the found text with the specified text."""
        editor = self.get_current_editor()
        if editor:
            find_text = self.find_replace_dialog.find_input.text()
            replace_text = self.find_replace_dialog.replace_input.text()
            cursor = editor.textCursor()
            if cursor.hasSelection() and cursor.selectedText() == find_text:
                cursor.insertText(replace_text)
                self.statusBar().showMessage(
                    f"Replaced '{find_text}' with '{replace_text}'", 2000
                )
            else:
                self.find_text()

    def replace_all_text(self) -> None:
        """Replace all occurrences of the found text with the specified text."""
        editor = self.get_current_editor()
        if editor:
            find_text = self.find_replace_dialog.find_input.text()
            replace_text = self.find_replace_dialog.replace_input.text()
            content = editor.toPlainText()
            new_content, count = content.replace(
                find_text, replace_text
            ), content.count(find_text)
            if count > 0:
                editor.setPlainText(new_content)
                self.statusBar().showMessage(
                    f"Replaced {count} occurrence(s) of '{find_text}' "
                    f"with '{replace_text}'",
                    2000,
                )
            else:
                self.statusBar().showMessage(f"'{find_text}' not found", 2000)

    def toggle_word_wrap(self) -> None:
        """Toggle word wrap for the current editor."""
        self.word_wrap_enabled = not self.word_wrap_enabled
        editor = self.get_current_editor()
        if editor:
            editor.setLineWrapMode(
                QPlainTextEdit.LineWrapMode.WidgetWidth
                if self.word_wrap_enabled
                else QPlainTextEdit.LineWrapMode.NoWrap
            )
        self.settings["word_wrap"] = self.word_wrap_enabled
        self.save_settings()

    def toggle_reopen_last(self) -> None:
        """Toggle the option to reopen the last file on startup."""
        self.reopen_last_enabled = not self.reopen_last_enabled
        self.settings["reopen_last"] = self.reopen_last_enabled
        self.save_settings()

    def load_settings(self) -> Dict:
        """Load settings from the settings file."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
                return settings
        return {
            "last_session": None,
            "word_wrap": False,
            "reopen_last": True,
            "recent_files": [],
            "max_recent_files": 5,
            "dark_mode": True,
        }

    def save_settings(self) -> None:
        """Save current settings to the settings file."""
        self.settings["max_recent_files"] = self.max_recent_files
        with open(self.settings_file, "w") as file:
            json.dump(self.settings, file, indent=4)

    def update_title(self) -> None:
        """Update the window title based on the current tab."""
        editor = self.get_current_editor()
        if editor:
            tab_name = self.tabs.tabText(self.tabs.currentIndex())
            if tab_name.startswith("•"):
                tab_name = tab_name[1:]
            title = (
                f"CNB Notepad • [{tab_name}]"
                if tab_name != "Untitled"
                else "CNB Notepad • [Untitled]"
            )
        else:
            title = "CNB Notepad"
        self.setWindowTitle(title)

    def text_changed(self) -> None:
        """Handle text changes in the current editor."""
        editor = self.get_current_editor()
        if editor and editor.document().isModified():
            current_tab_index = self.tabs.currentIndex()
            tab_name = self.tabs.tabText(current_tab_index)
            if not tab_name.startswith("•"):
                self.tabs.setTabText(current_tab_index, "•" + tab_name)
            self.update_title()
        self.update_file_status()
        self.update_counts()
        self.update_menu_state()

    def set_tab_saved(self, index: int) -> None:
        """Mark the tab at the given index as saved."""
        tab_name = self.tabs.tabText(index)
        if tab_name.startswith("•"):
            self.tabs.setTabText(index, tab_name[1:])
        editor = self.tabs.widget(index)
        if editor:
            editor.document().setModified(False)
        self.update_title()
        self.update_file_status()

    def create_editor(self, content: str = "") -> QPlainTextEdit:
        """Create a new text editor widget."""
        editor = QPlainTextEdit(content)
        editor.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.WidgetWidth
            if self.word_wrap_enabled
            else QPlainTextEdit.LineWrapMode.NoWrap
        )
        editor.textChanged.connect(self.text_changed)
        editor.textChanged.connect(self.update_file_status)

        editor.setAcceptDrops(True)
        editor.dragEnterEvent = self.editor_dragEnterEvent
        editor.dropEvent = self.editor_dropEvent

        return editor

    def get_current_editor(self) -> Optional[QPlainTextEdit]:
        """Get the currently active editor widget."""
        return self.tabs.currentWidget()

    def on_tab_changed(self) -> None:
        """Handle tab change events."""
        self.update_title()
        self.update_file_status()
        self.update_counts()
        self.update_menu_state()

    def add_recent_file(self, file_path: str) -> None:
        """Add a file to the recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[: self.max_recent_files]
        self.settings["recent_files"] = self.recent_files
        self.update_recent_files_menu()

    def update_recent_files_menu(self) -> None:
        """Update the recent files menu."""
        self.recent_menu.clear()

        recent_action = next(
            (
                action
                for action in self.file_menu.actions()
                if action.menu() == self.recent_menu
            ),
            None,
        )

        if self.max_recent_files == 0:

            if recent_action:
                self.file_menu.removeAction(recent_action)
            self.recent_menu_action.setMenu(None)
        else:

            self.recent_menu_action.setMenu(self.recent_menu)
            if self.recent_files:
                for file_path in self.recent_files[: self.max_recent_files]:
                    action = self.create_action(
                        os.path.basename(file_path),
                        lambda file_path=file_path: self.open_file(file_path),
                    )
                    self.recent_menu.addAction(action)
            else:
                action = self.create_action("(none)", lambda: None)
                action.setEnabled(False)
                self.recent_menu.addAction(action)

            if recent_action:
                self.file_menu.removeAction(recent_action)
            self.file_menu.insertMenu(
                self.file_menu.actions()[2], self.recent_menu
            )

        self.update_menu_state()

    def set_max_recent_files(self, value: int) -> None:
        """Set the maximum number of recent files to remember."""
        self.max_recent_files = max(0, min(int(value), 10))
        self.settings["max_recent_files"] = self.max_recent_files
        if self.max_recent_files > 0:
            self.recent_files = self.recent_files[: self.max_recent_files]
        else:
            self.recent_files = []
        self.settings["recent_files"] = self.recent_files
        self.save_settings()
        self.update_recent_files_menu()

        for action in self.recent_files_action_group.actions():
            action.setChecked(int(action.text()) == self.max_recent_files)

    def update_counts(self) -> None:
        """Update the word and character count labels."""
        editor = self.get_current_editor()
        if editor:
            text = editor.toPlainText()
            word_count = len(text.split())
            char_count = len(text)
            self.word_count_label.setText(f"Words: {word_count}")
            self.char_count_label.setText(f"Characters: {char_count}")
            self.word_count_label.show()
            self.char_count_label.show()
        else:
            self.word_count_label.hide()
            self.char_count_label.hide()

    def update_file_status(self) -> None:
        """Update the file status label with the current file status."""
        editor = self.get_current_editor()
        if editor:
            if editor.isReadOnly():
                status = "Read-Only"
            elif editor.document().isModified():
                status = "Modified"
            else:
                status = "Saved"
            self.file_status_label.setText(f"Status: {status}")
        else:
            self.file_status_label.setText("Status: No File")

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events for the main window."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events for the main window."""
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.open_file(file_path)

    def editor_dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events for the editor."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def editor_dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events for the editor."""
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.open_file(file_path)

    def undo(self) -> None:
        """Undo the last action in the current editor."""
        editor = self.get_current_editor()
        if editor:
            editor.undo()

    def redo(self) -> None:
        """Redo the last undone action in the current editor."""
        editor = self.get_current_editor()
        if editor:
            editor.redo()

    def show_find(self) -> None:
        """Show the find dialog."""
        self.find_replace_dialog.show()
        self.find_replace_dialog.replace_input.hide()
        self.find_replace_dialog.replace_button.hide()
        self.find_replace_dialog.replace_all_button.hide()

    def update_menu_state(self) -> None:
        """Update the state of menu items based on current conditions."""
        has_tabs = self.tabs.count() > 0
        current_tab = self.get_current_editor()

        self.save_action.setEnabled(has_tabs)
        self.save_as_action.setEnabled(has_tabs)

        self.close_tab_action.setEnabled(has_tabs)
        self.close_all_action.setEnabled(has_tabs)

        if self.edit_menu:
            for action in self.edit_menu.actions():
                action.setEnabled(has_tabs)

            if current_tab:
                undo_action = (
                    self.edit_menu.actions()[0]
                    if self.edit_menu.actions()
                    else None
                )
                redo_action = (
                    self.edit_menu.actions()[1]
                    if len(self.edit_menu.actions()) > 1
                    else None
                )

                if undo_action:
                    undo_action.setEnabled(
                        current_tab.document().isUndoAvailable()
                    )
                if redo_action:
                    redo_action.setEnabled(
                        current_tab.document().isRedoAvailable()
                    )


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    icon_filename = "app.ico" if sys.platform == "win32" else "app.icns"
    icon_path = resource_path(icon_filename)

    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    app.setStyleSheet(
        """
        QWidget {
            outline: none;
        }
        QPushButton {
            outline: none;
        }
        QLineEdit {
            outline: none;
        }
    """
    )
    QApplication.setWindowIcon(app_icon)

    notepad = Notepad()
    notepad.show()
    sys.exit(app.exec())
