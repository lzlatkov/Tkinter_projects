import tkinter as tk
from tkinter import messagebox
import math


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Графичен калкулатор")

        self.expression = ""
        self.memory = 0

        self.entry = tk.Entry(self, font=("Arial", 20))
        self.entry.grid(row=0, column=0, columnspan=5)

        self.create_buttons()

    def create_buttons(self):
        buttons = [
            ("MC", 1, 0), ("MR", 1, 1), ("M+", 1, 2), ("M-", 1, 3), ("√", 1, 4),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("/", 2, 3), ("n!", 2, 4),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("*", 3, 3), ("±", 3, 4),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("-", 4, 3), ("CE", 4, 4),
            ("0", 5, 0), (".", 5, 1), ("AC", 5, 2), ("+", 5, 3), ("=", 5, 4),
        ]

        for (text, row, col) in buttons:
            btn = tk.Button(self, text=text, width=6, height=2, font=("Arial", 14),
                            command=lambda t=text: self.button_click(t))
            btn.grid(row=row, column=col, padx=5, pady=5)

    def button_click(self, char):
        if char.isdigit() or char == ".":
            self.expression += char
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, self.expression)

        elif char in "+-*/":
            self.expression += char
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, self.expression)

        elif char == "AC":
            self.expression = ""
            self.entry.delete(0, tk.END)

        elif char == "CE":
            self.expression = self.expression[:-1]
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, self.expression)

        elif char == "±":

            try:
                if self.expression:
                    value = float(self.entry.get())
                    value = -value
                    self.expression = str(value)
                    self.entry.delete(0, tk.END)
                    self.entry.insert(tk.END, self.expression)
            except:
                messagebox.showerror("Грешка", "Невалидна операция")

        elif char == "√":
            try:
                value = float(self.entry.get())
                if value < 0:
                    raise ValueError
                result = math.sqrt(value)
                self.expression = str(result)
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, self.expression)
            except:
                messagebox.showerror("Грешка", "Невалиден корен!")

        elif char == "n!":
            try:
                value = int(float(self.entry.get()))
                if value < 0:
                    raise ValueError
                result = math.factorial(value)
                self.expression = str(result)
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, self.expression)
            except:
                messagebox.showerror("Грешка", "Невалиден факториел!")

        elif char in ["MC", "MR", "M+", "M-"]:
            self.memory_action(char)

        elif char == "=":
            try:
                result = eval(self.expression)
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, str(result))
                self.expression = str(result)
            except:
                messagebox.showerror("Грешка", "Невалиден израз")
                self.expression = ""
                self.entry.delete(0, tk.END)

    def memory_action(self, action):
        try:
            value = float(self.entry.get() or 0)
        except:
            value = 0

        if action == "MC":
            self.memory = 0
        elif action == "MR":
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(self.memory))
            self.expression = str(self.memory)
        elif action == "M+":
            self.memory += value
        elif action == "M-":
            self.memory -= value


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
