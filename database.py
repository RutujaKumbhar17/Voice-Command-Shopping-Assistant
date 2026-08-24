import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "freshroot.db")
if os.environ.get("VERCEL") or not os.access(os.path.dirname(DB_PATH) or ".", os.W_OK):
    DB_PATH = "/tmp/freshroot.db"

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create products table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_fk INTEGER NOT NULL,
                product_title TEXT NOT NULL,
                product_cat TEXT NOT NULL,
                product_type TEXT NOT NULL,
                product_expiry TEXT NOT NULL,
                product_image TEXT NOT NULL,
                product_stock INTEGER NOT NULL,
                product_price INTEGER NOT NULL,
                product_desc TEXT NOT NULL,
                product_keywords TEXT NOT NULL,
                product_delivery TEXT NOT NULL
            )
            """)

            # Create categories table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                cat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cat_title TEXT NOT NULL
            )
            """)

            # Create voice shopping list table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_shopping_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                unit TEXT DEFAULT 'items',
                category TEXT DEFAULT 'General',
                price INTEGER DEFAULT 0,
                is_checked INTEGER DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Create cart table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                phonenumber INTEGER NOT NULL,
                qty INTEGER NOT NULL DEFAULT 1,
                subtotal INTEGER NOT NULL
            )
            """)

            # Create orders table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                address TEXT NOT NULL,
                delivery TEXT NOT NULL,
                phonenumber INTEGER NOT NULL,
                total INTEGER NOT NULL,
                payment TEXT NOT NULL,
                buyer_phonenumber INTEGER NOT NULL
            )
            """)

            # Check if products need seed data
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            if count == 0:
                self._seed_data(cursor)

            conn.commit()

    def _seed_data(self, cursor):
        categories_data = [
            (1, 'Crops'),
            (2, 'Vegetables'),
            (3, 'Fruits')
        ]
        cursor.executemany("INSERT OR IGNORE INTO categories VALUES (?, ?)", categories_data)

        products_data = [
            (1, 1, 'Ramlal Potato', '2', 'Potato', '2026-04-15', 'Potato.jpg', 1000, 12, 'Best Quality product guaranteed 100 percent', 'potato', 'yes'),
            (3, 1, 'Ramlal Tomato', '2', 'Tomato', '2026-04-15', 'Tomato.jpg', 500, 15, 'Best Quality tomato assured', 'tomato, best quality tomato', 'no'),
            (17, 3, 'Shivneri Bananas', '3', 'Bananas', '2026-04-15', 'Bananas.jpg', 250, 30, 'Best Quality Bananas', 'banana, shivneri', 'yes'),
            (18, 3, 'Ram Rice', '1', 'Rice', '2026-04-15', 'Rice.jpg', 1500, 45, 'Premium aromatic Basmati rice', 'rice, best rice', 'yes'),
            (19, 1, 'Ansh Carrot', '2', 'Carrot', '2026-04-15', 'Carrot.jpg', 1250, 56, 'Big fat juicy best quality carrots assured', 'carrot, best carrot', 'yes'),
            (21, 1, 'Abhi Maize', '1', 'Maize', '2026-04-15', 'Maize.jpg', 750, 99, 'Seeds imported, grown naturally', 'maize, best maize', 'yes'),
            (22, 3, 'Calista Coconut', '1', 'Coconut', '2026-04-15', 'Coconut.jpg', 450, 25, 'Fresh sweet coconuts', 'coconut, best coconut', 'no'),
            (23, 1, 'Arpit Grapes', '3', 'Grapes', '2026-04-15', 'Green Grapes.jpg', 4560, 60, 'Best Grapes you will ever find', 'grapes, green grapes', 'yes'),
            (24, 1, 'Arpit Apples', '3', 'Apple', '2026-04-15', 'Apple.jpg', 1500, 100, 'Best Apples grown in Kashmir', 'apples, apple, best apple', 'no'),
            (25, 1, 'Ramlal Wheat', '1', 'Wheat', '2026-04-15', 'Wheat.jpg', 2000, 40, 'Fragrant wheat grains grown with care', 'wheat, best wheat', 'no'),
            (27, 3, 'Arpit Alphonso Mango', '3', 'Mango', '2026-04-15', 'Mango.jpg', 2000, 200, 'Grown with love in Ratnagiri', 'mango, alphonso mango', 'yes'),
            (28, 1, 'Ansh Custard Apple', '3', 'Custard Apple', '2026-04-15', 'custardapple.jpg', 500, 45, 'Custard Apple super sweet and tasty', 'custard apple', 'yes'),
            (29, 3, 'Omkar Cabbage', '2', 'Cabbage', '2026-04-15', 'Cabbage.jpg', 1500, 30, 'Fresh green organic cabbage', 'cabbage', 'yes'),
            (30, 1, 'Ansh Onion', '2', 'Onion', '2026-04-15', 'Onion.jpg', 1500, 35, 'Fresh local onions', 'onion, best onion', 'no'),
            (31, 1, 'Abhi Strawberry', '3', 'Strawberry', '2026-04-15', 'strawberry.jpg', 100, 50, 'Sweet organic strawberries', 'strawberry', 'yes'),
            (32, 1, 'Abhi Orange', '3', 'Orange', '2026-04-15', 'orange.jpg', 1500, 20, 'Juicy Nagpur oranges', 'orange', 'yes'),
            (37, 1, 'Ram Sugarcane', '1', 'Sugarcane', '2026-04-25', 'Sugarcane.jpg', 1000, 25, 'Best natural sugarcane', 'sugarcane', 'yes')
        ]
        cursor.executemany("INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", products_data)

    def get_all_products(self, category=None, max_price=None, search_query=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM products WHERE 1=1"
            params = []

            if category:
                query += " AND (product_cat = ? OR product_type LIKE ?)"
                params.extend([category, f"%{category}%"])
            if max_price:
                query += " AND product_price <= ?"
                params.append(max_price)
            if search_query:
                query += " AND (product_title LIKE ? OR product_type LIKE ? OR product_keywords LIKE ?)"
                params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_product_by_name(self, name):
        if not name:
            return None
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE LOWER(product_type) LIKE ? OR LOWER(product_title) LIKE ? LIMIT 1",
                (f"%{name.lower()}%", f"%{name.lower()}%")
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # Shopping List Methods
    def get_shopping_list(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM voice_shopping_list ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_to_shopping_list(self, item_name, quantity=1, unit='items', category='General', price=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check if item exists in shopping list
            cursor.execute("SELECT id, quantity FROM voice_shopping_list WHERE LOWER(item_name) = ?", (item_name.lower(),))
            row = cursor.fetchone()
            if row:
                new_qty = row["quantity"] + quantity
                cursor.execute("UPDATE voice_shopping_list SET quantity = ?, price = ? WHERE id = ?", (new_qty, price, row["id"]))
                item_id = row["id"]
            else:
                cursor.execute(
                    "INSERT INTO voice_shopping_list (item_name, quantity, unit, category, price) VALUES (?, ?, ?, ?, ?)",
                    (item_name, quantity, unit or 'items', category or 'General', price)
                )
                item_id = cursor.lastrowid
            conn.commit()
            return item_id

    def remove_from_shopping_list(self, item_name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM voice_shopping_list WHERE LOWER(item_name) LIKE ?", (f"%{item_name.lower()}%",))
            deleted = cursor.rowcount
            conn.commit()
            return deleted > 0

    def clear_shopping_list(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM voice_shopping_list")
            conn.commit()

    # Cart Methods
    def get_cart(self, phone=8169193101):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.product_id, c.qty, c.subtotal, p.product_title, p.product_type, p.product_price, p.product_image
                FROM cart c
                JOIN products p ON c.product_id = p.product_id
                WHERE c.phonenumber = ?
            """, (phone,))
            return [dict(row) for row in cursor.fetchall()]

    def add_to_cart(self, product_id, qty=1, phone=8169193101):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT product_price FROM products WHERE product_id = ?", (product_id,))
            prod = cursor.fetchone()
            if not prod:
                return False
            unit_price = prod["product_price"]

            cursor.execute("SELECT id, qty FROM cart WHERE product_id = ? AND phonenumber = ?", (product_id, phone))
            cart_item = cursor.fetchone()

            if cart_item:
                new_qty = cart_item["qty"] + qty
                subtotal = new_qty * unit_price
                cursor.execute("UPDATE cart SET qty = ?, subtotal = ? WHERE id = ?", (new_qty, subtotal, cart_item["id"]))
            else:
                subtotal = qty * unit_price
                cursor.execute(
                    "INSERT INTO cart (product_id, phonenumber, qty, subtotal) VALUES (?, ?, ?, ?)",
                    (product_id, phone, qty, subtotal)
                )
            conn.commit()
            return True

    def remove_from_cart(self, cart_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
            conn.commit()
            return True
