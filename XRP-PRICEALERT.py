import time
import requests
import pygame
import tkinter as tk
from tkinter import Label, Button, Scale, HORIZONTAL, filedialog, StringVar, OptionMenu, Toplevel
import threading
from PIL import Image, ImageTk
from bs4 import BeautifulSoup
import json
import os

# Config file path
CONFIG_FILE = "xrp_price_alert_config.json"

# Load settings from file
def load_settings():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"threshold": 0.10, "song_path": None, "background_path": None}

# Save settings to file
def save_settings():
    with open(CONFIG_FILE, "w") as f:
        json.dump({"threshold": threshold, "song_path": song_path, "background_path": background_path}, f, indent=4)

# Load initial settings
settings = load_settings()
threshold = settings.get("threshold", 0.10)
song_path = settings.get("song_path", None)
background_path = settings.get("background_path", None)

# Set background image if available
def set_background():
    global background_path
    if not background_path:
        return  # Do nothing if no background is set
    try:
        bg_image = Image.open(background_path)
        bg_image = bg_image.resize((400, 350), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label.config(image=bg_photo)
        bg_label.image = bg_photo
    except Exception as e:
        print(f"Error loading background image: {e}")

# Ensure background is loaded at startup
root = tk.Tk()
root.title("XRP Price Monitor")
root.geometry("400x400")
bg_label = Label(root)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
if background_path:
    set_background()

def get_xrp_price():
    try:
        url = "https://www.google.com/finance/quote/XRP-USD"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        price_element = soup.find("div", class_="YMlKec fxKbKc")
        if price_element:
            return float(price_element.text.replace("$", "").replace(",", ""))
    except Exception as e:
        print(f"Error fetching price: {e}")
    return None

def set_volume(val):
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(val / 100)

def play_song():
    global song_stopped
    song_stopped = False
    if song_path:
        pygame.mixer.init()
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(volume_slider.get() / 100)
        if not song_stopped:
            pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    else:
        status_label.config(text="No song selected!")

def stop_song():
    global song_stopped
    song_stopped = True
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        status_label.config(text="Song stopped!")

def update_price():
    global song_stopped
    song_stopped = False
    global last_price
    if 'last_price' not in globals():
        last_price = None
    price = get_xrp_price()
    if price is not None:
        price_label.config(text=f"Current XRP Price: ${price:,.4f}")
        if last_price is not None and abs(price - last_price) >= threshold:
            status_label.config(text=f"XRP price changed! Playing song... Monitoring at ${threshold:.4f}")
            threading.Thread(target=play_song, daemon=True).start()
        else:
            status_label.config(text=f"Monitoring price... Alert at ${threshold:.4f}")
        last_price = price
    root.after(30000, update_price)

def manual_play():
    status_label.config(text="Manual play triggered!")
    threading.Thread(target=play_song, daemon=True).start()

def select_song():
    global song_path
    song_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if song_path:
        save_settings()

def select_background():
    global background_path
    background_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if background_path:
        save_settings()
        set_background()

def update_threshold(value):
    global threshold
    threshold = float(value)
    status_label.config(text=f"Monitoring price... Alert at ${threshold:.4f}")
    save_settings()

def open_settings():
    global settings_window
    if 'settings_window' in globals() and settings_window.winfo_exists():
        settings_window.lift()
        settings_window.focus_force()
        return
    settings_window = Toplevel(root)
    settings_window.grab_set()
    settings_window.transient(root)
    settings_window.title("Global Options")
    settings_window.geometry("300x250")
    Label(settings_window, text="Global Options", font=("Arial", 12, "bold")).pack(pady=5)
    Button(settings_window, text="Select MP3 File", command=select_song).pack(pady=5)
    Button(settings_window, text="Select Background Image", command=select_background).pack(pady=5)
    threshold_var = StringVar(settings_window)
    threshold_var.set(str(threshold))
    OptionMenu(settings_window, threshold_var, "0.001", "0.01", "0.10", "1.00", "10.00", command=update_threshold).pack(pady=5)
    Label(settings_window, text="Select alert threshold (in USD)", font=("Arial", 10)).pack()

price_label = Label(root, text="Fetching price...", font=("Arial", 14))
price_label.pack(pady=10)
status_label = Label(root, text="Monitoring price...", font=("Arial", 12))
status_label.pack(pady=10)
Button(root, text="Play Song", command=manual_play).pack(pady=5)
Button(root, text="Stop Song", command=stop_song).pack(pady=5)
volume_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Volume", command=lambda val: set_volume(float(val)))
volume_slider.set(50)
volume_slider.pack(pady=5)
Button(root, text="Global Options", command=open_settings).pack(pady=10)
update_price()
root.mainloop()
