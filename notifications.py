import schedule
import time
import threading
from datetime import datetime, timedelta
import os
import tkinter as tk
from tkinter import messagebox

class NotificationManager:
    def __init__(self):
        self.notification_thread = None
        self.is_running = False
        self.scheduled_tasks = {}  # Store scheduled tasks
        self.root = None  # Will be set when needed
        # Get the path to the icon file
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon", "icon.ico")

    def set_root(self, root):
        self.root = root

    def show_notification(self, title, message):
        try:
            #print(f"Attempting to show notification: {title}")
            if self.root:
                # Create messagebox and auto-close after 10 seconds
                msg_box = messagebox.showinfo(title, message)
                self.root.after(10000, lambda: self.root.focus_force())
            else:
                # If no root window, create a temporary one
                temp_root = tk.Tk()
                temp_root.withdraw()  # Hide the temporary window
                msg_box = messagebox.showinfo(title, message)
                temp_root.after(10000, temp_root.destroy)  # Destroy after 10 seconds
            #print(f"Notification shown successfully: {title}")  # Debug print
            return True
        except Exception as e:
            print(f"Error showing notification: {e}")
            return False

    def schedule_reminder(self, task, reminder_time, is_recurring=False, recurrence_interval=None):
        def reminder_job():
            #print(f"Reminder job triggered for task: {task['Title']}")  # Debug print
            # Create a more detailed message
            message = (
                f"Task: {task['Title']}\n"
                f"Due Date: {task['Due Date']}\n"
                f"Priority: {task['Priority']}\n"
                f"Category: {task['Category']}\n"
                f"Status: {task['Status']}"
            )
            
            # Show notification
            self.show_notification(
                f"Task Reminder",
                message
            )

        try:
            # Parse the reminder time
            #print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")  # Debug print
            #print(f"Setting reminder for: {reminder_time}")  # Debug print
            
            # Parse the reminder datetime
            reminder_datetime = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
            current_time = datetime.now()
            
            # Calculate time until reminder
            time_until_reminder = (reminder_datetime - current_time).total_seconds()
            #print(f"Time until reminder: {time_until_reminder} seconds")  # Debug print
            #print(f"Reminder will trigger at: {reminder_datetime.strftime('%Y-%m-%d %H:%M')}")  # Debug print
            
            if time_until_reminder < 0:
                print(f"Reminder time {reminder_time} has already passed")
                return
            
            # Schedule the reminder
            if is_recurring and recurrence_interval:
                if recurrence_interval == 'Daily':
                    schedule.every().day.at(reminder_datetime.strftime('%H:%M')).do(reminder_job)
                elif recurrence_interval == 'Weekly':
                    schedule.every().monday.at(reminder_datetime.strftime('%H:%M')).do(reminder_job)
                elif recurrence_interval == 'Monthly':
                    schedule.every().day.at(reminder_datetime.strftime('%H:%M')).do(reminder_job)
                print(f"Set up recurring reminder: {recurrence_interval} at {reminder_datetime.strftime('%H:%M')}")
            else:
                # For one-time reminders, use threading.Timer
                #print(f"Setting up one-time reminder for {reminder_datetime.strftime('%Y-%m-%d %H:%M')}")  # Debug print
                timer = threading.Timer(time_until_reminder, reminder_job)
                timer.start()
                self.scheduled_tasks[task['Title']] = timer
                #print(f"Scheduled one-time reminder for {reminder_datetime.strftime('%Y-%m-%d %H:%M')}")
                
        except Exception as e:
            print(f"Error scheduling reminder: {e}")

    def start_notification_service(self):
        def run_scheduler():
            self.is_running = True
            #print("Notification service started")  # Debug print
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except Exception as e:
                    print(f"Error in notification service: {e}")
                    time.sleep(1)

        self.notification_thread = threading.Thread(target=run_scheduler)
        self.notification_thread.daemon = True
        self.notification_thread.start()
        #print("Notification thread started")  # Debug print

    def stop_notification_service(self):
        self.is_running = False
        # Cancel all scheduled tasks
        for task_name, timer in self.scheduled_tasks.items():
            timer.cancel()
        self.scheduled_tasks.clear()
        if self.notification_thread:
            self.notification_thread.join()
            #print("Notification service stopped")  # Debug print