import os
import json


class DataManager:
    '''
        Classe responsável por gerenciar os dados extraídos
    '''
    def __init__(self, filename:str):
        self.data = {"teams": [], "count": 0}
        self.filename = filename
        self.__load_data()

    def __load_data(self):
        '''
            Carrega os dados atuais do Dataset, caso estejam atualizados.
        '''
        if os.path.exists(os.path.abspath(self.filename)):
            with open(self.filename, mode="r") as file:
                self.data = json.load(file)

    def datasetHasTeam(self, id):
        return id in [team["Id"] for team in self.data["teams"]]

    def addNewTeam(self, id, name, players, region, coach, rank, recent_results, maps_stats, urls):
        '''
            Adiciona um novo time na lista de times.
        '''
        team = {
            "Id": id,
            "Name": name,
            "Players": players,
            "Coach": coach,
            "Region": region,
            "Rank": rank,
            "Recent Results": recent_results,
            "Maps Stats": maps_stats,
            "URLs": urls
        }
        self.data["teams"].append(team)
        self.data["count"] += 1

        if self.data["count"]%10 == 0:
            self.save_data()
    
    def save_data(self):
        '''
            Salva os dados extraídos em um arquivo JSON.
        '''
        filename = "VLRGG_Scraping_Dataset.json"
        with open(filename, mode="w", encoding="utf-8") as output:
            json.dump(self.data, output, indent=4, ensure_ascii=False)
    