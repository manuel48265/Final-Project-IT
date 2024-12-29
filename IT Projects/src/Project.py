import sqlite3
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import MouseEvent
from tkinter import Toplevel, Label

class Proyecto:
    def __init__(self, name, db_path, google_drive_link):
        self.name = name
        self.db_path = db_path
        self.google_drive_link = google_drive_link

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_name(self):
        return self.name

    def calcular_total_ingresos(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM ingresos")
        total_ingresos = cursor.fetchone()[0] or 0
        conn.close()
        return total_ingresos

    def calcular_total_gastos(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM gastos")
        total_gastos = cursor.fetchone()[0] or 0
        conn.close()
        return total_gastos

    def calcular_balance(self):
        total_ingresos = self.calcular_total_ingresos()
        total_gastos = self.calcular_total_gastos()
        return total_ingresos - total_gastos

    def generar_chart(self, periodo='mensual'):
        conn = self._connect()
        ingresos_query = "SELECT date, amount FROM ingresos"
        gastos_query = "SELECT date, amount FROM gastos"
        
        df_ingresos = pd.read_sql_query(ingresos_query, conn)
        df_gastos = pd.read_sql_query(gastos_query, conn)

        df_ingresos['date'] = pd.to_datetime(df_ingresos['date'])
        df_gastos['date'] = pd.to_datetime(df_gastos['date'])

        if periodo == 'mensual':
            df_ingresos['period'] = df_ingresos['date'].dt.to_period('M')
            df_gastos['period'] = df_gastos['date'].dt.to_period('M')
        elif periodo == 'anual':
            df_ingresos['period'] = df_ingresos['date'].dt.to_period('A')
            df_gastos['period'] = df_gastos['date'].dt.to_period('A')

        ingresos = df_ingresos.groupby('period')['amount'].sum()
        gastos = df_gastos.groupby('period')['amount'].sum().abs()

        ingresos.index = ingresos.index.astype(str)
        gastos.index = gastos.index.astype(str)

        df_agg = pd.DataFrame({'Ingresos': ingresos, 'Gastos': gastos})

        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        bars = df_agg.plot(kind='bar', ax=ax, color=['green', 'red'])
        ax.set_title(f'Resumen de {periodo}')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Monto')
        conn.close()

        return fig, ax.patches, df_agg

    def obtener_pagos_pendientes(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT concept, amount, date FROM gastos WHERE payment_state = 'pending' ORDER BY date ASC")
        pagos_pendientes = cursor.fetchall()
        conn.close()
        return pagos_pendientes

class Ventana:
    def __init__(self, root, proyecto):
        self.root = root
        self.proyecto = proyecto
        self.tooltip = None

    def mostrar_chart(self, periodo='mensual'):
        fig, bars, data = self.proyecto.generar_chart(periodo=periodo)
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

        def show_tooltip(event: MouseEvent):
            if event.inaxes:
                for rect, (label, row) in zip(event.inaxes.patches, data.iterrows()):
                    if rect.contains(event)[0]:
                        x_value = label
                        y_value = rect.get_height()
                        print(x_value, y_value)

                        # Determinar si la barra es Ingreso o Gasto
                        is_income = y_value == row["Ingresos"]

                        if self.tooltip:
                            self.tooltip.destroy()

                        # Crear la ventana emergente
                        x_root, y_root = canvas.get_tk_widget().winfo_pointerxy()
                        self.tooltip = Toplevel(self.root)
                        self.tooltip.wm_overrideredirect(True)
                        self.tooltip.geometry(f"+{x_root+15}+{y_root+15}")

                        # Configurar contenido del tooltip
                        tipo = "Ingresos" if is_income else "Gastos"
                        color = "green" if is_income else "red"

                        label = Label(
                            self.tooltip,
                            text=f"{tipo}:\n{x_value}: {y_value}",
                            bg="lightyellow",
                            fg=color,
                            font=("Arial", 10, "bold"),
                            relief="solid",
                            borderwidth=1,
                            padx=10,
                            pady=5,
                        )
                        label.pack()



        def hide_tooltip(event: MouseEvent):
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None


        fig.canvas.mpl_connect('motion_notify_event', show_tooltip)
        fig.canvas.mpl_connect('figure_leave_event', hide_tooltip)

# Ejemplo de uso
if __name__ == "__main__":
    proyecto = Proyecto('Contabilidad', 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id')
    print("Total Ingresos:", proyecto.calcular_total_ingresos())
    print("Total Gastos:", proyecto.calcular_total_gastos())
    print("Balance:", proyecto.calcular_balance())

    from tkinter import Tk

    root = Tk()
    ventana = Ventana(root, proyecto)
    ventana.mostrar_chart(periodo='mensual')
    root.mainloop()


