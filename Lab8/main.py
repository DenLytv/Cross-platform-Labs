import tkinter as tk
import csv
import os
from tkinter import ttk, messagebox

MEALS = ["Borscht", "Varenyky", "Cutlet", "Olivier", "Mashed Potatoes", "Salad", "Soup"]
CSV_FILE = "orders.csv"
MIN_QTY = 1
MAX_QTY = 10

root = tk.Tk()
root.title("Meal Order Form")
root.columnconfigure([0, 1], weight=1)

def validate_surname(char):
    return char.isascii() and (char.isalpha() or char in "- ") and char

def validate_meal_name(char):
    return char.isascii() and (char.isalpha() or char in " ")

def validate_quantity(value):
    return value.isdecimal() and MIN_QTY <= int(value) <= MAX_QTY or value == ""

def show_invalid_surname():
    label_status.config(fg="red", text="Surname: only English letters, space or '-'")

def show_invalid_meal_name():
    label_status.config(fg="red", text="Meal: only English letters or space")

def show_invalid_quantity():
    label_status.config(fg="red", text=f"Quantity must be {MIN_QTY}–{MAX_QTY}")

def update_listbox(event):
    value = entry_meal.get().strip().lower()
    listbox.delete(0, tk.END)
    if not value:
        listbox.grid_remove()
        return
    matches = [meal for meal in MEALS if meal.lower().startswith(value)]
    if matches:
        listbox.grid()
        for meal in matches[:3]:
            listbox.insert(tk.END, meal)
    else:
        listbox.grid_remove()

def select_from_listbox(event):
    if listbox.curselection():
        entry_meal.delete(0, tk.END)
        entry_meal.insert(0, listbox.get(listbox.curselection()))
        listbox.grid_remove()

def submit_order():
    meal = entry_meal.get().strip()
    surname = entry_surname.get().strip()
    try:
        qty = int(spinbox_qty.get())
    except ValueError:
        label_status.config(fg="red", text="Invalid quantity")
        return
    if meal not in MEALS:
        label_status.config(fg="red", text="Meal must be a valid option from the list")
        return
    if not surname:
        label_status.config(fg="red", text="Please enter a surname")
        return
    write_to_csv(meal, surname, qty)
    label_status.config(fg="green", text=f"Saved: {qty} × {meal} for {surname}")
    clear_fields()

def clear_fields():
    entry_meal.delete(0, tk.END)
    entry_surname.delete(0, tk.END)
    spinbox_qty.delete(0, tk.END)
    spinbox_qty.insert(0, str(MIN_QTY))
    listbox.grid_remove()

def write_to_csv(meal, surname, qty):
    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Meal", "Surname", "Quantity"])
        writer.writerow([meal, surname, qty])

def open_order_list_window():
    if not os.path.exists(CSV_FILE):
        label_status.config(fg="red", text="No orders found.")
        return
    win = tk.Toplevel(root)
    win.title("Order List")
    win.grab_set()
    win.transient(root)
    tree = ttk.Treeview(win, columns=("No", "Meal", "Surname", "Quantity"), show="headings", height=10)
    tree.heading("No", text="#")
    tree.heading("Meal", text="Meal")
    tree.heading("Surname", text="Surname")
    tree.heading("Quantity", text="Quantity")
    tree.column("No", width=30, anchor="center")
    tree.column("Meal", width=120)
    tree.column("Surname", width=120)
    tree.column("Quantity", width=80, anchor="center")
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    def load_orders():
        tree.delete(*tree.get_children())
        if not os.path.exists(CSV_FILE):
            return

        with open(CSV_FILE, newline='', encoding="utf-8") as f:
            rows = list(csv.reader(f))

        valid_rows = []
        header = rows[0] if rows else []
        data_rows = rows[1:] if rows and header == ["Meal", "Surname", "Quantity"] else rows

        for row in data_rows:
            if len(row) != 3:
                continue
            meal, surname, qty = row
            if (
                    meal in MEALS and
                    surname.strip() != "" and
                    validate_surname(surname) and
                    qty.isdigit() and MIN_QTY <= int(qty) <= MAX_QTY
            ):
                valid_rows.append([meal, surname, qty])

        with open(CSV_FILE, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Meal", "Surname", "Quantity"])
            writer.writerows(valid_rows)

        for idx, row in enumerate(valid_rows, start=1):
            tree.insert("", "end", values=(idx, row[0], row[1], row[2]))

    def complete_order():
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Please select an order to complete.")
            return
        values = tree.item(selected[0])["values"]
        order_to_delete = list(map(str, values[1:]))
        tree.delete(selected[0])
        with open(CSV_FILE, newline='', encoding="utf-8") as f:
            rows = list(csv.reader(f))
        with open(CSV_FILE, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in rows:
                if row != order_to_delete:
                    writer.writerow(row)
        load_orders()

    def edit_order():
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Please select an order to edit.")
            return
        values = tree.item(selected[0])["values"]
        edit_win = tk.Toplevel(win)
        edit_win.title("Edit Order")
        edit_win.grab_set()
        edit_win.transient(win)
        tk.Label(edit_win, text="Meal:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        entry_meal = tk.Entry(edit_win)
        entry_meal.insert(0, values[1])
        entry_meal.grid(row=0, column=1, padx=5, pady=5)
        listbox = tk.Listbox(edit_win, height=3)
        listbox.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        listbox.grid_remove()

        def on_keyrelease(event):
            value = entry_meal.get().strip().lower()
            listbox.delete(0, tk.END)
            if not value:
                listbox.grid_remove()
                return
            matches = [meal for meal in MEALS if meal.lower().startswith(value)]
            if matches:
                listbox.grid()
                for m in matches[:3]:
                    listbox.insert("end", m)
            else:
                listbox.grid_remove()

        def on_listbox_select(event):
            if listbox.curselection():
                selected_meal = listbox.get(listbox.curselection())
                entry_meal.delete(0, tk.END)
                entry_meal.insert(0, selected_meal)
                listbox.delete(0, tk.END)
                listbox.grid_remove()

        entry_meal.bind("<KeyRelease>", on_keyrelease)
        listbox.bind("<<ListboxSelect>>", on_listbox_select)

        tk.Label(edit_win, text="Surname:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        entry_surname = tk.Entry(edit_win)
        entry_surname.insert(0, values[2])
        entry_surname.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(edit_win, text="Quantity:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        spin_qty = tk.Spinbox(edit_win, from_=1, to=100)
        spin_qty.delete(0, tk.END)
        spin_qty.insert(0, values[3])
        spin_qty.grid(row=3, column=1, padx=5, pady=5)

        def save_edits():
            new_meal = entry_meal.get().strip()
            new_surname = entry_surname.get().strip()
            new_qty = spin_qty.get().strip()
            if new_meal not in MEALS:
                messagebox.showerror("Invalid input", "Meal must be a valid option from the list.")
                return
            if not validate_surname(new_surname):
                messagebox.showerror("Invalid input", "Surname must contain only English letters and '-' and can't be empty")
                return
            if not new_qty.isdigit() or not (MIN_QTY <= int(new_qty) <= MAX_QTY):
                messagebox.showerror("Invalid input", f"Quantity must be a number between {MIN_QTY} and {MAX_QTY}.")
                return
            new_row = [new_meal, new_surname, new_qty]
            with open(CSV_FILE, newline='', encoding="utf-8") as f:
                rows = list(csv.reader(f))
            with open(CSV_FILE, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                for row in rows:
                    if row == list(map(str, values[1:])):
                        writer.writerow(new_row)
                    else:
                        writer.writerow(row)
            load_orders()
            edit_win.destroy()

        tk.Button(edit_win, text="Save", command=save_edits).grid(row=4, column=0, columnspan=2, pady=10)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="Complete", command=complete_order).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(btn_frame, text="Edit", command=edit_order).grid(row=0, column=1, padx=5, pady=5)

    def on_double_click(event):
        edit_order()

    tree.bind("<Double-1>", on_double_click)
    load_orders()
    win.wait_window()

tk.Label(text="Meal").grid(row=0, column=0, padx=5, pady=5)
tk.Label(text="Surname").grid(row=0, column=1, padx=5, pady=5)

entry_meal = tk.Entry(
    validate="key",
    validatecommand=(root.register(validate_meal_name), "%S"),
    invalidcommand=root.register(show_invalid_meal_name),
)
entry_meal.grid(row=1, column=0, sticky="we", padx=5, pady=5)

entry_surname = tk.Entry(
    validate="key",
    validatecommand=(root.register(validate_surname), "%S"),
    invalidcommand=root.register(show_invalid_surname),
)
entry_surname.grid(row=1, column=1, sticky="we", padx=5, pady=5)

tk.Label(text=f"Number of portions ({MIN_QTY}–{MAX_QTY})").grid(row=2, column=0, columnspan=2)
spinbox_qty = tk.Spinbox(
    from_=MIN_QTY,
    to=MAX_QTY,
    validate="all",
    validatecommand=(root.register(validate_quantity), "%P"),
    invalidcommand=root.register(show_invalid_quantity),
)
spinbox_qty.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="we")

listbox = tk.Listbox(height=3)
listbox.grid(row=4, column=0, sticky="we", padx=5, pady=5)
listbox.grid_remove()

tk.Button(text="Clear", command=clear_fields).grid(row=5, column=0, padx=5, pady=5)
tk.Button(text="Submit", command=submit_order).grid(row=5, column=1, padx=5, pady=5)
tk.Button(text="Show Orders", command=open_order_list_window).grid(row=6, column=0, columnspan=2, pady=5)

label_status = tk.Label(anchor="w")
label_status.grid(row=7, column=0, columnspan=2, sticky="we", padx=5, pady=5)

entry_meal.bind("<KeyRelease>", update_listbox)
listbox.bind("<<ListboxSelect>>", select_from_listbox)
entry_meal.focus_set()

root.mainloop()