import tkinter as tk
from tkinter import ttk, messagebox


class MaterialsView(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg="#f5f5dc")
        self.db = db
        self.selected_id = None
        self.build_ui()
        self.load_data()

    def build_ui(self):
        tk.Label(self, text="Materials", font=("Arial", 18), bg="#f5f5dc").pack(pady=8)

        columns = ("ID", "Name", "Unit Cost", "Stock")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for c in columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        self.tree.pack(fill="both", expand=False, padx=12, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Form
        form = tk.Frame(self, bg="#f5f5dc")
        form.pack(pady=8)

        tk.Label(form, text="Name:", bg="#f5f5dc").grid(row=0, column=0, sticky="e")
        self.name_entry = tk.Entry(form, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form, text="Unit Cost:", bg="#f5f5dc").grid(row=1, column=0, sticky="e")
        self.unit_cost_entry = tk.Entry(form, width=30)
        self.unit_cost_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(form, text="Stock Qty:", bg="#f5f5dc").grid(row=2, column=0, sticky="e")
        self.stock_entry = tk.Entry(form, width=30)
        self.stock_entry.grid(row=2, column=1, padx=5, pady=2)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5dc")
        btn_frame.pack(pady=8)

        ttk.Button(btn_frame, text="Add New", command=self.add_material).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Update", command=self.update_material).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Delete", command=self.delete_material).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Reset Form", command=self.reset_form).pack(side="left", padx=4)

    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = self.db.list_materials()
        for row in rows:
            self.tree.insert("", "end", values=(row["id"], row["name"], row["unit_cost"], row["stock_quantity"]))

    def reset_form(self):
        self.selected_id = None
        self.name_entry.delete(0, tk.END)
        self.unit_cost_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)

    def on_select(self, action):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])["values"]
        self.selected_id = item[0]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, item[1])
        self.unit_cost_entry.delete(0, tk.END)
        self.unit_cost_entry.insert(0, str(item[2]))
        self.stock_entry.delete(0, tk.END)
        self.stock_entry.insert(0, str(item[3]))

    def add_material(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        try:
            unit_cost = float(self.unit_cost_entry.get())
            stock = float(self.stock_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid input")
            return
        self.db.add_material(name, unit_cost, stock)
        messagebox.showinfo("Success", "Material added")
        self.load_data()
        self.reset_form()

    def update_material(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Nothing selected")
            return
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        try:
            unit_cost = float(self.unit_cost_entry.get())
            stock = float(self.stock_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid input")
            return
        self.db.update_material(self.selected_id, name, unit_cost, stock)
        messagebox.showinfo("Success", "Material updated")
        self.load_data()

    def delete_material(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a material to delete")
            return
        if not messagebox.askyesno("Confirm", "Delete this material?"):
            return
        self.db.delete_material(self.selected_id)
        messagebox.showinfo("Deleted", "Material deleted")
        self.load_data()
        self.reset_form()
