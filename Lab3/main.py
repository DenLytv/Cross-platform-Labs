import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

FILENAME = "printers.csv"

COMBO_STATUS_VALUES = ("Available", "Not available")

HEADERS = {
    "name": "Model",
    "price": "Price ($)",
    "status": "Availability"
}

COLUMNS = ("name", "price", "status")

def load_data():
    if not os.path.exists(FILENAME):
        return []
    try:
        with open(FILENAME, newline='\n', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = []
            for row in reader:
                if len(row) == len(COLUMNS):
                    name, price, status = row[0].strip(), row[1].strip(), row[2].strip()

                    if not name or float(price) <= 0 or status not in COMBO_STATUS_VALUES:
                        continue
                    data.append((name, price, status))

            return data
    except Exception as ex:
        messagebox.showerror("Error", f"Failed to load data: {ex}")
        return []

def save_data():
    try:
        temp_filename = FILENAME + ".tmp"
        with open(temp_filename, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row_id in tree.get_children():
                writer.writerow(tree.item(row_id)["values"])
        os.replace(temp_filename, FILENAME)
    except Exception as ex:
        messagebox.showerror("Error", f"Failed to save data: {ex}")

root = tk.Tk()
root.title("Printers list")
root.protocol("WM_DELETE_WINDOW", lambda: (save_data(), root.destroy()))

var_name = tk.StringVar()
var_price = tk.IntVar()
var_status = tk.StringVar()
var_search = tk.StringVar()

frame_tree = tk.Frame()
frame_tree.pack(padx=(5, 0), pady=5, fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_tree, orient="vertical",)
scrollbar.pack(side="right", fill="y")

tree = ttk.Treeview(frame_tree, columns=COLUMNS, show="headings", selectmode="browse", height=10, yscrollcommand=scrollbar.set)

for col in COLUMNS:
    tree.heading(col, text=HEADERS[col], anchor="w")
    tree.column(col, width=180 if col == "name" else 100, anchor="w", stretch=True)

tree.pack(fill="both", expand=True)
scrollbar.config(command=tree.yview)

printers = load_data()

for printer in printers:
    tree.insert("", "end", values=printer)

children = tree.get_children()
if children:
    tree.selection_set(children[0])

labelframe_search = tk.LabelFrame(root, text="Search by model")
labelframe_search.pack(padx=5, pady=5, fill="both", expand=True)

labelframe_search.columnconfigure(0, weight=1)
labelframe_search.columnconfigure(1, weight=1)

entry_search = tk.Entry(labelframe_search, textvariable=var_search)
entry_search.grid(column=0, row=0, padx=5, pady=5, sticky="we")

def search():
    substring = var_search.get().strip().lower()
    for item in tree.get_children():
        properties = tree.item(item).get("values")
        if properties and len(properties) > 0 and substring in str(properties[0]).lower():
            tree.selection_set(item)
            tree.see(item)
            return
    messagebox.showinfo("Search", "No matching items found.")


button_search = tk.Button(labelframe_search, text="Find", command=search)
button_search.grid(column=1, row=0, padx=5, pady=5, sticky="we")

labelframe_entry = tk.LabelFrame(root, text="Adding/Editing")
labelframe_entry.pack(padx=5, pady=5, fill="both", expand=True)

labelframe_entry.columnconfigure(0, weight=1)
labelframe_entry.columnconfigure(1, weight=1)

entry_name = tk.Entry(labelframe_entry, textvariable=var_name,)
entry_name.grid(column=0, row=0, padx=5, pady=5, sticky="we")

scale_price = tk.Scale(
    labelframe_entry,
    variable=var_price,
    from_=0,
    to=400,
    tickinterval=100,
    resolution=10,
    orient="horizontal",
)

scale_price.grid(column=0, row=1, columnspan=2, padx=5, pady=5, sticky="we")

combo_status = ttk.Combobox(labelframe_entry, textvariable=var_status, values = COMBO_STATUS_VALUES,)
combo_status.grid(column=1, row=0, padx=5, pady=5, sticky="we")

def clear_inputs():
    var_name.set("")
    var_price.set(0)
    var_status.set(COMBO_STATUS_VALUES[1])

clear_inputs()

labelframe_button = tk.LabelFrame(root, text="Actions")
labelframe_button.pack(padx=5, pady=5, fill="both", expand=True)

labelframe_button.columnconfigure(0, weight=1)
labelframe_button.columnconfigure(1, weight=1)

def validation(name, price):
    if not name or price == 0:
        messagebox.showerror("Error", "Model name cannot be empty and price cannot be 0!")
        return False
    return True

def handle_insert():
    name, price, status = var_name.get(), var_price.get(), var_status.get()
    if validation(name, price):
        tree.insert("", "end", values=(name, price, status))
        clear_inputs()
        save_data()

button_insert = tk.Button(labelframe_button, text="Insert", command=handle_insert,)
button_insert.grid(column=0, row=0, padx=5, pady=5, sticky="we")

def handle_delete():
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("Warning", "No item selected to delete.")
        return
    answer = messagebox.askyesno("Delete", "Are you sure you want to delete this item?")
    if answer:
        tree.delete(selection[0])
        save_data()

button_delete = tk.Button(labelframe_button, text="Delete", command=handle_delete,)
button_delete.grid(column=1, row=0, padx=5, pady=5, sticky="we")

def handle_get():
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("Warning", "No item selected.")
        return
    values = tree.item(selection[0]).get("values")
    if values:
        var_name.set(values[0])
        var_price.set(values[1])
        var_status.set(values[2])

button_get = tk.Button(labelframe_button, text="Get", command=handle_get, )
button_get.grid(column=0, row=1, padx=5, pady=5, sticky="we")

def handle_set():
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("Warning", "No item selected.")
        return
    name, price, status = var_name.get(), var_price.get(), var_status.get()
    if validation(name, price):
        tree.item(selection[0], values=(name, price, status))
        clear_inputs()
        save_data()

button_set = tk.Button(labelframe_button, text="Set", command=handle_set,)
button_set.grid(column=1, row=1, padx=5, pady=5, sticky="we")

root.mainloop()