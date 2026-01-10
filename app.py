import sys
import tkinter as tk
from cpas.ui.main_window import CPASMainWindow

def main():
    """
    Main entry point for the Chain Pattern Analysis System (CPAS).
    Initializes the root Tkinter window and launches the main application dashboard.
    """
    root = tk.Tk()
    root.title("Chain Pattern Analysis System (CPAS) - Milestone 1")
    root.geometry("1400x900")
    
    # Initialize the main window logic
    app = CPASMainWindow(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
