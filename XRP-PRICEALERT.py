import time
import requests
import pygame
import tkinter as tk
from tkinter import Label, Button, Scale, HORIZONTAL, filedialog, StringVar, OptionMenu
import threading

# Set the API endpoint for XRP price
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd"

# Set initial price
last_price = None
threshold = 0.10  # Default threshold
song_path = None  # Default song file path

def get_xrp_price():
    try:
        response = requests.get(API_URL)
        data = response.json()
        return data["ripple"]["usd"]
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def play_song():
    if song_path:
        pygame.mixer.init()
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(volume_slider.get() / 100)
        pygame.mixer.music.play()
    else:
        status_label.config(text="No song selected!")

def stop_song():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        status_label.config(text="Song stopped!")

def update_price():
    global last_price
    price = get_xrp_price()
    if price is not None:
        price_label.config(text=f"Current XRP Price: ${price:.2f}")
        if last_price is not None and price >= last_price + threshold:
            status_label.config(text="XRP price increased! Playing song...")
            threading.Thread(target=play_song, daemon=True).start()
        else:
            status_label.config(text="Monitoring price...")
        last_price = price
    root.after(30000, update_price)  # Check every 30 seconds

def manual_play():
    status_label.config(text="Manual play triggered!")
    threading.Thread(target=play_song, daemon=True).start()

def select_song():
    global song_path
    song_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if song_path:
        song_label.config(text=f"Selected: {song_path.split('/')[-1]}")

def update_volume(val):
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(float(val) / 100)

def update_threshold(value):
    global threshold
    threshold = float(value)

# GUI setup
root = tk.Tk()
root.title("XRP Price Monitor")
root.geometry("400x350")

price_label = Label(root, text="Fetching price...", font=("Arial", 14))
price_label.pack(pady=10)

status_label = Label(root, text="Monitoring price...", font=("Arial", 12))
status_label.pack(pady=10)

play_button = Button(root, text="Play Song", command=manual_play)
play_button.pack(pady=5)

stop_button = Button(root, text="Stop Song", command=stop_song)
stop_button.pack(pady=5)

volume_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Volume", command=update_volume)
volume_slider.set(50)
volume_slider.pack(pady=5)

song_button = Button(root, text="Select MP3 File", command=select_song)
song_button.pack(pady=5)

song_label = Label(root, text="No song selected", font=("Arial", 10))
song_label.pack(pady=5)

# Dropdown menu for selecting price change alert threshold
threshold_var = StringVar(root)
threshold_var.set("0.10")  # Default value
threshold_options = ["0.10", "1.00", "10.00"]
threshold_menu = OptionMenu(root, threshold_var, *threshold_options, command=update_threshold)
threshold_menu.pack(pady=5)
threshold_label = Label(root, text="Select alert threshold (in USD)", font=("Arial", 10))
threshold_label.pack()

# Start price monitoring
update_price()

root.mainloop()
