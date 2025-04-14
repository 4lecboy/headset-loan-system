import tkinter as tk
from tkinter import Label, Entry, StringVar, Button, OptionMenu, messagebox
from datetime import datetime

from controllers.loan_controller import LoanController
from ui.custom_widgets import AutocompleteEntry
from utils.validation import on_validate, on_validatename, on_validateasset

class LoanForm:
    def __init__(self, parent, user_name, ashima_id, open_loan_window, fetch_campaigns, 
                 fetch_rooms, fetch_asset_tags, open_headset_window,
                 open_campaign_window, open_room_window):
        self.parent = parent
        self.controller = LoanController()
        self.user_name = user_name
        self.ashima_id = ashima_id
        self.open_loan_window = open_loan_window
        self.fetch_campaigns = fetch_campaigns
        self.fetch_rooms = fetch_rooms
        self.fetch_asset_tags = fetch_asset_tags
        self.open_headset_window = open_headset_window
        self.open_campaign_window = open_campaign_window
        self.open_room_window = open_room_window
        
        self.frame = tk.Frame(parent, background="#172f66", 
                              highlightbackground="#CBCBCB", highlightthickness=2)
        self.frame.pack(side="right", anchor="n", fill="both", expand=True)
        
        self.create_form()
    
    def create_form(self):
        """Create the loan form UI"""
        centerframe = tk.Frame(self.frame, background="#172f66")
        centerframe.pack(side="left", anchor="n", fill="both", expand=True)
        
        # Date field
        Label(centerframe, text="Date*", font=("ANTON", 12, "bold"),
              bg="#172f66", fg="#FFFFFF").grid(row=2, column=1, padx=200, pady=(30,0), sticky='nw')
        
        self.date_entry = Entry(centerframe, font=15)
        self.date_entry.grid(row=3, column=1, columnspan=2, padx=200, pady=10, sticky='nw')
        self.update_current_date_time()
        
        # Ashima field
        Label(centerframe, text="Ashima Number*", font=("ANTON", 12, "bold"),
              bg="#172f66", fg="#FFFFFF").grid(row=2, column=3, padx=200, pady=(30,0), sticky='nw')
        
        vcmd = (centerframe.register(on_validate), '%P')
        emp_IDs = self.controller.user_model.fetch_empID()
        
        self.ashima_entry = AutocompleteEntry(centerframe, completevalues=emp_IDs,
                                           validate="key", validatecommand=vcmd, font=12)
        self.ashima_entry.grid(row=3, column=3, columnspan=3, padx=200, pady=10, sticky='nw')
        self.ashima_entry.bind("<KeyRelease>", 
                            lambda event: self.populate_employee_info())
        self.ashima_entry.focus()
        
        # Name fields
        Label(centerframe, text="Name*", font=("ANTON", 12, "bold"),
              bg="#172f66", fg="#FFFFFF").grid(row=4, column=1, padx=200, pady=(30,0), sticky='nw')
        
        vcmdname = (centerframe.register(on_validatename), '%P')
        
        self.name1_entry = Entry(centerframe, font=12)
        self.name1_entry.grid(row=5, column=1, columnspan=3, padx=200, pady=10, sticky='nw')
        
        self.name2_entry = Entry(centerframe, font=12)
        self.name2_entry.grid(row=5, column=3, columnspan=3, padx=200, pady=10, sticky='nw')
        
        Label(centerframe, text="First", font=("ANTON", 8, "bold"),
              bg="#172f66", fg="#d3d3d3").grid(row=6, column=1, padx=200, pady=(1,0), sticky='nw')
        
        Label(centerframe, text="Last", font=("ANTON", 8, "bold"),
              bg="#172f66", fg="#d3d3d3").grid(row=6, column=3, padx=200, pady=(1,0), sticky='nw')
        
        # Campaign field
        Label(centerframe, text="Campaign*", font=("ANTON", 12, "bold"),
              bg="#172f66", fg="#FFFFFF").grid(row=7, column=1, padx=200, pady=(30,0), sticky='nw')
        
        campaign_list = self.fetch_campaigns()
        
        self.campaign = StringVar()
        self.campaign.set("Select Campaign")
        
        campaign_entry = OptionMenu(centerframe, self.campaign, *campaign_list)
        campaign_entry.grid(row=8, column=1, columnspan=3, padx=(210,10), pady=10, ipadx=15, sticky='nw')
        
        campaign_add = Button(centerframe, text="+", command=self.open_campaign_window,
                           bg="#172f66", fg="#FFFFFF", font=("ANTON", 7, "bold"))
        campaign_add.grid(row=8, column=1, columnspan=2, padx=200, sticky='nw', pady=15, ipadx=5)
        
        # Room field
        Label(centerframe, text="Room Number*", font=("ANTON", 12, "bold"),
              bg="#172f66", fg="#FFFFFF").grid(row=7, column=3, padx=200, pady=(30,0), sticky='nw')
        
        rooms_list = self.fetch_rooms()
        
        self.room = StringVar()
        self.room.set("Select Room")
        
        room_entry = OptionMenu(centerframe, self.room, *rooms_list)
        room_entry.grid(row=8, column=3, columnspan=3, padx=215, ipadx=2, pady=10, sticky='nw')
        
        room_add = Button(centerframe, text="+", command=self.open_room_window,
                        bg="#172f66", fg="#FFFFFF", font=("ANTON", 7, "bold"))
        room_add.grid(row=8, column=3, columnspan=2, padx=200, sticky='nw', pady=15, ipadx=5)
        
        # Asset tag field
        Label(centerframe, text="Asset Tags*", font=("ANTON", 12, "bold"),
              bg="#172f66", fg="#FFFFFF").grid(row=9, column=1, padx=200, pady=(30, 0), sticky='nw')
        
        asset_tags_list = self.fetch_asset_tags()
        
        self.assettag = AutocompleteEntry(centerframe, completevalues=asset_tags_list, font=12)
        self.assettag.grid(row=10, column=1, padx=(225, 10), pady=5, sticky='nw')
        
        bulk_loan_button = Button(centerframe, text="Bulk Loan",
                                command=lambda: self.open_bulk_loan_window(),
                                bg="#172f66", fg="#FFFFFF", font=("ANTON", 10, "bold"))
        bulk_loan_button.grid(row=10, column=1, padx=(415, 0), pady=5, sticky='nw')
        
        asset_add = Button(centerframe, text="+", command=self.open_headset_window,
                         bg="#172f66", fg="#FFFFFF", font=("ANTON", 7, "bold"))
        asset_add.grid(row=10, column=1, padx=(200,200), sticky='nw', ipadx=5)
        
        # Issued by field
        Label(centerframe, text="Issued By*", font=("ANTON", 12, "bold"),
              bg="#172f66", fg="#FFFFFF").grid(row=9, column=3, padx=200, pady=(30,0), sticky='nw')
        
        self.issuedby_entry = Entry(centerframe, validate="key", validatecommand=vcmdname, font=12)
        self.issuedby_entry.grid(row=10, column=3, columnspan=3, padx=200, sticky='nw')
        
        if self.user_name:
            self.issuedby_entry.insert(0, self.user_name)
        
        # Submit button
        submit_button = Button(centerframe, text="Submit", command=self.submit_loan_form,
                            bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
        submit_button.grid(row=11, column=2, columnspan=2, pady=30, sticky='nw')

    def update_current_date_time(self):
        """Update the date entry with current date and time"""
        now = datetime.now()
        current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, current_date_time)
        self.frame.after(1000, self.update_current_date_time)

    def populate_employee_info(self):
        """Populate employee info when Ashima ID is entered"""
        ashima_id = self.ashima_entry.get().strip()
        if ashima_id:
            employee_info = self.controller.user_model.fetch_emp(ashima_id)
            if employee_info:
                self.name1_entry.delete(0, tk.END)
                self.name1_entry.insert(0, employee_info['FirstName'])
                
                self.name2_entry.delete(0, tk.END)
                self.name2_entry.insert(0, employee_info['LastName'])
                
                self.campaign.set(employee_info['Campaign'])
            else:
                self.name1_entry.delete(0, tk.END)
                self.name2_entry.delete(0, tk.END)
                self.campaign.set("Select Campaign")
        else:
            self.name1_entry.delete(0, tk.END)
            self.name2_entry.delete(0, tk.END)
            self.campaign.set("Select Campaign")
    
    def open_bulk_loan_window(self):
        """Open window to enter multiple asset tags"""
        bulk_window = tk.Toplevel(self.parent)
        bulk_window.title("Bulk Loan - Enter Asset Tags")
        bulk_window.geometry("400x800")
        bulk_window.config(bg="#172f66")

        asset_entries = []  
        asset_tags_list = self.fetch_asset_tags()  

        def submit_bulk_loan():
            asset_tags = [entry.get().strip() for entry in asset_entries if entry.get().strip()]
            if not asset_tags:
                messagebox.showerror("Error", "Please enter at least one Asset Tag!", parent=bulk_window)
                return

            self.assettag.delete(0, tk.END)
            self.assettag.insert(0, ", ".join(asset_tags))  

            bulk_window.destroy()

        for i in range(10):
            label = Label(bulk_window, text=f"Asset Tag {i+1}:", bg="#172f66", fg="white", font=("Arial", 10, "bold"))
            label.pack(pady=(5, 0))

            entry = AutocompleteEntry(bulk_window, completevalues=asset_tags_list, font=("Arial", 10))
            entry.pack(pady=(0, 5), padx=20, fill="x")
            asset_entries.append(entry)

        submit_button = Button(bulk_window, text="Submit", command=submit_bulk_loan, bg="green", fg="white", font=("Arial", 12, "bold"))
        submit_button.pack(pady=20)
    
    def submit_loan_form(self):
        """Process the loan form submission"""
        date_issued = self.date_entry.get()
        ashima_id = self.ashima_entry.get()
        first_name = self.name1_entry.get()
        last_name = self.name2_entry.get()
        campaign = self.campaign.get()
        room_number = self.room.get()
        asset_tags = [tag.strip() for tag in self.assettag.get().split(",")]
        issued_by = self.issuedby_entry.get()
        
        success, message = self.controller.submit_loan(
            date_issued, ashima_id, first_name, last_name, 
            campaign, room_number, asset_tags, issued_by
        )
        
        if success:
            messagebox.showinfo("Success", message, parent=self.parent)
            self.open_loan_window()
        else:
            messagebox.showerror("Error", message, parent=self.parent)