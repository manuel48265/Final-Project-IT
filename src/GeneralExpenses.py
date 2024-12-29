import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
from Currency import Currency

class PaginaGastosGenerales:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        # Frame principal
        self.main_frame = tk.Frame(self.parent_frame, bg="#2F2F3F")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        self.title_label = tk.Label(self.main_frame, text="Gastos Generales", fg="white", bg="#2F2F3F", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)

        # Frame para los campos de entrada
        self.input_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.input_frame.pack(fill=tk.X, pady=10)

        # Etiquetas y campos de entrada
        self.type_label = tk.Label(self.input_frame, text="Tipo de Gasto:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.type_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.expense_type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(self.input_frame, textvariable=self.expense_type_var, state="readonly", font=("Arial", 12))
        self.type_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.date_label = tk.Label(self.input_frame, text="Fecha (YYYY-MM-DD):", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.date_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.date_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        self.amount_label = tk.Label(self.input_frame, text="Monto:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.amount_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.amount_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        self.invoice_label = tk.Label(self.input_frame, text="Enlace de Factura:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.invoice_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.invoice_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.invoice_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.currency_label = tk.Label(self.input_frame, text="Moneda:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.currency_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        self.currency_var = tk.StringVar()
        self.currency_combobox = ttk.Combobox(self.input_frame, textvariable=self.currency_var, state="readonly", font=("Arial", 12))
        self.currency_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self.currency_combobox['values'] = ["USD", "EUR", "MXN"]  # Ejemplo de monedas

        # Botón para agregar el gasto
        self.add_button = tk.Button(self.input_frame, text="Agregar Gasto", command=self.agregar_gasto, bg="#2196F3", fg="white", font=("Arial", 12))
        self.add_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Frame para la búsqueda de gastos
        self.search_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.search_frame.pack(fill=tk.X, pady=10)

        self.search_label = tk.Label(self.search_frame, text="Buscar Gastos", fg="white", bg="#2F2F3F", font=("Arial", 16, "bold"))
        self.search_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Campos de búsqueda con sus etiquetas
        self.search_type_label = tk.Label(self.search_frame, text="Tipo de Gasto:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_type_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.search_type_var = tk.StringVar()
        self.search_type_combobox = ttk.Combobox(self.search_frame, textvariable=self.search_type_var, state="readonly", font=("Arial", 12))
        self.search_type_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.cargar_tipos_de_gasto()  # Cargar los tipos de gasto en el combobox de búsqueda

        self.search_date_label = tk.Label(self.search_frame, text="Fecha (YYYY-MM-DD):", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_date_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        
        self.search_date_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.search_date_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")

        self.search_amount_label = tk.Label(self.search_frame, text="Monto:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_amount_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.search_amount_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.search_amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.search_invoice_label = tk.Label(self.search_frame, text="Enlace de Factura:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_invoice_label.grid(row=2, column=2, padx=10, pady=5, sticky="w")
        
        self.search_invoice_entry = tk.Entry(self.search_frame, font=("Arial", 12))
        self.search_invoice_entry.grid(row=2, column=3, padx=10, pady=5, sticky="w")

        self.search_currency_label = tk.Label(self.search_frame, text="Moneda:", fg="white", bg="#2F2F3F", font=("Arial", 12))
        self.search_currency_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.search_currency_var = tk.StringVar()
        self.search_currency_combobox = ttk.Combobox(self.search_frame, textvariable=self.search_currency_var, state="readonly", font=("Arial", 12))
        self.search_currency_combobox.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.search_currency_combobox['values'] = ["", "USD", "EUR", "MXN"]  # Ejemplo de monedas

        # Botón para realizar la búsqueda
        self.search_button = tk.Button(self.search_frame, text="Buscar", command=self.buscar_gastos, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.search_button.grid(row=4, column=0, columnspan=4, pady=10)

        # Frame para la tabla de gastos
        self.table_frame = tk.Frame(self.main_frame, bg="#2F2F3F")
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tabla de gastos
        self.tree = ttk.Treeview(self.table_frame, columns=("Tipo", "Fecha", "Monto", "Moneda", "Factura"), show="headings", height=8)
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Monto", text="Monto")
        self.tree.heading("Moneda", text="Moneda")
        self.tree.heading("Factura", text="Factura")
        
        self.tree.column("Tipo", width=150, anchor="w")
        self.tree.column("Fecha", width=100, anchor="center")
        self.tree.column("Monto", width=100, anchor="e")
        self.tree.column("Moneda", width=100, anchor="center")
        self.tree.column("Factura", width=200, anchor="w")
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Etiqueta para el total de gastos
        self.total_label = tk.Label(self.main_frame, text="Total Gastos: $0", fg="white", bg="#2F2F3F", font=("Arial", 14, "bold"))
        self.total_label.pack(pady=10)

        # Cargar los datos iniciales
        self.cargar_datos_gastos()

    def cargar_tipos_de_gasto(self):
        """Cargar los tipos de gasto desde la base de datos en el combobox"""
        conn = sqlite3.connect("genericos.db")
        cursor = conn.cursor()
        cursor.execute("SELECT type_name FROM expense_types")
        tipos = cursor.fetchall()
        conn.close()

        # Agregar los tipos de gasto al combobox
        self.type_combobox['values'] = [tipo[0] for tipo in tipos]
        self.search_type_combobox['values'] = [''] + [tipo[0] for tipo in tipos]  # También permitir búsqueda por tipo

    def cargar_datos_gastos(self, filter_query=""):
        """Cargar los gastos desde la base de datos en la tabla, con filtros opcionales"""
        conn = sqlite3.connect("genericos.db")
        cursor = conn.cursor()

        query = """
        SELECT expense_types.type_name, gastos.date, gastos.amount, gastos.currency, gastos.invoice_link
        FROM gastos
        JOIN expense_types ON gastos.expense_type = expense_types.val
        WHERE 1=1
        """ + filter_query  # Agregar los filtros al query

        cursor.execute(query)
        gastos = cursor.fetchall()
        conn.close()

        # Limpiar la tabla
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insertar los gastos en la tabla
        for gasto in gastos:
            self.tree.insert("", "end", values=gasto)

        # Calcular y actualizar el total
        self.actualizar_total()

    def buscar_gastos(self):
        """Buscar los gastos con los filtros proporcionados"""
        filters = []

        # Obtener los valores de búsqueda
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
        if moneda:
            filters.append(f"gastos.currency = '{moneda}'")

        filter_query = " AND ".join(filters)
        self.cargar_datos_gastos(f" AND {filter_query}" if filter_query else "")

    def agregar_gasto(self):
        """Agregar un gasto a la base de datos y actualizar la tabla"""
        tipo = self.expense_type_var.get()
        fecha = self.date_entry.get()
        monto = self.amount_entry.get()
        factura = self.invoice_entry.get()
        moneda = self.currency_var.get()

        if tipo and fecha and monto and factura and moneda:
            conn = sqlite3.connect("genericos.db")
            cursor = conn.cursor()

            # Obtener el ID del tipo de gasto
            cursor.execute("SELECT val FROM expense_types WHERE type_name = ?", (tipo,))
            tipo_id = cursor.fetchone()[0]

            # Insertar el gasto en la base de datos
            cursor.execute("""
            INSERT INTO gastos (amount, invoice_number, payment_state, concept, invoice_link, date, expense_type, currency)
            VALUES (?, ?, 'pending', ?, ?, ?, ?, ?)
            """, (monto, 0, tipo, factura, fecha, tipo_id, moneda))

            conn.commit()
            conn.close()

            # Actualizar la tabla y el total
            self.cargar_datos_gastos()
            self.clear_entries()

    def actualizar_total(self):
        """Actualizar el total de los gastos"""
        conn = sqlite3.connect("genericos.db")
        gastos_query = "SELECT amount,currency FROM gastos"
        df_gastos = pd.read_sql_query(gastos_query, conn)
        df_gastos['amount'] = df_gastos.apply(lambda x: Currency(x['amount'], x['currency']).convert(), axis=1)
        total= df_gastos['amount'].sum()
        conn.close()

        self.total_label.config(text=f"Total Gastos: {total} {Currency.current_currency}")

    def clear_entries(self):
        """Limpiar los campos de entrada"""
        self.date_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.invoice_entry.delete(0, tk.END)
        self.currency_combobox.set("")

# Crear la ventana y la clase
#root = tk.Tk()
#pagina_gastos = PaginaGastosGenerales(root)
#root.mainloop()




