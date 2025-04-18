import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import random
import sqlite3
from database import DatabaseManager

class FoodOrderingSystem:
    def __init__(self, root, user_email=None):
        self.root = root
        self.user_email = user_email
        print(f"Initializing with user email: {user_email}")  # Debug print
        self.db = DatabaseManager()
        self.cart_items = []
        # Store the user email for cart operations
        self.current_user_email = user_email
        # Variable to track dark mode state
        self.dark_mode = False

        # Main window setup
        self.root.title("Food Ordering System - Home")
        self.root.geometry("1000x650")
        self.root.config(bg="white")

        # Create UI components
        self.create_top_bar()
        self.create_weekend_deals()
        self.create_sidebar()
        self.create_main_content()

        # Display restaurants when app starts
        self.display_restaurants_in_main_window()

    def create_top_bar(self):
        # Top bar frame
        top_frame = tk.Frame(self.root, bg="white", height=80)
        top_frame.pack(fill="x")

        # Personalized greeting
        current_hour = datetime.datetime.now().hour
        greeting = "Good Morning" if 5 <= current_hour < 12 else "Good Afternoon" if 12 <= current_hour < 17 else "Good Evening"

        # App title
        title = tk.Label(top_frame, text="FoodExpress", font=("Arial", 24, "bold"), fg="#FF6347", bg="white")
        title.pack(side="left", padx=10, pady=20)

        # User greeting
        user_name = "User"
        if self.user_email:
            success, user_data = self.db.verify_user_login(self.user_email, "")
            if success and user_data:
                user_name = user_data.get('username', "User")
        username = tk.Label(top_frame, text=f"{greeting}, {user_name}", font=("Arial", 14), bg="white")
        username.pack(side="left", padx=20, pady=20)

        # Search bar
        search_var = tk.StringVar()
        search_frame = tk.Frame(top_frame, bg="#f0f0f0", height=30, width=300)
        search_frame.pack(side="left", padx=10, pady=20)
        search_frame.pack_propagate(False)
        search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Arial", 14), width=30)
        search_entry.pack(fill="both", expand=True)
        search_entry.insert(0, "Search for food or restaurants...")

        # Cart button
        self.cart_btn = tk.Button(top_frame, text="🛒 Cart", bg="#FF6347", fg="white",
                                 font=("Arial", 12), relief="flat", padx=10, pady=5,
                                 command=self.display_cart)
        self.cart_btn.pack(side="right", padx=20)

        # Profile button
        profile_btn = tk.Button(top_frame, text="👤 Profile", bg="white", fg="black",
                               font=("Arial", 12), relief="groove")
        profile_btn.pack(side="right", padx=10)

        ttk.Separator(self.root, orient='horizontal').pack(fill='x')

    def create_weekend_deals(self):
        # Weekend deals banner
        weekend_deals_frame = tk.Frame(self.root, bg="#FF6347", height=150)
        weekend_deals_frame.pack(fill="x", pady=10)
        weekend_deals_label = tk.Label(weekend_deals_frame, text="Weekend Deals",
                                      font=("Arial", 18, "bold"), fg="white", bg="#FF6347")
        weekend_deals_label.pack(pady=5)

        # Random deals data
        deals = [
            {"name": "Italian Cuisine Special", "description": "Get 20% off on all Italian dishes this weekend!"},
            {"name": "Weekend Special Combo", "description": "Buy any main course and get a drink for free!"},
            {"name": "New Restaurants", "description": "First order discount of 15% at new restaurants!"}
        ]

        # Randomly select 2 deals to display
        random_deals = random.sample(deals, 2)
        for deal in random_deals:
            self.create_deal_card(weekend_deals_frame, deal["name"], deal["description"])

    def create_deal_card(self, parent, deal_name, description):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=10, pady=10)
        card.pack(pady=5, fill="x", padx=20)
        name_label = tk.Label(card, text=deal_name, font=("Arial", 14, "bold"), bg="white")
        name_label.pack(anchor="w")
        desc_label = tk.Label(card, text=description, font=("Arial", 12), bg="white", fg="#555")
        desc_label.pack(anchor="w")

    def create_sidebar(self):
        # Sidebar navigation
        sidebar = tk.Frame(self.root, bg="#f0f0f0", width=150)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        # Home button
        home_btn = tk.Button(sidebar, text="🏠 Home", bg="#f0f0f0", fg="black",
                            font=("Arial", 12), relief="flat", anchor="w", padx=15, pady=8,
                            command=self.display_restaurants_in_main_window)
        home_btn.pack(fill="x", pady=5)
        
        # My Orders button
        orders_btn = tk.Button(sidebar, text="📋 My Orders", bg="#f0f0f0", fg="black",
                              font=("Arial", 12), relief="flat", anchor="w", padx=15, pady=8,
                              command=self.display_user_orders)
        orders_btn.pack(fill="x", pady=5)
        
        # Settings button
        settings_btn = tk.Button(sidebar, text="⚙️ Settings", bg="#f0f0f0", fg="black",
                                font=("Arial", 12), relief="flat", anchor="w", padx=15, pady=8,
                                command=self.show_settings)
        settings_btn.pack(fill="x", pady=5)
        
        # Quick actions section
        quick_actions_label = tk.Label(sidebar, text="Quick Actions", bg="#f0f0f0", fg="#555",
                                      font=("Arial", 10, "bold"), anchor="w", padx=15)
        quick_actions_label.pack(fill="x", pady=(20, 5))
        
        # Order Now button
        order_now_btn = tk.Button(sidebar, text="Order Now", bg="#e0e0e0", fg="black",
                                 font=("Arial", 10), relief="flat", anchor="w", padx=15, pady=5,
                                 command=self.display_restaurants_in_main_window)
        order_now_btn.pack(fill="x", pady=2)
        
        # Track Order button
        track_order_btn = tk.Button(sidebar, text="Track Order", bg="#e0e0e0", fg="black",
                                   font=("Arial", 10), relief="flat", anchor="w", padx=15, pady=5,
                                   command=self.show_order_tracker)
        track_order_btn.pack(fill="x", pady=2)

    def create_main_content(self):
        # Main content area with scrollbar
        self.main_content = tk.Frame(self.root, bg="white")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Search filters
        filter_frame = tk.Frame(self.main_content, bg="white")
        filter_frame.pack(fill="x", pady=10)
        tk.Label(filter_frame, text="Filters:", font=("Arial", 12), bg="white").pack(side="left", padx=5)

        price_var = tk.StringVar()
        price_dropdown = ttk.Combobox(filter_frame, textvariable=price_var,
                                     values=["All", "Under $10", "$10-$20", "Over $20"],
                                     width=15, state="readonly")
        price_dropdown.current(0)
        price_dropdown.pack(side="left", padx=5)

        rating_var = tk.StringVar()
        rating_dropdown = ttk.Combobox(filter_frame, textvariable=rating_var,
                                      values=["All", "4 Stars+", "3 Stars+", "2 Stars+"],
                                      width=15, state="readonly")
        rating_dropdown.current(0)
        rating_dropdown.pack(side="left", padx=5)

        # Recommended restaurants label
        self.resto_label = tk.Label(self.main_content, text="Recommended Restaurants",
                                   font=("Arial", 18, "bold"), bg="white", fg="#333")
        self.resto_label.pack(anchor="w", pady=10)

        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.main_content, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a scrollbar linked to the canvas
        scrollbar = ttk.Scrollbar(self.main_content, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create another frame inside the canvas for the restaurant cards
        self.restaurants_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.restaurants_frame, anchor="nw")

    def create_restaurant_card(self, parent, restaurant_id, name, rating):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=10, pady=10)
        card.pack(pady=8, fill="x")
        name_label = tk.Label(card, text=name, font=("Arial", 16, "bold"), bg="white")
        name_label.pack(anchor="w")
        info = f"⭐ {rating}"
        info_label = tk.Label(card, text=info, font=("Arial", 12), bg="white", fg="#555")
        info_label.pack(anchor="w")

        # Add a view menu button
        view_menu_btn = tk.Button(card, text="View Menu", bg="#FF6347", fg="white",
                                 font=("Arial", 10), relief="flat", padx=5, pady=2,
                                 command=lambda r_id=restaurant_id, r_name=name:
                                 self.display_restaurant_menu(r_id, r_name))
        view_menu_btn.pack(anchor="e", pady=5)

        # Add a rate restaurant button
        rate_btn = tk.Button(card, text="Rate Restaurant", bg="#4CAF50", fg="white",
                            font=("Arial", 10), relief="flat", padx=5, pady=2,
                            command=lambda r_id=restaurant_id, r_name=name:
                            self.show_rating_dialog(r_id, r_name))
        rate_btn.pack(anchor="e", pady=5)

        # Make the entire card clickable
        card.bind("<Button-1>", lambda event, r_id=restaurant_id, r_name=name:
                 self.display_restaurant_menu(r_id, r_name))
        name_label.bind("<Button-1>", lambda event, r_id=restaurant_id, r_name=name:
                       self.display_restaurant_menu(r_id, r_name))
        info_label.bind("<Button-1>", lambda event, r_id=restaurant_id, r_name=name:
                       self.display_restaurant_menu(r_id, r_name))

    def display_restaurants_in_main_window(self):
        # Clear existing content
        for widget in self.restaurants_frame.winfo_children():
            widget.destroy()

        # Fetch restaurant data from the database
        restaurants = self.db.get_all_restaurants()

        # Display each restaurant in a card
        for restaurant in restaurants:
            self.create_restaurant_card(
                self.restaurants_frame,
                restaurant['restaurant_id'],
                restaurant['name'],
                restaurant['rating']
            )

        # Update the scroll region
        self.restaurants_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def debug_database_content(self, restaurant_id):
        """Print all categories and menu items for a restaurant"""
        try:
            print(f"\n=== Database Debug for Restaurant ID: {restaurant_id} ===")
            
            # Print all categories for this restaurant
            self.db.cursor.execute("""
                SELECT * FROM menu_categories 
                WHERE restaurant_id = ?
            """, (restaurant_id,))
            categories = self.db.cursor.fetchall()
            print(f"Categories for restaurant {restaurant_id}:")
            for cat in categories:
                print(f"  ID: {cat['category_id']}, Name: {cat['name']}")
            
            # Print all menu items for this restaurant
            self.db.cursor.execute("""
                SELECT * FROM menu_items 
                WHERE restaurant_id = ?
            """, (restaurant_id,))
            items = self.db.cursor.fetchall()
            print(f"Menu items for restaurant {restaurant_id}:")
            for item in items:
                print(f"  ID: {item['item_id']}, Name: {item['name']}, Category ID: {item['category_id']}")
            
            # Check specific categories
            for cat in categories:
                cat_id = cat['category_id']
                self.db.cursor.execute("""
                    SELECT COUNT(*) as count FROM menu_items 
                    WHERE restaurant_id = ? AND category_id = ?
                """, (restaurant_id, cat_id))
                count_result = self.db.cursor.fetchone()
                count = count_result['count'] if count_result else 0
                print(f"  Category {cat['name']} (ID: {cat_id}) has {count} items")
            
            print("=== End Database Debug ===\n")
        except Exception as e:
            print(f"Error in debug_database_content: {e}")

    def display_restaurant_menu(self, restaurant_id, restaurant_name):
        # Debug database content first
        self.debug_database_content(restaurant_id)
        
        # Create a new window for the restaurant menu
        menu_window = tk.Toplevel(self.root)
        menu_window.title(f"{restaurant_name} - Menu")
        menu_window.geometry("800x600")
        menu_window.config(bg="white")

        # Restaurant name header
        header_frame = tk.Frame(menu_window, bg="#FF6347", height=60)
        header_frame.pack(fill="x")
        restaurant_label = tk.Label(header_frame, text=restaurant_name, font=("Arial", 18, "bold"),
                                   fg="white", bg="#FF6347")
        restaurant_label.pack(pady=10)

        # Create a frame for the category dropdown and menu items
        main_frame = tk.Frame(menu_window, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Category selection dropdown
        category_frame = tk.Frame(main_frame, bg="white")
        category_frame.pack(fill="x", pady=10)
        tk.Label(category_frame, text="Select Category:",
                font=("Arial", 14, "bold"), bg="white").pack(side="left", padx=5)

        # Fetch unique categories for this restaurant
        self.db.cursor.execute("""
            SELECT category_id, name
            FROM menu_categories
            WHERE restaurant_id = ?
            GROUP BY name  -- This ensures we get unique category names
            ORDER BY category_id
        """, (restaurant_id,))
        categories = self.db.cursor.fetchall()

        # Create a StringVar for the selected category
        category_var = tk.StringVar()

        # Create the dropdown with category names
        category_names = [category['name'] for category in categories]
        
        # Create a dictionary to map category names to IDs - FIX: Use the actual category_id from database
        self.category_map = {}
        for category in categories:
            self.category_map[category['name']] = category['category_id']
            print(f"Adding to category map: {category['name']} -> {category['category_id']}")

        # Create the combobox
        category_dropdown = ttk.Combobox(category_frame, textvariable=category_var,
                                        values=category_names, width=30, state="readonly")
        category_dropdown.pack(side="left", padx=10)

        # Set the default value to the first category if available
        if category_names:
            category_dropdown.current(0)

        # Create a frame for menu items with scrollbar
        items_frame_container = tk.Frame(main_frame, bg="white")
        items_frame_container.pack(fill="both", expand=True, pady=10)

        # Create a canvas for scrolling
        canvas = tk.Canvas(items_frame_container, bg="white")
        canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(items_frame_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas for the menu items
        self.menu_items_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=self.menu_items_frame, anchor="nw")

        # Function to display menu items for the selected category
        def show_category_items(*args):
            # Clear existing menu items
            for widget in self.menu_items_frame.winfo_children():
                widget.destroy()
            
            selected_category = category_var.get()
            if selected_category:
                category_id = self.category_map[selected_category]
                
                # Debug print to verify the category_id
                print(f"Selected category: {selected_category}, ID: {category_id}")
                print(f"Restaurant ID: {restaurant_id}")
                
                # Fetch menu items for this category with explicit column names
                try:
                    self.db.cursor.execute("""
                        SELECT DISTINCT item_id, restaurant_id, category_id, name, description, price 
                        FROM menu_items
                        WHERE restaurant_id = ? AND category_id = ?
                    """, (restaurant_id, category_id))
                    
                    menu_items = self.db.cursor.fetchall()
                    
                    # Debug output - check what we're getting from the database
                    print(f"Query executed: SELECT * FROM menu_items WHERE restaurant_id = {restaurant_id} AND category_id = {category_id}")
                    print(f"Found {len(menu_items)} items for category {selected_category}")
                    if menu_items:
                        for item in menu_items:
                            print(f"  Item: {item['name']}, Category ID: {item['category_id']}")
                    
                    # Display each menu item
                    if menu_items:
                        for item in menu_items:
                            self.create_menu_item_card(self.menu_items_frame, item, restaurant_id)
                    else:
                        # Display a message if no items in this category
                        no_items_label = tk.Label(self.menu_items_frame, text="No items in this category",
                                                 font=("Arial", 12), bg="white", fg="#555")
                        no_items_label.pack(pady=20)
                        
                        # Add a button to add items to this category (for testing)
                        add_test_item_btn = tk.Button(self.menu_items_frame, text="Add Test Item", 
                                                     bg="#FF6347", fg="white",
                                                     command=lambda: self.add_test_item(restaurant_id, category_id, selected_category))
                        add_test_item_btn.pack(pady=10)
                except Exception as e:
                    print(f"Error fetching menu items: {e}")
                    error_label = tk.Label(self.menu_items_frame, text=f"Error loading menu items: {str(e)}",
                                          font=("Arial", 12), bg="white", fg="red")
                    error_label.pack(pady=20)
            
            # Update the scroll region
            self.menu_items_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        # Bind the combobox selection to the show_category_items function
        category_dropdown.bind("<<ComboboxSelected>>", show_category_items)
        
        # Also show items for the first category by default
        if category_names:
            # Set a small delay to ensure the UI is fully loaded
            menu_window.after(100, show_category_items)

    def add_test_item(self, restaurant_id, category_id, category_name):
        try:
            # Add a sample menu item for testing
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.db.cursor.execute("""
                INSERT INTO menu_items (restaurant_id, category_id, name, description, price, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (restaurant_id, category_id, f"Test {category_name}", f"Test description for {category_name}", 99.00, current_time))
            
            self.db.conn.commit()
            messagebox.showinfo("Success", "Test item added successfully")
            
            # Refresh the menu items display - modified to work without direct reference
            for widget in self.menu_items_frame.winfo_children():
                widget.destroy()
                
            # Re-fetch items for the current category
            self.db.cursor.execute("""
                SELECT * FROM menu_items
                WHERE restaurant_id = ? AND category_id = ?
            """, (restaurant_id, category_id))
            
            menu_items = self.db.cursor.fetchall()
            
            if menu_items:
                for item in menu_items:
                    self.create_menu_item_card(self.menu_items_frame, item, restaurant_id)
            else:
                no_items_label = tk.Label(self.menu_items_frame, text="No items in this category",
                                        font=("Arial", 12), bg="white", fg="#555")
                no_items_label.pack(pady=20)
                
                # Add the button again
                add_test_item_btn = tk.Button(self.menu_items_frame, text="Add Test Item", 
                                            bg="#FF6347", fg="white",
                                            command=lambda: self.add_test_item(restaurant_id, category_id, category_name))
                add_test_item_btn.pack(pady=10)
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to add test item: {e}")

    def create_menu_item_card(self, parent, item, restaurant_id):
        item_frame = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=15, pady=10)
        item_frame.pack(fill="x", pady=5, padx=10)

        # Item details
        name_label = tk.Label(item_frame, text=item['name'], font=("Arial", 14, "bold"), bg="white")
        name_label.grid(row=0, column=0, sticky="w")

        price_label = tk.Label(item_frame, text=f"₹{item['price']:.2f}", font=("Arial", 14), bg="white", fg="#FF6347")
        price_label.grid(row=0, column=1, sticky="e", padx=(150, 0))

        desc_label = tk.Label(item_frame, text=item['description'], font=("Arial", 12), bg="white", fg="#555",
                             wraplength=400, justify="left")
        desc_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        # Quantity selector and add to cart button
        quantity_frame = tk.Frame(item_frame, bg="white")
        quantity_frame.grid(row=2, column=0, columnspan=2, sticky="e", pady=5)

        # Decrease quantity button
        decrease_btn = tk.Button(quantity_frame, text="-", font=("Arial", 12, "bold"), bg="#f0f0f0",
                                command=lambda: self.update_quantity(quantity_var, -1))
        decrease_btn.grid(row=0, column=0, padx=2)

        # Quantity display
        quantity_var = tk.StringVar(value="1")
        quantity_label = tk.Label(quantity_frame, textvariable=quantity_var, font=("Arial", 12),
                                 width=2, bg="white")
        quantity_label.grid(row=0, column=1, padx=5)

        # Increase quantity button
        increase_btn = tk.Button(quantity_frame, text="+", font=("Arial", 12, "bold"), bg="#f0f0f0",
                                command=lambda: self.update_quantity(quantity_var, 1))
        increase_btn.grid(row=0, column=2, padx=2)

        # Add to cart button
        add_to_cart_btn = tk.Button(quantity_frame, text="Add to Cart", bg="#FF6347", fg="white",
                                   font=("Arial", 10), relief="flat", padx=10, pady=2,
                                   command=lambda: self.add_item_to_cart(item, restaurant_id, int(quantity_var.get())))
        add_to_cart_btn.grid(row=0, column=3, padx=10)

    def update_quantity(self, quantity_var, change):
        current = int(quantity_var.get())
        new_value = current + change
        if new_value >= 1:  # Ensure quantity doesn't go below 1
            quantity_var.set(str(new_value))

    def add_item_to_cart(self, item, restaurant_id, quantity):
        # Get the current user's ID (assuming we have user_email from login)
        user_email = self.current_user_email
        # Debug print to check what's happening
        print(f"Current user email: {user_email}")
        if not user_email:
            messagebox.showinfo("Login Required", "Please login to add items to cart")
            return

        # Get user_id from email
        self.db.cursor.execute("SELECT user_id FROM users WHERE email = ?", (user_email,))
        user_data = self.db.cursor.fetchone()
        if not user_data:
            messagebox.showinfo("Error", "User not found")
            return

        user_id = user_data['user_id']
        item_id = item['item_id']

        # Check if item already exists in cart
        self.db.cursor.execute("""
            SELECT * FROM cart_items
            WHERE user_id = ? AND item_id = ? AND restaurant_id = ?
        """, (user_id, item_id, restaurant_id))
        existing_cart_item = self.db.cursor.fetchone()

        try:
            if existing_cart_item:
                # Update quantity if item already in cart
                new_quantity = existing_cart_item['quantity'] + quantity
                self.db.cursor.execute("""
                    UPDATE cart_items
                    SET quantity = ?
                    WHERE cart_item_id = ?
                """, (new_quantity, existing_cart_item['cart_item_id']))
            else:
                # Add new item to cart
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.db.cursor.execute("""
                    INSERT INTO cart_items
                    (user_id, item_id, restaurant_id, quantity, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, item_id, restaurant_id, quantity, current_time))

            self.db.conn.commit()
            messagebox.showinfo("Success", f"{quantity} x {item['name']} added to cart")
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to add item to cart: {e}")

    def display_cart(self):
        # Create a new window for the cart
        cart_window = tk.Toplevel(self.root)
        cart_window.title("Your Cart")
        cart_window.geometry("700x500")
        cart_window.config(bg="white")

        # Cart header
        header_frame = tk.Frame(cart_window, bg="#FF6347", height=60)
        header_frame.pack(fill="x")
        cart_label = tk.Label(header_frame, text="Your Cart", font=("Arial", 18, "bold"),
                             fg="white", bg="#FF6347")
        cart_label.pack(pady=10)

        # Create a frame for cart items with scrollbar
        main_frame = tk.Frame(cart_window, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create a canvas for scrolling
        canvas = tk.Canvas(main_frame, bg="white")
        canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas for the cart content
        cart_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=cart_frame, anchor="nw")

        # Get the current user's ID
        user_email = self.current_user_email
        if not user_email:
            empty_label = tk.Label(cart_frame, text="Please login to view your cart",
                                  font=("Arial", 14), bg="white", fg="#555")
            empty_label.pack(pady=50)
            return

        # Get user_id from email
        self.db.cursor.execute("SELECT user_id FROM users WHERE email = ?", (user_email,))
        user_data = self.db.cursor.fetchone()
        if not user_data:
            empty_label = tk.Label(cart_frame, text="User not found",
                                  font=("Arial", 14), bg="white", fg="#555")
            empty_label.pack(pady=50)
            return

        user_id = user_data['user_id']

        # Fetch cart items with menu item details
        self.db.cursor.execute("""
            SELECT ci.cart_item_id, ci.quantity, mi.name, mi.price, mi.item_id,
                   r.name as restaurant_name, r.restaurant_id
            FROM cart_items ci
            JOIN menu_items mi ON ci.item_id = mi.item_id
            JOIN restaurants r ON ci.restaurant_id = r.restaurant_id
            WHERE ci.user_id = ?
        """, (user_id,))
        cart_items = self.db.cursor.fetchall()

        if not cart_items:
            empty_label = tk.Label(cart_frame, text="Your cart is empty",
                                  font=("Arial", 14), bg="white", fg="#555")
            empty_label.pack(pady=50)
            return

        # Group items by restaurant
        restaurants = {}
        for item in cart_items:
            restaurant_id = item['restaurant_id']
            if restaurant_id not in restaurants:
                restaurants[restaurant_id] = {
                    'name': item['restaurant_name'],
                    'items': []
                }
            restaurants[restaurant_id]['items'].append(item)

        # Display items grouped by restaurant
        total_price = 0
        for restaurant_id, restaurant_data in restaurants.items():
            # Restaurant header
            restaurant_frame = tk.Frame(cart_frame, bg="#f9f9f9", padx=10, pady=5)
            restaurant_frame.pack(fill="x", pady=5)
            restaurant_label = tk.Label(restaurant_frame, text=restaurant_data['name'],
                                       font=("Arial", 14, "bold"), bg="#f9f9f9")
            restaurant_label.pack(anchor="w")

            # Display each cart item
            for item in restaurant_data['items']:
                item_price = item['price'] * item['quantity']
                total_price += item_price
                self.create_cart_item_card(cart_frame, item, self.update_cart_display)

        # Total price display
        total_frame = tk.Frame(cart_window, bg="white", height=100)
        total_frame.pack(fill="x", side="bottom", padx=20, pady=10)
        ttk.Separator(total_frame, orient='horizontal').pack(fill='x', pady=5)
        total_label = tk.Label(total_frame, text=f"Total: ₹{total_price:.2f}",
                              font=("Arial", 16, "bold"), bg="white")
        total_label.pack(side="left", pady=10)

        # Checkout button
        checkout_btn = tk.Button(total_frame, text="Proceed to Checkout", bg="#FF6347", fg="white",
                                font=("Arial", 12, "bold"), relief="flat", padx=20, pady=5,
                                command=lambda: self.show_payment_frame(cart_window, user_id, total_price, restaurants))
        checkout_btn.pack(side="right", pady=10)

        # Back button to return to homepage
        back_btn = tk.Button(total_frame, text="Back to Home", bg="#555", fg="white",
                            font=("Arial", 12), relief="flat", padx=15, pady=5,
                            command=cart_window.destroy)
        back_btn.pack(side="right", padx=10, pady=10)

    def create_cart_item_card(self, parent, item, callback):
        item_frame = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=10, pady=5)
        item_frame.pack(fill="x", pady=3, padx=10)

        # Item name and price
        name_label = tk.Label(item_frame, text=item['name'], font=("Arial", 12, "bold"), bg="white")
        name_label.grid(row=0, column=0, sticky="w")
        item_price = item['price'] * item['quantity']
        price_label = tk.Label(item_frame, text=f"₹{item_price:.2f}", font=("Arial", 12),
                              bg="white", fg="#FF6347")
        price_label.grid(row=0, column=2, sticky="e", padx=10)

        # Quantity controls
        quantity_frame = tk.Frame(item_frame, bg="white")
        quantity_frame.grid(row=1, column=0, sticky="w", pady=5)
        quantity_label = tk.Label(quantity_frame, text="Quantity: ", font=("Arial", 10), bg="white")
        quantity_label.grid(row=0, column=0)

        # Decrease quantity button
        decrease_btn = tk.Button(quantity_frame, text="-", font=("Arial", 10), bg="#f0f0f0",
                                command=lambda: self.update_cart_item_quantity(item['cart_item_id'],
                                                                             item['quantity'] - 1,
                                                                             callback))
        decrease_btn.grid(row=0, column=1, padx=2)

        # Quantity display
        quantity_var = tk.StringVar(value=str(item['quantity']))
        quantity_display = tk.Label(quantity_frame, textvariable=quantity_var, font=("Arial", 10),
                                   width=2, bg="white")
        quantity_display.grid(row=0, column=2, padx=5)

        # Increase quantity button
        increase_btn = tk.Button(quantity_frame, text="+", font=("Arial", 10), bg="#f0f0f0",
                                command=lambda: self.update_cart_item_quantity(item['cart_item_id'],
                                                                             item['quantity'] + 1,
                                                                             callback))
        increase_btn.grid(row=0, column=3, padx=2)

        # Remove button
        remove_btn = tk.Button(item_frame, text="Remove", font=("Arial", 10), bg="#f0f0f0", fg="#FF6347",
                              command=lambda: self.remove_cart_item(item['cart_item_id'], callback))
        remove_btn.grid(row=1, column=2, sticky="e", padx=10)

    def update_cart_item_quantity(self, cart_item_id, new_quantity, callback):
        try:
            if new_quantity <= 0:
                # If quantity is 0 or less, remove the item
                self.db.cursor.execute("DELETE FROM cart_items WHERE cart_item_id = ?", (cart_item_id,))
            else:
                # Update the quantity
                self.db.cursor.execute("""
                    UPDATE cart_items
                    SET quantity = ?
                    WHERE cart_item_id = ?
                """, (new_quantity, cart_item_id))

            self.db.conn.commit()
            # Refresh the cart display
            callback()
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to update cart: {e}")

    def remove_cart_item(self, cart_item_id, callback):
        try:
            self.db.cursor.execute("DELETE FROM cart_items WHERE cart_item_id = ?", (cart_item_id,))
            self.db.conn.commit()
            # Refresh the cart display
            callback()
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to remove item: {e}")

    def update_cart_display(self):
        # Close the current cart window and reopen it to refresh
        for widget in self.root.winfo_toplevel().winfo_children():
            if isinstance(widget, tk.Toplevel) and widget.title() == "Your Cart":
                widget.destroy()
        self.display_cart()

    def show_payment_frame(self, cart_window, user_id, total_amount, restaurants):
        # Hide the cart items
        for widget in cart_window.winfo_children():
            widget.pack_forget()

        # Payment header
        header_frame = tk.Frame(cart_window, bg="#FF6347", height=60)
        header_frame.pack(fill="x")
        payment_label = tk.Label(header_frame, text="Payment", font=("Arial", 18, "bold"),
                                fg="white", bg="#FF6347")
        payment_label.pack(pady=10)

        # Payment form
        payment_frame = tk.Frame(cart_window, bg="white")
        payment_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Order summary
        summary_label = tk.Label(payment_frame, text="Order Summary", font=("Arial", 14, "bold"), bg="white")
        summary_label.pack(anchor="w", pady=(0, 10))

        # Display total amount
        amount_label = tk.Label(payment_frame, text=f"Total Amount: ₹{total_amount:.2f}",
                               font=("Arial", 12), bg="white")
        amount_label.pack(anchor="w", pady=5)

        # Payment method selection
        method_label = tk.Label(payment_frame, text="Select Payment Method:",
                               font=("Arial", 12, "bold"), bg="white")
        method_label.pack(anchor="w", pady=(20, 10))

        payment_method = tk.StringVar(value="Credit Card")
        methods = ["Credit Card", "Debit Card", "UPI", "Cash on Delivery"]
        for method in methods:
            rb = tk.Radiobutton(payment_frame, text=method, variable=payment_method,
                               value=method, bg="white", font=("Arial", 11))
            rb.pack(anchor="w", pady=2)

        # Card details frame (shown only for card payments)
        card_frame = tk.Frame(payment_frame, bg="white")
        card_frame.pack(fill="x", pady=10)

        # Card number
        tk.Label(card_frame, text="Card Number:", bg="white", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        card_number = tk.Entry(card_frame, width=30)
        card_number.grid(row=0, column=1, sticky="w", pady=5)

        # Expiry date
        tk.Label(card_frame, text="Expiry Date (MM/YY):", bg="white", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=5)
        expiry_date = tk.Entry(card_frame, width=10)
        expiry_date.grid(row=1, column=1, sticky="w", pady=5)

        # CVV
        tk.Label(card_frame, text="CVV:", bg="white", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=5)
        cvv = tk.Entry(card_frame, width=5, show="*")
        cvv.grid(row=2, column=1, sticky="w", pady=5)

        # Buttons frame
        buttons_frame = tk.Frame(cart_window, bg="white")
        buttons_frame.pack(fill="x", side="bottom", padx=30, pady=20)

        # Back button
        back_btn = tk.Button(buttons_frame, text="Back to Cart", bg="#555", fg="white",
                            font=("Arial", 12), relief="flat", padx=15, pady=5,
                            command=lambda: self.update_cart_display())
        back_btn.pack(side="left")

        # Confirm payment button
        confirm_btn = tk.Button(buttons_frame, text="Confirm Payment", bg="#FF6347", fg="white",
                               font=("Arial", 12, "bold"), relief="flat", padx=20, pady=5,
                               command=lambda: self.process_payment(cart_window, user_id, total_amount,
                                                                  payment_method.get(), restaurants))
        confirm_btn.pack(side="right")

        # Show/hide card details based on payment method
        def toggle_card_details(*args):
            if payment_method.get() in ["Credit Card", "Debit Card"]:
                card_frame.pack(fill="x", pady=10)
            else:
                card_frame.pack_forget()

        payment_method.trace("w", toggle_card_details)
        toggle_card_details()  # Initial state

    def process_payment(self, cart_window, user_id, total_amount, payment_method, restaurants):
        try:
            # Start a transaction
            self.db.cursor.execute("BEGIN TRANSACTION")

            # Insert an order for each restaurant
            for restaurant_id, restaurant_data in restaurants.items():
                # Calculate subtotal for this restaurant
                restaurant_total = sum(item['price'] * item['quantity'] for item in restaurant_data['items'])

                # Add shipping cost (fixed at 30 for this example)
                shipping_cost = 30.0

                # Insert order record
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.db.cursor.execute("""
                    INSERT INTO orders
                    (user_id, restaurant_id, total_amount, shipping_cost, status, order_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, restaurant_id, restaurant_total, shipping_cost, 'pending', 'delivery', current_time))

                # Get the order_id of the inserted order
                order_id = self.db.cursor.lastrowid

                # Insert order items
                for item in restaurant_data['items']:
                    self.db.cursor.execute("""
                        INSERT INTO order_items
                        (order_id, item_id, quantity, price, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (order_id, item['item_id'], item['quantity'], item['price'], current_time))

                # Generate a random transaction ID
                transaction_id = f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"

                # Insert payment record
                self.db.cursor.execute("""
                    INSERT INTO payments
                    (order_id, payment_method, transaction_id, amount, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (order_id, payment_method, transaction_id, restaurant_total + shipping_cost, 'completed', current_time))

            # Clear the user's cart
            self.db.cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))

            # Commit the transaction
            self.db.conn.commit()

            # Show success message
            self.show_order_confirmation(cart_window)

        except Exception as e:
            # Rollback in case of error
            self.db.conn.rollback()
            messagebox.showerror("Payment Error", f"Failed to process payment: {e}")

    def show_order_confirmation(self, cart_window):
        # Clear the window
        for widget in cart_window.winfo_children():
            widget.pack_forget()

        # Success header
        header_frame = tk.Frame(cart_window, bg="#4CAF50", height=60)
        header_frame.pack(fill="x")
        success_label = tk.Label(header_frame, text="Order Confirmed!", font=("Arial", 18, "bold"),
                                fg="white", bg="#4CAF50")
        success_label.pack(pady=10)

        # Success message
        message_frame = tk.Frame(cart_window, bg="white")
        message_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Order confirmation message
        tk.Label(message_frame, text="Thank you for your order!",
                font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        tk.Label(message_frame, text="Your payment has been processed successfully.",
                font=("Arial", 12), bg="white").pack(pady=5)
        tk.Label(message_frame, text="You will receive an email confirmation shortly.",
                font=("Arial", 12), bg="white").pack(pady=5)

        # Order number
        order_number = f"#{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        tk.Label(message_frame, text=f"Order Number: {order_number}",
                font=("Arial", 12, "bold"), bg="white").pack(pady=20)

        # Estimated delivery time
        current_time = datetime.datetime.now()
        delivery_time = current_time + datetime.timedelta(minutes=45)
        delivery_time_str = delivery_time.strftime("%I:%M %p")
        tk.Label(message_frame, text=f"Estimated Delivery Time: {delivery_time_str}",
                font=("Arial", 12), bg="white").pack(pady=5)

        # Back to home button
        home_btn = tk.Button(message_frame, text="Back to Home", bg="#FF6347", fg="white",
                            font=("Arial", 12, "bold"), relief="flat", padx=20, pady=10,
                            command=cart_window.destroy)
        home_btn.pack(pady=30)

    def show_rating_dialog(self, restaurant_id, restaurant_name):
        # Create a new window for rating
        rating_window = tk.Toplevel(self.root)
        rating_window.title(f"Rate {restaurant_name}")
        rating_window.geometry("400x300")
        rating_window.config(bg="white")

        # Rating header
        header_frame = tk.Frame(rating_window, bg="#FF6347", height=60)
        header_frame.pack(fill="x")
        rating_label = tk.Label(header_frame, text=f"Rate {restaurant_name}", font=("Arial", 16, "bold"),
                               fg="white", bg="#FF6347")
        rating_label.pack(pady=10)

        # Rating form
        rating_frame = tk.Frame(rating_window, bg="white")
        rating_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Rating scale
        tk.Label(rating_frame, text="Your Rating:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", pady=5)
        rating_var = tk.IntVar(value=5)
        rating_scale = tk.Frame(rating_frame, bg="white")
        rating_scale.pack(fill="x", pady=10)
        for i in range(1, 6):
            rb = tk.Radiobutton(rating_scale, text=f"{i} ⭐", variable=rating_var,
                               value=i, bg="white", font=("Arial", 12))
            rb.pack(side="left", padx=10)

        # Review text
        tk.Label(rating_frame, text="Your Review (optional):", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", pady=5)
        review_text = tk.Text(rating_frame, height=4, width=40, font=("Arial", 10))
        review_text.pack(fill="x", pady=5)

        # Submit button
        submit_btn = tk.Button(rating_frame, text="Submit Rating", bg="#FF6347", fg="white",
                              font=("Arial", 12, "bold"), relief="flat", padx=20, pady=5,
                              command=lambda: self.submit_rating(restaurant_id, rating_var.get(),
                                                               review_text.get("1.0", "end-1c"), rating_window))
        submit_btn.pack(pady=15)

    def submit_rating(self, restaurant_id, rating_value, review, rating_window):
        # Get the current user's ID
        user_email = self.current_user_email
        if not user_email:
            messagebox.showinfo("Login Required", "Please login to rate restaurants")
            rating_window.destroy()
            return

        # Get user_id from email
        self.db.cursor.execute("SELECT user_id FROM users WHERE email = ?", (user_email,))
        user_data = self.db.cursor.fetchone()
        if not user_data:
            messagebox.showinfo("Error", "User not found")
            rating_window.destroy()
            return

        user_id = user_data['user_id']

        try:
            # Check if user has already rated this restaurant
            self.db.cursor.execute("""
                SELECT * FROM ratings
                WHERE restaurant_id = ? AND user_id = ?
            """, (restaurant_id, user_id))
            existing_rating = self.db.cursor.fetchone()

            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if existing_rating:
                # Update existing rating
                self.db.cursor.execute("""
                    UPDATE ratings
                    SET rating_value = ?, review = ?
                    WHERE rating_id = ?
                """, (rating_value, review, existing_rating['rating_id']))
                messagebox.showinfo("Success", "Your rating has been updated!")
            else:
                # Add new rating
                self.db.cursor.execute("""
                    INSERT INTO ratings
                    (restaurant_id, user_id, rating_value, review, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (restaurant_id, user_id, rating_value, review, current_time))
                messagebox.showinfo("Success", "Thank you for your rating!")

            self.db.conn.commit()
            # Refresh the restaurants display to show updated ratings
            self.display_restaurants_in_main_window()
            # Close the rating window
            rating_window.destroy()
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to submit rating: {e}")
            rating_window.destroy()

    # New function to display user orders
    def display_user_orders(self):
        # Create a new window for orders
        orders_window = tk.Toplevel(self.root)
        orders_window.title("My Orders")
        orders_window.geometry("800x600")
        orders_window.config(bg="white")

        # Orders header
        header_frame = tk.Frame(orders_window, bg="#FF6347", height=60)
        header_frame.pack(fill="x")
        orders_label = tk.Label(header_frame, text="My Orders", font=("Arial", 18, "bold"),
                               fg="white", bg="#FF6347")
        orders_label.pack(pady=10)

        # Create a frame for orders with scrollbar
        main_frame = tk.Frame(orders_window, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create a canvas for scrolling
        canvas = tk.Canvas(main_frame, bg="white")
        canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas for the orders
        orders_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=orders_frame, anchor="nw")

        # Get the current user's ID
        user_email = self.current_user_email
        if not user_email:
            empty_label = tk.Label(orders_frame, text="Please login to view your orders",
                                  font=("Arial", 14), bg="white", fg="#555")
            empty_label.pack(pady=50)
            return

        # Get user_id from email
        self.db.cursor.execute("SELECT user_id FROM users WHERE email = ?", (user_email,))
        user_data = self.db.cursor.fetchone()
        if not user_data:
            empty_label = tk.Label(orders_frame, text="User not found",
                                  font=("Arial", 14), bg="white", fg="#555")
            empty_label.pack(pady=50)
            return

        user_id = user_data['user_id']

        # Fetch user orders with restaurant details
        self.db.cursor.execute("""
            SELECT o.order_id, o.created_at, o.total_amount, o.status, r.name as restaurant_name
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
        """, (user_id,))
        
        orders = self.db.cursor.fetchall()

        if not orders:
            empty_label = tk.Label(orders_frame, text="You haven't placed any orders yet",
                                  font=("Arial", 14), bg="white", fg="#555")
            empty_label.pack(pady=50)
            return

        # Display each order
        for order in orders:
            self.create_order_card(orders_frame, order)

        # Back button
        back_btn = tk.Button(orders_window, text="Back to Home", bg="#555", fg="white",
                            font=("Arial", 12), relief="flat", padx=15, pady=5,
                            command=orders_window.destroy)
        back_btn.pack(side="bottom", pady=10)

    def create_order_card(self, parent, order):
        # Create a frame for the order
        order_frame = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=15, pady=10)
        order_frame.pack(fill="x", pady=8, padx=10)

        # Order ID and date
        order_date = datetime.datetime.strptime(order['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y at %I:%M %p')
        header_frame = tk.Frame(order_frame, bg="white")
        header_frame.pack(fill="x")
        
        order_id_label = tk.Label(header_frame, text=f"Order #{order['order_id']}", 
                                 font=("Arial", 14, "bold"), bg="white")
        order_id_label.pack(side="left")
        
        date_label = tk.Label(header_frame, text=order_date, 
                             font=("Arial", 12), bg="white", fg="#555")
        date_label.pack(side="right")
        
        ttk.Separator(order_frame, orient='horizontal').pack(fill='x', pady=5)
        
        # Restaurant name
        restaurant_label = tk.Label(order_frame, text=f"Restaurant: {order['restaurant_name']}", 
                                   font=("Arial", 12), bg="white")
        restaurant_label.pack(anchor="w", pady=2)
        
        # Order total
        total_label = tk.Label(order_frame, text=f"Total: ₹{order['total_amount']:.2f}", 
                              font=("Arial", 12), bg="white")
        total_label.pack(anchor="w", pady=2)
        
        # Order status with color coding
        status_frame = tk.Frame(order_frame, bg="white")
        status_frame.pack(fill="x", pady=5)
        
        status_label = tk.Label(status_frame, text="Status: ", 
                               font=("Arial", 12), bg="white")
        status_label.pack(side="left")
        
        # Color code based on status
        status_color = "#FF6347"  # Default red
        if order['status'] == 'delivered':
            status_color = "#4CAF50"  # Green
        elif order['status'] == 'shipped':
            status_color = "#2196F3"  # Blue
        elif order['status'] == 'scheduled':
            status_color = "#FF9800"  # Orange
        
        status_value = tk.Label(status_frame, text=order['status'].capitalize(), 
                               font=("Arial", 12, "bold"), bg="white", fg=status_color)
        status_value.pack(side="left")
        
        # Track order button
        track_btn = tk.Button(order_frame, text="Track Order", bg="#FF6347", fg="white",
                             font=("Arial", 10), relief="flat", padx=10, pady=2,
                             command=lambda o_id=order['order_id']: self.track_order(o_id))
        track_btn.pack(anchor="e", pady=5)

    def track_order(self, order_id):
        # Create a new window for tracking
        track_window = tk.Toplevel(self.root)
        track_window.title(f"Track Order #{order_id}")
        track_window.geometry("600x400")
        track_window.config(bg="white")
        
        # Header
        header_frame = tk.Frame(track_window, bg="#FF6347", height=60)
        header_frame.pack(fill="x")
        track_label = tk.Label(header_frame, text=f"Tracking Order #{order_id}", 
                              font=("Arial", 18, "bold"), fg="white", bg="#FF6347")
        track_label.pack(pady=10)
        
        # Main content
        content_frame = tk.Frame(track_window, bg="white")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Fetch order details
        self.db.cursor.execute("""
            SELECT o.*, r.name as restaurant_name
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            WHERE o.order_id = ?
        """, (order_id,))
        
        order = self.db.cursor.fetchone()
        
        if not order:
            error_label = tk.Label(content_frame, text="Order not found", 
                                  font=("Arial", 14), bg="white", fg="red")
            error_label.pack(pady=50)
            return
        
        # Update order status to "scheduled" if it's "pending"
        if order['status'] == 'pending':
            self.db.cursor.execute("""
                UPDATE orders
                SET status = 'scheduled'
                WHERE order_id = ?
            """, (order_id,))
            self.db.conn.commit()
            order['status'] = 'scheduled'
        
        # Order info
        order_date = datetime.datetime.strptime(order['created_at'], '%Y-%m-%d %H:%M:%S')
        info_label = tk.Label(content_frame, 
                             text=f"Order from {order['restaurant_name']} on {order_date.strftime('%B %d, %Y at %I:%M %p')}", 
                             font=("Arial", 12), bg="white")
        info_label.pack(anchor="w", pady=10)
        
        # Current status
        current_status = tk.Label(content_frame, text=f"Current Status: {order['status'].capitalize()}", 
                                 font=("Arial", 14, "bold"), bg="white")
        current_status.pack(anchor="w", pady=10)
        
        # Progress tracking
        progress_frame = tk.Frame(content_frame, bg="white")
        progress_frame.pack(fill="x", pady=20)
        
        # Define all possible statuses in order
        statuses = ["pending", "scheduled", "shipped", "delivered"]
        current_index = statuses.index(order['status'])
        
        # Create status indicators
        for i, status in enumerate(statuses):
            # Status circle
            status_frame = tk.Frame(progress_frame, bg="white")
            status_frame.pack(side="left", expand=True)
            
            # Determine color based on current progress
            if i < current_index:
                color = "#4CAF50"  # Completed - Green
            elif i == current_index:
                color = "#FF9800"  # Current - Orange
            else:
                color = "#E0E0E0"  # Upcoming - Gray
            
            # Create circle indicator
            circle = tk.Canvas(status_frame, width=40, height=40, bg="white", highlightthickness=0)
            circle.pack()
            circle.create_oval(5, 5, 35, 35, fill=color, outline="")
            
            # Status text
            status_label = tk.Label(status_frame, text=status.capitalize(), 
                                   font=("Arial", 10), bg="white")
            status_label.pack()
            
            # Connect with line if not the last status
            if i < len(statuses) - 1:
                line_canvas = tk.Canvas(progress_frame, width=50, height=20, bg="white", highlightthickness=0)
                line_canvas.pack(side="left")
                line_color = "#4CAF50" if i < current_index else "#E0E0E0"
                line_canvas.create_line(0, 10, 50, 10, fill=line_color, width=2)
        
        # Estimated delivery info
        # Calculate delivery date based on current date (April 18, 2025)
        current_date = datetime.datetime(2025, 4, 18, 0, 12)
        delivery_date = order_date + datetime.timedelta(days=1)
        
        # If the delivery date is in the past compared to current date, show delivered status
        if delivery_date < current_date and order['status'] != 'delivered':
            self.db.cursor.execute("""
                UPDATE orders
                SET status = 'delivered'
                WHERE order_id = ?
            """, (order_id,))
            self.db.conn.commit()
            order['status'] = 'delivered'
            messagebox.showinfo("Order Status", "Your order has been delivered!")
            # Refresh the tracking window
            track_window.destroy()
            self.track_order(order_id)
            return
        
        delivery_label = tk.Label(content_frame, 
                                 text=f"Estimated Delivery: {delivery_date.strftime('%B %d, %Y by %I:%M %p')}", 
                                 font=("Arial", 12), bg="white")
        delivery_label.pack(anchor="w", pady=20)
        
        # Back button
        back_btn = tk.Button(track_window, text="Back", bg="#555", fg="white",
                            font=("Arial", 12), relief="flat", padx=15, pady=5,
                            command=track_window.destroy)
        back_btn.pack(side="bottom", pady=20)

    def show_order_tracker(self):
        # Create a new window for order tracking
        tracker_window = tk.Toplevel(self.root)
        tracker_window.title("Track Your Order")
        tracker_window.geometry("500x300")
        tracker_window.config(bg="white")
        
        # Header
        header_frame = tk.Frame(tracker_window, bg="#FF6347", height=60)
        header_frame.pack(fill="x")
        tracker_label = tk.Label(header_frame, text="Track Your Order", 
                                font=("Arial", 18, "bold"), fg="white", bg="#FF6347")
        tracker_label.pack(pady=10)
        
        # Main content
        content_frame = tk.Frame(tracker_window, bg="white")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Instructions
        instruction_label = tk.Label(content_frame, 
                                    text="Enter your order number to track its status", 
                                    font=("Arial", 12), bg="white")
        instruction_label.pack(pady=10)
        
        # Order ID input
        order_id_frame = tk.Frame(content_frame, bg="white")
        order_id_frame.pack(fill="x", pady=10)
        
        order_id_label = tk.Label(order_id_frame, text="Order #:", 
                                 font=("Arial", 12), bg="white")
        order_id_label.pack(side="left")
        
        order_id_var = tk.StringVar()
        order_id_entry = tk.Entry(order_id_frame, textvariable=order_id_var, 
                                 font=("Arial", 12), width=15)
        order_id_entry.pack(side="left", padx=10)
        
        # Status message
        status_var = tk.StringVar()
        status_label = tk.Label(content_frame, textvariable=status_var, 
                               font=("Arial", 12), bg="white", fg="#555")
        status_label.pack(pady=10)
        
        # Function to handle tracking
        def track_order_by_id():
            order_id = order_id_var.get().strip()
            if not order_id:
                status_var.set("Please enter an order number")
                return
            
            try:
                order_id = int(order_id)
                # Check if order exists
                self.db.cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
                order = self.db.cursor.fetchone()
                
                if order:
                    # Close this window and open the detailed tracking
                    tracker_window.destroy()
                    self.track_order(order_id)
                else:
                    status_var.set("Order not found. Please check the order number.")
            except ValueError:
                status_var.set("Please enter a valid order number")
        
        # Track button
        track_btn = tk.Button(content_frame, text="Track Order", bg="#FF6347", fg="white",
                             font=("Arial", 12), relief="flat", padx=15, pady=5,
                             command=track_order_by_id)
        track_btn.pack(pady=10)
        
        # Back button
        back_btn = tk.Button(tracker_window, text="Back", bg="#555", fg="white",
                            font=("Arial", 12), relief="flat", padx=15, pady=5,
                            command=tracker_window.destroy)
        back_btn.pack(side="bottom", pady=10)

    def show_settings(self):
        # Create a new window for settings
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.config(bg="white")
        
        # Header
        header_frame = tk.Frame(settings_window, bg="#FF6347", height=60)
        header_frame.pack(fill="x")
        settings_label = tk.Label(header_frame, text="Settings", 
                                 font=("Arial", 18, "bold"), fg="white", bg="#FF6347")
        settings_label.pack(pady=10)
        
        # Main content
        content_frame = tk.Frame(settings_window, bg="white")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # App appearance section
        appearance_label = tk.Label(content_frame, text="App Appearance", 
                                   font=("Arial", 14, "bold"), bg="white")
        appearance_label.pack(anchor="w", pady=(0, 10))
        
        # Dark mode toggle
        dark_mode_frame = tk.Frame(content_frame, bg="white")
        dark_mode_frame.pack(fill="x", pady=5)
        
        dark_mode_label = tk.Label(dark_mode_frame, text="Dark Mode", 
                                  font=("Arial", 12), bg="white")
        dark_mode_label.pack(side="left")
        
        # Variable to track dark mode state
        self.dark_mode_var = tk.BooleanVar(value=False)
        
        # Function to toggle dark/light mode
        def toggle_dark_mode():
            if self.dark_mode_var.get():
                # Apply dark mode
                settings_window.config(bg="#333")
                content_frame.config(bg="#333")
                dark_mode_frame.config(bg="#333")
                appearance_label.config(bg="#333", fg="white")
                dark_mode_label.config(bg="#333", fg="white")
                account_label.config(bg="#333", fg="white")
                notif_label.config(bg="#333", fg="white")
                email_notif_frame.config(bg="#333")
                email_notif_label.config(bg="#333", fg="white")
                change_pwd_btn.config(bg="#444", fg="white")
                # Apply dark mode to main window
                self.root.config(bg="#333")
                self.main_content.config(bg="#333")
                self.resto_label.config(bg="#333", fg="white")
                self.canvas.config(bg="#333")
                self.restaurants_frame.config(bg="#333")
            else:
                # Apply light mode
                settings_window.config(bg="white")
                content_frame.config(bg="white")
                dark_mode_frame.config(bg="white")
                appearance_label.config(bg="white", fg="black")
                dark_mode_label.config(bg="white", fg="black")
                account_label.config(bg="white", fg="black")
                notif_label.config(bg="white", fg="black")
                email_notif_frame.config(bg="white")
                email_notif_label.config(bg="white", fg="black")
                change_pwd_btn.config(bg="#f0f0f0", fg="black")
                # Apply light mode to main window
                self.root.config(bg="white")
                self.main_content.config(bg="white")
                self.resto_label.config(bg="white", fg="#333")
                self.canvas.config(bg="white")
                self.restaurants_frame.config(bg="white")
        
        # Create toggle switch
        dark_mode_switch = tk.Checkbutton(dark_mode_frame, variable=self.dark_mode_var, 
                                         command=toggle_dark_mode, bg="white")
        dark_mode_switch.pack(side="right")
        
        # Account settings section
        account_label = tk.Label(content_frame, text="Account Settings", 
                                font=("Arial", 14, "bold"), bg="white")
        account_label.pack(anchor="w", pady=(20, 10))
        
        # Change password button
        change_pwd_btn = tk.Button(content_frame, text="Change Password", bg="#f0f0f0", fg="black",
                                  font=("Arial", 12), relief="flat", padx=15, pady=5)
        change_pwd_btn.pack(anchor="w", pady=5)
        
        # Notification settings section
        notif_label = tk.Label(content_frame, text="Notification Settings", 
                              font=("Arial", 14, "bold"), bg="white")
        notif_label.pack(anchor="w", pady=(20, 10))
        
        # Email notifications toggle
        email_notif_frame = tk.Frame(content_frame, bg="white")
        email_notif_frame.pack(fill="x", pady=5)
        
        email_notif_label = tk.Label(email_notif_frame, text="Email Notifications", 
                                    font=("Arial", 12), bg="white")
        email_notif_label.pack(side="left")
        
        email_notif_var = tk.BooleanVar(value=True)
        email_notif_switch = tk.Checkbutton(email_notif_frame, variable=email_notif_var, bg="white")
        email_notif_switch.pack(side="right")
        
        # Back button
        back_btn = tk.Button(settings_window, text="Save Settings", bg="#FF6347", fg="white",
                            font=("Arial", 12), relief="flat", padx=15, pady=5,
                            command=settings_window.destroy)
        back_btn.pack(side="bottom", pady=20)

def main(user_email=None):
    root = tk.Tk()
    app = FoodOrderingSystem(root, user_email)
    root.mainloop()  # This line is critical!

if __name__ == "__main__":
    main()