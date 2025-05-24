import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from datetime import datetime
import random
import json
import pyperclip

search_results = []
current_search_index = -1
search_colors = ["#ffff00", "#aaffaa", "#ffaaaa", "#aaaaff"]

root = tk.Tk()
root.title("Enhanced Chat Bot - Digital Hygiene")

current_theme = "light"
themes = {
    "light": {
        "bg_color": "gray95",
        "fg_color": "black",
        "text_bg": "white",
        "button_bg": "#f0f0f0",
        "entry_bg": "white",
        "highlight_bg": "#f5f5f5",
    },
    "dark": {
        "bg_color" : "#2d2d2d",
        "fg_color": "white",
        "text_bg": "#1e1e1e",
        "button_bg": "#3d3d3d",
        "entry_bg": "#3d3d3d",
        "highlight_bg": "#4d4d4d",
    }
}

case_var = tk.BooleanVar(value=False)
id_message = 0

messages = [
    "Hello! Let's talk about social networks and digital hygiene. How often do you use social media?",
    "Which social networks do you like the most and why?",
    "Do you take measures to protect your privacy on social networks?",
    "How much time per day do you think is safe to spend on social media?",
    "Do you know what a digital detox is? Have you ever tried it?",
    "What signs might indicate social media addiction?",
    "Do you set time limits for using social networks?",
    "What's your opinion on two-factor authentication for social networks?",
    "Do you check the privacy settings in your social networks?",
    "How do you react to cyberbullying or toxic behavior online?",
    "Do you know how to recognize fake accounts or scams on social networks?",
    "What digital hygiene rules do you follow?",
    "Do you use different passwords for different social networks?",
    "What do you think are the main dangers of social networks?",
    "Have you taught your family members about digital safety basics?",
    "What advantages and disadvantages of social networks do you see?",
    "Do you use apps to monitor your time spent on social networks?",
    "How do social networks affect your mood and productivity?",
    "Do you have strategies to reduce your time on social networks?",
    "What advice would you give to a friend who wants to improve their digital hygiene?",
    "Thank you for the interesting conversation! I hope you learned something useful about digital hygiene. Stay safe online!"
]

frame_text = tk.Frame(root)
frame_text.pack(fill="both", expand=True)

scroll = tk.Scrollbar(frame_text)
scroll.pack(side="right", fill="y")

text_widget = tk.Text(frame_text, width=70, wrap="word", yscrollcommand=scroll.set,
                      state="disabled", font=("Arial", 10), bg="white", fg="black")
text_widget.pack(side="left", fill="both", expand=True, padx=(5, 0))
scroll.config(command=text_widget.yview)

text_widget.tag_config("user", foreground="#2c7be5")
text_widget.tag_config("bot", foreground="#009933")
text_widget.tag_config("system", foreground="#990099")
text_widget.tag_config("timestamp", foreground="#666666")
text_widget.tag_config("highlight", background="#ffff00")


def add_message(sender, text):
    text_widget.config(state="normal")
    timestamp = datetime.now().strftime("[%H:%M] ")

    if sender == "user":
        prefix = "You: "
        tag = "user"
    elif sender == "bot":
        prefix = "Bot: "
        tag = "bot"
    elif sender == "system":
        prefix = "System: "
        tag = "system"
    else:
        prefix = ""
        tag = ""

    text_widget.insert(tk.END, timestamp, "timestamp")
    text_widget.insert(tk.END, prefix, tag)
    text_widget.insert(tk.END, f"{text}\n", tag)
    text_widget.yview_moveto(1.0)
    text_widget.config(state="disabled")


def get_random_response():
    responses = [
        "Interesting point! What else would you like to discuss?",
        "I'd love to hear more about your experience.",
        "That's a great question about digital hygiene!",
        "Many people struggle with this aspect of social media.",
        "Let me think about that... What else interests you?"
    ]
    return random.choice(responses)


def save_chat():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    try:
        content = text_widget.get("1.0", tk.END)

        if file_path.endswith('.json'):
            chat_data = {
                "metadata": {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message_count": content.count('\n')
                },
                "messages": []
            }

            lines = content.split('\n')
            for line in lines:
                if not line.strip():
                    continue

                if line.startswith('['):
                    time_end = line.index(']') + 1
                    timestamp = line[:time_end].strip()
                    sender_end = line.index(':', time_end) + 1
                    sender = line[time_end:sender_end].strip()
                    message = line[sender_end:].strip()

                    if sender != "System:":
                        chat_data["messages"].append({
                            "timestamp": timestamp[1:-1],
                            "sender": sender[:-1],
                            "message": message
                        })
                else:
                    if chat_data["messages"]:
                        chat_data["messages"][-1]["message"] += "\n" + line.strip()

                chat_data["metadata"]["message_count"] = len(chat_data["messages"])

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)

        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        add_message("system", f"Chat saved successfully to {file_path}")

    except Exception as e:
        add_message("system", f"Error saving file: {str(e)}")
        messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")


def clear_chat():
    text_widget.config(state="normal")
    text_widget.delete("1.0", tk.END)
    text_widget.config(state="disabled")
    global id_message
    id_message = 0
    add_message("bot", messages[0])
    add_message("system", "Chat history cleared")


def show_stats():
    content = text_widget.get("1.0", tk.END)
    lines = content.split('\n')

    user_msgs = 0
    bot_msgs = 0
    system_msgs = 0
    user_words = 0
    bot_words = 0
    system_words = 0
    user_chars = 0
    bot_chars = 0
    system_chars = 0

    for line in lines:
        if not line.strip():
            continue

        if "System: " in line:
            system_msgs += 1
            try:
                message = line.split('System: ')[1]
                system_words += len(message.split())
                system_chars += len(message)
            except:
                pass
        elif "You: " in line:
            user_msgs += 1
            try:
                message = line.split('You: ')[1]
                user_words += len(message.split())
                user_chars += len(message)
            except:
                pass
        elif "Bot: " in line:
            bot_msgs += 1
            try:
                message = line.split('Bot: ')[1]
                bot_words += len(message.split())
                bot_chars += len(message)
            except:
                pass

    total_msgs = user_msgs + bot_msgs + system_msgs
    total_words = user_words + bot_words + system_words
    total_chars = user_chars + bot_chars + system_chars

    stats = (f"📊 Chat Statistics:\n\n"
             f"• Messages:\n"
             f"  - Your messages: {user_msgs} ({user_words} words, {user_chars} chars)\n"
             f"  - Bot messages: {bot_msgs} ({bot_words} words, {bot_chars} chars)\n"
             f"  - System messages: {system_msgs} ({system_words} words, {system_chars} chars)\n"
             f"  - Total: {total_msgs} messages, {total_words} words, {total_chars} chars\n\n"
             f"• Lines: {len([l for l in lines if l.strip()])}")

    add_message("system", "Displayed detailed chat statistics")
    messagebox.showinfo("Chat Statistics", stats)


def generate_password():
    length = 12
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()'
    password = ''.join(random.choice(chars) for _ in range(length))

    # Копіювання в буфер обміну
    pyperclip.copy(password)

    add_message("system", f"Generated password: {password} (copied to clipboard)")
    messagebox.showinfo("Password Generator",
                        f"Your new password:\n{password}\n\nPassword has been copied to clipboard!")


def check_password_strength():
    password = simpledialog.askstring("Password Strength Check", "Enter password to check:")
    if password:
        strength = 0
        if len(password) >= 8: strength += 1
        if any(c.isupper() for c in password): strength += 1
        if any(c.isdigit() for c in password): strength += 1
        if not password.isalnum(): strength += 1


        add_message("system", f"Your password is {'Weak' if strength < 3 else 'Strong'}")
        messagebox.showinfo("Password Strength",
                            f"Strength: {strength}/4\n{'Weak' if strength < 3 else 'Strong'}")


def start_timer():
    while True:
        mins = simpledialog.askinteger("Social Media Timer",
                                       "Enter positive number of minutes for social media usage:",
                                       minvalue=1, maxvalue=600)
        if mins is None:
            return
        elif mins <= 0:
            messagebox.showerror("Error", "Please enter a positive number")
            continue
        else:
            break

    add_message("system", f"Timer set for {mins} minutes")
    root.after(mins * 60000, times_up)

def times_up():
    add_message("system", f"Your social media time is over!")
    messagebox.showwarning("Time's up!", "Your social media time is over!")

def toggle_theme():
    global current_theme
    if current_theme == "light":
        current_theme = "dark"
    else:
        current_theme = "light"

    bg_color = themes[current_theme]["bg_color"]
    fg_color = themes[current_theme]["fg_color"]
    text_bg = themes[current_theme]["text_bg"]
    button_bg = themes[current_theme]["button_bg"]
    entry_bg = themes[current_theme]["entry_bg"]
    highlight_bg = themes[current_theme]["highlight_bg"]

    root.config(bg=bg_color)

    text_widget.config(bg=text_bg, fg=fg_color, insertbackground=fg_color)

    for frame in [frame_text, frame_send, frame_find, button_frame]:
        frame.config(bg=themes[current_theme]["bg_color"])

    entry_send.config(bg=entry_bg, fg=fg_color, insertbackground=fg_color)
    entry_search.config(bg=entry_bg, fg=fg_color)

    label_case.config(bg=bg_color, fg=fg_color)
    search_status.config(bg=bg_color, fg=fg_color)

    check_case.config(bg=bg_color, fg=fg_color, activebackground=bg_color, activeforeground=fg_color)

    scroll.config(bg=button_bg, troughcolor=bg_color, activebackground=highlight_bg)

    add_message("system", f"Switched to {current_theme} theme")

def handle_find_all():
    global search_results, current_search_index

    text_widget.tag_remove("highlight", "1.0", "end")
    text_widget.tag_remove("highlight_current", "1.0", "end")

    pattern = entry_search.get()
    if not pattern:
        return

    text_widget.config(state="normal")
    search_results = []
    current_search_index = -1

    index = "1.0"
    while True:
        position = text_widget.search(
            pattern, index, stopindex="end",
            nocase=not case_var.get()
        )
        if not position:
            break
        end_pos = f"{position}+{len(pattern)}c"
        search_results.append((position, end_pos))
        index = end_pos

    for i, (start, end) in enumerate(search_results):
        color_idx = i % len(search_colors)
        text_widget.tag_add(f"highlight_{color_idx}", start, end)

    if search_results:
        current_search_index = 0
        highlight_current_match()
        update_search_status()
    else:
        add_message("system", f"No matches found for '{pattern}'")

    text_widget.config(state="disabled")


def highlight_current_match():
    if not search_results or current_search_index < 0:
        return

    text_widget.tag_remove("highlight_current", "1.0", "end")

    start, end = search_results[current_search_index]
    text_widget.tag_add("highlight_current", start, end)
    text_widget.see(start)

    update_search_status()


def update_search_status():
    if search_results:
        status = f"Match {current_search_index + 1} of {len(search_results)}"
        search_status.config(text=status)
    else:
        search_status.config(text="No matches")


def next_match():
    global current_search_index
    if search_results:
        current_search_index = (current_search_index + 1) % len(search_results)
        highlight_current_match()


def prev_match():
    global current_search_index
    if search_results:
        current_search_index = (current_search_index - 1) % len(search_results)
        highlight_current_match()


def handle_send():
    global id_message
    post = entry_send.get().strip()
    if not post:
        return

    if post.startswith("/"):
        if post == "/help":
            add_message("system",
                        "Available commands: /help, /clear, /save, /stats, /theme, /password, /timer, /checkpassword")
        elif post == "/clear":
            clear_chat()
        elif post == "/save":
            save_chat()
        elif post == "/stats":
            show_stats()
        elif post == "/theme":
            toggle_theme()
        elif post == "/password":
            generate_password()
        elif post == "/timer":
            start_timer()
        elif post == "/checkpassword":
            check_password_strength()
        else:
            add_message("system", "Unknown command. Type /help for options")
        entry_send.delete(0, tk.END)
        return

    add_message("user", post)
    entry_send.delete(0, tk.END)

    if id_message >= len(messages):
        add_message("bot", get_random_response())
    else:
        add_message("bot", messages[id_message])
        id_message += 1


frame_send = tk.Frame(root)
frame_send.pack(fill="x", padx=5, pady=5)

entry_send = tk.Entry(frame_send, width=50, font=("Arial", 11))
entry_send.pack(side="left", fill="x", expand=True, padx=5, pady=5)
entry_send.bind("<Return>", lambda e: handle_send())

button_send = tk.Button(
    frame_send, text="Send", width=10,
    command=handle_send, bg="#4CAF50", fg="white"
)
button_send.pack(side="left", padx=5, pady=5)

frame_find = tk.Frame(root)
frame_find.pack(fill="x", padx=5, pady=5)

entry_search = tk.Entry(frame_find, font=("Arial", 10))
entry_search.pack(side="left", fill="x", expand=True, padx=5, pady=5)

label_case = tk.Label(frame_find, text="Match case:")
label_case.pack(side="left", pady=5)

check_case = tk.Checkbutton(frame_find, variable=case_var)
check_case.pack(side="left", pady=5)

tk.Button(
    frame_find, text="◄", width=2,
    command=prev_match
).pack(side="left", padx=2)

tk.Button(
    frame_find, text="►", width=2,
    command=next_match
).pack(side="left", padx=2)

button_find = tk.Button(
    frame_find, text="Find All", width=8,
    command=handle_find_all
)
button_find.pack(side="left", padx=5)

search_status = tk.Label(frame_find, text="", fg="gray")
search_status.pack(side="left", padx=5)

button_frame = tk.Frame(root)
button_frame.pack(fill="x", padx=5, pady=5)

tk.Button(
    button_frame, text="Save Chat", width=10,
    command=save_chat, bg="#2196F3", fg="white"
).pack(side="left", padx=5)

tk.Button(
    button_frame, text="Clear Chat", width=10,
    command=clear_chat, bg="#f44336", fg="white"
).pack(side="left", padx=5)

tk.Button(
    button_frame, text="Stats", width=10,
    command=show_stats, bg="#9C27B0", fg="white"
).pack(side="left", padx=5)

tk.Button(
    button_frame, text="Theme", width=10,
    command=toggle_theme, bg="#607D8B", fg="white"
).pack(side="left", padx=5)

tk.Button(
    button_frame, text="Gen Password", width=12,
    command=generate_password, bg="#FF9800", fg="white"
).pack(side="left", padx=5)

tk.Button(
    button_frame, text="Set Timer", width=10,
    command=start_timer, bg="#607D8B", fg="white"
).pack(side="left", padx=5)

tk.Button(
    button_frame, text="Check Password", width=14,
    command=check_password_strength, bg="#795548", fg="white"
).pack(side="left", padx=5)

for i, color in enumerate(search_colors):
    text_widget.tag_config(f"highlight_{i}", background=color)
text_widget.tag_config("highlight_current", background="#ff9900", underline=1)

entry_send.bind("<Return>", lambda e: handle_send())
root.bind("<KeyPress>", lambda e: text_widget.tag_remove("highlight", "1.0", "end"))

add_message("bot", messages[0])
id_message = 1
entry_send.focus_set()

root.mainloop()