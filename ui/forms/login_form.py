import tkinter as tk
from tkinter import Label, Entry, Button, messagebox
from controllers.user_controller import UserController
from ui.themes import COLORS, FONTS

def open_login_window(parent, on_login_success):
    """
    Open the login window
    
    Args:
        parent: Parent widget
        on_login_success: Callback function for successful login
    """
    LoginWindow = tk.Toplevel()
    LoginWindow.title("Login")
    LoginWindow.config(background=COLORS["primary"])
    LoginWindow.resizable(False, False)
    
    # Set window size and position
    window_width = 400
    window_height = 450
    screen_width = LoginWindow.winfo_screenwidth()
    screen_height = LoginWindow.winfo_screenheight()
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 3
    LoginWindow.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    
    controller = UserController()

    # Create custom title bar
    title_bar = tk.Frame(LoginWindow, bg=COLORS["primary"], relief='raised', bd=0)
    title_bar.pack(fill=tk.X)

    title_label = Button(title_bar, text="Sign Up", bg=COLORS["primary"], 
                       fg=COLORS["text_light"], command=lambda: open_signup_window(LoginWindow),
                       font=FONTS["button"])
    title_label.pack(side=tk.LEFT, padx=10, pady=5)

    # Make title bar draggable
    title_bar.bind('<Button-1>', lambda e: start_move(e, LoginWindow))
    title_bar.bind('<ButtonRelease-1>', lambda e: stop_move(e, LoginWindow))
    title_bar.bind('<B1-Motion>', lambda e: on_move(e, LoginWindow))

    # Welcome message
    Label(LoginWindow, text="Welcome!", bg=COLORS["primary"], 
         fg=COLORS["text_light"], font=FONTS["header"]).pack(padx=10, pady=5)
    
    Label(LoginWindow, text="Please Login \nto access \nLoaning and Returning Forms", 
         bg=COLORS["primary"], fg=COLORS["text_light"], 
         font=FONTS["label"]).pack(padx=10, pady=15)

    # Login fields
    Label(LoginWindow, text="AshimaID:", bg=COLORS["primary"], 
         fg=COLORS["text_light"], font=FONTS["label"]).pack(pady=5)
    
    ashima_entry = Entry(LoginWindow)
    ashima_entry.pack()
    ashima_entry.focus()

    Label(LoginWindow, text="Password:", bg=COLORS["primary"], 
         fg=COLORS["text_light"], font=FONTS["label"]).pack(pady=5)
    
    password_entry = Entry(LoginWindow, show="*")
    password_entry.pack(pady=(0,10))

    def check_credentials(event=None):
        """Validate user credentials and log in"""
        ashima = ashima_entry.get()
        password = password_entry.get()
        
        if ashima and password:
            user_info = controller.check_user_credentials(ashima, password)
            
            if user_info:
                privilege_level = user_info[4]
                if privilege_level in (2, 3):  # Admin or Supervisor
                    user_name = user_info[1]
                    LoginWindow.destroy()
                    on_login_success(user_name, ashima, privilege_level)
                    return user_info
                else:
                    messagebox.showerror("Access Denied", "Insufficient privileges.")
                    password_entry.delete(0, 'end')
                    password_entry.focus()
            else:
                messagebox.showerror("Log In Failed", "Invalid username or password.")
                password_entry.delete(0, 'end')
                password_entry.focus()
        else:
            messagebox.showerror("Empty Fields", "Please enter both username and password.")

    # Login buttons
    login_button = Button(LoginWindow, text="Log In", bg=COLORS["primary"], 
                        fg=COLORS["text_light"], command=check_credentials, font=FONTS["button"])
    login_button.place(relx=0.3, rely=0.9, anchor="center")

    cancel_button = Button(LoginWindow, text="Cancel", bg=COLORS["primary"], 
                         fg=COLORS["text_light"], command=lambda: cancel_login(LoginWindow, parent), 
                         font=FONTS["button"])
    cancel_button.place(relx=0.7, rely=0.9, anchor="center")

    # Bind Enter key to login button
    LoginWindow.bind('<Return>', check_credentials)

def open_signup_window(parent):
    """Open the sign-up window"""
    from utils.validation import on_validate, on_validatename, on_validatepass
    
    SignWindow = tk.Toplevel()
    SignWindow.title("Sign Up")
    SignWindow.config(background=COLORS["primary"])
    SignWindow.resizable(False, False)
    
    window_width = 300
    window_height = 200
    screen_width = SignWindow.winfo_screenwidth()
    screen_height = SignWindow.winfo_screenheight()
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 3
    SignWindow.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    
    controller = UserController()
    
    vcmd = (SignWindow.register(on_validate), '%P')
    vcmdname = (SignWindow.register(on_validatename), '%P')
    vcmdpass = (SignWindow.register(on_validatepass), '%P')

    # Create entry fields
    Label(SignWindow, text="AshimaID:", bg=COLORS["primary"], 
         fg=COLORS["text_light"]).pack()
    
    ashima_entry = Entry(SignWindow, validate="key", validatecommand=vcmd)
    ashima_entry.pack()
    
    Label(SignWindow, text="Username:", bg=COLORS["primary"], 
         fg=COLORS["text_light"]).pack()
    
    username_entry = Entry(SignWindow, validate="key", validatecommand=vcmdname)
    username_entry.pack()

    Label(SignWindow, text="Password:", bg=COLORS["primary"], 
         fg=COLORS["text_light"]).pack()
    
    password_entry = Entry(SignWindow, show="*", validate="key", validatecommand=vcmdpass)
    password_entry.pack()

    def submit():
        """Handle sign-up submission"""
        # Retrieve input values
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        ashima = ashima_entry.get().strip()
        
        if username and password and ashima:
            success = controller.create_new_user(username, ashima, password)
            if success:
                messagebox.showinfo("Success", "New User has been Created!", parent=SignWindow)
                SignWindow.destroy()
            else:
                messagebox.showerror("Error", "Failed to create new user.", parent=SignWindow)
        else:
            messagebox.showinfo("Error", "Please Fill Out All Entry Fields!", parent=SignWindow)
    
    # Submit button
    Button(SignWindow, text="Submit", bg=COLORS["primary"], fg=COLORS["text_light"], 
          command=submit).pack(pady=10)

# Window movement functions
def start_move(event, window):
    window.x = event.x
    window.y = event.y

def stop_move(event, window):
    window.x = None
    window.y = None

def on_move(event, window):
    deltax = event.x - window.x
    deltay = event.y - window.y
    x = window.winfo_x() + deltax
    y = window.winfo_y() + deltay
    window.geometry(f"+{x}+{y}")

def cancel_login(login_window, parent):
    """Cancel login and exit application"""
    login_window.destroy()
    parent.destroy()