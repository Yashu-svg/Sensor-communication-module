import tkinter as tk
from tkinter import messagebox, scrolledtext
import serial
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Arduino Config ---
ARDUINO_PORT = "COM3"   # Change this to your port (e.g., "COM4" or "/dev/ttyACM0")
BAUD_RATE = 9600

# --- Global Variables ---
running = False
data = []
timestamps = []
arduino = None

# --- Functions ---
def connect_arduino():
    """Try connecting to Arduino."""
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # wait for Arduino reset
        return ser
    except Exception as e:
        messagebox.showerror("Connection Error", f"Could not connect to Arduino:\n{e}")
        return None

def read_data():
    """Continuously read distance data and update GUI."""
    global running, data, timestamps
    start_time = time.time()
    while running:
        try:
            if arduino and arduino.in_waiting > 0:
                line = arduino.readline().decode().strip()
                if line:
                    distance = float(line)
                    current_time = time.time() - start_time
                    data.append(distance)
                    timestamps.append(current_time)
                    update_display(distance)
                    update_graph()
                    update_serial_monitor(line)
        except Exception as e:
            update_serial_monitor(f"Error: {e}")
        time.sleep(0.1)

def start_reading():
    """Start background thread."""
    global running, arduino
    if not running:
        arduino = connect_arduino()
        if not arduino:
            return
        running = True
        thread = threading.Thread(target=read_data, daemon=True)
        thread.start()
        update_serial_monitor("Started reading from Arduino...\n")

def stop_reading():
    """Stop reading data."""
    global running
    running = False
    update_serial_monitor("Stopped reading.\n")

def update_display(distance):
    """Update the distance label."""
    distance_label.config(text=f"Distance: {distance:.2f} cm")

def update_graph():
    """Update live graph."""
    ax.clear()
    ax.plot(timestamps, data, color="blue", linewidth=1.5)
    ax.set_title("Distance vs Time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Distance (cm)")
    ax.grid(True)
    canvas.draw()

def update_serial_monitor(text):
    """Display data in text box like Serial Monitor."""
    serial_output.insert(tk.END, f"{text}\n")
    serial_output.yview(tk.END)  # auto scroll

def clear_graph():
    """Clear stored data and reset graph."""
    data.clear()
    timestamps.clear()
    ax.clear()
    ax.set_title("Distance vs Time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Distance (cm)")
    canvas.draw()
    update_serial_monitor("Graph cleared.\n")

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("HC-SR04 Distance Sensor GUI")
root.geometry("800x600")

title_label = tk.Label(root, text="HC-SR04 Ultrasonic Sensor", font=("Arial", 16))
title_label.pack(pady=10)

distance_label = tk.Label(root, text="Distance: -- cm", font=("Arial", 18), fg="blue")
distance_label.pack(pady=5)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_btn = tk.Button(button_frame, text="Start Reading", font=("Arial", 12), command=start_reading, bg="green", fg="white", width=12)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(button_frame, text="Stop Reading", font=("Arial", 12), command=stop_reading, bg="red", fg="white", width=12)
stop_btn.grid(row=0, column=1, padx=10)

clear_btn = tk.Button(button_frame, text="Clear Graph", font=("Arial", 12), command=clear_graph, bg="gray", fg="white", width=12)
clear_btn.grid(row=0, column=2, padx=10)

# Graph
fig, ax = plt.subplots(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10)

# Serial monitor-like text area
serial_label = tk.Label(root, text="Serial Monitor Output:", font=("Arial", 12))
serial_label.pack()

serial_output = scrolledtext.ScrolledText(root, width=90, height=10, font=("Consolas", 10))
serial_output.pack(pady=5)

root.mainloop()
