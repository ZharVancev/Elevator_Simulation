import tkinter as tk
import threading
import time
import queue

MOVE_TIME = 1
BOARDING_TIME = 1


def smart_list(direction, f_floor, targets):
    if not targets:
        return []
    targets = list(set(targets))
    min_distance = None
    nearest = None
    if direction == "goes up":
        max_v = max(targets)
        targets.remove(max_v)
        targets.insert(0, max_v)
    elif direction == "is going down":
        min_v = min(targets)
        targets.remove(min_v)
        targets.insert(0, min_v)
    elif direction == "is not moving":
        for i in targets:
            if min_distance is None or abs(i - f_floor) <= min_distance:
                min_distance = abs(i - f_floor)
                nearest = i
        if nearest:
            targets.remove(nearest)
            targets.insert(0, nearest)
    return targets


def el_life():
    global elevator_floor
    global elevator_direction
    global elevator_path
    global stop
    while True:
        if not elevator_path and not stop:
            log_queue.put(f"The elevator is on floor {elevator_floor}\n")
            elevator_direction = "is not moving"
            stop = True
            continue
        if elevator_path:
            if elevator_floor in elevator_path:
                log_queue.put(f"{elevator_floor} Stopped. Doors opened\n")
                elevator_path.remove(elevator_floor)
                time.sleep(BOARDING_TIME)
                continue
            elif elevator_floor < elevator_path[0]:
                elevator_floor += 1
                log_queue.put(f"the elevator goes up to floor:{elevator_floor}\n")
                elevator_direction = "goes up"
                stop = False
            elif elevator_floor > elevator_path[0]:
                elevator_floor -= 1
                elevator_direction = "is going down"
                log_queue.put(f"The elevator goes down to floor:{elevator_floor}\n")
                stop = False
            time.sleep(MOVE_TIME)


def new_values():
    global elevator_path
    try:
        new_floors = [x for x in entered.get().split()]
        if new_floors:
            new_floors = [int(x) for x in new_floors]
            if max(new_floors) > max_floor or min(new_floors) <= 0:
                bad_floors = str([x for x in new_floors if x > max_floor or x <= 0])[1:-1]
                text_elevator.insert(tk.END,f"There is no floor number {bad_floors} in the building\n")
            new_floors = [int(x) for x in new_floors if 0 < int(x) <= max_floor]
            if new_floors:
                text_elevator.insert(tk.END, f"the elevator is called to floors {str(new_floors)[1:-1]}\n")
                label_1.config(text="enter the floors separated by a space")
                label_2.config(text="")
                elevator_path = smart_list(elevator_direction, elevator_floor, elevator_path + new_floors)
        entered.delete(0, tk.END)
    except ValueError:
        label_2.config(text="You entered a bad number, please try again")
        entered.delete(0, tk.END)


def max_f():
    global max_floor
    try:
        value = int(entered.get())
        if value == 1:
            label_1.config(text="Why do you need an elevator in a one-story building?")
            entered.delete(0, tk.END)
        elif value <= 0:
            label_1.config(text="enter a number greater than zero")
            entered.delete(0, tk.END)
        else:
            max_floor = value
            label_1.config(text="enter the floors separated by a space")
            label_2.config(text="")
            button.config(command=new_values)
            entered.delete(0, tk.END)
            (threading.Thread(target=el_life, daemon=True)).start()
            text_elevator.insert(tk.END, f"maximum floor {max_floor}\n")
    except ValueError:
        label_2.config(text="an invalid number was entered, enter the maximum floor agin ")
        entered.delete(0, tk.END)


def update_gui_from_queue():
    try:
        while True:
            log = log_queue.get_nowait()
            text_elevator.insert(tk.END, log)
            text_elevator.see(tk.END)
    except queue.Empty:
        pass
    window.after(100, update_gui_from_queue)


log_queue = queue.Queue()


window = tk.Tk()
window.title("elevator_simulation")
window.geometry("525x300")

left_frame = tk.Frame(window)
left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

right_frame = tk.Frame(window)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10, expand=True, fill=tk.BOTH)

text_elevator = tk.Text(right_frame, width=30, height=10, bg="#f0f0f0", font=("Arial", 10))
text_elevator.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

scrollbar = tk.Scrollbar(right_frame, command=text_elevator.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_elevator.config(yscrollcommand=scrollbar.set)


label_1 = tk.Label(left_frame, text="Enter the maximum floor", wraplength=140)
label_1.pack(pady=10)

entered = tk.Entry(left_frame)
entered.pack(pady=5)

button = tk.Button(left_frame, command=max_f, text="send")
button.pack(pady=10)

label_2 = tk.Label(left_frame, text="", wraplength=140)
label_2.pack(pady=10)

entered.bind("<Return>", lambda event: button.invoke())

elevator_floor, elevator_path, elevator_direction, max_floor, stop = 1, [], "is not moving", 0, False


update_gui_from_queue()
window.protocol("WM_DELETE_WINDOW", window.destroy)
window.mainloop()
