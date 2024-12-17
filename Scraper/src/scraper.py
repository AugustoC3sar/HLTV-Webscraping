import re
import os
import datetime
from threading import Thread
from time import sleep

from src.downloader import Downloader
from src.dataExtractor import DataExtractor
from src.dataManager import DataManager

class VLRGGScraper:
    '''
        Classe que implementa um WebScraper para o site vlr.gg.

        Deve extrair, para os primeiros 100 times de cada ranking por região:
            - Nome do Time
            - Id do time
            - Rank do time
            - Jogadores (se houver)
            - Técnico (se houver)
            - Resultados recentes, considerando partidas nos últimos 6 meses (resultado, placar geral (se houver), mapas jogados, placar por mapa)
            - Estatísticas por mapa (porcetagem de vitórias, porcentagem de rounds vencidos do lado ATAQUE, porcentagem de rounds vencidos do lado DEFESA)
    '''

    host = "https://vlr.gg"

    def __init__(self, filename):
        self.downloader = Downloader(self.host)
        self.stop = False
        self.data_extractor = DataExtractor()
        self.data_manager = DataManager(filename)
        self.wait_time = 10
        now = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%s")
        self.log_file = f"scraper_log_{now}"
    
    def log(self, msg):
        with open(self.log_file, mode="a") as file:
            file.write(f"{msg}\n")
        print(f"{msg}")

    def getResponse(self, url:str):
        '''
            Obtém a resposta da requisição realizada para uma dada URL.

            Retorna o conteúdo (HTML) da resposta, se o status da resposta for OK.
        '''
        response = None
        while not response:
            response = self.downloader.getResponse(url)
        
        if response.status_code != 200:
            return None
        
        return response.content

    def run(self):
        '''
            Inicializa o WebScraper, configurando uma Thread dedicada para o crawler e
            efetuando o loop de execução para cada ranking.
        '''
        # Configurando thread crawler
        for _ in range(5):
            crawler_thread = Thread(target=self.downloaderRun, daemon=True)
            crawler_thread.start()

        # 1. Extraindo a lista de rankings por região
        self.downloader.addToQueue("/rankings", 1)

        ## Obtém a resposta da requisição
        response = self.getResponse("/rankings")
        if not response:
            self.log("Invalid response for URL '/rankings'! (ABORTING)")
            return -1

        ## O método retorna uma lista com a url de todos os rankings por região
        self.log("Extracting Regional Rankings URLs...")
        try:
            rankings = self.data_extractor.extractRegionalRankingsPaths(response)
        except Exception as e:
            self.log(f"Regional Rankings URLs extraction FAILED with error {e}! (ABORTING)")
            return -1

        #rankings = ["/rankings/brazil"]

        # 2. Adicionando o link dos rankings na fila de requisições
        self.log("Adding rankings URLs to queue...")
        for ranking in rankings:
            self.downloader.addToQueue(ranking, 1)

        # 3. Para cada ranking, executa o loop
        for ranking in rankings:
            self.log("="*70)
            self.log(f"Starting ranking '{ranking}' data extraction...")

            code = self.mainloop(ranking)
            if code == -1:
                self.log(f"Data extraction for ranking '{ranking}' finished with errors!")
                continue

            self.log(f"Data extraction for ranking '{ranking}' successfully finished!")
        self.log("="*70)
        
        self.data_manager.save_data()
        self.stop = True

        return 0

    def mainloop(self, ranking):
        '''
            Método principal do sistema.

            Para cada ranking:
                - Extrai os times e a região do ranking
                - Para todos os times do ranking
                    - Extrai as informações citadas na descrição da classe
        '''
        return_code = 0

        # 1. Espera pela resposta da requisição ao ranking
        response = self.getResponse(ranking)
        if not response:
            self.log(f"Invalid response for URL '{ranking}'! (SKIPPING RANKING)")
            return -1
        
        # 2. Extrai as URLs dos times
        self.log(f"Extracting Teams URLs from ranking '{ranking}'...")
        try:
            urls, region = self.data_extractor.extractTeamsFromRanking(response)
        except Exception as e:
            self.log(f"Teams URLs extraction from ranking '{ranking}' FAILED with error {e}! (SKIPPING RANKING)")
            return -1

        # 3. Adiciona as URLs na fila de requisições
        for url in urls:
            self.downloader.addToQueue(url, 2)

        # 4. Para cada URL (time) no ranking
        rank = 0

        for url in urls:
            team_ulrs = [self.host+ranking, self.host+url]
            rank += 1

            self.log("-"*70)
            self.log(f"Starting team '{url}' data extraction...")

            # 4.1 Espera pela resposta da requisição da página do time
            response = self.getResponse(url)
            if not response:
                self.log(f"Invalid response for URL '{url}'! (SKIPPING TEAM)")
                return_code = -1
                continue

            # 4.2 Extrai o ID do time da URL
            team_id = re.search(r"\d+", url).group(0)
            if self.data_manager.datasetHasTeam(team_id):
                self.log(f"Team '{team_id}' already on the dataset! (SKIPPING TEAM)")
                continue

            # 4.3 Extrai nome, jogadores e head coach do time
            self.log(f"Extracting team '{url}' info...")
            try:
                name, players, coach = self.data_extractor.extractTeamInfo(response)
            except Exception as e:
                self.log(f"Team '{url}' info extraction FAILED with error {e}! (SKIPPING TEAM)")
                return_code = -1
                continue

            # 4.4 Extrai a URL para a página com a lista de partidas do time e adiciona na fila de requisições
            self.log(f"Extracting team '{url}' matchlist page URL...")
            try:
                matchlist_page = self.data_extractor.extractTeamMatchlistPage(response)
            except Exception as e:
                self.log(f"Team '{url}' matchlist page URL extraction FAILED with error {e}! (SKIPPING TEAM)")
                return_code = -1
                continue
            self.downloader.addToQueue(matchlist_page, 3)

            # 4.5 Extrai a URL para a página de estatísticas do time e adiciona na fila de requisições
            self.log(f"Extracting team '{url}' statistics page URL...")
            try:
                stats_page = self.data_extractor.extractTeamStatsPage(response)
            except Exception as e:
                self.log(f"Team '{url}' statistics page URL extraction FAILED with error {e}! (SKIPPING TEAM)")
                return_code = -1
                continue
            self.downloader.addToQueue(stats_page, 3)

            # 4.6 Espera pela resposta da requisição da página de lista de partidas do time
            response = self.getResponse(matchlist_page)
            if not response:
                self.log(f"Invalid response for URL '{matchlist_page}'! (SKIPPING TEAM)")
                return_code = -1
                continue
            team_ulrs.append(self.host+matchlist_page)
            
            # 4.7 Extrai os resultados recentes do time
            self.log(f"Extracting team '{url}' recent matches results...")
            try:
                recent_results = self.data_extractor.extractTeamRecentMatchesResult(response)
            except Exception as e:
                self.log(f"Team '{url}' recent matches results extracion FAILED with error {e}! (SKIPPING TEAM)")
                return_code = -1
                continue

            # 4.8 Espera pela resposta da requisição da página de estatísticas do time
            response = self.getResponse(stats_page)
            if not response:
                self.log(f"Invalid response for URL '{stats_page}'! (SKIPPING TEAM)")
                return_code = -1
                continue
            team_ulrs.append(self.host+stats_page)

            # 4.9 Extrai as estatísticas de mapas do time
            self.log(f"Extracting team '{url}' maps statistics...")
            try:
                maps_stats = self.data_extractor.extractTeamMapsStats(response)
            except Exception as e:
                self.log(f"Team '{url}' maps statistics extraction FAILED with error {e}! (SKIPPING TEAM)")
                return_code = -1
                continue

            # 4.10 Salva o time na na lista de times
            self.data_manager.addNewTeam(team_id, name, players, region, coach, rank, recent_results, maps_stats, team_ulrs[:])
            self.log(f"Team '{name}' added to dataset!")

        self.log("-"*70)

        return return_code
                
    def downloaderRun(self):
        '''
            Método executado pela thread dedicada do crawler.

            Chama o método que efetua o download de uma página do crawler e
            espera por um tempo predefinido antes de efetuar um novo download.
        '''
        while not self.stop:
            self.downloader.requestPage()
            sleep(self.wait_time)


    
