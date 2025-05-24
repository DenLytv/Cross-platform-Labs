import sqlite3
import csv
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


class ApplicationManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Application Management System")
        self.data_file = "applications.json"
        self.db_file = "applications.sqlite"
        self.config_file = "config.json"

        # Email configuration
        self.email_config = {
            "receiver_email": os.getenv("SMTP_DESTINATION_EMAIL"),
            "notify_on_add": True,
            "notify_on_edit": False,
            "notify_on_delete": False
        }

        self.SMTP_CONFIG = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": os.getenv("SMTP_EMAIL"),
            "sender_password": os.getenv("SMTP_PASSWORD")
        }

        if not self.SMTP_CONFIG["sender_email"] or not self.SMTP_CONFIG["sender_password"]:
            messagebox.showwarning(
                "Email Configuration",
                "SMTP credentials not found. Email notifications will be disabled."
            )

        self.original_order = []
        self.applications = {}
        self.next_id = 1
        self.highlighted_items = set()

        self.current_filter = "All"
        self.current_search = ""
        self.sort_column = None
        self.sort_reverse = False

        self.dragging_item = None

        self.db_init()
        self.load_data_from_file()
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_email_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.title("Email Notification Settings")


        tk.Label(dialog, text="Receiver Email:").pack(pady=10, padx=10)
        receiver_email_entry = tk.Entry(dialog, width=40)
        receiver_email_entry.pack(pady=10, padx=10)
        receiver_email_entry.insert(0, self.email_config["receiver_email"])

        tk.Label(dialog, text="Notification Types:").pack(pady=10, padx=10)

        notify_frame = tk.Frame(dialog)
        notify_frame.pack(pady=10, padx=10)

        notify_add = tk.BooleanVar(value=self.email_config["notify_on_add"])
        tk.Checkbutton(notify_frame, text="New applications", variable=notify_add).pack(anchor="w")

        notify_edit = tk.BooleanVar(value=self.email_config["notify_on_edit"])
        tk.Checkbutton(notify_frame, text="Application edits", variable=notify_edit).pack(anchor="w")

        notify_delete = tk.BooleanVar(value=self.email_config["notify_on_delete"])
        tk.Checkbutton(notify_frame, text="Application deletions", variable=notify_delete).pack(anchor="w")

        def save_settings():
            self.email_config = {
                "receiver_email": receiver_email_entry.get(),
                "notify_on_add": notify_add.get(),
                "notify_on_edit": notify_edit.get(),
                "notify_on_delete": notify_delete.get()
            }
            dialog.destroy()

        tk.Button(dialog, text="Save", command=save_settings, width=10).pack(pady=10, padx=10)

    def send_email(self, subject, body):
        if not self.SMTP_CONFIG["sender_email"] or not self.SMTP_CONFIG["sender_password"]:
            return

        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = self.SMTP_CONFIG["sender_email"]
            msg['To'] = self.email_config["receiver_email"]

            with smtplib.SMTP(self.SMTP_CONFIG["smtp_server"], self.SMTP_CONFIG["smtp_port"]) as server:
                server.starttls()
                server.login(self.SMTP_CONFIG["sender_email"], self.SMTP_CONFIG["sender_password"])
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")

    def export_to_pdf(self):
        file_path = filedialog.asksaveasfilename(
            title="Export to PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            defaultextension=".pdf",
            initialfile="applications_report"
        )

        if not file_path:
            return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, txt="Applications Report", ln=1, align='C')
            pdf.cell(200, 10, txt=f"on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align='C')
            pdf.ln(10)

            total_apps = len(self.applications)
            total_seats = sum(app[2] for app in self.applications.values())
            unique_applicants = len(set(app[1] for app in self.applications.values()))

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Summary Statistics", ln=1)
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 8, txt=f"Total applications: {total_apps}", ln=1)
            pdf.cell(200, 8, txt=f"Total seats requested: {total_seats}", ln=1)
            pdf.cell(200, 8, txt=f"Unique applicants: {unique_applicants}", ln=1)
            pdf.ln(10)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Applications List", ln=1)
            pdf.set_font("Arial", 'B', 10)

            col_widths = [80, 60, 30]
            headers = ["Event Name", "Applicant", "Seats"]
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, txt=header, border=1)
            pdf.ln()

            pdf.set_font("Arial", size=10)
            for app_id in self.original_order:
                if app_id in self.applications:
                    event, applicant, seats = self.applications[app_id]
                    pdf.cell(col_widths[0], 8, txt=event[:35], border=1)
                    pdf.cell(col_widths[1], 8, txt=applicant[:25], border=1)
                    pdf.cell(col_widths[2], 8, txt=str(seats), border=1)
                    pdf.ln()

            pdf.output(file_path)
            messagebox.showinfo("Success", "PDF report generated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

    def setup_statistics_panel(self):
        self.stats_frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        self.stats_frame.pack(fill=tk.X, padx=5, pady=5)

        stats_labels = [
            ("Total Applications:", "total_apps"),
            ("Total Seats:", "total_seats"),
            ("Unique Applicants:", "unique_apps"),
            ("Avg Seats/App:", "avg_seats")
        ]

        self.stats_vars = {}
        for i, (label_text, var_name) in enumerate(stats_labels):
            tk.Label(self.stats_frame, text=label_text).grid(row=0, column=i * 2, padx=5, sticky="e")
            self.stats_vars[var_name] = tk.StringVar()
            tk.Label(self.stats_frame, textvariable=self.stats_vars[var_name],
                     width=10, anchor="w").grid(row=0, column=i * 2 + 1, padx=5, sticky="w")

        self.update_statistics()

    def update_statistics(self):
        total_apps = len(self.applications)
        total_seats = sum(app[2] for app in self.applications.values())
        unique_apps = len(set(app[1] for app in self.applications.values()))
        avg_seats = total_seats / total_apps if total_apps > 0 else 0

        self.stats_vars["total_apps"].set(str(total_apps))
        self.stats_vars["total_seats"].set(str(total_seats))
        self.stats_vars["unique_apps"].set(str(unique_apps))
        self.stats_vars["avg_seats"].set(f"{avg_seats:.1f}")

    def db_init(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY,
                    event TEXT,
                    applicant TEXT,
                    seats INTEGER
                )
            """)
            conn.commit()

    def db_save_all(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM applications")
            for app_id in self.original_order:
                if app_id in self.applications:
                    event, applicant, seats = self.applications[app_id]
                    cursor.execute(
                        "INSERT INTO applications VALUES (?, ?, ?, ?)",
                        (app_id, event, applicant, seats)
                    )
            conn.commit()

    def db_load_all(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applications ORDER BY id")
            rows = cursor.fetchall()

        self.applications = {}
        self.original_order = []
        self.next_id = 1

        for row in rows:
            app_id, event, applicant, seats = row
            self.applications[app_id] = (event, applicant, seats)
            self.original_order.append(app_id)
            if app_id >= self.next_id:
                self.next_id = app_id + 1

    def csv_export(self):
        file_path = filedialog.asksaveasfilename(
            title="Export to CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            defaultextension=".csv",
            initialfile="applications"
        )

        if not file_path:
            return

        data_to_export = []
        for app_id in self.original_order:
            if app_id in self.applications:
                data_to_export.append(self.applications[app_id])

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Event name", "Applicant", "Seats number"])
                writer.writerows(data_to_export)
            messagebox.showinfo("Success", "Data exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def csv_import(self):
        file_path = filedialog.askopenfilename(
            title="Import from CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            defaultextension=".csv"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)
                imported_data = [row for row in reader if len(row) == 3]

            if not imported_data:
                messagebox.showinfo("Info", "No valid data found in the CSV file")
                return

            self.applications = {}
            self.original_order = []
            self.next_id = 1
            self.highlighted_items = set()

            for row in imported_data:
                try:
                    event, applicant = row[0], row[1]
                    seats = int(row[2])
                    if seats < 1:
                        raise ValueError("Seats must be positive")
                    elif not event or not applicant:
                        raise ValueError("Event and applicant names cannot be empty")

                    self.applications[self.next_id] = (event, applicant, seats)
                    self.original_order.append(self.next_id)
                    self.next_id += 1
                except (ValueError, IndexError):
                    continue

            self.save_data_to_file()
            self.db_save_all()
            self.refresh_display()
            messagebox.showinfo("Success", "Data imported successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import data: {str(e)}")

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
            else:
                self.db_load_all()
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

    def setup_ui(self):
        self.setup_toolbar()
        self.setup_search_frame()
        self.setup_treeview()
        self.setup_statistics_panel()
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
            ("Clear Highlight", self.clear_highlight),
            ("Export CSV", self.csv_export),
            ("Import CSV", self.csv_import),
            ("Export PDF", self.export_to_pdf),
            ("Email Setup", self.setup_email_dialog),
            ("Sync DB", self.db_save_all)
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
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export to CSV", command=self.csv_export)
        self.context_menu.add_command(label="Import from CSV", command=self.csv_import)
        self.context_menu.add_command(label="Sync with Database", command=self.db_save_all)

    def validate_application_data(self, app_data):
        if len(app_data) != 3:
            return False

        event, applicant, seats = app_data
        return (isinstance(event, str) and bool(event.strip()) and
                isinstance(applicant, str) and bool(applicant.strip()) and
                isinstance(seats, int) and seats >= 1)

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
        self.update_statistics()

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
            self.db_save_all()
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
        self.db_save_all()
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
        def validate_seats(value):
            return value.isdecimal() and int(value) > 0 or value == ""

        def show_invalid_seats():
            status_label.config(text="Please enter valid seats number!")

        entries = {}
        for label_text, field_name, row in fields:
            tk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            if field_name == "seats":
                entry = tk.Entry(
                    main_frame,
                    width=40,
                    validate="key",
                    validatecommand=(main_frame.register(validate_seats), "%P"),
                    invalidcommand=main_frame.register(show_invalid_seats)
                )
            else:
                entry = tk.Entry(main_frame, width=40)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            entries[field_name] = entry

        status_label = tk.Label(main_frame, fg="red", font=("Arial", 8, "normal"))
        status_label.grid(row=3, column=0, columnspan=2, padx=5, sticky="w")

        if old_values:
            for field, value in zip(["event", "applicant", "seats"], old_values):
                entries[field].insert(0, value)

        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        def save():
            event = entries["event"].get().strip()
            applicant = entries["applicant"].get().strip()
            seats = entries["seats"].get().strip()

            if not event or not applicant or not seats:
                messagebox.showerror("Error", "All fields are required", parent=dialog)
                return

            seats = int(seats)

            is_new = item_id is None

            if is_new:
                self.applications[self.next_id] = (event, applicant, seats)
                self.original_order.append(self.next_id)
                self.next_id += 1

                if self.email_config["notify_on_add"]:
                    subject = f"New Application: {event}"
                    body = (f"New application has been added:\n"
                            f"Event: {event})\n"
                            f"Applicant: {applicant}\n"
                            f"Seats: {seats}\n"
                            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                    self.send_email(subject, body)

            else:
                old_event, old_applicant, old_seats = self.applications[item_id]
                self.applications[item_id] = (event, applicant, seats)

                if (self.email_config["notify_on_edit"]
                        and not (event == old_event
                                 and applicant == old_applicant
                                 and seats == old_seats)):
                    subject = f"Application Updated: {event}"
                    body = (f"Application has been edited:\n"
                            f"Event: {event} (was: {old_event})\n"
                            f"Applicant: {applicant} (was: {old_applicant}))\n"
                            f"Seats: {seats} (was: {old_seats})\n"
                            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                    self.send_email(subject, body)

            self.save_data_to_file()
            self.db_save_all()
            self.refresh_display()
            self.update_statistics()
            dialog.destroy()

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
            if self.email_config["notify_on_delete"]:
                event, applicant, seats = self.applications[item_id]
                subject = "Application Deleted"
                body = (f"Application has been deleted: {event}\n"
                        f"Event: {event}\n"
                        f"Applicant: {applicant})\n"
                        f"Seats: {seats}\n"
                        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                self.send_email(subject, body)

            if item_id in self.highlighted_items:
                self.highlighted_items.remove(item_id)

            del self.applications[item_id]
            self.original_order.remove(item_id)
            self.save_data_to_file()
            self.db_save_all()
            self.refresh_display()

    def show_context_menu(self, event):
        item = self.treeview.identify_row(event.y)
        if item:
            self.treeview.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def on_closing(self):
        self.save_data_to_file()
        self.db_save_all()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationManager(root)
    root.mainloop()