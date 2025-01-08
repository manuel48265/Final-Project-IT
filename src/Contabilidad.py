import sqlite3

def create_project_database(db_name="contabilidad.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Expense types table to add and manage new types
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expense_types (
        val INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE NOT NULL
    );
    """)

    # Income types table to add and manage new types
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS income_types (
        val INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE NOT NULL
    );
    """)

    # Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER NOT NULL,
        currency TEXT NOT NULL DEFAULT 'USD',
        invoice_number INTEGER,
        payment_state TEXT CHECK(payment_state IN ('paid','pending')),
        concept TEXT NOT NULL,
        invoice_link TEXT,
        date DATE NOT NULL,
        expense_type INTEGER,
        FOREIGN KEY (expense_type) REFERENCES expense_types(val)
    );
    """)

    # Income table
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

def load_initial_project_data(db_name="contabilidad.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Insert expense types
    expense_types = [("Rent",), ("Food",), ("Transport",), ("Services",),( "Supplies",), ("Marketing",)]
    cursor.executemany("INSERT OR IGNORE INTO expense_types(type_name) VALUES(?)", expense_types)

    # Insert income types
    income_types = [("Salary",), ("Investment",), ("Others",), ("Business",), ("Freelance",)]
    cursor.executemany("INSERT OR IGNORE INTO income_types(type_name) VALUES(?)", income_types)

    # Get the IDs of the types
    cursor.execute("SELECT val, type_name FROM expense_types")
    expense_dict = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT val, type_name FROM income_types")
    income_dict = {row[1]: row[0] for row in cursor.fetchall()}

    # Data from various years and months
    expense_data = [
        (800,'USD', 1010, 'paid', 'Rent payment 2020', 'https://invoice1.com', '2020-01-10', expense_dict['Rent']),
        (50,'USD', 1011, 'pending', 'Purchase 2021', 'https://invoice2.com', '2021-02-20', expense_dict['Food']),
        (100,'USD', 1012, 'pending', 'Services 2022', 'https://invoice3.com', '2022-07-15', expense_dict['Services']),
        (20,'USD', 1013, 'paid', 'Airport taxi 2023', 'https://invoice4.com', '2023-06-05', expense_dict['Transport']),
        (60,'USD', 1014, 'pending', 'Gym payment 2023', 'https://invoice5.com', '2023-08-12', expense_dict['Food']),
        (200,'USD', 1015, 'pending', 'Furniture purchase 2024', 'https://invoice6.com', '2024-01-20', expense_dict['Food']),
        (200,'USD', 1015, 'pending', 'Furniture purchase 2024', 'https://invoice6.com', '2025-01-20', expense_dict['Food']),
        (150,'USD', 1016, 'paid', 'Rent payment 2024', 'https://invoice7.com', '2025-02-01', expense_dict['Rent']),
        (300,'USD', 1017, 'pending', 'Purchase 2024', 'https://invoice8.com', '2025-02-05', expense_dict['Food']),
        (250,'USD', 1018, 'paid', 'Office supplies 2025', 'https://invoice9.com', '2025-03-10', expense_dict['Supplies']),
        (400,'USD', 1019, 'pending', 'Marketing campaign 2025', 'https://invoice10.com', '2025-04-15', expense_dict['Marketing']),
        (500,'USD', 1020, 'paid', 'Office rent 2026', 'https://invoice11.com', '2026-05-20', expense_dict['Rent']),
        (100,'USD', 1021, 'pending', 'Electricity bill 2026', 'https://invoice12.com', '2026-06-25', expense_dict['Services']),
        (300,'USD', 1022, 'paid', 'Internet bill 2027', 'https://invoice13.com', '2027-07-30', expense_dict['Services']),
        (150,'USD', 1023, 'pending', 'Water bill 2027', 'https://invoice14.com', '2027-08-05', expense_dict['Services']),
        (200,'USD', 1024, 'paid', 'Office rent 2028', 'https://invoice15.com', '2028-09-10', expense_dict['Rent']),
        (350,'USD', 1025, 'pending', 'Marketing campaign 2028', 'https://invoice16.com', '2028-10-15', expense_dict['Marketing']),
        (450,'USD', 1026, 'paid', 'Office supplies 2029', 'https://invoice17.com', '2029-11-20', expense_dict['Supplies']),
        (600,'USD', 1027, 'pending', 'Office rent 2029', 'https://invoice18.com', '2029-12-25', expense_dict['Rent']),
        # ...add more data if desired...
    ]
    cursor.executemany("""
        INSERT INTO gastos (amount, currency, invoice_number, payment_state, concept, invoice_link, date, expense_type)
        VALUES (?,?,?, ?, ?, ?, ?, ?)
    """, expense_data)

    income_data = [
        (1500,'USD', 'Salary 2020', income_dict['Salary'], '2020-02-01'),
        (1800,'USD', 'Salary 2021', income_dict['Salary'], '2021-07-15'),
        (200,'USD','Interest 2022', income_dict['Investment'], '2022-05-25'),
        (1200,'USD', 'Business earnings 2023', income_dict['Business'], '2023-11-10'),
        (300,'USD', 'Various income 2023', income_dict['Others'], '2020-01-20'),
        (1600,'USD', 'Salary 2024', income_dict['Salary'], '2024-03-01'),
        (1900,'USD', 'Salary 2025', income_dict['Salary'], '2025-08-15'),
        (250,'USD','Interest 2026', income_dict['Investment'], '2026-06-25'),
        (1300,'USD', 'Business earnings 2027', income_dict['Business'], '2027-12-10'),
        (350,'USD', 'Various income 2028', income_dict['Others'], '2028-02-20'),
        (1700,'USD', 'Salary 2029', income_dict['Salary'], '2029-04-01'),
        (2000,'USD', 'Salary 2030', income_dict['Salary'], '2030-09-15'),
        (300,'USD','Interest 2031', income_dict['Investment'], '2031-07-25'),
        (1400,'USD', 'Business earnings 2032', income_dict['Business'], '2032-01-10'),
        (400,'USD', 'Various income 2033', income_dict['Others'], '2033-03-20'),
        # ...add more data if desired...
    ]
    cursor.executemany("""
        INSERT INTO ingresos (amount, currency, concept, income_type, date)
        VALUES (?, ?, ?, ?, ?)
    """, income_data)

    conn.commit()
    conn.close()

def create_generic_expense_database(db_name="genericos.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create expense types table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expense_types (
        val INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE NOT NULL
    );
    """)

    # Create expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER NOT NULL,
        currency TEXT NOT NULL DEFAULT 'USD',
        invoice_number INTEGER,
        payment_state TEXT CHECK(payment_state IN ('paid','pending')),
        concept TEXT NOT NULL,
        invoice_link TEXT,
        date DATE NOT NULL,
        expense_type INTEGER,
        FOREIGN KEY (expense_type) REFERENCES expense_types(val)
    );
    """)

    conn.commit()
    conn.close()

def load_initial_generic_expense_data(db_name="genericos.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Insert expense types
    expense_types = [
        ('Rent',),
        ('Services',),
        ('Supplies',),
        ('Transport',),
        ('Marketing',), 
        ('Food',),
        ('Others',)
    ]
    cursor.executemany("INSERT OR IGNORE INTO expense_types (type_name) VALUES (?);", expense_types)

    # Insert some expenses
    expenses = [
        (1200,'USD', 101, 'paid', 'Office rent', 'http://linktoinvoice.com/101', '2024-01-10', 1),
        (150,'EUR', 102, 'pending', 'Electricity', 'http://linktoinvoice.com/102', '2024-01-15', 2),
        (80,'USD', 103, 'paid', 'Water', 'http://linktoinvoice.com/103', '2024-01-20', 3),
        (300,'USD', 104, 'paid', 'Monthly transport', 'http://linktoinvoice.com/104', '2024-02-01', 4),
        (500,'USD', 105, 'pending', 'Online advertising', 'http://linktoinvoice.com/105', '2024-02-05', 5),
        (600,'USD', 106, 'paid', 'Office rent', 'http://linktoinvoice.com/106', '2025-03-10', 1),
        (200,'EUR', 107, 'pending', 'Internet', 'http://linktoinvoice.com/107', '2021-03-15', 2),
        (90,'USD', 108, 'paid', 'Office supplies', 'http://linktoinvoice.com/108', '2020-03-20', 3),
        (350,'USD', 109, 'paid', 'Monthly transport', 'http://linktoinvoice.com/109', '2022-04-01', 4),
        (550,'USD', 110, 'pending', 'Social media advertising', 'http://linktoinvoice.com/110', '2019-04-05', 5),
        (700,'USD', 111, 'paid', 'Office rent', 'http://linktoinvoice.com/111', '2026-05-10', 1),
        (250,'EUR', 112, 'pending', 'Electricity', 'http://linktoinvoice.com/112', '2027-05-15', 2),
        (100,'USD', 113, 'paid', 'Water', 'http://linktoinvoice.com/113', '2028-05-20', 3),
        (400,'USD', 114, 'paid', 'Monthly transport', 'http://linktoinvoice.com/114', '2029-06-01', 4),
        (600,'USD', 115, 'pending', 'Online advertising', 'http://linktoinvoice.com/115', '2030-06-05', 5)
    ]
    cursor.executemany("""
        INSERT INTO gastos (amount,currency, invoice_number, payment_state, concept, invoice_link, date, expense_type)
        VALUES (?, ?,?, ?, ?, ?, ?, ?);
    """, expenses)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # A single database contabilidad.db
    create_project_database()
    load_initial_project_data()
    create_generic_expense_database()
    load_initial_generic_expense_data()



