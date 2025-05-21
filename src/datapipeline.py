#standard imports
import json
import pandas as pd
import numpy as np
import joblib
import tqdm
import sklearn
import sys 
import os

#custom imports
sys.path.insert(1, 'C:/Users/jalen/mlb_2025')
from common.database_connection import engine
from common.data import Dataset


class MLBDataPipeline:
    def __init__(
            self,
            used_for: str = 'training',
            start_datetime: str = '2001-01-01',
            include_playoff: bool = False,
            verbose: int = 1
    ):
        assert used_for in ['training', 'prediction','backtesting','simulation']
        self.used_for = used_for

        self.start_datetime = start_datetime

        self.current_season = None
        self.con = engine

        #cached data frames

        self.df_pbp = None
        self.df_batters = None
        self.df_pitchers = None
        self.df_bst = None
        self.df_event = None

        if verbose:
            print('initialized MLB data pipeline')
    #load event
    #load bst
    #load pbp
    #load batter
    #load pitcher
    def load_box_score_team(
            self,
            preprocessed: bool = True,
            from_csv: str = None,
            to_csv: str = None,
    ) -> pd.DataFrame:
        """Loading MLB Team Box Score Data"""
        if from_csv:
            df = pd.read_csv(from_csv)
        else:
            with self.con.connect() as con:
                query = f"""
                select * from mlb_jalen.box_score_team
                """
                df = pd.read_sql(query, con=con)
        self.df_bst = df
        return df.copy()
            
    def load_play_by_play(
            self,
    ) -> pd.DataFrame:
        with self.con.connect() as con:
            query = f"""
                select * from mlb_jalen.mlb_pbp
                where ab_start_time >= '{self.start_datetime}'
                and batter_name like '%Nick Sogard%'
                order by ab_start_time, inning, half_inning, at_bat_index, pitch_number
                """
            df = pd.read_sql(query, con=con)
            df.to_csv('pbp_iso.csv')
        self.df_pbp = df
        return df.copy()
    
    def prepare_game_dataset(
            self,
    ) -> Dataset:
        
        #load play by play data
        df_pbp = self.load_play_by_play(
        ) if self.df_pbp is None else self.df_pbp.copy()


        print(df_pbp.head(5))
        return 1
        



if __name__ == '__main__':
    dp = MLBDataPipeline(start_datetime='2025-01-01')
    dp.prepare_game_dataset()    