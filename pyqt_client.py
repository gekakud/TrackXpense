import threading
from server import run_server
from data_model import CURRENCY_LIST_REGULAR, CATEGORY_LIST_REGULAR, TAG_LIST_REGULAR
import sys
import requests
from requests.exceptions import ConnectionError
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QTextEdit, QPushButton, QMessageBox, QHBoxLayout, QLabel, QLineEdit, QDialog, QFormLayout, QComboBox


BASE_URL = "http://127.0.0.1:8000"

class AddExpenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add New Expense')
        self.setGeometry(100, 100, 900, 500)
        layout = QFormLayout()

        self.name_field = QLineEdit()
        self.category_field = QComboBox()
        self.category_field.addItems(CATEGORY_LIST_REGULAR)
        self.amount_field = QLineEdit()
        self.currency_field = QComboBox()
        self.currency_field.addItems(CURRENCY_LIST_REGULAR)
        self.tag_field = QComboBox()
        self.tag_field.addItems(TAG_LIST_REGULAR)
        self.notes_field = QLineEdit()

        layout.addRow('Name:', self.name_field)
        layout.addRow('Amount:', self.amount_field)
        layout.addRow('Currency:', self.currency_field)
        layout.addRow('Category:', self.category_field)
        layout.addRow('Tag:', self.tag_field)
        layout.addRow('Notes:', self.notes_field)

        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_expense)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def add_expense(self):
        new_expense = {
            'name': self.name_field.text(),
            'category': self.category_field.currentText(),
            'amount': float(self.amount_field.text()),
            'currency': self.currency_field.currentText(),
            'tag': self.tag_field.currentText(),
            'notes': self.notes_field.text()
        }

        try:
            response = requests.post(f"{BASE_URL}/expenses/", json=new_expense)
            if response.status_code == 201:
                QMessageBox.information(self, 'Success', 'Expense added successfully')
                self.accept()
            else:
                QMessageBox.critical(self, 'Error', 'Failed to add expense')
        except ConnectionError:
            QMessageBox.critical(self, 'Error', 'Failed to connect to the server')


class ExpenseTrackerClient(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Expense Tracker Client')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # List of all expenses
        self.expense_list = QListWidget()
        self.expense_list.itemClicked.connect(self.show_expense_info)
        layout.addWidget(self.expense_list)

        # Expense info display
        self.expense_info = QTextEdit()
        self.expense_info.setReadOnly(True)
        layout.addWidget(self.expense_info)

        # Update expense fields
        self.update_layout = QHBoxLayout()
        self.update_layout.addWidget(QLabel('Name:'))
        self.name_field = QLineEdit()
        self.update_layout.addWidget(self.name_field)
        self.update_layout.addWidget(QLabel('Category:'))
        self.category_field = QLineEdit()
        self.update_layout.addWidget(self.category_field)
        self.update_layout.addWidget(QLabel('Amount:'))
        self.amount_field = QLineEdit()
        self.update_layout.addWidget(self.amount_field)
        self.update_layout.addWidget(QLabel('Currency:'))
        self.currency_field = QLineEdit()
        self.update_layout.addWidget(self.currency_field)
        self.update_layout.addWidget(QLabel('Tag:'))
        self.tag_field = QLineEdit()
        self.update_layout.addWidget(self.tag_field)
        self.update_layout.addWidget(QLabel('Notes:'))
        self.notes_field = QLineEdit()
        self.update_layout.addWidget(self.notes_field)

        layout.addLayout(self.update_layout)

        # Buttons for add, delete, and update
        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton('Add New Expense')
        self.add_button.clicked.connect(self.open_add_expense_dialog)
        self.button_layout.addWidget(self.add_button)

        self.update_button = QPushButton('Update')
        self.update_button.clicked.connect(self.update_expense)
        self.button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_expense)
        self.button_layout.addWidget(self.delete_button)

        self.refresh_button = QPushButton('Refresh Expenses')
        self.refresh_button.clicked.connect(self.load_expenses)
        self.button_layout.addWidget(self.refresh_button)

        layout.addLayout(self.button_layout)

        self.setLayout(layout)

        self.load_expenses()

    def load_expenses(self):
        try:
            self.expense_list.clear()  # Clear the list before adding new items
            response = requests.get(f"{BASE_URL}/expenses/all")
            if response.status_code == 200:
                expenses = response.json()
                
                self.expenses = {expense['id']: expense for expense in expenses}  # Store expenses in a dictionary by ID
                for expense in expenses:
                    self.expense_list.addItem(expense['id'])  # Show ID only
            else:
                QMessageBox.critical(self, 'Error', 'Failed to load expenses')
        except ConnectionError:
            QMessageBox.critical(self, 'Error', 'Failed to connect to the server')

    def show_expense_info(self, item):
        expense_id = item.text()
        expense = self.expenses[expense_id]
        info = f"ID: {expense['id']}\nName: {expense['name']}\nCategory: {expense['category']}\nAmount: {expense['amount']}\nCurrency: {expense['currency']}\nTag: {expense['tag']}\nNotes: {expense['notes']}"
        self.expense_info.setText(info)
        self.name_field.setText(expense['name'])
        self.category_field.setText(expense['category'])
        self.amount_field.setText(str(expense['amount']))
        self.currency_field.setText(expense['currency'])
        self.tag_field.setText(expense['tag'])
        self.notes_field.setText(expense['notes'])
        self.current_expense_id = expense['id']

    def update_expense(self):
        if not hasattr(self, 'current_expense_id'):
            QMessageBox.warning(self, 'Warning', 'No expense selected')
            return

        updated_expense = {
            'name': self.name_field.text(),
            'category': self.category_field.text(),
            'amount': float(self.amount_field.text()),
            'currency': self.currency_field.text(),
            'tag': self.tag_field.text(),
            'notes': self.notes_field.text()
        }

        try:
            response = requests.put(f"{BASE_URL}/expenses/{self.current_expense_id}", json=updated_expense)
            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Expense updated successfully')
                self.load_expenses()
            else:
                QMessageBox.critical(self, 'Error', 'Failed to update expense')
        except ConnectionError:
            QMessageBox.critical(self, 'Error', 'Failed to connect to the server')

    def delete_expense(self):
        if not hasattr(self, 'current_expense_id'):
            QMessageBox.warning(self, 'Warning', 'No expense selected')
            return

        try:
            response = requests.delete(f"{BASE_URL}/expenses/{self.current_expense_id}")
            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Expense deleted successfully')
                self.load_expenses()
                self.expense_info.clear()
            else:
                QMessageBox.critical(self, 'Error', 'Failed to delete expense')
        except ConnectionError:
            QMessageBox.critical(self, 'Error', 'Failed to connect to the server')

    def open_add_expense_dialog(self):
        dialog = AddExpenseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_expenses()

def start_server():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

if __name__ == '__main__':
    # start_server()
    app = QApplication(sys.argv)
    client = ExpenseTrackerClient()
    client.show()
    sys.exit(app.exec_())
