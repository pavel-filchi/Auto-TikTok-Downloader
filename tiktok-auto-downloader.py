from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os

def downloadVideo(link, id):
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

    print("Getting the download link")
    response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
    downloadSoup = BeautifulSoup(response.text, "html.parser")

    downloadLink = downloadSoup.a["href"]
    videoTitle = downloadSoup.p.getText().strip()

    print("Saving the video in the folder")
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

print("Opening the Chrome browser")
options = Options()
options.add_argument("start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=options)
# Change the tiktok link to the channel you need
driver.get("https://www.tiktok.com/@example")

# Change this value if you have a Captcha (put just enough time to solve it)
time.sleep(60)

scroll_pause_time = 1
screen_height = driver.execute_script("return window.screen.height;")
i = 1

print("Scrolling page to get all the videos...")
while True:
    driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
    i += 1
    time.sleep(scroll_pause_time)
    scroll_height = driver.execute_script("return document.body.scrollHeight;")  
    if (screen_height) * i > scroll_height:
        break 

#read the README file to understand how to get the className
className = "css-example-example example"

script  = "let l = [];"
script += "document.getElementsByClassName(\""
script += className
script += "\").forEach(item => { l.push(item.querySelector('a').href)});"
script += "return l;"

urlsToDownload = driver.execute_script(script)

print(f" {len(urlsToDownload)} Videos found")
for index, url in enumerate(urlsToDownload):
    print(f"Downloading video: {index}")
    downloadVideo(url, index)
    time.sleep(10)
