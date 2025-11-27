import tkinter as tk
from tkinter import ttk, messagebox


class OrdersView(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg="#fafad2")
        self.db = db
        self.order_lines = []  # (product_id, qty)
        self.selected_order_id = None
        self.build_ui()
        self.load_customers()
        self.load_products()
        self.load_orders()

    def build_ui(self):
        tk.Label(self, text="Orders", font=("Arial", 18), bg="#fafad2").pack(pady=8)

        top_frame = tk.Frame(self, bg="#fafad2")
        top_frame.pack(fill="x", padx=12)

        # Create Order
        create_frame = tk.LabelFrame(top_frame, text="Create New Order", bg="#fafad2")
        create_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        tk.Label(create_frame, text="Customer:", bg="#fafad2").grid(row=0, column=0, sticky="e")
        self.customer_combo = ttk.Combobox(create_frame, width=30, state="readonly")
        self.customer_combo.grid(row=0, column=1, padx=5, pady=2)

        # Add product
        tk.Label(create_frame, text="Product:", bg="#fafad2").grid(row=1, column=0, sticky="e")
        self.product_combo = ttk.Combobox(create_frame, width=30, state="readonly")
        self.product_combo.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(create_frame, text="Quantity:", bg="#fafad2").grid(row=2, column=0, sticky="e")
        self.qty_entry = tk.Entry(create_frame, width=10)
        self.qty_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        ttk.Button(create_frame, text="Add Line", command=self.add_order_line).grid(row=3, column=0, columnspan=2, pady=4)

        # Order lines
        self.lines_tree = ttk.Treeview(create_frame, columns=("Product", "Qty"), show="headings", height=5)
        self.lines_tree.heading("Product", text="Product")
        self.lines_tree.heading("Qty", text="Quantity")
        self.lines_tree.column("Product", width=160)
        self.lines_tree.column("Qty", width=80)
        self.lines_tree.grid(row=4, column=0, columnspan=2, pady=4, sticky="nsew")

        create_frame.grid_columnconfigure(1, weight=1)
        create_frame.grid_rowconfigure(4, weight=1)

        ttk.Button(create_frame, text="Clear Lines", command=self.clear_order_lines).grid(row=5, column=0, pady=4)
        ttk.Button(create_frame, text="Create Order", command=self.create_order).grid(row=5, column=1, pady=4, sticky="e")

        # Orders list
        list_frame = tk.LabelFrame(top_frame, text="Existing Orders", bg="#fafad2")
        list_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        cols = ("ID", "Date", "Customer", "Status", "Total")
        self.orders_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        for c in cols:
            self.orders_tree.heading(c, text=c)
            self.orders_tree.column(c, width=120)
        self.orders_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.orders_tree.bind("<<TreeviewSelect>>", self.on_order_select)

        # Order details
        details_frame = tk.LabelFrame(self, text="Order Details", bg="#fafad2")
        details_frame.pack(fill="both", expand=True, padx=12, pady=8)

        dcols = ("Product", "Qty", "Subtotal")
        self.details_tree = ttk.Treeview(details_frame, columns=dcols, show="headings", height=8)
        for c in dcols:
            self.details_tree.heading(c, text=c)
            self.details_tree.column(c, width=160)
        self.details_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def load_customers(self):
        self.customers = self.db.list_customers()
        names = [f'{c["first_name"]} {c["last_name"]}' for c in self.customers]
        self.customer_combo["values"] = names

    def load_products(self):
        self.products = self.db.list_products()
        names = [p["name"] for p in self.products]
        self.product_combo["values"] = names

    def add_order_line(self):
        pname = self.product_combo.get()
        if not pname:
            messagebox.showerror("Error", "Select a product")
            return
        try:
            qty = int(self.qty_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer")
            return
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be > 0")
            return
        prod = next((p for p in self.products if p["name"] == pname), None)
        if not prod:
            messagebox.showerror("Error", "Product not found")
            return
        self.order_lines.append((prod["id"], qty))
        self.lines_tree.insert("", "end", values=(pname, qty))
        self.qty_entry.delete(0, tk.END)

    def clear_order_lines(self):
        self.order_lines = []
        self.lines_tree.delete(*self.lines_tree.get_children())

    def create_order(self):
        cname = self.customer_combo.get()
        if not cname:
            messagebox.showerror("Error", "Select a customer")
            return
        if not self.order_lines:
            messagebox.showerror("Error", "Add at least one line")
            return
        cust = next((c for c in self.customers if f'{c["first_name"]} {c["last_name"]}' == cname), None)
        if not cust:
            messagebox.showerror("Error", "Customer not found")
            return
        order_id = self.db.create_order(cust["id"], self.order_lines)
        messagebox.showinfo("Success", f"Order {order_id} created")
        self.clear_order_lines()
        self.load_orders()

    def load_orders(self):
        self.orders_tree.delete(*self.orders_tree.get_children())
        rows = self.db.list_orders()
        for row in rows:
            self.orders_tree.insert(
                "",
                "end",
                values=(row["id"], row["date_created"], row["customer_name"], row["status"], row["total_price"])
            )

    def on_order_select(self, event):
        sel = self.orders_tree.selection()
        if not sel:
            return
        vals = self.orders_tree.item(sel[0])["values"]
        self.selected_order_id = vals[0]
        self.load_order_details()

    def load_order_details(self):
        self.details_tree.delete(*self.details_tree.get_children())
        if not self.selected_order_id:
            return
        rows = self.db.get_order_products(self.selected_order_id)
        for row in rows:
            self.details_tree.insert(
                "",
                "end",
                values=(row["product_name"], row["quantity"], row["subtotal_value"])
            )
