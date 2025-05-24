import tkinter as tk
import tkinter.ttk as ttk
import json
import os

SETTINGS_FILE = "checkbutton_settings.json"

root = tk.Tk()
root.resizable(width=False, height=False)
text_var = tk.StringVar()
width_var = tk.IntVar()
indicatoron_var = tk.StringVar()
selectcolor_var = tk.StringVar()
offrelief_var = tk.StringVar()
check_var = tk.BooleanVar()

indicator_values = ("True", "False")
color_values = ("white", "gray", "black", "red", "green", "blue", "yellow", "orange", "purple", "cyan",
                "magenta", "brown", "pink", "turquoise", "gold", "silver", "navy", "maroon", "lime", "olive", "teal")
offrelief_values = ("flat", "raised", "sunken", "ridge", "groove", "solid")

top_level = None
trace_id = None
combo_offrelief = None


def create_labeled_widget(parent, label, widget_class, variable, **kwargs):
    frame = tk.LabelFrame(parent, text=label)
    frame.pack(padx=5, pady=5, fill="x")
    widget = widget_class(frame, textvariable=variable, **kwargs)
    widget.pack(padx=5, pady=5, fill="x")
    return widget


def handle_close():
    global top_level, trace_id
    if trace_id:
        indicatoron_var.trace_remove("write", trace_id)
        trace_id = None
    if top_level:
        top_level.grab_release()
        top_level.destroy()
        top_level = None


def handle_ok():
    apply_changes()
    save_settings()
    handle_close()


def handle_cancel():
    handle_close()


def apply_changes():
    indicatoron_value = indicatoron_var.get() == "True"
    checkbutton.config(
        text=text_var.get(),
        width=width_var.get(),
        indicatoron=indicatoron_value,
        selectcolor=selectcolor_var.get(),
        offrelief=offrelief_var.get()
    )


def update_offrelief_state(*args):
    if combo_offrelief and combo_offrelief.winfo_exists():
        state = "readonly" if indicatoron_var.get() == "False" else "disabled"
        combo_offrelief.config(state=state)


def handle_adjust():
    global top_level, combo_offrelief, trace_id
    if top_level is not None:
        return

    top_level = tk.Toplevel(root)
    top_level.title("Adjust")
    top_level.resizable(False, False)
    top_level.protocol("WM_DELETE_WINDOW", handle_close)

    create_labeled_widget(top_level, "Text:", tk.Entry, text_var)
    text_var.set(checkbutton.cget("text"))

    create_labeled_widget(top_level, "Width:", tk.Spinbox, width_var, from_=12, to=30, width=15, state="readonly")
    width_var.set(checkbutton.cget("width"))

    combo_indicator = create_labeled_widget(top_level, "Indicator On:", ttk.Combobox, indicatoron_var,
                                            values=indicator_values, state="readonly")
    indicatoron_var.set("True" if checkbutton.cget("indicatoron") else "False")
    trace_id = indicatoron_var.trace_add("write", update_offrelief_state)

    create_labeled_widget(top_level, "Select Color:", ttk.Combobox, selectcolor_var, values=color_values,
                          state="readonly")
    selectcolor_var.set(checkbutton.cget("selectcolor"))

    combo_offrelief = create_labeled_widget(top_level, "Off Relief (Only with Indicator Off):", ttk.Combobox,
                                            offrelief_var, values=offrelief_values, state="readonly")
    offrelief_var.set(checkbutton.cget("offrelief"))

    update_offrelief_state()

    tk.Button(top_level, text="Ok", width=15, command=handle_ok).pack(padx=5, pady=5)
    tk.Button(top_level, text="Cancel", width=15, command=handle_cancel).pack(padx=5, pady=5)

    top_level.grab_set()


def reset_to_default():
    text_var.set("Check me!")
    width_var.set(12)
    indicatoron_var.set("True")
    selectcolor_var.set("white")
    offrelief_var.set("flat")
    apply_changes()
    save_settings()


def save_settings():
    settings = {
        "text": text_var.get(),
        "width": width_var.get(),
        "indicatoron": indicatoron_var.get(),
        "selectcolor": selectcolor_var.get(),
        "offrelief": offrelief_var.get(),
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except (IOError, json.JSONDecodeError):
        pass


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        reset_to_default()
        return

    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)

        if not isinstance(settings, dict):
            raise ValueError("Invalid JSON structure")

        text = settings.get("text", "Check me!")
        width = settings.get("width", 12)
        indicatoron = settings.get("indicatoron", "True")
        selectcolor = settings.get("selectcolor", "white")
        offrelief = settings.get("offrelief", "flat")

        if (indicatoron not in indicator_values
            or selectcolor not in color_values
            or offrelief not in offrelief_values
            or not (12 <= width <= 30)
            or text == ""):
            reset_to_default()
        else:
            checkbutton.config(
                text=text,
                width=width,
                indicatoron=indicatoron == "True",
                selectcolor=selectcolor,
                offrelief=offrelief
            )

    except (IOError, json.JSONDecodeError, ValueError):
        reset_to_default()


checkbutton = tk.Checkbutton(
    root,
    text="Check me!",
    variable=check_var,
    width=12,
    indicatoron=True,
    selectcolor="white",
    offrelief="flat",
)
checkbutton.pack(padx=5, pady=5, fill="x")

button_adjust = tk.Button(text="Adjust", width=10, command=handle_adjust)
button_adjust.pack(padx=5, pady=5)

button_reset = tk.Button(text="Reset to Default", width=15, command=reset_to_default)
button_reset.pack(padx=5, pady=5)

load_settings()
root.mainloop()