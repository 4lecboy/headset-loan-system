import tkinter as tk
from tkinter import Label, Button
import threading
import schedule
import time
from PIL import ImageTk, Image
import io

from datetime import datetime
from tkinter import messagebox

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
        """Open a popup window to add a new headset to inventory"""
        # Create the popup window
        headset_window = tk.Toplevel(self.root)
        headset_window.title("Add New Headset")
        headset_window.geometry("450x250")
        headset_window.resizable(False, False)
        headset_window.configure(background="#172f66")
        
        # Make it modal
        headset_window.transient(self.root)
        headset_window.grab_set()
        
        # Center the window
        headset_window.update_idletasks()
        width = headset_window.winfo_width()
        height = headset_window.winfo_height()
        x = (headset_window.winfo_screenwidth() // 2) - (width // 2)
        y = (headset_window.winfo_screenheight() // 2) - (height // 2)
        headset_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Create form fields
        frame = tk.Frame(headset_window, bg="#172f66")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Asset Tag field
        Label(frame, text="Asset Tag ID:", font=("ANTON", 12, "bold"), 
            bg="#172f66", fg="#FFFFFF").grid(row=0, column=0, sticky="w", pady=10)
        
        from utils.validation import on_validateasset
        vcmd = (headset_window.register(on_validateasset), '%P')
        
        asset_entry = tk.Entry(frame, width=25, font=("Arial", 12), validate="key", validatecommand=vcmd)
        asset_entry.grid(row=0, column=1, sticky="w", pady=10)
        asset_entry.focus_set()
        
        # Description field (optional)
        Label(frame, text="Description:", font=("ANTON", 12, "bold"), 
            bg="#172f66", fg="#FFFFFF").grid(row=1, column=0, sticky="w", pady=10)
        
        desc_entry = tk.Entry(frame, width=25, font=("Arial", 12))
        desc_entry.grid(row=1, column=1, sticky="w", pady=10)
        
        # Button frame
        button_frame = tk.Frame(frame, bg="#172f66")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def save_headset():
            asset_tag = asset_entry.get().strip()
            description = desc_entry.get().strip()
            
            if not asset_tag:
                messagebox.showwarning("Input Error", "Asset Tag ID is required.", parent=headset_window)
                return
            
            # Save to database
            conn = connect_to_mysql()
            cursor = conn.cursor()
            try:
                # Check if asset tag already exists
                cursor.execute("SELECT COUNT(*) FROM storage_list WHERE AssetTagID = %s", (asset_tag,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Duplicate Error", 
                                        f"Asset Tag '{asset_tag}' already exists in the inventory.", 
                                        parent=headset_window)
                    return
                
                # Insert new headset
                cursor.execute(
                    "INSERT INTO storage_list (AssetTagID, Description, Flag) VALUES (%s, %s, 1)",
                    (asset_tag, description)
                )
                conn.commit()
                
                # Add log entry
                if self.user_name and self.ashima_id:
                    cursor.execute(
                        "INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)",
                        (self.ashima_id, self.user_name, "Added new headset", asset_tag, datetime.now())
                    )
                    conn.commit()
                
                # Success
                messagebox.showinfo("Success", f"Headset '{asset_tag}' added successfully.", parent=headset_window)
                headset_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to add headset: {str(e)}", parent=headset_window)
            finally:
                cursor.close()
                conn.close()
        
        # Save button
        save_btn = Button(button_frame, text="Save", command=save_headset,
                        bg="green", fg="#FFFFFF", font=("ANTON", 12, "bold"))
        save_btn.pack(side="left", padx=10)
        
        # Cancel button
        cancel_btn = Button(button_frame, text="Cancel", command=headset_window.destroy,
                        bg="red", fg="#FFFFFF", font=("ANTON", 12, "bold"))
        cancel_btn.pack(side="right", padx=10)
        
        # Bind keyboard shortcuts
        headset_window.bind("<Return>", lambda event: save_headset())
        headset_window.bind("<Escape>", lambda event: headset_window.destroy())

    def open_campaign_window(self):
        """Open a popup window to add a new campaign"""
        # Create the popup window
        campaign_window = tk.Toplevel(self.root)
        campaign_window.title("Add New Campaign")
        campaign_window.geometry("400x200")
        campaign_window.resizable(False, False)
        campaign_window.configure(background="#172f66")
        
        # Make it modal
        campaign_window.transient(self.root)
        campaign_window.grab_set()
        
        # Center the window
        campaign_window.update_idletasks()
        width = campaign_window.winfo_width()
        height = campaign_window.winfo_height()
        x = (campaign_window.winfo_screenwidth() // 2) - (width // 2)
        y = (campaign_window.winfo_screenheight() // 2) - (height // 2)
        campaign_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Create form fields
        frame = tk.Frame(campaign_window, bg="#172f66")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Campaign name field
        Label(frame, text="Campaign Name:", font=("ANTON", 12, "bold"), 
            bg="#172f66", fg="#FFFFFF").grid(row=0, column=0, sticky="w", pady=10)
        
        campaign_entry = tk.Entry(frame, width=25, font=("Arial", 12))
        campaign_entry.grid(row=0, column=1, sticky="w", pady=10)
        campaign_entry.focus_set()
        
        # Button frame
        button_frame = tk.Frame(frame, bg="#172f66")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def save_campaign():
            campaign_name = campaign_entry.get().strip()
            
            if not campaign_name:
                messagebox.showwarning("Input Error", "Campaign name is required.", parent=campaign_window)
                return
            
            # Save to database
            conn = connect_to_mysql()
            cursor = conn.cursor()
            try:
                # Check if campaign already exists
                cursor.execute("SELECT COUNT(*) FROM tblcampaign WHERE CampaignName = %s", (campaign_name,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Duplicate Error", 
                                        f"Campaign '{campaign_name}' already exists.", 
                                        parent=campaign_window)
                    return
                
                # Insert new campaign
                cursor.execute(
                    "INSERT INTO tblcampaign (CampaignName) VALUES (%s)",
                    (campaign_name,)
                )
                conn.commit()
                
                # Add log entry
                if self.user_name and self.ashima_id:
                    cursor.execute(
                        "INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)",
                        (self.ashima_id, self.user_name, "Added new campaign", campaign_name, datetime.now())
                    )
                    conn.commit()
                
                # Success
                messagebox.showinfo("Success", f"Campaign '{campaign_name}' added successfully.", parent=campaign_window)
                campaign_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to add campaign: {str(e)}", parent=campaign_window)
            finally:
                cursor.close()
                conn.close()
        
        # Save button
        save_btn = Button(button_frame, text="Save", command=save_campaign,
                        bg="green", fg="#FFFFFF", font=("ANTON", 12, "bold"))
        save_btn.pack(side="left", padx=10)
        
        # Cancel button
        cancel_btn = Button(button_frame, text="Cancel", command=campaign_window.destroy,
                        bg="red", fg="#FFFFFF", font=("ANTON", 12, "bold"))
        cancel_btn.pack(side="right", padx=10)
        
        # Bind keyboard shortcuts
        campaign_window.bind("<Return>", lambda event: save_campaign())
        campaign_window.bind("<Escape>", lambda event: campaign_window.destroy())

    def open_room_window(self):
        """Open a popup window to add a new room"""
        # Create the popup window
        room_window = tk.Toplevel(self.root)
        room_window.title("Add New Room")
        room_window.geometry("400x200")
        room_window.resizable(False, False)
        room_window.configure(background="#172f66")
        
        # Make it modal
        room_window.transient(self.root)
        room_window.grab_set()
        
        # Center the window
        room_window.update_idletasks()
        width = room_window.winfo_width()
        height = room_window.winfo_height()
        x = (room_window.winfo_screenwidth() // 2) - (width // 2)
        y = (room_window.winfo_screenheight() // 2) - (height // 2)
        room_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Create form fields
        frame = tk.Frame(room_window, bg="#172f66")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Room number field
        Label(frame, text="Room Number:", font=("ANTON", 12, "bold"), 
            bg="#172f66", fg="#FFFFFF").grid(row=0, column=0, sticky="w", pady=10)
        
        room_entry = tk.Entry(frame, width=25, font=("Arial", 12))
        room_entry.grid(row=0, column=1, sticky="w", pady=10)
        room_entry.focus_set()
        
        # Button frame
        button_frame = tk.Frame(frame, bg="#172f66")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def save_room():
            room_number = room_entry.get().strip()
            
            if not room_number:
                messagebox.showwarning("Input Error", "Room number is required.", parent=room_window)
                return
            
            # Save to database
            conn = connect_to_mysql()
            cursor = conn.cursor()
            try:
                # Check if room already exists
                cursor.execute("SELECT COUNT(*) FROM tblroom WHERE RoomNumber = %s", (room_number,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Duplicate Error", 
                                        f"Room '{room_number}' already exists.", 
                                        parent=room_window)
                    return
                
                # Insert new room
                cursor.execute(
                    "INSERT INTO tblroom (RoomNumber) VALUES (%s)",
                    (room_number,)
                )
                conn.commit()
                
                # Add log entry
                if self.user_name and self.ashima_id:
                    cursor.execute(
                        "INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)",
                        (self.ashima_id, self.user_name, "Added new room", room_number, datetime.now())
                    )
                    conn.commit()
                
                # Success
                messagebox.showinfo("Success", f"Room '{room_number}' added successfully.", parent=room_window)
                room_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to add room: {str(e)}", parent=room_window)
            finally:
                cursor.close()
                conn.close()
        
        # Save button
        save_btn = Button(button_frame, text="Save", command=save_room,
                        bg="green", fg="#FFFFFF", font=("ANTON", 12, "bold"))
        save_btn.pack(side="left", padx=10)
        
        # Cancel button
        cancel_btn = Button(button_frame, text="Cancel", command=room_window.destroy,
                        bg="red", fg="#FFFFFF", font=("ANTON", 12, "bold"))
        cancel_btn.pack(side="right", padx=10)
        
        # Bind keyboard shortcuts
        room_window.bind("<Return>", lambda event: save_room())
        room_window.bind("<Escape>", lambda event: room_window.destroy())
    
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