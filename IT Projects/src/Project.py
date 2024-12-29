import sqlite3
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import MouseEvent
from tkinter import Toplevel, Label
from src.Constants import current_currency
from src.Currency import Currency

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
        ingresos_query = "SELECT amount,currency FROM ingresos"
        df_ingresos = pd.read_sql_query(ingresos_query, conn)
        df_ingresos['amount'] = df_ingresos.apply(lambda x: Currency(x['amount'], x['currency']).convert_to(current_currency).get_amount(), axis=1)
        total_ingresos = df_ingresos['amount'].sum()
        conn.close()
        return total_ingresos

    def calcular_total_gastos(self):
        conn = self._connect()
        gastos_query = "SELECT amount,currency FROM gastos"
        df_gastos = pd.read_sql_query(gastos_query, conn)
        df_gastos['amount'] = df_gastos.apply(lambda x: Currency(x['amount'], x['currency']).convert_to(current_currency).get_amount(), axis=1)
        total_gastos = df_gastos['amount'].sum()
        conn.close()
        return total_gastos

    def calcular_balance(self):
        total_ingresos = self.calcular_total_ingresos()
        total_gastos = self.calcular_total_gastos()
        return total_ingresos - total_gastos

    def generar_chart(self, periodo='mensual'):
        conn = self._connect()
        ingresos_query = "SELECT date, amount,currency FROM ingresos"
        gastos_query = "SELECT date, amount,currency FROM gastos"
        
        df_ingresos = pd.read_sql_query(ingresos_query, conn)
        df_gastos = pd.read_sql_query(gastos_query, conn)

        df_ingresos['date'] = pd.to_datetime(df_ingresos['date'])
        df_gastos['date'] = pd.to_datetime(df_gastos['date'])

        # Convertir a la moneda actual
        df_ingresos['amount'] = df_ingresos.apply(lambda x: Currency(x['amount'], x['currency']).convert_to(current_currency).get_amount(), axis=1)
        df_gastos['amount'] = df_gastos.apply(lambda x: Currency(x['amount'], x['currency']).convert_to(current_currency).get_amount(), axis=1)


        if periodo == 'mensual':
            df_ingresos['period'] = df_ingresos['date'].dt.to_period('M')
            df_gastos['period'] = df_gastos['date'].dt.to_period('M')
        elif periodo == 'anual':
            df_ingresos['period'] = df_ingresos['date'].dt.to_period('Y')
            df_gastos['period'] = df_gastos['date'].dt.to_period('Y')

        ingresos = df_ingresos.groupby('period')['amount'].sum()
        gastos = df_gastos.groupby('period')['amount'].sum().abs()

        ingresos.index = ingresos.index.astype(str)
        gastos.index = gastos.index.astype(str)

        df_agg = pd.DataFrame({'Ingresos': ingresos, 'Gastos': gastos})

        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        width = 0.35  # Ancho de las barras

        # Crear las posiciones para las barras
        pos = range(len(df_agg))

        # Ploteo de las barras de ingresos y gastos
        bars1 = ax.bar([p - width/2 for p in pos], df_agg['Ingresos'], width=width, label='Ingresos', color='green')
        bars2 = ax.bar([p + width/2 for p in pos], df_agg['Gastos'], width=width, label='Gastos', color='red')

        # Configuración del gráfico
        ax.set_title(f'Resumen de {periodo}')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Monto')
        ax.set_xticks(pos)
        ax.set_xticklabels(df_agg.index)
        ax.legend()

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
    def __init__(self, parent, proyecto, periodo='mensual'):
        self.parent = parent  # Ajuste para usar el frame recibido
        self.proyecto = proyecto
        self.tooltip = None
        self.periodo = periodo
        self.chart = None

    def cambiar_periodo(self):
        if self.periodo == 'mensual':
            self.periodo = 'anual'
        else:
            self.periodo = 'mensual'

    def mostrar_chart(self):
        fig, bars, data = self.proyecto.generar_chart(periodo=self.periodo)
        canvas = FigureCanvasTkAgg(fig, master=self.parent)
        canvas.draw()
        canvas.get_tk_widget().pack()  # Se muestra debajo del botón en el mismo frame

        # Separa las barras en dos listas: barras de ingresos y barras de gastos
        n_rows = len(data)
        bars_ingresos = bars[:n_rows]
        bars_gastos = bars[n_rows:]

        def show_tooltip(event: MouseEvent):
            if event.inaxes:
                # Detectar las barras de ingresos
                for i, rect in enumerate(bars_ingresos):
                    if rect.contains(event)[0]:
                        # Obtener la fila correspondiente del DataFrame
                        row = data.iloc[i]
                        if self.tooltip:
                            self.tooltip.destroy()
                        x_root, y_root = canvas.get_tk_widget().winfo_pointerxy()
                        self.tooltip = Toplevel(self.parent)
                        self.tooltip.wm_overrideredirect(True)
                        self.tooltip.geometry(f"+{x_root+15}+{y_root+15}")
                        Label(
                            self.tooltip,
                            text=f"Ingresos:\n{row.name}: {row['Ingresos']}",
                            bg="lightyellow",
                            fg="green",
                            font=("Arial", 10, "bold"),
                            relief="solid",
                            borderwidth=1,
                            padx=10,
                            pady=5,
                        ).pack()

                # Detectar las barras de gastos
                for i, rect in enumerate(bars_gastos):
                    if rect.contains(event)[0]:
                        row = data.iloc[i]
                        if self.tooltip:
                            self.tooltip.destroy()
                        x_root, y_root = canvas.get_tk_widget().winfo_pointerxy()
                        self.tooltip = Toplevel(self.parent)
                        self.tooltip.wm_overrideredirect(True)
                        self.tooltip.geometry(f"+{x_root+15}+{y_root+15}")
                        Label(
                            self.tooltip,
                            text=f"Gastos:\n{row.name}: {row['Gastos']}",
                            bg="lightyellow",
                            fg="red",
                            font=("Arial", 10, "bold"),
                            relief="solid",
                            borderwidth=1,
                            padx=10,
                            pady=5,
                        ).pack()

        def hide_tooltip(event: MouseEvent):
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None

        fig.canvas.mpl_connect('motion_notify_event', show_tooltip)
        fig.canvas.mpl_connect('figure_leave_event', hide_tooltip)

        self.chart = canvas.get_tk_widget()

# Ejemplo de uso
if __name__ == "__main__":
    proyecto = Proyecto('Contabilidad', 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id')
    print("Total Ingresos:", proyecto.calcular_total_ingresos())
    print("Total Gastos:", proyecto.calcular_total_gastos())
    print("Balance:", proyecto.calcular_balance())

    from tkinter import Tk

    root = Tk()
    ventana = Ventana(root, proyecto, 'mensual')
    ventana.mostrar_chart(periodo='mensual')
    root.mainloop()






