import tkinter as tk
from tkinter import filedialog, simpledialog, font, messagebox

def create_separator(frame):
    separator = tk.Frame(frame, bg="gray", width=2, height=20)
    separator.pack(side="left", padx=5, pady=2)
    return separator

def create_button(frame, text, command):
    button = tk.Button(frame, text=text, width=2, height=1, relief="flat", command=command)
    button.pack(side="left", padx=2, pady=2)
    return button

def reset_background():
    bg_color.set("white")
    label.config(bg=bg_color.get())

def create_menu_item(menu, label, accelerator, command):
    menu.add_command(label=label, accelerator=accelerator, command=command)

def create_checkbutton(menu, label, variable, onvalue, offvalue, command):
    menu.add_checkbutton(label=label, variable=variable, onvalue=onvalue, offvalue=offvalue, command=command)

def create_radiobutton(menu, label, variable, value, command):
    menu.add_radiobutton(label=label, variable=variable, value=value, command=command)

def change_font_size(size):
    label.config(font=("Arial", size))

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        label.config(text=content)

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(label.cget("text"))

def change_font_family():
    family = simpledialog.askstring("Font", "Enter font family:")
    if family:
        if family in font.families():
            current_font = font.Font(font=label.cget("font"))
            current_font.config(family=family)
            label.config(font=current_font)
        else:
            messagebox.showerror("Error", f"Font '{family}' is not available.")


def create_menu(root):
    menu_bar = tk.Menu(root)

    menu_file = tk.Menu(menu_bar, tearoff=0)
    create_menu_item(menu_file, "New", "Ctrl+N", lambda: label.config(text="New"))
    create_menu_item(menu_file, "Open", "Ctrl+O", open_file)
    create_menu_item(menu_file, "Save", "Ctrl+S", save_file)
    create_menu_item(menu_file, "Save As", "Ctrl+Shift+S", save_file)
    menu_file.add_separator()
    create_menu_item(menu_file, "Close", None, lambda: label.config(text="Close"))
    create_menu_item(menu_file, "Exit", None, root.quit)

    menu_export = tk.Menu(menu_file, tearoff=0)
    create_menu_item(menu_export, "PDF", None, lambda: label.config(text="Export as PDF"))
    create_menu_item(menu_export, "DOCX", None, lambda: label.config(text="Export as DOCX"))
    menu_file.add_cascade(label="Export", menu=menu_export)

    create_menu_item(menu_file, "Print", None, lambda: label.config(text="Print"))
    create_menu_item(menu_file, "Recent Files", None, lambda: label.config(text="Recent Files"))
    menu_file.add_separator()
    create_menu_item(menu_file, "Exit App", None, root.quit)

    menu_bar.add_cascade(label="File", menu=menu_file)

    menu_edit = tk.Menu(menu_bar, tearoff=0)
    create_menu_item(menu_edit, "Undo", "Ctrl+Z", lambda: label.config(text="Undo"))
    create_menu_item(menu_edit, "Redo", "Ctrl+Y", lambda: label.config(text="Redo"))
    menu_edit.add_separator()
    create_checkbutton(menu_edit, "Autosave", border, 1, 0, lambda: label.config(bd=border.get()))
    menu_edit.add_separator()
    create_menu_item(menu_edit, "Preferences", None, lambda: label.config(text="Preferences"))

    create_menu_item(menu_edit, "Cut", "Ctrl+X", lambda: label.config(text="Cut"))
    create_menu_item(menu_edit, "Copy", "Ctrl+C", lambda: label.config(text="Copy"))
    create_menu_item(menu_edit, "Paste", "Ctrl+V", lambda: label.config(text="Paste"))
    create_menu_item(menu_edit, "Find", "Ctrl+F", lambda: label.config(text="Find"))
    create_menu_item(menu_edit, "Replace", "Ctrl+H", lambda: label.config(text="Replace"))

    menu_bar.add_cascade(label="Edit", menu=menu_edit)

    menu_view = tk.Menu(menu_bar, tearoff=0)
    create_radiobutton(menu_view, "White", bg_color, "white", lambda: label.config(bg=bg_color.get()))
    create_radiobutton(menu_view, "Light Yellow", bg_color, "lightyellow", lambda: label.config(bg=bg_color.get()))
    create_radiobutton(menu_view, "Light Blue", bg_color, "lightblue", lambda: label.config(bg=bg_color.get()))
    create_radiobutton(menu_view, "Dark", bg_color, "black", lambda: label.config(bg=bg_color.get()))
    create_radiobutton(menu_view, "Dark Grey", bg_color, "darkgray", lambda: label.config(bg=bg_color.get()))
    menu_view.add_separator()
    create_menu_item(menu_view, "Reset View", None, reset_background)

    create_checkbutton(menu_view, "Show Line Numbers", line_number, True, False, lambda: label.config(text="Line Numbers: " + str(line_number.get())))

    menu_view.add_separator()
    create_radiobutton(menu_view, "Font Size 12", font_size, 12, lambda: change_font_size(12))
    create_radiobutton(menu_view, "Font Size 14", font_size, 14, lambda: change_font_size(14))
    create_radiobutton(menu_view, "Font Size 16", font_size, 16, lambda: change_font_size(16))
    create_menu_item(menu_view, "Change Font Family", None, change_font_family)

    menu_bar.add_cascade(label="View", menu=menu_view)

    menu_tools = tk.Menu(menu_bar, tearoff=0)
    create_menu_item(menu_tools, "Compile", None, lambda: label.config(text="Compiling"))
    create_menu_item(menu_tools, "Run", None, lambda: label.config(text="Running"))
    create_menu_item(menu_tools, "Stop", None, lambda: label.config(text="Stopping"))
    menu_tools.add_separator()
    create_menu_item(menu_tools, "Preferences", None, lambda: label.config(text="Tool Preferences"))

    create_menu_item(menu_tools, "Format Code", None, lambda: label.config(text="Formatting Code"))
    create_menu_item(menu_tools, "Check Syntax", None, lambda: label.config(text="Checking Syntax"))
    create_menu_item(menu_tools, "Compile and Run", None, lambda: label.config(text="Compiling and Running"))

    menu_bar.add_cascade(label="Tools", menu=menu_tools)

    menu_help = tk.Menu(menu_bar, tearoff=0)
    create_menu_item(menu_help, "Documentation", None, lambda: label.config(text="Documentation"))
    create_menu_item(menu_help, "About", None, lambda: label.config(text="About"))
    menu_help.add_separator()
    create_menu_item(menu_help, "Check for Updates", None, lambda: label.config(text="Checking for Updates"))

    menu_bar.add_cascade(label="Help", menu=menu_help)

    root.config(menu=menu_bar)

def create_toolbar():
    frame_toolbar = tk.Frame(root, bd=1, relief="raised")
    frame_toolbar.pack(anchor="w")

    button_new = create_button(frame_toolbar, "\U0001F4C2", lambda: label.config(text="New"))
    create_separator(frame_toolbar)
    button_open = create_button(frame_toolbar, "\U0001F4C1", open_file)
    create_separator(frame_toolbar)
    button_save = create_button(frame_toolbar, "\U0001F4BE", save_file)
    create_separator(frame_toolbar)
    button_undo = create_button(frame_toolbar, "\U0001F504", lambda: label.config(text="Undo"))
    create_separator(frame_toolbar)
    button_redo = create_button(frame_toolbar, "\U0001F501", lambda: label.config(text="Redo"))
    create_separator(frame_toolbar)
    button_compile = create_button(frame_toolbar, "\U0001F4DD", lambda: label.config(text="Compiling"))
    create_separator(frame_toolbar)
    button_run = create_button(frame_toolbar, "\U000027A1", lambda: label.config(text="Running"))
    create_separator(frame_toolbar)
    button_stop = create_button(frame_toolbar, "\U000023F9", lambda: label.config(text="Stopping"))
    create_separator(frame_toolbar)
    button_export_pdf = create_button(frame_toolbar, "\U0001F4C4", lambda: label.config(text="Export as PDF"))
    create_separator(frame_toolbar)
    button_preferences = create_button(frame_toolbar, "\U0001F3AD", lambda: label.config(text="Preferences"))

def create_label():
    global label
    label = tk.Label(text="Welcome to Code Editor", bg="white", height=10, bd=0, relief="solid", font=("Arial", 12))
    label.pack(fill="both", expand=True, padx=5, pady=5)

root = tk.Tk()
root.title("Code Editor")

border = tk.IntVar(value=0)
bg_color = tk.StringVar(value="white")
font_size = tk.IntVar(value=12)
line_number = tk.BooleanVar(value=True)

create_menu(root)
create_toolbar()
create_label()

root.mainloop()