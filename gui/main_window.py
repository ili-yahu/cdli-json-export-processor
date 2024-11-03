import tkinter as tk
from tkinter import ttk
from .home_tab import create_home_tab
from .import_tab import create_import_tab
from .explore_tab import create_explore_tab  # Add this import
from .options_tab import create_options_tab
from .help_tab import create_help_tab
from .credits_tab import create_credits_tab

def create_main_window():
    """Create and configure the main application window"""
    root = tk.Tk()
    root.configure(bg='white')
    root.title("Database manager")

    # Center the window on the screen
    window_width = 600
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # Configure notebook style
    style = ttk.Style()
    style.configure('TNotebook.Tab', font=('Arial','12','bold'), padding=[10, 5])

    # Create notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Create tabs
    create_home_tab(notebook)
    create_import_tab(notebook)
    create_explore_tab(notebook)  # Add this line
    create_options_tab(notebook)
    create_help_tab(notebook)
    create_credits_tab(notebook)

    return root
