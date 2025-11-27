import sqlite3
import os
from typing import List, Tuple, Dict, Any
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "knife_production.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database():
    """Create DB and all tables if not present."""
    first = not os.path.exists(DB_PATH)
    conn = get_connection()
    cur = conn.cursor()

    # create tables (idempotent)
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS Customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT
    );

    CREATE TABLE IF NOT EXISTS "Order" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_created TEXT NOT NULL,
        customer_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Pending',
        total_price REAL DEFAULT 0,
        FOREIGN KEY (customer_id) REFERENCES Customer(id)
    );

    CREATE TABLE IF NOT EXISTS Product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS Material (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        unit_cost REAL NOT NULL,
        stock_quantity REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS OrderProduct (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        subtotal_value REAL DEFAULT 0,
        FOREIGN KEY (order_id) REFERENCES "Order"(id),
        FOREIGN KEY (product_id) REFERENCES Product(id)
    );

    CREATE TABLE IF NOT EXISTS ProductMaterial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        material_id INTEGER NOT NULL,
        quantity_used REAL NOT NULL,
        unit_cost REAL,
        FOREIGN KEY (product_id) REFERENCES Product(id),
        FOREIGN KEY (material_id) REFERENCES Material(id)
    );

    CREATE TABLE IF NOT EXISTS Production (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_product_id INTEGER NOT NULL,
        start_date TEXT,
        end_date TEXT,
        status TEXT DEFAULT 'Pending',
        notes TEXT,
        FOREIGN KEY (order_product_id) REFERENCES OrderProduct(id)
    );

    CREATE TABLE IF NOT EXISTS Worker (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        role TEXT,
        hourly_rate REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS ProductionWorker (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        production_id INTEGER NOT NULL,
        worker_id INTEGER NOT NULL,
        hours_worked REAL DEFAULT 0,
        wage REAL DEFAULT 0,
        FOREIGN KEY (production_id) REFERENCES Production(id),
        FOREIGN KEY (worker_id) REFERENCES Worker(id)
    );

    CREATE TABLE IF NOT EXISTS Tool (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,
        status TEXT DEFAULT 'Available',
        last_maintenance_date TEXT
    );

    CREATE TABLE IF NOT EXISTS WorkerTool (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER NOT NULL,
        tool_id INTEGER NOT NULL,
        assigned_date TEXT,
        return_date TEXT,
        FOREIGN KEY (worker_id) REFERENCES Worker(id),
        FOREIGN KEY (tool_id) REFERENCES Tool(id)
    );

    CREATE TABLE IF NOT EXISTS MaterialUsage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        production_id INTEGER NOT NULL,
        material_id INTEGER NOT NULL,
        quantity_used REAL DEFAULT 0,
        cost_used REAL DEFAULT 0,
        FOREIGN KEY (production_id) REFERENCES Production(id),
        FOREIGN KEY (material_id) REFERENCES Material(id)
    );
    """)
    conn.commit()
    conn.close()


### === Materials APIs ===
def list_materials() -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, unit_cost, stock_quantity FROM Material ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_material(name: str, unit_cost: float, stock_quantity: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Material (name, unit_cost, stock_quantity) VALUES (?, ?, ?)",
                (name, unit_cost, stock_quantity))
    conn.commit()
    conn.close()


def update_material(mat_id: int, name: str, unit_cost: float, stock_quantity: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Material SET name=?, unit_cost=?, stock_quantity=? WHERE id=?",
                (name, unit_cost, stock_quantity, mat_id))
    conn.commit()
    conn.close()


def delete_material(mat_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Material WHERE id=?", (mat_id,))
    conn.commit()
    conn.close()


### === Products + ProductMaterial APIs ===
def list_products() -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, description FROM Product ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_product(product_id: int) -> sqlite3.Row:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, description FROM Product WHERE id=?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row


def add_product(name: str, price: float, description: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Product (name, price, description) VALUES (?, ?, ?)", (name, price, description))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def update_product(product_id: int, name: str, price: float, description: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Product SET name=?, price=?, description=? WHERE id=?", (name, price, description, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    # remove product-material relations first
    cur.execute("DELETE FROM ProductMaterial WHERE product_id=?", (product_id,))
    cur.execute("DELETE FROM Product WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def list_product_materials(product_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT pm.id, pm.material_id, m.name as material_name, pm.quantity_used, pm.unit_cost
        FROM ProductMaterial pm
        JOIN Material m ON pm.material_id = m.id
        WHERE pm.product_id = ?
        ORDER BY m.name
    """, (product_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def add_product_material(product_id: int, material_id: int, quantity_used: float, unit_cost: float = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO ProductMaterial (product_id, material_id, quantity_used, unit_cost) VALUES (?, ?, ?, ?)",
                (product_id, material_id, quantity_used, unit_cost))
    conn.commit()
    conn.close()


def delete_product_material(pm_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ProductMaterial WHERE id=?", (pm_id,))
    conn.commit()
    conn.close()


### === Customers APIs ===
def list_customers() -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, email, phone FROM Customer ORDER BY last_name, first_name")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_customer(first_name: str, last_name: str, email: str, phone: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Customer (first_name, last_name, email, phone) VALUES (?, ?, ?, ?)",
                (first_name, last_name, email, phone))
    conn.commit()
    conn.close()


def update_customer(customer_id: int, first_name: str, last_name: str, email: str, phone: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Customer SET first_name=?, last_name=?, email=?, phone=? WHERE id=?",
                (first_name, last_name, email, phone, customer_id))
    conn.commit()
    conn.close()


def delete_customer(customer_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Customer WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()


### === Orders + Production APIs ===


def create_order(customer_id: int, products: List[Tuple[int, int]]) -> int:
    """
    Create an order.
    products: list of tuples (product_id, quantity)
    Returns order_id.
    Also creates OrderProduct rows and Production rows and updates total_price.
    """
    conn = get_connection()
    cur = conn.cursor()
    date_created = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO 'Order' (date_created, customer_id, status, total_price) VALUES (?, ?, 'Pending', 0)",
                (date_created, customer_id))
    order_id = cur.lastrowid

    total = 0.0
    for product_id, qty in products:
        cur.execute("SELECT price FROM Product WHERE id=?", (product_id,))
        pr = cur.fetchone()
        if not pr:
            continue
        price = pr["price"]
        subtotal = price * qty
        cur.execute("INSERT INTO OrderProduct (order_id, product_id, quantity, subtotal_value) VALUES (?, ?, ?, ?)",
                    (order_id, product_id, qty, subtotal))
        op_id = cur.lastrowid
        total += subtotal

        # create a Production row for this order-product (one production per orderproduct)
        cur.execute("INSERT INTO Production (order_product_id, status) VALUES (?, 'Pending')", (op_id,))

    # update order total
    cur.execute("UPDATE 'Order' SET total_price=? WHERE id=?", (total, order_id))
    conn.commit()
    conn.close()
    return order_id


def list_orders() -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT o.id, o.date_created, o.status, o.total_price,
                   c.first_name || ' ' || c.last_name as customer_name
                   FROM "Order" o
                   JOIN Customer c ON o.customer_id = c.id
                   ORDER BY o.date_created DESC""")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_order_products(order_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT op.id, op.product_id, p.name as product_name, op.quantity, op.subtotal_value
                   FROM OrderProduct op
                   JOIN Product p ON op.product_id = p.id
                   WHERE op.order_id = ?""", (order_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def list_production():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.status, p.order_product_id,
               pr.name as product_name
        FROM Production p
        JOIN OrderProduct op ON op.id = p.order_product_id
        JOIN Product pr ON pr.id = op.product_id
        ORDER BY p.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_production(production_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, op.order_id, op.product_id
        FROM Production p
        JOIN OrderProduct op ON op.id = p.order_product_id
        WHERE p.id=?
    """, (production_id,))
    row = cur.fetchone()
    conn.close()
    return row


def mark_production_done(production_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Production SET status='Completed', end_date=datetime('now') WHERE id=?",
                (production_id,))
    conn.commit()
    conn.close()


def complete_production_with_materials(production_id: int):
    conn = get_connection()
    cur = conn.cursor()

    # Step 1: get related order-product record
    cur.execute("""
        SELECT p.order_product_id, op.product_id, op.quantity
        FROM Production p
        JOIN OrderProduct op ON op.id = p.order_product_id
        WHERE p.id=?
    """, (production_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise Exception("Production not found")

    op_id = row["order_product_id"]
    product_id = row["product_id"]
    order_qty = row["quantity"]

    # Step 2: retrieve required materials for this product
    cur.execute("""
        SELECT pm.material_id, pm.quantity_used, m.stock_quantity
        FROM ProductMaterial pm
        JOIN Material m ON m.id = pm.material_id
        WHERE pm.product_id=?
    """, (product_id,))
    materials = cur.fetchall()

    # Step 3: validate stock
    for m in materials:
        needed = m["quantity_used"] * order_qty
        if m["stock_quantity"] < needed:
            conn.close()
            raise Exception(
                f"Not enough stock for material ID {m['material_id']}. "
                f"Needed: {needed}, Available: {m['stock_quantity']}"
            )

    # Step 4: deduct stock
    for m in materials:
        needed = m["quantity_used"] * order_qty
        cur.execute("""
            UPDATE Material
            SET stock_quantity = stock_quantity - ?
            WHERE id=?
        """, (needed, m["material_id"]))

    # Step 5: mark production completed
    cur.execute("""
        UPDATE Production
        SET status='Completed', end_date=datetime('now')
        WHERE id=?
    """, (production_id,))

    conn.commit()
    conn.close()
