import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class ApplicationManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Application Management System")
        self.data_file = "applications.json"

        self.original_order = []
        self.applications = {}
        self.next_id = 1
        self.highlighted_items = set()

        self.current_filter = "All"
        self.current_search = ""
        self.sort_column = None
        self.sort_reverse = False

        self.dragging_item = None

        self.load_data_from_file()
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        self.setup_toolbar()
        self.setup_search_frame()
        self.setup_treeview()
        self.setup_context_menu()
        self.refresh_display()

    def setup_toolbar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        buttons = [
            ("Add", self.add_application),
            ("Delete", self.delete_application),
            ("Edit", self.edit_application),
            ("Highlight", self.highlight_selected),
            ("Clear Highlight", self.clear_highlight)
        ]

        for text, command in buttons:
            tk.Button(toolbar, text=text, command=command).pack(side=tk.LEFT, padx=2)

    def setup_search_frame(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        tk.Label(search_frame, text="Filter by seats:").pack(side=tk.LEFT, padx=(10, 0))
        self.filter_var = tk.StringVar(value="All")
        options = ["All", "1", "2", "3", "4", "5+"]
        tk.OptionMenu(search_frame, self.filter_var, *options, command=lambda e: self.apply_filters()).pack(
            side=tk.LEFT)

    def setup_treeview(self):
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.treeview = ttk.Treeview(
            self.tree_frame,
            columns=("event", "applicant", "seats"),
            show="headings",
            selectmode="browse"
        )

        columns = {
            "event": ("Event name", 300),
            "applicant": ("Applicant", 200),
            "seats": ("Seats number", 100)
        }

        for col, (text, width) in columns.items():
            self.treeview.heading(col, text=text, command=lambda c=col: self.sort_by_column(c))
            self.treeview.column(col, width=width, anchor="w" if col != "seats" else "center")

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.treeview.tag_configure('highlight', background='#e6f3ff')

        self.treeview.bind("<Double-1>", lambda e: self.edit_application())
        self.treeview.bind("<Button-3>", self.show_context_menu)
        self.treeview.bind("<ButtonPress-1>", self.on_drag_start)
        self.treeview.bind("<B1-Motion>", self.on_drag_motion)
        self.treeview.bind("<ButtonRelease-1>", self.on_drag_end)
        self.treeview.bind("<KeyPress-Page_Up>", lambda e: self.on_key_move("up"))
        self.treeview.bind("<KeyPress-Page_Down>", lambda e: self.on_key_move("down"))
        self.treeview.bind("<KeyPress-Home>", lambda e: self.on_key_move("home"))
        self.treeview.bind("<KeyPress-End>", lambda e: self.on_key_move("end"))

    def setup_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Add", command=self.add_application)
        self.context_menu.add_command(label="Edit", command=self.edit_application)
        self.context_menu.add_command(label="Delete", command=self.delete_application)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Highlight", command=self.highlight_selected)
        self.context_menu.add_command(label="Clear Highlight", command=self.clear_highlight)

    def load_data_from_file(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for app in data:
                        if self.validate_application_data(app):
                            self.applications[self.next_id] = (app[0], app[1], int(app[2]))
                            self.original_order.append(self.next_id)
                            self.next_id += 1
        except (json.JSONDecodeError, IOError):
            default_data = [
                ("Python Conference", "Ivanov I.I.", 3),
                ("Data Science Seminar", "Petrova P.P.", 2),
                ("Tkinter Workshop", "Sydorov S.S.", 5),
                ("AI Lecture", "Kovalenko K.K.", 1),
                ("Pandas Workshop", "Melnyk M.M.", 4),
                ("IT News Presentation", "Lysenko L.L.", 2),
                ("SQL Training", "Shevchenko Sh.Sh.", 3),
                ("Networking Evening", "Bondarenko B.B.", 6),
                ("Machine Learning Course", "Tkachenko T.T.", 1),
                ("Experts Meeting", "Savchenko S.S.", 2)
            ]
            for app in default_data:
                self.applications[self.next_id] = app
                self.original_order.append(self.next_id)
                self.next_id += 1

    def save_data_to_file(self):
        try:
            data_to_save = [self.applications[app_id] for app_id in self.original_order]
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def refresh_display(self):
        self.treeview.delete(*self.treeview.get_children())

        filtered_data = []
        for app_id in self.original_order:
            if app_id in self.applications:
                event, applicant, seats = self.applications[app_id]

                search_ok = (not self.current_search or
                             self.current_search in event.lower() or
                             self.current_search in applicant.lower())

                if self.current_filter == "All":
                    filter_ok = True
                elif self.current_filter == "5+":
                    filter_ok = seats >= 5
                else:
                    filter_ok = seats == int(self.current_filter)

                if search_ok and filter_ok:
                    filtered_data.append((app_id, (event, applicant, seats)))

        if self.sort_column:
            col_index = ["event", "applicant", "seats"].index(self.sort_column)
            filtered_data.sort(key=lambda x: x[1][col_index], reverse=self.sort_reverse)

        for app_id, app_data in filtered_data:
            tags = ['highlight'] if app_id in self.highlighted_items else []
            self.treeview.insert("", "end", values=app_data, tags=tags, iid=str(app_id))

        self.update_column_headers()

    def apply_filters(self, event=None):
        self.current_search = self.search_var.get().lower()
        self.current_filter = self.filter_var.get()
        self.refresh_display()

    def sort_by_column(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.refresh_display()

    def update_column_headers(self):
        for col in ["event", "applicant", "seats"]:
            text = col.capitalize().replace("_", " ")
            if col == self.sort_column:
                arrow = "▼" if self.sort_reverse else "▲"
                text = f"{text} {arrow}"
            self.treeview.heading(col, text=text)

    def validate_application_data(self, app_data):
        if len(app_data) != 3:
            return False

        event, applicant, seats = app_data
        return (isinstance(event, str) and bool(event.strip()) and
                isinstance(applicant, str) and bool(applicant.strip()) and
                isinstance(seats, int) and seats >= 1)

    def on_drag_start(self, event):
        self.dragging_item = self.treeview.identify_row(event.y)
        if self.dragging_item:
            self.treeview.selection_set(self.dragging_item)

    def on_drag_motion(self, event):
        if not self.dragging_item:
            return

        target_item = self.treeview.identify_row(event.y)
        if target_item and self.dragging_item != target_item:
            self.treeview.move(self.dragging_item, "", self.treeview.index(target_item))

    def on_drag_end(self, event):
        if self.dragging_item:
            moved_id = int(self.dragging_item)
            new_index = self.treeview.index(self.dragging_item)

            self.original_order.remove(moved_id)
            self.original_order.insert(new_index, moved_id)

            self.save_data_to_file()
            self.dragging_item = None

    def on_key_move(self, direction):
        selected = self.treeview.selection()
        if not selected:
            return

        selected_item = selected[0]
        current_index = self.treeview.index(selected_item)
        items = self.treeview.get_children()

        if direction == "up" and current_index > 0:
            new_index = current_index - 1
        elif direction == "down" and current_index < len(items) - 1:
            new_index = current_index + 1
        elif direction == "home":
            new_index = 0
        elif direction == "end":
            new_index = len(items) - 1
        else:
            return

        self.treeview.move(selected_item, "", new_index)

        moved_id = int(selected_item)
        self.original_order.remove(moved_id)
        self.original_order.insert(new_index, moved_id)

        self.save_data_to_file()
        self.treeview.selection_set(selected_item)
        self.treeview.focus(selected_item)

    def highlight_selected(self):
        selected = self.treeview.selection()
        if not selected:
            messagebox.showinfo("Select Event", "Please select event to highlight")
            return
        app_id = int(selected[0])
        if app_id not in self.highlighted_items:
            self.highlighted_items.add(app_id)
            self.treeview.item(selected[0], tags=('highlight',))
        self.refresh_display()

    def clear_highlight(self):
        selected = self.treeview.selection()
        if not selected:
            messagebox.showinfo("Select Event", "Please select event to clear highlight")
            return
        app_id = int(selected[0])
        if app_id in self.highlighted_items:
            self.highlighted_items.remove(app_id)
            self.treeview.item(selected[0], tags=())
        self.refresh_display()

    def add_application(self):
        self.application_dialog("Add New Application")

    def edit_application(self, event=None):
        selected = self.treeview.selection()
        if not selected:
            messagebox.showinfo("Select Event", "Please select event to edit")
            return

        item_id = int(selected[0])
        old_values = self.treeview.item(selected[0], "values")
        self.application_dialog("Edit Application", old_values, item_id)

    def application_dialog(self, title, old_values=None, item_id=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, padx=10, pady=10)
        main_frame.pack()

        fields = [
            ("Event name:", "event", 0),
            ("Applicant:", "applicant", 1),
            ("Seats number:", "seats", 2)
        ]

        entries = {}
        for label_text, field_name, row in fields:
            tk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(main_frame, width=40)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            entries[field_name] = entry

        if old_values:
            for field, value in zip(["event", "applicant", "seats"], old_values):
                entries[field].insert(0, value)

        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def save():
            try:
                event = entries["event"].get().strip()
                applicant = entries["applicant"].get().strip()

                if not event or not applicant:
                    messagebox.showerror("Error", "All fields are required", parent=dialog)
                    return

                seats = int(entries["seats"].get().strip())

                if seats < 1:
                    messagebox.showerror("Error", "Number of seats must be greater than 0", parent=dialog)
                    return

                if item_id is not None:
                    self.applications[item_id] = (event, applicant, seats)
                else:
                    self.applications[self.next_id] = (event, applicant, seats)
                    self.original_order.append(self.next_id)
                    self.next_id += 1

                self.save_data_to_file()
                self.refresh_display()
                dialog.destroy()

            except ValueError as e:
                messagebox.showerror("Error", "Number of seats must be an integer", parent=dialog)

        tk.Button(button_frame, text="Save", width=10, command=save).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", width=10, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        main_frame.columnconfigure(1, weight=1)

    def delete_application(self):
        selected = self.treeview.selection()
        if not selected:
            messagebox.showinfo("Select Event", "Please select event to delete")
            return

        item_id = int(selected[0])

        if messagebox.askyesno("Confirm", "Delete selected application?"):
            if item_id in self.highlighted_items:
                self.highlighted_items.remove(item_id)

            del self.applications[item_id]
            self.original_order.remove(item_id)
            self.save_data_to_file()
            self.refresh_display()

    def show_context_menu(self, event):
        item = self.treeview.identify_row(event.y)
        if item:
            self.treeview.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def on_closing(self):
        self.save_data_to_file()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationManager(root)
    root.mainloop()