from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, \
    QLabel, QGridLayout, QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        # Set style
        self.setStyleSheet("background-color: #afb6cc; \
                           color: #2a2c2e")
        self.setFixedWidth(400)
        self.setFixedHeight(400)

        # Set menu
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        search_menu_item = self.menuBar().addMenu("&Search")

        add_student_action = QAction("Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        add_help_action = QAction("Help", self)
        help_menu_item.addAction(add_help_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        search_action = QAction("Search", self)
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

    def load_data(self):
        connection = sqlite3.connect("database.db")
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
        connection = sqlite3.connect("database.db")
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
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        items = student_mng_system.table.findItems(name, Qt.MatchFlag.MatchFixedString)

        for item in items:
            student_mng_system.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    student_mng_system = MainWindow()
    student_mng_system.show()
    student_mng_system.load_data()
    sys.exit(app.exec())