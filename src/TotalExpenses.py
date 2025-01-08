import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
from src.Currency import Currency
from src.Constants import CURRENCY_TYPES


class PaginaTransacciones:
    def __init__(self, parent_frame, projects):
        self.projects = projects
        self.parent_frame = parent_frame
        self.main_frame = tk.Frame(self.parent_frame, bg="#2F2F3F")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self._setup_ui()
        self.buscar_transacciones()

    def _setup_ui(self):
        """Set up the graphic interface."""
        self.title_label = tk.Label(self.main_frame, text="Total Transactions", fg="white",
                                    bg="#2F2F3F", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)

        self._setup_search_ui()
        self._setup_table()

        self.total_label = tk.Label(self.main_frame, fg="white", bg="#2F2F3F", font=("Arial", 14))
        self.total_label.pack(anchor="e")

        self.main_frame.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Handle the resizing of the main frame."""
        self._resize_table_columns()

    def _resize_table_columns(self):
        """Resize the table columns based on the current width of the table frame."""
        total_width = self.table_frame.winfo_width()
        column_widths = {
            "date": int(total_width * 0.1), "concept": int(total_width * 0.18),
            "type": int(total_width * 0.1), "amount": int(total_width * 0.1),
            "currency": int(total_width * 0.08), "invoice": int(total_width * 0.08),
            "pstatus": int(total_width * 0.12)
        }

        for col, width in column_widths.items():
            self.tree.column(col, width=width)

    def _setup_search_ui(self):
        """Set up the search interface."""
        self.search_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.search_frame.pack(fill=tk.X, pady=10)

        # Search fields
        tk.Label(self.search_frame, text="Start Date:", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.search_frame, text="End Date:", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.end_date_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        tk.Label(self.search_frame, text="Type (Income/Expense):", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.tipo_var = tk.StringVar()
        self.tipo_combobox = ttk.Combobox(self.search_frame, textvariable=self.tipo_var,
                                          values=["", "Income", "Expense"], state="readonly", font=("Arial", 12))
        self.tipo_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.search_frame, text="Project:", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.project_var = tk.StringVar()
        self.project_combobox = ttk.Combobox(self.search_frame, textvariable=self.project_var,
                                             values=[""] + [p.name for p in self.projects] + ["General"], state="readonly", font=("Arial", 12))
        self.project_combobox.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        tk.Label(self.search_frame, text="Min Amount:", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.min_amount_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.min_amount_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.search_frame, text="Max Amount:", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.max_amount_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.max_amount_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        tk.Label(self.search_frame, text="Currency:", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.currency_var = tk.StringVar()
        self.currency_combobox = ttk.Combobox(self.search_frame, textvariable=self.currency_var,
                                              values=[""] + CURRENCY_TYPES, state="readonly", font=("Arial", 12))
        self.currency_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.search_frame, text="Payment Status:", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.pstatus_var = tk.StringVar()
        self.pstatus_combobox = ttk.Combobox(self.search_frame, textvariable=self.pstatus_var,
                                             values=["", "paid", "pending"], state="readonly", font=("Arial", 12))
        self.pstatus_combobox.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        # Search button
        buscar_btn = tk.Button(self.search_frame, text="Search", command=self.buscar_transacciones,
                               bg="#4CAF50", fg="white", font=("Arial", 12))
        buscar_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Clear filters button
        clear_btn = tk.Button(self.search_frame, text="Clear Filters", command=self.limpiar_filtros,
                              bg="#F44336", fg="white", font=("Arial", 12))
        clear_btn.grid(row=4, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        for i in range(4):
            self.search_frame.grid_columnconfigure(i, weight=1)

    def _setup_table(self):
        """Set up the transactions table."""
        self.table_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("date", "concept", "type", "amount", "currency", "invoice", "pstatus")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=10)
        self._resize_table_columns()

        for col in columns:
            self.tree.heading(col, text=col.capitalize())

        self.tree.pack(fill=tk.BOTH, expand=True)

    def buscar_transacciones(self):
        """Search transactions and update the table."""
        df_final = self._obtener_transacciones()
        self._actualizar_tabla(df_final)
        self._actualizar_total(df_final)

    def _obtener_transacciones(self):
        """Retrieve transactions from the projects and generic databases."""
        rows = []
        filters = self._obtener_filtros()

        for proyecto in self.projects:
            try:
                conn = sqlite3.connect(proyecto.db_path)
                df_p = pd.read_sql_query("""
                    SELECT date, 'Income' as type, amount, currency,
                           '-' as invoice_number, '-' as payment_state
                    FROM ingresos
                    UNION ALL
                    SELECT date, 'Expense' as type, amount, currency,
                           COALESCE(invoice_number, '-') as invoice_number,
                           COALESCE(payment_state, '-') as payment_state
                    FROM gastos
                """, conn)
                conn.close()
                df_p["concept"] = proyecto.name
                rows.append(df_p)
            except sqlite3.Error as e:
                print(f"Error accessing the project's database {proyecto.name}: {e}")

        try:
            conn_gen = sqlite3.connect("genericos.db")
            df_gen = pd.read_sql_query("""
                SELECT date, 'Expense' as type, amount, currency,
                       COALESCE(invoice_number, '-') as invoice_number,
                       COALESCE(payment_state, '-') as payment_state
                FROM gastos
            """, conn_gen)
            conn_gen.close()
            df_gen["concept"] = "General"
            rows.append(df_gen)
        except sqlite3.Error as e:
            print(f"Error accessing the generic database: {e}")

        df_final = pd.concat(rows, ignore_index=True)
        if filters:
            query = " and ".join(filters)
            df_final = df_final.query(query)

        return df_final.sort_values(by="date", ascending=False)

    def _obtener_filtros(self):
        """Generate filters according to search values."""
        filters = []
        if self.start_date_entry.get():
            filters.append(f"date >= '{self.start_date_entry.get()}'")
        if self.end_date_entry.get():
            filters.append(f"date <= '{self.end_date_entry.get()}'")
        if self.tipo_var.get():
            filters.append(f"type == '{self.tipo_var.get()}'")
        if self.project_var.get():
            filters.append(f"concept == '{self.project_var.get()}'")
        if self.min_amount_entry.get():
            filters.append(f"amount >= {self.min_amount_entry.get()}")
        if self.max_amount_entry.get():
            filters.append(f"amount <= {self.max_amount_entry.get()}")
        if self.currency_var.get():
            filters.append(f"currency == '{self.currency_var.get()}'")
        if self.pstatus_var.get():
            filters.append(f"payment_state == '{self.pstatus_var.get()}'")
        return filters

    def _actualizar_tabla(self, df_final):
        """Fill the table with transaction data."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        if df_final.empty:
            return

        for _, row in df_final.iterrows():
            self.tree.insert("", "end", values=(
                row["date"], row["concept"], row["type"], row["amount"],
                row["currency"], row["invoice_number"], row["payment_state"]
            ))

    def _actualizar_total(self, df_final):
        """Calculate and display the adjusted total."""
        if df_final.empty:
            self.total_label.config(text="Total: 0.00" + Currency.current_currency)
        else:    
            df_final["converted"] = df_final.apply(
                lambda x: Currency(x["amount"], x["currency"]).convert(), axis=1
            )
            df_final["adjusted_amount"] = df_final.apply(
                lambda x: x["converted"] if x["type"] == "Income" else -x["converted"], axis=1
            )
            total = df_final["adjusted_amount"].sum()
            self.total_label.config(text=f"Total: {round(total, 2)} {Currency.current_currency}")

    def update_currency(self):
        self._actualizar_total(self._obtener_transacciones())

    def limpiar_filtros(self):
        """Clear all filters and show all transactions."""
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self.tipo_var.set("")
        self.project_var.set("")
        self.min_amount_entry.delete(0, tk.END)
        self.max_amount_entry.delete(0, tk.END)
        self.currency_var.set("")
        self.pstatus_var.set("")
        self.buscar_transacciones()
