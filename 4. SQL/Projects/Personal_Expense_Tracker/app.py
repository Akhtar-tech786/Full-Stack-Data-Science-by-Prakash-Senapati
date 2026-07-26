import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from db import Database

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("850x600")

        self.db = Database()
        self.selected_id = None  # Holds the actual MySQL ID

        self.setup_ui()
        self.load_transactions()
        self.update_summary()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---------------- INPUT FORM FRAME ----------------
        form_frame = ttk.LabelFrame(main_frame, text=" Add / Edit Transaction ", padding="10")
        form_frame.pack(fill=tk.X, pady=(0, 10))

        # Inputs
        ttk.Label(form_frame, text="Amount ($):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        categories = ["Food", "Rent & Utilities", "Entertainment", "Transportation", "Shopping", "Other"]
        self.category_cb = ttk.Combobox(form_frame, values=categories, state="readonly")
        self.category_cb.set("Food")
        self.category_cb.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(form_frame)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Payment Method:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        methods = ["Cash", "Credit Card", "Debit Card", "Bank Transfer"]
        self.payment_cb = ttk.Combobox(form_frame, values=methods, state="readonly")
        self.payment_cb.set("Credit Card")
        self.payment_cb.grid(row=1, column=3, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        self.add_btn = ttk.Button(btn_frame, text="Add Transaction", command=self.add_expense)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.update_btn = ttk.Button(btn_frame, text="Update Transaction", command=self.update_expense, state="disabled")
        self.update_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(btn_frame, text="Clear / Deselect", command=self.clear_inputs)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # ---------------- TREEVIEW TABLE FRAME ----------------
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # We keep "db_id" hidden or visible, but display clean row indexing
        columns = ("db_id", "row_num", "amount", "category", "date", "payment_method")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("row_num", text="#")
        self.tree.heading("amount", text="Amount ($)")
        self.tree.heading("category", text="Category")
        self.tree.heading("date", text="Date")
        self.tree.heading("payment_method", text="Payment Method")

        # Hide db_id column from user view, but keep data accessible
        self.tree.column("db_id", width=0, stretch=tk.NO)
        self.tree.column("row_num", width=40, anchor=tk.CENTER)
        self.tree.column("amount", width=100, anchor=tk.E)
        self.tree.column("category", width=150, anchor=tk.W)
        self.tree.column("date", width=120, anchor=tk.CENTER)
        self.tree.column("payment_method", width=150, anchor=tk.W)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bindings for selection and deselection
        self.tree.bind("<ButtonRelease-1>", self.on_select_item)
        self.root.bind("<Escape>", lambda event: self.clear_inputs())  # Press Escape to deselect!

        # Action Buttons
        action_btn_frame = ttk.Frame(main_frame)
        action_btn_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(action_btn_frame, text="Delete Selected Transaction", command=self.delete_expense).pack(side=tk.RIGHT)

        # ---------------- SUMMARY BAR ----------------
        summary_frame = ttk.LabelFrame(main_frame, text=" Financial Summary ", padding="10")
        summary_frame.pack(fill=tk.X)

        self.total_label = ttk.Label(summary_frame, text="Total Spent: $0.00", font=("Arial", 11, "bold"))
        self.total_label.pack(side=tk.LEFT, padx=10)

        self.breakdown_label = ttk.Label(summary_frame, text="Category Breakdown: None", font=("Arial", 9))
        self.breakdown_label.pack(side=tk.RIGHT, padx=10)

    # ==========================================
    # LOGIC METHODS
    # ==========================================
    def validate_inputs(self):
        amount_str = self.amount_entry.get().strip()
        date_str = self.date_entry.get().strip()

        if not amount_str or not date_str:
            messagebox.showerror("Input Error", "Please fill in all required fields.")
            return False

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Input Error", "Amount must be greater than zero.")
                return False
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a valid number.")
            return False

        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format.")
            return False

        return True

    def load_transactions(self):
        """Displays data with sequential row numbers (1, 2, 3...)."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = self.db.fetch_all()
        # enumerate gives us sequential numbers (1, 2, 3...) regardless of DB ID!
        for index, row in enumerate(rows, start=1):
            formatted_amount = f"${row[1]:,.2f}"
            db_id = row[0]
            self.tree.insert("", tk.END, values=(db_id, index, formatted_amount, row[2], row[3], row[4]))

    def update_summary(self):
        total = self.db.get_total_spending()
        self.total_label.config(text=f"Total Spent: ${total:,.2f}")

        breakdown = self.db.get_spending_by_category()
        if breakdown:
            summary_str = " | ".join([f"{cat}: ${amt:,.2f}" for cat, amt in breakdown])
        else:
            summary_str = "No expenses recorded."
        
        self.breakdown_label.config(text=summary_str)

    def add_expense(self):
        if not self.validate_inputs():
            return

        amount = float(self.amount_entry.get().strip())
        category = self.category_cb.get()
        date = self.date_entry.get().strip()
        payment_method = self.payment_cb.get()

        self.db.insert_expense(amount, category, date, payment_method)
        self.clear_inputs()
        self.load_transactions()
        self.update_summary()
        messagebox.showinfo("Success", "Expense added successfully!")

    def on_select_item(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        row_data = item["values"]

        # row_data[0] is hidden db_id
        self.selected_id = row_data[0]
        raw_amount = str(row_data[2]).replace("$", "").replace(",", "")

        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, raw_amount)

        self.category_cb.set(row_data[3])
        
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, row_data[4])

        self.payment_cb.set(row_data[5])

        # Enable Edit Mode
        self.add_btn.config(state="disabled")
        self.update_btn.config(state="normal")

    def update_expense(self):
        if not self.selected_id:
            return
        if not self.validate_inputs():
            return

        amount = float(self.amount_entry.get().strip())
        category = self.category_cb.get()
        date = self.date_entry.get().strip()
        payment_method = self.payment_cb.get()

        self.db.update_expense(self.selected_id, amount, category, date, payment_method)
        self.clear_inputs()
        self.load_transactions()
        self.update_summary()
        messagebox.showinfo("Success", "Expense updated successfully!")

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Row", "Please select a transaction row from the table to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense entry?")
        if confirm:
            db_id = self.tree.item(selected[0])["values"][0]
            self.db.delete_expense(db_id)
            self.clear_inputs()
            self.load_transactions()
            self.update_summary()

    def clear_inputs(self):
        """Clears selection, resets form, and re-enables the Add button."""
        self.selected_id = None
        
        # Deselect any highlighted tree items
        for item in self.tree.selection():
            self.tree.selection_remove(item)

        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.category_cb.set("Food")
        self.payment_cb.set("Credit Card")

        # Re-enable Add button
        self.add_btn.config(state="normal")
        self.update_btn.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()