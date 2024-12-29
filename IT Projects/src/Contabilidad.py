import sqlite3

def crear_base_datos():
    conn = sqlite3.connect("contabilidad.db")
    cursor = conn.cursor()

    # Tabla de tipos de gasto (expenseType) para añadir y gestionar nuevos tipos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expense_types (
        val INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE NOT NULL
    );
    """)

    # Tabla de tipos de ingreso (incomeType) para añadir y gestionar nuevos tipos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS income_types (
        val INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE NOT NULL
    );
    """)

    # Tabla de gastos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER NOT NULL,
        invoice_number INTEGER,
        payment_state TEXT CHECK(payment_state IN ('payed','pending')),
        concept TEXT NOT NULL,
        invoice_link TEXT,
        date DATE NOT NULL,
        expense_type INTEGER,
        FOREIGN KEY (expense_type) REFERENCES expense_types(val)
    );
    """)

    # Tabla de ingresos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingresos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER NOT NULL,
        concept TEXT NOT NULL,
        income_type INTEGER,
        date DATE NOT NULL,
        FOREIGN KEY (income_type) REFERENCES income_types(val)
    );
    """)

    conn.commit()
    conn.close()

def cargar_datos_iniciales():
    conn = sqlite3.connect("contabilidad.db")
    cursor = conn.cursor()

    # Insertar tipos de gasto
    expense_types = [("Alquiler",), ("Comida",), ("Transporte",)]
    cursor.executemany("INSERT OR IGNORE INTO expense_types(type_name) VALUES(?)", expense_types)

    # Insertar tipos de ingreso
    income_types = [("Salario",), ("Inversión",), ("Otros",)]
    cursor.executemany("INSERT OR IGNORE INTO income_types(type_name) VALUES(?)", income_types)

    # Obtenemos los ID de los tipos
    cursor.execute("SELECT val, type_name FROM expense_types")
    expense_dict = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT val, type_name FROM income_types")
    income_dict = {row[1]: row[0] for row in cursor.fetchall()}

    # Insertar datos de ejemplo en 'gastos'
    datos_gastos = [
        (-800, 1001, 'payed', 'Pago alquiler', 'https://factura1.com', '2023-10-01', expense_dict['Alquiler']),
        (50, 1002, 'pending', 'Compra supermercado', 'https://factura2.com', '2023-10-02', expense_dict['Comida']),
        (20, 1003, 'payed', 'Taxi al aeropuerto', 'https://factura3.com', '2023-10-03', expense_dict['Transporte'])
    ]
    cursor.executemany("""
        INSERT INTO gastos (amount, invoice_number, payment_state, concept, invoice_link, date, expense_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, datos_gastos)

    # Insertar datos de ejemplo en 'ingresos'
    datos_ingresos = [
        (1500, 'Salario mensual', income_dict['Salario'], '2023-10-01'),
        (200, 'Intereses bancarios', income_dict['Inversión'], '2023-10-05'),
        (300, 'Venta de muebles usados', income_dict['Otros'], '2023-10-10')
    ]
    cursor.executemany("""
        INSERT INTO ingresos (amount, concept, income_type, date)
        VALUES (?, ?, ?, ?)
    """, datos_ingresos)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_base_datos()
    cargar_datos_iniciales()



