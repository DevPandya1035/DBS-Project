import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk, ImageDraw
import os
import time
from database import DatabaseManager  # Import DatabaseManager
from Admin_System import AdminLoginWindow  # Import AdminLoginWindow
import HomePage #Import HomePage

class LoginSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Login System")
        self.root.geometry("800x600")
        self.root.state("zoomed")  # Start in maximized mode

        # Initialize database connection
        self.db = DatabaseManager()

        # Create gradient background
        self.create_gradient_background()

        # Configure fonts
        self.title_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.label_font = font.Font(family="Helvetica", size=12)
        self.button_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.small_font = font.Font(family="Helvetica", size=10)

        # Frame for Login/Register
        self.frame = tk.Frame(self.root, bg="white", bd=0, relief="raised", highlightthickness=1, highlightbackground="#dddddd")
        self.frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=450)

        # Load user icon
        self.load_icons()

        # Show the login screen by default
        self.show_login_screen()

    def create_gradient_background(self):
        """Creates a gradient background canvas."""
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Create gradient (blue to red)
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        
        # Create a smoother gradient
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

    def load_icons(self):
        """Load user icon from file."""
        try:
            self.user_icon = Image.open("user_icon.png")
            self.user_icon = self.user_icon.resize((60, 60), Image.Resampling.LANCZOS)
            self.user_icon = ImageTk.PhotoImage(self.user_icon)
        except:
            # Create a default user icon if file not found
            self.user_icon = self.create_default_user_icon()

    def create_default_user_icon(self):
        """Create a default user icon if file not found."""
        icon_size = 60
        user_icon = Image.new("RGB", (icon_size, icon_size), "white")
        draw = ImageDraw.Draw(user_icon)
        
        # Draw head
        head_radius = icon_size // 4
        head_x, head_y = icon_size // 2, icon_size // 3
        draw.ellipse([
            head_x - head_radius, head_y - head_radius, 
            head_x + head_radius, head_y + head_radius
        ], fill="black")
        
        # Draw body
        body_width = head_radius * 2
        body_height = head_radius * 2
        body_x, body_y = icon_size // 2, icon_size - (icon_size // 4)
        draw.pieslice([
            body_x - body_width, body_y - body_height * 0.6, 
            body_x + body_width, body_y + body_height * 0.6
        ], start=0, end=180, fill="black")
        
        return ImageTk.PhotoImage(user_icon)

    def clear_frame(self):
        """Removes all widgets from the frame before switching screens."""
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        """Displays the login screen."""
        self.clear_frame()

        # Title
        title_label = tk.Label(self.frame, text="Login", font=self.title_font, bg="white")
        title_label.pack(pady=(30, 10))

        # User icon at the top
        user_icon_label = tk.Label(self.frame, image=self.user_icon, bg="white")
        user_icon_label.pack(pady=(0, 20))

        # Email Field with icon
        email_frame = tk.Frame(self.frame, bg="white")
        email_frame.pack(fill="x", padx=40, pady=5)
        
        email_icon_label = tk.Label(email_frame, text="✉", font=("Arial", 16), bg="white")
        email_icon_label.pack(side="left", padx=(0, 10))
        
        email_label = tk.Label(email_frame, text="Email", font=self.label_font, bg="white", anchor="w")
        email_label.pack(side="left", fill="x", expand=True)
        
        self.email_entry = tk.Entry(self.frame, font=self.label_font, bd=1, relief="solid", width=30)
        self.email_entry.pack(fill="x", padx=40, pady=(0, 15))

        # Password Field with icon
        password_frame = tk.Frame(self.frame, bg="white")
        password_frame.pack(fill="x", padx=40, pady=5)
        
        password_icon_label = tk.Label(password_frame, text="🔒", font=("Arial", 16), bg="white")
        password_icon_label.pack(side="left", padx=(0, 10))
        
        password_label = tk.Label(password_frame, text="Password", font=self.label_font, bg="white", anchor="w")
        password_label.pack(side="left", fill="x", expand=True)
        
        self.password_entry = tk.Entry(self.frame, font=self.label_font, bd=1, relief="solid", show="•", width=30)
        self.password_entry.pack(fill="x", padx=40, pady=(0, 10))

        # Create a frame for the buttons
        button_frame = tk.Frame(self.frame, bg="white")
        button_frame.pack(fill="x", padx=40, pady=5)

        # Forgot Password on the left
        forgot_button = tk.Button(button_frame, text="Forgot Password?", font=self.small_font, 
                                 fg="#007BFF", bg="white", bd=0, activebackground="white",
                                 command=self.show_forgot_password)
        forgot_button.pack(side="left", pady=(0, 20))

        # Admin Login on the right
        admin_login_button = tk.Button(button_frame, text="Admin Login", font=self.small_font, 
                                     fg="#007BFF", bg="white", bd=0, activebackground="white",
                                     command=self.admin_login)
        admin_login_button.pack(side="right", pady=(0, 20))

        # Login Button
        login_button = tk.Button(self.frame, text="Login", font=self.button_font, 
                                bg="#343A40", fg="white", activebackground="#1A1E21",
                                activeforeground="white", bd=0, 
                                command=self.login)
        login_button.pack(fill="x", padx=100, pady=(0, 10), ipady=8)

        # Register Button
        register_button = tk.Button(self.frame, text="Register", font=self.button_font, 
                                   bg="#28A745", fg="white", activebackground="#1E7E34",
                                   activeforeground="white", bd=0,
                                   command=self.show_register_screen)
        register_button.pack(fill="x", padx=100, pady=(0, 1), ipady=5)

    def show_register_screen(self):
        """Displays the registration screen."""
        self.clear_frame()

        # Title
        title_label = tk.Label(self.frame, text="Register", font=self.title_font, bg="white")
        title_label.pack(pady=(15, 5))

        # User icon at the top
        user_icon_label = tk.Label(self.frame, image=self.user_icon, bg="white")
        user_icon_label.pack(pady=(0, 5))

        # Username Field
        username_frame = tk.Frame(self.frame, bg="white")
        username_frame.pack(fill="x", padx=10, pady=1)
        
        username_label = tk.Label(username_frame, text="Username", font=self.label_font, bg="white", anchor="w")
        username_label.pack(side="left", padx=(0, 10))
        
        self.username_entry = tk.Entry(self.frame, font=self.label_font, bd=1, relief="solid", width=30)
        self.username_entry.pack(fill="x", padx=10, pady=(0, 5))

        # Email Field with icon
        email_frame = tk.Frame(self.frame, bg="white")
        email_frame.pack(fill="x", padx=10, pady=1)
        
        email_label = tk.Label(email_frame, text="Email", font=self.label_font, bg="white", anchor="w")
        email_label.pack(side="left", padx=(0, 10))
        
        self.register_email_entry = tk.Entry(self.frame, font=self.label_font, bd=1, relief="solid", width=30)
        self.register_email_entry.pack(fill="x", padx=10, pady=(0, 5))

        # Password Field with icon
        password_frame = tk.Frame(self.frame, bg="white")
        password_frame.pack(fill="x", padx=10, pady=1)
        
        password_label = tk.Label(password_frame, text="Password", font=self.label_font, bg="white", anchor="w")
        password_label.pack(side="left", padx=(0, 5))
        
        self.register_password_entry = tk.Entry(self.frame, font=self.label_font, bd=1, relief="solid", show="•", width=30)
        self.register_password_entry.pack(fill="x", padx=10, pady=(0, 5))

        # Phone Number Field
        phone_frame = tk.Frame(self.frame, bg="white")
        phone_frame.pack(fill="x", padx=10, pady=1)
        
        phone_label = tk.Label(phone_frame, text="Phone Number", font=self.label_font, bg="white", anchor="w")
        phone_label.pack(side="left", padx=(0, 5))
        
        self.phone_entry = tk.Entry(self.frame, font=self.label_font, bd=1, relief="solid", width=30)
        self.phone_entry.pack(fill="x", padx=10, pady=(0, 5))

        # Register Button
        register_button = tk.Button(self.frame, text="Register", font=self.button_font, 
                                   bg="#28A745", fg="white", activebackground="#1E7E34",
                                   activeforeground="white", bd=0,
                                   command=self.register)
        register_button.pack(fill="x", padx=100, pady=(0, 1), ipady=4)

        # Back Button
        back_button = tk.Button(self.frame, text="Back to Login", font=self.small_font, 
                               fg="#007BFF", bg="white", bd=0, activebackground="white",
                               command=self.show_login_screen)
        back_button.pack(pady=3)

    def register(self):
        """Handles registration and redirects to login screen."""
        username = self.username_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        phone_number = self.phone_entry.get()

        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        success, result = self.db.register_user(username, password, email)
        
        if success:
            messagebox.showinfo("Success", "Login successful!")
            # Switch to HomePage and pass the user's email
            self.root.destroy()  # Destroy the login window
            HomePage.main(user_email=email)  # Open the HomePage with user email
        else:
            messagebox.showerror("Error", f"Login failed for user with email: {email}. {result}")

    def login(self):
        """Handles login functionality."""
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        success, result = self.db.verify_user_login(email, password)
        
        if success:
            messagebox.showinfo("Success", "Login successful!")
            # Add logic to navigate to the user dashboard
            self.root.destroy()  # Destroy the login window
            HomePage.main()  # Open the HomePage            
        else:
            messagebox.showerror("Error", f"Login failed for user with email: {email}. {result}")

    def admin_login(self):
        """Handles admin login functionality by showing the admin registration window."""
        # Withdraw the user login window instead of destroying it
        self.root.withdraw()
        
        # Create a new Toplevel window for admin login
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Login")
        admin_window.geometry("800x600")
        admin_window.state("zoomed")
        
        # Create an instance of AdminLoginWindow in the new Toplevel window
        self.admin_app = AdminLoginWindow(admin_window, user_login_root=self.root)

    def return_to_user_login(self):
        """Returns to the user login screen from admin login."""
        # Clear the admin login interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Recreate the gradient background
        self.create_gradient_background()
        
        # Recreate the frame
        self.frame = tk.Frame(self.root, bg="white", bd=0, relief="raised", highlightthickness=1, highlightbackground="#dddddd")
        self.frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=450)
        
        # Reload user icon
        self.load_icons()
        
        # Show the login screen
        self.show_login_screen()

    def show_forgot_password(self):
        """Displays the password forgot screen."""
        self.clear_frame()

        title_label = tk.Label(self.frame, text="Reset Password", font=self.title_font, bg="white")
        title_label.pack(pady=(30, 20))

        # User icon at the top
        user_icon_label = tk.Label(self.frame, image=self.user_icon, bg="white")
        user_icon_label.pack(pady=(0, 20))

        # Email Field with icon
        email_frame = tk.Frame(self.frame, bg="white")
        email_frame.pack(fill="x", padx=40, pady=5)
        
        email_label = tk.Label(email_frame, text="Email", font=self.label_font, bg="white", anchor="w")
        email_label.pack(side="left", padx=(0, 10))
        
        self.reset_email_entry = tk.Entry(self.frame, font=self.label_font, bd=1, relief="solid", width=30)
        self.reset_email_entry.pack(fill="x", padx=40, pady=(0, 25))

        # Reset Button
        reset_button = tk.Button(self.frame, text="Send Reset Link", font=self.button_font, 
                                bg="#007BFF", fg="white", activebackground="#0056b3",
                                activeforeground="white", bd=0,
                                command=self.reset_password)
        reset_button.pack(fill="x", padx=100, pady=(0, 15), ipady=8)

        # Back Button
        back_button = tk.Button(self.frame, text="Back to Login", font=self.small_font, 
                               fg="#007BFF", bg="white", bd=0, activebackground="white",
                               command=self.show_login_screen)
        back_button.pack(pady=5)

    def reset_password(self):
        """Simulates sending a reset password link."""
        email = self.reset_email_entry.get()
        if not email:
            messagebox.showerror("Error", "Please enter your email.")
            return
        
        # Fetch user ID based on email
        success, user = self.db.verify_user_login(email, "")  # Empty password for verification
        
        if success:
            # Generate a new password (for simplicity, use a timestamp)
            new_password = str(int(time.time()))
            
            # Update the user's password
            success, message = self.db.change_user_password(user['user_id'], new_password)
            
            if success:
                messagebox.showinfo("Success", f"Password reset successful! New password: {new_password}")
                self.show_login_screen()
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showerror("Error", "User not found.")
            
    def login(self):
        """Handles login functionality."""
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        success, result = self.db.verify_user_login(email, password)
        
        if success:
            messagebox.showinfo("Success", "Login successful!")
            # Pass the user_email to HomePage
            self.root.destroy()  # Destroy the login window
            HomePage.main(user_email=email)  # Open the HomePage with user email
        else:
            messagebox.showerror("Error", f"Login failed for user with email: {email}. {result}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginSystem(root)
    root.mainloop()