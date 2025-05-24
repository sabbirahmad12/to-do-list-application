import pandas as pd
from tkinter import messagebox
import os

class DatabaseManager:
    def __init__(self, excel_file="tasks.xlsx", history_file="history.xlsx"):
        # Create data directory if it doesn't exist
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Set file paths in data directory
        self.excel_file = os.path.join(self.data_dir, excel_file)
        self.history_file = os.path.join(self.data_dir, history_file)
        
        self.tasks = []
        self.history_tasks = []
        self.load_tasks()
        self.load_history()
        
    def load_tasks(self):
        if os.path.exists(self.excel_file):
            try:
                df = pd.read_excel(self.excel_file)
                # Ensure Reminder Time column exists
                if 'Reminder Time' not in df.columns:
                    df['Reminder Time'] = ''
                self.tasks = df.to_dict("records")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading tasks: {str(e)}")
                self.tasks = []
        else:
            self.tasks = []
            
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                df = pd.read_excel(self.history_file)
                # Ensure Reminder Time column exists
                if 'Reminder Time' not in df.columns:
                    df['Reminder Time'] = ''
                self.history_tasks = df.to_dict("records")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading history: {str(e)}")
                self.history_tasks = []
        else:
            self.history_tasks = []
            
    def save_tasks(self):
        try:
            df = pd.DataFrame(self.tasks)
            df.to_excel(self.excel_file, index=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving tasks: {str(e)}")
            
    def save_history(self):
        try:
            df = pd.DataFrame(self.history_tasks)
            df.to_excel(self.history_file, index=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving history: {str(e)}")
            
    def add_task(self, task):
        self.tasks.append(task)
        self.save_tasks()
        # Also add to history
        self.history_tasks.append(task)
        self.save_history()
        
    def update_task(self, index, task):
        if 0 <= index < len(self.tasks):
            self.tasks[index] = task
            self.save_tasks()
            
    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_tasks()
            
    def get_all_tasks(self):
        return self.tasks
        
    def get_all_history_tasks(self):
        return self.history_tasks
        
    def filter_tasks(self, search_text="", priority="All", category="All"):
        filtered_tasks = []
        search_text = search_text.lower()
        
        for task in self.tasks:
            if (search_text in task["Title"].lower() or 
                search_text in task["Description"].lower()) and \
               (priority == "All" or task["Priority"] == priority) and \
               (category == "All" or task["Category"] == category):
                filtered_tasks.append(task)
                
        return filtered_tasks 

    def clear_all_tasks(self):
        self.tasks = []
        self.save_tasks()
        
    def clear_all_history(self):
        self.history_tasks = []
        self.save_history() 