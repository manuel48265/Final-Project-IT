import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from src.Currency import Currency
from src.Project import Proyecto
import sys

# Clase InterfazData que contiene la interfaz gráfica
class InterfazData(tk.Frame):
    def __init__(self, master, proyecto : Proyecto):
        super().__init__(master)
        self.proyecto = proyecto
        self.pack(fill=tk.BOTH, expand=True)
        self.crear_interfaz()

    def crear_interfaz(self):
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

        # Frame para el nombre del proyecto
        frame_nombre = tk.Frame(self, padx=10, pady=10)
        frame_nombre.pack(fill=tk.X)
        label_nombre = tk.Label(frame_nombre, text=f"Proyecto: {self.proyecto.name}", font=("Arial", 16))
        label_nombre.pack()

        # Frame para mostrar el saldo total
        frame_saldo = tk.Frame(self, padx=10, pady=10)
        frame_saldo.pack(fill=tk.X)
        saldo_total = self.proyecto.obtener_saldo_total()
        label_saldo = tk.Label(frame_saldo, text=f"Saldo Total: {saldo_total:.2f} {Currency.current_currency}", font=("Arial", 16))
        label_saldo.pack()

        # Frame para las fechas y botón de actualización
        frame_fechas = tk.Frame(self, padx=10, pady=10)
        frame_fechas.pack(fill=tk.X, pady=10)
        frame_fechas.pack_propagate(False)
        frame_fechas.grid_columnconfigure(0, weight=1)
        frame_fechas.grid_columnconfigure(1, weight=1)
        frame_fechas.grid_columnconfigure(2, weight=1)
        frame_fechas.grid_columnconfigure(3, weight=1)

        tk.Label(frame_fechas, text="Fecha de Inicio:").grid(row=0, column=0, sticky=tk.E)
        self.fecha_inicio_entry = tk.Entry(frame_fechas)
        self.fecha_inicio_entry.grid(row=0, column=1, sticky=tk.W)
        tk.Label(frame_fechas, text="Fecha de Fin:").grid(row=0, column=2, sticky=tk.E)
        self.fecha_fin_entry = tk.Entry(frame_fechas)
        self.fecha_fin_entry.grid(row=0, column=3, sticky=tk.W)
        btn_actualizar = tk.Button(frame_fechas, text="Actualizar", command=self.actualizar_datos)
        btn_actualizar.grid(row=0, column=4, sticky=tk.W)

        # Frame para gráficos
        frame_graficos = tk.Frame(self, padx=10, pady=10)
        frame_graficos.pack(fill=tk.BOTH, expand=True)
        self.frame_graficos = frame_graficos
        self.crear_graficos(frame_graficos)

        # Frame para transacciones
        frame_transacciones = tk.Frame(self, padx=10, pady=10)
        frame_transacciones.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(frame_transacciones, columns=list(self.columnas.keys()), show='headings')
        for col, text in self.columnas.items():
            self.tree.heading(col, text=text, command=lambda _col=col: self.encabezado_click(_col))

        self.tree.pack(expand=True, fill=tk.BOTH)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_fila)

        self.actualizar_treeview("date")

    def actualizar_treeview(self, orden, ascendente=True):
        for row in self.tree.get_children():
            self.tree.delete(row)
        datos = self.proyecto.obtener_datos(orden, ascendente)
        for fila in datos:
            self.tree.insert("", "end", values=fila)

    def encabezado_click(self, col):
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
                self.actualizar_treeview(col, self.orden_actual[col])
            self.actualizar_encabezados()

    def actualizar_encabezados(self):
        for col, text in self.columnas.items():
            if self.orden_actual[col] is None:
                self.tree.heading(col, text=text)
            else:
                orden_dir = "\u2191" if self.orden_actual[col] else "\u2193"
                self.tree.heading(col, text=f"{text} {orden_dir}")

    def seleccionar_fila(self, event):
        item = self.tree.selection()[0]
        fecha = self.tree.item(item, "values")[4]  # La fecha está en la columna 4 (índice 3)
        print(f"Fecha seleccionada: {fecha}")

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
                    color = "green" if tipo == "Ingresos" else "red"
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

    def crear_graficos(self, frame):
        # Eliminar gráficos existentes
        for widget in frame.winfo_children():
            widget.destroy()

        # Frame para gráficos de gastos
        frame_gastos = tk.Frame(frame)
        frame_gastos.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Gráfico de evolución de gastos
        evolucion = self.proyecto.obtener_evolucion_gastos()
        if evolucion:
            meses = [fila[0] for fila in evolucion]
            totales = [fila[1] for fila in evolucion]

            fig, ax = plt.subplots(figsize=(5, 3))
            bars_gastos = ax.bar(meses, totales, color='red')
            ax.set_title(f'Evolución de los Gastos ({Currency.current_currency})')
            ax.set_xlabel('Mes')
            ax.set_ylabel(f'Total ({Currency.current_currency})')

            canvas1 = FigureCanvasTkAgg(fig, master=frame_gastos)
            canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Gráfico de distribución de gastos por tipo
        gastos_por_tipo = self.proyecto.obtener_gastos_por_tipo()
        if len(gastos_por_tipo) != 0:
            tipos = [fila[0] for fila in gastos_por_tipo]
            valores = [fila[1] for fila in gastos_por_tipo]

            fig2, ax2 = plt.subplots(figsize=(5, 3))
            ax2.pie(valores, labels=tipos, autopct='%1.1f%%')
            ax2.set_title(f'Distribución de Gastos ({Currency.current_currency})')

            canvas2 = FigureCanvasTkAgg(fig2, master=frame_gastos)
            canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame para gráficos de ingresos
        frame_ingresos = tk.Frame(frame)
        frame_ingresos.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Gráfico de evolución de los Ingresos
        evolucion_ingresos = self.proyecto.obtener_evolucion_ingresos()
        if evolucion_ingresos:
            meses_ing = [fila[0] for fila in evolucion_ingresos]
            totales_ing = [fila[1] for fila in evolucion_ingresos]

            fig3, ax3 = plt.subplots(figsize=(5, 3))
            bars_ingresos = ax3.bar(meses_ing, totales_ing, color='blue')
            ax3.set_title(f'Evolución de los Ingresos ({Currency.current_currency})')
            ax3.set_xlabel('Mes')
            ax3.set_ylabel(f'Total ({Currency.current_currency})')

            canvas3 = FigureCanvasTkAgg(fig3, master=frame_ingresos)
            canvas3.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Gráfico de distribución de Ingresos por tipo
        ingresos_por_tipo = self.proyecto.obtener_ingresos_por_tipo()
        if len(ingresos_por_tipo) != 0:
            tipos_ing = [fila[0] for fila in ingresos_por_tipo]
            valores_ing = [fila[1] for fila in ingresos_por_tipo]

            fig4, ax4 = plt.subplots(figsize=(5, 3))
            ax4.pie(valores_ing, labels=tipos_ing, autopct='%1.1f%%')
            ax4.set_title(f'Distribución de Ingresos ({Currency.current_currency})')

            canvas4 = FigureCanvasTkAgg(fig4, master=frame_ingresos)
            canvas4.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tooltips
        self.tooltip_var = [None]
        if evolucion_ingresos:
            canvas3.mpl_connect("motion_notify_event", lambda event: self.show_tooltip(event, canvas3, bars_ingresos, evolucion_ingresos, frame_ingresos, self.tooltip_var, "Ingresos"))
            canvas3.mpl_connect("figure_leave_event", lambda event: self.hide_tooltip(event, self.tooltip_var))
        if evolucion:
            canvas1.mpl_connect("motion_notify_event", lambda event: self.show_tooltip(event, canvas1, bars_gastos, evolucion, frame_gastos, self.tooltip_var, "Gastos"))
            canvas1.mpl_connect("figure_leave_event", lambda event: self.hide_tooltip(event, self.tooltip_var))

        # Guardar referencias a los canvas para poder eliminarlos
        self.canvases = [canvas1, canvas2, canvas3, canvas4] if evolucion and evolucion_ingresos else []

    def actualizar_datos(self):
        fecha_inicio = self.fecha_inicio_entry.get()
        fecha_fin = self.fecha_fin_entry.get()
        self.proyecto.set_fechas(fecha_inicio, fecha_fin)
        self.actualizar_treeview("date")
        self.crear_graficos(self.frame_graficos)

    # Manejador de evento para cerrar la ventana
    def on_closing(self):
        for canvas in self.canvases:
            canvas.get_tk_widget().destroy()
        self.proyecto.conexion.close()
        root.destroy()
        sys.exit()

# Ejecutar el programa
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gestión de Ingresos y Gastos")

    # Crear una instancia de la clase Proyecto (sin interfaz gráfica)
    proyecto_base = Proyecto('Contabilidad', 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id')

    # Pasar la instancia de Proyecto a la clase InterfazData
    interfaz = InterfazData(root, proyecto_base)
    root.protocol("WM_DELETE_WINDOW", interfaz.on_closing)
    root.mainloop()



