# Main desktop application for clustering systems management
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add shared module to path
shared_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shared')
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from api_client import APIClient, AuthenticationError


class ClusteringSystemManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clustering Systems Manager")
        self.root.geometry("800x600")

        # API client for state management
        self.api_client = APIClient()
        self.current_user = None

        # Create UI elements
        self.create_widgets()
        self.check_auth_status()

        # Load systems after a short delay to allow auth to settle
        self.root.after(500, self.refresh_systems)

    def check_auth_status(self):
        """Check if we have existing auth and verify it."""
        try:
            user_data = self.api_client.get_current_user()
            self.current_user = user_data['user']
            self.update_auth_ui(True)
            self.status_label.config(text=f"Logged in as: {self.current_user['username']}")
        except Exception:
            self.show_login_dialog()

    def update_auth_ui(self, logged_in):
        """Update UI based on login status."""
        if logged_in:
            self.login_btn.config(state='disabled')
            self.logout_btn.config(state='normal')
            self.add_btn.config(state='normal')
            self.update_btn.config(state='normal')
            self.delete_btn.config(state='normal')
        else:
            self.login_btn.config(state='normal')
            self.logout_btn.config(state='disabled')
            self.add_btn.config(state='disabled')
            self.update_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')

    def show_login_dialog(self):
        """Show login dialog."""
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")
        login_window.geometry("300x200")
        login_window.transient(self.root)
        login_window.grab_set()

        ttk.Label(login_window, text="Username:").pack(pady=(10, 0))
        username_entry = ttk.Entry(login_window, width=30)
        username_entry.pack()
        username_entry.insert(0, "admin")

        ttk.Label(login_window, text="Password:").pack(pady=(10, 0))
        password_entry = ttk.Entry(login_window, width=30, show="*")
        password_entry.pack()
        password_entry.insert(0, "admin123")

        def do_login():
            username = username_entry.get()
            password = password_entry.get()
            try:
                result = self.api_client.login(username, password)
                self.current_user = result['user']
                self.update_auth_ui(True)
                self.status_label.config(text=f"Logged in as: {self.current_user['username']}")
                login_window.destroy()
                self.refresh_systems()
            except AuthenticationError:
                messagebox.showerror("Login Failed", "Invalid username or password")
            except Exception as e:
                messagebox.showerror("Error", f"Could not connect to server: {str(e)}")

        ttk.Button(login_window, text="Login", command=do_login).pack(pady=(15, 10))

    def show_logout_confirmation(self):
        """Show logout confirmation."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.api_client.logout()
            self.current_user = None
            self.update_auth_ui(False)
            self.status_label.config(text="Not logged in")
            self.clear_tree()
            messagebox.showinfo("Logged Out", "You have been logged out.")

    def show_add_dialog(self):
        """Show dialog to add a new system."""
        if not self.current_user:
            messagebox.showwarning("Unauthorized", "Please login first.")
            return

        add_window = tk.Toplevel(self.root)
        add_window.title("Add System")
        add_window.geometry("350x250")
        add_window.transient(self.root)
        add_window.grab_set()

        ttk.Label(add_window, text="Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(add_window, width=40)
        name_entry.pack()

        ttk.Label(add_window, text="Status:").pack(pady=(10, 0))
        status_combo = ttk.Combobox(add_window, values=["active", "inactive", "maintenance", "error"], width=38)
        status_combo.pack()
        status_combo.set("active")

        def do_add():
            name = name_entry.get().strip()
            status = status_combo.get()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            try:
                self.api_client.create_system({'name': name, 'status': status})
                add_window.destroy()
                self.refresh_systems()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create system: {str(e)}")

        ttk.Button(add_window, text="Add", command=do_add).pack(pady=(15, 10))

    def show_update_dialog(self):
        """Show dialog to update selected system."""
        if not self.current_user:
            messagebox.showwarning("Unauthorized", "Please login first.")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a system to update.")
            return

        item = self.tree.item(selected[0])
        system_id = item['values'][0]

        # Get current system data
        try:
            system_data = self.api_client.get_system(system_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get system data: {str(e)}")
            return

        update_window = tk.Toplevel(self.root)
        update_window.title("Update System")
        update_window.geometry("350x250")
        update_window.transient(self.root)
        update_window.grab_set()

        ttk.Label(update_window, text="Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(update_window, width=40)
        name_entry.pack()
        name_entry.insert(0, system_data.get('name', 'New System'))

        ttk.Label(update_window, text="Status:").pack(pady=(10, 0))
        status_combo = ttk.Combobox(update_window, values=["active", "inactive", "maintenance", "error"], width=38)
        status_combo.pack()
        status_combo.set(system_data.get('status', 'active'))

        def do_update():
            name = name_entry.get().strip()
            status = status_combo.get()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            try:
                self.api_client.update_system(system_id, {'name': name, 'status': status})
                update_window.destroy()
                self.refresh_systems()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update system: {str(e)}")

        ttk.Button(update_window, text="Update", command=do_update).pack(pady=(15, 10))

    def confirm_delete(self):
        """Confirm and delete selected system."""
        if not self.current_user:
            messagebox.showwarning("Unauthorized", "Please login first.")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a system to delete.")
            return

        item = self.tree.item(selected[0])
        system_id = item['values'][0]
        system_name = item['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{system_name}'?"):
            try:
                self.api_client.delete_system(system_id)
                self.refresh_systems()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete system: {str(e)}")

    def clear_tree(self):
        """Clear all items from the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def refresh_systems(self):
        """Refresh systems from the API."""
        if not self.current_user:
            return

        try:
            systems = self.api_client.get_systems()
            self.clear_tree()
            for system in systems:
                self.tree.insert("", tk.END, values=(
                    system['id'],
                    system['name'],
                    system['status']
                ))
        except AuthenticationError:
            messagebox.showwarning("Session Expired", "Your session has expired. Please login again.")
            self.api_client.clear_auth()
            self.current_user = None
            self.update_auth_ui(False)
            self.status_label.config(text="Not logged in")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load systems: {str(e)}")

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="we ns")

        # Title
        title_label = ttk.Label(main_frame, text="Clustering Systems Manager", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Status label
        self.status_label = ttk.Label(main_frame, text="Not logged in", font=("Arial", 10))
        self.status_label.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="w")

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 20))

        self.add_btn = ttk.Button(button_frame, text="Add System", command=self.show_add_dialog, state='disabled')
        self.add_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.update_btn = ttk.Button(button_frame, text="Update System", command=self.show_update_dialog, state='disabled')
        self.update_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.delete_btn = ttk.Button(button_frame, text="Delete System", command=self.confirm_delete, state='disabled')
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.login_btn = ttk.Button(button_frame, text="Login", command=lambda: self.show_login_dialog())
        self.login_btn.pack(side=tk.LEFT)

        self.logout_btn = ttk.Button(button_frame, text="Logout", command=self.show_logout_confirmation, state='disabled')
        self.logout_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Systems treeview
        columns = ("ID", "Name", "Status")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.grid(row=3, column=0, columnspan=2, sticky="we ns")

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClusteringSystemManager(root)
    root.mainloop()