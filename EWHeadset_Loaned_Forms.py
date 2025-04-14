#MADE BY WILLIE DAVIS
#02-22-2024

#BULK LOAN FEATURE added by ALEC QUIAMBAO
#02-12-2025

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import OptionMenu, StringVar
from PIL import ImageTk, Image
from tkcalendar import DateEntry
from datetime import datetime
import threading
import schedule
import time
from tkinter import filedialog, messagebox
import io
import os
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage  # Add this line
from email import encoders
# MADE BY WILLIE DAVIS

main = tk.Tk()
main.title("Headset Loaning System")
main.config(background="#E0E1E1")
window_width = 1200
window_height = 960
screen_width = main.winfo_screenwidth()
screen_height = main.winfo_screenheight()
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 3
main.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

LoanFrame = None
HeadsetFrame = None
StatisticsFrame = None
TableFrame = None
GraphFrame = None
DeletionFrame = None
LogsFrame = None

global MAX_ALLOWED_ISSUED
body = None
html_body = None
all_items = None

global user_name_global
global ashima_user_global
user_name_global = None 
ashima_user_global = None


def destroy_frame(frame):
    if frame:
        frame.destroy()
        

def connect_to_mysql():
    conn = pymysql.connect(
        host='10.42.10.38', #10.42.10.38
        user='root',
        password='',
        database='headsets',
        autocommit=True
    )
    return conn

"""def connect_to_mysql():
    conn = pymysql.connect(
        host='localhost', #10.42.10.38
        user='root',
        password='',
        database='headsets',
        autocommit=True
    )
    return conn"""

def get_image_from_db(image_id):
    connection = connect_to_mysql()
    try:
        cursor = connection.cursor()
        query = "SELECT image_data FROM images WHERE id = %s"
        cursor.execute(query, (image_id,))
        result = cursor.fetchone()
        if result:
            image_data = result[0]
            # Convert the raw bytes to a PIL Image object
            image = Image.open(io.BytesIO(image_data))
            return image_data, image
        else:
            print("Image not found.")
            return None, None
    except Exception as e:
        print(f"Error retrieving image from database: {e}")
        return None, None
    finally:
        cursor.close()
        connection.close()



def fetch_sent_records():
    conn = connect_to_mysql()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM sentrecords WHERE Status = 'Issued'")
        records = cursor.fetchall()
        return records
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching records: {str(e)}")
    finally:
        cursor.close()
        conn.close()
        
def fetch_emp(AshimaID):
        conn = connect_to_mysql()
        cursor = conn.cursor()

        try:
            # Execute query to fetch employee information based on Ashima ID
            cursor.execute("SELECT FirstName, LastName, Campaign FROM empinfo WHERE AshimaID = %s", (AshimaID,))
            record = cursor.fetchone()
            
            if record:
                return {
                    'FirstName': record[0],
                    'LastName': record[1],
                    'Campaign': record[2]
                }
            else:
                return None
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching employee info: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()
        
def open_loan_window():
    destroy_frame(ReturnFrame)
    destroy_frame(StatisticsFrame)
    destroy_frame(GraphFrame)
    destroy_frame(LoanFrame)
    destroy_frame(DeletionFrame)
    destroy_frame(LogsFrame)
    Loan_Form()
    

def open_return_window():
    destroy_frame(LoanFrame)
    destroy_frame(StatisticsFrame)
    destroy_frame(GraphFrame)
    destroy_frame(ReturnFrame)
    destroy_frame(DeletionFrame)
    destroy_frame(LogsFrame)
    Return_form()
    
def open_statistics_window():
    destroy_frame(LoanFrame)
    destroy_frame(StatisticsFrame)
    destroy_frame(GraphFrame)
    destroy_frame(ReturnFrame)
    destroy_frame(DeletionFrame)
    destroy_frame(LogsFrame)
    Statistics_form()
    
def open_deletion_window():
    destroy_frame(LoanFrame)
    destroy_frame(StatisticsFrame)
    destroy_frame(GraphFrame)
    destroy_frame(ReturnFrame)
    destroy_frame(DeletionFrame)
    destroy_frame(LogsFrame)
    Deletion_form()
    
def open_logs_window():
    destroy_frame(LoanFrame)
    destroy_frame(StatisticsFrame)
    destroy_frame(GraphFrame)
    destroy_frame(ReturnFrame)
    destroy_frame(DeletionFrame)
    destroy_frame(LogsFrame)
    Logs()

    
def open_headset_window():
    Addheadset()
    
def open_campaign_window():
    AddCampaign()
    
def open_room_window():
    AddRoom()

def close_application(event=None):
        if messagebox.askokcancel("Closing Application", "Do you want to close the application?"):
            main.destroy()
    
def validate_input(new_value):
    # Check if the new value is empty or consists only of digits and has length <= 10
    if new_value == "" or (new_value.isdigit() and len(new_value) <= 10):
        return True
    else:
        return False

def on_validate(P):
    if len(P) > 10:
        return False
    if all(char.isdigit() or char == '-' for char in P) or P == "":
        return True
    return False

def on_validatename(P):
    if len(P) > 15:
        return False
    return True

def on_validatepass(P):
    if len(P) > 25:
        return False
    return True

def on_validateasset(P):
    if len(P) > 15:
        return False
    if all(char.isalnum() or char == '-' for char in P) or P == "":
        return True
    return False

def on_validateroom(P):
    if len(P) > 20:
        return False
    if all(char.isalnum() for char in P) or P == "":
        return True
    return False

def on_validatecampaign(P):
    if len(P) > 15:
        return False
    if all(char.isalnum() for char in P) or P == "":
        return True
    return False


def populate_employee_info(ashima_id_entry, name1_entry, name2_entry, campaign_var):
        ashima_id = ashima_id_entry.get().strip()

        if ashima_id:
            employee_info = fetch_emp(ashima_id)
            if employee_info:
                name1_entry.delete(0, tk.END)
                name1_entry.insert(0, employee_info['FirstName'])

                name2_entry.delete(0, tk.END)
                name2_entry.insert(0, employee_info['LastName'])

                campaign_var.set(employee_info['Campaign'])
            else:
                # Clear fields if no matching record found
                name1_entry.delete(0, tk.END)
                name2_entry.delete(0, tk.END)
                campaign_var.set("Select Campaign")  # Reset campaign to default
        else:
            # Clear fields if Ashima ID is empty
            name1_entry.delete(0, tk.END)
            name2_entry.delete(0, tk.END)
            campaign_var.set("Select Campaign")  # Reset campaign to default
            
class AutocompleteEntry(Entry):
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
        print("Showing listbox...")
        print("Showing listbox for Ashima entry...")
        if self.completevalues:
            search_term = self.var.get().lower()
            print("Search term:", search_term)
            matches = [name for name in self.completevalues if search_term in name.lower()]
            print("Matches:", matches)
            self.update_listbox(matches)
            if matches:
                self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                num_items = min(len(matches), 6)
                self.listbox.config(height=num_items)
                self.listbox_visible = True
        else:
            self.hide_listbox()

    def hide_listbox(self):
        print("Hiding listbox...")
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
        print("Key released:", event.keysym)
        print("Key released for Ashima entry:", event.keysym)
        self.show_listbox()

def fetch_asset_tags():
    """Fetch all available asset tags from the database."""
    conn = connect_to_mysql()  # Ensure this function exists and connects to your database
    cursor = conn.cursor()

    try:
        query = "SELECT AssetTagID FROM storage_list WHERE Flag = 1"  # Fetch available asset tags
        cursor.execute(query)
        records = cursor.fetchall()
        return [record[0] for record in records]  # Extract only the AssetTagID values
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching asset tags: {str(e)}", parent=main)
        return []
    finally:
        cursor.close()
        conn.close()


def open_bulk_loan_window(asset_entry):
    bulk_window = tk.Toplevel(main)
    bulk_window.title("Bulk Loan - Enter Asset Tags")
    bulk_window.geometry("400x800")
    bulk_window.config(bg="#172f66")

    asset_entries = []  
    asset_tags_list = fetch_asset_tags()  

    def submit_bulk_loan():
        asset_tags = [entry.get().strip() for entry in asset_entries if entry.get().strip()]
        if not asset_tags:
            messagebox.showerror("Error", "Please enter at least one Asset Tag!", parent=bulk_window)
            return

        asset_entry.delete(0, tk.END)
        asset_entry.insert(0, ", ".join(asset_tags))  

        bulk_window.destroy()

    for i in range(10):
        label = Label(bulk_window, text=f"Asset Tag {i+1}:", bg="#172f66", fg="white", font=("Arial", 10, "bold"))
        label.pack(pady=(5, 0))

        entry = AutocompleteEntry(bulk_window, completevalues=asset_tags_list, font=("Arial", 10))
        entry.pack(pady=(0, 5), padx=20, fill="x")
        asset_entries.append(entry)

    submit_button = Button(bulk_window, text="Submit", command=submit_bulk_loan, bg="green", fg="white", font=("Arial", 12, "bold"))
    submit_button.pack(pady=20)
     
        
def Loan_Form():
    global LoanFrame
    global user_name_global
    
    
    LoanFrame = tk.Frame(main, background="#172f66", highlightbackground="#CBCBCB", highlightthickness=2)
    LoanFrame.pack(side=RIGHT, anchor=N, fill=BOTH, expand=TRUE)

    
    def fetch_asset_tags():
        conn = connect_to_mysql()
        cursor = conn.cursor()
        
        try:
            query = "SELECT AssetTagID FROM storage_list WHERE Flag = 1"
            print("Executing SQL query:", query)  # Print the SQL query for debugging
            cursor.execute(query)
            records = cursor.fetchall()
            asset_tags = [record[0] for record in records]
            return asset_tags
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching asset tags: {str(e)}", parent = main)
            return []
        finally:
            cursor.close()
            conn.close()
            
    def fetch_campaigns():
        conn = connect_to_mysql()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT CampaignName FROM tblcampaign")
            records = cursor.fetchall()
            return [record[0] for record in records]  # Extracting tag_name from each record
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching asset tags: {str(e)}", parent = main)
        finally:
            cursor.close()
            conn.close()
            
    def fetch_rooms():
        conn = connect_to_mysql()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT RoomNumber FROM tblroom")
            records = cursor.fetchall()
            return [record[0] for record in records]  # Extracting tag_name from each record
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching Rooms: {str(e)}", parent = main)
        finally:
            cursor.close()
            conn.close()
            
    def fetch_empID():
        conn = connect_to_mysql()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT AshimaID FROM empinfo")
            records = cursor.fetchall()
            return [record[0] for record in records]  # Extracting tag_name from each record
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching Rooms: {str(e)}", parent = main)
        finally:
            cursor.close()
            conn.close()
            
    def validate_entry():
        # Get all required fields and strip whitespace
        required_fields = [
            Room.get().strip(),
            Issuedby_entry.get().strip(),
            Assettag.get().strip(),  # Ensure asset tags are entered
            Campaign.get().strip(),
            Ashima_entry.get().strip(),
            Name1_entry.get().strip(),
            Name2_entry.get().strip()
        ]

        # Ensure at least one asset tag is entered
        if not required_fields[2]:  # Assettag.get().strip()
            messagebox.showerror("Error", "Please enter at least one Asset Tag!", parent=main)
            return False

        # Check if any required field is empty
        if "" in required_fields:
            messagebox.showerror("Error", "Please fill out all required fields!", parent=main)
            return False

        return True  # All validations passed
      
            
    '''def update_treeview():
        tree.delete(*tree.get_children())
    
        # Fetch latest records from the database
        records = fetch_sent_records()
        
        # Insert fetched records into the treeview
        for record in records:
            # Extract columns 0, 1, 2, 3, and 6 from each record
            values_to_display = (record[0], record[1], record[2], record[3], record[6])
            tree.insert('', 'end', values=values_to_display)'''
    
    def update_current_date_time():
        # Get current date and time
        now = datetime.now()
        current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")  # Format the date and time
        
        # Update the entry widget with the current date and time
        Date_entry.delete(0, tk.END)  # Clear any existing text
        Date_entry.insert(0, current_date_time)  # Set the current date and time as text in the entry widget
        
        # Schedule the update function to run again after 1 second (1000 milliseconds)
        LoanFrame.after(1000, update_current_date_time)
    
    
    centerframe = tk.Frame(LoanFrame, background="#172f66")
    centerframe.pack(side="left", anchor="n", fill= "both", expand=TRUE)
    
    Date = Label(centerframe, text = "Date*", font=("ANTON", 12, "bold"),bg="#172f66", fg="#FFFFFF")
    Date.grid(row=2, column=1, padx=200, pady=(30,0), sticky='nw')
    
    Date_entry = Entry(centerframe, font=15)
    Date_entry.grid(row=3, column=1, columnspan=2, padx=200, pady=10, sticky='nw')
    
    Ashima = Label(centerframe, text = "Ashima Number*", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    Ashima.grid(row= 2, column= 3, padx=200, pady=(30,0), sticky='nw')
    
    
    vcmd = (centerframe.register(on_validate), '%P')
    emp_ID = fetch_empID()
    
    print("Ashima IDs:", emp_ID)
    
    Ashima_entry = AutocompleteEntry(centerframe, completevalues=emp_ID, validate="key", validatecommand=vcmd, font=12)
    Ashima_entry.grid(row=3, column=3, columnspan=3, padx=200, pady=10, sticky='nw')
    Ashima_entry.bind("<KeyRelease>", lambda event: populate_employee_info(Ashima_entry, Name1_entry, Name2_entry, Campaign), Ashima_entry.on_key_release)
    
    Ashima_entry.focus()
    
    Name = Label(centerframe, text = "Name*", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    Name.grid(row= 4, column= 1, padx=200, pady=(30,0), sticky='nw')
    
    vcmdname = (centerframe.register(on_validatename), '%P')
    vcmdasset = (centerframe.register(on_validateasset), '%P')
    
    Name1_entry = Entry(centerframe, font=12)
    Name1_entry.grid(row=5, column=1, columnspan=3, padx=200, pady=10, sticky='nw')
    
    
    Name2_entry = Entry(centerframe, font=12)
    Name2_entry.grid(row=5, column=3, columnspan=3, padx=200, pady=10, sticky='nw')
    
    
    Name1 = Label(centerframe, text = "First", font=("ANTON", 8, "bold"), bg="#172f66", fg="#d3d3d3")
    Name1.grid(row= 6, column= 1, padx=200, pady=(1,0), sticky='nw')
    
    Name2 = Label(centerframe, text = "Last", font=("ANTON", 8, "bold"), bg="#172f66", fg="#d3d3d3")
    Name2.grid(row= 6, column= 3, padx=200, pady=(1,0), sticky='nw')
    
    Campaign = Label(centerframe, text = "Campaign*", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    Campaign.grid(row= 7, column= 1, padx=200, pady=(30,0), sticky='nw')
    
    Campaign_list = fetch_campaigns()
    
    Campaign = StringVar()
    
    default_campaign = "Select Campaign"  # Set your desired default value here
    Campaign.set(default_campaign)
    
    Campaign_entry = OptionMenu( centerframe , Campaign , *Campaign_list ) 
    Campaign_entry.grid(row=8, column=1, columnspan=3, padx=(210,10), pady=10, ipadx=15, sticky='nw')
    CampaignAdd = Button(centerframe, text="+", command=open_campaign_window, bg="#172f66", fg="#FFFFFF", font=("ANTON", 7, "bold"))
    CampaignAdd.grid(row=8, column=1, columnspan=2, padx=200, sticky='nw', pady=15, ipadx=5)
    
    
    Room = Label(centerframe, text = "Room Number*", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    Room.grid(row= 7, column= 3, padx=200, pady=(30,0), sticky='nw')
    
    Roomslist = fetch_rooms()
    
    Room = StringVar()
    
    default_room = "Select Room"  # Set your desired default value here
    Room.set(default_room)
    
    Room_entry = OptionMenu( centerframe , Room , *Roomslist ) 
    Room_entry.grid(row=8, column=3, columnspan=3, padx=215, ipadx=2, pady=10, sticky='nw')
    RoomAdd = Button(centerframe, text="+", command=open_room_window, bg="#172f66", fg="#FFFFFF", font=("ANTON", 7, "bold"))
    RoomAdd.grid(row=8, column=3, columnspan=2, padx=200, sticky='nw', pady=15, ipadx=5)
    
    
    AssetTag = Label(centerframe, text="Asset Tags*", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    AssetTag.grid(row=9, column=1, padx=200, pady=(30, 0), sticky='nw')

    asset_tags_list = fetch_asset_tags()  # Fetch available asset tags

    Assettag = AutocompleteEntry(centerframe, completevalues=asset_tags_list, font=12)
    Assettag.grid(row=10, column=1, padx=(225, 10), pady=5, sticky='nw')

    # Move the button directly beside the entry box
    bulk_loan_button = Button(centerframe, text="Bulk Loan", 
                            command=lambda: open_bulk_loan_window(Assettag), 
                            bg="#172f66", fg="#FFFFFF", font=("ANTON", 10, "bold"))
    bulk_loan_button.grid(row=10, column=1, padx=(415, 0), pady=5, sticky='nw')  # Adjusted positioning


    Assetadd = Button(centerframe, text="+", command=open_headset_window, bg="#172f66", fg="#FFFFFF", font=("ANTON", 7, "bold"))
    Assetadd.grid(row=10, column=1, padx=(200,200), sticky='nw', ipadx=5)
    
    
    Issuedby = Label(centerframe, text = "Issued By*", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    Issuedby.grid(row= 9, column= 3, padx=200, pady=(30,0), sticky='nw')
    
    Issuedby_entry = Entry(centerframe, validate="key", validatecommand=vcmdname, font=12)
    Issuedby_entry.grid(row=10, column=3, columnspan=3, padx=200, sticky='nw')
    
    if user_name_global:
        Issuedby_entry.insert(0, user_name_global)
    
    
    '''tree = ttk.Treeview(sideframe, columns=('ID', 'Date','AshimaID', 'Name', 'AssetTag'), show='headings')
    tree.heading('#1', text='ID')
    tree.heading('#2', text='Date')
    tree.heading('#3', text='AshimaID')
    tree.heading('#4', text='Name')
    tree.heading('#5', text='AssetTag')
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(sideframe, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)
    
    update_treeview()
    
    back = Button(main, text = "Home", command= Loan_window.destroy , bg="#f46206", fg="#000000", font=("ANTON", 15, "bold"))
    back.pack(side="bottom", pady=25, anchor="sw")'''
    
    
    update_current_date_time()

    
    # Configure row and column to expand automatically
    LoanFrame.grid_rowconfigure(1, weight=1)
    LoanFrame.grid_columnconfigure(1, weight=1)
    
    def check_ashima_id_exists(conn, ashima_id):
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM empinfo WHERE AshimaID = %s", (ashima_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    
    def check_asset_id_exists(conn, asset_tag):
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM storage_list WHERE AssetTagID = %s", (asset_tag,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count > 0
     
    def submit_loan_form():
        print("Submit button clicked!")
        if validate_entry():
            date_issued = Date_entry.get()
            ashima_id = Ashima_entry.get()
            name = f"{Name1_entry.get()} {Name2_entry.get()}"
            campaign = Campaign.get()
            room_number = Room.get()
            asset_tags = [tag.strip() for tag in Assettag.get().split(",")]  # Split input by commas
            issued_by = Issuedby_entry.get()
            emp1 = Name1_entry.get()
            emp2 = Name2_entry.get()

            if room_number != default_room and campaign != default_campaign:
                conn = connect_to_mysql()
                
                if check_ashima_id_exists(conn, ashima_id):
                    MAX_ALLOWED_ISSUED = maxissued(ashima_id)
                    count_issued = count_issued_instances(conn, name)

                    if count_issued + len(asset_tags) <= MAX_ALLOWED_ISSUED:
                        for asset_tag in asset_tags:
                            if check_asset_id_exists(conn, asset_tag):  # Check each asset tag
                                insert_loan_record(date_issued, ashima_id, name, campaign, room_number, asset_tag, issued_by)
                            else:
                                messagebox.showerror("Error", f"Asset_Tag: ({asset_tag}) does not exist!", parent=main)
                        messagebox.showinfo("Success", "Loan records added successfully!", parent=main)
                        open_loan_window()
                    else:
                        messagebox.showerror(
                            "Error", 
                            f"Maximum number of issued items ({MAX_ALLOWED_ISSUED}) reached for {name}!", 
                            parent=main
                        )
                else:
                    conn.close()
                    if messagebox.askyesno("Confirmation", "Ashima ID does not exist. Is this ID for a supervisor?", parent=main):
                        privilege = 2
                    else:
                        privilege = 1
                    insert_empinfo(ashima_id, privilege, emp1, emp2, campaign)

                    # Insert all asset tags for the new employee
                    for asset_tag in asset_tags:
                        insert_loan_record(date_issued, ashima_id, name, campaign, room_number, asset_tag, issued_by)
                    
                    messagebox.showinfo("Success", "Loan records added successfully!", parent=main)
                    open_loan_window()
                    
                conn.close()
            else:
                messagebox.showerror("Error", "Please Fill Out All Entry Fields!", parent=main)
        else:
            messagebox.showerror("Error", "Please Fill Out All Entry Fields!", parent=main)

    submit_button = Button(centerframe, text="Submit", command=submit_loan_form, bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
    submit_button.grid(row=11, column=2, columnspan=2, pady=30, sticky='nw')


def insert_empinfo(ashima_id, privilege, emp1, emp2, campaign):
        conn = connect_to_mysql()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO empinfo (AshimaID, FirstName, LastName, Campaign, Privilege) VALUES (%s, %s, %s, %s, %s)", (ashima_id, emp1, emp2, campaign, privilege))
        conn.commit()
        
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)", 
                       (ashima_user_global, user_name_global, "Added Employee", ashima_id, current_datetime))
        conn.commit()
        cursor.close()
        conn.close()

    
def count_issued_instances(conn, name):
    # Function to count the number of "Issued" instances for a specific name
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM SentRecords WHERE Name = %s AND Status = 'Issued'", (name,))
    count = cursor.fetchone()[0]
    cursor.close()
    return count
        
def insert_loan_record(date_issued, ashima_id, name, campaign, room_number, asset_tag, issued_by):
    conn = connect_to_mysql()
    cursor = conn.cursor()
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Insert into SentRecords
        cursor.execute("INSERT INTO SentRecords (DateIssued, AshimaID, Name, Campaign, RoomNumber, AssetTag, IssuedBy, Status) VALUES (%s, %s, %s, %s, %s, %s, %s, 'Issued')",
                       (date_issued, ashima_id, name, campaign, room_number, asset_tag, issued_by))

        # Mark headset as loaned
        cursor.execute("UPDATE storage_list SET Flag = '0' WHERE AssetTagID = %s", (asset_tag,))  

        # Log the action in tbllogs
        cursor.execute("INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)", 
                       (ashima_id, issued_by, "Loaned Headset", asset_tag, current_datetime))

        conn.commit()
    except Exception as e:
        messagebox.showerror("Error", f"Database Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
    
def maxissued(ashima_id):
    conn = connect_to_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT Privilege FROM empinfo WHERE AshimaID = %s", (ashima_id,))
    result = cursor.fetchone()
    
    if result:
        privilege = result[0]
        if privilege == 1:
            MAX_ALLOWED_ISSUED = 2
        elif privilege == 2:
            MAX_ALLOWED_ISSUED = 10
    else:
        # Default values if AshimaID is not found
        privilege = 1
        MAX_ALLOWED_ISSUED = 2
    
    cursor.close()
    conn.close()
    
    return MAX_ALLOWED_ISSUED

def returnedissued():
    conn = connect_to_mysql()
    cursor = conn.cursor()

    try:
        # Count the number of records with status 'Issued'
        cursor.execute("SELECT COUNT(*) FROM storage_list WHERE Flag = '0'")
        issued_amount = cursor.fetchone()[0]
        

        # Count the number of records with status 'Returned'
        cursor.execute("SELECT COUNT(*) FROM storage_list WHERE Flag = '1'")
        returned_amount = cursor.fetchone()[0]

    except Exception as e:
        print(f"Error counting records: {e}")
        issued_amount = 0
        returned_amount = 0

    finally:
        cursor.close()
        conn.close()
    
    return issued_amount, returned_amount

def get_all_items(tree):
    global all_items
    all_items = []
    for item in tree.get_children():
        values = tree.item(item, 'values')
        all_items.append(values)
    return all_items

def format_tree_data(data):
    # Define header WITHOUT "Campaign"
    header = ["Date Issued", "AshimaID", "Issued To", "Room Number", "Asset Tags", "Issued By", "Status"]

    # Create HTML table
    html_table = '<table border="1" cellspacing="0" cellpadding="5">'
    
    # Add header row
    html_table += '<tr>' + ''.join(f'<th>{col}</th>' for col in header) + '</tr>'
    
    # Add data rows, SKIPPING index 3 (Campaign)
    for row in data:
        html_table += '<tr>'
        for i, item in enumerate(row):
            if i == 3:  # Skip Campaign column
                continue
            html_table += f'<td>{item}</td>'
        html_table += '</tr>'
    
    html_table += '</table>'
    return html_table


def create_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header row without the first column
        csv_writer.writerow(["Date Issued", "AshimaID", "Issued To", "Campaign", "Room Number", "Asset Tags", "Issued By", "Status"])
        # Write data without the first column
        csv_writer.writerows(data)
        
def send_email_with_attachment(sender_email, receiver_email, cc_emails, subject, body, attachment_filename, logo_data, smtp_server, smtp_port, login, password):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Cc'] = ', '.join(cc_emails)
    msg['Subject'] = subject

    # Read the logo image file and attach it to the email
    logo = MIMEImage(logo_data)
    logo.add_header('Content-ID', '<logo>')
    msg.attach(logo)

    # Generate HTML content with logo
    html_content = f"""
    <html>
    <head></head>
    <body>
        <img src="cid:logo" alt="Logo" style="width:100px;height:100px;position:absolute;top:0;left:0;"><br>
        <p>Good Day Team,</p>
        <p>I hope this message finds you well.</p>
        <p>As part of our ongoing efforts to maintain inventory accuracy, Our records indicate that there are several headsets that have not been returned.</p>
        <p>As for PDDs, your assistance in addressing this issue promptly is crucial. Could we kindly request your support in reminding your team members to return their headsets immediately after their shifts?</p>
        <p>Your guidance in reinforcing the importance of adhering to company policies will greatly assist in resolving this matter swiftly.</p>
        <p>Please find below the list of unreturned headsets along with the names of agents whom they were issued:</p>
        {body}
        <p>Thank you for your prompt attention to this matter.</p>
        <p>Note: This is an auto-generated email no need to reply.</p>
    </body>
    </html>
    """

    # Attach HTML content
    msg.attach(MIMEText(html_content, 'html'))

    # Attach CSV file
    with open(attachment_filename, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
        msg.attach(part)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(login, password)
        server.sendmail(sender_email, [receiver_email] + cc_emails, msg.as_string())

    # Remove the CSV file after sending the email
    os.remove(attachment_filename)
    
def Return_form():
    global ReturnFrame
    global user_name_global
    global body
    global html_body
    
    
    
    ReturnFrame = tk.Frame(main, background="#172f66", highlightbackground="#CBCBCB", highlightthickness=2)
    ReturnFrame.pack(side=RIGHT, anchor=N, fill=BOTH, expand=TRUE)
    
    #topframe = tk.Frame(ReturnFrame, background="#172f66")
    #topframe.pack(side="top", anchor="n", fill= "x")
    
    issued_amount, returned_amount = returnedissued()
    
    def export_to_csv():
        selected_items = tree.selection()
        if selected_items:
            # Prompt the user to choose the file path and name for saving the CSV file
            file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')],
                                                    initialfile='exported_data', title='Save CSV file')
            if file_path:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    # Write header row
                    writer.writerow(['Date Issued','AshimaID','Issued To','Campaign','Room Number','Asset Tag','Issued By', 'Status'])
                    # Write selected items to CSV
                    for item in selected_items:
                        item_text = tree.item(item, 'values')
                        writer.writerow(item_text)
                messagebox.showinfo('Success', 'CSV file exported successfully.')
        else:
            messagebox.showwarning('No Selection', 'Please select items to export.')

    def export_all_to_csv():
        # Prompt the user to choose the file path and name for saving the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')],
                                                    initialfile='exported_data', title='Save CSV file')
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write header row
                writer.writerow(['Date Issued','AshimaID','Issued To','Campaign','Room Number','Asset Tag','Issued By', 'Status'])
                # Write all items in the treeview to CSV
                for item in tree.get_children():
                    item_text = tree.item(item, 'values')
                    writer.writerow(item_text)
            messagebox.showinfo('Success', 'All data exported to CSV successfully.')
    def validate_entrytree():
        required_fields = [
        RecievedEntry.get().strip()
        ]
        if all(required_fields):
            return True
        else:
            print("Entry cannot be empty!")
            return False  
            

    
    #Loan = Label(topframe, text = "Headset Temporary Return Form", font=("ANTON", 35, "bold"),bg="#172f66", fg="#f46206")
    #Loan.pack(side="left", anchor="nw", pady=50, padx = 40)
    
    
    midframe = tk.Frame(ReturnFrame, background="#172f66")
    midframe.pack(side="top", anchor="n", fill="x", padx=20)
    
    Searchbar = Label(midframe, text="Search:", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    Searchbar.grid(row=1, column=0, sticky="nw",pady=10)
    
    SearchEntry = Entry(midframe, font=20)
    SearchEntry.grid(row=2, column=0, columnspan=2, sticky="nw")
    SearchEntry.focus()
    
    
    
    RecievedBy = Label(midframe, text="ReceivedBy*", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    RecievedBy.grid(row=1, column=1, sticky="nw", padx=200, pady=10)
    
    RecievedEntry = Entry(midframe, font=20)
    RecievedEntry.grid(row=2, column=1, sticky="nw", columnspan=3, padx=200)
    if user_name_global:
        RecievedEntry.insert(0, user_name_global)
    
    export_all_button = tk.Button(midframe, text= "Export All", command=export_all_to_csv, bg="#172f66", fg="#FFFFFF", font=("ANTON", 12, "bold"))
    export_all_button.grid(row=2, column=3, sticky="nw", padx=(300,0))

    export_button = tk.Button(midframe, text='Export Selected', bg="#172f66", fg="#FFFFFF", command=export_to_csv, font=("ANTON", 12, "bold"))
    export_button.grid(row=2, column=4, sticky="nw")
    
    
    bezel_frame = tk.Frame(ReturnFrame, background="#000000", highlightbackground="#0096F7", highlightthickness=4, bd=0)
    bezel_frame.pack(side="top", anchor="n", fill="both", expand=True, pady=10, padx=20)

    contentframe = tk.Frame(bezel_frame, background="#0096F7")
    contentframe.pack(side="top", anchor="n", fill="x", pady=10, padx=10)
    
    Results = Label(contentframe, text="Loaned Headsets", font=("ANTON", 25, "bold"), bg="#0096F7", fg="#E7E7E7")
    Results.grid(row=1, column=1, padx=(0,200))
    
    Remaining = Label(contentframe, text=f"Remaining: {returned_amount}", font=("ANTON", 15, "bold"), bg="#0096F7", fg="#E7E7E7")
    Remaining.grid(row=1, column=2, padx=(250,20))
    
    Issued = Label(contentframe, text=f"Issued: {issued_amount}", font=("ANTON", 15, "bold"), bg="#0096F7", fg="#E7E7E7")
    Issued.grid(row=1, column=3,padx=20, sticky=E)
    
    tableframe = tk.Frame(bezel_frame, background="#0096F7")
    tableframe.pack(side="top", anchor="n", fill="both", expand=True, pady=10, padx=10)
    
    
    def update_column_widths(event):
        
        frame_width = tableframe.winfo_width()
        column_width = frame_width // 8

        # Update column widths for each column in the Treeview
        for col in range(1, 8):
            tree.column('#' + str(col), width=column_width)
        
    tree = ttk.Treeview(tableframe, columns=('Date Issued', 'AshimaID', 'Issued To', 'Campaign', 'Room Number', 'Asset Tag', 'Issued By', 'Status'), show='headings')
    tree.heading('#1', text='Date Issued')
    tree.heading('#2', text='AshimaID')
    tree.heading('#3', text='Issued To')
    tree.heading('#4', text='Campaign')
    tree.heading('#5', text='Room Number')
    tree.heading('#6', text='Asset Tag')
    tree.heading('#7', text='Issued By')
    tree.heading('#8', text='Status')
    tree.pack(side="top", fill="both", expand=True)
    
    for col in range(1, 8):
        tree.column('#' + str(col), width=180)
    
    tableframe.bind("<Configure>", update_column_widths)
    
    def on_double_click(event):
        item = tree.selection()[0]  # Get selected item
        item_values = tree.item(item, "values")
        
        if item_values:
            asset_tag = item_values[5]
            ashima_id = item_values[1]# Assuming Asset Tag is at index 6 in values
            if asset_tag:
                recieved_by = RecievedEntry.get()
                check_asset_existence(asset_tag, recieved_by, ashima_id)
            else:
                messagebox.showerror("Error", "Asset Tag not found in selected row.")
        
    tree.bind("<Double-1>", on_double_click)
    
    
    
    def check_asset_existence(asset_tag, recieved_by, ashima_id):
        conn = connect_to_mysql()
        cursor = conn.cursor()

        if validate_entrytree():
            try:
                cursor.execute("SELECT * FROM sentrecords WHERE AssetTag = %s", (asset_tag,))
                result = cursor.fetchone()

                if result:
                    # Asset tag exists
                    confirm_return = messagebox.askyesno("Confirm Return", f"Return asset with tag: {asset_tag}?")
                    if confirm_return:
                        update_return_record(asset_tag, recieved_by, ashima_id)  # Update return record in the database
                        messagebox.showinfo("Success", "Asset returned successfully!")
                        SearchEntry.delete(0, 'end')
                        update_treeview()
                        open_return_window()
                        
                else:
                    # Asset tag not found
                    messagebox.showerror("Asset Not Found", f"Asset with tag '{asset_tag}' not found in loan records.")

            except Exception as e:
                messagebox.showerror("Error", f"Error checking asset tag: {str(e)}")
            finally:
                cursor.close()
                conn.close()
        else:
            messagebox.showinfo("Error", "Please Fill Out ReceivedBy!")
    
    def filter_treeview(event=None):
        # Get the current contents of the SearchEntry and strip it
        search_term = SearchEntry.get().strip().lower()
        # Clear the existing items in the Treeview
        tree.delete(*tree.get_children())

        # Fetch all loan records from the database
        records = fetch_loan_records()

        # If the search term is blank, display all records
        if not search_term:
            filtered_records = records
        else:
            # Filter records based on the search term in multiple columns
            filtered_records = set()
            for record in records:
                # Convert each relevant field to lower case and check for the search term
                if (search_term in str(record[0]).lower() or  # DateIssued
                    search_term in str(record[1]).lower() or  # AshimaID
                    search_term in str(record[2]).lower() or  # Issued To (Name)
                    search_term in str(record[3]).lower() or  # Campaign
                    search_term in str(record[4]).lower() or  # Room Number
                    search_term in str(record[5]).lower() or  # Asset Tag
                    search_term in str(record[6]).lower() or  # Issued By
                    search_term in str(record[7]).lower()):   # Status
                    filtered_records.add(record)

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
                record[7],  # Status
            )
            tree.insert('', 'end', values=values_to_display)

    # Bind the filter_treeview function to the KeyRelease event of the SearchEntry
    SearchEntry.bind("<KeyRelease>", filter_treeview)

    
    def fetch_loan_records():
        conn = connect_to_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT DateIssued, AshimaID, Name, Campaign, RoomNumber, AssetTag, IssuedBy, Status FROM sentrecords WHERE Status = 'Issued' ORDER BY ID DESC")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records
    
    def update_treeview():
        tree.delete(*tree.get_children())
        
        # Fetch latest records from the database
        records = fetch_loan_records()
        
        # Insert fetched records into the treeview
        for record in records:
            # Extract all columns from each record
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
            tree.insert('', 'end', values=values_to_display)
    
    update_treeview()
        


    def update_return_record(asset_tag, received_by, ashima_id):
        conn = connect_to_mysql()
        cursor = conn.cursor()
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Update the Status and ReceivedBy fields in SentRecords
            cursor.execute("UPDATE SentRecords SET Status = 'Returned', RecievedBy = %s, ReturnedDate = %s WHERE AssetTag = %s", (received_by, current_datetime, asset_tag))
            conn.commit()

            # Update the Flag in storage_list (assuming AssetTagID is the primary key)
            cursor.execute("UPDATE storage_list SET Flag = '1' WHERE AssetTagID = %s", (asset_tag,))
            conn.commit()
            
            cursor.execute("INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)", 
                           (ashima_user_global, user_name_global, f"Returned {ashima_id}'s Headset", asset_tag, current_datetime))
            conn.commit()

        except Exception as e:
            messagebox.showerror("Error", f"Error updating return record: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            
    all_items = get_all_items(tree)


    # Generate HTML content
    body = format_tree_data(all_items)
    html_body = body

    Home.config(state='disabled')
    HeadsetLoan.config(state='normal')
    Statistics.config(state="normal")
    Deletion.config(state="normal") 
    LogsButton.config(state="normal") 

def job():
    image_id = 1
    logo_data, logo_image = get_image_from_db(image_id)
    if logo_data and logo_image:
        print("Sending email...")
        create_csv(all_items, 'table_data.csv')
        send_email_with_attachment(
            #'ewsupport@eastwestbpo.com'
            #'pdd@eastwestbpo.com'
            sender_email='[eastwestcallcenter.com]',
            receiver_email='ewsupport@eastwestbpo.com',
            cc_emails=['pdd@eastwestbpo.com', 'operationsmanagers@eastwestbpo.com '],
            subject='Urgent: List of Unreturned Headsets',
            body=html_body,
            attachment_filename='table_data.csv',
            logo_data= logo_data,
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            login='jcarlos@eastwestbpo.com',
            password='ehls jqsp yruk wvsr'  # Use the app password generated by Google
        )
    

def Statistics_form():
    global StatisticsFrame, Statistics, GraphFrame, main


    StatisticsFrame = tk.Frame(main, background="#172f66", highlightbackground="#CBCBCB", highlightthickness=2, width=800, height=600)
    StatisticsFrame.pack(side=tk.RIGHT, anchor=tk.N, fill=tk.BOTH, expand=True)
    StatisticsFrame.pack_propagate(False)  # Prevent frame from resizing to fit content

    SearchFrame = tk.Frame(StatisticsFrame, background="#172f66", highlightbackground="#CBCBCB", highlightthickness=2)
    SearchFrame.pack(side=tk.TOP, anchor=tk.N, fill=tk.X, expand=True)
    
    Home.config(state='normal')
    HeadsetLoan.config(state='normal')
    Statistics.config(state="disabled")
    Deletion.config(state="normal")
    LogsButton.config(state="normal")
    
    def plot_headsets_graph(start_date, end_date):
        conn = connect_to_mysql()
        global GraphFrame
        try:
            with conn.cursor() as cursor:
                # Write your SQL query to retrieve data from the sentrecords table for the specified date range
                sql = f"""
                SELECT DATE(DateIssued) as DateIssued, 
                    SUM(CASE WHEN Status = 'Issued' THEN 1 ELSE 0 END) AS Issued, 
                    SUM(CASE WHEN Status = 'Returned' THEN 1 ELSE 0 END) AS Returned 
                FROM sentrecords 
                WHERE DATE(DateIssued) >= '{start_date}' 
                AND DATE(DateIssued) <= '{end_date}' 
                GROUP BY DATE(DateIssued)
                """
                cursor.execute(sql)
                result = cursor.fetchall()

                # Process the retrieved data
                data = pd.DataFrame(result, columns=['DateIssued', 'Issued', 'Returned'])
                data['DateIssued'] = pd.to_datetime(data['DateIssued'])
                data['Issued'] = pd.to_numeric(data['Issued'], errors='coerce')
                data['Returned'] = pd.to_numeric(data['Returned'], errors='coerce')
                data.dropna(subset=['Issued', 'Returned'], inplace=True)

                # Create the plot using matplotlib directly
                fig, ax = plt.subplots(figsize=(10, 6))
                width = 0.35  # the width of the bars

                x = data['DateIssued']
                indices = range(len(x))

                # Create bar plots
                ax.bar(indices, data['Issued'], width, label='Issued')
                ax.bar([i + width for i in indices], data['Returned'], width, label='Returned')

                ax.set_title(f'Comparison of Issued and Returned Headsets ({start_date} to {end_date})')
                ax.set_xlabel('Date')
                ax.set_ylabel('Count')
                ax.set_xticks([i for i in indices])  # Set x-ticks to the index positions
                ax.set_xticklabels(data['DateIssued'].dt.strftime('%Y-%m-%d'), rotation=360)
                ax.legend(title='Status')

                # Add data labels to the bars
                for p in ax.patches:
                    height = p.get_height()
                    if height > 0:
                        ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., p.get_y() + height),
                                    ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')

                # Ensure the x-axis labels are spaced equally
                ax.xaxis.set_major_locator(MaxNLocator(integer=True, prune=None))

                # Create a frame to contain the plot
                GraphFrame = tk.Frame(StatisticsFrame, highlightbackground="#CBCBCB", highlightthickness=2)
                GraphFrame.pack(fill=tk.BOTH, expand=FALSE)

                # Create a canvas widget for the plot
                canvas = FigureCanvasTkAgg(fig, master=GraphFrame)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)
                
                # Add navigation toolbar
                toolbar = NavigationToolbar2Tk(canvas, GraphFrame)
                toolbar.update()
                toolbar.pack(side=tk.BOTTOM, fill=tk.BOTH)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def destroy_frame(frame):
        global GraphFrame
        if frame:
            frame.destroy()
            GraphFrame = None
    
    def apply_dates():
        start_date = start_cal.get()
        end_date = end_cal.get()
        destroy_frame(GraphFrame)
        plot_headsets_graph(start_date, end_date)

    # Create DateEntry widgets for selecting start and end dates
    start_label = ttk.Label(SearchFrame, text="Start Date:")
    start_label.grid(column=1, row=1, sticky=tk.NW, padx=100, pady=(10,0))
    start_cal = DateEntry(SearchFrame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    start_cal.grid(column=1, row=2, sticky=tk.NW, padx=100, pady=10)

    end_label = ttk.Label(SearchFrame, text="End Date:")
    end_label.grid(column=3, row=1, sticky=tk.NW, padx=100, pady=(10,0))
    end_cal = DateEntry(SearchFrame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    end_cal.grid(column=3, row=2, sticky=tk.NW, padx=100, pady=10)

    apply_button = ttk.Button(SearchFrame, text="Apply", command=apply_dates)
    apply_button.grid(row=2, column=4, columnspan=2, sticky='nw')
    
class DataTable:
    def __init__(self, parent, columns, column_names):
        self.table = ttk.Treeview(parent, columns=columns, show='headings')
        
        for col in columns:
            self.table.column(col, anchor=tk.CENTER, width=120)
            self.table.heading(col, text=column_names[col], anchor=tk.CENTER)

    def populate_table(self):
        for i, row in enumerate(self.data_source):
            self.table.insert(parent='', index='end', iid=i, text='', values=row)

    def get_table(self):
        return self.table

def fetch_data(query):
    conn = connect_to_mysql(
    )
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

def delete_row_from_database(item_values, table_name, column_name):
    row_id = item_values[0]
    query = f"DELETE FROM {table_name} WHERE {column_name} = %s"

    conn = connect_to_mysql()
    cursor = conn.cursor()
    cursor.execute(query, (row_id,))
    conn.commit()
    
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)", 
                   (ashima_user_global, user_name_global, "Deleted", row_id, current_datetime))
    conn.commit()
    conn.close()

def on_row_double_click(event):
    table = event.widget
    selected_item = table.selection()[0]
    item_values = table.item(selected_item, "values")

    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {item_values}?"):
        for table_data in tables:
            if table_data["table"].get_table() == table:
                delete_row_from_database(item_values, table_data["table_name"], list(table_data["column_names"].values())[0])
                break
        table.delete(selected_item)

# Sample SQL queries for the tables


def Deletion_form():
    global DeletionFrame
    global Deletion
    
    query_empinfo = "SELECT AshimaID, FirstName FROM empinfo"
    query_tblcampaign = "SELECT CampaignName, Id FROM tblcampaign"
    query_tblroom = "SELECT RoomNumber, Id FROM tblroom"
    query_storage_list = "SELECT AssetTagID, Description FROM storage_list"
    query_userinfo = "SELECT AshimaID, Name FROM admin_login"

    # Fetching data from the database
    empinfo = fetch_data(query_empinfo)
    tblcampaign = fetch_data(query_tblcampaign)
    tblroom = fetch_data(query_tblroom)
    storage_list = fetch_data(query_storage_list)
    userinfo = fetch_data(query_userinfo)

    DeletionFrame = tk.Frame(main, background="#172f66", highlightbackground="#CBCBCB", highlightthickness=2, width=800, height=600)
    DeletionFrame.pack(side=tk.RIGHT, anchor=tk.N, fill=tk.BOTH, expand=True)
    
    midframe = tk.Frame(DeletionFrame, background="#172f66")
    midframe.pack(side="top", anchor="n", fill="x", padx=20)
    
    Searchbar = tk.Label(midframe, text="Search:", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    Searchbar.grid(row=1, column=0, sticky="nw", pady=10, padx=500)
    
    SearchEntry = tk.Entry(midframe, font=20)
    SearchEntry.grid(row=2, column=0, columnspan=2, sticky="nw", padx=500)
    SearchEntry.focus()
    
    bezel_frame = tk.Frame(DeletionFrame, background="#000000", highlightbackground="#0096F7", highlightthickness=4, bd=0)
    bezel_frame.pack(side="top", anchor="n", fill="both", expand=True, pady=10, padx=20)

    contentframe = tk.Frame(bezel_frame, background="#0096F7")
    contentframe.pack(side="top", anchor="n", fill="x", pady=10, padx=10)
    
    User = tk.Label(contentframe, text="Admins", font=("ANTON", 15, "bold"), bg="#0096F7", fg="#E7E7E7")
    User.pack(side=LEFT, ipadx=70)
    
    Employee = tk.Label(contentframe, text="Employee", font=("ANTON", 15, "bold"), bg="#0096F7", fg="#E7E7E7")
    Employee.pack(side=LEFT, ipadx=70)
    
    Campaigns = tk.Label(contentframe, text="Campaigns", font=("ANTON", 15, "bold"), bg="#0096F7", fg="#E7E7E7")
    Campaigns.pack(side=LEFT, ipadx=70)
    
    Rooms = tk.Label(contentframe, text="Rooms", font=("ANTON", 15, "bold"), bg="#0096F7", fg="#E7E7E7")
    Rooms.pack(side=LEFT, ipadx=70)
    
    Headsets = tk.Label(contentframe, text="Headsets", font=("ANTON", 15, "bold"), bg="#0096F7", fg="#E7E7E7")
    Headsets.pack(side=LEFT, ipadx=70)
    
    tableframe = tk.Frame(bezel_frame, background="#0096F7")
    tableframe.pack(side="top", anchor="n", fill="both", expand=True, pady=10, padx=10)
    
    tableframe.columnconfigure(0, weight=1)
    tableframe.columnconfigure(1, weight=1)
    tableframe.columnconfigure(2, weight=1)
    tableframe.columnconfigure(3, weight=1)
    tableframe.columnconfigure(4, weight=1)
    tableframe.rowconfigure(0, weight=1)
    
    global tables
    tables = [
        {"data": userinfo, "columns": ("col1", "col2"), "column_names": {"col1": "AshimaID", "col2": "User Name"}, "table_name": "admin_login"},
        {"data": empinfo, "columns": ("col1", "col2"), "column_names": {"col1": "AshimaID", "col2": "Employee Name"}, "table_name": "empinfo"},
        {"data": tblcampaign, "columns": ("col1", "col2"), "column_names": {"col1": "Campaigns", "col2": "Id"}, "table_name": "tblcampaign"},
        {"data": tblroom, "columns": ("col1", "col2"), "column_names": {"col1": "Rooms", "col2": "Id"}, "table_name": "tblroom"},
        {"data": storage_list, "columns": ("col1", "col2"), "column_names": {"col1": "AssetTagID", "col2": "Description"}, "table_name": "storage_list"}
    ]

    table_instances = []

    for i, table_data in enumerate(tables):
        table = DataTable(tableframe, table_data["columns"], table_data["column_names"])
        table.data_source = table_data["data"]  # Set the data source for the table
        table.populate_table()  # Populate the table with data from data_source
        table.get_table().grid(row=0, column=i, sticky="nsew")
        table.get_table().bind("<Double-1>", on_row_double_click)  # Bind double-click event
        table_data["table"] = table  # Store table instance for later reference
        table_instances.append(table)

    for i in range(5):  # Adjust column weights for all columns
        tableframe.columnconfigure(i, weight=1)
    
    tables_data = {table.get_table(): table.data_source for table in table_instances}

    def filter_treeview(event=None):
        search_term = SearchEntry.get().strip().lower()

        for table, data in tables_data.items():
            for item in table.get_children():
                table.delete(item)

            if not search_term:
                filtered_records = data
            else:
                filtered_records = set()
                for record in data:
                    if any(search_term in str(field).lower() for field in record):
                        filtered_records.add(record)

            for record in filtered_records:
                table.insert("", "end", values=record)
    
    SearchEntry.bind("<KeyRelease>", filter_treeview)

    
    Home.config(state='normal')
    HeadsetLoan.config(state='normal')
    Statistics.config(state="normal")
    Deletion.config(state="disabled")
    LogsButton.config(state="normal")
    
def Logs():
    global LogsFrame
    global user_name_global
    global body
    global html_body
    
    
    def export_to_csv():
        selected_items = tree.selection()
        if selected_items:
            # Prompt the user to choose the file path and name for saving the CSV file
            file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')],
                                                    initialfile='exported_data', title='Save CSV file')
            if file_path:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    # Write header row
                    writer.writerow(['Date Issued','AshimaID','Issued To','Campaign','Room Number','Asset Tag','Issued By', 'Status'])
                    # Write selected items to CSV
                    for item in selected_items:
                        item_text = tree.item(item, 'values')
                        writer.writerow(item_text)
                messagebox.showinfo('Success', 'CSV file exported successfully.')
        else:
            messagebox.showwarning('No Selection', 'Please select items to export.')

    def export_all_to_csv():
        # Prompt the user to choose the file path and name for saving the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')],
                                                    initialfile='exported_data', title='Save CSV file')
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write header row
                writer.writerow(['Date Issued','AshimaID','Issued To','Campaign','Room Number','Asset Tag','Issued By', 'Status'])
                # Write all items in the treeview to CSV
                for item in tree.get_children():
                    item_text = tree.item(item, 'values')
                    writer.writerow(item_text)
            messagebox.showinfo('Success', 'All data exported to CSV successfully.')
            
    LogsFrame = tk.Frame(main, background="#172f66", highlightbackground="#CBCBCB", highlightthickness=2)
    LogsFrame.pack(side=RIGHT, anchor=N, fill=BOTH, expand=TRUE)
    
    
    midframe = tk.Frame(LogsFrame, background="#172f66")
    midframe.pack(side="top", anchor="n", fill="x", padx=20)
    
    Searchbar = Label(midframe, text="Search:", font=("ANTON", 12, "bold"), bg="#172f66", fg="#FFFFFF")
    Searchbar.grid(row=1, column=0, sticky="nw",pady=10)
    
    SearchEntry = Entry(midframe, font=20)
    SearchEntry.grid(row=2, column=0, columnspan=2, sticky="nw")
    SearchEntry.focus()
    
    export_all_button = tk.Button(midframe, text= "Export All", command=export_all_to_csv, bg="#172f66", fg="#FFFFFF", font=("ANTON", 12, "bold"))
    export_all_button.grid(row=2, column=3, sticky="nw", padx=(300,0))

    export_button = tk.Button(midframe, text='Export Selected', bg="#172f66", fg="#FFFFFF", command=export_to_csv, font=("ANTON", 12, "bold"))
    export_button.grid(row=2, column=4, sticky="nw")
    
    bezel_frame = tk.Frame(LogsFrame, background="#000000", highlightbackground="#0096F7", highlightthickness=4, bd=0)
    bezel_frame.pack(side="top", anchor="n", fill="both", expand=True, pady=10, padx=20)

    contentframe = tk.Frame(bezel_frame, background="#0096F7")
    contentframe.pack(side="top", anchor="n", fill="x", pady=10, padx=10)
    
    Results = Label(contentframe, text="Action Logs", font=("ANTON", 25, "bold"), bg="#0096F7", fg="#E7E7E7")
    Results.grid(row=1, column=1, padx=(0,200))
    
    tableframe = tk.Frame(bezel_frame, background="#0096F7")
    tableframe.pack(side="top", anchor="n", fill="both", expand=True, pady=10, padx=10)
    
    
    def update_column_widths(event):
        
        frame_width = tableframe.winfo_width()
        column_width = frame_width // 5

        # Update column widths for each column in the Treeview
        for col in range(1, 5):
            tree.column('#' + str(col), width=column_width)
        
    tree = ttk.Treeview(tableframe, columns=('AshimaID', 'Name', 'Performed', 'Item', 'Date'), show='headings')
    tree.heading('#1', text='AshimaID')
    tree.heading('#2', text='Name')
    tree.heading('#3', text='Performed')
    tree.heading('#4', text='Item')
    tree.heading('#5', text='Date')
    tree.pack(side="top", fill="both", expand=True)
    
    for col in range(1, 5):
        tree.column('#' + str(col), width=180)
    
    tableframe.bind("<Configure>", update_column_widths)

    
    def filter_treeview(event=None):
        # Get the current contents of the SearchEntry and strip it
        search_term = SearchEntry.get().strip().lower()
        # Clear the existing items in the Treeview
        tree.delete(*tree.get_children())

        # Fetch all loan records from the database
        records = fetch_loan_records()

        # If the search term is blank, display all records
        if not search_term:
            filtered_records = records
        else:
            # Filter records based on the search term in multiple columns
            filtered_records = set()
            for record in records:
                # Convert each relevant field to lower case and check for the search term
                if (search_term in str(record[0]).lower() or  
                    search_term in str(record[1]).lower() or 
                    search_term in str(record[2]).lower() or 
                    search_term in str(record[3]).lower() or  
                    search_term in str(record[4]).lower()):   
                    filtered_records.add(record)

        # Insert filtered records into the Treeview
        for record in filtered_records:
            values_to_display = (
                record[0],  # DateIssued
                record[1],  # AshimaID
                record[2],  # Issued To (Name)
                record[3],  # Campaign
                record[4]
            )
            tree.insert('', 'end', values=values_to_display)

    # Bind the filter_treeview function to the KeyRelease event of the SearchEntry
    SearchEntry.bind("<KeyRelease>", filter_treeview)

    
    
    
    def fetch_loan_records():
        conn = connect_to_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT AshimaID, Name, Performed, Item, Date FROM tbllogs ORDER BY ID DESC")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records
    
    def update_treeview():
        tree.delete(*tree.get_children())
        
        # Fetch latest records from the database
        records = fetch_loan_records()
        
        # Insert fetched records into the treeview
        for record in records:
            # Extract all columns from each record
            values_to_display = (
                record[0],  # AshimaID
                record[1],  # Name
                record[2],  # Performed
                record[3],  # Item
                record[4]   # Date
            )
            tree.insert('', 'end', values=values_to_display)
    
    update_treeview()
        

    Home.config(state='normal')
    HeadsetLoan.config(state='normal')
    Statistics.config(state="normal")
    Deletion.config(state="normal")
    LogsButton.config(state="disabled")
    
def AddCampaign():
    
    def validate_entry():
        required_fields = [
        CampaignEntry.get().strip(),
        ]
        if all(required_fields):
            return True
        else:
            print("Entry cannot be empty!")
            return False  
        
    def submitassets():
        Campaigns = CampaignEntry.get()
        
        if validate_entry():
            # Check if the asset already exists
            if not asset_already_exists(Campaigns):
                # Asset does not exist, proceed with upload
                upload_to_AssestList(Campaigns)
                messagebox.showinfo("Success", "Asset Uploaded Successfully!")
                CampaignEntry.delete(0, 'end')
                CampaignFrame.destroy()
                open_loan_window()
            else:
                # Asset already exists, show error message
                messagebox.showerror("Error", f"Asset {Campaigns} already exists in the table!", parent=CampaignFrame)
                CampaignEntry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Please Fill All Entry Fields!", parent=CampaignFrame)
    
    def asset_already_exists(Campaignlist):
        conn = connect_to_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT CampaignName FROM tblcampaign WHERE CampaignName = %s", (Campaignlist,))
        existing_asset = cursor.fetchone()
        cursor.close()
        conn.close()
        return existing_asset is not None

    def upload_to_AssestList(Campaigns):
        conn = connect_to_mysql()
        cursor = conn.cursor()

        try:
            # Insert new asset into the table
            cursor.execute("INSERT INTO tblcampaign (CampaignName) VALUES (%s)",
                        (Campaigns))
            conn.commit()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)", 
                           (ashima_user_global, user_name_global, "Added Campaign", Campaigns, current_datetime))
            conn.commit()
        except Exception as e:
            # Handle any database errors
            conn.rollback()
            messagebox.showerror("Error", f"Failed to upload asset: {e}", parent=CampaignFrame)
        finally:
            cursor.close()
            conn.close()
        
    
    CampaignFrame = tk.Toplevel()
    CampaignFrame.title("Add Campaign")
    window_width = 290
    window_height = 200
    screen_width = main.winfo_screenwidth()
    screen_height = main.winfo_screenheight()
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 3
    CampaignFrame.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    
    centerframe = tk.Frame(CampaignFrame, background="#172f66")
    centerframe.pack(side="top", anchor="n", fill= "both", expand=TRUE)
    
    Campaigns = Label(centerframe, text="Campaign*", font=("ANTON", 15, "bold"),bg="#172f66", fg="#FFFFFF" )
    Campaigns.grid(column=1, row=1, padx=50, pady=(20,0))
    
    vcmdcampaign = (centerframe.register(on_validatecampaign), '%P')
    
    CampaignEntry = Entry(centerframe, validate="key", validatecommand=vcmdcampaign, font=15)
    CampaignEntry.grid(column=1, row=2, sticky=NW, padx=50, pady=30)
    CampaignEntry.focus()
    
    Upload =  Button(centerframe, text="Submit", command=submitassets, bg="#172f66", fg="#FFFFFF", font=("ANTON", 10, "bold"))
    Upload.grid(row=3, column=1, pady=30, padx=50)
    
    HeadsetFrame.grid_rowconfigure(1, weight=1)
    HeadsetFrame.grid_columnconfigure(1, weight=1)
    
def AddRoom():

    def validate_entry():
        required_fields = [
        RoomEntry.get().strip(),
        ]
        if all(required_fields):
            return True
        else:
            print("Entry cannot be empty!")
            return False  
        
    def submitassets():
        Rooms = RoomEntry.get()
        
        if validate_entry():
            # Check if the asset already exists
            if not asset_already_exists(Rooms):
                # Asset does not exist, proceed with upload
                upload_to_AssestList(Rooms)
                messagebox.showinfo("Success", "Asset Uploaded Successfully!")
                RoomEntry.delete(0, 'end')
                RoomFrame.destroy()
                open_loan_window()
            else:
                # Asset already exists, show error message
                messagebox.showerror("Error", f"Asset {Rooms} already exists in the table!", parent=RoomFrame)
                RoomEntry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Please Fill All Entry Fields!", parent=RoomFrame)
    
    def asset_already_exists(Roomlist):
        conn = connect_to_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT RoomNumber FROM tblroom WHERE RoomNumber = %s", (Roomlist,))
        existing_asset = cursor.fetchone()
        cursor.close()
        conn.close()
        return existing_asset is not None

    def upload_to_AssestList(Rooms):
        conn = connect_to_mysql()
        cursor = conn.cursor()

        try:
            # Insert new asset into the table
            cursor.execute("INSERT INTO tblroom (RoomNumber) VALUES (%s)",
                        (Rooms))
            conn.commit()
            
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)", 
                           (ashima_user_global, user_name_global, "Added Room", Rooms, current_datetime))
            conn.commit()
        except Exception as e:
            # Handle any database errors
            conn.rollback()
            messagebox.showerror("Error", f"Failed to upload asset: {e}", parent=RoomFrame)
        finally:
            cursor.close()
            conn.close()
            
    
    
    RoomFrame = tk.Toplevel()
    RoomFrame.title("Add Rooms")
    window_width = 290
    window_height = 200
    screen_width = main.winfo_screenwidth()
    screen_height = main.winfo_screenheight()
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 3
    RoomFrame.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    
    centerframe = tk.Frame(RoomFrame, background="#172f66")
    centerframe.pack(side="top", anchor="n", fill= "both", expand=TRUE)
    
    Rooms = Label(centerframe, text="Room*", font=("ANTON", 15, "bold"),bg="#172f66", fg="#FFFFFF" )
    Rooms.grid(column=1, row=1, padx=50, pady=(20,0))
    
    vcmdroom = (centerframe.register(on_validateroom), '%P')
    
    RoomEntry = Entry(centerframe, validate="key", validatecommand=vcmdroom, font=15)
    RoomEntry.grid(column=1, row=2, sticky=NW, padx=50, pady=30)
    RoomEntry.focus()
    
    Upload =  Button(centerframe, text="Submit", command=submitassets, bg="#172f66", fg="#FFFFFF", font=("ANTON", 10, "bold"))
    Upload.grid(row=3, column=1, pady=30, padx=50)
    
    HeadsetFrame.grid_rowconfigure(1, weight=1)
    HeadsetFrame.grid_columnconfigure(1, weight=1)
    
def Addheadset():
    global HeadsetFrame
    
    def validate_entry():
        required_fields = [
        AssetEntry.get().strip(),
        DesEntry.get().strip()
        ]
        if all(required_fields):
            return True
        else:
            print("Entry cannot be empty!")
            return False  
        
    def submitassets():
        Assets = AssetEntry.get()
        Descript = DesEntry.get()
        
        if validate_entry():
            # Check if the asset already exists
            if not asset_already_exists(Assets):
                # Asset does not exist, proceed with upload
                upload_to_AssestList(Assets, Descript)
                messagebox.showinfo("Success", "Asset Uploaded Successfully!")
                AssetEntry.delete(0, 'end')
                DesEntry.delete(0, 'end')
                HeadsetFrame.destroy()
                open_loan_window()
            else:
                # Asset already exists, show error message
                messagebox.showerror("Error", f"Asset {Assets} already exists in the table!", parent=HeadsetFrame)
                AssetEntry.delete(0, 'end')
                DesEntry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Please Fill All Entry Fields!", parent=HeadsetFrame)
    
    def asset_already_exists(asset_id):
        conn = connect_to_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT AssetTagID FROM storage_list WHERE AssetTagID = %s", (asset_id,))
        existing_asset = cursor.fetchone()
        cursor.close()
        conn.close()
        return existing_asset is not None

    def upload_to_AssestList(Assets, Descript):
        conn = connect_to_mysql()
        cursor = conn.cursor()

        try:
            # Insert new asset into the table
            cursor.execute("INSERT INTO storage_list (AssetTagID, Description, Flag) VALUES (%s, %s, '1')",
                        (Assets, Descript))
            conn.commit()
            
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) VALUES (%s, %s, %s, %s, %s)", 
                           (ashima_user_global, user_name_global, "Added Headset", Assets, current_datetime))
            conn.commit()
            
        except Exception as e:
            # Handle any database errors
            conn.rollback()
            messagebox.showerror("Error", f"Failed to upload asset: {e}", parent=HeadsetFrame)
        finally:
            cursor.close()
            conn.close()
        
    
    HeadsetFrame = tk.Toplevel()
    HeadsetFrame.title("Add AssetTags")
    window_width = 570
    window_height = 200
    screen_width = main.winfo_screenwidth()
    screen_height = main.winfo_screenheight()
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 3
    HeadsetFrame.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    
    centerframe = tk.Frame(HeadsetFrame, background="#172f66")
    centerframe.pack(side="top", anchor="n", fill= "both", expand=TRUE)
    
    AssetTags = Label(centerframe, text="AssetTags*", font=("ANTON", 15, "bold"),bg="#172f66", fg="#FFFFFF" )
    AssetTags.grid(column=1, row=1, sticky=NW, padx=50, pady=(20,0))
    
    vcmdasset = (centerframe.register(on_validateasset), '%P')
    
    AssetEntry = Entry(centerframe, validate="key", validatecommand=vcmdasset, font=15)
    AssetEntry.grid(column=1, row=2, sticky=NW, padx=50, pady=30)
    AssetEntry.focus()
    
    Description = Label(centerframe, text="Description*", font=("ANTON", 15, "bold"),bg="#172f66", fg="#FFFFFF" )
    Description.grid(column=3, row=1, sticky=NW, padx=50, pady=(20,0))
    
    DesEntry = Entry(centerframe, font=15)
    DesEntry.grid(column=3, row=2, sticky=NW, padx=50, pady=30)
    
    Upload =  Button(centerframe, text="Submit", command=submitassets, bg="#172f66", fg="#FFFFFF", font=("ANTON", 10, "bold"))
    Upload.grid(row=11, column=2, columnspan=2, pady=30, sticky='nw')
    
    HeadsetFrame.grid_rowconfigure(1, weight=1)
    HeadsetFrame.grid_columnconfigure(1, weight=1)
    
def admin_login_window():
    admin_window=Toplevel()
    admin_window.title("Return Form")
    admin_window.config(background="#172f66")
    
    topframe = tk.Frame(admin_window, background="#172f66")
    topframe.pack(side="top", anchor="n", fill= "x")

    
    
    def toggle_fullscreen(event=None):
        # Toggle fullscreen mode
        fullscreen = not admin_window.attributes("-fullscreen")
        admin_window.attributes("-fullscreen", fullscreen)
        
    
    admin_window.bind("<F11>", toggle_fullscreen)
    admin_window.attributes('-fullscreen', True)
    
    image_id = 1  # Specify the image ID you want to retrieve
    logo_data, logo_image = get_image_from_db(image_id)
    if logo_data and logo_image:
        # Resize the image
        logosize = logo_image.resize((500, 200))
        logon = ImageTk.PhotoImage(logosize)

    
    Loan = Label(topframe, text = "Admin Office", font=("ANTON", 35, "bold"),bg="#172f66", fg="#f46206")
    Loan.pack(side="left", anchor="nw", pady=50, padx = 40)
    
    lbl1 = Label(topframe, image=logon, bg="#172f66")
    lbl1.image = logon
    lbl1.pack(side="right", anchor="ne")
    
    midframe = tk.Frame(admin_window, background="#172f66")
    midframe.pack(side="top", anchor="n", fill= "x")
    
    Assettags = Button(midframe, text="Add/Remove AsseetTags",  font=("ANTON", 25, "bold"),bg="#172f66", fg="#f46206")
    Assettags.grid(row=1, column=1, sticky=NW, padx=300)
    
    Admins = Button(midframe, text="Add/Remove Admins",  font=("ANTON", 25, "bold"),bg="#172f66", fg="#f46206")
    Admins.grid(row=2, column=1, sticky=NW, padx=300, pady=100)
    

    
    
    
    
def login_prompt():
    #testing
    
    label = Label
    
def open_login_window():
    LoginWindow = tk.Toplevel()
    LoginWindow.title("Login")
    LoginWindow.config(background="#172f66")
    LoginWindow.resizable(False, False)
    window_width = 400
    window_height = 450
    screen_width = LoginWindow.winfo_screenwidth()
    screen_height = LoginWindow.winfo_screenheight()
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 3
    LoginWindow.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    def sign_up():
        # Create the sign-up window
        SignWindow = tk.Toplevel()
        SignWindow.title("Sign Up")
        SignWindow.config(background="#172f66")
        SignWindow.resizable(False, False)
        window_width = 300
        window_height = 200
        screen_width = SignWindow.winfo_screenwidth()
        screen_height = SignWindow.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 3
        SignWindow.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        
        vcmd = (SignWindow.register(on_validate), '%P')
        vcmdname = (SignWindow.register(on_validatename), '%P')
        vcmdpass = (SignWindow.register(on_validatepass), '%P')
        
    
        # Create entry fields for username, password, and Ashima
        Ashima_label = tk.Label(SignWindow, text="AshimaID:", bg="#172f66", fg="white")
        Ashima_label.pack()
        Ashima_entry = tk.Entry(SignWindow, validate="key", validatecommand=vcmd)
        Ashima_entry.pack()
        
        username_label = tk.Label(SignWindow, text="Username:", bg="#172f66", fg="white")
        username_label.pack()
        username_entry = tk.Entry(SignWindow, validate="key", validatecommand=vcmdname)
        username_entry.pack()

        password_label = tk.Label(SignWindow, text="Password:", bg="#172f66", fg="white")
        password_label.pack()
        password_entry = tk.Entry(SignWindow, show="*", validate="key", validatecommand=vcmdpass)
        password_entry.pack()

        def validate_entry():
            required_fields = [
                Ashima_entry.get().strip(),
                username_entry.get().strip(),
                password_entry.get().strip()
            ]
            if all(required_fields):
                return True
            else:
                print("Entry cannot be empty!")
                return False 
        
        # Function to handle sign-up submission
        def submit():
            # Retrieve input values
            username = username_entry.get()
            password = password_entry.get()
            ashima = Ashima_entry.get()
            
            conn = connect_to_mysql()
            # Create a cursor object to execute SQL queries
            cursor = conn.cursor()

            if validate_entry():
                # SQL statement to insert data into admin_login table
                sql = "INSERT INTO admin_login (Name, AshimaID, Password, Privilege) VALUES (%s, %s, %s, '3')"
                # Tuple containing values to be inserted
                val = (username, ashima, password)

                try:
                    # Execute the SQL query
                    cursor.execute(sql, val)

                    # Commit changes to the database
                    conn.commit()
                    
                    # Print a success message
                    print("Data inserted successfully into admin_login table.")
                    messagebox.showinfo("Success", "New User has been Created!", parent=SignWindow)
                    # Close the sign-up window
                    SignWindow.destroy()
                except Exception as e:
                    # Rollback changes if there's an error
                    conn.rollback()
                    # Print error message
                    print("Error inserting data into admin_login table:", e)
                finally:
                    # Close cursor and database connection
                    cursor.close()
                    conn.close()
            else:
                messagebox.showinfo("Error", "Please Fill Out All Entry Fields!", parent=SignWindow)
                
        # Button to submit sign-up information
        submit_button = tk.Button(SignWindow, text="Submit", bg="#172f66", fg="#FFFFFF", command=submit)
        submit_button.pack(pady=10)
        
    # Create custom title bar
    title_bar = tk.Frame(LoginWindow, bg='#172f66', relief='raised', bd=0)
    title_bar.pack(fill=tk.X)

    title_label = tk.Button(title_bar, text="Sign Up", bg='#172f66', fg='white', command=sign_up, font=("Anton", 12, "bold"))
    title_label.pack(side=tk.LEFT, padx=10, pady=5)


    # Allow the window to be moved by dragging the title bar
    def start_move(event):
        LoginWindow.x = event.x
        LoginWindow.y = event.y

    def stop_move(event):
        LoginWindow.x = None
        LoginWindow.y = None

    def on_move(event):
        deltax = event.x - LoginWindow.x
        deltay = event.y - LoginWindow.y
        x = LoginWindow.winfo_x() + deltax
        y = LoginWindow.winfo_y() + deltay
        LoginWindow.geometry(f"+{x}+{y}")

    title_bar.bind('<Button-1>', start_move)
    title_bar.bind('<ButtonRelease-1>', stop_move)
    title_bar.bind('<B1-Motion>', on_move)

    # Welcome message
    Welcome = tk.Label(LoginWindow, text="Welcome!", bg="#172f66", fg="#FFFFFF", font=("Anton", 20, "bold"))
    Welcome.pack(padx=10, pady=5)
    Warning = tk.Label(LoginWindow, text="Please Login \nto access \nLoaning and Returning Forms", bg="#172f66", fg="#FFFFFF", font=("Anton", 12, "bold"))
    Warning.pack(padx=10, pady=15)

    # Widgets for login window
    Ashima_label = tk.Label(LoginWindow, text="AshimaID:", bg="#172f66", fg="#FFFFFF", font=("Anton", 12, "bold"))
    Ashima_label.pack(pady=5)
    Ashima_entry = tk.Entry(LoginWindow)
    Ashima_entry.pack()
    Ashima_entry.focus()

    password_label = tk.Label(LoginWindow, text="Password:", bg="#172f66", fg="#FFFFFF", font=("Anton", 12, "bold"))
    password_label.pack(pady=5)
    password_entry = tk.Entry(LoginWindow, show="*")
    password_entry.pack(pady=(0,10))

    def check_credentials(event=None):
        global user_name_global
        global ashima_user_global
        
        ashima = Ashima_entry.get()
        password = password_entry.get()
        if ashima and password:
            ashima_user_global = ashima
            user_info = check_user_credentials(ashima, password)
            if user_info:
                privilege_level = user_info[4]
                if privilege_level == 2:
                    user_name = user_info[1]
                    if user_name:
                        user_name_global = user_name
                        LoginWindow.destroy()
                        main.state('normal')
                        main.lift()
                        main.focus_force()
                        usernameb.config(state='normal', text=f"Welcome, {user_name}")
                        level2()
                        Return_form()
                        return user_info
                elif privilege_level == 3:
                    user_name = user_info[1]
                    if user_name:
                        user_name_global = user_name
                        LoginWindow.destroy()
                        main.state('normal')  # Enable main window
                        main.lift()
                        main.focus_force()
                        usernameb.config(state='normal', text=f"Welcome, {user_name}")
                        level3()
                        Return_form()
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

    login_button = tk.Button(LoginWindow, text="Log In", bg="#172f66", fg="#FFFFFF", command=check_credentials, font=("Anton", 13, "bold"))
    login_button.place(relx=0.3, rely=0.9, anchor="center")

    def cancel_login():
        LoginWindow.destroy()
        main.destroy()

    cancel_button = tk.Button(LoginWindow, text="Cancel", bg="#172f66", fg="#FFFFFF", command=cancel_login, font=("Anton", 13, "bold"))
    cancel_button.place(relx=0.7, rely=0.9, anchor="center")

    # Bind Enter key to login button
    LoginWindow.bind('<Return>', check_credentials)
    

def get_user_name(ashima):
    conn = connect_to_mysql()
    cursor = conn.cursor()

    # Execute SQL query to retrieve user's Name
    cursor.execute("SELECT Name FROM admin_login WHERE AshimaID = %s", (ashima,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result[0]
    else:
        return None
    
def check_user_credentials(ashima, password):
    conn = connect_to_mysql()
    cursor = conn.cursor()

    # Execute SQL query to check user credentials
    cursor.execute("SELECT * FROM admin_login WHERE AshimaID = %s AND PASSWORD = %s", (ashima, password))
    user_info = cursor.fetchone()

    cursor.close()
    conn.close()

    return user_info

def get_user_privilege_level(ashima):
    conn = connect_to_mysql()
    cursor = conn.cursor()

    # Execute SQL query to retrieve user privilege level
    cursor.execute("SELECT Privilege FROM admin_login WHERE AshimaID = %s", (ashima,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result[0]
    else:
        return 0
    
def logout():
    # Display a confirmation message box
    confirmed = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    if confirmed:
        usernameb.config(text="", state='disabled')
        open_login_window()
        destroy_frame(ReturnFrame)
        destroy_frame(StatisticsFrame)
        destroy_frame(LoanFrame)
        destroy_frame(DeletionFrame)
        destroy_frame(LogsFrame)
        main.state('withdrawn')

def destroybuttons():
    global HeadsetLoan, HeadsetLoan2
    global Statistics
    global Deletion
    global LogsButton
    
    # Destroy existing buttons if they exist
    if HeadsetLoan:
        HeadsetLoan.destroy()
        HeadsetLoan = None
    if Statistics:
        Statistics.destroy()
        Statistics = None
    if Deletion:
        Deletion.destroy()
        Deletion = None
    if LogsButton:
        LogsButton.destroy()
        LogsButton = None
    
        
image_id = 2  # Specify the image ID you want to retrieve
logo_data, logo_image = get_image_from_db(image_id)
if logo_data and logo_image:
    # Resize the image
    logosize = logo_image.resize((500, 200))
    logon = ImageTk.PhotoImage(logosize)


logo_data, logo_image = get_image_from_db(image_id)
if logo_data and logo_image:
    img_width, img_height = logo_image.size
    window_width, window_height = 1200, 1200
    scale = max(window_width / img_width, window_height / img_height)
    img = logo_image.resize((int(img_width * scale), int(img_height * scale)))
    background_image = ImageTk.PhotoImage(img)



background_label = tk.Label(main, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

topframe = tk.Frame(main, background="#172f66")
topframe.pack(side=TOP, anchor=N, fill=X)

sideframe = tk.Frame(main, background="#172f66")
sideframe.pack(side=TOP, anchor=N, fill=X)

Home = Button(topframe, image=logon, command=open_return_window, relief=tk.FLAT, bg="#172f66")
Home.image = logon
Home.pack(side="left", anchor="nw")

usernameb = Button(topframe, text= "", bg="#172f66", fg="#FFFFFF", command= logout, relief=tk.FLAT, state='disabled', font=("ANTON", 15, "bold"))
usernameb.pack(side="right", anchor="ne", pady=30)

HeadsetLoan = Button(sideframe, text= "Headset Loan Form", command=open_loan_window, relief=tk.RAISED , bg="#172f66", fg="#FF5900", font=("ANTON", 15, "bold"))
HeadsetLoan.pack(side="left", anchor="n")

#HeadsetLoanr = Button(sideframe, text= "Headset Return Form", command=open_return_window, relief=tk.RAISED, bg="#172f66", fg="#FF5900", font=("ANTON", 15, "bold"))
#HeadsetLoanr.pack(side="left", anchor="n")

Statistics = Button(sideframe, text= "Statistics", command=open_statistics_window, relief=tk.RAISED , bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
Statistics.pack(side="left", anchor="n")

Deletion = Button(sideframe, text= "Deletion", command=open_deletion_window, relief=tk.RAISED , bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
Deletion.pack(side="left", anchor="n")

LogsButton = Button(sideframe, text= "Logs", command=open_logs_window, relief=tk.RAISED , bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
LogsButton.pack(side="left", anchor="n")

def level3():
    global HeadsetLoan
    global Statistics
    global Deletion
    global LogsButton
    
    print("Calling level3()")
    
    destroybuttons()
    
    HeadsetLoan = Button(sideframe, text= "Headset Loan Form", command=open_loan_window, relief=tk.RAISED , bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
    HeadsetLoan.pack(side="left", anchor="n")
    
    Statistics = Button(sideframe, text= "Statistics", command=open_statistics_window, relief=tk.RAISED , bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
    Statistics.pack(side="left", anchor="n")
    
    Deletion = Button(sideframe, text= "Deletion", command=open_deletion_window, relief=tk.RAISED , bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
    Deletion.pack(side="left", anchor="n")
    
    LogsButton = Button(sideframe, text= "Logs", command=open_logs_window, relief=tk.RAISED , bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
    LogsButton.pack(side="left", anchor="n")

    #HeadsetLoanr = Button(sideframe, text= "Headset Return Form", command=open_return_window, relief=tk.RAISED, bg="#172f66", fg="#FF5900", font=("ANTON", 15, "bold"))
    #HeadsetLoanr.pack(side="left", anchor="n")
    
def level2():
    global HeadsetLoan
    print("Calling level2()")
    
    destroybuttons()
        
    HeadsetLoan = Button(sideframe, text= "Headset Loan Form", command=open_loan_window, relief=tk.RAISED , bg="#172f66", fg="#FFFFFF", font=("ANTON", 15, "bold"))
    HeadsetLoan.pack(side="left", anchor="n")



def run_schedule(exit_event):
    global schedule_thread
    schedule.every().day.at("16:00").do(job)
    while not exit_event.is_set():  # Check if exit event is set
        schedule.run_pending()
        time.sleep(2)
        
def on_closing(exit_event):
    exit_event.set()
    main.destroy()

main.state('withdrawn')

open_login_window()

# Define a function to run schedule.run_pending() in the background

exit_event = threading.Event()


# Start the background thread
schedule_thread = threading.Thread(target=run_schedule, args=(exit_event,), daemon=True)
schedule_thread.start()

main.protocol("WM_DELETE_WINDOW", lambda: on_closing(exit_event))

main.mainloop()
