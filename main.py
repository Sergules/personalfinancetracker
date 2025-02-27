import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FinanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("1000x600")
        
        self.transactions = []
        self.load_data()
        
        self.create_widgets()
        self.update_balance()
        self.update_treeview()

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="New Transaction")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Transaction Type
        ttk.Label(input_frame, text="Type:").grid(row=0, column=0)
        self.type_var = tk.StringVar()
        ttk.Combobox(input_frame, textvariable=self.type_var, 
                    values=["Income", "Expense"]).grid(row=0, column=1)

        # Amount
        ttk.Label(input_frame, text="Amount:").grid(row=1, column=0)
        self.amount_var = tk.DoubleVar()
        ttk.Entry(input_frame, textvariable=self.amount_var).grid(row=1, column=1)

        # Category
        ttk.Label(input_frame, text="Category:").grid(row=2, column=0)
        self.category_var = tk.StringVar()
        categories = ["Salary", "Rent", "Food", "Transport", "Entertainment", "Utilities"]
        ttk.Combobox(input_frame, textvariable=self.category_var, 
                     values=categories).grid(row=2, column=1)

        # Date
        ttk.Label(input_frame, text="Date:").grid(row=3, column=0)
        self.date_var = tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
        ttk.Entry(input_frame, textvariable=self.date_var).grid(row=3, column=1)

        # Buttons
        ttk.Button(input_frame, text="Add Transaction", 
                  command=self.add_transaction).grid(row=4, columnspan=2)

        # Transaction List
        tree_frame = ttk.Frame(self.root)
        tree_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(tree_frame, columns=("Date", "Type", "Category", "Amount"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.pack(expand=True, fill="both")

        # Balance Display
        balance_frame = ttk.Frame(self.root)
        balance_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.balance_var = tk.StringVar()
        ttk.Label(balance_frame, textvariable=self.balance_var, 
                 font=("Arial", 14, "bold")).pack()

        # Visualization
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Configure grid weights
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

    def add_transaction(self):
        try:
            transaction = {
                "date": self.date_var.get(),
                "type": self.type_var.get(),
                "category": self.category_var.get(),
                "amount": self.amount_var.get()
            }
            
            # Validate inputs
            if not all(transaction.values()):
                raise ValueError("All fields are required")
            if transaction["amount"] <= 0:
                raise ValueError("Amount must be positive")
                
            self.transactions.append(transaction)
            self.update_treeview()
            self.update_balance()
            self.update_chart()
            self.save_data()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for transaction in self.transactions:
            amount = f"${transaction['amount']:.2f}"
            if transaction["type"] == "Expense":
                amount = f"-{amount}"
            self.tree.insert("", "end", values=(
                transaction["date"],
                transaction["type"],
                transaction["category"],
                amount
            ))

    def update_balance(self):
        balance = sum(t["amount"] if t["type"] == "Income" else -t["amount"] 
                     for t in self.transactions)
        self.balance_var.set(f"Current Balance: ${balance:.2f}")

    def update_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Group expenses by category
        expenses = [t for t in self.transactions if t["type"] == "Expense"]
        categories = {}
        for t in expenses:
            categories[t["category"]] = categories.get(t["category"], 0) + t["amount"]
            
        if categories:
            ax.pie(categories.values(), labels=categories.keys(), autopct="%1.1f%%")
            ax.set_title("Expense Distribution")
            self.canvas.draw()

    def load_data(self):
        try:
            with open("transactions.csv", "r") as f:
                reader = csv.DictReader(f)
                self.transactions = [{
                    "date": row["date"],
                    "type": row["type"],
                    "category": row["category"],
                    "amount": float(row["amount"])
                } for row in reader]
        except FileNotFoundError:
            pass

    def save_data(self):
        with open("transactions.csv", "w", newline="") as f:
            fieldnames = ["date", "type", "category", "amount"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.transactions)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTracker(root)
    root.mainloop()