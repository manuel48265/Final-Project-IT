import sqlite3
import tkinter as tk
from tkinter import ttk

# Función para obtener datos de la base de datos
def obtener_datos(orden, ascendente=True):
    conexion = sqlite3.connect('genericos.db')
    cursor = conexion.cursor()
    # Usar un formato seguro para ordenar
    orden_dir = "ASC" if ascendente else "DESC"
    consulta = f"""
        SELECT f.id, f.amount, f.currency, f.invoice_number, f.payment_state, f.concept, f.invoice_link, f.date, e.type_name as expense_type
        FROM gastos f
        JOIN expense_types e ON f.expense_type = e.val
        ORDER BY {orden} {orden_dir}
    """
    cursor.execute(consulta)
    datos = cursor.fetchall()
    conexion.close()
    return datos

# Función para actualizar el Treeview
def actualizar_treeview(tree, orden, ascendente=True):
    for row in tree.get_children():
        tree.delete(row)  # Eliminar filas existentes
    datos = obtener_datos(orden, ascendente)
    for fila in datos:
        tree.insert("", "end", values=fila)

def encabezado_click(event, col):
    columna = col
    if columna in columnas:
        # Restablecer el estado de orden de todas las columnas a None
        for key in orden_actual.keys():
            if key != columna:
                orden_actual[key] = None

        # Alternar el estado de orden de la columna seleccionada
        if orden_actual[columna] is None:
            orden_actual[columna] = True
        elif orden_actual[columna] is True:
            orden_actual[columna] = False
        elif orden_actual[columna] is False:
            orden_actual[columna] = True
        else:
            orden_actual[columna] = None

        if orden_actual[columna] is not None:
            actualizar_treeview(tree, columna, orden_actual[columna])
        actualizar_encabezados()

# Función para actualizar los encabezados con flechas
def actualizar_encabezados():
    for col, text in columnas.items():
        if orden_actual[col] is None:
            tree.heading(col, text=text)
        else:
            orden_dir = "↑" if orden_actual[col] else "↓"
            tree.heading(col, text=f"{text} {orden_dir}")

# Función para manejar la selección de una fila
def seleccionar_fila(event):
    item = tree.selection()[0]
    fecha = tree.item(item, "values")[6]  # La fecha está en la columna 6 (índice 5)
    print(f"Fecha seleccionada: {fecha}")

# Crear la interfaz
def crear_interfaz():
    global tree, columnas, orden_actual
    root = tk.Tk()
    root.title("Visualizar Base de Datos")

    # Configurar el Treeview con columnas
    columnas = {
        "id": "ID",
        "amount": "Amount",
        "currency": "Currency",
        "invoice_number": "Invoice Number",
        "payment_state": "Payment State",
        "concept": "Concept",
        "invoice_link": "Invoice Link",
        "date": "Date",
        "expense_type": "Expense Type"
    }
    orden_actual = {col: None for col in columnas}  # None para sin orden, True para ascendente, False para descendente

    tree = ttk.Treeview(root, columns=list(columnas.keys()), show='headings')
    for col, text in columnas.items():
        tree.heading(col, text=text, command=lambda _col=col: encabezado_click(None, _col))

    tree.pack(expand=True, fill=tk.BOTH)

    # Vincular el evento de selección de una fila
    tree.bind("<<TreeviewSelect>>", seleccionar_fila)

    # Cargar datos iniciales
    actualizar_treeview(tree, "id")

    root.mainloop()

# Ejecutar el programa
if __name__ == "__main__":
    crear_interfaz()