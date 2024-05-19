import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import configparser
import webbrowser

stop_download = False

def exitProgram():
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        root.destroy()

def log_message(message, color=None):
    log_text.config(state=tk.NORMAL)
    if color:
        log_text.insert(tk.END, message + "\n", color)
        log_text.tag_configure(color, foreground=color)
    else:
        log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)
    log_text.config(state=tk.DISABLED)

def downloadVideo(link, id):
    global stop_download
    if stop_download:
        return
    log_message(f"Downloading video {id} from: {link}", "cyan")

    cookies = {
      # read the README file to understand how to get the cookies
    }

    headers = {
      # read the README file to understand how to get the headers
    }

    params = {
        # read the README file to understand how to get the params
    }

    data = {
        'id': link, # Keep this as it is
        #read the README file to understand how to get the data
    }

    log_message("Getting the download link", "cyan")
    response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
    downloadSoup = BeautifulSoup(response.text, "html.parser")

    downloadLink = downloadSoup.a["href"]
    videoTitle = downloadSoup.p.getText().strip()

    log_message("Saving the video in the folder", "cyan")
    mp4File = urlopen(downloadLink)
    video_directory = "video"
    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    # Save the video file
    with open(f"{video_directory}/{id}.mp4", "wb") as output:
        while True:
            data = mp4File.read(4096)
            if data:
                output.write(data)
            else:
                break

    log_message(f"Video {id} downloaded successfully", "green")

def startDownload():
    global stop_download
    stop_download = False
    channel_link = entry_channel_link.get()
    class_name = entry_class_name.get()
    num_videos = entry_num_videos.get()
    if not num_videos:
        log_message("Number of Videos can't be null", "red")
        return

    if num_videos.upper() == 'ALL':
        log_message("Downloading all found videos...", "green")
        return

    try:
        num_videos = int(num_videos)
        if num_videos <= 0:
            raise ValueError
    except ValueError:
        log_message("Number of Videos must be a positive number ", "red")
        return


    def download_thread():
        log_message("Opening the Chrome browser", "cyan")
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        driver = webdriver.Chrome(options=options)
        driver.get(channel_link)

        remaining_time = 30

        while remaining_time > 0:
            log_message(f"Waiting for {remaining_time} seconds...", "cyan")
            time.sleep(1)
            remaining_time -= 1

        scroll_pause_time = 1
        screen_height = driver.execute_script("return window.screen.height;")
        i = 1

        log_message("Scrolling page to get all the videos...", "cyan")

        while True:
            if stop_download:
                driver.quit()
                return
            driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
            i += 1
            time.sleep(scroll_pause_time)
            scroll_height = driver.execute_script("return document.body.scrollHeight;")
            if (screen_height) * i > scroll_height:
                break

        script = "let l = [];"
        script += "Array.from(document.getElementsByClassName(\""
        script += class_name
        script += "\")).forEach(item => { l.push(item.querySelector('a').href)});"
        script += "return l;"

        urlsToDownload = driver.execute_script(script)

        log_message(f"{len(urlsToDownload)} Videos found", "green")
        for index, url in enumerate(urlsToDownload):
            if stop_download or index >= num_videos:
                break
            log_message(f"Downloading video: {index + 1}/{num_videos}", "cyan")
            downloadVideo(url, index)
            time.sleep(10)

        driver.quit()

    thread = threading.Thread(target=download_thread)
    thread.start()

def stopDownload():
    global stop_download
    stop_download = True
    log_message("Download stopped", "red")

def saveConfig():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'channel_link': entry_channel_link.get(),
        'class_name': entry_class_name.get()
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    messagebox.showinfo("Info", "Configuration saved successfully!")

def loadConfig():
    config = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
        entry_channel_link.insert(0, config['DEFAULT'].get('channel_link', ''))
        entry_class_name.insert(0, config['DEFAULT'].get('class_name', ''))

def open_github_link(event):
    webbrowser.open_new("https://github.com/pavel-filchi/Auto-TikTok-Downloader")


root = tk.Tk()
root.title("TikTok Video Downloader")
root.geometry("700x500")

icon_path = 'logo.png'
if os.path.exists(icon_path):
    root.iconphoto(False, tk.PhotoImage(file=icon_path))

style = ttk.Style(root)
style.theme_use('clam')

style.configure('TFrame', background='black')
style.configure('TLabel', background='black', foreground='white')
style.configure('TEntry', fieldbackground='black', foreground='white')
style.configure('TButton', background='black', foreground='white')

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(1, weight=1)
mainframe.rowconfigure(3, weight=1)

ttk.Label(mainframe, text="Channel Link:").grid(row=0, column=0, sticky=tk.W, pady=5)
entry_channel_link = ttk.Entry(mainframe, width=50)
entry_channel_link.grid(row=0, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))

ttk.Label(mainframe, text="Class Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
entry_class_name = ttk.Entry(mainframe, width=50)
entry_class_name.grid(row=1, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))

ttk.Label(mainframe, text="Number of Videos:").grid(row=2, column=0, sticky=tk.W, pady=5)
entry_num_videos = ttk.Entry(mainframe, width=50)
entry_num_videos.grid(row=2, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))

log_frame = ttk.Frame(mainframe)
log_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
log_frame.columnconfigure(0, weight=1)
log_frame.rowconfigure(0, weight=1)

log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80, state=tk.DISABLED, wrap=tk.WORD, background='black', foreground='white')
log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

button_frame = ttk.Frame(mainframe)
button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

button_download = ttk.Button(button_frame, text="Download", command=startDownload)
button_download.grid(row=0, column=0, padx=10)

button_stop = ttk.Button(button_frame, text="Stop", command=stopDownload)
button_stop.grid(row=0, column=1, padx=10)

button_save = ttk.Button(button_frame, text="Save Config", command=saveConfig)
button_save.grid(row=0, column=2, padx=10)

button_exit = ttk.Button(button_frame, text="Exit", command=exitProgram)
button_exit.grid(row=0, column=3, padx=10)

github_label = ttk.Label(button_frame, text="GitHub Project", foreground="cyan", cursor="hand2", background='black')
github_label.grid(row=0, column=4, padx=10)
github_label.bind("<Button-1>", open_github_link)

loadConfig()
root.mainloop()