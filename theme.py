import tkinter as tk
from tkinter import ttk

class CustomCombobox(ttk.Combobox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._popup = None
        self.bind('<Button-1>', self._show_popup)
        
    def _show_popup(self, event):
        if self._popup:
            self._popup.destroy()
            
        # Get the current theme colors
        style = ttk.Style()
        if hasattr(self.master, 'theme_manager'):
            theme_manager = self.master.theme_manager
            is_dark = theme_manager.is_dark_theme
            if is_dark:
                bg_color = '#181825'  # Dark theme background
                text_color = '#cdd6f4'  # Dark theme text
                select_bg = '#89b4fa'  # Dark theme accent
                select_fg = '#1e1e2e'  # Dark theme background
                border_color = '#313244'  # Dark theme border
            else:
                bg_color = '#ffffff'  # Light theme background
                text_color = '#1a237e'  # Light theme text
                select_bg = '#2196f3'  # Light theme accent
                select_fg = '#ffffff'  # Light theme text
                border_color = '#e0e0e0'  # Light theme border
        else:
            bg_color = '#ffffff'
            text_color = '#000000'
            select_bg = '#0078d7'
            select_fg = '#ffffff'
            border_color = '#e0e0e0'
            
        # Create popup window
        self._popup = tk.Toplevel(self)
        self._popup.overrideredirect(True)
        self._popup.configure(bg=border_color)
        
        # Position popup below combobox
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self._popup.geometry(f'+{x}+{y}')
        
        # Create frame to hold listbox with border
        frame = ttk.Frame(self._popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Create listbox with fixed height
        listbox = tk.Listbox(frame, 
                           bg=bg_color,
                           fg=text_color,
                           selectbackground=select_bg,
                           selectforeground=select_fg,
                           highlightthickness=0,
                           borderwidth=0,
                           activestyle='none',
                           height=min(3, len(self['values'])))  # Show max 3 items
        listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar if needed
        if len(self['values']) > 3:
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.configure(yscrollcommand=scrollbar.set)
        
        # Add values
        for value in self['values']:
            listbox.insert(tk.END, value)
            
        # Set width to match combobox
        listbox.configure(width=self.winfo_width())
        
        # Handle selection
        def on_select(event):
            selection = listbox.curselection()
            if selection:
                value = listbox.get(selection[0])
                self.set(value)
                self.event_generate('<<ComboboxSelected>>')
                self._popup.destroy()
                self._popup = None
                
        listbox.bind('<ButtonRelease-1>', on_select)
        
        # Handle escape key
        def on_escape(event):
            self._popup.destroy()
            self._popup = None
            
        self._popup.bind('<Escape>', on_escape)
        
        # Handle focus out
        def on_focus_out(event):
            if str(event.widget) != str(self._popup):
                self._popup.destroy()
                self._popup = None
                
        self._popup.bind('<FocusOut>', on_focus_out)
        
        # Set focus to listbox
        listbox.focus_set()
        
        # Add hover effect
        def on_enter(e):
            if not listbox.curselection():
                listbox.selection_set(listbox.nearest(e.y))
                
        def on_leave(e):
            if not listbox.curselection():
                listbox.selection_clear(0, tk.END)
                
        listbox.bind('<Motion>', on_enter)
        listbox.bind('<Leave>', on_leave)
        
        # Force update colors
        self._popup.update_idletasks()
        frame.configure(style='TFrame')
        listbox.configure(bg=bg_color, fg=text_color)

class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.is_dark_theme = False
        
        # Priority colors
        self.priority_colors = {
            'High': '#f38ba8',    # Soft red
            'Medium': '#f9e2af',  # Soft yellow
            'Low': '#a6e3a1'      # Soft green
        }
        
        # Initialize with light theme
        self.apply_light_theme()
        
    def apply_light_theme(self):
        # Main colors
        bg_color = '#e8f4f8'  # Light blue-gray
        text_color = '#1a237e'  # Deep indigo
        accent_color = '#2196f3'  # Material blue
        hover_color = '#1F7CC3' 
        
        # Configure styles
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabelframe', background=bg_color)
        self.style.configure('TLabelframe.Label', background=bg_color, foreground=text_color)
        self.style.configure('TLabel', background=bg_color, foreground=text_color)
        
        # Button styles with hover effect
        self.style.configure('TButton', 
                           background=accent_color, 
                           foreground='#ffffff')
        self.style.map('TButton',
                      background=[('active', hover_color)],
                      foreground=[('active', '#ffffff')])
        
        # Treeview styles
        self.style.configure('Treeview', 
                           background='#ffffff',
                           foreground=text_color,
                           fieldbackground='#ffffff')
        self.style.configure('Treeview.Heading', 
                           background=accent_color,
                           foreground='#ffffff')
        
        # Input styles
        self.style.configure('TEntry', 
                           fieldbackground='#ffffff',
                           foreground=text_color)
        
        # Custom Combobox styles for light theme
        self.style.configure('Custom.TCombobox', 
                           fieldbackground='#ffffff',
                           background='#ffffff',
                           foreground=text_color,
                           arrowcolor=text_color)
        
        # Configure Combobox popup list for light theme
        self.style.map('Custom.TCombobox',
                      fieldbackground=[('readonly', '#ffffff')],
                      selectbackground=[('readonly', accent_color)],
                      selectforeground=[('readonly', '#ffffff')],
                      background=[('readonly', '#ffffff')],
                      foreground=[('readonly', text_color)])
        
        # Update root window
        self.root.configure(bg=bg_color)
        
    def apply_dark_theme(self):
        # Main colors
        bg_color = '#1e1e2e'  # Rich dark blue-gray
        darker_bg = '#181825'  # Even darker background
        text_color = '#cdd6f4'  # Light lavender text
        accent_color = '#89b4fa'  # Soft blue accent
        hover_color = '#b4c6fc' 
        
        # Configure styles
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabelframe', background=bg_color)
        self.style.configure('TLabelframe.Label', background=bg_color, foreground=text_color)
        self.style.configure('TLabel', background=bg_color, foreground=text_color)
        
        # Button styles with hover effect
        self.style.configure('TButton', 
                           background=accent_color, 
                           foreground=bg_color)
        self.style.map('TButton',
                      background=[('active', hover_color)],
                      foreground=[('active', bg_color)])
        
        # Treeview styles
        self.style.configure('Treeview', 
                           background=darker_bg,
                           foreground=text_color,
                           fieldbackground=darker_bg)
        self.style.configure('Treeview.Heading', 
                           background=accent_color,
                           foreground=bg_color)
        
        # Input styles
        self.style.configure('TEntry', 
                           fieldbackground=darker_bg,
                           foreground=text_color)
        
        # Custom Combobox styles for dark theme
        self.style.configure('Custom.TCombobox', 
                           fieldbackground=darker_bg,
                           background=darker_bg,
                           foreground=text_color,
                           arrowcolor=text_color)
        
        # Configure Combobox popup list for dark theme
        self.style.map('Custom.TCombobox',
                      fieldbackground=[('readonly', darker_bg)],
                      selectbackground=[('readonly', accent_color)],
                      selectforeground=[('readonly', bg_color)],
                      background=[('readonly', darker_bg)],
                      foreground=[('readonly', text_color)])
        
        # Update root window
        self.root.configure(bg=bg_color)
        
        # Update any existing Combobox widgets
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Combobox):
                widget.configure(style='Custom.TCombobox')
                
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
            
    def get_priority_color(self, priority):
        return self.priority_colors.get(priority, '#ffffff') 