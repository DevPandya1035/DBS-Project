import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3
from database import DatabaseManager
from Admin_System import AdminLoginWindow
class AdminPortal:
    def __init__(self, root, admin_data, db_manager):
        """Initialize the Admin Portal with the admin's data and database connection."""
        self.root = root
        self.admin_data = admin_data
        self.db = db_manager
        
        # Configure the main window
        self.root.title(f"Admin Portal - {admin_data['username']}")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f5f5f5")
        
        # Create the main container frame
        self.main_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header()
        
        # Dashboard summary section
        self.create_dashboard()
        
        # Orders section
        self.create_orders_section()
        
        # Load initial data
        self.load_restaurant_data()
        self.load_orders()

    def create_header(self):
        """Create the header section with admin info and logout button."""
        header_frame = tk.Frame(self.main_frame, bg="#ffffff", pady=15, padx=20)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Admin welcome message
        welcome_label = tk.Label(
            header_frame, 
            text=f"Welcome, {self.admin_data['username']}", 
            font=("Arial", 18, "bold"), 
            bg="#ffffff"
        )
        welcome_label.pack(side="left")

        # Settings button
        settings_btn = tk.Button(
            header_frame, 
            text="Settings", 
            bg="#2196F3", 
            fg="white", 
            font=("Arial", 12),
            padx=15,
            command=self.show_settings
        )
        settings_btn.pack(side="right", padx=(10, 0))

        # Logout button
        logout_btn = tk.Button(
            header_frame, 
            text="Logout", 
            bg="#ff4d4d", 
            fg="white", 
            font=("Arial", 12),
            padx=15,
            command=self.logout
        )
        logout_btn.pack(side="right")
        
    def show_settings(self):
        """Show restaurant settings in a new window."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Restaurant Settings")
        settings_window.geometry("600x500")
        settings_window.configure(bg="#ffffff")
        
        # Load restaurant settings
        self.load_restaurant_settings(settings_window)
        
    def load_restaurant_settings(self, parent_window):
        """Load and display restaurant settings."""
        # Get restaurant data
        restaurant_id = self.current_restaurant['restaurant_id']
        
        try:
            self.cursor.execute("SELECT * FROM restaurants WHERE restaurant_id = ?", (restaurant_id,))
            restaurant_data = self.cursor.fetchone()
            
            if not restaurant_data:
                messagebox.showinfo("Info", "Restaurant data not found.")
                return
            
            # Create settings UI
            settings_frame = tk.LabelFrame(parent_window, text="Restaurant Settings", padx=20, pady=10, bg="#ffffff")
            settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Restaurant name
            tk.Label(settings_frame, text="Restaurant Name:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", pady=10)
            name_var = tk.StringVar(value=restaurant_data[1])
            name_entry = tk.Entry(settings_frame, textvariable=name_var, font=("Arial", 12), width=30)
            name_entry.grid(row=0, column=1, padx=10, pady=10)
            
            # Restaurant description
            tk.Label(settings_frame, text="Description:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=1, column=0, sticky="w", pady=10)
            desc_var = tk.StringVar(value=restaurant_data[2])
            desc_entry = tk.Entry(settings_frame, textvariable=desc_var, font=("Arial", 12), width=30)
            desc_entry.grid(row=1, column=1, padx=10, pady=10)
            
            # Update button
            update_btn = tk.Button(
                settings_frame, 
                text="Update Settings", 
                bg="#4CAF50", 
                fg="white",
                command=lambda: self.update_restaurant_settings(
                    restaurant_id, 
                    name_var.get(), 
                    desc_var.get(),
                    parent_window
                )
            )
            update_btn.grid(row=2, column=0, columnspan=2, pady=20)
            
            # Close button
            close_btn = tk.Button(
                settings_frame, 
                text="Close", 
                bg="#f44336", 
                fg="white",
                command=parent_window.destroy
            )
            close_btn.grid(row=3, column=0, columnspan=2, pady=10)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load restaurant settings: {e}")

    def update_restaurant_settings(self, restaurant_id, name, description, window):
        """Update restaurant settings in the database."""
        try:
            self.cursor.execute(
                "UPDATE restaurants SET name = ?, description = ? WHERE restaurant_id = ?",
                (name, description, restaurant_id)
            )
            self.db.conn.commit()
            
            messagebox.showinfo("Success", "Restaurant settings updated successfully!")
            
            # Refresh the admin portal title with the new restaurant name
            self.root.title(f"Admin Portal - {name}")
            
            # Close the settings window
            window.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to update restaurant settings: {e}")
            
    def show_settings(self):
        """Show restaurant settings, password reset, and theme toggle in a new window."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("600x650")
        settings_window.configure(bg="#ffffff")
        
        # Load restaurant settings
        self.load_restaurant_settings(settings_window)
        
        # Add password reset section
        self.create_password_reset_section(settings_window)
        
        # Add theme toggle
        self.create_theme_toggle_section(settings_window)

    def create_password_reset_section(self, parent_window):
        """Create the password reset section in settings."""
        password_frame = tk.LabelFrame(parent_window, text="Change Password", padx=20, pady=10, bg="#ffffff")
        password_frame.pack(fill="x", padx=20, pady=10)
        
        # Current password
        tk.Label(password_frame, text="Current Password:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", pady=10)
        self.current_pass_var = tk.StringVar()
        current_pass_entry = tk.Entry(password_frame, textvariable=self.current_pass_var, show="*", font=("Arial", 12), width=30)
        current_pass_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # New password
        tk.Label(password_frame, text="New Password:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=1, column=0, sticky="w", pady=10)
        self.new_pass_var = tk.StringVar()
        new_pass_entry = tk.Entry(password_frame, textvariable=self.new_pass_var, show="*", font=("Arial", 12), width=30)
        new_pass_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Confirm new password
        tk.Label(password_frame, text="Confirm New Password:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=2, column=0, sticky="w", pady=10)
        self.confirm_pass_var = tk.StringVar()
        confirm_pass_entry = tk.Entry(password_frame, textvariable=self.confirm_pass_var, show="*", font=("Arial", 12), width=30)
        confirm_pass_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Update password button
        update_pass_btn = tk.Button(
            password_frame, 
            text="Update Password", 
            bg="#4CAF50", 
            fg="white",
            command=self.reset_password
        )
        update_pass_btn.grid(row=3, column=0, columnspan=2, pady=20)

    def reset_password(self):
        """Reset the admin's password."""
        current_pass = self.current_pass_var.get()
        new_pass = self.new_pass_var.get()
        confirm_pass = self.confirm_pass_var.get()
        
        # Validate password fields
        if not current_pass or not new_pass or not confirm_pass:
            messagebox.showerror("Error", "All fields are required!")
            return
            
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "New password and confirm password do not match!")
            return
            
        # Validate password strength (example: minimum 8 characters)
        if len(new_pass) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long!")
            return
            
        try:
            # Verify current password (this is a simplified check)
            # In a real application, you would hash the password and compare with the stored hash
            admin_id = self.admin_data['admin_id']
            self.cursor.execute("SELECT password FROM admins WHERE admin_id = ?", (admin_id,))
            stored_password = self.cursor.fetchone()[0]
            
            if stored_password != current_pass:
                messagebox.showerror("Error", "Current password is incorrect!")
                return
                
            # Update password in database
            self.cursor.execute(
                "UPDATE admins SET password = ? WHERE admin_id = ?",
                (new_pass, admin_id)
            )
            self.db.conn.commit()
            
            messagebox.showinfo("Success", "Password updated successfully!")
            
            # Clear password fields
            self.current_pass_var.set("")
            self.new_pass_var.set("")
            self.confirm_pass_var.set("")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update password: {e}")

    def create_theme_toggle_section(self, parent_window):
        """Create the theme toggle section in settings."""
        theme_frame = tk.LabelFrame(parent_window, text="Appearance", padx=20, pady=10, bg="#ffffff")
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        # Theme toggle
        self.is_dark_mode = tk.BooleanVar(value=False)
        theme_toggle = tk.Checkbutton(
            theme_frame,
            text="Enable Dark Mode",
            variable=self.is_dark_mode,
            font=("Arial", 12),
            bg="#ffffff",
            command=self.toggle_dark_mode
        )
        theme_toggle.grid(row=0, column=0, sticky="w", pady=10)

    def toggle_dark_mode(self):
        """Toggle between light and dark modes."""
        if self.is_dark_mode.get():
            # Dark mode
            self.root.configure(bg="#333333")
            self.main_frame.configure(bg="#333333")
            self.dashboard_frame.configure(bg="#444444", fg="white")
            self.stats_frame.configure(bg="#444444")
            
            # Update all stat widgets
            for widget in self.stats_frame.winfo_children():
                widget.configure(bg="#555555")
                for child in widget.winfo_children():
                    child.configure(bg="#555555", fg="white")
            
            self.today_revenue_label.configure(fg="white")
            self.total_orders_label.configure(fg="white")
            self.pending_orders_label.configure(fg="white")
            self.completed_orders_label.configure(fg="white")
            
            # Update orders section
            self.orders_tree.configure(
                fieldbackground="#444444",
                background="#555555",
                foreground="white",
                headingbackground="#444444",
                headingforeground="white"
            )
            
            # Update scrollbar colors
            self.orders_tree.configure(selectbackground="#666666")
            
        else:
            # Light mode
            self.root.configure(bg="#f5f5f5")
            self.main_frame.configure(bg="#f5f5f5")
            self.dashboard_frame.configure(bg="#ffffff", fg="black")
            self.stats_frame.configure(bg="#ffffff")
            
            # Update all stat widgets
            for widget in self.stats_frame.winfo_children():
                widget.configure(bg="#ffffff")
                for child in widget.winfo_children():
                    child.configure(bg="#ffffff", fg="black")
            
            self.today_revenue_label.configure(fg="black")
            self.total_orders_label.configure(fg="black")
            self.pending_orders_label.configure(fg="black")
            self.completed_orders_label.configure(fg="black")
            
            # Update orders section
            self.orders_tree.configure(
                fieldbackground="white",
                background="white",
                foreground="black",
                headingbackground="#f5f5")

    def create_dashboard(self):
        """Create the dashboard with summary statistics."""
        self.dashboard_frame = tk.LabelFrame(
            self.main_frame, 
            text="Dashboard", 
            font=("Arial", 14, "bold"),
            bg="#ffffff", 
            padx=20, 
            pady=15
        )
        self.dashboard_frame.pack(fill="x", pady=(0, 20))
        
        # Create statistics widgets
        self.stats_frame = tk.Frame(self.dashboard_frame, bg="#ffffff")
        self.stats_frame.pack(fill="x")
        
        # These will be populated when restaurant data is loaded
        self.total_orders_label = self.create_stat_widget("Total Orders", "0")
        self.pending_orders_label = self.create_stat_widget("Pending Orders", "0")
        self.completed_orders_label = self.create_stat_widget("Completed Orders", "0")
        self.today_revenue_label = self.create_stat_widget("Today's Revenue", "₹0")

    def create_stat_widget(self, title, value):
        """Create a statistics widget for the dashboard."""
        frame = tk.Frame(self.stats_frame, bg="#ffffff", padx=15, pady=10)
        frame.pack(side="left", padx=10, fill="y")
        
        value_label = tk.Label(
            frame, 
            text=value, 
            font=("Arial", 24, "bold"), 
            bg="#ffffff"
        )
        value_label.pack()
        
        title_label = tk.Label(
            frame, 
            text=title, 
            font=("Arial", 12), 
            bg="#ffffff"
        )
        title_label.pack()
        
        return value_label

    def create_orders_section(self):
        """Create the orders section with filtering and table."""
        # Orders frame
        orders_frame = tk.LabelFrame(
            self.main_frame, 
            text="Orders", 
            font=("Arial", 14, "bold"),
            bg="#ffffff", 
            padx=20, 
            pady=15
        )
        orders_frame.pack(fill="both", expand=True)
        
        # Create filter controls
        filter_frame = tk.Frame(orders_frame, bg="#ffffff")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Status filter
        tk.Label(filter_frame, text="Filter by Status:", bg="#ffffff").pack(side="left", padx=(0, 10))
        self.status_var = tk.StringVar(value="All")
        status_options = ["All", "pending", "preparing", "ready", "delivered", "cancelled"]
        status_menu = tk.OptionMenu(filter_frame, self.status_var, *status_options, command=self.filter_orders)
        status_menu.pack(side="left", padx=(0, 20))
        
        # Date filter
        tk.Label(filter_frame, text="Filter by Date:", bg="#ffffff").pack(side="left", padx=(0, 10))
        self.date_var = tk.StringVar(value="All Time")
        date_options = ["All Time", "Today", "Yesterday", "This Week", "This Month"]
        date_menu = tk.OptionMenu(filter_frame, self.date_var, *date_options, command=self.filter_orders)
        date_menu.pack(side="left")
        
        # Refresh button
        refresh_btn = tk.Button(
            filter_frame, 
            text="Refresh", 
            bg="#4CAF50", 
            fg="white",
            command=self.load_orders
        )
        refresh_btn.pack(side="right")
        
        # Create orders table
        self.create_orders_table(orders_frame)

    def create_orders_table(self, parent_frame):
        """Create the orders table with scrollbars."""
        # Create a frame for the table with scrollbars
        table_frame = tk.Frame(parent_frame, bg="#ffffff")
        table_frame.pack(fill="both", expand=True)
        
        # Add scrollbar
        scrollbar_y = tk.Scrollbar(table_frame)
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = tk.Scrollbar(table_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Define columns
        columns = ("order_id", "customer", "items", "total_amount", "order_date", "status", "actions")
        column_widths = (80, 150, 300, 100, 150, 100, 150)
        
        # Create Treeview widget
        self.orders_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        # Configure scrollbars
        scrollbar_y.config(command=self.orders_tree.yview)
        scrollbar_x.config(command=self.orders_tree.xview)
        
        # Define column headings and widths
        for col, width in zip(columns, column_widths):
            self.orders_tree.heading(col, text=col.replace("_", " ").title())
            self.orders_tree.column(col, width=width, minwidth=width)
        
        self.orders_tree.pack(fill="both", expand=True)
        
        # Bind click event for order details
        self.orders_tree.bind("<Double-1>", self.show_order_details)

    def load_restaurant_data(self):
        """Load the admin's restaurant data."""
        # Get the admin's restaurant(s)
        admin_id = self.admin_data['admin_id']
        self.cursor = self.db.conn.cursor()
        self.cursor.execute("SELECT * FROM restaurants WHERE admin_id = ?", (admin_id,))
        self.restaurants = []
        
        for row in self.cursor.fetchall():
            restaurant_dict = {}
            for idx, col in enumerate(self.cursor.description):
                restaurant_dict[col[0]] = row[idx]
            self.restaurants.append(restaurant_dict)
        
        if not self.restaurants:
            messagebox.showinfo("Info", "No restaurants found for this admin account.")
            return
        
        # If admin has multiple restaurants, we could add a selector
        # For now, we'll use the first restaurant
        self.current_restaurant = self.restaurants[0]
        
        # Update window title with restaurant name
        self.root.title(f"Admin Portal - {self.current_restaurant['name']}")

    def load_orders(self):
        """Load and display orders for the admin's restaurant."""
        # Clear existing orders
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        restaurant_id = self.current_restaurant['restaurant_id']
        
        # Get orders for this restaurant
        try:
            self.cursor.execute("""
                SELECT o.*, u.username as customer_name, u.email as customer_email, u.phone_number
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                WHERE o.restaurant_id = ?
                ORDER BY o.order_date DESC
            """, (restaurant_id,))
            
            orders = []
            for row in self.cursor.fetchall():
                order_dict = {}
                for idx, col in enumerate(self.cursor.description):
                    order_dict[col[0]] = row[idx]
                orders.append(order_dict)
            
            # Update dashboard statistics
            total_orders = len(orders)
            pending_orders = sum(1 for order in orders if order['status'] == 'pending')
            completed_orders = sum(1 for order in orders if order['status'] == 'delivered')
            
            # Calculate today's revenue
            today = datetime.now().strftime('%Y-%m-%d')
            today_revenue = sum(order['total_amount'] for order in orders 
                                if str(order['order_date']).startswith(today))
            
            # Update dashboard labels
            self.total_orders_label.config(text=str(total_orders))
            self.pending_orders_label.config(text=str(pending_orders))
            self.completed_orders_label.config(text=str(completed_orders))
            self.today_revenue_label.config(text=f"₹{today_revenue:.2f}")
            
            # Populate the orders table
            for order in orders:
                # Get order items
                self.cursor.execute("""
                    SELECT oi.*, mi.name as item_name
                    FROM order_items oi
                    JOIN menu_items mi ON oi.item_id = mi.item_id
                    WHERE oi.order_id = ?
                """, (order['order_id'],))
                
                order_items = []
                for row in self.cursor.fetchall():
                    item_dict = {}
                    for idx, col in enumerate(self.cursor.description):
                        item_dict[col[0]] = row[idx]
                    order_items.append(item_dict)
                
                # Create a summary of items
                items_summary = ", ".join([f"{item['item_name']} (x{item['quantity']})" 
                                         for item in order_items[:2]])
                
                if len(order_items) > 2:
                    items_summary += f" and {len(order_items) - 2} more"
                
                # Create a button for actions
                actions_text = "Update Status"
                
                # Insert into treeview
                self.orders_tree.insert(
                    "", "end",
                    values=(
                        order['order_id'],
                        f"{order['customer_name']}\n{order['customer_email']}",
                        items_summary,
                        f"₹{order['total_amount']:.2f}",
                        order['order_date'],
                        order['status'],
                        actions_text
                    ),
                    tags=(str(order['order_id']),)
                )
            
            # Configure row tags for status colors
            for order in orders:
                status = order['status']
                order_id = str(order['order_id'])
                
                if status == 'pending':
                    self.orders_tree.tag_configure(order_id, background="#fff9c4")
                elif status == 'preparing':
                    self.orders_tree.tag_configure(order_id, background="#e3f2fd")
                elif status == 'ready':
                    self.orders_tree.tag_configure(order_id, background="#e8f5e9")
                elif status == 'delivered':
                    self.orders_tree.tag_configure(order_id, background="#f1f8e9")
                elif status == 'cancelled':
                    self.orders_tree.tag_configure(order_id, background="#ffebee")
                    
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load orders: {e}")

    def show_order_details(self, event):
        """Show detailed information about a selected order."""
        # Get selected item
        selected_items = self.orders_tree.selection()
        if not selected_items:
            return
            
        selected_item = selected_items[0]
        order_id = self.orders_tree.item(selected_item)['values'][0]
        
        # Create a new window for order details
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Order #{order_id} Details")
        details_window.geometry("800x600")
        details_window.configure(bg="#ffffff")
        
        # Get order details
        self.cursor.execute("""
            SELECT o.*, u.username, u.email, u.phone_number
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.order_id = ?
        """, (order_id,))
        
        order_row = self.cursor.fetchone()
        if not order_row:
            messagebox.showerror("Error", "Order not found")
            details_window.destroy()
            return
            
        order = {}
        for idx, col in enumerate(self.cursor.description):
            order[col[0]] = order_row[idx]
        
        # Get order items
        self.cursor.execute("""
            SELECT oi.*, mi.name as item_name, mi.description
            FROM order_items oi
            JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        order_items = []
        for row in self.cursor.fetchall():
            item_dict = {}
            for idx, col in enumerate(self.cursor.description):
                item_dict[col[0]] = row[idx]
            order_items.append(item_dict)
        
        # Create details UI
        # Order info section
        info_frame = tk.LabelFrame(details_window, text="Order Information", padx=15, pady=10, bg="#ffffff")
        info_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Order ID and Date
        tk.Label(info_frame, text=f"Order #: {order['order_id']}", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(info_frame, text=f"Date: {order['order_date']}", font=("Arial", 12), bg="#ffffff").grid(row=0, column=1, sticky="w", pady=5)
        
        # Customer info
        tk.Label(info_frame, text="Customer:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=1, column=0, sticky="w", pady=5)
        tk.Label(info_frame, text=f"{order['username']}", font=("Arial", 12), bg="#ffffff").grid(row=1, column=1, sticky="w", pady=5)
        
        tk.Label(info_frame, text="Contact:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=2, column=0, sticky="w", pady=5)
        tk.Label(info_frame, text=f"{order['email']} | {order['phone_number'] or 'No phone'}", font=("Arial", 12), bg="#ffffff").grid(row=2, column=1, sticky="w", pady=5)
        
        # Order status section
        status_frame = tk.LabelFrame(details_window, text="Order Status", padx=15, pady=10, bg="#ffffff")
        status_frame.pack(fill="x", padx=20, pady=10)
        
        # Current status
        tk.Label(status_frame, text="Current Status:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=0, column=0, sticky="w", pady=5)
        
        # Status dropdown for updating
        status_options = ["pending", "preparing", "ready", "delivered", "cancelled"]
        status_var = tk.StringVar(value=order['status'])
        status_dropdown = tk.OptionMenu(status_frame, status_var, *status_options)
        status_dropdown.grid(row=0, column=1, sticky="w", pady=5)
        
        # Update button
        update_btn = tk.Button(
            status_frame, 
            text="Update Status", 
            bg="#4CAF50", 
            fg="white",
            command=lambda: self.update_order_status(order_id, status_var.get(), details_window)
        )
        update_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Order items section
        items_frame = tk.LabelFrame(details_window, text="Order Items", padx=15, pady=10, bg="#ffffff")
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create headers
        headers = ["Item", "Description", "Price", "Quantity", "Subtotal"]
        for i, header in enumerate(headers):
            tk.Label(items_frame, text=header, font=("Arial", 12, "bold"), bg="#ffffff").grid(row=0, column=i, sticky="w", padx=5, pady=5)
        
        # Add items
        for i, item in enumerate(order_items, start=1):
            subtotal = item['price'] * item['quantity']
            
            description = item['description']
            if description and len(description) > 30:
                description = description[:30] + "..."
            
            tk.Label(items_frame, text=item['item_name'], bg="#ffffff").grid(row=i, column=0, sticky="w", padx=5, pady=3)
            tk.Label(items_frame, text=description or "", bg="#ffffff").grid(row=i, column=1, sticky="w", padx=5, pady=3)
            tk.Label(items_frame, text=f"₹{item['price']:.2f}", bg="#ffffff").grid(row=i, column=2, sticky="w", padx=5, pady=3)
            tk.Label(items_frame, text=f"{item['quantity']}", bg="#ffffff").grid(row=i, column=3, sticky="w", padx=5, pady=3)
            tk.Label(items_frame, text=f"₹{subtotal:.2f}", bg="#ffffff").grid(row=i, column=4, sticky="w", padx=5, pady=3)
        
        # Total row
        total_row = len(order_items) + 1
        tk.Label(items_frame, text="", bg="#ffffff").grid(row=total_row, column=0, pady=10)
        tk.Label(items_frame, text="", bg="#ffffff").grid(row=total_row, column=1, pady=10)
        tk.Label(items_frame, text="", bg="#ffffff").grid(row=total_row, column=2, pady=10)
        tk.Label(items_frame, text="Total:", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=total_row, column=3, sticky="e", padx=5, pady=10)
        tk.Label(items_frame, text=f"₹{order['total_amount']:.2f}", font=("Arial", 12, "bold"), bg="#ffffff").grid(row=total_row, column=4, sticky="w", padx=5, pady=10)
        
        # Close button
        close_btn = tk.Button(
            details_window, 
            text="Close", 
            bg="#f44336", 
            fg="white",
            command=details_window.destroy
        )
        close_btn.pack(pady=20)

    def update_order_status(self, order_id, new_status, details_window=None):
        """Update the status of an order."""
        # Update order status in database
        try:
            self.cursor.execute(
                "UPDATE orders SET status = ? WHERE order_id = ?",
                (new_status, order_id)
            )
            self.db.conn.commit()
            
            messagebox.showinfo("Success", f"Order #{order_id} status updated to {new_status}")
            
            # Refresh orders list
            self.load_orders()
            
            # Close details window if it exists
            if details_window:
                details_window.destroy()
                
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to update order status: {e}")

    def filter_orders(self, event=None):
        """Filter orders based on status and date."""
        # Implementation of filter functionality
        status_filter = self.status_var.get()
        date_filter = self.date_var.get()
        
        # Clear existing orders
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        restaurant_id = self.current_restaurant['restaurant_id']
        
        # Build query based on filters
        query = """
            SELECT o.*, u.username as customer_name, u.email as customer_email, u.phone_number
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.restaurant_id = ?
        """
        params = [restaurant_id]
        
        # Add status filter
        if status_filter != "All":
            query += " AND o.status = ?"
            params.append(status_filter)
        
        # Add date filter
        if date_filter != "All Time":
            today = datetime.now().strftime('%Y-%m-%d')
            
            if date_filter == "Today":
                query += " AND date(o.order_date) = ?"
                params.append(today)
            elif date_filter == "Yesterday":
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                query += " AND date(o.order_date) = ?"
                params.append(yesterday)
            elif date_filter == "This Week":
                # Get the start of the week (Monday)
                today_date = datetime.now()
                start_of_week = (today_date - timedelta(days=today_date.weekday())).strftime('%Y-%m-%d')
                query += " AND date(o.order_date) >= ?"
                params.append(start_of_week)
            elif date_filter == "This Month":
                start_of_month = datetime.now().strftime('%Y-%m-01')
                query += " AND date(o.order_date) >= ?"
                params.append(start_of_month)
        
        query += " ORDER BY o.order_date DESC"
        
        try:
            # Execute query
            self.cursor.execute(query, params)
            
            orders = []
            for row in self.cursor.fetchall():
                order_dict = {}
                for idx, col in enumerate(self.cursor.description):
                    order_dict[col[0]] = row[idx]
                orders.append(order_dict)
            
            # Populate the orders table (similar to load_orders method)
            for order in orders:
                # Get order items
                self.cursor.execute("""
                    SELECT oi.*, mi.name as item_name
                    FROM order_items oi
                    JOIN menu_items mi ON oi.item_id = mi.item_id
                    WHERE oi.order_id = ?
                """, (order['order_id'],))
                
                order_items = []
                for row in self.cursor.fetchall():
                    item_dict = {}
                    for idx, col in enumerate(self.cursor.description):
                        item_dict[col[0]] = row[idx]
                    order_items.append(item_dict)
                
                # Create a summary of items
                items_summary = ", ".join([f"{item['item_name']} (x{item['quantity']})" 
                                         for item in order_items[:2]])
                
                if len(order_items) > 2:
                    items_summary += f" and {len(order_items) - 2} more"
                
                # Insert into treeview
                self.orders_tree.insert(
                    "", "end",
                    values=(
                        order['order_id'],
                        f"{order['customer_name']}\n{order['customer_email']}",
                        items_summary,
                        f"₹{order['total_amount']:.2f}",
                        order['order_date'],
                        order['status'],
                        "Update Status"
                    ),
                    tags=(str(order['order_id']),)
                )
            
            # Configure row tags for status colors
            for order in orders:
                status = order['status']
                order_id = str(order['order_id'])
                
                if status == 'pending':
                    self.orders_tree.tag_configure(order_id, background="#fff9c4")
                elif status == 'preparing':
                    self.orders_tree.tag_configure(order_id, background="#e3f2fd")
                elif status == 'ready':
                    self.orders_tree.tag_configure(order_id, background="#e8f5e9")
                elif status == 'delivered':
                    self.orders_tree.tag_configure(order_id, background="#f1f8e9")
                elif status == 'cancelled':
                    self.orders_tree.tag_configure(order_id, background="#ffebee")
                    
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to filter orders: {e}")

    def logout(self):
        """Log out of the admin portal."""
        self.root.destroy()





# For standalone testing
if __name__ == "__main__":
    # Create a root window
    root = tk.Tk()
    
    # Initialize a dummy database manager (replace with actual implementation)
    db_manager = DatabaseManager()  # Ensure this is properly implemented
    
    # Simulate the login process
    login_window = AdminLoginWindow(root, db_manager)
    
    # Function to open admin portal after login
    def on_login_success():
        # Get admin data from the login window
        admin_data = login_window.admin_data
        
        if admin_data:
            # Destroy the login window
            login_window.destroy()
            
            # Create a new window for the admin portal
            portal_root = tk.Tk()
            app = AdminPortal(portal_root, admin_data, db_manager)
            portal_root.mainloop()
    
    # Connect the login success event
    login_window.on_login_success = on_login_success
    
    root.mainloop()
