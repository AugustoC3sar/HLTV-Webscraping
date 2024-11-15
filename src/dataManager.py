import json
import datetime

class DataManager:
    def __init__(self):
        self.data = {"teams": [], "count": 0}

    def addNewTeam(self, id, name, players, rank, coach):
        team = {
            "Id": id,
            "Name": name,
            "Players": players,
            "Coach": coach,
            "HLTV Rank": rank,
        }
        self.data["teams"].append(team)
        self.data["count"] += 1
    
    def exportJson(self):
        data = json.dumps(self.data)

        date = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        filename = f"HTLV_Scraping_{date}.json"
        with open(filename, mode="w", encoding="utf-8") as output:
            output.write(data)
    