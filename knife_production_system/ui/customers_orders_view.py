import tkinter as tk
from tkinter import ttk, messagebox


class CustomersOrdersView(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg="#f5f5dc")
        self.db = db

        self.selected_customer_id = None
        self.selected_customer_name = None
        self.order_lines = []
        self.selected_order_id = None

        self.customers = []
        self.products = []
        self.build_ui()
        self.load_customers()
        self.load_products()
        self.load_orders()

    def build_ui(self):
        main_frame = tk.Frame(self, bg="#f5f5dc")
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)
# Customers

        left = tk.Frame(main_frame, bg="#f5f5dc")
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        tk.Label(left, text="Customers", font=("Arial", 18), bg="#f5f5dc").pack(pady=4)

        cols = ("ID", "First Name", "Last Name", "Email", "Phone")
        self.cust_tree = ttk.Treeview(left, columns=cols, show="headings", height=10)
        for c in cols:
            self.cust_tree.heading(c, text=c)
            self.cust_tree.column(c, width=120)
        self.cust_tree.pack(fill="x", padx=4, pady=4)
        self.cust_tree.bind("<<TreeviewSelect>>", self.on_customer_select)

        form = tk.Frame(left, bg="#f5f5dc")
        form.pack(pady=4)

        tk.Label(form, text="First Name:", bg="#f5f5dc").grid(row=0, column=0, sticky="e")
        self.fn_entry = tk.Entry(form, width=25)
        self.fn_entry.grid(row=0, column=1, padx=4, pady=2)

        tk.Label(form, text="Last Name:", bg="#f5f5dc").grid(row=1, column=0, sticky="e")
        self.ln_entry = tk.Entry(form, width=25)
        self.ln_entry.grid(row=1, column=1, padx=4, pady=2)

        tk.Label(form, text="Email:", bg="#f5f5dc").grid(row=2, column=0, sticky="e")
        self.email_entry = tk.Entry(form, width=25)
        self.email_entry.grid(row=2, column=1, padx=4, pady=2)

        tk.Label(form, text="Phone:", bg="#f5f5dc").grid(row=3, column=0, sticky="e")
        self.phone_entry = tk.Entry(form, width=25)
        self.phone_entry.grid(row=3, column=1, padx=4, pady=2)

        btn_frame = tk.Frame(left, bg="#f5f5dc")
        btn_frame.pack(pady=4)

        ttk.Button(btn_frame, text="Add New", command=self.add_customer).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Update", command=self.update_customer).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Delete", command=self.delete_customer).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Reset Form", command=self.reset_customer_form).pack(side="left", padx=3)

# Orders
        right = tk.Frame(main_frame, bg="#fafad2")
        right.pack(side="right", fill="both", expand=True, padx=(6, 0))

        tk.Label(right, text="Orders", font=("Arial", 18), bg="#fafad2").pack(pady=4)

        top_frame = tk.Frame(right, bg="#fafad2")
        top_frame.pack(fill="x", padx=6, pady=4)

        create_frame = tk.LabelFrame(top_frame, text="Create New Order", bg="#fafad2")
        create_frame.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        tk.Label(create_frame, text="Customer:", bg="#fafad2").grid(row=0, column=0, sticky="e")
        self.customer_label = tk.Label(create_frame, text="(no customer selected)", bg="#fafad2", anchor="w")
        self.customer_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        tk.Label(create_frame, text="Product:", bg="#fafad2").grid(row=1, column=0, sticky="e")
        self.product_combo = ttk.Combobox(create_frame, width=30, state="readonly")
        self.product_combo.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(create_frame, text="Quantity:", bg="#fafad2").grid(row=2, column=0, sticky="e")
        self.qty_entry = tk.Entry(create_frame, width=10)
        self.qty_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        ttk.Button(create_frame, text="Add Line", command=self.add_order_line).grid(row=3, column=0, columnspan=2,
                                                                                    pady=4)
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

        list_frame = tk.LabelFrame(top_frame, text="Existing Orders", bg="#fafad2")
        list_frame.pack(side="right", fill="both", expand=True, padx=4, pady=4)

        order_cols = ("ID", "Date", "Customer", "Status", "Total")
        self.orders_tree = ttk.Treeview(list_frame, columns=order_cols, show="headings", height=10)
        for c in order_cols:
            self.orders_tree.heading(c, text=c)
            self.orders_tree.column(c, width=110)
        self.orders_tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.orders_tree.bind("<<TreeviewSelect>>", self.on_order_select)

        # order details
        details_frame = tk.LabelFrame(right, text="Order Details", bg="#fafad2")
        details_frame.pack(fill="both", expand=True, padx=8, pady=6)

        details_cols = ("Product", "Qty", "Subtotal")
        self.details_tree = ttk.Treeview(details_frame, columns=details_cols, show="headings", height=8)
        for c in details_cols:
            self.details_tree.heading(c, text=c)
            self.details_tree.column(c, width=150)
        self.details_tree.pack(fill="both", expand=True, padx=4, pady=4)

    # Customer

    def load_customers(self):
        self.customers = self.db.list_customers()
        self.cust_tree.delete(*self.cust_tree.get_children()) # deletes all rows inside the Treeview widget
        for row in self.customers:
            self.cust_tree.insert("", "end", values=(
            row["id"], row["first_name"], row["last_name"], row["email"] or "", row["phone"] or ""))

    def reset_customer_form(self):
        self.selected_customer_id = None
        self.selected_customer_name = None
        self.customer_label.config(text="(no customer selected)")
        for e in (self.fn_entry, self.ln_entry, self.email_entry, self.phone_entry):
            e.delete(0, tk.END)
        self.load_orders()

    def on_customer_select(self, event):
        sel = self.cust_tree.selection()
        if not sel:
            return
        vals = self.cust_tree.item(sel[0])["values"]
        self.selected_customer_id = vals[0]
        self.selected_customer_name = f"{vals[1]} {vals[2]}"

        self.fn_entry.delete(0, tk.END)
        self.fn_entry.insert(0, vals[1])
        self.ln_entry.delete(0, tk.END)
        self.ln_entry.insert(0, vals[2])
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, vals[3])
        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, vals[4])

        self.customer_label.config(text=self.selected_customer_name)

        self.load_orders()

    def add_customer(self):
        fn = self.fn_entry.get().strip()
        ln = self.ln_entry.get().strip()
        if not fn or not ln:
            messagebox.showerror("Error", "First and last name are required")
            return
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        self.db.add_customer(fn, ln, email, phone)
        messagebox.showinfo("Success", "Customer added")
        self.load_customers()
        self.reset_customer_form()

    def update_customer(self):
        if not self.selected_customer_id:
            messagebox.showwarning("Select", "Select a customer")
            return
        fn = self.fn_entry.get().strip()
        ln = self.ln_entry.get().strip()
        if not fn or not ln:
            messagebox.showerror("Error", "First and last name are required")
            return
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        self.db.update_customer(self.selected_customer_id, fn, ln, email, phone)
        messagebox.showinfo("Success", "Customer updated")
        self.load_customers()

    def delete_customer(self):
        if not self.selected_customer_id:
            messagebox.showwarning("Select", "Select a customer")
            return
        if not messagebox.askyesno("Confirm", "Delete this customer?"):
            return
        self.db.delete_customer(self.selected_customer_id)
        messagebox.showinfo("Deleted", "Customer deleted")
        self.load_customers()
        self.reset_customer_form()

    def load_products(self):
        self.products = self.db.list_products()
        names = [p["name"] for p in self.products]
        self.product_combo["values"] = names

    def add_order_line(self):
        product_name = self.product_combo.get()
        if not product_name:
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
        prod = next((p for p in self.products if p["name"] == product_name), None)
        if not prod:
            messagebox.showerror("Error", "Product not found")
            return
        self.order_lines.append((prod["id"], qty))
        self.lines_tree.insert("", "end", values=(product_name, qty))
        self.qty_entry.delete(0, tk.END)

    def clear_order_lines(self):
        self.order_lines = []
        self.lines_tree.delete(*self.lines_tree.get_children())

    def create_order(self):
        if not self.selected_customer_id:
            messagebox.showerror("Error", "Select a customer on the left")
            return
        if not self.order_lines:
            messagebox.showerror("Error", "Add at least one order line")
            return

        order_id = self.db.create_order(self.selected_customer_id, self.order_lines)
        messagebox.showinfo("Success", f"Order {order_id} created")
        self.clear_order_lines()
        self.load_orders()

    def load_orders(self):
        self.orders_tree.delete(*self.orders_tree.get_children()) # deletes all rows inside the Treeview widget
        rows = self.db.list_orders()
        for row in rows:
            if self.selected_customer_name and row["customer_name"] != self.selected_customer_name:
                continue
            self.orders_tree.insert("",  "end", values=(row["id"], row["date_created"][:16], row["customer_name"], row["status"], row["total_price"]))
        self.details_tree.delete(*self.details_tree.get_children())
        self.selected_order_id = None

    def on_order_select(self, action):
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
            self.details_tree.insert("", "end", values=(row["product_name"], row["quantity"], row["subtotal_value"]))
