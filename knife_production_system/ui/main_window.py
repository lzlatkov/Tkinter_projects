import tkinter as tk
from .materials_view import MaterialsView
from .products_view import ProductsView
from .customers_view import CustomersView
from .orders_view import OrdersView
from .production_view import ProductionView


class MainWindow(tk.Tk):
    def __init__(self, db_module):
        super().__init__()
        self.db = db_module
        self.title("Knife Production Management System")
        self.geometry("1100x650")
        self.configure(bg="#e0e0e0")

        self.create_menu()

        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(fill="both", expand=True)

        # Start with Materials view
        self.load_view(MaterialsView)

    def create_menu(self):
        menu_bar = tk.Menu(self)

        # Materials
        materials_menu = tk.Menu(menu_bar, tearoff=0)
        materials_menu.add_command(
            label="Materials",
            command=lambda: self.load_view(MaterialsView)
        )
        menu_bar.add_cascade(label="Materials", menu=materials_menu)

        # Products
        products_menu = tk.Menu(menu_bar, tearoff=0)
        products_menu.add_command(
            label="Products",
            command=lambda: self.load_view(ProductsView)
        )
        menu_bar.add_cascade(label="Products", menu=products_menu)

        # Customers
        customers_menu = tk.Menu(menu_bar, tearoff=0)
        customers_menu.add_command(
            label="Customers",
            command=lambda: self.load_view(CustomersView)
        )
        menu_bar.add_cascade(label="Customers", menu=customers_menu)

        # Orders
        orders_menu = tk.Menu(menu_bar, tearoff=0)
        orders_menu.add_command(
            label="Orders",
            command=lambda: self.load_view(OrdersView)
        )
        menu_bar.add_cascade(label="Orders", menu=orders_menu)

        self.config(menu=menu_bar)

        # Production
        production_menu = tk.Menu(menu_bar, tearoff=0)
        production_menu.add_command(
            label="Production Overview",
            command=lambda: self.load_view(ProductionView)
        )
        menu_bar.add_cascade(label="Production", menu=production_menu)

    def load_view(self, view_class, **kwargs):
        """
        view_class: a Frame subclass, e.g. MaterialsView
        kwargs: extra args to pass to the view_class if needed
        """
        for c in self.content_frame.winfo_children():
            c.destroy()
        frame = view_class(self.content_frame, self.db, **kwargs)
        frame.pack(fill="both", expand=True)