import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import tkinter as tk
from tkinter import messagebox
import configparser

stop_download = False  # Global variable to control the stopping of the download process

def exitProgram():
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        root.destroy()
def log_message(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

def downloadVideo(link, id):
    global stop_download
    if stop_download:
        return
    print(f"Downloading video {id} from: {link}")
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

    log_message("Getting the download link")
    response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
    downloadSoup = BeautifulSoup(response.text, "html.parser")

    downloadLink = downloadSoup.a["href"]
    videoTitle = downloadSoup.p.getText().strip()

    log_message("Saving the video in the folder")
    mp4File = urlopen(downloadLink)
    # Check if the directory exists, if not, create it
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


# Function to start the download process
def startDownload():
    global stop_download
    stop_download = False  # Reset stop_download flag at the beginning of the download
    channel_link = entry_channel_link.get()
    class_name = entry_class_name.get()

    def download_thread():
        log_message("Opening the Chrome browser")
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        driver = webdriver.Chrome(options=options)
        driver.get(channel_link)

        remaining_time = 30

        while remaining_time > 0:
            log_message(f"Waiting for {remaining_time} seconds...")
            time.sleep(1)
            remaining_time -= 1

        scroll_pause_time = 1
        screen_height = driver.execute_script("return window.screen.height;")
        i = 1

        log_message("Scrolling page to get all the videos...")

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

        log_message(f" {len(urlsToDownload)} Videos found")
        for index, url in enumerate(urlsToDownload):
            if stop_download:
                break
            log_message(f"Downloading video: {index}")
            downloadVideo(url, index)
            time.sleep(10)

        driver.quit()

    thread = threading.Thread(target=download_thread)
    thread.start()


def stopDownload():
    global stop_download
    stop_download = True
    log_message("Download stopped")


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


root = tk.Tk()
root.title("TikTok Video Downloader")

tk.Label(root, text="Channel Link:").grid(row=0, column=0, sticky=tk.W)
entry_channel_link = tk.Entry(root, width=50)
entry_channel_link.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Class Name:").grid(row=1, column=0, sticky=tk.W)
entry_class_name = tk.Entry(root, width=50)
entry_class_name.grid(row=1, column=1, padx=10, pady=5)

log_text = tk.Text(root, height=20, width=80)
log_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
log_text.tag_configure("red", foreground="red")

button_exit = tk.Button(root, text="Exit", command=exitProgram)
button_exit.grid(row=6, column=3, padx=10, pady=10, sticky=tk.W)

button_download = tk.Button(root, text="Download", command=startDownload)
button_download.grid(row=6, column=1, padx=10, pady=10, sticky=tk.E)

button_stop = tk.Button(root, text="Stop", command=stopDownload)
button_stop.grid(row=6, column=2, padx=10, pady=10, sticky=tk.E)

button_save = tk.Button(root, text="Save Config", command=saveConfig)
button_save.grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)

loadConfig()
root.mainloop()