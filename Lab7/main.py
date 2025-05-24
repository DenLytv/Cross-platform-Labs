import tkinter as tk
import random
import json
from tkinter import messagebox

grid_spacing = 40
figure_x = 0
figure_y = 0
selected_figure = None

BOUNDARY_MIN_X = 20.0
BOUNDARY_MIN_Y = 20.0
BOUNDARY_MAX_X = 1500.0
BOUNDARY_MAX_Y = 780.0

COLOR_PALETTE = [
    "red", "green", "blue", "yellow", "orange", "purple", "pink",
    "cyan", "magenta", "lime", "teal", "indigo", "violet",
    "gold", "brown", "navy", "salmon", "turquoise", "orchid",
    "darkgreen", "crimson", "slateblue", "chocolate", "deepskyblue"
]

root = tk.Tk()
root.config()

canvas_frame = tk.Frame()
canvas_frame.pack(fill="both", expand=True)
canvas = tk.Canvas(canvas_frame, bg="white")
canvas.pack(fill="both", expand=True)

label = tk.Label(canvas_frame, anchor="w", text="Start")
label.pack(fill="x", expand=False)

figures = []

def handle_start_drag(event):
    global figure_x, figure_y, selected_figure
    selected_figure = canvas.find_withtag("current")[0]
    figure_x = event.x
    figure_y = event.y
    canvas.itemconfig(selected_figure, width=2)
    canvas.config(cursor="hand2")
    canvas.tag_raise(selected_figure)


def handle_on_drag(event):
    global figure_x, figure_y
    dx = event.x - figure_x
    dy = event.y - figure_y

    if selected_figure:
        x1, y1, x2, y2 = canvas.coords(selected_figure)
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if (x1 + dx >= 0 and x2 + dx <= canvas_width and
                y1 + dy >= 0 and y2 + dy <= canvas_height):
            canvas.move(selected_figure, dx, dy)
            figure_x = event.x
            figure_y = event.y


def handle_end_drag(event):
    global figure_x, figure_y
    snap_to_target()
    if selected_figure:
        canvas.itemconfig(selected_figure, width=0)
    canvas.config(cursor="arrow")
    figure_x = 0
    figure_y = 0

def get_snapped_coords(x, y):
    snapped_x = (round(x / grid_spacing - 0.5) + 0.5) * grid_spacing
    snapped_y = (round(y / grid_spacing - 0.5) + 0.5) * grid_spacing

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    half_spacing = grid_spacing // 2

    if canvas_width != 1 and canvas_height != 1:
        if snapped_x + half_spacing > canvas_width and snapped_y + half_spacing > canvas_height:
            return snapped_x - grid_spacing, snapped_y - grid_spacing
        elif snapped_x + half_spacing > canvas_width:
             return snapped_x - grid_spacing, snapped_y
        elif snapped_y + half_spacing > canvas_height:
             return snapped_x, snapped_y - grid_spacing
    return snapped_x, snapped_y

def create_figure(x, y):
    radius = 15
    snapped_x, snapped_y = get_snapped_coords(x, y)
    color = random.choice(COLOR_PALETTE)

    new_figure = canvas.create_oval(
        snapped_x - radius, snapped_y - radius,
        snapped_x + radius, snapped_y + radius,
        width=0,
        outline="black",
        fill=color,
    )
    figures.append(new_figure)

    canvas.tag_bind(new_figure, "<Button-1>", handle_start_drag)
    canvas.tag_bind(new_figure, "<B1-Motion>", handle_on_drag)
    canvas.tag_bind(new_figure, "<ButtonRelease-1>", handle_end_drag)

    return new_figure

create_figure(20, 20)

def draw_grid():
    canvas.delete("grid")
    width, height = canvas.winfo_width(), canvas.winfo_height()
    for x in range(0, width, grid_spacing):
        canvas.create_line(x, 0, x, height, fill="lightgray", tags="grid")
    for y in range(0, height, grid_spacing):
        canvas.create_line(0, y, width, y, fill="lightgray", tags="grid")

def handle_resize(event):
    draw_grid()


def show_coords(event):
    label.config(text=f"x: {event.x}, y: {event.y}")


def handle_move(event, dx=0, dy=0):
    if selected_figure:
        x1, y1, x2, y2 = canvas.coords(selected_figure)
        new_x1, new_y1, new_x2, new_y2 = x1 + dx, y1 + dy, x2 + dx, y2 + dy
        canvas_width, canvas_height = canvas.winfo_width(), canvas.winfo_height()
        if 0 <= new_x1 <= canvas_width - (x2 - x1) and 0 <= new_y1 <= canvas_height - (y2 - y1):
            canvas.move(selected_figure, dx, dy)

def handle_up(event):
    handle_move(event, dy=-grid_spacing)
def handle_down(event):
    handle_move(event, dy=grid_spacing)
def handle_left(event):
    handle_move(event, dx=-grid_spacing)
def handle_right(event):
    handle_move(event, dx=grid_spacing)
def handle_up_right(event):
    handle_move(event, dx=grid_spacing, dy=-grid_spacing)
def handle_up_left(event):
    handle_move(event, dx=-grid_spacing, dy=-grid_spacing)
def handle_down_right(event):
    handle_move(event, dx=grid_spacing, dy=grid_spacing)
def handle_down_left(event):
    handle_move(event, dx=-grid_spacing, dy=grid_spacing)

def snap_to_target():
    if not selected_figure:
        return

    x1, y1, x2, y2 = canvas.coords(selected_figure)
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    grid_x = (round(center_x / grid_spacing - 0.5) + 0.5) * grid_spacing
    grid_y = (round(center_y / grid_spacing - 0.5) + 0.5) * grid_spacing

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    half_spacing = grid_spacing // 2

    dx = grid_x - center_x
    dy = grid_y - center_y

    new_x1, new_y1 = x1 + dx, y1 + dy
    new_x2, new_y2 = x2 + dx, y2 + dy

    if grid_x + half_spacing > canvas_width and grid_y + half_spacing > canvas_height:
        canvas.move(selected_figure, dx - grid_spacing, dy - grid_spacing)
    elif grid_x + half_spacing > canvas_width:
        canvas.move(selected_figure, dx - grid_spacing, dy)
    elif grid_y + half_spacing > canvas_height:
        canvas.move(selected_figure, dx, dy - grid_spacing)
    elif (new_x1 >= 0 and new_x2 <= canvas_width and
          new_y1 >= 0 and new_y2 <= canvas_height):
        canvas.move(selected_figure, dx, dy)


def handle_add_figure(event):
    create_figure(event.x, event.y)

def reset_grid():
    for fig in figures:
        canvas.delete(fig)
    figures.clear()

def save_figures():
    if len(figures) != 0:
        data = []
        for fig in figures:
            x1, y1, x2, y2 = canvas.coords(fig)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            color = canvas.itemcget(fig, "fill")
            data.append({"x": center_x, "y": center_y, "color": color})

        try:
            with open("figures.json", "w") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Save", "Figures saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save figures:\n{e}")
    else:
        messagebox.showwarning("Warning", "You cannot save empty canvas")

def is_valid_color(color):
    try:
        canvas.winfo_rgb(color)
        return True
    except tk.TclError:
        return False

def load_figures():
    try:
        with open("figures.json", "r") as f:
            content = f.read()
            if not content.strip():
                raise Exception("File is empty.")
            data = json.loads(content)

        if not isinstance(data, list):
            raise Exception("Invalid file structure. Expected a list of objects.")


        for i, item in enumerate(data):
            if not all(k in item for k in ("x", "y", "color")):
                raise Exception(f"Object #{i+1} is missing required keys.")
            if (not isinstance(item["x"], (int, float)) or not isinstance(item["y"], (int, float))
                or not BOUNDARY_MIN_X <= item["x"] <= BOUNDARY_MAX_X
                or not BOUNDARY_MIN_Y <= item["y"] <= BOUNDARY_MAX_Y):
                raise Exception(f"Invalid coordinates in object #{i+1}.")
            if not isinstance(item["color"], str) or not is_valid_color(item["color"]):
                raise Exception(f"Invalid color in object #{i + 1}.")

        reset_grid()

        for item in data:
            x, y, color = item["x"], item["y"], item["color"]
            radius = 15
            fig = canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                width=0,
                outline="black",
                fill=color,
            )
            figures.append(fig)
            canvas.tag_bind(fig, "<Button-1>", handle_start_drag)
            canvas.tag_bind(fig, "<B1-Motion>", handle_on_drag)
            canvas.tag_bind(fig, "<ButtonRelease-1>", handle_end_drag)

        messagebox.showinfo("Load", "Figures loaded successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load figures:\n{e}")

canvas.bind("<Configure>", handle_resize)
canvas.bind("<Motion>", show_coords)
canvas.bind("<Button-3>", handle_add_figure)

root.bind("<KeyPress-Up>", handle_up)
root.bind("<KeyPress-Down>", handle_down)
root.bind("<KeyPress-Left>", handle_left)
root.bind("<KeyPress-Right>", handle_right)
root.bind("<e>", handle_up_right)
root.bind("<q>", handle_up_left)
root.bind("<d>", handle_down_right)
root.bind("<a>", handle_down_left)

buttons_frame = tk.Frame()
buttons_frame.pack(pady=5)

reset_button = tk.Button(buttons_frame, text="Reset grid", command=reset_grid, width=10)
reset_button.grid(column=0, row=0, pady=5, padx=5)

save_button = tk.Button(buttons_frame, text="Save figures", command=save_figures)
save_button.grid(column=1, row=0, pady=5, padx=5)

load_button = tk.Button(buttons_frame, text="Load figures", command=load_figures)
load_button.grid(column=2, row=0, pady=5, padx=5)

root.mainloop()