import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
from src.Currency import Currency
from src.Constants import CURRENCY_TYPES

class GastosDB:
    def __init__(self, database):
        self.database = database

    def _connect(self):
        """Private method to connect to the database"""
        return sqlite3.connect(self.database)

    def load_expense_types(self):
        """Load expense types from the database"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT type_name FROM expense_types")
        tipos = cursor.fetchall()
        conn.close()
        return tipos

    def load_expense_data(self, filter_query=""):
        """Load expenses from the database with optional filters"""
        conn = self._connect()
        cursor = conn.cursor()
        query = """
        SELECT expense_types.type_name, gastos.date, gastos.amount, gastos.currency, gastos.invoice_link
        FROM gastos
        JOIN expense_types ON gastos.expense_type = expense_types.val
        WHERE 1=1
        """ + filter_query
        cursor.execute(query)
        expenses = cursor.fetchall()
        conn.close()
        return expenses

    def add_expense(self, tipo, fecha, monto, factura, moneda):
        """Add an expense to the database"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT val FROM expense_types WHERE type_name = ?", (tipo,))
        tipo_id = cursor.fetchone()[0]
        cursor.execute("""
        INSERT INTO gastos (amount, invoice_number, payment_state, concept, invoice_link, date, expense_type, currency)
        VALUES (?, ?, 'pending', ?, ?, ?, ?, ?)
        """, (monto, 0, tipo, factura, fecha, tipo_id, moneda))
        conn.commit()
        conn.close()

    def get_total_expenses(self, filter_query=""):
        """Get the total expenses with an optional filter"""
        conn = self._connect()
        query = f"""
        SELECT expense_types.type_name, gastos.amount, gastos.currency
        FROM gastos
        JOIN expense_types ON gastos.expense_type = expense_types.val
        WHERE 1=1
        """ + filter_query
        df_expenses = pd.read_sql_query(query, conn)
        conn.close()
        return df_expenses
    
    def get_upcoming_payments(self, head=5):
        conn = self._connect()
        cursor = conn.cursor()
        query = """
            SELECT concept, amount, date, invoice_number, currency
            FROM gastos
            WHERE payment_state = 'pending'
              AND date >= DATE('now')
            ORDER BY date ASC
        """
        cursor.execute(query)
        upcoming_dates = cursor.fetchall()
        conn.close()
        return upcoming_dates[:head]
    
    def get_basic_data(self):
        """Get basic expense data"""
        conn = self._connect()
        query = """
        SELECT strftime('%Y', date) as year, 
               SUM(amount) as total_expenses, 
               expense_types.type_name, 
               SUM(amount) as type_total,
               currency
        FROM gastos
        JOIN expense_types ON gastos.expense_type = expense_types.val
        GROUP BY year, expense_types.type_name, currency
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            df['type_total'] = df.apply(lambda x: Currency(x['type_total'], x['currency']).convert(), axis=1)
            df['total_expenses'] = df.apply(lambda x: Currency(x['total_expenses'], x['currency']).convert(), axis=1)
            df = df.groupby(['year', 'type_name']).sum().reset_index()
            df = df.round(2)
        
        result = {}
        for year in df['year'].unique():
            year_data = df[df['year'] == year]
            total_expenses = year_data['total_expenses'].sum()
            total_expenses = round(total_expenses, 2)
            expenses_distribution = year_data[['type_name', 'type_total']].set_index('type_name').to_dict()['type_total']
            result[year] = {
                'Total Expenses': f"{total_expenses} {Currency.current_currency}",
                'Expenses Distribution': {k: f"{v} {Currency.current_currency}" for k, v in expenses_distribution.items()}
            }
        
        return str(result)



class PaginaGastosGenerales:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.db = GastosDB("genericos.db")
        
        # Main frame
        self.main_frame = tk.Frame(self.parent_frame, bg="#2F2F3F")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = tk.Label(self.main_frame, text="General Expenses", fg="white", bg="#2F2F3F", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)

        # Frame for input fields
        self.input_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.input_frame.pack(fill=tk.X, pady=10)

        # Labels and input fields
        self.type_label = tk.Label(self.input_frame, text="Expense Type:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.type_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.expense_type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(self.input_frame, textvariable=self.expense_type_var, state="readonly", font=("Arial", 12))
        self.type_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.date_label = tk.Label(self.input_frame, text="Date (YYYY-MM-DD):", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.date_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.date_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        self.amount_label = tk.Label(self.input_frame, text="Amount:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.amount_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.amount_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        self.invoice_label = tk.Label(self.input_frame, text="Invoice Link:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.invoice_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.invoice_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.invoice_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.currency_label = tk.Label(self.input_frame, text="Currency:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.currency_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        self.currency_var = tk.StringVar()
        self.currency_combobox = ttk.Combobox(self.input_frame, textvariable=self.currency_var, state="readonly", font=("Arial", 12))
        self.currency_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self.currency_combobox['values'] = CURRENCY_TYPES  # Example currencies

        # Button to add expense
        self.add_button = tk.Button(self.input_frame, text="Add Expense", command=self.add_expense, bg="#2196F3", fg="white", font=("Arial", 12))
        self.add_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Frame for expense search
        self.search_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.search_frame.pack(fill=tk.X, pady=10)

        self.search_label = tk.Label(self.search_frame, text="Search Expenses", fg="white", bg="#2F2F3F", font=("Arial", 16, "bold"))
        self.search_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Search fields with labels
        self.search_type_label = tk.Label(self.search_frame, text="Expense Type:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_type_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.search_type_var = tk.StringVar()
        self.search_type_combobox = ttk.Combobox(self.search_frame, textvariable=self.search_type_var, state="readonly", font=("Arial", 12))
        self.search_type_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.load_expense_types()  # Load expense types into the search combobox

        self.search_date_label = tk.Label(self.search_frame, text="Date (YYYY-MM-DD):", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_date_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        
        self.search_date_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.search_date_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")

        self.search_amount_label = tk.Label(self.search_frame, text="Amount:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_amount_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.search_amount_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.search_amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.search_invoice_label = tk.Label(self.search_frame, text="Invoice Link:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_invoice_label.grid(row=2, column=2, padx=10, pady=5, sticky="w")
        
        self.search_invoice_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.search_invoice_entry.grid(row=2, column=3, padx=10, pady=5, sticky="w")

        self.search_currency_label = tk.Label(self.search_frame, text="Currency:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_currency_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.search_currency_var = tk.StringVar()
        self.search_currency_combobox = ttk.Combobox(self.search_frame, textvariable=self.search_currency_var, state="readonly", font=("Arial", 12))
        self.search_currency_combobox.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.search_currency_combobox['values'] = ["ALL"] + CURRENCY_TYPES  # Example currencies

        # Button to perform search
        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search_expenses, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.search_button.grid(row=4, column=0, columnspan=4, pady=10)

        # Frame for expense table
        self.table_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Expense table
        self.tree = ttk.Treeview(self.table_frame, columns=("Type", "Date", "Amount", "Currency", "Invoice"), show="headings", height=8)
        self.tree.heading("Type", text="Type")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Currency", text="Currency")
        self.tree.heading("Invoice", text="Invoice")
        
        self.tree.column("Type", width=150, anchor="w")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Amount", width=100, anchor="e")
        self.tree.column("Currency", width=100, anchor="center")
        self.tree.column("Invoice", width=200, anchor="w")
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Label for total expenses
        self.total_label = tk.Label(self.main_frame, text="Total Expenses: $0", fg="white", bg="#2F2F3F", font=("Arial", 14, "bold"))
        self.total_label.pack(pady=10)

        # Load initial data
        self.load_expense_data()

    def load_expense_types(self):
        """Load expense types into the combobox"""
        types = self.db.load_expense_types()
        self.type_combobox['values'] = [tipo[0] for tipo in types]
        self.search_type_combobox['values'] = [''] + [tipo[0] for tipo in types]

    def load_expense_data(self, filter_query=""):
        """Load expenses into the table with optional filters"""
        expenses = self.db.load_expense_data(filter_query)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for expense in expenses:
            self.tree.insert("", "end", values=expense)
        self.update_total(filter_query)

    def search_expenses(self):
        """Search expenses with provided filters and update the total"""
        filters = []
        tipo = self.search_type_var.get()
        fecha = self.search_date_entry.get()
        monto = self.search_amount_entry.get()
        factura = self.search_invoice_entry.get()
        moneda = self.search_currency_var.get()
        if tipo:
            filters.append(f"expense_types.type_name LIKE '%{tipo}%'")
        if fecha:
            filters.append(f"gastos.date LIKE '{fecha}%'")
        if monto:
            filters.append(f"gastos.amount = {monto}")
        if factura:
            filters.append(f"gastos.invoice_link LIKE '%{factura}%'")
        if moneda and moneda != "ALL":
            filters.append(f"gastos.currency = '{moneda}'")
        filter_query = " AND ".join(filters)
        self.load_expense_data(f" AND {filter_query}" if filter_query else "")

    def add_expense(self):
        """Add an expense and update the table"""
        tipo = self.expense_type_var.get()
        fecha = self.date_entry.get()
        monto = self.amount_entry.get()
        factura = self.invoice_entry.get()
        moneda = self.currency_var.get()
        if tipo and fecha and monto and factura and moneda:
            self.db.add_expense(tipo, fecha, monto, factura, moneda)
            self.load_expense_data()
            self.clear_entries()

    def update_total(self, filter_query=""):
        """Update the total expenses with an optional filter"""
        df_expenses = self.db.get_total_expenses(filter_query)
        if not df_expenses.empty:
            df_expenses['amount'] = df_expenses.apply(lambda x: Currency(x['amount'], x['currency']).convert(), axis=1)
            total = df_expenses['amount'].sum()
        else:
            total = 0
        self.total_label.config(text=f"Total Expenses: {round(total, 2)} {Currency.current_currency}")
        self.total_label.update()

    def clear_entries(self):
        """Clear the input fields"""
        self.date_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.invoice_entry.delete(0, tk.END)
        self.currency_combobox.set("")


    def update_currency(self):
        """Update the view when the currency changes"""
        self.update_total()

# Create the window and the class
if __name__ == "__main__":
    root = tk.Tk()
    general_expenses_page = PaginaGastosGenerales(root)
    print(general_expenses_page.db.get_basic_data())
    root.mainloop()




