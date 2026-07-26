import mysql.connector

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",       # Your MySQL username
    "password": "2505",   # Your MySQL password
    "database": "student_db"
}

def get_db_connection():
    """Establishes and returns a fresh connection to MySQL."""
    return mysql.connector.connect(**DB_CONFIG)

class Database:
    def __init__(self):
        self.create_table()

    def create_table(self):
        """Creates the expenses table if it does not exist."""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            amount DECIMAL(10, 2) NOT NULL,
            category VARCHAR(100) NOT NULL,
            date DATE NOT NULL,
            payment_method VARCHAR(50) NOT NULL
        )
        """
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()

    def insert_expense(self, amount, category, date, payment_method):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO expenses (amount, category, date, payment_method) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (amount, category, date, payment_method))
        conn.commit()
        cursor.close()
        conn.close()

    def fetch_all(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount, category, date, payment_method FROM expenses ORDER BY date DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def delete_expense(self, expense_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "DELETE FROM expenses WHERE id = %s"
        cursor.execute(query, (expense_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def update_expense(self, expense_id, amount, category, date, payment_method):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        UPDATE expenses 
        SET amount = %s, category = %s, date = %s, payment_method = %s 
        WHERE id = %s
        """
        cursor.execute(query, (amount, category, date, payment_method, expense_id))
        conn.commit()
        cursor.close()
        conn.close()

    # --- SQL Aggregations ---
    def get_total_spending(self):
        """Calculates total spending using MySQL SUM()."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM expenses")
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        # MySQL returns Decimal or None for SUM()
        return float(result) if result else 0.0

    def get_spending_by_category(self):
        """Groups expenses by category using SUM() and GROUP BY."""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        SELECT category, SUM(amount) 
        FROM expenses 
        GROUP BY category 
        ORDER BY SUM(amount) DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Convert Decimal values to floats for consistency in Tkinter formatting
        return [(cat, float(amt)) for cat, amt in rows]