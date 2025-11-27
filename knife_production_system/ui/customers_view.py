import tkinter as tk
from tkinter import ttk, messagebox


class CustomersView(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg="#f5f5dc")
        self.db = db
        self.selected_id = None
        self.build_ui()
        self.load_data()

    def build_ui(self):
        tk.Label(self, text="Customers", font=("Arial", 18), bg="#f5f5dc").pack(pady=8)

        cols = ("ID", "First Name", "Last Name", "Email", "Phone")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140)
        self.tree.pack(fill="x", padx=12, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form = tk.Frame(self, bg="#f5f5dc")
        form.pack(pady=8)

        tk.Label(form, text="First Name:", bg="#f5f5dc").grid(row=0, column=0, sticky="e")
        self.fn_entry = tk.Entry(form, width=30)
        self.fn_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form, text="Last Name:", bg="#f5f5dc").grid(row=1, column=0, sticky="e")
        self.ln_entry = tk.Entry(form, width=30)
        self.ln_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(form, text="Email:", bg="#f5f5dc").grid(row=2, column=0, sticky="e")
        self.email_entry = tk.Entry(form, width=30)
        self.email_entry.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(form, text="Phone:", bg="#f5f5dc").grid(row=3, column=0, sticky="e")
        self.phone_entry = tk.Entry(form, width=30)
        self.phone_entry.grid(row=3, column=1, padx=5, pady=2)

        btn_frame = tk.Frame(self, bg="#f5f5dc")
        btn_frame.pack(pady=8)

        ttk.Button(btn_frame, text="Add New", command=self.add_customer).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Update", command=self.update_customer).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Delete", command=self.delete_customer).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Reset Form", command=self.reset_form).pack(side="left", padx=4)

    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = self.db.list_customers()
        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=(row["id"], row["first_name"], row["last_name"], row["email"] or "", row["phone"] or "")
            )

    def reset_form(self):
        self.selected_id = None
        for e in (self.fn_entry, self.ln_entry, self.email_entry, self.phone_entry):
            e.delete(0, tk.END)

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]
        self.fn_entry.delete(0, tk.END); self.fn_entry.insert(0, vals[1])
        self.ln_entry.delete(0, tk.END); self.ln_entry.insert(0, vals[2])
        self.email_entry.delete(0, tk.END); self.email_entry.insert(0, vals[3])
        self.phone_entry.delete(0, tk.END); self.phone_entry.insert(0, vals[4])

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
        self.load_data()
        self.reset_form()

    def update_customer(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a customer")
            return
        fn = self.fn_entry.get().strip()
        ln = self.ln_entry.get().strip()
        if not fn or not ln:
            messagebox.showerror("Error", "First and last name are required")
            return
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        self.db.update_customer(self.selected_id, fn, ln, email, phone)
        messagebox.showinfo("Success", "Customer updated")
        self.load_data()

    def delete_customer(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a customer")
            return
        if not messagebox.askyesno("Confirm", "Delete this customer?"):
            return
        self.db.delete_customer(self.selected_id)
        messagebox.showinfo("Deleted", "Customer deleted")
        self.load_data()
        self.reset_form()