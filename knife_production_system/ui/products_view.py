import tkinter as tk
from tkinter import ttk, messagebox


class ProductsView(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg="#f5f5dc")
        self.db = db
        self.selected_product_id = None
        self.materials_cache = []
        self.build_ui()
        self.load_products()

    def build_ui(self):
        tk.Label(self, text="Products", font=("Arial", 18), bg="#f5f5dc").pack(pady=8)

        # Products Treeview
        columns = ("ID", "Name", "Price", "Description")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for c in columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150)
        self.tree.pack(fill="x", padx=12, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_product_select)

        # Product form
        form = tk.Frame(self, bg="#f5f5dc")
        form.pack(pady=8, fill="x", padx=12)

        tk.Label(form, text="Name:", bg="#f5f5dc").grid(row=0, column=0, sticky="e")
        self.name_entry = tk.Entry(form, width=30)
        self.name_entry.grid(row=0, column=1, pady=2, padx=5)

        tk.Label(form, text="Price:", bg="#f5f5dc").grid(row=1, column=0, sticky="e")
        self.price_entry = tk.Entry(form, width=30)
        self.price_entry.grid(row=1, column=1, pady=2, padx=5)

        tk.Label(form, text="Description:", bg="#f5f5dc").grid(row=2, column=0, sticky="ne")
        self.desc_text = tk.Text(form, width=40, height=3)
        self.desc_text.grid(row=2, column=1, pady=2, padx=5)

        btn_frame = tk.Frame(self, bg="#f5f5dc")
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text="Add New", command=self.add_product).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Update", command=self.update_product).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Delete", command=self.delete_product).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Reset Form", command=self.reset_form).pack(side="left", padx=4)

        # Product Material section
        sep = ttk.Separator(self, orient="horizontal")
        sep.pack(fill="x", pady=8)

        tk.Label(self, text="Product Materials", font=("Arial", 16), bg="#f5f5dc").pack()

        pm_frame = tk.Frame(self, bg="#f5f5dc")
        pm_frame.pack(fill="both", expand=True, padx=12, pady=6)

        self.pm_tree = ttk.Treeview(pm_frame, columns=("PM_ID", "Material", "Qty", "Unit Cost"), show="headings", height=6)
        for c in ("PM_ID", "Material", "Qty", "Unit Cost"):
            self.pm_tree.heading(c, text=c)
            self.pm_tree.column(c, width=120)
        self.pm_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(pm_frame, orient="vertical", command=self.pm_tree.yview)
        self.pm_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Add material to product
        add_pm_frame = tk.Frame(self, bg="#f5f5dc")
        add_pm_frame.pack(pady=6)

        tk.Label(add_pm_frame, text="Material:", bg="#f5f5dc").grid(row=0, column=0)
        self.materials_combo = ttk.Combobox(add_pm_frame, width=25, state="readonly")
        self.materials_combo.grid(row=0, column=1, padx=5)

        tk.Label(add_pm_frame, text="Quantity Used:", bg="#f5f5dc").grid(row=1, column=0)
        self.pm_qty_entry = tk.Entry(add_pm_frame, width=10)
        self.pm_qty_entry.grid(row=1, column=1, sticky="w")

        tk.Label(add_pm_frame, text="Unit Cost (opt):", bg="#f5f5dc").grid(row=2, column=0)
        self.pm_cost_entry = tk.Entry(add_pm_frame, width=10)
        self.pm_cost_entry.grid(row=2, column=1, sticky="w")

        ttk.Button(add_pm_frame, text="Add Material to Product", command=self.add_material_to_product).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(add_pm_frame, text="Remove Selected Material", command=self.remove_selected_product_material).grid(row=4, column=0, columnspan=2, pady=5)

    def load_products(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = self.db.list_products()
        for row in rows:
            self.tree.insert("", "end",
                             values=(row["id"], row["name"], row["price"], row["description"] or ""))

        self.load_materials_cache()

    def load_materials_cache(self):
        self.materials_cache = self.db.list_materials()
        names = [m["name"] for m in self.materials_cache]
        self.materials_combo["values"] = names

    def reset_form(self):
        self.selected_product_id = None
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.pm_tree.delete(*self.pm_tree.get_children())

    def on_product_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_product_id = vals[0]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, vals[1])
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, str(vals[2]))
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", vals[3])
        self.load_product_materials()

    def add_product(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        try:
            price = float(self.price_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
            return
        desc = self.desc_text.get("1.0", tk.END).strip()
        pid = self.db.add_product(name, price, desc)
        messagebox.showinfo("Success", f"Product added (ID {pid})")
        self.load_products()
        self.reset_form()

    def update_product(self):
        if not self.selected_product_id:
            messagebox.showwarning("Select", "Select a product to update")
            return
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        try:
            price = float(self.price_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
            return
        desc = self.desc_text.get("1.0", tk.END).strip()
        self.db.update_product(self.selected_product_id, name, price, desc)
        messagebox.showinfo("Success", "Product updated")
        self.load_products()

    def delete_product(self):
        if not self.selected_product_id:
            messagebox.showwarning("Select", "Select a product to delete")
            return
        if not messagebox.askyesno("Confirm", "Delete this product and its material relations?"):
            return
        self.db.delete_product(self.selected_product_id)
        messagebox.showinfo("Deleted", "Product deleted")
        self.load_products()
        self.reset_form()

    def load_product_materials(self):
        self.pm_tree.delete(*self.pm_tree.get_children())
        if not self.selected_product_id:
            return
        rows = self.db.list_product_materials(self.selected_product_id)
        for row in rows:
            self.pm_tree.insert(
                "",
                "end",
                values=(row["id"], row["material_name"], row["quantity_used"], row["unit_cost"])
            )

    def add_material_to_product(self):
        if not self.selected_product_id:
            messagebox.showwarning("Select", "Select a product first")
            return
        mat_name = self.materials_combo.get()
        if not mat_name:
            messagebox.showerror("Error", "Select a material")
            return
        try:
            qty = float(self.pm_qty_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
            return
        cost_text = self.pm_cost_entry.get().strip()
        unit_cost = float(cost_text) if cost_text else None

        mat = next((m for m in self.materials_cache if m["name"] == mat_name), None)
        if not mat:
            messagebox.showerror("Error", "Material not found")
            return

        self.db.add_product_material(self.selected_product_id, mat["id"], qty, unit_cost)
        self.load_product_materials()
        self.pm_qty_entry.delete(0, tk.END)
        self.pm_cost_entry.delete(0, tk.END)

    def remove_selected_product_material(self):
        sel = self.pm_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a product-material row to remove")
            return
        pm_id = self.pm_tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", "Remove this material from product?"):
            return
        self.db.delete_product_material(pm_id)
        self.load_product_materials()