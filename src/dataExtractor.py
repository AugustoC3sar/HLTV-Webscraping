from bs4 import BeautifulSoup


class DataExtractor:
    
    def getHTML(self, webpage):
        return BeautifulSoup(webpage, "html.parser")

    def extractTeamsFromRanking(self, webpage):
        urls = []

        html = self.getHTML(webpage)
        
        elements = html.find_all(lambda tag: tag.name == "a" and tag.text == "HLTV Team profile")
        elements = elements[:100]

        for element in elements:
            urls.append(element["href"])

        return urls

    def extractTeamInfo(self, webpage):
        html = self.getHTML(webpage)

        name = html.find(class_="profile-team-name").text
        players = [player.text for player in html.find_all(class_="playerFlagName")]
        rank = ""
        coach = ""

        stats_divs = html.find_all("div", class_="profile-team-stat")
        for div in stats_divs:
            label = div.find("b")
            if label:
                if label.text == "World ranking":
                    rank_span = div.find("span", class_="right")
                    if rank_span:
                        rank = rank_span.text
                if label.text == "Coach":
                    coach_span = div.find("a", class_="right")
                    if coach_span:
                        coach = coach_span.text

        return name, players, rank, coach