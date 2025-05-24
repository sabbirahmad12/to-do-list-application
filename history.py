import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class HistoryPage:
    def __init__(self, main_container, db_manager):
        self.main_container = main_container
        self.db_manager = db_manager
        self.create_history_page()
        
    def create_history_page(self):
        # Create header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="Task History", font=("Helvetica", 24))
        title_label.pack(side=tk.LEFT)
        
        # Create button frame for right-aligned buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Refresh Button
        refresh_button = ttk.Button(button_frame, text="↻ Refresh", 
                                  command=self.refresh_history)
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Clear All Button
        clear_all_button = ttk.Button(button_frame, text="🗑️ Clear All History", 
                                    command=self.clear_all_history)
        clear_all_button.pack(side=tk.RIGHT, padx=5)
        
        # Create history list
        list_frame = ttk.LabelFrame(self.main_container, text="Task History")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with custom style
        style = ttk.Style()
        style.configure("Custom.Treeview.Heading", 
                       background="#2196f3",
                       foreground="white",
                       font=("Helvetica", 10))
        
        # Configure hover effect for headers
        style.map("Custom.Treeview.Heading",
                 background=[('active', '#1F7CC3')],
                 foreground=[('active', 'white')])

        # Create Treeview
        columns = ("Title", "Description", "Date", "Reminder Time", "Priority", "Category", "Status")
        self.history_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Custom.Treeview")
        
        # Set column headings
        for col in columns:
            self.history_tree.heading(col, text=col, anchor="w")
            self.history_tree.column(col, width=150, anchor="w")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load history
        self.load_history()
        
    def load_history(self):
        """Load task history from database"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Load history tasks from database
        self.db_manager.load_history()  # Reload history from Excel
        tasks = self.db_manager.get_all_history_tasks()
        
        # Add tasks to history
        for task in tasks:
            values = (
                task["Title"],
                task["Description"],
                task["Due Date"],
                task.get("Reminder Time", ""),
                task["Priority"],
                task["Category"],
                task["Status"]
            )
            
            self.history_tree.insert("", tk.END, values=values)
            
    def refresh_history(self):
        self.load_history()
        messagebox.showinfo("Refresh", "History has been refreshed!")
            
    def clear_all_history(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all task history?"):
            # Clear the history database
            self.db_manager.clear_all_history()
            # Clear the treeview
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            messagebox.showinfo("Success", "All task history has been cleared!") 