import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# --- Database Connection Function ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # Replace with your MySQL username
        password="2505",  # Replace with your MySQL password
        database="student_db"
    )

# --- Application Class ---
class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Registration System")
        self.root.geometry("600x500")

        # --- Form Variables ---
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.fee_var = tk.StringVar()

        # --- Form UI (Labels & Entries) ---
        tk.Label(root, text="Student ID").place(x=80, y=30)
        self.txt_id = tk.Entry(root, textvariable=self.id_var, state="readonly") # ID auto-generated or selected
        self.txt_id.place(x=200, y=30, width=150)

        tk.Label(root, text="Name").place(x=80, y=70)
        self.txt_name = tk.Entry(root, textvariable=self.name_var)
        self.txt_name.place(x=200, y=70, width=150)

        tk.Label(root, text="Course").place(x=80, y=110)
        self.txt_course = tk.Entry(root, textvariable=self.course_var)
        self.txt_course.place(x=200, y=110, width=150)

        tk.Label(root, text="Fee").place(x=80, y=150)
        self.txt_fee = tk.Entry(root, textvariable=self.fee_var)
        self.txt_fee.place(x=200, y=150, width=150)

        # --- Action Buttons ---
        btn_add = tk.Button(root, text="Add", width=10, command=self.add_student)
        btn_add.place(x=80, y=200)

        btn_update = tk.Button(root, text="Update", width=10, command=self.update_student)
        btn_update.place(x=240, y=200)

        btn_delete = tk.Button(root, text="Delete", width=10, command=self.delete_student)
        btn_delete.place(x=400, y=200)

        # --- Treeview Table (Display Records) ---
        columns = ("id", "name", "course", "fee")
        self.student_table = ttk.Treeview(root, columns=columns, show="headings")

        # Headings matching your interface
        self.student_table.heading("id", text="id")
        self.student_table.heading("name", text="name")
        self.student_table.heading("course", text="course")
        self.student_table.heading("fee", text="fee")

        # Column Alignments & Widths
        self.student_table.column("id", width=80, anchor="center")
        self.student_table.column("name", width=160, anchor="w")
        self.student_table.column("course", width=120, anchor="w")
        self.student_table.column("fee", width=100, anchor="e")

        self.student_table.place(x=20, y=250, width=560, height=220)

        # Bind row selection to populate entry fields
        self.student_table.bind("<ButtonRelease-1>", self.get_cursor)

        # Load existing database records into UI
        self.fetch_data()

    # --- Database Operations ---

    def add_student(self):
        if self.name_var.get() == "" or self.course_var.get() == "" or self.fee_var.get() == "":
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO students (name, course, fee) VALUES (%s, %s, %s)"
            cursor.execute(query, (self.name_var.get(), self.course_var.get(), self.fee_var.get()))
            conn.commit()
            conn.close()
            self.fetch_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Student record added successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def fetch_data(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            rows = cursor.fetchall()

            # Clear current table view
            self.student_table.delete(*self.student_table.get_children())

            # Repopulate table view
            for row in rows:
                self.student_table.insert("", tk.END, values=row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching data: {e}")

    def get_cursor(self, event):
        """Populates the input fields when a row in the table is clicked."""
        cursor_row = self.student_table.focus()
        contents = self.student_table.item(cursor_row)
        row = contents.get("values")

        if row:
            self.id_var.set(row[0])
            self.name_var.set(row[1])
            self.course_var.set(row[2])
            self.fee_var.set(row[3])

    def update_student(self):
        if self.id_var.get() == "":
            messagebox.showerror("Error", "Select a record to update!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "UPDATE students SET name=%s, course=%s, fee=%s WHERE id=%s"
            cursor.execute(query, (
                self.name_var.get(),
                self.course_var.get(),
                self.fee_var.get(),
                self.id_var.get()
            ))
            conn.commit()
            conn.close()
            self.fetch_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Record updated successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def delete_student(self):
        if self.id_var.get() == "":
            messagebox.showerror("Error", "Select a record to delete!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "DELETE FROM students WHERE id=%s"
            cursor.execute(query, (self.id_var.get(),))
            conn.commit()
            conn.close()
            self.fetch_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Record deleted successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def clear_fields(self):
        self.id_var.set("")
        self.name_var.set("")
        self.course_var.set("")
        self.fee_var.set("")

# --- Run the GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()