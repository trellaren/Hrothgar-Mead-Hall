# Main desktop application for clustering systems management
import tkinter as tk
from tkinter import ttk
import json

class ClusteringSystemManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clustering Systems Manager")
        self.root.geometry("800x600")
        
        # In-memory storage for clustering systems
        self.systems = []
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Clustering Systems Manager", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        add_button = ttk.Button(button_frame, text="Add System", command=self.add_system)
        add_button.pack(side=tk.LEFT, padx=(0, 10))
        
        update_button = ttk.Button(button_frame, text="Update System", command=self.update_system)
        update_button.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_button = ttk.Button(button_frame, text="Delete System", command=self.delete_system)
        delete_button.pack(side=tk.LEFT)
        
        # Systems treeview
        columns = ("ID", "Name", "Status")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
            
        self.tree.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate with sample data
        self.populate_tree()
        
    def populate_tree(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add systems
        for system in self.systems:
            self.tree.insert("", tk.END, values=(system['id'], system['name'], system['status']))
    
    def add_system(self):
        # Simple implementation - would normally open a dialog
        new_system = {
            'id': len(self.systems) + 1,
            'name': f'System {len(self.systems) + 1}',
            'status': 'active'
        }
        self.systems.append(new_system)
        self.populate_tree()
        
    def update_system(self):
        # Simple implementation - would normally open a dialog
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            system_id = item['values'][0]
            for system in self.systems:
                if system['id'] == system_id:
                    system['status'] = 'updated'
                    break
            self.populate_tree()
        
    def delete_system(self):
        # Simple implementation - would normally confirm deletion
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            system_id = item['values'][0]
            self.systems = [s for s in self.systems if s['id'] != system_id]
            self.populate_tree()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClusteringSystemManager(root)
    root.mainloop()