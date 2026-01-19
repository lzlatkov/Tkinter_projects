import tkinter as tk
from tkinter import ttk, messagebox
from database import db


class ProductionView(tk.Frame):
    def __init__(self, parent, db_module):
        super().__init__(parent, bg="#f5f5dc")
        self.db = db_module

        tk.Label(self, text="Production Overview", font=("Arial", 20), bg="#f5f5dc").pack(pady=10)

        container = tk.Frame(self, bg="#f5f5dc")
        container.pack(fill="both", expand=True)

        # Left
        left_frame = tk.Frame(container, bg="#f5f5dc")
        left_frame.pack(side="left", fill="both", expand=True)

        columns = ("ID", "Product", "Status")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=20)
        for c in columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150)

        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Right
        self.details_frame = tk.Frame(container, bg="#fff8dc", relief="groove", bd=2)
        self.details_frame.pack(side="right", fill="y", padx=10, pady=10)

        tk.Label(self.details_frame, text="Production Details", font=("Arial", 16), bg="#fff8dc").pack(pady=10)

        self.details_text = tk.Text(self.details_frame, width=40, height=25, bg="#fff8dc")
        self.details_text.pack(padx=10, pady=10)

        btn_frame = tk.Frame(self, bg="#f5f5dc")
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="View Details", command=self.show_details).pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Mark as Completed", command=self.mark_selected_complete).pack(side="left", padx=5)
        self.load_data()

    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        rows = db.list_production()
        for row in rows:
            self.tree.insert("", "end", values=(row["id"], row["product_name"], row["status"]))

    def show_details(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Nothing selected")
            return

        prod_id = self.tree.item(sel[0])["values"][0]
        prod_row = db.get_production(prod_id)

        if not prod_row:
            return

        product_id = prod_row["product_id"]
        order_id = prod_row["order_id"]
        customer_id = prod_row["customer_id"]

        product = db.get_product(product_id)
        materials = db.list_product_materials(product_id)
        customer = db.get_customer(customer_id) if customer_id else None

        self.details_text.delete("1.0", tk.END)

        self.details_text.insert(tk.END, f"Production ID: {prod_id}\n")
        self.details_text.insert(tk.END, f"Order ID: {order_id}\n")
        self.details_text.insert(tk.END, f"Product: {product['name']}\n")
        self.details_text.insert(tk.END, f"Status: {prod_row['status']}\n\n")

        self.details_text.insert(tk.END, "Customer Information:\n")
        self.details_text.insert(tk.END, "----------------------\n")

        if customer:
            self.details_text.insert(tk.END, f"Name: {customer['first_name']} {customer['last_name']}\n")
            self.details_text.insert(tk.END, f"Email: {customer['email'] or 'N/A'}\n")
            self.details_text.insert(tk.END, f"Phone: {customer['phone'] or 'N/A'}\n\n")
        else:
            self.details_text.insert(tk.END, "No customer data found.\n\n")

        self.details_text.insert(tk.END, "Materials Required:\n")
        self.details_text.insert(tk.END, "----------------------\n")

        if not materials:
            self.details_text.insert(tk.END, "No materials assigned.\n")
        else:
            for m in materials:
                self.details_text.insert(
                    tk.END, f"{m['material_name']} - {m['quantity_used']} units\n"
                )

    def mark_selected_complete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Nothing selected")
            return
        prod_id = self.tree.item(sel[0])["values"][0]
        try:
            db.complete_production_with_materials(prod_id)
            messagebox.showinfo("Done", "Production completed")
        except Exception as e:
            messagebox.showerror("Error", str(e))

        self.load_data()
        
