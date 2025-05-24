import json
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("GUI")
root.resizable(width=False, height=False)

SPACE = ["Star", "Planet", "Comet"]
REQUIRED_KEYS = {"entry", "radiobutton", "checkbuttons", "spinbox", "optionmenu"}

def save():
    data = {
        "entry": entry_var.get(),
        "radiobutton": radiobutton_var.get(),
        "checkbuttons": {item: var.get() for item, var in checkbutton_items.items()},
        "spinbox": spinbox_var.get(),
        "optionmenu": optionmenu_var.get(),
    }
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)
    label.config(text="Data saved successfully", fg="green", font=("Arial", 12))

def load():
    try:
        with open("data.json", "r") as file:
            data = json.load(file)

        if set(data.keys()) != REQUIRED_KEYS:
            raise ValueError("Invalid keys in JSON file")

        if (data["entry"] not in SPACE
            or data["radiobutton"] not in SPACE
            or data["spinbox"] not in SPACE
            or data["optionmenu"] not in SPACE
            or not isinstance(data["checkbuttons"], dict)):
            raise ValueError("Invalid JSON file or file not found")

        entry_var.set(data["entry"])
        radiobutton_var.set(data["radiobutton"])
        for item, value in data["checkbuttons"].items():
            if item in checkbutton_items and isinstance(value, bool):
                checkbutton_items[item].set(value)
            else:
                raise ValueError("Invalid JSON file or file not found")
        spinbox_var.set(data["spinbox"])
        optionmenu_var.set(data["optionmenu"])
        label.config(text="Data loaded successfully", fg="green", font=("Arial", 12))
    except (FileNotFoundError, json.JSONDecodeError):
        messagebox.showerror("Error", "Invalid JSON file or file not found")
    except ValueError as e:
        messagebox.showerror("Error", str(e))


def reset():
    entry_var.set("")
    radiobutton_var.set(SPACE[0])
    spinbox_var.set(SPACE[0])
    optionmenu_var.set(SPACE[0])
    for item in SPACE:
        checkbutton_items[item].set(False)
    label.config(text="")

def is_valid_data():
    if (entry_var.get() not in SPACE
        or radiobutton_var.get() == ""
        or spinbox_var.get() == ""
        or optionmenu_var.get() == ""
        or not any(var.get() for var in checkbutton_items.values())):
        label.config(text="Invalid data", fg="red", font=("Arial", 12))
        return False
    label.config(text="", fg="black")
    return True

def get_values():
    if is_valid_data():
        counter = {item: 0 for item in SPACE}
        sources = [
            entry_var.get(),
            radiobutton_var.get(),
            spinbox_var.get(),
            optionmenu_var.get(),
        ] + [item for item, var in checkbutton_items.items() if var.get()]

        for item in sources:
            if item in counter:
                counter[item] += 1

        label.config(text=", ".join(f"{item}={counter[item]}" for item in SPACE), fg="black", font=("Arial", 12))

frame = tk.Frame(root, padx=5, pady=5)
frame.pack(fill="both", expand=False)

# Entry ---------------------------------------------------------------
entry_var = tk.StringVar(value="Star")
entry_frame = tk.Frame(frame, relief="solid")
entry_frame.pack(padx=5, pady=5, fill="x")
entry = tk.Entry(entry_frame, bg="white", textvariable=entry_var, font=("Arial", 12))
entry.pack(padx=5, pady=5, fill="x")

# Radiobutton --------------------------------------------------------
radiobutton_var = tk.StringVar(value="Star")
radiobutton_frame = tk.LabelFrame(frame, text="Radiobutton", bd=1, relief="solid")
radiobutton_frame.pack(padx=5, pady=5, fill="x")

for item in SPACE:
    tk.Radiobutton(radiobutton_frame, variable=radiobutton_var, value=item, text=item, font=("Arial", 12)).pack(anchor="w")

# Checkbutton --------------------------------------------------------
checkbutton_items = {item: tk.BooleanVar(value=(item == "Star")) for item in SPACE}
checkbutton_frame = tk.LabelFrame(frame, text="Checkbutton")
checkbutton_frame.pack(padx=5, pady=5, fill="x")

for item in SPACE:
    tk.Checkbutton(checkbutton_frame, variable=checkbutton_items[item], text=item, font=("Arial", 12)).pack(anchor="w")

# Spinbox ------------------------------------------------------------
spinbox_var = tk.StringVar(value="Star")
spinbox_frame = tk.Frame(frame, relief="solid")
spinbox_frame.pack(padx=5, pady=5, fill="x")
spinbox = tk.Spinbox(spinbox_frame, textvariable=spinbox_var, values=SPACE, state="readonly", font=("Arial", 12))
spinbox.pack(padx=5, pady=5, fill="x")

# OptionMenu ---------------------------------------------------------
optionmenu_var = tk.StringVar(value="Star")
optionmenu_frame = tk.Frame(frame, relief="solid")
optionmenu_frame.pack(padx=5, pady=5, fill="x")
optionmenu = tk.OptionMenu(optionmenu_frame, optionmenu_var, *SPACE)
optionmenu.pack(padx=5, pady=5, fill="x")

# Label --------------------------------------------------------------
label_frame = tk.Frame(frame, relief="solid")
label_frame.pack(padx=5, pady=5, fill="x")
label = tk.Label(label_frame, bg="white")
label.pack(padx=5, pady=5, fill="x")

buttons_frame = tk.Frame(frame, relief="solid")
buttons_frame.pack(padx=5, pady=5, fill="x")

buttons_frame.columnconfigure(0, weight=1)
buttons_frame.columnconfigure(1, weight=1)

get_values_button = tk.Button(buttons_frame, text="Get Values", command=get_values, font=("Arial", 12), width=15)
get_values_button.grid(row=0, column=0, padx=5, pady=5, sticky="we")

reset_button = tk.Button(buttons_frame, text="Reset", command=reset, font=("Arial", 12), bg="red", width=15)
reset_button.grid(row=0, column=1, padx=5, pady=5, sticky="we")

save_button = tk.Button(buttons_frame, text="Save", command=save, bg="green", font=("Arial", 12))
save_button.grid(row=1, column=0, padx=5, pady=5, sticky="we")

load_button = tk.Button(buttons_frame, text="Load", command=load, bg="yellow", font=("Arial", 12))
load_button.grid(row=1, column=1, padx=5, pady=5, sticky="we")

root.mainloop()