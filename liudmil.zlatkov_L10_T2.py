import tkinter as tk
import random
from tkinter import messagebox


WORDS = ["компютър", "програма", "питон", "училище", "интернет", "прозорец", "клавиатура", "монитор", "игра", "данни"]
MAX_TRIES = 6


secret_word = random.choice(WORDS)
guessed_letters = []
wrong_attempts = 0


def update_display():
    # display_word = " ".join([letter if letter in guessed_letters else "_" for letter in secret_word])
    display_word = ""
    for i, letter in enumerate(secret_word):
        if i == 0 or i == len(secret_word) - 1 or letter in guessed_letters:
            display_word += letter + " "
        else:
            display_word += "_ "
    label_word.config(text=display_word)
    label_tries.config(text=f"Грешки: {wrong_attempts}/{MAX_TRIES}")


def guess_letter():
    global wrong_attempts
    letter = entry_letter.get().lower()

    if not letter.isalpha() or len(letter) != 1:
        messagebox.showwarning("Грешка", "Моля, въведете само една буква!")
        return

    if letter in guessed_letters:
        messagebox.showinfo("Инфо", "Вече сте въвели тази буква!")
        return

    guessed_letters.append(letter)

    if letter not in secret_word:
        wrong_attempts += 1

    update_display()

    if all(l in guessed_letters for l in secret_word):
        messagebox.showinfo("Поздравления!", f"Познахте думата: {secret_word.upper()} 🎉")
        reset_game()
    elif wrong_attempts >= MAX_TRIES:
        messagebox.showerror("Край на играта", f"Думата беше: {secret_word.upper()}")
        reset_game()

    entry_letter.delete(0, tk.END)


def reset_game():
    global secret_word, guessed_letters, wrong_attempts
    secret_word = random.choice(WORDS)
    guessed_letters = []
    wrong_attempts = 0
    update_display()


root = tk.Tk()
root.title("Игра: Бесеница")

label_title = tk.Label(root, text="Познай думата!", font=("Arial", 16, "bold"))
label_title.pack(pady=10)

label_word = tk.Label(root, text="", font=("Courier", 20))
label_word.pack(pady=10)

frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Буква:").grid(row=0, column=0, padx=5)
entry_letter = tk.Entry(frame_input, width=5, font=("Arial", 14))
entry_letter.grid(row=0, column=1, padx=5)

btn_guess = tk.Button(frame_input, text="Познай", command=guess_letter, bg="#4CAF50", fg="white")
btn_guess.grid(row=0, column=2, padx=5)

label_tries = tk.Label(root, text=f"Грешки: {wrong_attempts}/{MAX_TRIES}", font=("Arial", 12))
label_tries.pack(pady=5)

btn_reset = tk.Button(root, text="Нова игра", command=reset_game, bg="#4CAF50", fg="white")
btn_reset.pack(pady=10)

update_display()

root.mainloop()