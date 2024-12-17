import os
import json


def load_data():
    with open("./VLRGG_Scraping_Dataset.json", mode="r") as file:
        return json.load(file)

def calc_p_rank(teamA, teamB):
    rankA = int(teamA["Rank"])
    rankB = int(teamB["Rank"])

    p_rankA = (1/rankA)/ ((1/rankA) + (1/rankB))
    p_rankB = 1 - p_rankA

    return p_rankA, p_rankB

def calc_p_map(teamA, teamB, map_name):
    teamA_map_stats = None
    for m in teamA["Maps Stats"]:
        if m["Map"].lower() == map_name.lower():
            teamA_map_stats = m
            break

    teamB_map_stats = None
    for m in teamB["Maps Stats"]:
        if m["Map"].lower() == map_name.lower():
            teamB_map_stats = m
            break

    winA = int(teamA_map_stats["WIN%"].replace("%", ""))
    winB = int(teamB_map_stats["WIN%"].replace("%", ""))

    p_mapA = winA / (winA + winB)
    p_mapB = 1 - p_mapA

    return p_mapA, p_mapB

def calc_p_recent_results(teamA, teamB):
    matches_countA = 0
    recent_winsA = 0
    for match in teamA["Recent Results"]:
        matches_countA += 1
        if match["result"] == "win":
            recent_winsA += 1
    
    if matches_countA == 0:
        return 0, 0

    matches_countB = 0
    recent_winsB = 0
    for match in teamB["Recent Results"]:
        matches_countB += 1
        if match["result"] == "win":
            recent_winsB += 1

    if matches_countB == 0:
        return 0, 0

    r_recentA = recent_winsA/matches_countA
    r_recentB = recent_winsB/matches_countB

    p_recentA = r_recentA / (r_recentA + r_recentB)
    p_recentB = 1 - p_recentA

    return p_recentA, p_recentB

def main(name_teamA:str, name_teamB:str, series:int, maps:list[str]):
    data = load_data()
    
    weights = []
    match series:
        case 1:
            weights = {"rank":0.4, "map":0.5, "results":0.1}
        case 3:
            weights = {"rank":0.4, "map":0.4, "results":0.2}
        case 5:
            weights = {"rank":0.2, "map":0.4, "results":0.4}

    teamA = None
    for team in data["teams"]:
        if team["Name"].lower() == name_teamA.lower():
            teamA = team

    if teamA == None:
        print(f"Team '{name_teamA}' not found in dataset! Simulation aborted.")
        return -1

    teamB = None
    for team in data["teams"]:
        if team["Name"].lower() == name_teamB.lower():
            teamB = team
    
    if teamB == None:
        print(f"Team '{name_teamB}' not found in dataset! Simulation aborted.")
        return -1
    
    for map_name in maps:
        teamA_maps = [map_item["Map"].lower() for map_item in teamA["Maps Stats"]]
        if map_name.lower() not in teamA_maps:
            print(f"Map '{map_name}' is a invalid map! Simulation aborted.")
            return -1

    p_rankA, p_rankB = calc_p_rank(teamA, teamB)
    p_mapsA = []
    p_mapsB = []
    for i in range(series):
        a, b = calc_p_map(teamA, teamB, maps[i])
        p_mapsA.append(a)
        p_mapsB.append(b)
    
    p_mapA = 0
    for p_map in p_mapsA:
        p_mapA += p_map
    p_mapA = p_mapA / series
    p_mapB = 1 - p_mapA

    p_recentA, p_recentB = calc_p_recent_results(teamA, teamB)

    p_winA = weights["rank"]*p_rankA + weights["map"]*p_mapA + weights["results"]*p_recentA
    p_winB = 1 - p_winA

    p_winA = p_winA*100
    p_winB = p_winB*100

    print(f"Probability of team A winning: {p_winA:.1f}%")
    print(f"Probability of team B winning: {p_winB:.1f}%")

if __name__ == "__main__":
    print("="*70)
    print("Valorant Matchup Simulator".center(70, " "))
    print("="*70)

    name_teamA = input("Input team A name: ").strip()
    print("-"*70)

    name_teamB = input("Input team B name: ").strip()
    print("-"*70)
    
    while True:
        series = input("Number of maps played (series): ").strip()
        try:
            series = int(series)
            if series not in (1,3,5):
                raise ValueError
        except ValueError:
            print("Invalid number of maps! Must be 1, 3 or 5.")
        else:
            break
        finally:
            print("-"*70)

    maps = []
    for i in range(series):
        map_n = input(f"Map {i+1}: ").strip()
        maps.append(map_n)
    print("-"*70)
    
    code = main(name_teamA, name_teamB, series, maps)
    print("="*70)

    exit(code)

    
