import tkinter as tk
from nagato_ui import NagatoUI

def launch_nagato():
    root = tk.Tk()
    app = NagatoUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_nagato()
