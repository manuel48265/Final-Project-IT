import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from src.Currency import Currency
from src.Project import Proyecto
import sys

# InterfazData class that contains the graphical interface
class InterfazData(tk.Frame):
    def __init__(self, master, proyecto: Proyecto):
        super().__init__(master)
        self.proyecto = proyecto
        self.pack(fill=tk.BOTH, expand=True)
        self.create_interface()

    def create_interface(self):
        self.columnas = {
            "transaction_type": "Transaction Type",
            "amount": "Amount",
            "currency": "Currency",
            "date": "Date",
            "payment_state": "Payment State",
            "invoice_number": "Invoice Number",
            "invoice_link": "Invoice Link",
            "concept": "Concept",
            "type_name": "Type Name"
        }
        self.orden_actual = {col: None for col in self.columnas}

        # Frame for project name
        frame_nombre = tk.Frame(self, padx=10, pady=10)
        frame_nombre.pack(fill=tk.X)
        label_nombre = tk.Label(frame_nombre, text=f"Project: {self.proyecto.name}", font=("Arial", 16))
        label_nombre.pack()

        # Frame to display total balance
        frame_saldo = tk.Frame(self, padx=10, pady=10)
        frame_saldo.pack(fill=tk.X)
        saldo_total = self.proyecto.obtener_saldo_total()
        label_saldo = tk.Label(frame_saldo, text=f"Total Balance: {saldo_total:.2f} {Currency.current_currency}", font=("Arial", 16))
        label_saldo.pack()
        self.label_saldo = label_saldo

        # Frame for dates and update button
        frame_fechas = tk.Frame(self, padx=10, pady=10)
        frame_fechas.pack(fill=tk.X, pady=10)
        frame_fechas.pack_propagate(False)
        frame_fechas.grid_columnconfigure(0, weight=1)
        frame_fechas.grid_columnconfigure(1, weight=1)
        frame_fechas.grid_columnconfigure(2, weight=1)
        frame_fechas.grid_columnconfigure(3, weight=1)

        # Frame for expense charts
        frame_graficos_gastos = tk.Frame(self, padx=10, pady=10)
        frame_graficos_gastos.pack(fill=tk.BOTH, expand=True)
        self.frame_graficos_gastos = frame_graficos_gastos
        self.create_expense_charts(frame_graficos_gastos)

        # Frame for upcoming payments and transactions
        frame_fechas_transacciones = tk.Frame(self, padx=10, pady=10)
        frame_fechas_transacciones.pack(fill=tk.BOTH, expand=True)

        # Frame for upcoming payments
        frame_fechas_futuras = tk.Frame(frame_fechas_transacciones, padx=10, pady=10, width=600)
        frame_fechas_futuras.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        frame_fechas_futuras.pack_propagate(False)
        label_fechas_futuras = tk.Label(frame_fechas_futuras, text="Upcoming Pending Payments", font=("Arial", 14, "bold"))
        label_fechas_futuras.pack()
        self.show_upcoming_dates(frame_fechas_futuras)

        tk.Label(frame_fechas, text="Start Date:").grid(row=0, column=0, sticky=tk.E)
        self.fecha_inicio_entry = tk.Entry(frame_fechas)
        self.fecha_inicio_entry.grid(row=0, column=1, sticky=tk.W)
        tk.Label(frame_fechas, text="End Date:").grid(row=0, column=2, sticky=tk.E)
        self.fecha_fin_entry = tk.Entry(frame_fechas)
        self.fecha_fin_entry.grid(row=0, column=3, sticky=tk.W)
        btn_actualizar = tk.Button(frame_fechas, text="Update", command=self.update_data)
        btn_actualizar.grid(row=0, column=4, sticky=tk.W)

        # Frame for transactions
        frame_transacciones = tk.Frame(frame_fechas_transacciones, padx=10, pady=10, height=200)
        frame_transacciones.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        frame_transacciones.pack_propagate(False)

        self.tree = ttk.Treeview(frame_transacciones, columns=list(self.columnas.keys()), show='headings', height=8)
        for col, text in self.columnas.items():
            self.tree.heading(col, text=text, command=lambda _col=col: self.header_click(_col))
            if col in ["transaction_type", "amount", "currency", "payment_state", "date", "invoice_number"]:
                self.tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(frame_transacciones, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.select_row)

        self.update_treeview("date")

        # Frame for income charts
        frame_graficos_ingresos = tk.Frame(self, padx=10, pady=10)
        frame_graficos_ingresos.pack(fill=tk.BOTH, expand=True)
        self.frame_graficos_ingresos = frame_graficos_ingresos
        self.create_income_charts(frame_graficos_ingresos)

    def show_upcoming_dates(self, frame):
        fechas_futuras = self.proyecto.get_upcoming_payments()
        for fecha in fechas_futuras:
            label = tk.Label(frame, text=f"{fecha[0]}: {fecha[1]} {fecha[4]} - {fecha[2]}", font=("Arial", 12))
            label.pack()

    def create_expense_charts(self, frame):
        # Remove existing charts
        for widget in frame.winfo_children():
            widget.destroy()

        # Expense evolution chart
        evolucion = self.proyecto.obtener_evolucion_gastos()
        if evolucion:
            meses = [fila[0] for fila in evolucion]
            totales = [fila[1] for fila in evolucion]

            fig, ax = plt.subplots(figsize=(5, 3))
            bars_gastos = ax.bar(meses, totales, color='red')
            ax.set_title(f'Expense Evolution ({Currency.current_currency})')
            ax.set_xlabel('Month')
            ax.set_ylabel(f'Total ({Currency.current_currency})')

            canvas1 = FigureCanvasTkAgg(fig, master=frame)
            canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Expense distribution by type chart
        gastos_por_tipo = self.proyecto.obtener_gastos_por_tipo()
        if len(gastos_por_tipo) != 0:
            tipos = [fila[0] for fila in gastos_por_tipo]
            valores = [fila[1] for fila in gastos_por_tipo]

            fig2, ax2 = plt.subplots(figsize=(5, 3))
            ax2.pie(valores, labels=tipos, autopct='%1.1f%%')
            ax2.set_title(f'Expense Distribution ({Currency.current_currency})')

            canvas2 = FigureCanvasTkAgg(fig2, master=frame)
            canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tooltips
        self.tooltip_var = [None]
        if evolucion:
            canvas1.mpl_connect("motion_notify_event", lambda event: self.show_tooltip(event, canvas1, bars_gastos, evolucion, frame, self.tooltip_var, "Expenses"))
            canvas1.mpl_connect("figure_leave_event", lambda event: self.hide_tooltip(event, self.tooltip_var))

        # Save references to the canvases to be able to remove them
        self.canvases = [canvas1, canvas2] if evolucion else []

    def create_income_charts(self, frame):
        # Remove existing charts
        for widget in frame.winfo_children():
            widget.destroy()

        # Income evolution chart
        evolucion_ingresos = self.proyecto.obtener_evolucion_ingresos()
        if evolucion_ingresos:
            meses_ing = [fila[0] for fila in evolucion_ingresos]
            totales_ing = [fila[1] for fila in evolucion_ingresos]

            fig3, ax3 = plt.subplots(figsize=(5, 3))
            bars_ingresos = ax3.bar(meses_ing, totales_ing, color='blue')
            ax3.set_title(f'Income Evolution ({Currency.current_currency})')
            ax3.set_xlabel('Month')
            ax3.set_ylabel(f'Total ({Currency.current_currency})')

            canvas3 = FigureCanvasTkAgg(fig3, master=frame)
            canvas3.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Income distribution by type chart
        ingresos_por_tipo = self.proyecto.obtener_ingresos_por_tipo()
        if len(ingresos_por_tipo) != 0:
            tipos_ing = [fila[0] for fila in ingresos_por_tipo]
            valores_ing = [fila[1] for fila in ingresos_por_tipo]

            fig4, ax4 = plt.subplots(figsize=(5, 3))
            ax4.pie(valores_ing, labels=tipos_ing, autopct='%1.1f%%')
            ax4.set_title(f'Income Distribution ({Currency.current_currency})')

            canvas4 = FigureCanvasTkAgg(fig4, master=frame)
            canvas4.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tooltips
        self.tooltip_var = [None]
        if evolucion_ingresos:
            canvas3.mpl_connect("motion_notify_event", lambda event: self.show_tooltip(event, canvas3, bars_ingresos, evolucion_ingresos, frame, self.tooltip_var, "Income"))
            canvas3.mpl_connect("figure_leave_event", lambda event: self.hide_tooltip(event, self.tooltip_var))

        # Save references to the canvases to be able to remove them
        self.canvases += [canvas3, canvas4] if evolucion_ingresos else []

    def update_treeview(self, orden, ascendente=True):
        for row in self.tree.get_children():
            self.tree.delete(row)
        datos = self.proyecto.obtener_datos(orden, ascendente)
        for fila in datos:
            self.tree.insert("", "end", values=fila)

    def header_click(self, col):
        if col in self.columnas:
            for key in self.orden_actual.keys():
                if key != col:
                    self.orden_actual[key] = None

            if self.orden_actual[col] is None:
                self.orden_actual[col] = True
            elif self.orden_actual[col] is True:
                self.orden_actual[col] = False
            else:
                self.orden_actual[col] = None

            if self.orden_actual[col] is not None:
                self.update_treeview(col, self.orden_actual[col])
            self.update_headers()

    def update_headers(self):
        for col, text in self.columnas.items():
            if self.orden_actual[col] is None:
                self.tree.heading(col, text=text)
            else:
                orden_dir = "\u2191" if self.orden_actual[col] else "\u2193"
                self.tree.heading(col, text=f"{text} {orden_dir}")

    def select_row(self, event):
        item = self.tree.selection()[0]
        fecha = self.tree.item(item, "values")[4]  # The date is in column 4 (index 3)
        print(f"Selected date: {fecha}")

    def show_tooltip(self, event, canvas, bars, data, parent, tooltip_var, tipo):
        if event.inaxes:
            for i, rect in enumerate(bars):
                if rect.contains(event)[0]:
                    row = data[i]
                    if tooltip_var[0]:
                        tooltip_var[0].destroy()
                    x_root, y_root = canvas.get_tk_widget().winfo_pointerxy()
                    tooltip = tk.Toplevel(parent)
                    tooltip.wm_overrideredirect(True)
                    tooltip.geometry(f"+{x_root+15}+{y_root+15}")
                    color = "green" if tipo == "Income" else "red"
                    tk.Label(
                        tooltip,
                        text=f"{tipo}:\n{row[0]}: {round(row[1], 2)} {Currency.current_currency}",
                        bg="lightyellow",
                        fg=color,
                        font=("Arial", 10, "bold"),
                        relief="solid",
                        borderwidth=1,
                        padx=10,
                        pady=5,
                    ).pack()
                    tooltip_var[0] = tooltip
                    break

    def hide_tooltip(self, event, tooltip_var):
        if tooltip_var[0]:
            tooltip_var[0].destroy()
            tooltip_var[0] = None

    def create_charts(self, frame):
        # Remove existing charts
        for widget in frame.winfo_children():
            widget.destroy()

        # Frame for expense charts
        frame_gastos = tk.Frame(frame)
        frame_gastos.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Expense evolution chart
        evolucion = self.proyecto.obtener_evolucion_gastos()
        if evolucion:
            meses = [fila[0] for fila in evolucion]
            totales = [fila[1] for fila in evolucion]

            fig, ax = plt.subplots(figsize=(5, 3))
            bars_gastos = ax.bar(meses, totales, color='red')
            ax.set_title(f'Expense Evolution ({Currency.current_currency})')
            ax.set_xlabel('Month')
            ax.set_ylabel(f'Total ({Currency.current_currency})')

            canvas1 = FigureCanvasTkAgg(fig, master=frame_gastos)
            canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Expense distribution by type chart
        gastos_por_tipo = self.proyecto.obtener_gastos_por_tipo()
        if len(gastos_por_tipo) != 0:
            tipos = [fila[0] for fila in gastos_por_tipo]
            valores = [fila[1] for fila in gastos_por_tipo]

            fig2, ax2 = plt.subplots(figsize=(5, 3))
            ax2.pie(valores, labels=tipos, autopct='%1.1f%%')
            ax2.set_title(f'Expense Distribution ({Currency.current_currency})')

            canvas2 = FigureCanvasTkAgg(fig2, master=frame_gastos)
            canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame for income charts
        frame_ingresos = tk.Frame(frame)
        frame_ingresos.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Income evolution chart
        evolucion_ingresos = self.proyecto.obtener_evolucion_ingresos()
        if evolucion_ingresos:
            meses_ing = [fila[0] for fila in evolucion_ingresos]
            totales_ing = [fila[1] for fila in evolucion_ingresos]

            fig3, ax3 = plt.subplots(figsize=(5, 3))
            bars_ingresos = ax3.bar(meses_ing, totales_ing, color='blue')
            ax3.set_title(f'Income Evolution ({Currency.current_currency})')
            ax3.set_xlabel('Month')
            ax3.set_ylabel(f'Total ({Currency.current_currency})')

            canvas3 = FigureCanvasTkAgg(fig3, master=frame_ingresos)
            canvas3.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Income distribution by type chart
        ingresos_por_tipo = self.proyecto.obtener_ingresos_por_tipo()
        if len(ingresos_por_tipo) != 0:
            tipos_ing = [fila[0] for fila in ingresos_por_tipo]
            valores_ing = [fila[1] for fila in ingresos_por_tipo]

            fig4, ax4 = plt.subplots(figsize=(5, 3))
            ax4.pie(valores_ing, labels=tipos_ing, autopct='%1.1f%%')
            ax4.set_title(f'Income Distribution ({Currency.current_currency})')

            canvas4 = FigureCanvasTkAgg(fig4, master=frame_ingresos)
            canvas4.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tooltips
        self.tooltip_var = [None]
        if evolucion_ingresos:
            canvas3.mpl_connect("motion_notify_event", lambda event: self.show_tooltip(event, canvas3, bars_ingresos, evolucion_ingresos, frame_ingresos, self.tooltip_var, "Income"))
            canvas3.mpl_connect("figure_leave_event", lambda event: self.hide_tooltip(event, self.tooltip_var))
        if evolucion:
            canvas1.mpl_connect("motion_notify_event", lambda event: self.show_tooltip(event, canvas1, bars_gastos, evolucion, frame_gastos, self.tooltip_var, "Expenses"))
            canvas1.mpl_connect("figure_leave_event", lambda event: self.hide_tooltip(event, self.tooltip_var))

        # Save references to the canvases to be able to remove them
        self.canvases = [canvas1, canvas2, canvas3, canvas4] if evolucion and evolucion_ingresos else []

    def update_data(self):
        fecha_inicio = self.fecha_inicio_entry.get()
        fecha_fin = self.fecha_fin_entry.get()
        self.proyecto.set_fechas(fecha_inicio, fecha_fin)
        self.update_treeview("date")
        self.create_expense_charts(self.frame_graficos_gastos)
        self.create_income_charts(self.frame_graficos_ingresos)

    # Event handler to close the window
    def on_closing(self):
        for canvas in self.canvases:
            canvas.get_tk_widget().destroy()
        self.proyecto.conexion.close()
        root.destroy()
        sys.exit()

    def update_currency(self):
        saldo_total = self.proyecto.obtener_saldo_total()
        self.label_saldo.config(text=f"Total Balance: {saldo_total:.2f} {Currency.current_currency}")
        self.create_expense_charts(self.frame_graficos_gastos)
        self.create_income_charts(self.frame_graficos_ingresos)

# Run the program
if __name__ == "__main__":
    root = tk.Tk()

    # Create an instance of the Proyecto class (without graphical interface)
    proyecto_base = Proyecto('Contabilidad', 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id')

    # Pass the Proyecto instance to the InterfazData class
    interface = InterfazData(root, proyecto_base)
    root.protocol("WM_DELETE_WINDOW", interface.on_closing)
    root.mainloop()



