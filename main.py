import json
from random import choice, randint, shuffle
from tkinter import *  # type: ignore
from tkinter import messagebox
from pathlib import Path
import tempfile, shutil
import os

# Optional clipboard + platform-safe helpers
try:
    import pyperclip
except ImportError:
    pyperclip = None
import platform
import subprocess

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "vault.json"

show_password = False

def copy_to_clipboard(text: str):
    """Copy text to clipboard using pyperclip if available; fallback to Tk clipboard."""
    if pyperclip is not None:
        try:
            pyperclip.copy(text)
            return
        except Exception:
            pass
    # Fallback: use Tkinter clipboard if window exists
    try:
        window.clipboard_clear()
        window.clipboard_append(text)
    except Exception:
        # Last resort: ignore if no clipboard available yet
        pass

# ---------------------------- PASSWORD GENERATOR ------------------------------- #
# Password Generator Project
def generate_password():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_letters = [choice(letters) for _ in range(randint(8, 10))]
    password_symbols = [choice(symbols) for _ in range(randint(2, 4))]
    password_numbers = [choice(numbers) for _ in range(randint(2, 4))]

    password_list = password_letters + password_symbols + password_numbers

    shuffle(password_list)

    password = "".join(password_list)

    if not password_input.get():
        password_input.insert(0, string=password)
    copy_to_clipboard(password)


def load_db() -> dict:
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Vault file is corrupted. A backup will be created.")
        backup = DATA_FILE.with_suffix(".bak.json")
        shutil.copy(DATA_FILE, backup)
        return {}


def atomic_write(data: dict):
    temp_file = tempfile.NamedTemporaryFile(delete=False, dir=DATA_DIR, suffix=".tmp", mode="w", encoding="utf-8")
    with temp_file as f:
        json.dump(data, f, indent=4)
    shutil.move(temp_file.name, DATA_FILE)


# ---------------------------- SAVE PASSWORD ------------------------------- #

# my version:
# def save():
#     with open("data.txt", "a") as f:
#         f.write(f"{website_input.get()}|{email_input.get()}|{password_input.get()}\n")
#     website_input.delete(0,END)
#     email_input.delete(0, END)
#     password_input.delete(0, END)

# Udemy version
def save():
    website = website_input.get().lower().strip()
    email = email_input.get()
    password = password_input.get()
    if len(website) == 0 or len(password) == 0:
        messagebox.showinfo(title="Oops", message="Please don't leave any fields empty!")
        return
    else:
        data = load_db()
        if website in data:
            overwrite = messagebox.askyesno("Duplicate", f"An entry for '{website}' exists. Overwrite?")
            if not overwrite:
                return
        data[website] = {"email": email, "password": password}
        atomic_write(data)
        website_input.delete(0, END)
        password_input.delete(0, END)
        website_input.focus()


# ---------------------------- FINDING PASSWORD ------------------------------- #

def find_password():
    website = website_input.get()
    data = load_db()
    found = {k: v for k, v in data.items() if k.lower() == website.lower()}
    if found:
        for k, v in found.items():
            email = v["email"]
            password = v["password"]
            messagebox.showinfo(title=f"{k}", message=f"Email: {email}\nPassword: {password}")
    else:
        open_folder = messagebox.askyesno("Not Found", "No details found. Open data folder?")
        if open_folder:
            system = platform.system()
            try:
                if system == "Darwin":  # macOS
                    subprocess.call(["open", str(DATA_DIR)])
                elif system == "Windows":
                    os.startfile(str(DATA_DIR)) # type: ignore
                else:  # Linux and others
                    subprocess.call(["xdg-open", str(DATA_DIR)])
            except Exception:
                messagebox.showinfo("Info", f"Data directory: {DATA_DIR}")


# ---------------------------- PASSWORD VISIBILITY TOGGLE ------------------------------- #

def toggle_password_visibility():
    global show_password
    show_password = not show_password
    if show_password:
        password_input.config(show="")
        toggle_button.config(text="Hide")
    else:
        password_input.config(show="*")
        toggle_button.config(text="Show")


# ---------------------------- UI SETUP ------------------------------- #
# window_setup
window = Tk()
window.title("Password Manager")
# window.minsize(width=500, height=500)
window.config(padx=50, pady=50)

# Canvas setup
canvas = Canvas(width=200, height=200, highlightthickness=0)
try:
    logo_path = BASE_DIR / "logo.png"
    logo_img = PhotoImage(file=str(logo_path))
except Exception:
    logo_img = None
if logo_img:
    canvas.create_image(100, 100, image=logo_img)
canvas.grid(row=0, column=1)

# Label setup

website_label = Label(text="Website:")
website_label.grid(row=1, column=0)

email_label = Label(text="Email/Username:")
email_label.grid(row=2, column=0)

password_label = Label(text="Password:")
password_label.grid(row=3, column=0)

# Entry setup
website_input = Entry(width=20)
website_input.grid(row=1, column=1)
website_input.focus()

email_input = Entry(width=35)
email_input.insert(0, string="rushikeshreddy3002@gmail.com")
email_input.grid(row=2, column=1, columnspan=2)

password_input = Entry(width=20, show="*")
password_input.grid(row=3, column=1)

# Button setup

generate_password_button = Button(text="Generate Password", width=11, command=generate_password)
generate_password_button.grid(row=3, column=2)

toggle_button = Button(text="Show", width=6, command=toggle_password_visibility)
toggle_button.grid(row=3, column=3)

add_button = Button(text="Add", width=32, command=save)
add_button.grid(row=4, column=1, columnspan=2)

search_button = Button(text="Search", width=11, command=find_password)
search_button.grid(row=1, column=2)

website_input.bind("<Return>", lambda e: save())
email_input.bind("<Return>", lambda e: save())
password_input.bind("<Return>", lambda e: save())





window.mainloop()

