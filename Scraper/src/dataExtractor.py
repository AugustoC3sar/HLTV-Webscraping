import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class DataExtractor:
    '''
        Classe responsável pela extração de dados de páginas HTML.
    '''
    
    def getHTML(self, webpage):
        '''
            Recebe o conteúdo de uma página web e retorna o HTML manipulável via BeautifulSoup.
        '''
        return BeautifulSoup(webpage, "html.parser")

    def cleanText(self, text):
        return " ".join(text.split())

    def extractRegionalRankingsPaths(self, webpage):
        '''
            Extrai e retorna as URLs dos rankings regionais da página de rankings principal.
        '''
        html = self.getHTML(webpage)

        urls = [el["href"] for el in html.find_all("a", class_="wf-card mod-hover mod-dark mod-fullrankings")]

        return urls

    def extractTeamsFromRanking(self, webpage):
        '''
            Extrai e retorna as URLs dos 100 primeiros times listados nos rankings regionais e a região do ranking.
        '''
        urls = []

        html = self.getHTML(webpage)
        
        teams_items = html.find_all("a", class_="rank-item-team fc-flex")

        urls = [item["href"] for item in teams_items]
        urls = urls

        ranking_title = html.find("span", class_="normal", string=re.compile(r"Valorant Team Rankings:*")).text.strip()
        ranking_title = self.cleanText(ranking_title)
        region = ranking_title.split(":")[-1].strip()

        return urls, region

    def extractTeamInfo(self, webpage):
        '''
            Extrai e retorna as seguintes informações, dada a página de um time:
                - Jogadores (se houver)
                - Técnico (se houver)
                - Nome do time
        '''
        html = self.getHTML(webpage)

        # Extraindo jogadores
        players_label = html.find("div", class_="wf-module-label", string=re.compile("players"))

        players = []

        ## Caso especial: um time pode não possuir jogadores listados durante a janela de transferências
        if players_label:
            ## Extraindo divs dos jogadores
            players_div = players_label.find_next_sibling("div")
            players_items = players_div.find_all("div", class_="team-roster-item")

            ## Para cada jogador na página, extrair apelido e nome real
            for item in players_items:
                player_alias = item.find("div", class_="team-roster-item-name-alias").text
                player_alias = self.cleanText(player_alias)
                player = player_alias
                
                player_name_item = item.find("div", class_="team-roster-item-name-real")

                # Caso: um jogador pode não ter o nome real informado no site
                if player_name_item:
                    player_name = player_name_item.text
                    player_name = self.cleanText(player_name)
                    player = player_name.replace(" ", f" '{player_alias}' ")
                
                players.append(player)


        # Extraindo Head Coach
        staff_label = html.find("div", class_="wf-module-label", string=re.compile("staff"))

        coach = ""

        # Caso: um time pode não possuir nenhum membro de staff
        if staff_label:
            staff_div = staff_label.find_next_sibling("div")
            staff_items = staff_div.find_all("div", class_="team-roster-item")

            for item in staff_items:
                role_div = item.find("div", class_="team-roster-item-name-role", string=re.compile("head coach"))

                # Caso: um time pode não possuir nenhum Head Coach
                if role_div:
                    coach_div = role_div.find_parent("div", class_="team-roster-item-name")
                    coach_alias = coach_div.find("div", class_="team-roster-item-name-alias").text.strip()
                    coach_alias = self.cleanText(coach_alias)
                    coach = coach_alias

                    coach_name_item = coach_div.find("div", class_="team-roster-item-name-real")
                    if coach_name_item:
                        coach_name = coach_name_item.text
                        coach_name = self.cleanText(coach_name)
                        coach = coach_name.replace(" ", f" '{coach_alias}' ")

        # Extraindo nome do time
        name = html.find("h1", class_="wf-title").text.strip()

        return name, players, coach

    def extractTeamMatchlistPage(self, webpage):
        '''
            Extrai e retorna a URL da página de partidas, dada a página de um time.
        '''
        html = self.getHTML(webpage)

        match_div = html.find("a", class_="wf-nav-item mod-matches")
        return match_div["href"]

    def extractTeamStatsPage(self, webpage):
        '''
            Extrai e retorna a URL da página de estatísticas, dada a página de um time.
        '''
        html = self.getHTML(webpage)

        stats_div = html.find("a", class_="wf-nav-item mod-stats")
        return stats_div["href"]

    def extractTeamRecentMatchesResult(self, webpage):
        '''
            Extrai e retorna, dada a página de partidas de um time, as seguintes informações:
                - Data da partida
                - Serie, ou número de mapas jogados (se houver)
                - Oponente
                - Resultado ("win" ou "loss")
                - Mapas jogados (se houver)
                    - Cada mapa com as informações do nome do mapa e o placar do mapa.
        '''
        html = self.getHTML(webpage)

        recent_results = list()

        matches = html.find_all("a", class_="wf-card fc-flex m-item")

        for match in matches:
            # Verificando se a partida aconteceu nos últimos 6 meses
            match_date_div = match.find("div", class_="m-item-date")
            match_date = match_date_div.find("div").text.strip()
            match_date_obj = datetime.strptime(match_date, "%Y/%m/%d")

            current_date = datetime.now()
            six_months_ago = current_date - timedelta(days=6*30)

            # Caso verdadeiro
            if match_date_obj >= six_months_ago:
                # Extrai oponente
                oponent_name_div = match.find("div", class_="m-item-team text-of mod-right")
                oponent_name = oponent_name_div.find("span", class_="m-item-team-name").text.strip()

                # Extrai resultado
                result_div = match.find("div", class_="m-item-result")
                result = "loss" if "mod-loss" in result_div["class"] else "win"

                # Extrai placar
                score = result_div.text.strip()
                series = None
                maps = dict()

                ## Se a partida aconteceu
                if score != "FFL" and score != "FFW":
                    # Extrai o tipo de serie (MD1, MD3, MD5)
                    score_team_a, score_team_b = score.split(":")
                    score_team_a = int(score_team_a)
                    score_team_b = int(score_team_b)
                    maps_sum = score_team_a + score_team_b

                    series = 1
                    if maps_sum == 2:
                        series = 3
                    elif maps_sum == 3:
                        if score_team_a == 0 or score_team_b == 0:
                            series = 5
                        else:
                            series = 3
                    elif maps_sum == 4:
                        series = 5

                    # Extrai mapas jogados
                    games_div = match.parent.find("div", class_="m-item-games")
                    games = [] if games_div == None else games_div.find_all("a")
                    for game in games:
                        game_result_div = game.find("div", class_="m-item-games-result").find("div")
                        map_name = game_result_div.find("div", class_="map").text.strip()
                        map_score = game_result_div.find("div", class_="score").text.strip()
                        maps[map_name] = map_score

                match_item = {
                    "date": match_date,
                    "series": f"bo{series}" if series else "",
                    "oponent": oponent_name,
                    "result": result,
                    "maps": maps
                }

                recent_results.append(match_item)

        return recent_results

    def extractTeamMapsStats(self, webpage):
        '''
            Extrai e retorna, dada uma página de estatísticas de uma time, as seguintes informações:
                - Nome do mapa
                - Porcentagem de vitórias
                - Porcentagem de rounds vencidos no lado ATAQUE
                - Porcentagem de rounds vencidos no lado DEFESA
        '''
        html = self.getHTML(webpage)

        # Encontrando a tabela
        table = html.find("table", class_="wf-table mod-team-maps")

        # Lista para armazenar as estatísticas dos mapas
        maps_stats = []

        # Para cada linha no corpo da tabela
        for row in table.find("tbody").find_all("tr"):
            # Ignorar linhas com a classe "mod-toggle"
            if "mod-toggle" in row.get("class", []):
                continue
            
            # Extrair o nome do mapa
            map_cell = row.select("td:nth-child(1)")[0]
            if map_cell:
                map_name = map_cell.text
                map_name = map_name.split("(")[0]
                map_name = map_name.strip()
                
            # Extrair WIN%, ATK RWIN%, DEF RWIN%
            win_percent = row.select("td:nth-child(3)")[0].text.strip()
            win_percent = win_percent.strip()
            atk_rwin_percent = row.select("td:nth-child(8)")[0].text.strip()
            atk_rwin_percent = atk_rwin_percent.strip()
            def_rwin_percent = row.select("td:nth-child(11)")[0].text.strip()
            def_rwin_percent = def_rwin_percent.strip()
            
            # Adicionar os dados à lista
            maps_stats.append({
                "Map": map_name,
                "WIN%": win_percent,
                "ATK RWIN%": atk_rwin_percent,
                "DEF RWIN%": def_rwin_percent,
            })

        return maps_stats
