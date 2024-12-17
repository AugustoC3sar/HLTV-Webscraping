import cloudscraper
from src.scheduler import Scheduler
from src.request import Request
from src.priority import Priority
from src.storage import Storage

import os
import datetime


class Downloader:
    '''
        Classe responsável por efetuar o download das páginas necessárias para extração de dados.
    '''

    def __init__(self, host):
        self.host = host
        self.scheduler = Scheduler()
        self.downloader = cloudscraper.create_scraper()
        self.storage = Storage()
        if os.path.exists(os.path.abspath("./download_log.txt")):
            with open("./download_log.txt", mode="w") as file:
                pass

    def log(self, msg:str):
        '''
            Faz o log de um download no arquivo de logs.
        '''
        with open("./download_log.txt", mode="a") as log:
            date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            log.write(f"[{date}]: {msg}\n")
    
    def addToQueue(self, url:str, priority:int):
        '''
            Adiciona a url a fila de requisições com uma certa prioridade.
        '''
        request = Request(url, Priority(priority)) 
        self.scheduler.put(request)

    def requestPage(self):
        '''
            Efetua a primeira requisição da fila de requisições.
        '''
        header = {
            "User-Agent": "*"
        }

        request = self.scheduler.get()
        response = self.downloader.get(self.host+request.getUrl(), headers=header, allow_redirects=True)
        request.addResponse(response)
        
        self.storage.put(request)

        if response.status_code < 400:
            self.log(f"{request.getUrl()} sucessfully downloaded!")
        else:
            self.log(f"{request.getUrl()} download failed with code {response.status_code}!")
    
    def getResponse(self, url):
        return self.storage.get(url).getResponse()

    