import tkinter as tk
from tkinter import Label, Entry, Button, Frame, LabelFrame, messagebox, ttk

from controllers.deletion_controller import DeletionController
from ui.components import ContentFrame
from ui.themes import COLORS, FONTS

class DeletionForm:
    """
    Form for safely deleting records from the database
    """
    def __init__(self, parent, user_name=None, ashima_id=None):
        """
        Initialize the deletion form
        
        Args:
            parent: Parent widget
            user_name: Current user's name for logging
            ashima_id: Current user's Ashima ID for logging
        """
        self.parent = parent
        self.user_name = user_name
        self.ashima_id = ashima_id
        self.controller = DeletionController(user_name, ashima_id)
        
        # Create main frame
        self.frame = tk.Frame(parent, background=COLORS["primary"], 
                             highlightbackground=COLORS["bezel"], highlightthickness=2)
        self.frame.pack(side="right", anchor="n", fill="both", expand=True)
        
        # Create UI components
        self.create_search_panel()
        self.create_content_panel()
        
        # Initial data load
        self.fetch_and_populate_data()
    
    def create_search_panel(self):
        """Create the search panel with controls"""
        search_frame = tk.Frame(self.frame, background=COLORS["primary"])
        search_frame.pack(side="top", anchor="n", fill="x", padx=20, pady=10)
        
        # Search field
        Label(search_frame, text="Search:", font=FONTS["label"], 
              bg=COLORS["primary"], fg=COLORS["text_light"]).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.search_entry = Entry(search_frame, font=FONTS["entry"], width=30)
        self.search_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_records)
        
        # Search button
        search_button = Button(search_frame, text="Search", 
                              command=self.search_records,
                              bg=COLORS["primary"], fg=COLORS["text_light"],
                              font=FONTS["button"])
        search_button.grid(row=0, column=2, sticky="w", pady=5, padx=5)
        
        # Refresh button
        refresh_button = Button(search_frame, text="Refresh Data", 
                              command=self.fetch_and_populate_data,
                              bg=COLORS["primary"], fg=COLORS["text_light"],
                              font=FONTS["button"])
        refresh_button.grid(row=0, column=3, sticky="w", pady=5, padx=20)
    
    def create_content_panel(self):
        """Create the content panel with tables for different record types"""
        # Use ContentFrame component
        content = ContentFrame(self.frame, "Record Deletion")
        
        # Use a notebook to organize different record types
        self.notebook = ttk.Notebook(content.get_bezel_frame())
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Admin Users Tab
        self.admin_tab = Frame(self.notebook, bg=COLORS["background"])
        self.notebook.add(self.admin_tab, text="Admin Users")
        self.setup_table_for_tab(self.admin_tab, "Admin Users", 
                                ["Ashima ID", "Name"], 
                                "admin_login", "AshimaID")
        
        # Employees Tab
        self.employee_tab = Frame(self.notebook, bg=COLORS["background"])
        self.notebook.add(self.employee_tab, text="Employees")
        self.setup_table_for_tab(self.employee_tab, "Employees", 
                                ["Ashima ID", "First Name"], 
                                "empinfo", "AshimaID")
        
        # Campaigns Tab
        self.campaign_tab = Frame(self.notebook, bg=COLORS["background"])
        self.notebook.add(self.campaign_tab, text="Campaigns")
        self.setup_table_for_tab(self.campaign_tab, "Campaigns", 
                                ["Campaign Name", "ID"], 
                                "tblcampaign", "CampaignName")
        
        # Rooms Tab
        self.room_tab = Frame(self.notebook, bg=COLORS["background"])
        self.notebook.add(self.room_tab, text="Rooms")
        self.setup_table_for_tab(self.room_tab, "Rooms", 
                                ["Room Number", "ID"], 
                                "tblroom", "RoomNumber")
        
        # Headsets Tab
        self.headset_tab = Frame(self.notebook, bg=COLORS["background"])
        self.notebook.add(self.headset_tab, text="Headsets")
        self.setup_table_for_tab(self.headset_tab, "Headsets", 
                                ["Asset Tag ID", "Description"], 
                                "storage_list", "AssetTagID")
    
    def setup_table_for_tab(self, tab, title, columns, table_name, id_column):
        """
        Set up a table with delete functionality for a specific tab
        
        Args:
            tab: The tab frame to add the table to
            title: Title for the table section
            columns: List of column names
            table_name: Database table name
            id_column: Name of the ID column in the table
        """
        # Store table info for later use
        tab.table_info = {
            "table_name": table_name,
            "id_column": id_column
        }
        
        # Create a label frame for the table
        table_frame = LabelFrame(tab, text=title, bg=COLORS["background"], font=FONTS["label"])
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create treeview for the table
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        tab.tree = tree  # Store reference to tree for later use
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create button frame
        button_frame = Frame(tab, bg=COLORS["background"])
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Add delete button
        delete_button = Button(button_frame, text="Delete Selected Record", 
                              command=lambda: self.delete_record(tab),
                              bg=COLORS["error"], fg=COLORS["text_light"],
                              font=FONTS["button"])
        delete_button.pack(side="right", padx=10)
    
    def fetch_and_populate_data(self):
        """Fetch data from database and populate all tables"""
        try:
            # Get data from controller
            data = self.controller.fetch_table_data()
            
            # Populate each table
            self.populate_table(self.admin_tab.tree, data['userinfo'])
            self.populate_table(self.employee_tab.tree, data['empinfo'])
            self.populate_table(self.campaign_tab.tree, data['campaigns'])
            self.populate_table(self.room_tab.tree, data['rooms'])
            self.populate_table(self.headset_tab.tree, data['headsets'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {str(e)}", parent=self.parent)
    
    def populate_table(self, tree, data):
        """
        Populate a treeview with data
        
        Args:
            tree: Treeview to populate
            data: List of tuples containing row data
        """
        # Clear existing rows
        tree.delete(*tree.get_children())
        
        # Add new rows
        for row in data:
            tree.insert('', 'end', values=row)
    
    def search_records(self, event=None):
        """
        Search for records matching the search term
        
        Args:
            event: Key event (optional)
        """
        search_term = self.search_entry.get().strip()
        
        try:
            # Get filtered data from controller
            data = self.controller.search_records(search_term)
            
            # Populate each table with filtered data
            self.populate_table(self.admin_tab.tree, data['userinfo'])
            self.populate_table(self.employee_tab.tree, data['empinfo'])
            self.populate_table(self.campaign_tab.tree, data['campaigns'])
            self.populate_table(self.room_tab.tree, data['rooms'])
            self.populate_table(self.headset_tab.tree, data['headsets'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}", parent=self.parent)
    
    def delete_record(self, tab):
        """
        Delete the selected record from the table
        
        Args:
            tab: Tab containing the treeview
        """
        # Get the selected item
        selected_items = tab.tree.selection()
        
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a record to delete.", parent=self.parent)
            return
        
        # Get the first selected item
        selected_item = selected_items[0]
        
        # Get the values for the selected item
        values = tab.tree.item(selected_item, "values")
        
        if not values:
            return
        
        # Get the record ID (first value)
        record_id = values[0]
        
        # Get table info from the tab
        table_name = tab.table_info["table_name"]
        id_column = tab.table_info["id_column"]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete {record_id}?\n\nThis action cannot be undone.",
            parent=self.parent
        )
        
        if confirm:
            try:
                # Attempt to delete the record
                success = self.controller.delete_record(table_name, record_id, id_column)
                
                if success:
                    # Remove the item from the treeview
                    tab.tree.delete(selected_item)
                    messagebox.showinfo("Success", f"Record deleted successfully.", parent=self.parent)
                else:
                    messagebox.showerror("Error", "Failed to delete record. It may be referenced by other records.", parent=self.parent)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete record: {str(e)}", parent=self.parent)

    def safely_check_delete_dependencies(self, table_name, record_id):
        """
        Check if record can be safely deleted (not referenced elsewhere)
        
        Args:
            table_name: Table containing the record
            record_id: ID of the record to delete
            
        Returns:
            tuple: (can_delete, message)
        """
        # This is a placeholder for a more complex implementation
        # In a real system, you would check for foreign key constraints
        
        if table_name == "admin_login":
            # Don't allow deletion of the current user
            if str(record_id) == str(self.ashima_id):
                return False, "You cannot delete your own account."
                
        # For headsets, check if they're currently issued
        elif table_name == "storage_list":
            # Code to check if headset is currently issued
            pass
            
        return True, ""