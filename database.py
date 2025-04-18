import sqlite3
import hashlib
import os
import time
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_file="Database.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_file}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def create_tables(self):
        """Create tables if they don't exist."""
        try:
            # Create admins table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create users table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create restaurants table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                name TEXT NOT NULL,
                address TEXT,
                phone_number TEXT,
                email TEXT,
                rating DECIMAL(2,1) DEFAULT 0.0,
                total_ratings INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES admins (admin_id)
            )
            ''')
            
            # Create restaurant_locations table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurant_locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id INTEGER NOT NULL,
                address TEXT NOT NULL,
                opening_hours TEXT,
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
            )
            ''')
            
            # Create menu_categories table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                item_count INTEGER DEFAULT 0,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
            )
            ''')
            
            # Create menu_items table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id INTEGER NOT NULL,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id),
                FOREIGN KEY (category_id) REFERENCES menu_categories (category_id)
            )
            ''')
            
            # Create cart_items table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                restaurant_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (item_id) REFERENCES menu_items (item_id),
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
            )
            ''')
            
            # Create orders table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                restaurant_id INTEGER NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                shipping_cost DECIMAL(10,2),
                order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                order_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
            )
            ''')
            
            # Create order_items table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                price DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (item_id) REFERENCES menu_items (item_id)
            )
            ''')
            
            # Create payments table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                payment_method TEXT,
                transaction_id TEXT,
                amount DECIMAL(10,2) NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (order_id)
            )
            ''')
            
            # Create ratings table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                rating_value INTEGER CHECK (rating_value BETWEEN 1 AND 5),
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            ''')
            self.setup_rating_triggers()
            self.conn.commit()
            print("Tables created successfully")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
    
    def generate_salt(self):
        """Generate a random salt for password hashing."""
        return os.urandom(32).hex()
    
    def hash_password(self, password, salt):
        """Hash the password with the salt using SHA-256."""
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode('utf-8'))
        return hash_obj.hexdigest()
    
    def register_user(self, username, password, email, phone_number=None):
        """Register a new user with a salted password."""
        try:
            # Check if user already exists
            self.cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
            if self.cursor.fetchone():
                return False, "Username or email already exists"
            
            # Generate salt and hash password
            salt = self.generate_salt()
            hashed_password = self.hash_password(password, salt)
            
            # Insert user into database
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO users (username, password, salt, email, phone_number, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username, hashed_password, salt, email, phone_number, current_time, current_time)
            )
            self.conn.commit()
            return True, "User registered successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Registration error: {e}"
    
    def register_admin(self, username, password, email):
        """Register a new admin with a salted password."""
        try:
            # Check if admin already exists
            self.cursor.execute("SELECT * FROM admins WHERE username = ? OR email = ?", (username, email))
            if self.cursor.fetchone():
                return False, "Admin username or email already exists"
            
            # Generate salt and hash password
            salt = self.generate_salt()
            hashed_password = self.hash_password(password, salt)
            
            # Insert admin into database
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO admins (username, password, salt, email, created_at) VALUES (?, ?, ?, ?, ?)",
                (username, hashed_password, salt, email, current_time)
            )
            self.conn.commit()
            return True, "Admin registered successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Admin registration error: {e}"
    
    def verify_user_login(self, email, password):
        """Verify user login credentials."""
        try:
            self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = self.cursor.fetchone()
            
            if not user:
                return False, "User not found"
            
            stored_password = user['password']
            salt = user['salt']
            
            # Hash the provided password with stored salt
            hashed_password = self.hash_password(password, salt)
            
            if hashed_password == stored_password:
                # Convert row to dictionary
                user_dict = dict(user)
                return True, user_dict
            else:
                return False, "Invalid password"
        except sqlite3.Error as e:
            return False, f"Login error: {e}"
    
    def verify_admin_login(self, email, password):
        """Verify admin login credentials."""
        try:
            self.cursor.execute("SELECT * FROM admins WHERE email = ?", (email,))
            admin = self.cursor.fetchone()
            
            if not admin:
                return False, "Admin not found"
            
            stored_password = admin['password']
            salt = admin['salt']
            
            # Hash the provided password with stored salt
            hashed_password = self.hash_password(password, salt)
            
            if hashed_password == stored_password:
                # Convert row to dictionary
                admin_dict = dict(admin)
                return True, admin_dict
            else:
                return False, "Invalid password"
        except sqlite3.Error as e:
            return False, f"Admin login error: {e}"
    
    # CRUD operations for admins
    def get_all_admins(self):
        """Get all admins from the database."""
        try:
            self.cursor.execute("SELECT * FROM admins")
            admins = [dict(row) for row in self.cursor.fetchall()]
            return admins
        except sqlite3.Error as e:
            print(f"Error fetching admins: {e}")
            return []
    
    def add_admin(self, username, password, email):
        """Add a new admin."""
        try:
            # Generate salt and hash password
            salt = self.generate_salt()
            hashed_password = self.hash_password(password, salt)
            
            self.cursor.execute(
                "INSERT INTO admins (username, password, salt, email) VALUES (?, ?, ?, ?)",
                (username, hashed_password, salt, email)
            )
            self.conn.commit()
            return True, "Admin added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding admin: {e}"
    
    def update_admin(self, admin_id, username=None, email=None):
        """Update admin information."""
        try:
            update_fields = []
            params = []
            
            if username:
                update_fields.append("username = ?")
                params.append(username)
            
            if email:
                update_fields.append("email = ?")
                params.append(email)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Add admin_id to params
            params.append(admin_id)
            
            query = f"UPDATE admins SET {', '.join(update_fields)} WHERE admin_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Admin updated successfully"
            else:
                return False, "Admin not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_admin(self, admin_id):
        """Delete an admin from the database."""
        try:
            self.cursor.execute("DELETE FROM admins WHERE admin_id = ?", (admin_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Admin deleted successfully"
            else:
                return False, "Admin not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for users
    def get_all_users(self):
        """Get all users from the database."""
        try:
            self.cursor.execute("SELECT * FROM users")
            users = [dict(row) for row in self.cursor.fetchall()]
            return users
        except sqlite3.Error as e:
            print(f"Error fetching users: {e}")
            return []
    
    def add_user(self, username, password, email, phone_number=None):
        """Add a new user."""
        try:
            # Generate salt and hash password
            salt = self.generate_salt()
            hashed_password = self.hash_password(password, salt)
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO users (username, password, salt, email, phone_number, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username, hashed_password, salt, email, phone_number, current_time, current_time)
            )
            self.conn.commit()
            return True, "User added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding user: {e}"
    
    def update_user(self, user_id, username=None, email=None, phone_number=None):
        """Update user information."""
        try:
            update_fields = []
            params = []
            
            if username:
                update_fields.append("username = ?")
                params.append(username)
            
            if email:
                update_fields.append("email = ?")
                params.append(email)
            
            if phone_number:
                update_fields.append("phone_number = ?")
                params.append(phone_number)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Add user_id to params
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "User updated successfully"
            else:
                return False, "User not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_user(self, user_id):
        """Delete a user from the database."""
        try:
            self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "User deleted successfully"
            else:
                return False, "User not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for restaurants
    def get_all_restaurants(self):
        """Get all restaurants from the database."""
        try:
            self.cursor.execute("SELECT * FROM restaurants")
            restaurants = [dict(row) for row in self.cursor.fetchall()]
            return restaurants
        except sqlite3.Error as e:
            print(f"Error fetching restaurants: {e}")
            return []
    
    def add_restaurant(self, admin_id, name, address, phone_number, email):
        """Add a new restaurant."""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO restaurants (admin_id, name, address, phone_number, email, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (admin_id, name, address, phone_number, email, current_time, current_time)
            )
            self.conn.commit()
            return True, "Restaurant added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding restaurant: {e}"
    
    def update_restaurant(self, restaurant_id, admin_id=None, name=None, address=None, phone_number=None, email=None, rating=None, total_ratings=None):
        """Update restaurant information."""
        try:
            update_fields = []
            params = []
            
            if admin_id:
                update_fields.append("admin_id = ?")
                params.append(admin_id)
            
            if name:
                update_fields.append("name = ?")
                params.append(name)
            
            if address:
                update_fields.append("address = ?")
                params.append(address)
            
            if phone_number:
                update_fields.append("phone_number = ?")
                params.append(phone_number)
            
            if email:
                update_fields.append("email = ?")
                params.append(email)
            
            if rating is not None:  # Check if rating is provided
                update_fields.append("rating = ?")
                params.append(rating)
            
            if total_ratings is not None:  # Check if total_ratings is provided
                update_fields.append("total_ratings = ?")
                params.append(total_ratings)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Add restaurant_id to params
            params.append(restaurant_id)
            
            query = f"UPDATE restaurants SET {', '.join(update_fields)} WHERE restaurant_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Restaurant updated successfully"
            else:
                return False, "Restaurant not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_restaurant(self, restaurant_id):
        """Delete a restaurant from the database."""
        try:
            self.cursor.execute("DELETE FROM restaurants WHERE restaurant_id = ?", (restaurant_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Restaurant deleted successfully"
            else:
                return False, "Restaurant not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for restaurant locations
    def get_all_restaurant_locations(self):
        """Get all restaurant locations from the database."""
        try:
            self.cursor.execute("SELECT * FROM restaurant_locations")
            locations = [dict(row) for row in self.cursor.fetchall()]
            return locations
        except sqlite3.Error as e:
            print(f"Error fetching restaurant locations: {e}")
            return []
    
    def add_restaurant_location(self, restaurant_id, address, opening_hours, latitude, longitude):
        """Add a new restaurant location."""
        try:
            self.cursor.execute(
                "INSERT INTO restaurant_locations (restaurant_id, address, opening_hours, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
                (restaurant_id, address, opening_hours, latitude, longitude)
            )
            self.conn.commit()
            return True, "Restaurant location added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding restaurant location: {e}"
    
    def update_restaurant_location(self, location_id, restaurant_id=None, address=None, opening_hours=None, latitude=None, longitude=None):
        """Update restaurant location information."""
        try:
            update_fields = []
            params = []
            
            if restaurant_id:
                update_fields.append("restaurant_id = ?")
                params.append(restaurant_id)
            
            if address:
                update_fields.append("address = ?")
                params.append(address)
            
            if opening_hours:
                update_fields.append("opening_hours = ?")
                params.append(opening_hours)
            
            if latitude:
                update_fields.append("latitude = ?")
                params.append(latitude)
            
            if longitude:
                update_fields.append("longitude = ?")
                params.append(longitude)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add location_id to params
            params.append(location_id)
            
            query = f"UPDATE restaurant_locations SET {', '.join(update_fields)} WHERE location_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Restaurant location updated successfully"
            else:
                return False, "Restaurant location not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_restaurant_location(self, location_id):
        """Delete a restaurant location from the database."""
        try:
            self.cursor.execute("DELETE FROM restaurant_locations WHERE location_id = ?", (location_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Restaurant location deleted successfully"
            else:
                return False, "Restaurant location not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for menu categories
    def get_all_menu_categories(self):
        """Get all menu categories from the database."""
        try:
            self.cursor.execute("SELECT * FROM menu_categories")
            categories = [dict(row) for row in self.cursor.fetchall()]
            return categories
        except sqlite3.Error as e:
            print(f"Error fetching menu categories: {e}")
            return []
    
    def add_menu_category(self, restaurant_id, name):
        """Add a new menu category."""
        try:
            self.cursor.execute(
                "INSERT INTO menu_categories (restaurant_id, name) VALUES (?, ?)",
                (restaurant_id, name)
            )
            self.conn.commit()
            return True, "Menu category added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding menu category: {e}"
    
    def update_menu_category(self, category_id, restaurant_id=None, name=None):
        """Update menu category information."""
        try:
            update_fields = []
            params = []
            
            if restaurant_id:
                update_fields.append("restaurant_id = ?")
                params.append(restaurant_id)
            
            if name:
                update_fields.append("name = ?")
                params.append(name)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add category_id to params
            params.append(category_id)
            
            query = f"UPDATE menu_categories SET {', '.join(update_fields)} WHERE category_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Menu category updated successfully"
            else:
                return False, "Menu category not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_menu_category(self, category_id):
        """Delete a menu category from the database."""
        try:
            self.cursor.execute("DELETE FROM menu_categories WHERE category_id = ?", (category_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Menu category deleted successfully"
            else:
                return False, "Menu category not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for menu items
    def get_all_menu_items(self):
        """Get all menu items from the database."""
        try:
            self.cursor.execute("SELECT * FROM menu_items")
            items = [dict(row) for row in self.cursor.fetchall()]
            return items
        except sqlite3.Error as e:
            print(f"Error fetching menu items: {e}")
            return []
    
    def add_menu_item(self, restaurant_id, category_id, name, description, price):
        """Add a new menu item."""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO menu_items (restaurant_id, category_id, name, description, price, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (restaurant_id, category_id, name, description, price, current_time)
            )
            self.conn.commit()
            return True, "Menu item added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding menu item: {e}"
    
    def update_menu_item(self, item_id, restaurant_id=None, category_id=None, name=None, description=None, price=None):
        """Update menu item information."""
        try:
            update_fields = []
            params = []
            
            if restaurant_id:
                update_fields.append("restaurant_id = ?")
                params.append(restaurant_id)
            
            if category_id:
                update_fields.append("category_id = ?")
                params.append(category_id)
            
            if name:
                update_fields.append("name = ?")
                params.append(name)
            
            if description:
                update_fields.append("description = ?")
                params.append(description)
            
            if price:
                update_fields.append("price = ?")
                params.append(price)
            
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add item_id to params
            params.append(item_id)
            
            query = f"UPDATE menu_items SET {', '.join(update_fields)} WHERE item_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Menu item updated successfully"
            else:
                return False, "Menu item not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_menu_item(self, item_id):
        """Delete a menu item from the database."""
        try:
            self.cursor.execute("DELETE FROM menu_items WHERE item_id = ?", (item_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Menu item deleted successfully"
            else:
                return False, "Menu item not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for cart items
    def get_all_cart_items(self):
        """Get all cart items from the database."""
        try:
            self.cursor.execute("SELECT * FROM cart_items")
            cart_items = [dict(row) for row in self.cursor.fetchall()]
            return cart_items
        except sqlite3.Error as e:
            print(f"Error fetching cart items: {e}")
            return []
    
    def add_cart_item(self, user_id, item_id, restaurant_id, quantity=1):
        """Add a new cart item."""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO cart_items (user_id, item_id, restaurant_id, quantity, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, item_id, restaurant_id, quantity, current_time)
            )
            self.conn.commit()
            return True, "Cart item added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding cart item: {e}"
    
    def update_cart_item(self, cart_item_id, user_id=None, item_id=None, restaurant_id=None, quantity=None):
        """Update cart item information."""
        try:
            update_fields = []
            params = []
            
            if user_id:
                update_fields.append("user_id = ?")
                params.append(user_id)
            
            if item_id:
                update_fields.append("item_id = ?")
                params.append(item_id)
            
            if restaurant_id:
                update_fields.append("restaurant_id = ?")
                params.append(restaurant_id)
            
            if quantity:
                update_fields.append("quantity = ?")
                params.append(quantity)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add cart_item_id to params
            params.append(cart_item_id)
            
            query = f"UPDATE cart_items SET {', '.join(update_fields)} WHERE cart_item_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Cart item updated successfully"
            else:
                return False, "Cart item not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_cart_item(self, cart_item_id):
        """Delete a cart item from the database."""
        try:
            self.cursor.execute("DELETE FROM cart_items WHERE cart_item_id = ?", (cart_item_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Cart item deleted successfully"
            else:
                return False, "Cart item not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for orders
    def get_all_orders(self):
        """Get all orders from the database."""
        try:
            self.cursor.execute("SELECT * FROM orders")
            orders = [dict(row) for row in self.cursor.fetchall()]
            return orders
        except sqlite3.Error as e:
            print(f"Error fetching orders: {e}")
            return []
    
    def add_order(self, user_id, restaurant_id, total_amount, shipping_cost, status='pending', order_type=None):
        """Add a new order."""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO orders (user_id, restaurant_id, total_amount, shipping_cost, status, order_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, restaurant_id, total_amount, shipping_cost, status, order_type, current_time)
            )
            self.conn.commit()
            return True, "Order added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding order: {e}"
    
    def update_order(self, order_id, user_id=None, restaurant_id=None, total_amount=None, shipping_cost=None, status=None, order_type=None):
        """Update order information."""
        try:
            update_fields = []
            params = []
            
            if user_id:
                update_fields.append("user_id = ?")
                params.append(user_id)
            
            if restaurant_id:
                update_fields.append("restaurant_id = ?")
                params.append(restaurant_id)
            
            if total_amount:
                update_fields.append("total_amount = ?")
                params.append(total_amount)
            
            if shipping_cost:
                update_fields.append("shipping_cost = ?")
                params.append(shipping_cost)
            
            if status:
                update_fields.append("status = ?")
                params.append(status)
            
            if order_type:
                update_fields.append("order_type = ?")
                params.append(order_type)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add updated_at timestamp
            update_fields.append("updated_at = ?")
            params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Add order_id to params
            params.append(order_id)
            
            query = f"UPDATE orders SET {', '.join(update_fields)} WHERE order_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Order updated successfully"
            else:
                return False, "Order not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_order(self, order_id):
        """Delete an order from the database."""
        try:
            self.cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Order deleted successfully"
            else:
                return False, "Order not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for order items
    def get_all_order_items(self):
        """Get all order items from the database."""
        try:
            self.cursor.execute("SELECT * FROM order_items")
            order_items = [dict(row) for row in self.cursor.fetchall()]
            return order_items
        except sqlite3.Error as e:
            print(f"Error fetching order items: {e}")
            return []
    
    def add_order_item(self, order_id, item_id, quantity=1, price=None):
        """Add a new order item."""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO order_items (order_id, item_id, quantity, price, created_at) VALUES (?, ?, ?, ?, ?)",
                (order_id, item_id, quantity, price, current_time)
            )
            self.conn.commit()
            return True, "Order item added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding order item: {e}"
    
    def update_order_item(self, order_item_id, order_id=None, item_id=None, quantity=None, price=None):
        """Update order item information."""
        try:
            update_fields = []
            params = []
            
            if order_id:
                update_fields.append("order_id = ?")
                params.append(order_id)
            
            if item_id:
                update_fields.append("item_id = ?")
                params.append(item_id)
            
            if quantity:
                update_fields.append("quantity = ?")
                params.append(quantity)
            
            if price:
                update_fields.append("price = ?")
                params.append(price)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add order_item_id to params
            params.append(order_item_id)
            
            query = f"UPDATE order_items SET {', '.join(update_fields)} WHERE order_item_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Order item updated successfully"
            else:
                return False, "Order item not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_order_item(self, order_item_id):
        """Delete an order item from the database."""
        try:
            self.cursor.execute("DELETE FROM order_items WHERE order_item_id = ?", (order_item_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Order item deleted successfully"
            else:
                return False, "Order item not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for payments
    def get_all_payments(self):
        """Get all payments from the database."""
        try:
            self.cursor.execute("SELECT * FROM payments")
            payments = [dict(row) for row in self.cursor.fetchall()]
            return payments
        except sqlite3.Error as e:
            print(f"Error fetching payments: {e}")
            return []
    
    def add_payment(self, order_id, payment_method, transaction_id, amount, status='pending'):
        """Add a new payment."""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO payments (order_id, payment_method, transaction_id, amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (order_id, payment_method, transaction_id, amount, status, current_time)
            )
            self.conn.commit()
            return True, "Payment added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding payment: {e}"
    
    def update_payment(self, payment_id, order_id=None, payment_method=None, transaction_id=None, amount=None, status=None):
        """Update payment information."""
        try:
            update_fields = []
            params = []
            
            if order_id:
                update_fields.append("order_id = ?")
                params.append(order_id)
            
            if payment_method:
                update_fields.append("payment_method = ?")
                params.append(payment_method)
            
            if transaction_id:
                update_fields.append("transaction_id = ?")
                params.append(transaction_id)
            
            if amount:
                update_fields.append("amount = ?")
                params.append(amount)
            
            if status:
                update_fields.append("status = ?")
                params.append(status)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add payment_id to params
            params.append(payment_id)
            
            query = f"UPDATE payments SET {', '.join(update_fields)} WHERE payment_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Payment updated successfully"
            else:
                return False, "Payment not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_payment(self, payment_id):
        """Delete a payment from the database."""
        try:
            self.cursor.execute("DELETE FROM payments WHERE payment_id = ?", (payment_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Payment deleted successfully"
            else:
                return False, "Payment not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # CRUD operations for ratings
    def get_all_ratings(self):
        """Get all ratings from the database."""
        try:
            self.cursor.execute("SELECT * FROM ratings")
            ratings = [dict(row) for row in self.cursor.fetchall()]
            return ratings
        except sqlite3.Error as e:
            print(f"Error fetching ratings: {e}")
            return []
    
    def add_rating(self, restaurant_id, user_id, rating_value, review=None):
        """Add a new rating."""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                "INSERT INTO ratings (restaurant_id, user_id, rating_value, review, created_at) VALUES (?, ?, ?, ?, ?)",
                (restaurant_id, user_id, rating_value, review, current_time)
            )
            self.conn.commit()
            return True, "Rating added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding rating: {e}"
    
    def update_rating(self, rating_id, restaurant_id=None, user_id=None, rating_value=None, review=None):
        """Update rating information."""
        try:
            update_fields = []
            params = []
            
            if restaurant_id:
                update_fields.append("restaurant_id = ?")
                params.append(restaurant_id)
            
            if user_id:
                update_fields.append("user_id = ?")
                params.append(user_id)
            
            if rating_value:
                update_fields.append("rating_value = ?")
                params.append(rating_value)
            
            if review:
                update_fields.append("review = ?")
                params.append(review)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add rating_id to params
            params.append(rating_id)
            
            query = f"UPDATE ratings SET {', '.join(update_fields)} WHERE rating_id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Rating updated successfully"
            else:
                return False, "Rating not found or no changes made"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Update error: {e}"
    
    def delete_rating(self, rating_id):
        """Delete a rating from the database."""
        try:
            self.cursor.execute("DELETE FROM ratings WHERE rating_id = ?", (rating_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Rating deleted successfully"
            else:
                return False, "Rating not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Delete error: {e}"
    
    # Function to print all data from a table
    def print_table_data(self, table_name):
        """Print all data from a specific table."""
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            
            if not rows:
                print(f"No data found in {table_name}")
                return
            
            # Get column names
            columns = [description[0] for description in self.cursor.description]
            
            # Print column headers
            print(f"\nData in {table_name}:")
            print(", ".join(columns))
            
            # Print rows
            for row in rows:
                row_data = []
                for column in columns:
                    row_data.append(str(row[column]))
                print(", ".join(row_data))
            
        except sqlite3.Error as e:
            print(f"Error fetching data from {table_name}: {e}")
    
    def get_restaurants_with_ratings(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT name, rating FROM restaurants")  # Removed cuisine from the query
            rows = cursor.fetchall()
            restaurants = [{"name": row[0], "rating": row[1]} for row in rows]
            return restaurants
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def setup_rating_triggers(self):
        """Set up triggers to automatically update restaurant ratings."""
        try:
            # Drop existing triggers if they exist
            self.cursor.execute("DROP TRIGGER IF EXISTS after_rating_insert")
            self.cursor.execute("DROP TRIGGER IF EXISTS after_rating_update")
            self.cursor.execute("DROP TRIGGER IF EXISTS after_rating_delete")

            # Create trigger for INSERT operation on ratings table
            self.cursor.execute('''
                CREATE TRIGGER after_rating_insert
                AFTER INSERT ON ratings
                BEGIN
                    UPDATE restaurants
                    SET rating = COALESCE((SELECT AVG(rating_value) FROM ratings WHERE restaurant_id = NEW.restaurant_id), 0.0)
                    WHERE restaurant_id = NEW.restaurant_id;
                END;
            ''')

            # Create trigger for UPDATE operation on ratings table
            self.cursor.execute('''
                CREATE TRIGGER after_rating_update
                AFTER UPDATE ON ratings
                BEGIN
                    -- Update old restaurant's rating
                    UPDATE restaurants
                    SET rating = COALESCE((SELECT AVG(rating_value) FROM ratings WHERE restaurant_id = OLD.restaurant_id), 0.0)
                    WHERE restaurant_id = OLD.restaurant_id;
                    
                    -- Update new restaurant's rating
                    UPDATE restaurants
                    SET rating = COALESCE((SELECT AVG(rating_value) FROM ratings WHERE restaurant_id = NEW.restaurant_id), 0.0)
                    WHERE restaurant_id = NEW.restaurant_id;
                END;
            ''')

            # Create trigger for DELETE operation on ratings table
            self.cursor.execute('''
                CREATE TRIGGER after_rating_delete
                AFTER DELETE ON ratings
                BEGIN
                    UPDATE restaurants
                    SET rating = COALESCE((SELECT AVG(rating_value) FROM ratings WHERE restaurant_id = OLD.restaurant_id), 0.0)
                    WHERE restaurant_id = OLD.restaurant_id;
                END;
            ''')

            self.conn.commit()
            print("Rating triggers created successfully")
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error creating rating triggers: {e}")
    def insert_ratings_to_match_restaurant_ratings(self):
        """Insert ratings into the ratings table such that the average matches the restaurant's rating."""
        try:
            # Fetch all restaurants
            self.cursor.execute("SELECT * FROM restaurants")
            restaurants = self.cursor.fetchall()

            # Fetch all users to use as raters
            self.cursor.execute("SELECT user_id FROM users")
            users = [row['user_id'] for row in self.cursor.fetchall()]

            for restaurant in restaurants:
                restaurant_id = restaurant['restaurant_id']
                target_rating = restaurant['rating']
                total_ratings = restaurant['total_ratings']

                # Calculate the sum of ratings needed to achieve the target average
                total_rating_sum = target_rating * total_ratings

                # Generate ratings that sum up to total_rating_sum
                # Distribute the ratings as evenly as possible among users
                ratings_to_insert = []
                for i in range(total_ratings):
                    # Assign ratings to users in a round-robin fashion
                    user_id = users[i % len(users)]
                    # For simplicity, distribute the exact rating value
                    # In a real scenario, you might want to vary the ratings but ensure the average matches
                    rating_value = target_rating
                    ratings_to_insert.append((restaurant_id, user_id, rating_value, None))  # None for review

                # Insert the generated ratings
                self.cursor.executemany(
                    "INSERT INTO ratings (restaurant_id, user_id, rating_value, review) VALUES (?, ?, ?, ?)",
                    ratings_to_insert
                )

            self.conn.commit()
            print("Ratings inserted successfully to match restaurant ratings")
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error inserting ratings: {e}")
    def insert_restaurant_locations(self):
        """Insert sample data into the restaurant_locations table."""
        try:
            # Sample data for restaurant locations
            locations_data = [
                (1, 1, "Main Street, Manipal", "Mon-Sun 9:00-23:00", 12.9142, 74.8540),
                (2, 2, "City Center, Manipal", "Mon-Sun 10:00-22:30", 12.9212, 74.8612),
                (3, 3, "East Avenue, Manipal", "Mon-Sun 8:00-22:00", 12.9178, 74.8523),
                (4, 4, "West Street, Manipal", "Mon-Sun 11:00-23:30", 12.9156, 74.8578),
                (5, 5, "North Road, Manipal", "Mon-Sun 9:30-22:30", 12.9201, 74.8555),
                (6, 6, "South Avenue, Manipal", "Mon-Sun 10:30-23:00", 12.9189, 74.8592),
            ]

            # Insert the data into the restaurant_locations table
            self.cursor.executemany(
                """
                INSERT INTO restaurant_locations 
                (location_id, restaurant_id, address, opening_hours, latitude, longitude) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                locations_data,
            )

            self.conn.commit()
            print("Restaurant locations inserted successfully")
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error inserting restaurant locations: {e}")
    def insert_menu_categories_and_items(self):
        """Insert sample data into menu_categories and menu_items tables."""
        try:
            # Sample data for menu categories
            categories_data = [
                (1, "Burgers"),
                (1, "Fries"),
                (1, "Shakes"),
                (2, "Burgers"),
                (2, "Fries"),
                (2, "Drinks"),
                (3, "Breakfast"),
                (3, "Lunch"),
                (3, "Dinner"),
                (4, "Sushi"),
                (4, "Ramen"),
                (4, "Appetizers"),
                (5, "Vegetarian"),
                (5, "Non-Vegetarian"),
                (5, "Desserts"),
                (6, "Punjabi Main Course"),
                (6, "Appetizers"),
                (6, "Desserts"),
            ]

            # Insert menu categories
            self.cursor.executemany(
                "INSERT INTO menu_categories (restaurant_id, name) VALUES (?, ?)",
                categories_data,
            )

            # Sample data for menu items
            items_data = [
                # MCD (restaurant_id 1)
                (1, 1, "Classic Cheeseburger", "Juicy beef patty with cheese", 120.00),
                (1, 1, "Big Mac", "Two beef patties with special sauce", 150.00),
                (1, 2, "Large Fries", "Crispy golden fries", 80.00),
                (1, 3, "McFloat", "Ice cream float with soda", 60.00),
                
                # Burger King (restaurant_id 2)
                (2, 4, "Whopper", "Beef patty with lettuce and tomato", 130.00),
                (2, 4, "Chicken Burger", "Crispy chicken patty", 140.00),
                (2, 5, "Crinkle Cut Fries", "Golden crispy fries", 70.00),
                (2, 6, "Fanta", "Refreshing citrus drink", 40.00),
                
                # Pai Tiffins (restaurant_id 3)
                (3, 7, "Idli Sambar", "South Indian breakfast", 80.00),
                (3, 7, "Dosa", "Crispy rice crepe", 90.00),
                (3, 8, "Masala Rice", "Spiced rice with vegetables", 120.00),
                (3, 9, "Pongal", "South Indian rice dish", 100.00),
                
                # Kyoto (restaurant_id 4)
                (4, 10, "California Roll", "Sushi roll with crab and avocado", 250.00),
                (4, 10, "Spicy Tuna Roll", "Spicy tuna sushi roll", 280.00),
                (4, 11, "Beef Ramen", "Noodle soup with beef", 220.00),
                (4, 12, "Edamame", "Steamed soybeans", 80.00),
                
                # Madhuvan Veg (restaurant_id 5)
                (5, 13, "Paneer Tikka", "Grilled cottage cheese", 180.00),
                (5, 13, "Veg Biryani", "Spiced rice with vegetables", 200.00),
                (5, 14, "Chicken Curry", "Spiced chicken dish", 220.00),
                (5, 15, "Gulab Jamun", "Sweet dessert", 70.00),
                
                # Tawa Punjab (restaurant_id 6)
                (6, 16, "Butter Chicken", "Tandoori chicken in butter sauce", 240.00),
                (6, 16, "Dal Makhani", "Creamy black lentil dish", 190.00),
                (6, 17, "Naan", "Grilled flatbread", 60.00),
                (6, 18, "Kheer", "Rice pudding dessert", 80.00),
            ]

            # Insert menu items
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            menu_items = []
            for item in items_data:
                menu_items.append((
                    item[0],  # restaurant_id
                    item[1],  # category_id
                    item[2],  # name
                    item[3],  # description
                    item[4],  # price
                    current_time  # created_at
                ))

            self.cursor.executemany(
                """
                INSERT INTO menu_items 
                (restaurant_id, category_id, name, description, price, created_at) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                menu_items,
            )

            self.conn.commit()
            print("Menu categories and items inserted successfully")
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error inserting menu categories and items: {e}")
    def insert_new_restaurant(self, admin_id, name, address, phone_number, email, categories_and_items):
        """
        Insert a new restaurant along with its menu categories and items.

        Parameters:
        admin_id (int): Admin ID for the restaurant
        name (str): Name of the restaurant
        address (str): Address of the restaurant
        phone_number (str): Phone number of the restaurant
        email (str): Email of the restaurant
        categories_and_items (list): List of tuples containing category and item information.
            Each tuple should be in the format:
            (category_name, [(item_name, item_description, item_price), ...])
        """
        try:
            # Insert restaurant
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                """
                INSERT INTO restaurants 
                (admin_id, name, address, phone_number, email, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (admin_id, name, address, phone_number, email, current_time, current_time)
            )
            restaurant_id = self.cursor.lastrowid

            # Insert menu categories and items
            for category_name, items in categories_and_items:
                # Insert category
                self.cursor.execute(
                    "INSERT INTO menu_categories (restaurant_id, name) VALUES (?, ?)",
                    (restaurant_id, category_name)
                )
                category_id = self.cursor.lastrowid

                # Insert items
                for item_name, item_description, item_price in items:
                    self.cursor.execute(
                        """
                        INSERT INTO menu_items 
                        (restaurant_id, category_id, name, description, price, created_at) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (restaurant_id, category_id, item_name, item_description, item_price, current_time)
                    )

            self.conn.commit()
            print("New restaurant and menu items added successfully")
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error adding new restaurant: {e}")
            return False
        
    def setup_rating_triggers(self):
        """Set up triggers to automatically update restaurant ratings."""
        try:
            # Drop existing triggers if they exist
            self.cursor.execute("DROP TRIGGER IF EXISTS after_rating_insert")
            self.cursor.execute("DROP TRIGGER IF EXISTS after_rating_update")
            self.cursor.execute("DROP TRIGGER IF EXISTS after_rating_delete")
            
            # Create trigger for INSERT operation on ratings table
            self.cursor.execute('''
            CREATE TRIGGER after_rating_insert
            AFTER INSERT ON ratings
            BEGIN
                UPDATE restaurants
                SET rating = (SELECT AVG(rating_value) FROM ratings WHERE restaurant_id = NEW.restaurant_id),
                    total_ratings = (SELECT COUNT(*) FROM ratings WHERE restaurant_id = NEW.restaurant_id)
                WHERE restaurant_id = NEW.restaurant_id;
            END;
            ''')
            
            # Create trigger for UPDATE operation on ratings table
            self.cursor.execute('''
            CREATE TRIGGER after_rating_update
            AFTER UPDATE ON ratings
            BEGIN
                -- Update restaurant's rating
                UPDATE restaurants
                SET rating = (SELECT AVG(rating_value) FROM ratings WHERE restaurant_id = NEW.restaurant_id),
                    total_ratings = (SELECT COUNT(*) FROM ratings WHERE restaurant_id = NEW.restaurant_id)
                WHERE restaurant_id = NEW.restaurant_id;
            END;
            ''')
            
            # Create trigger for DELETE operation on ratings table
            self.cursor.execute('''
            CREATE TRIGGER after_rating_delete
            AFTER DELETE ON ratings
            BEGIN
                UPDATE restaurants
                SET rating = COALESCE((SELECT AVG(rating_value) FROM ratings WHERE restaurant_id = OLD.restaurant_id), 0.0),
                    total_ratings = (SELECT COUNT(*) FROM ratings WHERE restaurant_id = OLD.restaurant_id)
                WHERE restaurant_id = OLD.restaurant_id;
            END;
            ''')
            
            self.conn.commit()
            print("Rating triggers created successfully")
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error creating rating triggers: {e}")

    def remove_duplicate_menu_data(self):
        """
        Remove duplicate menu categories and menu items from the database.
        This function keeps only one instance of each unique category per restaurant
        and one instance of each unique menu item per category.
        """
        try:
            print("Starting duplicate removal process...")
            
            # Begin transaction
            self.cursor.execute("BEGIN TRANSACTION")
            
            # 1. First, identify and remove duplicate menu categories
            print("Removing duplicate menu categories...")
            self.cursor.execute("""
                DELETE FROM menu_categories
                WHERE category_id NOT IN (
                    SELECT MIN(category_id) 
                    FROM menu_categories 
                    GROUP BY restaurant_id, name
                )
            """)
            categories_removed = self.cursor.rowcount
            print(f"Removed {categories_removed} duplicate menu categories")
            
            # 2. Then, identify and remove duplicate menu items
            print("Removing duplicate menu items...")
            self.cursor.execute("""
                DELETE FROM menu_items
                WHERE item_id NOT IN (
                    SELECT MIN(item_id) 
                    FROM menu_items 
                    GROUP BY restaurant_id, category_id, name
                )
            """)
            items_removed = self.cursor.rowcount
            print(f"Removed {items_removed} duplicate menu items")
            
            # 3. Update item_count in menu_categories to reflect the current count
            print("Updating category item counts...")
            self.cursor.execute("""
                UPDATE menu_categories
                SET item_count = (
                    SELECT COUNT(*) 
                    FROM menu_items 
                    WHERE menu_items.category_id = menu_categories.category_id
                )
            """)
            
            # 4. Add unique constraints to prevent future duplicates
            print("Adding unique constraints to prevent future duplicates...")
            try:
                # Create unique index for menu_categories
                self.cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_restaurant_category
                    ON menu_categories (restaurant_id, name)
                """)
                
                # Create unique index for menu_items
                self.cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_menu_item
                    ON menu_items (restaurant_id, category_id, name)
                """)
            except sqlite3.Error as e:
                print(f"Warning: Could not create unique indexes: {e}")
                # Continue execution even if we can't create the indexes
            
            # Commit the transaction
            self.conn.commit()
            
            print("Duplicate removal completed successfully")
            return True, f"Successfully removed {categories_removed} duplicate categories and {items_removed} duplicate menu items"
        
        except sqlite3.Error as e:
            # Rollback in case of error
            self.conn.rollback()
            print(f"Error removing duplicates: {e}")
            return False, f"Error removing duplicates: {e}"
        
    # Add these methods to the DatabaseManager class

    def get_order_by_id(self, order_id):
        """Get order details by order ID"""
        try:
            self.cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            order = self.cursor.fetchone()
            return dict(order) if order else None
        except Exception as e:
            print(f"Error getting order: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Get user details by user ID"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = self.cursor.fetchone()
            return dict(user) if user else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def get_order_items(self, order_id):
        """Get items for a specific order"""
        try:
            self.cursor.execute("""
                SELECT oi.*, mi.name, mi.description, mi.price
                FROM order_items oi
                JOIN menu_items mi ON oi.item_id = mi.item_id
                WHERE oi.order_id = ?
            """, (order_id,))
            items = self.cursor.fetchall()
            return [dict(item) for item in items]
        except Exception as e:
            print(f"Error getting order items: {e}")
            return []

    def update_order_status(self, order_id, new_status):
        """Update the status of an order"""
        try:
            self.cursor.execute(
                "UPDATE orders SET status = ? WHERE order_id = ?",
                (new_status, order_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False




# Create an instance of DatabaseManager
db_manager = DatabaseManager()

tables = [
    "admins",
    "users",
    "restaurants",
    "restaurant_locations",
    "menu_categories",
    "menu_items",
    "cart_items",
    "orders",
    "order_items",
    "payments",
    "ratings"
]

for table in tables:
    print(f"\n{'='*50}\n")
    db_manager.print_table_data(table)





db_manager.close()