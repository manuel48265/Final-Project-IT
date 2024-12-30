import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
from src.Currency import Currency


class PaginaTransacciones:
    def __init__(self, parent_frame, projects):
        self.projects = projects
        self.parent_frame = parent_frame
        self.main_frame = tk.Frame(self.parent_frame, bg="#2F2F3F")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self._setup_ui()
        self.buscar_transacciones()

    def _setup_ui(self):
        """Configura la interfaz gráfica."""
        self.title_label = tk.Label(self.main_frame, text="Transacciones Totales", fg="white",
                                    bg="#2F2F3F", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)

        self._setup_search_ui()
        self._setup_table()

        self.total_label = tk.Label(self.main_frame, fg="white", bg="#2F2F3F", font=("Arial", 14))
        self.total_label.pack(anchor="e")

    def _setup_search_ui(self):
        """Configura la interfaz de búsqueda."""
        self.search_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.search_frame.pack(fill=tk.X, pady=10)

        # Campos de búsqueda
        tk.Label(self.search_frame, text="Fecha:", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.search_frame, text="Tipo (Income/Expense):", fg="white", bg="#2F2F3F",
                 font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.tipo_var = tk.StringVar()
        self.tipo_combobox = ttk.Combobox(self.search_frame, textvariable=self.tipo_var,
                                          values=["", "Income", "Expense"], state="readonly", font=("Arial", 12))
        self.tipo_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Botón buscar
        buscar_btn = tk.Button(self.search_frame, text="Buscar", command=self.buscar_transacciones,
                               bg="#4CAF50", fg="white", font=("Arial", 12))
        buscar_btn.grid(row=0, column=4, padx=5, pady=5)

    def _setup_table(self):
        """Configura la tabla de transacciones."""
        self.table_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("date", "concept", "type", "amount", "currency", "invoice", "pstatus")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=10)
        column_widths = {
            "date": 100, "concept": 180, "type": 100, "amount": 100,
            "currency": 80, "invoice": 80, "pstatus": 120
        }

        for col, width in column_widths.items():
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=width, anchor="center" if col != "concept" else "w")

        self.tree.pack(fill=tk.BOTH, expand=True)

    def buscar_transacciones(self):
        """Busca transacciones y actualiza la tabla."""
        df_final = self._obtener_transacciones()
        self._actualizar_tabla(df_final)
        self._actualizar_total(df_final)

    def _obtener_transacciones(self):
        """Recupera las transacciones de las bases de datos de proyectos y genéricos."""
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
                print(f"Error al acceder a la base de datos del proyecto {proyecto.name}: {e}")

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
            print(f"Error al acceder a la base de datos genérica: {e}")

        df_final = pd.concat(rows, ignore_index=True)
        if filters:
            query = " and ".join(filters)
            df_final = df_final.query(query)

        return df_final.sort_values(by="date", ascending=False)

    def _obtener_filtros(self):
        """Genera filtros según los valores de búsqueda."""
        filters = []
        if self.date_entry.get():
            filters.append(f"date.str.startswith('{self.date_entry.get()}')")
        if self.tipo_var.get():
            filters.append(f"type == '{self.tipo_var.get()}'")
        return filters

    def _actualizar_tabla(self, df_final):
        """Llena la tabla con los datos de las transacciones."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for _, row in df_final.iterrows():
            self.tree.insert("", "end", values=(
                row["date"], row["concept"], row["type"], row["amount"],
                row["currency"], row["invoice_number"], row["payment_state"]
            ))

    def _actualizar_total(self, df_final):
        """Calcula y muestra el total ajustado."""
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
