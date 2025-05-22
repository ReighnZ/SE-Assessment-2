import tkinter as tk
import random
import string
from tkinter import messagebox, simpledialog
from db import get_db_connection
from encryption import encrypt_password, decrypt_password
from auth import authenticate, create_user

class PasswordManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Password Manager")
        self.entry_frame = tk.Frame(self.master)
        self.entry_frame.pack()
        self.master.configure(bg="lightgrey")
        self.login_screen()

    def login_screen(self):
        self.clear()

        login_frame = tk.Frame(self.master, bg="lightgrey", pady=20)
        login_frame.pack(expand=True)

        tk.Label(login_frame, text="Username", bg="lightgrey", font=('Arial', 12)).grid(row=0, column=0, pady=5, sticky="e")
        self.username_entry = tk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(login_frame, text="Password", bg="lightgrey", font=('Arial', 12)).grid(row=1, column=0, pady=5, sticky="e")
        self.password_entry = tk.Entry(login_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)

        btn_frame = tk.Frame(login_frame, bg="lightgrey")
        btn_frame.grid(row=2, columnspan=2, pady=15)

        tk.Button(btn_frame, text="Login", width=12, command=self.login).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Register", width=12, command=self.register).grid(row=0, column=1, padx=10)

    def logout(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.login_screen()

    def main_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        if hasattr(self, 'back_button') and self.back_button.winfo_exists():
            self.back_button.destroy()

        # ✅ Add a horizontal frame for the top buttons
        top_button_frame = tk.Frame(self.master, bg="lightgrey", pady=10)
        top_button_frame.pack(pady=10)

        tk.Button(top_button_frame, text="Add Entry", width=15, command=self.add_entry).pack(side=tk.LEFT, padx=10)
        tk.Button(top_button_frame, text="Search", width=15, command=self.search_entry).pack(side=tk.LEFT, padx=10)
        tk.Button(top_button_frame, text="Logout", width=15, command=self.logout).pack(side=tk.LEFT, padx=10)

        # ✅ Entries frame stays below the buttons
        self.entries_frame = tk.Frame(self.master)
        self.entries_frame.pack()

        self.load_entries()

    def clear(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def login(self):
        if authenticate(self.username_entry.get(), self.password_entry.get()):
            self.main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register(self):
        create_user(self.username_entry.get(), self.password_entry.get())
        messagebox.showinfo("Registered", "You can now log in.")

    def add_entry(self):
        service = simpledialog.askstring("Service", "Enter service name:")
        username = simpledialog.askstring("Username", "Enter username:")
    
        choice = messagebox.askyesno("Use Generator?", "Generate a strong password or create a password manually?")
        if choice:
            password = self.generate_password()
        else:
            password = simpledialog.askstring("Password", "Enter password:")
    
        category = simpledialog.askstring("Category", "Enter category (e.g., Email, Social Media):")
        encrypted_pw = encrypt_password(password)

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO passwords (service, username, password, category) VALUES (?, ?, ?, ?)", 
              (service, username, encrypted_pw, category))
        conn.commit()
        conn.close()
        self.load_entries()

    def load_entries(self):
        # Clear previous entries
        for widget in self.entries_frame.winfo_children():
            widget.destroy()

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM passwords")
        rows = c.fetchall()
        conn.close()

        for row in rows:
            decrypted_pw = decrypt_password(row[3])
            masked_pw = '*' * len(decrypted_pw)
            pw_var = tk.StringVar(value=masked_pw)

            frame = tk.Frame(self.entries_frame)
            frame.pack(pady=5)

            info_label = tk.Label(frame, text=f"{row[1]} | {row[2]} | Category: {row[4]}")
            info_label.pack(side=tk.LEFT, padx=5)

            pw_label = tk.Label(frame, textvariable=pw_var, width=20)
            pw_label.pack(side=tk.LEFT)

            def toggle_pw(var=pw_var, pw=decrypted_pw):
                var.set(pw if var.get().startswith('*') else '*' * len(pw))

            toggle_btn = tk.Button(frame, text="Show/Hide", command=toggle_pw)
            toggle_btn.pack(side=tk.LEFT, padx=5)

            edit_btn = tk.Button(frame, text="Edit", command=lambda r=row: self.edit_entry(r))
            edit_btn.pack(side=tk.LEFT, padx=5)

            delete_btn = tk.Button(frame, text="Delete", command=lambda r=row: self.delete_entry(r[0]))
            delete_btn.pack(side=tk.LEFT, padx=5)

    def edit_entry(self, row):
        new_pw = simpledialog.askstring("Edit Password", "Enter new password:")
        if new_pw:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE passwords SET password=? WHERE id=?", (encrypt_password(new_pw), row[0]))
            conn.commit()
            conn.close()
            self.load_entries()

    def delete_entry(self, entry_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM passwords WHERE id=?", (entry_id,))
        conn.commit()
        conn.close()
        self.load_entries()

    def search_entry(self):
        # Get unique categories from the DB
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT DISTINCT category FROM passwords")
        categories = [row[0] for row in c.fetchall() if row[0]]
        conn.close()

        # Create a new popup window
        search_win = tk.Toplevel(self.master)
        search_win.title("Search by Category")

        tk.Label(search_win, text="Select a category to filter entries:").pack(pady=5)

        # 🔽 Dropdown menu for category selection only
        selected_category = tk.StringVar()
        selected_category.set("Select Category")
        if categories:
            tk.OptionMenu(search_win, selected_category, *categories).pack(pady=5)

        def perform_search():
            category = selected_category.get()
            if category == "Select Category":
                return  # Ignore if no category selected

            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM passwords WHERE category = ?", (category,))
            rows = c.fetchall()
            conn.close()

            for widget in self.entries_frame.winfo_children():
                widget.destroy()

        # Show only the search results
            self.display_search_results(rows)
            search_win.destroy()

        tk.Button(search_win, text="Search", command=perform_search).pack(pady=10)

    def display_search_results(self, rows):
        for widget in self.entries_frame.winfo_children():
            widget.destroy()

        for row in rows:
            decrypted_pw = decrypt_password(row[3])
            masked_pw = '*' * len(decrypted_pw)
            pw_var = tk.StringVar(value=masked_pw)

            frame = tk.Frame(self.entries_frame)
            frame.pack(pady=5)

            info_label = tk.Label(frame, text=f"{row[1]} | {row[2]} | Category: {row[4]}")
            info_label.pack(side=tk.LEFT, padx=5)

            pw_label = tk.Label(frame, textvariable=pw_var, width=20)
            pw_label.pack(side=tk.LEFT)

            def toggle_pw(var=pw_var, pw=decrypted_pw):
                var.set(pw if var.get().startswith('*') else '*' * len(pw))

            toggle_btn = tk.Button(frame, text="Show/Hide", command=toggle_pw)
            toggle_btn.pack(side=tk.LEFT, padx=5)

            edit_btn = tk.Button(frame, text="Edit", command=lambda r=row: self.edit_entry(r))
            edit_btn.pack(side=tk.LEFT, padx=5)

            delete_btn = tk.Button(frame, text="Delete", command=lambda r=row: self.delete_entry(r[0]))
            delete_btn.pack(side=tk.LEFT, padx=5)

        # Only create back button on search screen
        if hasattr(self, 'back_button') and self.back_button.winfo_exists():
            self.back_button.destroy()

        self.back_button = tk.Button(self.master, text="Back", command=self.main_screen)
        self.back_button.pack(pady=10)

    def return_to_main_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.main_screen()

    def generate_password(self):
        length = simpledialog.askinteger("Length", "Enter password length (e.g., 12):", minvalue=6, maxvalue=32)
        if not length:
            return "Generated123!"  # fallback

        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))
