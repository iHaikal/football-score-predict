import pandas as pd

class DataLoader:
    def __init__(self, path: str, elo_path=None):
        self.path = path
        self.elo_path = elo_path
    
    def __parse(self, df: pd.DataFrame):
        # Remove dates in results
        df.drop(df[df['Result'].str.contains('JAN')].index, inplace=True)
        df.drop(df[df['Result'].str.contains('MAR')].index, inplace=True)
        # Remove brackets and everything before and after.
        df['Result'] = df['Result'].str.replace('\d\s\(', '').str.replace('\)\s\d', '')
        df['Home_Score'] = df['Result'].apply(lambda x: int(x.split('-')[0]))
        df['Away_Score'] = df['Result'].apply(lambda x: int(x.split('-')[1]))
        df['Result'] = df.apply(lambda x: 0 if x['Home_Score'] > x['Away_Score'] else 1 if x['Home_Score'] < x['Away_Score'] else 2, axis=1)
        return df
    
    def load(self, features=[]):
        df = pd.read_csv(self.path)
        df = self.__parse(df)
        for f in features:
            try:
                df = f(df, elo_path=self.elo_path)
            except Exception as err:
                print(f'Error building feature "{f.__name__}": {err}')
        return df