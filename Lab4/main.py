import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, EpsImagePlugin
import os

EpsImagePlugin.gs_windows_binary = "C:/Program Files/gs/gs10.05.0/bin/gswin64.exe"

root = tk.Tk()
root.title("Bitmap Editor")
root.config(pady=5, padx=5)

x_var = tk.IntVar(value=50)
y_var = tk.IntVar(value=50)
anchor_var = tk.StringVar(value="center")
bitmap_var = tk.StringVar(value="error")
foreground_var = tk.StringVar(value="black")
background_var = tk.StringVar(value="white")

frame = tk.Frame(root)
frame.pack(side="left", fill="y")

frame_position = tk.LabelFrame(frame, text="Position:", bd=1, relief="solid")
frame_position.pack(pady=2, padx=2, fill="x")

frame_x = tk.LabelFrame(frame_position, text="x:", bd=1, relief="solid")
frame_x.pack(pady=2, padx=2, fill="x")
spinbox_x = tk.Spinbox(frame_x, textvariable=x_var, from_=0, to=500, width=5)
spinbox_x.pack(pady=2, padx=2, fill="x")

frame_y = tk.LabelFrame(frame_position, text="y:", bd=1, relief="solid")
frame_y.pack(pady=2, padx=2, fill="x")
spinbox_y = tk.Spinbox(frame_y, textvariable=y_var, from_=0, to=500, width=5)
spinbox_y.pack(pady=2, padx=2, fill="x")

frame_anchor = tk.LabelFrame(frame, text="Anchor:", bd=1, relief="solid")
frame_anchor.pack(pady=2, padx=2, fill="x")

combo_anchor = ttk.Combobox(frame_anchor, textvariable=anchor_var,
                            values=("n", "ne", "e", "se", "s", "sw", "w", "nw", "center"), width=7, state="readonly")
combo_anchor.pack(pady=2, padx=2, fill="x")

frame_bitmap = tk.LabelFrame(frame, text="Bitmap:", bd=1, relief="solid")
frame_bitmap.pack(pady=2, padx=2, fill="x")

combo_bitmap = ttk.Combobox(frame_bitmap, textvariable=bitmap_var,
                            values=("error", "hourglass", "info", "questhead", "question", "warning"), width=10,
                            state="readonly")
combo_bitmap.pack(pady=2, padx=2, fill="x")

frame_foreground = tk.LabelFrame(frame, text="Foreground:", bd=1, relief="solid")
frame_foreground.pack(pady=2, padx=2, fill="x")

combo_foreground = ttk.Combobox(
    frame_foreground, textvariable=foreground_var,
    values=("black", "red", "blue", "green", "purple", "orange", "brown", "pink",
            "lime", "navy", "gold", "turquoise", "violet", "indigo", "crimson"),
    width=10, state="readonly"
)
combo_foreground.pack(pady=2, padx=2, fill="x")

frame_background = tk.LabelFrame(frame, text="Background:", bd=1, relief="solid")
frame_background.pack(pady=2, padx=2, fill="x")

combo_background = ttk.Combobox(
    frame_background, textvariable=background_var,
    values=("white", "yellow", "cyan", "gray", "lightblue", "beige", "lightgreen", "magenta",
            "lavender", "peach", "lightgray", "seashell", "salmon", "khaki", "coral"),
    width=10, state="readonly"
)
combo_background.pack(pady=2, padx=2, fill="x")

last_drawn = []

def update_buttons_state():
    undo_button.config(state="normal" if last_drawn else "disabled")
    clear_button.config(state="normal" if canvas.find_all() else "disabled")

def handle_draw():
    try:
        obj = canvas.create_bitmap(
            x_var.get(), y_var.get(),
            anchor=anchor_var.get(),
            bitmap=bitmap_var.get(),
            foreground=foreground_var.get(),
            background=background_var.get()
        )
        last_drawn.append(obj)
        update_buttons_state()
    except Exception:
        messagebox.showerror(title="Error", message="x and y values cannot be empty!")

def undo():
    if last_drawn:
        obj = last_drawn.pop()
        canvas.delete(obj)
        update_buttons_state()

def save_canvas():
    file_name = "canvas.png"
    canvas.update()
    canvas.postscript(file="canvas.ps", colormode='color')

    with Image.open("canvas.ps") as img:
        img.save(file_name, "png")

    os.remove("canvas.ps")

    messagebox.showinfo("Saved", f"Canvas saved as {file_name}")

def validate_spinbox_input(value, max_value):
    if value == "":
        return True
    if value.isdigit():
        num = int(value)
        return 0 <= num <= max_value
    return False

def handle_clear():
    global last_drawn
    canvas.delete("all")
    last_drawn = []
    update_buttons_state()

def update_spinbox_limits(event):
    width = max(0, canvas.winfo_width() - 1)
    height = max(0, canvas.winfo_height() - 1)

    spinbox_x.config(to=width)
    spinbox_y.config(to=height)

    x_validate_cmd = root.register(lambda v: validate_spinbox_input(v, width))
    y_validate_cmd = root.register(lambda v: validate_spinbox_input(v, height))

    spinbox_x.config(validate="key", validatecommand=(x_validate_cmd, "%P"))
    spinbox_y.config(validate="key", validatecommand=(y_validate_cmd, "%P"))

root.bind("<Configure>", update_spinbox_limits)

tk.Button(frame, text="Draw", bg="orange", command=handle_draw).pack(pady=2, padx=2, fill="x")
undo_button = tk.Button(frame, text="Undo", command=undo)
undo_button.pack(pady=2, padx=2, fill="x")

tk.Button(frame, text="Save", command=save_canvas).pack(pady=2, padx=2, fill="x")
clear_button = tk.Button(frame, text="Clear", command=handle_clear)
clear_button.pack(pady=2, padx=2, fill="x")

frame_canvas = tk.LabelFrame(root, text="Canvas area", bd=1, relief="solid")
frame_canvas.pack(side="right", fill="both", expand=True, padx=2, pady=2)

canvas = tk.Canvas(frame_canvas, bg="white", width=500, height=500)
canvas.pack(fill="both", expand=True)

update_buttons_state()

root.mainloop()