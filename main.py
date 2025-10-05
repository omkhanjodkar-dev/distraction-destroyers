from operator import is_
import os
import time
import string
from datetime import datetime
import json
import subprocess

# os.system("pip install pywin32 pyautogui pywinauto keyboard transformers torch yt-dlp requests beautifulsoup4 pygame")

# import pyautogui
# from pywinauto import Desktop
# import keyboard
# from transformers import pipeline
# import sys
# import argparse
# import requests
# from bs4 import BeautifulSoup
# import urllib.parse
# import re

import json
import tkinter as tk
from tkinter import ttk
import time
import random
import os
import pygame
import shutil
from tkinter import filedialog, messagebox




# os.environ["CUDA_VISIBLE_DEVICES"] = "1"
# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)
# hashmap = {}

def get_current_datetime():
    return datetime.now().strftime("%d/%m/%y %H:%M:%S")



def install_music_files():
    target_dir = filedialog.askdirectory(title="Select Folder to Install Music")
    if not target_dir:
        return

    source_dir = "assets/music"
    files = [f for f in os.listdir(source_dir) if f.endswith(".mp3")]

    try:
        for file in files:
            src = os.path.join(source_dir, file)
            dst = os.path.join(target_dir, file)
            shutil.copy2(src, dst)
        messagebox.showinfo("Success", f"Installed {len(files)} music files to:\n{target_dir}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install music files:\n{e}")



def count_distractions_today():
    json_path = 'distractionHistory.json'
    with open(json_path, "r") as f:
        data = json.load(f)

    today = datetime.now().strftime("%d/%m/%y")
    distractions = data.get("Distractions", [])
    
    count = sum(1 for _, timestamp in distractions if timestamp.startswith(today))
    return count

def total_session_time_today():
    json_path = 'userSessions.json'
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    today = datetime.now().strftime("%d/%m/%y")
    sessions = data.get("Sessions", [])

    total_time = sum(duration for duration, timestamp in sessions if timestamp.startswith(today))
    return total_time




class FocusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Dashboard")
        self.root.geometry("760x480")
        self.theme = tk.StringVar(value="Dark")
        self.focus_mode = tk.BooleanVar()
        self.timer_running = False
        self.time_left = 25 * 60
        self.style = ttk.Style()

        self.bg = "#1e1e2f"
        self.fg = "#f8f8f2"
        self.accent = "#ff79c6"
        self.label = "#8be9fd"
        self.summary = "#f1fa8c"
        self.root.configure(bg=self.bg)
        self.style.theme_use("default")
        self.style.configure("TButton", font=("Helvetica", 11), padding=6)
        self.style.configure("TCheckbutton", background=self.bg, foreground=self.fg, font=("Helvetica", 11))
        self.style.configure("TMenubutton", background=self.bg, foreground=self.fg)

        self.build_ui()


    def build_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="🎯 Focus Dashboard", font=("Helvetica", 18, "bold"), bg=self.bg, fg=self.fg).pack(pady=10)
        
        tk.Label(self.root, text="⚡ Quick Actions", font=("Helvetica", 14, "bold"), bg=self.bg, fg=self.label).pack(pady=10)
        ttk.Button(self.root, text="View Distraction History", command=self.view_distractions).pack(pady=5)
        ttk.Button(self.root, text="Customize Settings", command=self.open_settings).pack(pady=5)
        ttk.Button(self.root, text="Gamification & Rewards", command=self.open_gamification).pack(pady=5)
        ttk.Button(self.root, text="Open Timer Screen", command=self.open_timer_screen).pack(pady=5)

    def switch_theme(self, *_):
        self.configure_theme()
        self.build_ui()

    def view_distractions(self):
        DistractionLogViewer(self.root)

    def open_settings(self):
        SettingsPanel(self.root)

    def open_gamification(self):
        GamificationPanel(self.root)

    def open_timer_screen(self):
        TimerScreen(tk.Toplevel(self.root))

class TimerScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Timer")
        self.root.geometry("860x650")
        self.root.configure(bg="#1e1e2f")
        with open("userData.json", 'r') as f:
            self.session_time_def = json.load(f)["Session Time"] * 60
        self.time_left = self.session_time_def
        self.timer_running = False
        self.paused = False
        self.music_on = False
        self.music_index = 0
        self.music_files = [
            "assets/music/ambient1.mp3",
            "assets/music/ambient2.mp3",
            "assets/music/ambient3.mp3",
            "assets/music/ambient4.mp3",
            "assets/music/ambient5.mp3"
        ]
        
        self.quotes = [
            "Stay focused and never give up.",
            "Small steps lead to big results.",
            "Discipline is the bridge to success.",
            "Your future is created by what you do today.",
            "Push yourself, because no one else will."
        ]
        pygame.mixer.init()
        self.build_ui()

    def build_ui(self):
        self.timer_label = tk.Label(self.root, text=self.format_time(self.time_left),
                                    font=("Helvetica", 36, "bold"), bg="#1e1e2f", fg="#ff79c6")
        self.timer_label.pack(pady=20)

        self.quote_label = tk.Label(self.root, text=random.choice(self.quotes),
                                    font=("Helvetica", 12, "italic"), wraplength=360,
                                    bg="#1e1e2f", fg="#8be9fd")
        self.quote_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, length=300, mode="determinate")
        self.progress.pack(pady=10)
        self.progress["maximum"] = self.time_left

        tk.Label(self.root, text="📊 Today's Summary", font=("Helvetica", 14, "bold"),
                 bg="#1e1e2f", fg="#8be9fd").pack(pady=10)

        summary_frame = tk.Frame(self.root, bg="#1e1e2f")
        summary_frame.pack()

        self.time_focused_label = tk.Label(summary_frame, text=f"Time Elapsed: {total_session_time_today()}",
                                           bg="#1e1e2f", fg="#f1fa8c", font=("Helvetica", 11))
        self.time_focused_label.pack(anchor="w")

        self.distractions_label = tk.Label(summary_frame, text=f"Distraction Count: {count_distractions_today()}",
                                           bg="#1e1e2f", fg="#f1fa8c", font=("Helvetica", 11))
        self.distractions_label.pack(anchor="w")

        style = ttk.Style()
        style.theme_use("default")

        style.configure("Custom.Horizontal.TScale",
            troughcolor="#44475a",     
            sliderthickness=5,        
            background="#ffb86c",      
            bordercolor="#6272a4",     
            relief="flat")

        tk.Label(self.root, text="🎵 Background Music", font=("Helvetica", 14, "bold"),
                 bg="#1e1e2f", fg="#8be9fd").pack(pady=10)

        music_frame = tk.Frame(self.root, bg="#1e1e2f")
        music_frame.pack()

        self.selected_track = tk.StringVar()
        self.selected_track.set("ambient1.mp3") 

        track_names = [f"ambient{i}.mp3" for i in range(1, 6)]
        ttk.OptionMenu(music_frame, self.selected_track, self.selected_track.get(), *track_names).grid(row=0, column=0, padx=5)

        ttk.Button(music_frame, text="Play", command=self.play_music).grid(row=0, column=1, padx=5)
        ttk.Button(music_frame, text="Pause", command=self.pause_music).grid(row=0, column=2, padx=5)
        ttk.Button(music_frame, text="Resume", command=self.resume_music).grid(row=0, column=3, padx=5)
        

        tk.Label(self.root, text="🔊 Volume", font=("Helvetica", 11), bg="#1e1e2f", fg="#8be9fd").pack(pady=(10, 0))

        volume_frame = tk.Frame(self.root, bg="#1e1e2f")
        volume_frame.pack()

        self.volume_value = tk.IntVar(value=50) 

        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=100, orient="horizontal",
                               variable=self.volume_value, command=self.set_volume,
                               style="Custom.Horizontal.TScale")

        self.volume_slider.pack(side="left", padx=5)

        self.volume_label = tk.Label(volume_frame, text="50%", font=("Helvetica", 10),
                                     bg="#1e1e2f", fg="#f1fa8c")
        self.volume_label.pack(side="left")


        btn_frame = tk.Frame(self.root, bg="#1e1e2f")
        btn_frame.pack(pady=20)
        
        self.start_but = tk.Button(btn_frame, text="Start", command=self.start_timer, font=("Helvetica", 22))
        self.start_but.grid(row=0, column=0, padx=5)

    def start_timer(self):
        if self.start_but.cget("text") == "Start":
            self.start_but.config(text = 'Stop')
            self.resume_timer()
            subprocess.Popen(["start", "cmd", "/c", f"python backend.py"], shell=True)
            try:
                with open("userData.json", "r") as f:
                    data = json.load(f)
                with open("userData.json", "w") as f:
                    data["backendActive"] = True
                    json.dump(data, f, indent=4)
            except PermissionError as e:
                time.sleep(1)
                with open("userData.json", "r") as f:
                    data = json.load(f)
                with open("userData.json", "w") as f:
                    data["backendActive"] = True
                    json.dump(data, f, indent=4)
            except OSError as e1:
                time.sleep(1)
                with open("userData.json", "r") as f:
                    data = json.load(f)
                with open("userData.json", "w") as f:
                    data["backendActive"] = True
                    json.dump(data, f, indent=4)
            except Exception as e2:
                print("Fatal Error: JSON file loading or dumping couldn't work. Rewriting the JSON file to its default.")
                with open("userData.json", 'w') as f:
                    f.dump({"backendActive" : True}, f, indent=4)
        else:
            self.start_but.config(text = 'Start')
            try:
                with open("userData.json", "r") as f:
                    data = json.load(f)
                with open("userData.json", "w") as f:
                    data["backendActive"] = False
                    json.dump(data, f, indent=4)
            except PermissionError as e:
                time.sleep(1)
                with open("userData.json", "r") as f:
                    data = json.load(f)
                with open("userData.json", "w") as f:
                    data["backendActive"] = False
                    json.dump(data, f, indent=4)
            except OSError as e1:
                time.sleep(1)
                with open("userData.json", "r") as f:
                    data = json.load(f)
                with open("userData.json", "w") as f:
                    data["backendActive"] = False
                    json.dump(data, f, indent=4)
            except Exception as e2:
                print("Fatal Error: JSON file loading or dumping couldn't work. Rewriting the JSON file to its default.")
                with open("userData.json", 'w') as f:
                    f.dump({"backendActive" : False}, f, indent=4)
            self.end_timer()

    def format_time(self, seconds):
        return f"{seconds // 60:02}:{seconds % 60:02}"

    def toggle_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running and not self.paused and self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=self.format_time(self.time_left))
            self.progress["value"] = self.session_time_def - self.time_left
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0:
            # self.timer_running = False
            self.start_but.config(text = 'Start')
            try:
                with open("userData.json", "r") as f:
                    data = json.load(f)
                with open("userData.json", "w") as f:
                    data["backendActive"] = False
                    json.dump(data, f, indent=4)
            except PermissionError as e:
                time.sleep(1)
                with open("userData.json", "r") as f:
                    data = json.load(f)
                with open("userData.json", "w") as f:
                    data["backendActive"] = False
                    json.dump(data, f, indent=4)
            except OSError as e1:
                time.sleep(1)
                with open("userData.json", "r") as f:
                    data = json.load(f)
                with open("userData.json", "w") as f:
                    data["backendActive"] = False
                    json.dump(data, f, indent=4)
            except Exception as e2:
                print("Fatal Error: JSON file loading or dumping couldn't work. Rewriting the JSON file to its default.")
                with open("userData.json", 'w') as f:
                    f.dump({"backendActive" : False}, f, indent=4)
            self.end_timer()
            self.timer_label.config(text="00:00")
            self.quote_label.config(text="Session Complete! Great job 🎉")
            # self.time_focused_label.config(text="Time Elapsed: 25 min")
            # self.distractions_label.config(text="Distraction Count: 3")

    def pause_timer(self):
        self.paused = True

    def resume_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()
        self.paused = False

    def end_timer(self):
        self.timer_running = False
        with open('userSessions.json', "r") as f:
            sesdat = json.load(f)
            sesdat['Sessions'].append([int((self.session_time_def - self.time_left)/60), get_current_datetime()])
        with open("userSessions.json", 'w') as f:
            json.dump(sesdat, f, indent=4)
        with open('userXP.json', 'r') as f:
            xpdat = json.load(f)
            xpdat["XP"] += int(int((self.session_time_def - self.time_left)/60)/6)
        with open('userXP.json', 'w') as f:
            json.dump(xpdat, f, indent=4)


        self.time_left = self.session_time_def
        self.timer_label.config(text=self.format_time(self.time_left))
        self.progress["value"] = 0
        self.quote_label.config(text=random.choice(self.quotes))
        
    def play_music(self):
        track = f"assets/music/{self.selected_track.get()}"
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(self.volume_slider.get())
            pygame.mixer.music.play(-1, fade_ms=2000) 
            self.music_on = True
        except Exception as e:
            print(f"Error playing music: {e}")

    def pause_music(self):
        if self.music_on:
            pygame.mixer.music.pause() 
            self.music_on = False

    def resume_music(self):
        try:
            pygame.mixer.music.unpause()
            self.music_on = True
        except Exception as e:
            print(f"Error resuming music: {e}")


    def set_volume(self, val):
        volume = int(float(val))
        pygame.mixer.music.set_volume(volume / 100)
        self.volume_label.config(text=f"{volume}%")

class SettingsPanel(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("🛠️ Settings")
        self.geometry("380x380")
        self.configure(bg="#1e1e2f")

        with open("userData.json", "r") as f:
            user_data = json.load(f)

        intervention_style = user_data.get("Intervention Style", "nudge")
        session_time = user_data.get("Session Time", 60)

        # style = ttk.Style(self)
        # style.configure("TLabel", background="#1e1e2f", font=("Helvetica", 10))
        # style.configure("TButton", font=("Helvetica", 10, "bold"))
        # style.configure("TCheckbutton", foreground="black", font=("Helvetica", 10))
        # style.configure("TRadiobutton", foreground='black', font=("Helvetica", 10))

        tk.Label(self, text="Customize Your Experience", font=("Helvetica", 14, "bold"), bg="#1e1e2f", fg="white").pack(pady=10)

        section = ttk.LabelFrame(self, text="Intervention Style", padding=10)
        section.pack(fill="x", padx=20, pady=10)

        self.intervention_var = tk.StringVar(value=intervention_style)
        for style_option in ["nudge", "auto-close"]:
            ttk.Radiobutton(section, text=style_option.capitalize(),
                            variable=self.intervention_var, value=style_option).pack(anchor="w")

        time_section = ttk.LabelFrame(self, text="Pomodoro Timer (minutes)", padding=10)
        time_section.pack(fill="x", padx=20, pady=10)

        self.session_time_var = tk.IntVar(value=session_time)
        ttk.Spinbox(time_section, from_=10, to=180, textvariable=self.session_time_var, width=10).pack(pady=5)

        ttk.Button(self, text="Install Default Music", command=install_music_files).pack(pady=10)
        ttk.Button(self, text="Apply Settings", command=self.apply_settings).pack(pady=20)

    def apply_settings(self):
        with open("userData.json", "r") as f:
            data = json.load(f)

        data["Intervention Style"] = self.intervention_var.get()
        data["Session Time"] = self.session_time_var.get()

        with open("userData.json", "w") as f:
            json.dump(data, f, indent=4)

        print(f"Intervention style: {data['Intervention Style']}")
        print(f"Pomodoro session time: {data['Session Time']} minutes")

        self.destroy()

class GamificationPanel(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("🎮 Gamification & Rewards")
        self.geometry("640x280")
        self.configure(bg="#1e1e2f")

        with open("userXP.json", 'r') as f:
            xp = json.load(f)["XP"]

        # style = ttk.Style(self)
        # style.configure("TLabel", font=("Helvetica", 10))
        # style.configure("TButton", font=("Helvetica", 10, "bold"))
        # style.configure("TProgressbar", thickness=20)

        tk.Label(self, text="Your Progress & Achievements", font=("Helvetica", 14, "bold"), fg='white', bg='#1e1e2f').pack(pady=10)

        xp_frame = ttk.LabelFrame(self, text="XP Progress", padding=10)
        xp_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(xp_frame, text=f"Level {int(xp/100 + 1)}", bg="#d9d9d9").pack(anchor="w")
        self.xp_bar = ttk.Progressbar(xp_frame, maximum=100, value=xp%100)
        self.xp_bar.pack(fill="x", pady=5)
        tk.Label(xp_frame, text=f"{xp%100} / 100 XP", bg = '#d9d9d9').pack(anchor="e")

        ttk.Button(self, text="Close", command=self.destroy).pack(pady=20)


class DistractionLogViewer(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("🚫 Distraction Intervention Log")
        self.geometry("640x560")
        self.configure(bg="#1e1e2f")

        with open("distractionHistory.json", "r") as f:
            data = json.load(f)
        data = data["Distractions"]
        counter = 0
        log_entries = []
        for i in data:
            log_entries.append(f'{i[1]}: {i[0]}')
            counter += 1

        print(log_entries)

        tk.Label(self, text="Distraction Report", font=("Helvetica", 14, "bold"), bg="#1e1e2f", fg="white").pack(pady=10)

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        canvas = tk.Canvas(frame, bg="#1e1e2f", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        s1 = ttk.Style()
        s1.configure('TFrame', background='#1e1e2f')
        scroll_frame = ttk.Frame(canvas, style='TFrame')
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, entry in enumerate(log_entries, start=1):
            tk.Label(scroll_frame, text=f"{i}. {entry}", wraplength=540, bg="#1e1e2f", fg="white").pack(anchor="w", pady=4)

        tk.Label(self, text="\n\nSummary", font=("Helvetica", 12, "bold"), bg="#1e1e2f", fg="white").pack(pady=10)
        summary = self.generate_summary(data)
        print(summary)
        for line in summary.split('\n'):
            tk.Label(self, text=line, wraplength=560, bg="#1e1e2f", fg="white").pack(anchor="w", padx=20)

        ttk.Button(self, text="Close", command=self.destroy).pack(pady=20)

    def generate_summary(self, entries):
        out = ''

        # total distractions detected
        out = f"Total Distractions Detected: {len(entries)}"

        # most frequent distraction
        dist_hash = {}
        for i in entries:
            if i[0] in dist_hash:
                dist_hash[i[0]] += 1
            else:
                dist_hash[i[0]] = 1
        maximum = 0
        mfd = ''
        for i in entries:
            if dist_hash[i[0]] > maximum:
                maximum = dist_hash[i[0]]
                mfd = i[0]
        out += f'\nMost Frequent Distraction: {mfd} -> {maximum} times!'

        return out




if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("460x700")
    app = FocusApp(root)
    root.mainloop()


# cux xf dpvme'wf kvtu ejsfdumz sbo uif nbjo.qz cbdlfoe qsphsbn boe vtfe uif ktpo vtfsebub gjmf up hfu tubsu tupq dpnnboet cz svoojoh ju jo b dne (opu pt.tztufn) (xifsf ju pqfot tfqbsbufmz) cvu epjoh ju vtjoh kbwb boe b qbsbmmfm uisfbe jt dppmfs tp xf eje ju uibu xbz 
# own j foefe vq opu vtjoh kbwb