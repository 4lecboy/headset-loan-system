import tkinter as tk
from tkinter import Label, Button, Frame, StringVar, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from tkcalendar import DateEntry

from controllers.statistics_controller import StatisticsController
from ui.components import ContentFrame
from ui.themes import COLORS, FONTS

class StatisticsForm:
    """
    Form for displaying and interacting with system statistics and visualizations
    """
    def __init__(self, parent):
        """
        Initialize the statistics form
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.controller = StatisticsController()
        
        # Create main frame
        self.frame = tk.Frame(parent, background=COLORS["primary"], 
                             highlightbackground=COLORS["bezel"], highlightthickness=2)
        self.frame.pack(side="right", anchor="n", fill="both", expand=True)
        
        # Create the UI components
        self.create_filter_panel()
        self.create_content_panel()
        
        # Default end date is today, start date is 30 days ago
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=30)
        
        # Update the date entries with the default values
        self.start_date_entry.set_date(self.start_date)
        self.end_date_entry.set_date(self.end_date)
        
        # Generate initial statistics
        self.generate_statistics()
    
    def create_filter_panel(self):
        """Create the filter panel with date controls and buttons"""
        filter_frame = tk.Frame(self.frame, background=COLORS["primary"])
        filter_frame.pack(side="top", anchor="n", fill="x", padx=20, pady=10)
        
        # Date range selection
        Label(filter_frame, text="Start Date:", font=FONTS["label"], 
              bg=COLORS["primary"], fg=COLORS["text_light"]).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.start_date_entry = DateEntry(filter_frame, width=12, 
                                         background=COLORS["primary"],
                                         foreground=COLORS["text_light"],
                                         borderwidth=2,
                                         date_pattern='yyyy-mm-dd')
        self.start_date_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        Label(filter_frame, text="End Date:", font=FONTS["label"], 
              bg=COLORS["primary"], fg=COLORS["text_light"]).grid(row=0, column=2, sticky="w", pady=5, padx=5)
        
        self.end_date_entry = DateEntry(filter_frame, width=12, 
                                       background=COLORS["primary"],
                                       foreground=COLORS["text_light"],
                                       borderwidth=2,
                                       date_pattern='yyyy-mm-dd')
        self.end_date_entry.grid(row=0, column=3, sticky="w", pady=5, padx=5)
        
        # Action buttons
        generate_btn = Button(filter_frame, text="Generate Statistics", 
                             command=self.generate_statistics,
                             bg=COLORS["primary"], fg=COLORS["text_light"],
                             font=FONTS["button"])
        generate_btn.grid(row=0, column=4, sticky="w", pady=5, padx=20)
        
        export_btn = Button(filter_frame, text="Export Report", 
                           command=self.export_statistics,
                           bg=COLORS["primary"], fg=COLORS["text_light"],
                           font=FONTS["button"])
        export_btn.grid(row=0, column=5, sticky="w", pady=5, padx=5)
        
        # Filter presets
        preset_frame = tk.Frame(filter_frame, bg=COLORS["primary"])
        preset_frame.grid(row=1, column=0, columnspan=6, sticky="w", pady=5)
        
        # Preset buttons for common date ranges
        presets = [
            ("Last 7 Days", 7),
            ("Last 30 Days", 30),
            ("Last 90 Days", 90),
            ("This Year", 365)
        ]
        
        for i, (text, days) in enumerate(presets):
            btn = Button(preset_frame, 
                       text=text, 
                       command=lambda d=days: self.set_date_range(d),
                       bg=COLORS["secondary"], 
                       fg=COLORS["text_light"],
                       font=FONTS["small_label"])
            btn.grid(row=0, column=i, padx=5)
    
    def create_content_panel(self):
        """Create the main content panel with statistics and charts"""
        # Use the ContentFrame component
        content = ContentFrame(self.frame, "Headset Usage Statistics")
        
        # Create a notebook for multiple tabs of statistics
        self.notebook = ttk.Notebook(content.get_bezel_frame())
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Summary Statistics
        self.summary_tab = Frame(self.notebook, bg=COLORS["background"])
        self.notebook.add(self.summary_tab, text="Summary")
        
        # Tab 2: Charts
        self.charts_tab = Frame(self.notebook, bg=COLORS["background"])
        self.notebook.add(self.charts_tab, text="Charts")
        
        # Tab 3: Top Users
        self.users_tab = Frame(self.notebook, bg=COLORS["background"])
        self.notebook.add(self.users_tab, text="Top Users")
        
        # Tab 4: Headset Usage
        self.headsets_tab = Frame(self.notebook, bg=COLORS["background"])
        self.notebook.add(self.headsets_tab, text="Headset Usage")
    
    def set_date_range(self, days):
        """
        Set date range based on preset buttons
        
        Args:
            days: Number of days to look back
        """
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=days)
        
        # Update the date entries
        self.start_date_entry.set_date(self.start_date)
        self.end_date_entry.set_date(self.end_date)
        
        # Generate statistics with new date range
        self.generate_statistics()
    
    def generate_statistics(self):
        """Generate and display statistics based on selected date range"""
        # Get dates from the date entries
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        
        # Format dates for database query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        try:
            # Get headset data from controller
            data = self.controller.generate_headsets_graph(start_date_str, end_date_str)
            
            if data.empty:
                messagebox.showinfo("No Data", 
                                   f"No headset activity data found between {start_date_str} and {end_date_str}.",
                                   parent=self.parent)
                return
            
            # Generate overall statistics
            overall_stats = self.controller.get_overall_statistics()
            
            # Clear previous widgets from tabs
            for widget in self.summary_tab.winfo_children():
                widget.destroy()
                
            for widget in self.charts_tab.winfo_children():
                widget.destroy()
                
            for widget in self.users_tab.winfo_children():
                widget.destroy()
                
            for widget in self.headsets_tab.winfo_children():
                widget.destroy()
            
            # Populate Summary Tab
            self.populate_summary_tab(overall_stats)
            
            # Populate Charts Tab
            self.populate_charts_tab(data)
            
            # Populate Users Tab
            self.populate_users_tab(overall_stats['top_borrowers'])
            
            # Populate Headsets Tab
            self.populate_headsets_tab(overall_stats['most_borrowed_headsets'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate statistics: {str(e)}", parent=self.parent)
    
    def populate_summary_tab(self, stats):
        """
        Populate the summary statistics tab
        
        Args:
            stats: Dictionary containing overall statistics
        """
        # Create a frame for the summary statistics
        summary_frame = Frame(self.summary_tab, bg=COLORS["background"])
        summary_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create labels for statistics
        Label(summary_frame, text="Overview Statistics", 
             font=FONTS["subheader"], bg=COLORS["background"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Display key statistics
        stat_items = [
            ("Total Headsets:", stats['total_headsets']),
            ("Available Headsets:", stats['available_headsets']),
            ("Currently Issued:", stats['issued_headsets']),
            ("Never Returned:", stats['never_returned']),
        ]
        
        for i, (label, value) in enumerate(stat_items):
            Label(summary_frame, text=label, 
                 font=FONTS["label"], bg=COLORS["background"]).grid(
                row=i+1, column=0, sticky="w", pady=5)
            
            value_label = Label(summary_frame, text=str(value), 
                               font=FONTS["label"], bg=COLORS["background"])
            value_label.grid(row=i+1, column=1, sticky="w", pady=5, padx=20)
            
            # Color coding for values
            if label == "Available Headsets:":
                value_label.config(fg=COLORS["success"])
            elif label == "Currently Issued:":
                value_label.config(fg=COLORS["accent"])
            elif label == "Never Returned:":
                if stats['never_returned'] > 0:
                    value_label.config(fg=COLORS["error"])
        
        # Create a small pie chart for headset status
        fig, ax = plt.subplots(figsize=(4, 4))
        labels = ['Available', 'Issued']
        sizes = [stats['available_headsets'], stats['issued_headsets']]
        colors = [COLORS["success"], COLORS["accent"]]
        
        # Plot the pie chart
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Embed the pie chart in the summary tab
        canvas = FigureCanvasTkAgg(fig, master=summary_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=2, rowspan=4, padx=20)
    
    def populate_charts_tab(self, data):
        """
        Populate the charts tab with visualization of headset activity
        
        Args:
            data: DataFrame with headset activity data
        """
        # Create chart using the controller
        fig = self.controller.create_comparison_plot(data)
        
        # Embed the chart in the charts tab
        canvas = FigureCanvasTkAgg(fig, master=self.charts_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def populate_users_tab(self, top_borrowers):
        """
        Populate the users tab with top borrowers data
        
        Args:
            top_borrowers: List of tuples with (name, count) for top borrowers
        """
        # Create a frame for the top borrowers table
        users_frame = Frame(self.users_tab, bg=COLORS["background"])
        users_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add label
        Label(users_frame, text="Top Borrowers", 
             font=FONTS["subheader"], bg=COLORS["background"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Create column headers
        Label(users_frame, text="Name", font=FONTS["label"], 
             bg=COLORS["secondary"], fg=COLORS["text_light"], width=30).grid(
            row=1, column=0, sticky="ew", pady=2)
        
        Label(users_frame, text="Headsets Borrowed", font=FONTS["label"], 
             bg=COLORS["secondary"], fg=COLORS["text_light"], width=15).grid(
            row=1, column=1, sticky="ew", pady=2)
        
        # Populate data rows
        for i, (name, count) in enumerate(top_borrowers):
            Label(users_frame, text=name, font=FONTS["entry"], 
                 bg=COLORS["background"], anchor="w", padx=5).grid(
                row=i+2, column=0, sticky="ew", pady=2)
            
            Label(users_frame, text=str(count), font=FONTS["entry"], 
                 bg=COLORS["background"]).grid(
                row=i+2, column=1, sticky="ew", pady=2)
        
        # Create a bar chart of top borrowers
        if top_borrowers:
            names, counts = zip(*top_borrowers)
            
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(names, counts, color=COLORS["secondary"])
            
            ax.set_title('Top Borrowers')
            ax.set_ylabel('Number of Headsets Borrowed')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Add data labels above bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                      f'{height}', ha='center', va='bottom')
            
            # Embed the chart
            chart_frame = Frame(users_frame, bg=COLORS["background"])
            chart_frame.grid(row=len(top_borrowers)+2, column=0, columnspan=2, pady=20)
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def populate_headsets_tab(self, most_borrowed):
        """
        Populate the headsets tab with most borrowed headsets data
        
        Args:
            most_borrowed: List of tuples with (asset_tag, count) for most borrowed headsets
        """
        # Create a frame for the most borrowed headsets table
        headsets_frame = Frame(self.headsets_tab, bg=COLORS["background"])
        headsets_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add label
        Label(headsets_frame, text="Most Frequently Borrowed Headsets", 
             font=FONTS["subheader"], bg=COLORS["background"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Create column headers
        Label(headsets_frame, text="Asset Tag", font=FONTS["label"], 
             bg=COLORS["secondary"], fg=COLORS["text_light"], width=20).grid(
            row=1, column=0, sticky="ew", pady=2)
        
        Label(headsets_frame, text="Times Borrowed", font=FONTS["label"], 
             bg=COLORS["secondary"], fg=COLORS["text_light"], width=15).grid(
            row=1, column=1, sticky="ew", pady=2)
        
        # Populate data rows
        for i, (asset_tag, count) in enumerate(most_borrowed):
            Label(headsets_frame, text=asset_tag, font=FONTS["entry"], 
                 bg=COLORS["background"], anchor="w", padx=5).grid(
                row=i+2, column=0, sticky="ew", pady=2)
            
            Label(headsets_frame, text=str(count), font=FONTS["entry"], 
                 bg=COLORS["background"]).grid(
                row=i+2, column=1, sticky="ew", pady=2)
        
        # Create a bar chart of most borrowed headsets
        if most_borrowed:
            assets, counts = zip(*most_borrowed)
            
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(assets, counts, color=COLORS["accent"])
            
            ax.set_title('Most Frequently Borrowed Headsets')
            ax.set_ylabel('Number of Times Borrowed')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Add data labels above bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                      f'{height}', ha='center', va='bottom')
            
            # Embed the chart
            chart_frame = Frame(headsets_frame, bg=COLORS["background"])
            chart_frame.grid(row=len(most_borrowed)+2, column=0, columnspan=2, pady=20)
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def export_statistics(self):
        """Export statistics to CSV file"""
        try:
            # Get dates from the date entries
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()
            
            # Format dates for export
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Export statistics using controller
            filename = self.controller.export_statistics(start_date_str, end_date_str)
            
            if filename:
                messagebox.showinfo("Export Successful", 
                                  f"Statistics exported to {filename}",
                                  parent=self.parent)
            else:
                messagebox.showwarning("Export Failed", 
                                     "No data available to export.",
                                     parent=self.parent)
                
        except Exception as e:
            messagebox.showerror("Export Error", 
                               f"Failed to export statistics: {str(e)}",
                               parent=self.parent)