import cloudscraper
from queue import Queue
import datetime

from util.waitableDict import WaitableDict


class Crawler:
    def __init__(self, host):
        self.host = host
        self.scheduler = Queue()
        self.downloader = cloudscraper.create_scraper()
        self.storage = WaitableDict()
        self.last_request_time = 0

    def log(self, msg):
        with open("./log.txt", mode="a") as log:
            date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            log.write(f"[{date}]: {msg}\n")

    def addToQueue(self, url):
        self.scheduler.put(url)
    
    def requestPage(self):
        header = {
            "User-Agent": "*"
        }

        url = self.scheduler.get()
        response = self.downloader.get(self.host+url, headers=header, allow_redirects=True)
        self.storage.put(url, response.content)
        
        self.log(f"{url} successfully downloaded!")
    
    def getResponse(self, url):
        return self.storage.get(url)

    