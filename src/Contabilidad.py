import sqlite3

def crear_base_datos_projectos(db_name="contabilidad.db"):
    conn = sqlite3.connect(db_name)
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
        currency TEXT NOT NULL DEFAULT 'USD',
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
        currency TEXT NOT NULL DEFAULT 'USD',
        concept TEXT NOT NULL,
        income_type INTEGER,
        date DATE NOT NULL,
        FOREIGN KEY (income_type) REFERENCES income_types(val)
    );
    """)

    conn.commit()
    conn.close()

def cargar_datos_iniciales_projectos(db_name="contabilidad.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Insertar tipos de gasto
    expense_types = [("Alquiler",), ("Comida",), ("Transporte",), ("Servicios",)]
    cursor.executemany("INSERT OR IGNORE INTO expense_types(type_name) VALUES(?)", expense_types)

    # Insertar tipos de ingreso
    income_types = [("Salario",), ("Inversión",), ("Otros",), ("Negocio",)]
    cursor.executemany("INSERT OR IGNORE INTO income_types(type_name) VALUES(?)", income_types)

    # Obtenemos los ID de los tipos
    cursor.execute("SELECT val, type_name FROM expense_types")
    expense_dict = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT val, type_name FROM income_types")
    income_dict = {row[1]: row[0] for row in cursor.fetchall()}

    # Datos de diversos años y meses
    datos_gastos = [
        (800,'USD', 1010, 'payed', 'Pago alquiler 2020', 'https://factura1.com', '2020-01-10', expense_dict['Alquiler']),
        (50,'USD', 1011, 'pending', 'Compra 2021', 'https://factura2.com', '2021-02-20', expense_dict['Comida']),
        (100,'USD', 1012, 'pending', 'Servicios 2022', 'https://factura3.com', '2022-07-15', expense_dict['Servicios']),
        (20,'USD', 1013, 'payed', 'Taxi aeropuerto 2023', 'https://factura4.com', '2023-06-05', expense_dict['Transporte']),
        (60,'USD', 1014, 'pending', 'Pago gimnasio 2023', 'https://factura5.com', '2023-08-12', expense_dict['Comida']),
        (200,'USD', 1015, 'pending', 'Compra muebles 2024', 'https://factura6.com', '2024-01-20', expense_dict['Comida']),
        (200,'USD', 1015, 'pending', 'Compra muebles 2024', 'https://factura6.com', '2025-01-20', expense_dict['Comida']),
        (150,'USD', 1016, 'payed', 'Pago alquiler 2024', 'https://factura7.com', '2025-02-01', expense_dict['Alquiler']),
        (300,'USD', 1017, 'pending', 'Compra 2024', 'https://factura8.com', '2025-02-05', expense_dict['Comida']),
        # ...añade más datos si deseas...
    ]
    cursor.executemany("""
        INSERT INTO gastos (amount, currency, invoice_number, payment_state, concept, invoice_link, date, expense_type)
        VALUES (?,?,?, ?, ?, ?, ?, ?)
    """, datos_gastos)

    datos_ingresos = [
        (1500,'USD', 'Salario 2020', income_dict['Salario'], '2020-02-01'),
        (1800,'USD', 'Salario 2021', income_dict['Salario'], '2021-07-15'),
        (200,'USD','Intereses 2022', income_dict['Inversión'], '2022-05-25'),
        (1200,'USD', 'Ganancias negocio 2023', income_dict['Negocio'], '2023-11-10'),
        (300,'USD', 'Ingresos varios 2023', income_dict['Otros'], '2020-01-20'),
        # ...añade más datos si deseas...
    ]
    cursor.executemany("""
        INSERT INTO ingresos (amount, currency, concept, income_type, date)
        VALUES (?, ?, ?, ?, ?)
    """, datos_ingresos)

    conn.commit()
    conn.close()

def crear_base_de_datos_gastos_genericos(db_name="genericos.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Crear tabla de tipos de gastos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expense_types (
        val INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE NOT NULL
    );
    """)

    # Crear tabla de gastos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER NOT NULL,
        currency TEXT NOT NULL DEFAULT 'USD',
        invoice_number INTEGER,
        payment_state TEXT CHECK(payment_state IN ('payed','pending')),
        concept TEXT NOT NULL,
        invoice_link TEXT,
        date DATE NOT NULL,
        expense_type INTEGER,
        FOREIGN KEY (expense_type) REFERENCES expense_types(val)
    );
    """)

    conn.commit()
    conn.close()

def cargar_datos_iniciales_gastos_genericos(db_name="genericos.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Insertar tipos de gasto
    tipos_gastos = [
        ('Alquiler',),
        ('Servicios',),
        ('Suministros',),
        ('Transporte',),
        ('Marketing',)
    ]
    cursor.executemany("INSERT OR IGNORE INTO expense_types (type_name) VALUES (?);", tipos_gastos)

    # Insertar algunos gastos
    gastos = [
        (1200,'USD', 101, 'payed', 'Alquiler oficina', 'http://linktoinvoice.com/101', '2024-01-10', 1),
        (150,'EUR', 102, 'pending', 'Electricidad', 'http://linktoinvoice.com/102', '2024-01-15', 2),
        (80,'USD', 103, 'payed', 'Agua', 'http://linktoinvoice.com/103', '2024-01-20', 3),
        (300,'USD', 104, 'payed', 'Transporte mensual', 'http://linktoinvoice.com/104', '2024-02-01', 4),
        (500,'USD', 105, 'pending', 'Publicidad online', 'http://linktoinvoice.com/105', '2024-02-05', 5)
    ]
    cursor.executemany("""
        INSERT INTO gastos (amount,currency, invoice_number, payment_state, concept, invoice_link, date, expense_type)
        VALUES (?, ?,?, ?, ?, ?, ?, ?);
    """, gastos)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Una sola base de datos contabilidad.db
    crear_base_datos_projectos()
    cargar_datos_iniciales_projectos()
    crear_base_de_datos_gastos_genericos()
    cargar_datos_iniciales_gastos_genericos()



