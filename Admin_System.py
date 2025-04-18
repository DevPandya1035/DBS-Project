import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk
import os
import time
from database import DatabaseManager  # Import DatabaseManager

class AdminLoginWindow:
    def __init__(self, root, user_login_root=None, width=600, height=400):
        self.root = root
        self.user_login_root = user_login_root
        self.root.title("Admin Login")

        # Initialize database connection
        self.db = DatabaseManager()

        # Set an initial size to avoid sudden expansion
        self.root.geometry(f"{width}x{height}")  # Adjust as needed
        self.root.resizable(True, True)

        # Create canvas for the gradient background
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Create login frame
        self.login_frame = tk.Frame(self.canvas, bg="white", bd=5, relief="flat")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Bind resize event
        self.root.bind("<Configure>", self.on_resize)

        # Load icons and background image
        self.load_resources()

        # Clear placeholder on focus
        self.email_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.email_entry, "Enter Email"))
        self.password_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.password_entry, "Enter Password"))

        # Process UI tasks before showing the window
        self.root.update_idletasks()

        # Create gradient and show the window
        self.create_gradient()
        self.root.deiconify()  # Now show the window smoothly

    def load_resources(self):
        """ Load all necessary resources (icons) """
        # Load icons
        try:
            self.user_icon = ImageTk.PhotoImage(Image.open("user_icon.png").resize((50, 50), Image.Resampling.LANCZOS))
        except:
            self.user_icon = None  # Fallback if icon not found

        try:
            self.email_icon = ImageTk.PhotoImage(Image.open("email_icon.png").resize((20, 20), Image.Resampling.LANCZOS))
        except:
            self.email_icon = None  # Fallback if icon not found

        try:
            self.password_icon = ImageTk.PhotoImage(Image.open("password_icon.png").resize((20, 20), Image.Resampling.LANCZOS))
        except:
            self.password_icon = None  # Fallback if icon not found

        # Add UI components
        if self.user_icon:
            self.user_label = tk.Label(self.login_frame, image=self.user_icon, bg="white")
            self.user_label.grid(row=0, column=0, columnspan=2, pady=10)
        else:
            self.user_label = tk.Label(self.login_frame, text="👤", font=("Arial", 24), bg="white")
            self.user_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.admin_label = tk.Label(self.login_frame, text="Admin Login", font=("Arial", 16, "bold"), bg="white")
        self.admin_label.grid(row=1, column=0, columnspan=2, pady=5)

        if self.email_icon:
            self.email_label = tk.Label(self.login_frame, image=self.email_icon, bg="white")
            self.email_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        else:
            self.email_label = tk.Label(self.login_frame, text="✉", font=("Arial", 16), bg="white")
            self.email_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        
        self.email_entry = tk.Entry(self.login_frame, width=25, font=("Arial", 12))
        self.email_entry.insert(0, "Enter Email")
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)

        if self.password_icon:
            self.password_label = tk.Label(self.login_frame, image=self.password_icon, bg="white")
            self.password_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        else:
            self.password_label = tk.Label(self.login_frame, text="🔒", font=("Arial", 16), bg="white")
            self.password_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        
        self.password_entry = tk.Entry(self.login_frame, width=25, font=("Arial", 12))
        self.password_entry.insert(0, "Enter Password")
        self.password_entry.grid(row=3, column=1, padx=5, pady=5)

        # Add command to the forgot password label
        self.forgot_password = tk.Label(self.login_frame, text="Forgot password?", font=("Arial", 10), fg="blue", bg="white", cursor="hand2")
        self.forgot_password.grid(row=4, column=0, columnspan=2, pady=5)
        self.forgot_password.bind("<Button-1>", self.show_forgot_password)

        self.signin_button = tk.Button(self.login_frame, text="Sign In", font=("Arial", 12), bg="#333", fg="white", width=15, command=self.sign_in)
        self.signin_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.register_button = tk.Button(self.login_frame, text="Register Admin", font=("Arial", 10), bg="#4CAF50", fg="white", width=15, command=self.show_register_screen)
        self.register_button.grid(row=6, column=0, columnspan=2, pady=5)

        self.back_button = tk.Button(self.login_frame, text="Back to User Login", font=("Arial", 10), bg="#ddd", width=15, command=self.back_to_user_login)
        self.back_button.grid(row=7, column=0, columnspan=2, pady=10)

    def on_resize(self, event):
        # Update the gradient on window resize
        self.create_gradient()
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if entry == self.password_entry:
                entry.config(show="*")
    
    def sign_in(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        success, result = self.db.verify_admin_login(email, password)
        
        if success:
            messagebox.showinfo("Success", "Admin login successful!")
            # Add logic to navigate to the admin dashboard
        else:
            messagebox.showerror("Error", f"Admin login failed for email: {email}. {result}")
    
    def back_to_user_login(self):
        if self.user_login_root:
            # Destroy the admin login window
            self.root.destroy()
            # Restore the user login window
            self.user_login_root.deiconify()
        else:
            print("User login window reference not set")

    def create_gradient(self):
        """Creates a gradient background canvas."""
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        self.canvas.delete("all")
        
        # Create gradient (blue to red)
        colors = [
            (0, 0, 255),      # Blue
            (75, 0, 230),     # Blue-purple
            (150, 0, 180),    # Purple
            (200, 0, 130),    # Purple-red
            (255, 0, 0)       # Red
        ]
        
        segments = len(colors) - 1
        segment_width = width / segments
        
        for i in range(segments):
            start_color = colors[i]
            end_color = colors[i+1]
            
            for j in range(int(segment_width)):
                # Position within this segment (0 to 1)
                pos = j / segment_width
                
                # Calculate color for this position
                r = int(start_color[0] + (end_color[0] - start_color[0]) * pos)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * pos)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * pos)
                
                # Calculate the x position
                x = int(i * segment_width + j)
                
                # Draw the vertical line
                color = f'#{r:02x}{g:02x}{b:02x}'
                self.canvas.create_line(x, 0, x, height, fill=color)

    def show_forgot_password(self, event):
        """Displays the password forgot screen."""
        # Clear the current contents of the frame
        for widget in self.login_frame.winfo_children():
            widget.destroy()

        # Title
        title_label = tk.Label(self.login_frame, text="Reset Password", font=("Arial", 16, "bold"), bg="white")
        title_label.grid(row=0, column=0, columnspan=2, pady=(30, 20))

        # User icon at the top
        if self.user_icon:
            user_icon_label = tk.Label(self.login_frame, image=self.user_icon, bg="white")
        else:
            user_icon_label = tk.Label(self.login_frame, text="👤", font=("Arial", 24), bg="white")
        user_icon_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Email Field with icon
        email_frame = tk.Frame(self.login_frame, bg="white")
        email_frame.grid(row=2, column=0, columnspan=2, padx=40, pady=5, sticky="ew")
        
        if self.email_icon:
            email_icon_label = tk.Label(email_frame, image=self.email_icon, bg="white")
        else:
            email_icon_label = tk.Label(email_frame, text="✉", font=("Arial", 16), bg="white")
        email_icon_label.pack(side="left", padx=(0, 10))
        
        email_label = tk.Label(email_frame, text="Email", font=("Arial", 12), bg="white", anchor="w")
        email_label.pack(side="left", fill="x", expand=True)
        
        self.reset_email_entry = tk.Entry(self.login_frame, width=25, font=("Arial", 12))
        self.reset_email_entry.grid(row=3, column=0, columnspan=2, padx=40, pady=(0, 25))

        # Reset Button
        reset_button = tk.Button(self.login_frame, text="Send Reset Link", font=("Arial", 12), bg="#007BFF", fg="white", 
                                activebackground="#0056b3", activeforeground="white", bd=0,
                                command=self.reset_password)
        reset_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Back Button
        back_button = tk.Button(self.login_frame, text="Back to Login", font=("Arial", 10), fg="#007BFF", bg="white", 
                               bd=0, activebackground="white", command=self.show_login_screen)
        back_button.grid(row=5, column=0, columnspan=2, pady=5)

    def reset_password(self):
        """Simulates sending a reset password link."""
        email = self.reset_email_entry.get()
        if not email:
            messagebox.showerror("Error", "Please enter your email.")
            return
        
        # Fetch admin ID based on email
        success, admin = self.db.verify_admin_login(email, "")  # Empty password for verification
        
        if success:
            # Generate a new password (for simplicity, use a timestamp)
            new_password = str(int(time.time()))
            
            # Update the admin's password
            success, message = self.db.change_admin_password(admin['admin_id'], new_password)
            
            if success:
                messagebox.showinfo("Success", f"Password reset successful! New password: {new_password}")
                self.show_login_screen()
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showerror("Error", "Admin not found.")

    def show_login_screen(self):
        """Displays the login screen."""
        # Clear the current contents of the frame
        for widget in self.login_frame.winfo_children():
            widget.destroy()

        # Rebuild the login screen
        self.load_resources()

    def show_register_screen(self):
        """Displays the admin registration screen."""
        # Clear the current contents of the frame
        for widget in self.login_frame.winfo_children():
            widget.destroy()

        # Title
        title_label = tk.Label(self.login_frame, text="Register Admin", font=("Arial", 16, "bold"), bg="white")
        title_label.grid(row=0, column=0, columnspan=2, pady=(30, 20))

        # User icon at the top
        if self.user_icon:
            user_icon_label = tk.Label(self.login_frame, image=self.user_icon, bg="white")
        else:
            user_icon_label = tk.Label(self.login_frame, text="👤", font=("Arial", 24), bg="white")
        user_icon_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Username Field
        username_frame = tk.Frame(self.login_frame, bg="white")
        username_frame.grid(row=2, column=0, columnspan=2, padx=40, pady=5, sticky="ew")
        
        username_label = tk.Label(username_frame, text="Username", font=("Arial", 12), bg="white", anchor="w")
        username_label.pack(side="left", padx=(0, 10))
        
        self.username_entry = tk.Entry(self.login_frame, width=25, font=("Arial", 12))
        self.username_entry.grid(row=3, column=0, columnspan=2, padx=40, pady=(0, 15))

        # Email Field with icon
        email_frame = tk.Frame(self.login_frame, bg="white")
        email_frame.grid(row=4, column=0, columnspan=2, padx=40, pady=5, sticky="ew")
        
        email_label = tk.Label(email_frame, text="Email", font=("Arial", 12), bg="white", anchor="w")
        email_label.pack(side="left", padx=(0, 10))
        
        self.register_email_entry = tk.Entry(self.login_frame, width=25, font=("Arial", 12))
        self.register_email_entry.grid(row=5, column=0, columnspan=2, padx=40, pady=(0, 15))

        # Password Field with icon
        password_frame = tk.Frame(self.login_frame, bg="white")
        password_frame.grid(row=6, column=0, columnspan=2, padx=40, pady=5, sticky="ew")
        
        password_label = tk.Label(password_frame, text="Password", font=("Arial", 12), bg="white", anchor="w")
        password_label.pack(side="left", padx=(0, 10))
        
        self.register_password_entry = tk.Entry(self.login_frame, width=25, font=("Arial", 12), show="•")
        self.register_password_entry.grid(row=7, column=0, columnspan=2, padx=40, pady=(0, 25))

        # Register Button
        register_button = tk.Button(self.login_frame, text="Register Admin", font=("Arial", 12), 
                                   bg="#4CAF50", fg="white", activebackground="#45a049",
                                   activeforeground="white", bd=0,
                                   command=self.register_admin)
        register_button.grid(row=8, column=0, columnspan=2, pady=10)

        # Back Button
        back_button = tk.Button(self.login_frame, text="Back to Login", font=("Arial", 10), 
                               fg="#007BFF", bg="white", bd=0, activebackground="white",
                               command=self.show_login_screen)
        back_button.grid(row=9, column=0, columnspan=2, pady=5)

    def register_admin(self):
        """Registers a new admin."""
        username = self.username_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        
        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        success, message = self.db.register_admin(username, password, email)
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_login_screen()
        else:
            messagebox.showerror("Error", message)
                
    def sign_in(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        success, result = self.db.verify_admin_login(email, password)
        
        if success:
            messagebox.showinfo("Success", "Admin login successful!")
            self.root.withdraw()  # Hide the login window
            self.open_admin_portal(result)  # result contains admin dict
        else:
            messagebox.showerror("Error", f"Admin login failed: {result}")
            
    def open_admin_portal(self, admin_data):
        """Open the admin portal with the provided admin data."""
        from Admin_Portal import AdminPortal  # Import here to avoid circular imports
        
        # Create a new window for the admin portal
        portal_window = tk.Toplevel(self.root)
        portal_window.geometry("1200x700")
        portal_window.configure(bg="#f5f5f5")
        
        # Pass the admin data and database connection to the AdminPortal
        admin_portal = AdminPortal(portal_window, admin_data, self.db)
        
        # Handle window close event to properly close the portal
        def on_closing():
            portal_window.destroy()
            self.root.deiconify()  # Show login window again
        
        portal_window.protocol("WM_DELETE_WINDOW", on_closing)
                
    def logout(self, portal_window):
        portal_window.destroy()
        self.root.deiconify()  # Show login window again
        




if __name__ == "__main__":
    root = tk.Tk()
    app = AdminLoginWindow(root)
    root.mainloop()