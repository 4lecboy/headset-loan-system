import tkinter as tk
from tkinter import Label, Button
import threading
import schedule
import time
from PIL import ImageTk, Image
import io
from datetime import datetime

from config.database import connect_to_mysql
from ui.forms.loan_form import LoanForm
from ui.forms.return_form import ReturnForm
from ui.forms.statistics_form import StatisticsForm
from ui.forms.deletion_form import DeletionForm
from ui.forms.logs_form import LogsForm
from ui.forms.login_form import open_login_window
from utils.email_sender import send_scheduled_email
from models.image import get_image_from_db

class HeadsetLoanSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Headset Loaning System")
        self.root.config(background="#E0E1E1")
        
        # Set window size and position
        window_width = 1200
        window_height = 960
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 3
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        
        # Initialize frames
        self.current_frame = None
        self.user_name = None
        self.ashima_id = None
        
        # Set up background and UI
        self.setup_background()
        self.setup_ui_frames()
        
        # Start in hidden state, show login first
        self.root.state('withdrawn')
        open_login_window(self.root, self.on_login_success)
        
        # Set up scheduler
        self.exit_event = threading.Event()
        self.schedule_thread = threading.Thread(target=self.run_schedule, daemon=True)
        self.schedule_thread.start()
        
        # Handle application closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_background(self):
        # Load and set up background image
        image_id = 2
        logo_data, logo_image = get_image_from_db(image_id)
        if logo_data and logo_image:
            img_width, img_height = logo_image.size
            window_width, window_height = 1200, 1200
            scale = max(window_width / img_width, window_height / img_height)
            img = logo_image.resize((int(img_width * scale), int(img_height * scale)))
            self.background_image = ImageTk.PhotoImage(img)
            
            background_label = tk.Label(self.root, image=self.background_image)
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Set up logo
            logosize = logo_image.resize((500, 200))
            self.logo = ImageTk.PhotoImage(logosize)
    
    def setup_ui_frames(self):
        # Create top frame for header and navigation
        self.top_frame = tk.Frame(self.root, background="#172f66")
        self.top_frame.pack(side=tk.TOP, anchor=tk.N, fill=tk.X)
        
        self.side_frame = tk.Frame(self.root, background="#172f66")
        self.side_frame.pack(side=tk.TOP, anchor=tk.N, fill=tk.X)
        
        # Create home button with logo
        self.home_button = Button(self.top_frame, image=self.logo, 
                                 command=self.open_return_window, 
                                 relief=tk.FLAT, bg="#172f66")
        self.home_button.pack(side="left", anchor="nw")
        
        # Create username display that also acts as logout button
        self.username_button = Button(self.top_frame, text="", 
                                     bg="#172f66", fg="#FFFFFF", 
                                     command=self.logout, relief=tk.FLAT, 
                                     state='disabled', font=("ANTON", 15, "bold"))
        self.username_button.pack(side="right", anchor="ne", pady=30)
        
        # Create navigation buttons
        self.loan_button = Button(self.side_frame, text="Headset Loan Form", 
                                 command=self.open_loan_window, relief=tk.RAISED, 
                                 bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
        
        self.statistics_button = Button(self.side_frame, text="Statistics", 
                                      command=self.open_statistics_window, relief=tk.RAISED, 
                                      bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
        
        self.deletion_button = Button(self.side_frame, text="Deletion", 
                                    command=self.open_deletion_window, relief=tk.RAISED, 
                                    bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
        
        self.logs_button = Button(self.side_frame, text="Logs", 
                               command=self.open_logs_window, relief=tk.RAISED, 
                               bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
    
    def destroy_current_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
    
    def on_login_success(self, username, ashima_id, privilege):
        self.user_name = username
        self.ashima_id = ashima_id
        self.root.state('normal')
        self.root.lift()
        self.root.focus_force()
        
        # Update username display
        self.username_button.config(state='normal', text=f"Welcome, {username}")
        
        # Configure navigation based on privilege
        if privilege == 3:  # Admin
            self.setup_admin_navigation()
        elif privilege == 2:  # Supervisor
            self.setup_supervisor_navigation()
        
        # Open default view
        self.open_return_window()
    
    def setup_admin_navigation(self):
        # Reset existing buttons
        for widget in self.side_frame.winfo_children():
            widget.destroy()
        
        # Add buttons for admin
        self.loan_button = Button(self.side_frame, text="Headset Loan Form", 
                                command=self.open_loan_window, relief=tk.RAISED, 
                                bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
        self.loan_button.pack(side="left", anchor="n")
        
        self.statistics_button = Button(self.side_frame, text="Statistics", 
                                     command=self.open_statistics_window, relief=tk.RAISED, 
                                     bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
        self.statistics_button.pack(side="left", anchor="n")
        
        self.deletion_button = Button(self.side_frame, text="Deletion", 
                                   command=self.open_deletion_window, relief=tk.RAISED, 
                                   bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
        self.deletion_button.pack(side="left", anchor="n")
        
        self.logs_button = Button(self.side_frame, text="Logs", 
                              command=self.open_logs_window, relief=tk.RAISED, 
                              bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
        self.logs_button.pack(side="left", anchor="n")
    
    def setup_supervisor_navigation(self):
        # Reset existing buttons
        for widget in self.side_frame.winfo_children():
            widget.destroy()
        
        # Add buttons for supervisor (more limited)
        self.loan_button = Button(self.side_frame, text="Headset Loan Form", 
                                command=self.open_loan_window, relief=tk.RAISED, 
                                bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
        self.loan_button.pack(side="left", anchor="n")
    
    def open_loan_window(self):
        self.destroy_current_frame()
        self.loan_button.config(state='disabled')
        self.statistics_button.config(state='normal')
        self.deletion_button.config(state='normal')
        self.logs_button.config(state='normal')
        
        self.current_frame = LoanForm(
            self.root, 
            self.user_name, 
            self.ashima_id,
            self.open_loan_window,
            self.fetch_campaigns,
            self.fetch_rooms,
            self.fetch_asset_tags,
            self.open_headset_window,
            self.open_campaign_window,
            self.open_room_window
        ).frame
    
    def open_return_window(self):
        self.destroy_current_frame()
        self.loan_button.config(state='normal')
        self.statistics_button.config(state='normal')
        self.deletion_button.config(state='normal')
        self.logs_button.config(state='normal')
        
        self.current_frame = ReturnForm(
            self.root,
            self.user_name,
            self.ashima_id
        ).frame
    
    def open_statistics_window(self):
        self.destroy_current_frame()
        self.loan_button.config(state='normal')
        self.statistics_button.config(state='disabled')
        self.deletion_button.config(state='normal')
        self.logs_button.config(state='normal')
        
        self.current_frame = StatisticsForm(self.root).frame
    
    def open_deletion_window(self):
        self.destroy_current_frame()
        self.loan_button.config(state='normal')
        self.statistics_button.config(state='normal')
        self.deletion_button.config(state='disabled')
        self.logs_button.config(state='normal')
        
        self.current_frame = DeletionForm(self.root, self.user_name, self.ashima_id).frame
    
    def open_logs_window(self):
        self.destroy_current_frame()
        self.loan_button.config(state='normal')
        self.statistics_button.config(state='normal')
        self.deletion_button.config(state='normal')
        self.logs_button.config(state='disabled')
        
        self.current_frame = LogsForm(self.root).frame
    
    def open_headset_window(self):
        # Implement this method to open headset window
        pass
    
    def open_campaign_window(self):
        # Implement this method to open campaign window
        pass
    
    def open_room_window(self):
        # Implement this method to open room window
        pass
    
    def fetch_campaigns(self):
        # Implement method to fetch campaigns
        conn = connect_to_mysql()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT CampaignName FROM tblcampaign")
            records = cursor.fetchall()
            return [record[0] for record in records]
        finally:
            cursor.close()
            conn.close()
    
    def fetch_rooms(self):
        # Implement method to fetch rooms
        conn = connect_to_mysql()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT RoomNumber FROM tblroom")
            records = cursor.fetchall()
            return [record[0] for record in records]
        finally:
            cursor.close()
            conn.close()
    
    def fetch_asset_tags(self):
        # Implement method to fetch asset tags
        conn = connect_to_mysql()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT AssetTagID FROM storage_list WHERE Flag = 1")
            records = cursor.fetchall()
            return [record[0] for record in records]
        finally:
            cursor.close()
            conn.close()
    
    def logout(self):
        from tkinter import messagebox
        confirmed = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if confirmed:
            self.username_button.config(text="", state='disabled')
            self.destroy_current_frame()
            self.root.state('withdrawn')
            open_login_window(self.root, self.on_login_success)
    
    def run_schedule(self):
        schedule.every().day.at("16:00").do(send_scheduled_email)
        while not self.exit_event.is_set():
            schedule.run_pending()
            time.sleep(2)
    
    def on_closing(self):
        self.exit_event.set()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HeadsetLoanSystem(root)
    root.mainloop()