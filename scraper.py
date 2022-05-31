import time
import requests
import pickle

from bs4 import BeautifulSoup as bs

# Credits to Ivan
def get_elo(league: str, year: int):
    url = "https://www.besoccer.com/competition"
    r = requests.get(f"{url}/scores/{league}/{year}")
    time.sleep(1)
    soup = bs(r.content, 'html.parser')
    matchday_str = soup.find('div', {'class': 'panel-title'}).text
    matchday_bound = [int(s) for s in matchday_str.split() if s.isdigit()][0]
    
    links = []
    elo_dict = {}
    for round in range(1, matchday_bound + 1):
        r = requests.get(f"{url}/scores/{league}/{year}/round{round}")
        time.sleep(3)
        soup = bs(r.content, 'html.parser')
        matches_box = soup.find('div', {'class': 'panel-body p0 match-list-new'})
        links += [match.get('href') for match in matches_box.find_all('a', {'class': 'match-link'})]
    for link in links:
        r = requests.get(link + '/analysis')
        time.sleep(3)
        soup = bs(r.content, 'html.parser')
        elo_box = soup.find('div', {'class': 'panel-body pn compare-data'})
        if elo_box:
            elo_row = elo_box.find_all('tr')[1]
            if len(elo_row) > 0:
                home_elo_box = elo_row.find('td', {'class': 'team1-c'})
                away_elo_box = elo_row.find('td', {'class': 'team2-c'})
                if home_elo_box:
                    home_elo = home_elo_box.text.strip()
                else:
                    home_elo = 'N/A'
                if away_elo_box:
                    away_elo = away_elo_box.text.strip()
                else:
                    away_elo = 'N/A'
            else:
                home_elo = 'N/A'
                away_elo = 'N/A'
        else:
            home_elo = 'N/A'
            away_elo = 'N/A'
        elo_dict[link] = {'Elo_home': home_elo, 'Elo_away': away_elo}
    return elo_dict

def main():
    leagues = ['segunda_division', # Spain
            'serie_a', 'serie_b',  # Italy
            'bundesliga', '2_liga', # Germany
            'ligue_1', 'ligue_2', # France
            'premier_league', 'championship', # England
            'eredivisie', 'eerste_divisie', # Netherlands
            'primeira_liga', 'segunda_liga', # Portugal
            ]
    years = range(1990, 2022)
    elo = {}
    for league in leagues:
        for year in years:
            elo.update(get_elo(league, year))
    with open('elo_dict.pkl', 'wb') as f:
        pickle.dump(elo, f)

if __name__ == '__main__':
    main()