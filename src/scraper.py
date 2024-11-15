import re
from threading import Thread
from time import sleep


from src.crawler import Crawler
from src.dataExtractor import DataExtractor
from src.dataManager import DataManager


class HLTVScraper:
    def __init__(self):
        self.crawler = Crawler("https://hltv.org")
        self.stop = False
        self.data_extractor = DataExtractor()
        self.data_manager = DataManager()
        self.wait_time = 15.0
    
    def run(self):
        # Configurando execução periódica do crawler
        crawler_thread = Thread(target=self.crawlerRun, daemon=True)
        crawler_thread.start()

        # 1. Extrair as URLs dos primeiros 100 times
        ## Adiciona a url a fila de requisições
        self.crawler.addToQueue("/ranking/teams")

        ## Espera pela resposta
        response = None
        while not response:
            response = self.crawler.getResponse("/ranking/teams")
        
        ## Extrai as urls dos times
        urls = self.data_extractor.extractTeamsFromRanking(response)

        for url in urls:
            self.crawler.addToQueue(url)

        # 2. Acessar cada URL e extrair: Nome do time, jogadores, técnico, posição no ranking
        for url in urls:
            response = None
            while not response:
                response = self.crawler.getResponse(url)
            
            team_id = re.search(r"\d+", url).group(0)
            name, players, rank, coach = self.data_extractor.extractTeamInfo(response)
            self.data_manager.addNewTeam(team_id, name, players, rank, coach)
            self.data_manager.exportJson()
        
        # 3. Acessar a página de resultado de cada time, filtrando pelos últimos 3 meses, e extrair a URL de todas as partidas

        # 4. Acessar cada partida e extrair os vetos
        
        self.stop = True
    
    def crawlerRun(self):
        while not self.stop:
            self.crawler.requestPage()
            sleep(self.wait_time)


    
