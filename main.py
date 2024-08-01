from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, \
    QLabel, QGridLayout, QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        # Set style
        self.setStyleSheet("background-color: #afb6cc; \
                           color: #2a2c2e")
        self.setMinimumSize(800, 600)

        # Set menu
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        search_menu_item = self.menuBar().addMenu("&Search")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        add_help_action = QAction("Help", self)
        help_menu_item.addAction(add_help_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        search_menu_item.addAction(search_action)

        # Set table
        self.table = QTableWidget()
        self.table.setStyleSheet("background-color: #bec8d1; \
                                   color: #101112")
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone Number"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create Toolbar and elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create Statusbar and elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton(QIcon("icons/edit.png"), "Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton(QIcon("icons/delete.png"), "Delete Record")
        delete_button.clicked.connect(self.delete)

        # Delete buttons
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(250)

        layout = QVBoxLayout()

        # Set layout of dialog
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Art", "Astronomy", "Physics", "Math"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.student_phone = QLineEdit()
        self.student_phone.setPlaceholderText("Phone Number")
        layout.addWidget(self.student_phone)

        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        button.clicked.connect(self.close)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.student_phone.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?,?,?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        student_mng_system.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search")
        self.setFixedWidth(300)
        self.setFixedHeight(150)

        # Set layout of dialog
        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Student Name")
        layout.addWidget(self.student_name)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        search_button.clicked.connect(self.close)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        items = student_mng_system.table.findItems(name, Qt.MatchFlag.MatchFixedString)

        for item in items:
            student_mng_system.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(250)

        layout = QVBoxLayout()

        # Find original data
        index = student_mng_system.table.currentRow()
        student_name = student_mng_system.table.item(index, 1).text()
        course_name = student_mng_system.table.item(index, 2).text()
        student_phone = student_mng_system.table.item(index, 3).text()
        self.student_id = student_mng_system.table.item(index, 0).text()

        # Set layout of dialog
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Art", "Astronomy", "Physics", "Math"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        self.student_phone = QLineEdit(student_phone)
        self.student_phone.setPlaceholderText("Phone Number")
        layout.addWidget(self.student_phone)

        button = QPushButton("Submit")
        button.clicked.connect(self.edit_student)
        button.clicked.connect(self.close)
        layout.addWidget(button)

        self.setLayout(layout)

    def edit_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?,"
                       " course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.student_phone.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        student_mng_system.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        # Set layout
        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete this record?")
        confirmation.setStyleSheet("color: red")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.close)

    def delete_student(self):
        # Get selected record for delete
        index = student_mng_system.table.currentRow()
        student_id = student_mng_system.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?",
                       (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        student_mng_system.load_data()

        self.close()

        # Show confirmation message
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Record was deleted")
        confirmation_widget.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the course "The python mega course".
        Feel free to modify and reuse this app.
        """
        self.setText(content)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    student_mng_system = MainWindow()
    student_mng_system.show()
    student_mng_system.load_data()
    sys.exit(app.exec())