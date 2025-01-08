import sqlite3
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import MouseEvent
from tkinter import Toplevel, Label
from src.Currency import Currency

class Proyecto:
    def __init__(self, name, db_path, google_drive_link):
        self.name = name
        self.db_path = db_path
        self.google_drive_link = google_drive_link
        self.conexion = sqlite3.connect(self.db_path)
        self.cursor = self.conexion.cursor()
        self.fecha_inicio = None
        self.fecha_fin = None

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_name(self):
        return self.name
    
    def get_dbpath(self):
        return self.db_path

    def calcular_total_ingresos(self):
        conn = self._connect()
        ingresos_query = "SELECT amount,currency FROM ingresos"
        if self.fecha_inicio and self.fecha_fin:
            ingresos_query += f" WHERE date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"
        df_ingresos = pd.read_sql_query(ingresos_query, conn)
        df_ingresos['amount'] = df_ingresos.apply(lambda x: Currency(x['amount'], x['currency']).convert(), axis=1)
        total_ingresos = df_ingresos['amount'].sum()
        conn.close()
        return total_ingresos

    def calcular_total_gastos(self):
        conn = self._connect()
        gastos_query = "SELECT amount,currency FROM gastos"
        if self.fecha_inicio and self.fecha_fin:
            gastos_query += f" WHERE date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"
        df_gastos = pd.read_sql_query(gastos_query, conn)
        df_gastos['amount'] = df_gastos.apply(lambda x: Currency(x['amount'], x['currency']).convert(), axis=1)
        total_gastos = df_gastos['amount'].sum()
        conn.close()
        return total_gastos

    def calcular_balance(self):
        total_ingresos = self.calcular_total_ingresos()
        total_gastos = self.calcular_total_gastos()
        return total_ingresos - total_gastos

    def obtener_datos(self, orden, ascendente=True):
        orden_dir = "ASC" if ascendente else "DESC"
        consulta = f"""
            SELECT t.transaction_type, t.amount, t.currency, t.date, t.payment_state, 
                   t.invoice_number, t.invoice_link, t.concept, 
                   COALESCE(et.type_name, it.type_name) as type_name
            FROM (
                SELECT id, 'expense' as transaction_type, amount, currency, date, payment_state, 
                       invoice_number, invoice_link, concept, expense_type as type_id
                FROM gastos
                UNION ALL
                SELECT id, 'income' as transaction_type, amount, currency, date, '-' as payment_state, 
                       NULL as invoice_number, '-' as invoice_link, concept, income_type as type_id
                FROM ingresos
            ) t
            LEFT JOIN expense_types et ON (t.transaction_type = 'expense' AND t.type_id = et.val)
            LEFT JOIN income_types it ON (t.transaction_type = 'income' AND t.type_id = it.val)
        """
        if self.fecha_inicio and self.fecha_fin:
            consulta += f" WHERE t.date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"
        consulta += f" ORDER BY {orden} {orden_dir}"
        self.cursor.execute(consulta)
        return self.cursor.fetchall()

    def obtener_saldo_total(self):
        """Get the total balance with currency conversion."""
        consulta = """
            SELECT transaction_type, amount, currency, date
            FROM (
                SELECT 'expense' as transaction_type, amount,date, currency FROM gastos
                UNION ALL
                SELECT 'income' as transaction_type, amount,date, currency FROM ingresos
            )
        """
        if self.fecha_inicio and self.fecha_fin:
            consulta += f" WHERE date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"
        df = pd.read_sql_query(consulta, self.conexion)
        df['amount'] = df.apply(lambda row: Currency(row['amount'], row['currency']).convert(), axis=1)
        saldo = df.apply(lambda row: row['amount'] if row['transaction_type'] == 'income' else -row['amount'], axis=1).sum()
        return saldo

    def obtener_gastos_por_tipo(self):
        consulta = """
            SELECT et.type_name, g.amount, g.currency, g.date
            FROM gastos g
            LEFT JOIN expense_types et ON g.expense_type = et.val
        """
        if self.fecha_inicio and self.fecha_fin:
            consulta += f" WHERE g.date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"
        df = pd.read_sql_query(consulta, self.conexion)
        
        if df.empty:
            return []
        else:
            df['amount'] = df.apply(lambda row: Currency(row['amount'], row['currency']).convert(), axis=1)
            df_grouped = df.groupby('type_name')['amount'].sum().reset_index()
            return df_grouped.values.tolist()

    def obtener_evolucion_gastos(self):
        consulta = """
            SELECT strftime('%Y-%m', date) as mes, amount, currency
            FROM gastos
        """
        if self.fecha_inicio and self.fecha_fin:
            consulta += f" WHERE date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"
        df = pd.read_sql_query(consulta, self.conexion)
        if not df.empty:
            df['amount'] = df.apply(lambda row: Currency(row['amount'], row['currency']).convert(), axis=1)
            df_grouped = df.groupby('mes')['amount'].sum().reset_index()
            return df_grouped.values.tolist()
        return []

    def obtener_ingresos_por_tipo(self):
        """Get the sum of income grouped by type."""
        consulta = """
            SELECT it.type_name, i.amount, i.currency, i.date
            FROM ingresos i
            JOIN income_types it ON i.income_type = it.val
        """
        if self.fecha_inicio and self.fecha_fin:
            consulta += f" WHERE i.date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"
        df = pd.read_sql_query(consulta, self.conexion)
        if not df.empty:
            df['amount'] = df.apply(lambda row: Currency(row['amount'], row['currency']).convert(), axis=1)
            df_grouped = df.groupby('type_name')['amount'].sum().reset_index()
            return df_grouped.values.tolist()
        else: 
            return df

    def obtener_evolucion_ingresos(self):
        """Get the monthly evolution of income."""
        consulta = """
            SELECT strftime('%Y-%m', date) as mes, amount, currency
            FROM ingresos
        """
        if self.fecha_inicio and self.fecha_fin:
            consulta += f" WHERE date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"
        df = pd.read_sql_query(consulta, self.conexion)
        if not df.empty:
            df['amount'] = df.apply(lambda row: Currency(row['amount'], row['currency']).convert(), axis=1)
            df_grouped = df.groupby('mes')['amount'].sum().reset_index()
            return df_grouped.values.tolist()
        return []

    def set_fechas(self, fecha_inicio, fecha_fin):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

    def generar_chart(self, periodo='mensual'):
        conn = self._connect()
        ingresos_query = "SELECT date, amount, currency FROM ingresos"
        gastos_query = "SELECT date, amount, currency FROM gastos"

        if self.fecha_inicio and self.fecha_fin:
            ingresos_query += f" WHERE date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"
            gastos_query += f" WHERE date BETWEEN '{self.fecha_inicio}' AND '{self.fecha_fin}'"

        df_ingresos = pd.read_sql_query(ingresos_query, conn)
        df_gastos = pd.read_sql_query(gastos_query, conn)

        if df_ingresos.empty or df_gastos.empty:
            return None, [], pd.DataFrame()

        df_ingresos['date'] = pd.to_datetime(df_ingresos['date'])
        df_gastos['date'] = pd.to_datetime(df_gastos['date'])

        # Convert to the current currency
        df_ingresos['amount'] = round(df_ingresos.apply(lambda x: Currency(x['amount'], x['currency']).convert(), axis=1), 2)
        df_gastos['amount'] = round(df_gastos.apply(lambda x: Currency(x['amount'], x['currency']).convert(), axis=1), 2)

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
        width = 0.35  # Width of the bars

        # Create positions for the bars
        pos = range(len(df_agg))

        # Plot income and expense bars
        bars1 = ax.bar([p - width/2 for p in pos], df_agg['Ingresos'], width=width, label='Ingresos', color='green')
        bars2 = ax.bar([p + width/2 for p in pos], df_agg['Gastos'], width=width, label='Gastos', color='red')

        # Chart configuration
        ax.set_title(f'Summary of {periodo}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Amount')
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
        fechas_futuras = cursor.fetchall()
        conn.close()
        return fechas_futuras[:head]
    
    def get_accurate_data(self):
        conn = self._connect()
        cursor = conn.cursor()
        
        # Get all available years and months in the database
        cursor.execute("SELECT DISTINCT strftime('%Y-%m', date) as period FROM ingresos UNION SELECT DISTINCT strftime('%Y-%m', date) as period FROM gastos ORDER BY period")
        periods = cursor.fetchall()
        
        data_str = ""
        
        for period in periods:
            year, month = period[0].split('-')
            data_str += f"{year}, {month}\n"
            
            # Get total income for the month and year
            cursor.execute(f"SELECT amount, currency FROM ingresos WHERE strftime('%Y-%m', date) = '{period[0]}'")
            ingresos = cursor.fetchall()
            data_str += "-Total Income:\n"
            if ingresos:
                total_ingresos = round(sum(Currency(ingreso[0], ingreso[1]).convert() for ingreso in ingresos), 2)
                data_str += f"  {total_ingresos} {Currency.current_currency}\n"
            else:
                data_str += "  None\n"
            
            # Get total expenses for the month and year
            cursor.execute(f"SELECT amount, currency FROM gastos WHERE strftime('%Y-%m', date) = '{period[0]}'")
            gastos = cursor.fetchall()
            data_str += "-Total Expenses:\n"
            if gastos:
                total_gastos = round(sum(Currency(gasto[0], gasto[1]).convert() for gasto in gastos), 2)
                data_str += f"  {total_gastos} {Currency.current_currency}\n"
            else:
                data_str += "  None\n"
            
            # Get income distribution by type
            cursor.execute(f"""
                SELECT it.type_name, SUM(i.amount), i.currency
                FROM ingresos i
                JOIN income_types it ON i.income_type = it.val
                WHERE strftime('%Y-%m', i.date) = '{period[0]}'
                GROUP BY it.type_name, i.currency
            """)
            income_distribution = cursor.fetchall()
            data_str += "-Income Distribution:\n"
            if income_distribution:
                for dist in income_distribution:
                    amount = round(Currency(dist[1], dist[2]).convert(), 2)
                    data_str += f"  {dist[0]}: {amount} {Currency.current_currency}\n"
            else:
                data_str += "  None\n"
            
            # Get expense distribution by type
            cursor.execute(f"""
                SELECT et.type_name, SUM(g.amount), g.currency
                FROM gastos g
                LEFT JOIN expense_types et ON g.expense_type = et.val
                WHERE strftime('%Y-%m', g.date) = '{period[0]}'
                GROUP BY et.type_name, g.currency
            """)
            expense_distribution = cursor.fetchall()
            data_str += "-Expenses Distribution:\n"
            if expense_distribution:
                for dist in expense_distribution:
                    amount = round(Currency(dist[1], dist[2]).convert(), 2)
                    data_str += f"  {dist[0]}: {amount} {Currency.current_currency}\n"
            else:
                data_str += "  None\n"
        
        conn.close()
        return data_str
    
    def get_basic_data(self):
        conn = self._connect()
        cursor = conn.cursor()
        
        # Get all available years in the database
        cursor.execute("SELECT DISTINCT strftime('%Y', date) as year FROM ingresos UNION SELECT DISTINCT strftime('%Y', date) as year FROM gastos ORDER BY year")
        years = cursor.fetchall()
        
        data_str = ""
        
        for year in years:
            year = year[0]
            data_str += f"{year}:\n"
            
            # Get total income for the year
            cursor.execute(f"SELECT amount, currency FROM ingresos WHERE strftime('%Y', date) = '{year}'")
            ingresos = cursor.fetchall()
            data_str += "-Total Incomes:\n"
            if ingresos:
                total_ingresos = round(sum(Currency(ingreso[0], ingreso[1]).convert() for ingreso in ingresos), 2)
                data_str += f"  {total_ingresos} {Currency.current_currency}\n"
            else:
                data_str += "  None\n"
            
            # Get total expenses for the year
            cursor.execute(f"SELECT amount, currency FROM gastos WHERE strftime('%Y', date) = '{year}'")
            gastos = cursor.fetchall()
            data_str += "-Total Expenses:\n"
            if gastos:
                total_gastos = round(sum(Currency(gasto[0], gasto[1]).convert() for gasto in gastos), 2)
                data_str += f"  {total_gastos} {Currency.current_currency}\n"
            else:
                data_str += "  None\n"
            
            # Get income distribution by type
            cursor.execute(f"""
                SELECT it.type_name, SUM(i.amount), i.currency
                FROM ingresos i
                JOIN income_types it ON i.income_type = it.val
                WHERE strftime('%Y', i.date) = '{year}'
                GROUP BY it.type_name, i.currency
            """)
            income_distribution = cursor.fetchall()
            data_str += "-Income Distribution:\n"
            if income_distribution:
                for dist in income_distribution:
                    amount = round(Currency(dist[1], dist[2]).convert(), 2)
                    data_str += f"  {dist[0]} {amount} {Currency.current_currency}\n"
            else:
                data_str += "  None\n"
            
            # Get expense distribution by type
            cursor.execute(f"""
                SELECT et.type_name, SUM(g.amount), g.currency
                FROM gastos g
                LEFT JOIN expense_types et ON g.expense_type = et.val
                WHERE strftime('%Y', g.date) = '{year}'
                GROUP BY et.type_name, g.currency
            """)
            expense_distribution = cursor.fetchall()
            data_str += "-Expenses Distribution:\n"
            if expense_distribution:
                for dist in expense_distribution:
                    amount = round(Currency(dist[1], dist[2]).convert(), 2)
                    data_str += f"  {dist[0]} {amount} {Currency.current_currency}\n"
            else:
                data_str += "  None\n"
        
        conn.close()
        return data_str

class Ventana:
    def __init__(self, parent, proyecto : Proyecto, period='mensual'):
        self.parent = parent  # Adjustment to use the received frame
        self.proyecto = proyecto
        self.tooltip = None
        self.period = period
        self.chart = None
        self.lbl_info = None

    def change_period(self):
        if self.period == 'mensual':
            self.period = 'anual'
        else:
            self.period = 'mensual'

    def set_period(self, periodo):
        self.period = periodo

    def show_chart(self):
        
        fig, bars, data = self.proyecto.generar_chart(periodo=self.period)
        canvas = FigureCanvasTkAgg(fig, master=self.parent)
        canvas.draw()
        canvas.get_tk_widget().pack()  # Displayed below the button in the same frame

        # Separate the bars into two lists: income bars and expense bars
        n_rows = len(data)
        bars_ingresos = bars[:n_rows]
        bars_gastos = bars[n_rows:]

        def show_tooltip(event: MouseEvent):
            if event.inaxes:
                # Detect income bars
                for i, rect in enumerate(bars_ingresos):
                    if rect.contains(event)[0]:
                        # Get the corresponding row from the DataFrame
                        row = data.iloc[i]
                        if self.tooltip:
                            self.tooltip.destroy()
                        x_root, y_root = canvas.get_tk_widget().winfo_pointerxy()
                        self.tooltip = Toplevel(self.parent)
                        self.tooltip.wm_overrideredirect(True)
                        self.tooltip.geometry(f"+{x_root+15}+{y_root+15}")
                        Label(
                            self.tooltip,
                            text=f"Ingresos:\n{row.name}: {round(row['Ingresos'],2)} {Currency.current_currency}",
                            bg="lightyellow",
                            fg="green",
                            font=("Arial", 10, "bold"),
                            relief="solid",
                            borderwidth=1,
                            padx=10,
                            pady=5,
                        ).pack()

                # Detect expense bars
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
                            text=f"Gastos:\n{row.name}: {round(row['Gastos'],2)} {Currency.current_currency}",
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
        self.chart.pack()

        lbl_info = Label(self.parent, text="These are the nearest upcoming payments:", fg="black")
        lbl_info.pack()

        pagos = self.proyecto.get_upcoming_payments()
        for pago in pagos:
            lbl = Label(self.parent, text=f"{pago[0]}: Deadline: {pago[2]} Invoice number: {pago[3]}", fg="blue", cursor="hand2")
            lbl.pack()
            lbl.bind("<Button-1>", lambda e, concept=pago[3]: self.copy_to_clipboard(concept))

        self.lbl_info = lbl_info

    def eliminate_chart(self):
        if self.chart:
            self.chart.destroy()
            self.chart = None

        if self.lbl_info:
            self.lbl_info.destroy()
            self.lbl_info = None

        for widget in self.parent.winfo_children():
            if isinstance(widget, Label) and widget.cget("fg") == "blue":
                widget.destroy()

    def copy_to_clipboard(self, invoice):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(invoice)

# Example usage
if __name__ == "__main__":
    proyecto = Proyecto('Contabilidad', 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id')
    print("Total Ingresos:", proyecto.calcular_total_ingresos())
    print("Total Gastos:", proyecto.calcular_total_gastos())
    print("Balance:", proyecto.calcular_balance())
    print(proyecto.get_accurate_data())
    print(proyecto.get_basic_data())

    from tkinter import Tk

    root = Tk()
    ventana = Ventana(root, proyecto, 'anual')
    ventana.show_chart()
    root.mainloop()






