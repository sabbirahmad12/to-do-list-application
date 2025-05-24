import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from ttkthemes import ThemedTk
from datetime import datetime
import shutil
import os
from theme import ThemeManager, CustomCombobox
from database import DatabaseManager
from notifications import NotificationManager
from history import HistoryPage

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do-List Application")
        self.root.geometry("1100x800+100+100")
        self.root.minsize(1100, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Initialize managers
        self.theme_manager = ThemeManager(root)
        self.db_manager = DatabaseManager()
        self.notification_manager = NotificationManager()
        self.notification_manager.set_root(root)  # Set root window for notifications
        
        # Start notification service
        self.notification_manager.start_notification_service()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create UI components
        self.create_header()
        self.create_task_input()
        self.create_task_list()
        self.create_filters()
        self.create_footer()
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Add Home and History directly to menubar
        menubar.add_command(label="Home", command=self.show_home)
        menubar.add_command(label="History", command=self.show_history)
        
    def show_home(self):
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        # Recreate home page components
        self.create_header()
        self.create_task_input()
        self.create_task_list()
        self.create_filters()
        self.create_footer()
        
    def show_history(self):
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        # Create history page
        self.history_page = HistoryPage(self.main_container, self.db_manager)
        
    def create_header(self):
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add image
        try:
            img = tk.PhotoImage(file="img/img.png")
            # Resize image to smaller size
            img = img.subsample(10, 10)  # This will make the image one-fourth its original size
            # Keep a reference to prevent garbage collection
            self.header_img = img
            img_label = ttk.Label(header_frame, image=img)
            img_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            messagebox.showerror("Error", f"Error loading image: {e}")
        
        title_label = ttk.Label(header_frame, text="To-Do-List Application", 
                              font=("Helvetica", 24))
        title_label.pack(side=tk.LEFT)
        
        # Create button frame for right-aligned buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Backup Button
        backup_button = ttk.Button(button_frame, text="💾 Backup", 
                                 command=self.backup_data)
        backup_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Theme Button
        theme_button = ttk.Button(button_frame, text="🎨 Change Theme", 
                                command=self.theme_manager.toggle_theme)
        theme_button.pack(side=tk.RIGHT, padx=(5, 0))

    def create_footer(self):
        footer_frame = ttk.Frame(self.main_container)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        copyright_label = ttk.Label(footer_frame, text="© 2025 Developed by Md Sabbir Ahmad", 
                                  font=("Helvetica", 8))
        copyright_label.pack(side=tk.BOTTOM, pady=5)
        
    def backup_data(self):
        try:
            # Create backups directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Get the current date and time for the backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup tasks.xlsx
            tasks_backup_filename = f"tasks_backup_{timestamp}.xlsx"
            tasks_backup_path = os.path.join(backup_dir, tasks_backup_filename)
            shutil.copy2(self.db_manager.excel_file, tasks_backup_path)
            
            # Backup history.xlsx
            history_backup_filename = f"history_backup_{timestamp}.xlsx"
            history_backup_path = os.path.join(backup_dir, history_backup_filename)
            shutil.copy2(self.db_manager.history_file, history_backup_path)
            
            messagebox.showinfo("Backup Successful", 
                              f"Data has been backed up successfully to:\n{tasks_backup_path}\n{history_backup_path}")
            
        except Exception as e:
            messagebox.showerror("Backup Error", 
                               f"An error occurred while creating the backup:\n{str(e)}")
            
    def restore_backup(self):
        try:
            # Set the default backup directory
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
            
            # Ask user to select a backup file from the backups directory
            backup_path = filedialog.askopenfilename(
                initialdir=backup_dir,
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if backup_path:  # If user didn't cancel
                # Confirm restoration
                if messagebox.askyesno("Confirm Restore", 
                                     "This will replace all current data with the backup data. Continue?"):
                    # Determine if this is a tasks or history backup
                    if "tasks_backup" in backup_path:
                        target_file = self.db_manager.excel_file
                    elif "history_backup" in backup_path:
                        target_file = self.db_manager.history_file
                    else:
                        messagebox.showerror("Error", "Invalid backup file format!")
                        return
                    
                    # Copy the backup file to the current database location
                    shutil.copy2(backup_path, target_file)
                    
                    # Reload the data
                    self.reload_tasks()
                    
                    messagebox.showinfo("Restore Successful", 
                                      "Data has been restored successfully from the backup.")
                    
        except Exception as e:
            messagebox.showerror("Restore Error", 
                               f"An error occurred while restoring the backup:\n{str(e)}")
            
    def create_task_input(self):
        input_frame = ttk.LabelFrame(self.main_container, text="Add New Task")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create a frame for the input fields with 3 columns
        fields_frame = ttk.Frame(input_frame)
        fields_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Configure grid columns
        fields_frame.columnconfigure(0, weight=0)  # Labels column
        fields_frame.columnconfigure(1, weight=0)  # Separator column
        fields_frame.columnconfigure(2, weight=1)  # Input fields column
        
        # Title
        ttk.Label(fields_frame, text="Title").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(fields_frame, text=":").grid(row=0, column=1, padx=2, pady=5)
        self.title_entry = ttk.Entry(fields_frame, width=40)
        self.title_entry.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        # Description
        ttk.Label(fields_frame, text="Description").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(fields_frame, text=":").grid(row=1, column=1, padx=2, pady=5)
        self.desc_entry = ttk.Entry(fields_frame, width=40)
        self.desc_entry.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        # Due Date
        ttk.Label(fields_frame, text="Date").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(fields_frame, text=":").grid(row=2, column=1, padx=2, pady=5)
        self.due_date = DateEntry(fields_frame, width=12)
        self.due_date.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        
        # Priority
        ttk.Label(fields_frame, text="Priority").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(fields_frame, text=":").grid(row=3, column=1, padx=2, pady=5)
        self.priority_var = tk.StringVar(value="Select priority")
        priority_combo = ttk.Combobox(fields_frame, textvariable=self.priority_var,
                                    values=["Select priority", "High", "Medium", "Low"], 
                                    width=15, state="readonly", style="Custom.TCombobox")
        priority_combo.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        
        # Category
        ttk.Label(fields_frame, text="Category").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(fields_frame, text=":").grid(row=4, column=1, padx=2, pady=5)
        self.category_var = tk.StringVar(value="Select category")
        category_combo = ttk.Combobox(fields_frame, textvariable=self.category_var,
                                    values=["Select category", "Work", "Personal", "Shopping", "Health", "Other"], 
                                    width=15, state="readonly", style="Custom.TCombobox")
        category_combo.grid(row=4, column=2, padx=5, pady=5, sticky="w")
        
        # Reminder Time
        ttk.Label(fields_frame, text="Reminder Time").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(fields_frame, text=":").grid(row=5, column=1, padx=2, pady=5)
        reminder_frame = ttk.Frame(fields_frame)
        reminder_frame.grid(row=5, column=2, padx=5, pady=5, sticky="w")
        
        # Date picker
        ttk.Label(reminder_frame, text="Date:").pack(side="left", padx=5)
        self.reminder_date = ttk.Entry(reminder_frame, width=10)
        self.reminder_date.pack(side="left", padx=5)
        self.reminder_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Time picker
        ttk.Label(reminder_frame, text="Time:").pack(side="left", padx=5)
        self.reminder_time = ttk.Entry(reminder_frame, width=5)
        self.reminder_time.pack(side="left", padx=5)
        self.reminder_time.insert(0, datetime.now().strftime("%H:%M"))
        
        # Recurrence
        ttk.Label(fields_frame, text="Recurrence").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(fields_frame, text=":").grid(row=6, column=1, padx=2, pady=5)
        self.recurrence_var = tk.StringVar(value="Select recurring")
        recurrence_combo = ttk.Combobox(fields_frame, textvariable=self.recurrence_var,
                                      values=["Select recurring", "daily", "weekly", "monthly"], 
                                      width=15, state="readonly", style="Custom.TCombobox")
        recurrence_combo.grid(row=6, column=2, padx=5, pady=5, sticky="w")
        
        # Button frame - placed below all input fields
        button_frame = ttk.Frame(fields_frame)
        button_frame.grid(row=7, column=2, pady=10, sticky="w")
        
        # Add Task Button
        add_button = ttk.Button(button_frame, text="📝 Add Task", command=self.add_task)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Reload Button
        reload_button = ttk.Button(button_frame, text="↻ Reload", command=self.reload_tasks)
        reload_button.pack(side=tk.LEFT, padx=5)
        
    def create_task_list(self):
        """Create the task list section"""
        list_frame = ttk.LabelFrame(self.main_container, text="Tasks")
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
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Custom.Treeview")
        
        # Set column headings
        for col in columns:
            self.task_tree.heading(col, text=col, anchor="w")
            self.task_tree.column(col, width=150, anchor="w") 
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add context menu
        self.create_context_menu()
        
        # Refresh task list
        self.refresh_task_list()
        
    def create_filters(self):
        """Create the filter section"""
        filter_frame = ttk.LabelFrame(self.main_container, text="Filters")
        filter_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Search
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.apply_filters)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Priority Filter
        ttk.Label(filter_frame, text="Priority:").pack(side=tk.LEFT, padx=5)
        self.priority_filter = ttk.Combobox(filter_frame, values=["All", "High", "Medium", "Low"],
                                          style="Custom.TCombobox")
        self.priority_filter.set("All")
        self.priority_filter.pack(side=tk.LEFT, padx=5)
        self.priority_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # Category Filter
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_filter = ttk.Combobox(filter_frame, values=["All", "Work", "Personal", "Shopping", "Health", "Other"],
                                          style="Custom.TCombobox")
        self.category_filter.set("All")
        self.category_filter.pack(side=tk.LEFT, padx=5)
        self.category_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_task)
        self.context_menu.add_command(label="Delete", command=self.delete_task)
        self.context_menu.add_command(label="Change Status", command=self.toggle_task_status)
        
        self.task_tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        item = self.task_tree.identify_row(event.y)
        if item:
            self.task_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def add_task(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Please enter a task title!")
            return
            
        # Validate priority selection
        if self.priority_var.get() == "Select priority":
            messagebox.showwarning("Warning", "Please select a priority!")
            return
            
        # Validate category selection
        if self.category_var.get() == "Select category":
            messagebox.showwarning("Warning", "Please select a category!")
            return
            
        # Validate recurrence selection
        if self.recurrence_var.get() == "Select recurring":
            messagebox.showwarning("Warning", "Please select a recurrence!")
            return
            
        # Get reminder time
        reminder_date = self.reminder_date.get().strip()
        reminder_time = self.reminder_time.get().strip()
        reminder_datetime = f"{reminder_date} {reminder_time}" if reminder_date and reminder_time else ""
            
        task = {
            "Title": title,
            "Description": self.desc_entry.get().strip(),
            "Due Date": self.due_date.get_date().strftime("%Y-%m-%d"),
            "Priority": self.priority_var.get(),
            "Category": self.category_var.get(),
            "Status": "Pending",
            "Reminder Time": reminder_datetime
        }
        
        # Add task to database
        self.db_manager.add_task(task)
        
        # Schedule reminder if time is provided
        if reminder_date and reminder_time:
            try:
                # Validate datetime format
                reminder_dt = datetime.strptime(reminder_datetime, '%Y-%m-%d %H:%M')
                
                # Check if reminder time has already passed
                current_dt = datetime.now()
                if reminder_dt < current_dt:
                    messagebox.showwarning("Warning", f"Reminder time {reminder_datetime} has already passed!")
                    return
                
                self.notification_manager.schedule_reminder(
                    task,
                    reminder_datetime,
                    False,
                    None
                )
                # Show success message with reminder info
                messagebox.showinfo("Success", f"Task added successfully!\nScheduled one-time reminder for {reminder_datetime}")
            except ValueError:
                messagebox.showwarning("Warning", "Invalid reminder date/time format! Use YYYY-MM-DD HH:MM")
        else:
            # Show success message without reminder info
            messagebox.showinfo("Success", "Task added successfully!")
        
        self.refresh_task_list()
        self.clear_inputs()
        
    def edit_task(self):
        selected = self.task_tree.selection()
        if not selected:
            return
            
        task_idx = self.task_tree.index(selected[0])
        task = self.db_manager.tasks[task_idx]
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("400x500")
        edit_window.configure(bg='#f0f0f0')  # Light gray background
        
        # Create main frame with padding
        main_frame = ttk.Frame(edit_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style configuration
        style = ttk.Style()
        style.configure('Edit.TLabel', font=('Helvetica', 10, 'bold'))
        style.configure('Edit.TEntry', font=('Helvetica', 10))
        style.configure('Edit.TCombobox', font=('Helvetica', 10))
        style.configure('Edit.TButton', font=('Helvetica', 10, 'bold'))
        
        # Title
        ttk.Label(main_frame, text="Title:", style='Edit.TLabel').pack(pady=(0, 5))
        title_entry = ttk.Entry(main_frame, width=40, style='Edit.TEntry')
        title_entry.insert(0, task["Title"])
        title_entry.pack(pady=(0, 10))
        
        # Description
        ttk.Label(main_frame, text="Description:", style='Edit.TLabel').pack(pady=(0, 5))
        desc_entry = ttk.Entry(main_frame, width=40, style='Edit.TEntry')
        desc_entry.insert(0, task["Description"])
        desc_entry.pack(pady=(0, 10))
        
        # Priority
        ttk.Label(main_frame, text="Priority:", style='Edit.TLabel').pack(pady=(0, 5))
        priority_var = tk.StringVar(value=task["Priority"])
        priority_combo = ttk.Combobox(main_frame, textvariable=priority_var,
                                    values=["High", "Medium", "Low"], 
                                    width=15, state="readonly", style='Edit.TCombobox')
        priority_combo.pack(pady=(0, 10))
        
        # Category
        ttk.Label(main_frame, text="Category:", style='Edit.TLabel').pack(pady=(0, 5))
        category_var = tk.StringVar(value=task["Category"])
        category_combo = ttk.Combobox(main_frame, textvariable=category_var,
                                    values=["Work", "Personal", "Shopping", "Health", "Other"], 
                                    width=15, state="readonly", style='Edit.TCombobox')
        category_combo.pack(pady=(0, 10))
        
        # Reminder Time
        ttk.Label(main_frame, text="Reminder Time:", style='Edit.TLabel').pack(pady=(0, 5))
        reminder_frame = ttk.Frame(main_frame)
        reminder_frame.pack(pady=(0, 10))
        
        # Date picker
        ttk.Label(reminder_frame, text="Date:").pack(side="left", padx=5)
        reminder_date = ttk.Entry(reminder_frame, width=10)
        reminder_date.pack(side="left", padx=5)
        reminder_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Time picker
        ttk.Label(reminder_frame, text="Time:").pack(side="left", padx=5)
        reminder_time = ttk.Entry(reminder_frame, width=5)
        reminder_time.pack(side="left", padx=5)
        reminder_time.insert(0, datetime.now().strftime("%H:%M"))
        
        # Recurrence
        ttk.Label(main_frame, text="Recurrence:", style='Edit.TLabel').pack(pady=(0, 5))
        recurrence_var = tk.StringVar(value="Select recurring")
        recurrence_combo = ttk.Combobox(main_frame, textvariable=recurrence_var,
                                      values=["Select recurring", "daily", "weekly", "monthly"], 
                                      width=15, state="readonly", style='Edit.TCombobox')
        recurrence_combo.pack(pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def save_changes():
            task["Title"] = title_entry.get().strip()
            task["Description"] = desc_entry.get().strip()
            task["Priority"] = priority_var.get()
            task["Category"] = category_var.get()
            
            # Schedule reminder if time is provided
            reminder_date_str = reminder_date.get().strip()
            reminder_time_str = reminder_time.get().strip()
            if reminder_date_str and reminder_time_str:
                try:
                    # Combine date and time
                    reminder_datetime = f"{reminder_date_str} {reminder_time_str}"
                    # Validate datetime format
                    reminder_dt = datetime.strptime(reminder_datetime, '%Y-%m-%d %H:%M')
                    
                    # Check if reminder time has already passed
                    current_dt = datetime.now()
                    if reminder_dt < current_dt:
                        messagebox.showwarning("Warning", f"Reminder time {reminder_datetime} has already passed!")
                        return
                    
                    self.notification_manager.schedule_reminder(
                        task,
                        reminder_datetime,
                        False,
                        None
                    )
                except ValueError:
                    messagebox.showwarning("Warning", "Invalid reminder date/time format! Use YYYY-MM-DD HH:MM")
                    return
            
            self.db_manager.update_task(task_idx, task)
            self.refresh_task_list()
            edit_window.destroy()
            
        # Save button with custom style
        save_button = ttk.Button(button_frame, text="Save Changes", 
                               command=save_changes, style='Edit.TButton')
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                 command=edit_window.destroy, style='Edit.TButton')
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Center the window
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry(f'{width}x{height}+{x}+{y}')
        
    def delete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            task_idx = self.task_tree.index(selected[0])
            self.db_manager.delete_task(task_idx)
            self.refresh_task_list()
            
    def toggle_task_status(self):
        selected = self.task_tree.selection()
        if not selected:
            return
            
        task_idx = self.task_tree.index(selected[0])
        task = self.db_manager.tasks[task_idx]
        task["Status"] = "Completed" if task["Status"] == "Pending" else "Pending"
        self.db_manager.update_task(task_idx, task)
        self.refresh_task_list()
        
    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.priority_var.set("Select priority")
        self.category_var.set("Select category")
        self.recurrence_var.set("Select recurring")
        
        # Update reminder time fields with current time instead of clearing
        current_time = datetime.now()
        self.reminder_date.delete(0, tk.END)
        self.reminder_date.insert(0, current_time.strftime("%Y-%m-%d"))
        self.reminder_time.delete(0, tk.END)
        self.reminder_time.insert(0, current_time.strftime("%H:%M"))
        
    def refresh_task_list(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
            
        for task in self.db_manager.tasks:
            values = (
                task["Title"],
                task["Description"],
                task["Due Date"],
                task.get("Reminder Time", ""),  # Get reminder time with default empty string
                task["Priority"],
                task["Category"],
                task["Status"]
            )
            
            item = self.task_tree.insert("", tk.END, values=values)
            
            # Apply priority color
            if task['Priority'] in self.theme_manager.priority_colors:
                self.task_tree.item(item, tags=(task['Priority'],))
                
    def apply_filters(self, *args):
        search_text = self.search_var.get()
        priority_filter = self.priority_filter.get()
        category_filter = self.category_filter.get()
        
        filtered_tasks = self.db_manager.filter_tasks(search_text, priority_filter, category_filter)
        
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
            
        for task in filtered_tasks:
            values = (
                task["Title"],
                task["Description"],
                task["Due Date"],
                task.get("Reminder Time", ""),  # Get reminder time with default empty string
                task["Priority"],
                task["Category"],
                task["Status"]
            )
            
            item = self.task_tree.insert("", tk.END, values=values)
            
            # Apply priority color
            if task['Priority'] in self.theme_manager.priority_colors:
                self.task_tree.item(item, tags=(task['Priority'],))

    def reload_tasks(self):
        # Clear current display
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
            
        # Reload tasks from database
        self.db_manager.load_tasks()
        
        # Refresh the display
        self.refresh_task_list()
        
        # Show confirmation message
        messagebox.showinfo("Reload", "Task list has been refreshed!")

    def __del__(self):
        if hasattr(self, 'notification_manager'):
            self.notification_manager.stop_notification_service()

if __name__ == "__main__":
    root = ThemedTk(theme="clam")
    # Set application icon
    root.iconbitmap("icon/icon.ico")
    app = TodoApp(root)
    root.mainloop() 