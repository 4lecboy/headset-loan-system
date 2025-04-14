import tkinter as tk
from tkinter import Button, Label, Frame

class NavButton:
    """
    Standardized navigation button for consistent look and feel
    """
    def __init__(self, parent, text, command, active=False):
        self.button = Button(
            parent, 
            text=text,
            command=command,
            relief=tk.RAISED,
            bg="#172f66",
            fg="#FFFFFF" if not active else "#FF5900",
            font=("ANTON", 15, "bold")
        )
        
    def get_button(self):
        return self.button
        
    def set_active(self, active=True):
        self.button.config(fg="#FF5900" if active else "#FFFFFF", state='disabled' if active else 'normal')


class HeaderFrame:
    """
    Standard header frame with logo and title
    """
    def __init__(self, parent, title, logo=None):
        self.frame = Frame(parent, background="#172f66")
        self.frame.pack(side="top", anchor="n", fill="x")
        
        self.title = Label(
            self.frame, 
            text=title, 
            font=("ANTON", 35, "bold"),
            bg="#172f66", 
            fg="#f46206"
        )
        self.title.pack(side="left", anchor="nw", pady=50, padx=40)
        
        if logo:
            self.logo = Label(self.frame, image=logo, bg="#172f66")
            self.logo.pack(side="right", anchor="ne")
    
    def get_frame(self):
        return self.frame


class ContentFrame:
    """
    Standard bezel content frame for consistent look
    """
    def __init__(self, parent, title=None):
        self.bezel_frame = Frame(
            parent, 
            background="#000000", 
            highlightbackground="#0096F7", 
            highlightthickness=4, 
            bd=0
        )
        self.bezel_frame.pack(side="top", anchor="n", fill="both", expand=True, pady=10, padx=20)

        self.content_frame = Frame(self.bezel_frame, background="#0096F7")
        self.content_frame.pack(side="top", anchor="n", fill="x", pady=10, padx=10)
        
        if title:
            self.title = Label(
                self.content_frame, 
                text=title, 
                font=("ANTON", 25, "bold"), 
                bg="#0096F7", 
                fg="#E7E7E7"
            )
            self.title.grid(row=1, column=1, padx=(0, 200))
    
    def get_bezel_frame(self):
        return self.bezel_frame
        
    def get_content_frame(self):
        return self.content_frame