import tkinter as tk
from tkinter import Label, Entry, Button, messagebox, ttk
from datetime import datetime

from controllers.return_controller import ReturnController
from ui.components import HeaderFrame, ContentFrame, NavButton
from ui.themes import COLORS, FONTS, apply_frame_style
from models.loan import LoanModel

class ReturnForm:
    def __init__(self, parent, user_name, ashima_id):
        """
        Initialize the Return Form UI
        
        Args:
            parent: Parent widget
            user_name: Logged in user's name
            ashima_id: Logged in user's Ashima ID
        """
        self.parent = parent
        self.controller = ReturnController()
        self.user_name = user_name
        self.ashima_id = ashima_id
        
        # Create main frame
        self.frame = tk.Frame(parent, background=COLORS["primary"], 
                             highlightbackground=COLORS["bezel"], highlightthickness=2)
        self.frame.pack(side="right", anchor="n", fill="both", expand=True)
        
        # Create the form UI
        self.create_search_panel()
        self.create_content_panel()
        
        # Load initial data
        self.update_treeview()
    
    def create_search_panel(self):
        """Create the search panel with filters and controls"""
        midframe = tk.Frame(self.frame, background=COLORS["primary"])
        midframe.pack(side="top", anchor="n", fill="x", padx=20)
        
        # Search bar
        Label(midframe, text="Search:", font=FONTS["label"], 
              bg=COLORS["primary"], fg=COLORS["text_light"]).grid(row=1, column=0, sticky="nw", pady=10)
        
        self.search_entry = Entry(midframe, font=FONTS["entry"])
        self.search_entry.grid(row=2, column=0, columnspan=2, sticky="nw")
        self.search_entry.focus()
        self.search_entry.bind("<KeyRelease>", self.filter_treeview)
        
        # Received by field
        Label(midframe, text="ReceivedBy*", font=FONTS["label"], 
              bg=COLORS["primary"], fg=COLORS["text_light"]).grid(row=1, column=1, sticky="nw", padx=200, pady=10)
        
        self.received_entry = Entry(midframe, font=FONTS["entry"])
        self.received_entry.grid(row=2, column=1, sticky="nw", columnspan=3, padx=200)
        
        if self.user_name:
            self.received_entry.insert(0, self.user_name)
        
        # Export buttons
        export_all_button = Button(midframe, text="Export All", command=self.export_all_to_csv, 
                                bg=COLORS["primary"], fg=COLORS["text_light"], font=FONTS["button"])
        export_all_button.grid(row=2, column=3, sticky="nw", padx=(300,0))

        export_button = Button(midframe, text='Export Selected', bg=COLORS["primary"], 
                            fg=COLORS["text_light"], command=self.export_to_csv, font=FONTS["button"])
        export_button.grid(row=2, column=4, sticky="nw")
    
    def create_content_panel(self):
        """Create the table content panel"""
        # Use the ContentFrame component
        content = ContentFrame(self.frame, "Loaned Headsets")
        
        # Get database statistics
        issued_amount, returned_amount = self.controller.get_issued_returned_counts()
        
        # Add statistics labels
        Remaining = Label(content.get_content_frame(), text=f"Remaining: {returned_amount}", 
                         font=FONTS["label"], bg=COLORS["secondary"], fg=COLORS["text_light"])
        Remaining.grid(row=1, column=2, padx=(250,20))
        
        Issued = Label(content.get_content_frame(), text=f"Issued: {issued_amount}", 
                      font=FONTS["label"], bg=COLORS["secondary"], fg=COLORS["text_light"])
        Issued.grid(row=1, column=3, padx=20, sticky="e")
        
        # Create table frame
        tableframe = tk.Frame(content.get_bezel_frame(), background=COLORS["secondary"])
        tableframe.pack(side="top", anchor="n", fill="both", expand=True, pady=10, padx=10)
        
        # Create the treeview for displaying records
        columns = ('Date Issued', 'AshimaID', 'Issued To', 'Campaign', 
                  'Room Number', 'Asset Tag', 'Issued By', 'Status')
        
        self.tree = ttk.Treeview(tableframe, columns=columns, show='headings')
        
        # Define column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160)
        
        self.tree.pack(side="top", fill="both", expand=True)
        
        # Add a scrollbar
        scrollbar = tk.Scrollbar(tableframe, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click event for returning items
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Handle column width adjustment on window resize
        tableframe.bind("<Configure>", self.update_column_widths)
    
    def update_column_widths(self, event):
        """Adjust column widths when window is resized"""
        frame_width = event.width
        column_width = frame_width // 8

        # Update column widths for each column in the Treeview
        for col in range(8):
            self.tree.column(f"#{col+1}", width=column_width)
    
    def update_treeview(self):
        """Refresh the data in the treeview"""
        self.tree.delete(*self.tree.get_children())
        
        # Fetch latest records from the database
        records = self.controller.fetch_loan_records()
        
        # Insert fetched records into the treeview
        for record in records:
            values_to_display = (
                record[0],  # DateIssued
                record[1],  # AshimaID
                record[2],  # Issued To (Name)
                record[3],  # Campaign
                record[4],  # Room Number
                record[5],  # Asset Tag
                record[6],  # Issued By
                record[7]   # Status
            )
            self.tree.insert('', 'end', values=values_to_display)
    
    def filter_treeview(self, event=None):
        """Filter the treeview records based on search text"""
        search_term = self.search_entry.get().strip().lower()
        self.tree.delete(*self.tree.get_children())

        # Fetch all loan records from the database
        records = self.controller.fetch_loan_records()

        # If the search term is blank, display all records
        if not search_term:
            filtered_records = records
        else:
            # Filter records based on the search term in multiple columns
            filtered_records = []
            for record in records:
                if any(search_term in str(field).lower() for field in record):
                    filtered_records.append(record)

        # Insert filtered records into the Treeview
        for record in filtered_records:
            values_to_display = (
                record[0],  # DateIssued
                record[1],  # AshimaID
                record[2],  # Issued To (Name)
                record[3],  # Campaign
                record[4],  # Room Number
                record[5],  # Asset Tag
                record[6],  # Issued By
                record[7]   # Status
            )
            self.tree.insert('', 'end', values=values_to_display)
    
    def on_double_click(self, event):
        """Handle double-click on a row to return a headset"""
        item = self.tree.selection()[0]  # Get selected item
        item_values = self.tree.item(item, "values")
        
        if item_values:
            asset_tag = item_values[5]
            ashima_id = item_values[1]
            
            if asset_tag:
                received_by = self.received_entry.get()
                self.check_and_process_return(asset_tag, received_by, ashima_id)
            else:
                messagebox.showerror("Error", "Asset Tag not found in selected row.")
    
    def check_and_process_return(self, asset_tag, received_by, ashima_id):
        """Verify and process a headset return"""
        # Validate received_by field
        if not received_by.strip():
            messagebox.showinfo("Error", "Please Fill Out ReceivedBy!")
            return
        
        # Check if asset exists and confirm return
        asset_exists = self.controller.check_asset_exists(asset_tag)
        
        if asset_exists:
            confirm_return = messagebox.askyesno(
                "Confirm Return", 
                f"Return asset with tag: {asset_tag}?"
            )
            
            if confirm_return:
                success = self.controller.process_return(
                    asset_tag, 
                    received_by, 
                    ashima_id, 
                    self.ashima_id, 
                    self.user_name
                )
                
                if success:
                    messagebox.showinfo("Success", "Asset returned successfully!")
                    self.search_entry.delete(0, 'end')
                    self.update_treeview()
                else:
                    messagebox.showerror("Error", "Failed to process return. Please try again.")
        else:
            messagebox.showerror(
                "Asset Not Found", 
                f"Asset with tag '{asset_tag}' not found in loan records."
            )
    
    def export_to_csv(self):
        """Export selected rows to CSV file"""
        selected_items = self.tree.selection()
        if selected_items:
            filename = self.controller.export_selected_to_csv(
                [self.tree.item(item, 'values') for item in selected_items]
            )
            if filename:
                messagebox.showinfo('Success', 'CSV file exported successfully.')
        else:
            messagebox.showwarning('No Selection', 'Please select items to export.')
    
    def export_all_to_csv(self):
        """Export all displayed rows to CSV file"""
        all_items = [self.tree.item(item, 'values') for item in self.tree.get_children()]
        filename = self.controller.export_all_to_csv(all_items)
        if filename:
            messagebox.showinfo('Success', 'All data exported to CSV successfully.')