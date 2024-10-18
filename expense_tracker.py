import sqlite3
from datetime import datetime
import pandas as pd
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt

conn = sqlite3.connect('expenses.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                description TEXT,
                date TEXT
            )''')
conn.commit()

class ExpenseTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Personal Expense Tracker")
        self.setGeometry(200, 200, 1000, 600) 
        
        self.layout = QGridLayout()
        
        self.amount_label = QLabel("Amount:")
        self.amount_input = QLineEdit()

        self.category_label = QLabel("Category:")
        self.category_input = QLineEdit()

        self.description_label = QLabel("Description:")
        self.description_input = QLineEdit()

        self.add_button = QPushButton("Add Expense")
        self.add_button.clicked.connect(self.add_expense)

        self.view_button = QPushButton("Show Expenses")
        self.view_button.clicked.connect(self.view_expenses)

        self.summary_button = QPushButton("Generate Summary")
        self.summary_button.clicked.connect(self.generate_summary)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)

        self.table_widget = None

        self.layout.addWidget(self.amount_label, 0, 0)
        self.layout.addWidget(self.amount_input, 0, 1)
        self.layout.addWidget(self.category_label, 1, 0)
        self.layout.addWidget(self.category_input, 1, 1)
        self.layout.addWidget(self.description_label, 2, 0)
        self.layout.addWidget(self.description_input, 2, 1)
        self.layout.addWidget(self.add_button, 3, 0, 1, 2)
        self.layout.addWidget(self.view_button, 4, 0, 1, 2)
        self.layout.addWidget(self.summary_button, 5, 0, 1, 2)
        self.layout.addWidget(self.output_area, 6, 0, 1, 2)

        self.setLayout(self.layout)

    def add_expense(self):
        amount = self.amount_input.text()
        category = self.category_input.text()
        description = self.description_input.text()
        date = datetime.now().strftime("%Y-%m-%d")

        if not amount or not category:
            QMessageBox.warning(self, "Input Error", "Please enter both amount and category.")
            return

        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a valid number.")
            return

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()

        c.execute('''INSERT INTO expenses (amount, category, description, date)
                     VALUES (?, ?, ?, ?)''', (amount, category, description, date))

        conn.commit()
        conn.close()

        self.output_area.setText(f"Added: {amount} | {category} | {description} | {date}")
        self.clear_fields()

    def clear_fields(self):
        self.amount_input.clear()
        self.category_input.clear()
        self.description_input.clear()

    def view_expenses(self):
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()

        c.execute('SELECT * FROM expenses')
        rows = c.fetchall()

        if self.table_widget:
            self.layout.removeWidget(self.table_widget)
            self.table_widget.deleteLater()
            self.table_widget = None

        if not rows:
            self.output_area.setText("No expenses recorded.")
            return

        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['ID', 'Amount', 'Category', 'Description', 'Date'])

        for i, row in enumerate(rows):
            for j, item in enumerate(row):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(item)))

        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()

        self.layout.addWidget(self.table_widget, 7, 0, 1, 2)

        conn.close()

    def generate_summary(self):
        conn = sqlite3.connect('expenses.db')

        df = pd.read_sql_query("SELECT * FROM expenses", conn)
        conn.close()

        if self.table_widget:
            self.layout.removeWidget(self.table_widget)
            self.table_widget.deleteLater()
            self.table_widget = None

        if df.empty:
            self.output_area.setText("No expenses to summarize.")
        else:
            df['date'] = pd.to_datetime(df['date'])
            summary = df.groupby('category')['amount'].sum()

            output = "Expense Summary by Category:\n"
            for category, amount in summary.items():
                output += f"{category}: {amount:.2f}\n"

            self.output_area.setText(output)

def main():
    app = QApplication([])
    window = ExpenseTrackerApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
