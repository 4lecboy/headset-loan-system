import tkinter as tk
from tkinter import Entry, StringVar, Listbox

class AutocompleteEntry(Entry):
    """
    Custom entry widget with autocomplete functionality
    """
    def __init__(self, master, completevalues=[], *args, **kwargs):
        self.var = StringVar()
        super().__init__(master, textvariable=self.var, *args, **kwargs)
        self.listbox = Listbox(master, width=self['width'])
        self.completevalues = completevalues
        self.listbox_visible = False
        self.listbox.bind("<Double-Button-1>", self.on_select)
        self.bind("<KeyRelease>", self.on_key_release)

    def update_listbox(self, matches):
        self.listbox.delete(0, tk.END)
        for item in matches:
            self.listbox.insert(tk.END, item)

    def show_listbox(self):
        if self.completevalues:
            search_term = self.var.get().lower()
            matches = [name for name in self.completevalues if search_term in name.lower()]
            self.update_listbox(matches)
            if matches:
                self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                num_items = min(len(matches), 6)
                self.listbox.config(height=num_items)
                self.listbox_visible = True
        else:
            self.hide_listbox()

    def hide_listbox(self):
        self.listbox.delete(0, tk.END)
        self.listbox.place_forget()
        self.listbox_visible = False

    def on_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_item = self.listbox.get(selected_index)
            self.var.set(selected_item)
            self.hide_listbox()

    def on_key_release(self, event):
        self.show_listbox()
        

class DataTable:
    """
    Custom table widget for displaying data in a tabular format
    """
    def __init__(self, parent, columns, column_names):
        from tkinter import ttk
        
        self.table = ttk.Treeview(parent, columns=columns, show='headings')
        
        for col in columns:
            self.table.column(col, anchor=tk.CENTER, width=120)
            self.table.heading(col, text=column_names[col], anchor=tk.CENTER)

    def populate_table(self):
        for i, row in enumerate(self.data_source):
            self.table.insert(parent='', index='end', iid=i, text='', values=row)

    def get_table(self):
        return self.table