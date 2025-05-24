import tkinter as tk
from tkinter import simpledialog

root = tk.Tk()
root.title("Code lock")
root.resizable(width=False, height=False)

frame_timer = tk.Frame(root)
frame_timer.pack(fill="x", padx=5, pady=5)

label_timer = tk.Label(frame_timer, bg="white", font=("Arial", 14), fg="green")
label_timer.pack(fill="x", padx=2, pady=2)

frame_display = tk.Frame(root)
frame_display.pack(fill="x", padx=5, pady=5)

label_display = tk.Label(frame_display, bg="white", font=("Arial", 14))
label_display.pack(fill="x", padx=2, pady=2)

frame_keyboard = tk.Frame(root)
frame_keyboard.pack(fill="both", padx=5, pady=5)

correct_code = "2156"
code = ""
current_attempts = 0
max_attempts = 3
ENTER_TIME = 60
time_left = ENTER_TIME
lock_time = 0
is_locked = False
timer_id = None

def reset():
    """Resets state of the lock, clears the code, and starts the timer."""
    global code, time_left
    code = ""
    time_left = ENTER_TIME
    label_display.config(text="Enter code", fg="black")
    if timer_id:
        root.after_cancel(timer_id)
    start_timer()

def start_timer():
    """Starts the countdown timer."""
    global time_left, timer_id
    if is_locked:
        label_timer.config(text="")
    elif time_left > 0:
        label_timer.config(text=f"Time: {time_left}s", fg="red" if time_left <= 10 else "green")
        time_left -= 1
        timer_id = root.after(1000, start_timer)
    else:
        label_timer.config(text="Time is up", fg="red")
        lock_input()


def handle_digit(digit):
    """Handles digit input, reloads timer."""
    global code, time_left
    if is_locked or len(code) >= 4:
        return
    if not timer_id:
        time_left = ENTER_TIME
        start_timer()
    code += digit
    label_display.config(text=code, fg="black")

def handle_back():
    """Handles back button by removing last inputted number"""
    global code
    if is_locked:
        return
    code = code[:-1]
    label_display.config(text=code)

def handle_enter():
    """Handles enter button, restarts timer, counts attempts"""
    global code, current_attempts, timer_id, time_left
    if is_locked:
        return

    if code == correct_code:
        label_display.config(text="Correct!", fg="green")
        if timer_id:
            root.after_cancel(timer_id)
        timer_id = None
        label_timer.config(text="")
    else:
        if not timer_id:
            time_left = ENTER_TIME
            start_timer()
        current_attempts += 1
        attempts_difference = max_attempts - current_attempts
        label_display.config(text=f"Wrong! {attempts_difference} attempts" if attempts_difference > 1
        else f"Wrong! {attempts_difference} attempt", fg="red", font=("Arial", 12))
        if current_attempts >= max_attempts:
            lock_input()
    code = ""

def lock_input():
    """Locks input after failed attempts"""
    global is_locked, lock_time
    lock_time += 10
    is_locked = True
    countdown(lock_time)

def countdown(time_left):
    """Counts down, display remaining lock time."""
    if time_left > 0:
        label_display.config(text=f"Locked {time_left}s", fg="red", font=("Arial", 13))
        root.after(1000, countdown, time_left - 1)
        label_timer.config(text=f"")
    else:
        unlock_input()

def unlock_input():
    """Unlocks input after lock period"""
    global current_attempts, is_locked
    current_attempts = 0
    is_locked = False
    reset()

def handle_clear():
    """Handles clear button by clearing input field"""
    global code
    if is_locked:
        return
    code = ""
    label_display.config(text=code)

def change_code():
    """Changes code through a user prompt"""
    global correct_code
    new_code = simpledialog.askstring("New Code", "Enter new 4-digit code:")
    if new_code and new_code.isdigit() and len(new_code) == 4:
        correct_code = new_code
        label_display.config(text="Code changed", fg="green")
    else:
        label_display.config(text="Invalid code", fg="red")
    start_timer()

def key_press(event):
    """Handles keyboard input"""
    if event.char.isdigit():
        handle_digit(event.char)
    elif event.keysym == "Return":
        handle_enter()
    elif event.keysym == "BackSpace":
        handle_back()
    elif event.keysym == "Delete":
        handle_clear()
    elif event.keysym == "n" and event.state & 4:
        if timer_id:
            root.after_cancel(timer_id)
        change_code()

def create_buttons():
    """Creates digit keyboard buttons"""
    for i, digit in enumerate("789456123"):
        row, col = divmod(i, 3)
        button = tk.Button(frame_keyboard, width=5, text=digit, command=lambda d=digit: handle_digit(d))
        button.grid(row=row, column=col, padx=2, pady=2)

    button_back = tk.Button(frame_keyboard, width=5, text="Back", bg="yellow", command=handle_back)
    button_back.grid(row=3, column=0, padx=2, pady=2)

    button_0 = tk.Button(frame_keyboard, width=5, text="0", command=lambda: handle_digit("0"))
    button_0.grid(row=3, column=1, padx=2, pady=2)

    button_enter = tk.Button(frame_keyboard, width=5, text="Enter", bg="lightgreen", command=handle_enter)
    button_enter.grid(row=3, column=2, padx=2, pady=2)

    button_clear = tk.Button(frame_keyboard, text="Clear", bg="red", command=handle_clear)
    button_clear.grid(row=4, column = 0, columnspan=3, padx=2, pady=2, sticky="we")

root.bind("<KeyPress>", key_press)
create_buttons()
reset()

root.mainloop()
