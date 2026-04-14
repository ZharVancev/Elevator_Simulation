import tkinter as tk
import threading
import time
import queue

MOVE_TIME = 1
BOARDING_TIME = 1


def prioritize_floors(direction, floor, targets):   #Выбирает главную цель для лифта и ставит ее в начало списка 
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
            if min_distance is None or abs(i - floor) <= min_distance:
                min_distance = abs(i - floor)
                nearest = i
        if nearest:
            targets.remove(nearest)
            targets.insert(0, nearest)
    return targets


def run_elevator():                #отвечает за жизь лифта. Его движение, открытие дверей. Выводит состояние лифта в данный момент 
    global current_floor
    global elevator_direction
    global target_floors
    global is_waiting
    while True:
        if not target_floors and not is_waiting:
            log_queue.put(f"The elevator is on floor {current_floor}\n")
            elevator_direction = "is not moving"
            is_waiting = True
            time.sleep(1)
            continue
        if target_floors:
            if current_floor in target_floors:
                log_queue.put(f"{current_floor} floor. Stop. Doors opened\n")
                target_floors.remove(current_floor)
                time.sleep(BOARDING_TIME)
                continue
            elif current_floor < target_floors[0]:
                current_floor += 1
                log_queue.put(f"the elevator goes up to floor:{current_floor}\n")
                elevator_direction = "goes up"
                is_waiting = False
            elif current_floor > target_floors[0]:
                current_floor -= 1
                elevator_direction = "is going down"
                log_queue.put(f"The elevator goes down to floor:{current_floor}\n")
                is_waiting = False
            time.sleep(MOVE_TIME)


def add_floors():         #функция отвечающая за принятие новыых этажей. Выводит этажи на которые был вызван лифт и ошибки ввода
    global target_floors
    try:
        new_floors = [x for x in floor_entry.get().split()]
        if new_floors:
            new_floors = [int(x) for x in new_floors]
            if max(new_floors) > max_floor or min(new_floors) <= 0:
                bad_floors = str([x for x in new_floors if x > max_floor or x <= 0])[1:-1]
                text_elevator.insert(tk.END,f"There is no floor number {bad_floors} in the building\n")
            new_floors = [int(x) for x in new_floors if 0 < int(x) <= max_floor]
            if new_floors:
                text_elevator.insert(tk.END, f"the elevator is called to floors {str(new_floors)[1:-1]}\n")
                instruction_lbl.config(text="enter the floors separated by a space")
                error_lbl.config(text="")
                target_floors = prioritize_floors(elevator_direction, current_floor, target_floors + new_floors)
        floor_entry.delete(0, tk.END)
    except ValueError:
        error_lbl.config(text="You floor entry a bad number, please try again")
        floor_entry.delete(0, tk.END)


def max_f():    #отвечает за ввод максимального этажа
    global max_floor
    try:
        value = int(floor_entry.get())
        if value == 1:
            instruction_lbl.config(text="Why do you need an elevator in a one-story building?")
            floor_entry.delete(0, tk.END)
        elif value <= 0:
            instruction_lbl.config(text="enter a number greater than zero")
            floor_entry.delete(0, tk.END)
        else:
            max_floor = value
            instruction_lbl.config(text="enter the floors separated by a space")
            error_lbl.config(text="")
            button.config(command=add_floors)
            floor_entry.delete(0, tk.END)
            (threading.Thread(target=run_elevator, daemon=True)).start()
            text_elevator.insert(tk.END, f"maximum floor {max_floor}\n")
    except ValueError:
        error_lbl.config(text="an invalid number was floor_entry, enter the maximum floor agin ")
        floor_entry.delete(0, tk.END)


def update_gui_from_queue():          #очередь для синхронизации потоков. Берет значение из очерери и выводит их
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


instruction_lbl = tk.Label(left_frame, text="Enter the maximum floor", wraplength=140)
instruction_lbl.pack(pady=10)

floor_entry = tk.Entry(left_frame)
floor_entry.pack(pady=5)

button = tk.Button(left_frame, command=max_f, text="send")
button.pack(pady=10)

error_lbl = tk.Label(left_frame, text="", wraplength=140)
error_lbl.pack(pady=10)

floor_entry.bind("<Return>", lambda event: button.invoke())

current_floor, target_floors, elevator_direction, max_floor, is_waiting = 1, [], "is not moving", 0, False


update_gui_from_queue()
window.protocol("WM_DELETE_WINDOW", window.destroy)
window.mainloop()
