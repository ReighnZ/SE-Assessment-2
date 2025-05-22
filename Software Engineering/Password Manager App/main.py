from tkinter import Tk
from ui import PasswordManagerApp
from db import init_db

if __name__ == "__main__":
    init_db()
    root = Tk()
    app = PasswordManagerApp(root)
    root.mainloop()