import pandas as pd
import pickle

from collections import defaultdict

def build_streaks(df: pd.DataFrame, **kwargs):
    def seasons_streak(df: pd.DataFrame, season: int):
        s_df = df[df['Season'] == season].copy()
        s_df.sort_values(by='Round', ascending=True)
        streaks = {}
        team_streaks = defaultdict(lambda : { 'wins': 0, 'score': 0 })
        for _, row in s_df.iterrows():
            home_team = row['Home_Team']
            away_team = row['Away_Team']
            streaks[row['Link']] = {
                'wins': {
                    'home_streak' : team_streaks[home_team]['wins'],
                    'away_streak' : team_streaks[away_team]['wins']
                },
                'scores': {
                    'home_streak' : team_streaks[home_team]['score'],
                    'away_streak' : team_streaks[away_team]['score']
                }
            }
            # Score streaks
            team_streaks[home_team]['score'] += row['Home_Score']
            team_streaks[away_team]['score'] += row['Away_Score']
            # Win streaks
            if row['Result'] == 0:
                team_streaks[home_team]['wins'] += 1
                team_streaks[away_team]['wins'] = 0
            elif row['Result'] == 1:
                team_streaks[home_team]['wins'] = 0
                team_streaks[away_team]['wins'] += 1
            else:
                team_streaks[home_team]['wins'] = 0
                team_streaks[away_team]['wins'] = 0
        return streaks
    streaks = {}
    for league in df['League'].unique():
        league_df = df[df['League'] == league].copy(deep=False)
        for season in league_df['Season'].unique():
            streaks.update(seasons_streak(league_df, season))
    df['Home_Win_Streak'] = df.apply(lambda x: streaks[x['Link']]['wins']['home_streak'], axis=1)
    df['Away_Win_Streak'] = df.apply(lambda x: streaks[x['Link']]['wins']['away_streak'], axis=1)
    df['Home_Score_Streak'] = df.apply(lambda x: streaks[x['Link']]['scores']['home_streak'], axis=1)
    df['Away_Score_Streak'] = df.apply(lambda x: streaks[x['Link']]['scores']['away_streak'], axis=1)
    return df

def build_elo(df: pd.DataFrame, **kwargs):
    elo_path = kwargs.get('elo_path')
    if elo_path is None:
        return df
    
    with open(elo_path, 'rb') as f:
        elo_info = pickle.load(f)
        
    df['Home_Elo'] = df.apply(lambda x: elo_info[x['Link']]['Elo_home'], axis=1).fillna(0)
    df['Away_Elo'] = df.apply(lambda x: elo_info[x['Link']]['Elo_away'], axis=1).fillna(0)
    return df