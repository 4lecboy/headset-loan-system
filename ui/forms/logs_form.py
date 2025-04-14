import tkinter as tk
from tkinter import Label, Entry, Button, messagebox, ttk
import csv
from tkinter import filedialog

from controllers.logs_controller import LogsController
from ui.components import ContentFrame
from ui.themes import COLORS, FONTS

class LogsForm:
    """
    Form for displaying and interacting with system logs
    """
    def __init__(self, parent):
        """
        Initialize the logs form
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.controller = LogsController()
        
        # Create main frame
        self.frame = tk.Frame(parent, background=COLORS["primary"], 
                             highlightbackground=COLORS["bezel"], highlightthickness=2)
        self.frame.pack(side="right", anchor="n", fill="both", expand=True)
        
        # Create the UI components
        self.create_search_panel()
        self.create_content_panel()
        
        # Load initial data
        self.update_logs_display()
    
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
        self.search_entry.bind("<KeyRelease>", self.filter_logs)
        
        # Export buttons
        export_all_button = Button(midframe, text="Export All", 
                                  command=self.export_all_to_csv, 
                                  bg=COLORS["primary"], fg=COLORS["text_light"], 
                                  font=FONTS["button"])
        export_all_button.grid(row=2, column=3, sticky="nw", padx=(300,0))

        export_button = Button(midframe, text='Export Selected', 
                             bg=COLORS["primary"], fg=COLORS["text_light"], 
                             command=self.export_selected_to_csv, 
                             font=FONTS["button"])
        export_button.grid(row=2, column=4, sticky="nw")
    
    def create_content_panel(self):
        """Create the main content panel with logs table"""
        # Use the ContentFrame component
        content = ContentFrame(self.frame, "Action Logs")
        
        # Create table frame
        tableframe = tk.Frame(content.get_bezel_frame(), background=COLORS["secondary"])
        tableframe.pack(side="top", anchor="n", fill="both", expand=True, pady=10, padx=10)
        
        # Create the treeview for displaying logs
        columns = ('AshimaID', 'Name', 'Performed', 'Item', 'Date')
        
        self.tree = ttk.Treeview(tableframe, columns=columns, show='headings')
        
        # Define column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        
        self.tree.pack(side="top", fill="both", expand=True)
        
        # Add a scrollbar
        scrollbar = tk.Scrollbar(tableframe, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Handle column width adjustment on window resize
        tableframe.bind("<Configure>", self.update_column_widths)
    
    def update_column_widths(self, event):
        """Adjust column widths when window is resized"""
        frame_width = event.width
        column_width = frame_width // 5  # 5 columns

        # Update column widths for each column in the Treeview
        for col in range(5):
            self.tree.column(f"#{col+1}", width=column_width)
    
    def update_logs_display(self):
        """Refresh the logs in the treeview"""
        self.tree.delete(*self.tree.get_children())
        
        # Fetch latest logs from the database
        logs = self.controller.fetch_logs()
        
        # Insert logs into the treeview
        for log in logs:
            values_to_display = (
                log[0],  # AshimaID
                log[1],  # Name
                log[2],  # Performed
                log[3],  # Item
                log[4]   # Date
            )
            self.tree.insert('', 'end', values=values_to_display)
    
    def filter_logs(self, event=None):
        """Filter logs based on search text"""
        search_term = self.search_entry.get().strip().lower()
        self.tree.delete(*self.tree.get_children())

        # Get logs from controller
        logs = self.controller.search_logs(search_term)
        
        # Insert filtered logs into the Treeview
        for log in logs:
            values_to_display = (
                log[0],  # AshimaID
                log[1],  # Name
                log[2],  # Performed
                log[3],  # Item
                log[4]   # Date
            )
            self.tree.insert('', 'end', values=values_to_display)
    
    def export_selected_to_csv(self):
        """Export selected logs to CSV file"""
        selected_items = self.tree.selection()
        if selected_items:
            # Get the selected logs data
            selected_logs = []
            for item in selected_items:
                values = self.tree.item(item, 'values')
                selected_logs.append(values)
            
            # Export to CSV via controller
            file_path = self.controller.export_logs_to_csv(selected_logs)
            
            if file_path:
                messagebox.showinfo('Success', 'CSV file exported successfully.', parent=self.parent)
        else:
            messagebox.showwarning('No Selection', 'Please select items to export.', parent=self.parent)
    
    def export_all_to_csv(self):
        """Export all displayed logs to CSV file"""
        # Get all the logs data currently displayed
        all_logs = []
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            all_logs.append(values)
        
        # Export to CSV via controller
        file_path = self.controller.export_logs_to_csv(all_logs)
        
        if file_path:
            messagebox.showinfo('Success', 'All logs exported to CSV successfully.', parent=self.parent)