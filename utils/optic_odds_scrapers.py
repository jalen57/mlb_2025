import requests
import pandas as pd
from utils.database_connection import engine
from utils.database_connection import record_to_table
key = '1a4b0e52-0281-46fb-a853-3730165bd846'

def optic_odds_get_fixtures(
        key: str = '1a4b0e52-0281-46fb-a853-3730165bd846',
        start_date_before: str = None,
        start_date_after: str = None,
        include_lineups: bool = False,
):
    base_url = f'https://api.opticodds.com/api/v3/fixtures?league=MLB&key={key}'
    url = base_url
    if start_date_before:
        base_url = f'https://api.opticodds.com/api/v3/fixtures?league=MLB&start_date_after={start_date_after}&start_date_before={start_date_before}&key={key}'

    if include_lineups:
        url = f'{base_url}&include_starting_lineups=True'
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        data = data['data']
        df = pd.DataFrame(data)
    else:
        df = 'no data'
    return df

def optic_odds_get_fixtures_active(
        key: str = '1a4b0e52-0281-46fb-a853-3730165bd846',
        start_date: str = None,
        include_lineups: bool = False,
):
    base_url = f'https://api.opticodds.com/api/v3/fixtures?league=MLB&key={key}'
    url = base_url
    if start_date:
        base_url = f'https://api.opticodds.com/api/v3/fixtures?league=MLB&start_date={start_date}&key={key}'

    if include_lineups:
        url = f'{base_url}&include_starting_lineups=True'
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        data = data['data']
        df = pd.DataFrame(data)
    else:
        df = 'no data'
    return df


def optic_odds_get_odds(
        key: str = '1a4b0e52-0281-46fb-a853-3730165bd846',
        id: str = None,
        odds_format: str = 'DECIMAL',
        sportsbook: str = 'bet365',
):
    url = f'https://api.opticodds.com/api/v3/fixtures/odds?&sportsbook={sportsbook}&fixture_id={id}&key={key}&odds_format={odds_format}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        data = data['data'][0]['odds']
        
        df = pd.DataFrame(data)
        df['game_id'] = id
    else:
        df = 'no data'
    return df

def update_pregame_odds(
        write: bool = True,
        start_date: str = None,
        end_date: str = None,
) -> dict:
    """updates pregame odds"""
    #get df of games
    df = optic_odds_get_fixtures(include_lineups=True, start_date_before=end_date, start_date_after=start_date)
    #filter to life games
    df = df[df['status'] == 'unplayed']
    #loop through games
    for index, row in df.iterrows():
        df_odds_pinn = optic_odds_get_odds(id = row['id'], sportsbook='Pinnacle')
        df_odds_b365 = optic_odds_get_odds(id = row['id'], sportsbook='bet365')
        df_odds_bmgm = optic_odds_get_odds(id = row['id'], sportsbook='BetMGM')
        df_odds_bova = optic_odds_get_odds(id = row['id'], sportsbook='Bovada')

        df_odds_drki = optic_odds_get_odds(id = row['id'], sportsbook='Draftkings')
        df_odds_cris = optic_odds_get_odds(id = row['id'], sportsbook='Betcris')
        df_odds_briv = optic_odds_get_odds(id = row['id'], sportsbook='BetRivers')
        df_odds_rock = optic_odds_get_odds(id = row['id'], sportsbook='Hard Rock')

        #stack data frames
        combined_df = pd.concat(
            [
                df_odds_pinn,
                df_odds_b365,
                df_odds_bmgm,
                df_odds_bova,
                df_odds_drki,
                df_odds_cris,
                df_odds_briv,
                df_odds_rock,
            ], ignore_index=True)
        record_to_table(combined_df, 'mlb_jalen.mlb_pregame_odds')
    response = {
        'meta':
            {
                'message':
                    f'Successfully written mlb pregame odds.',
            },

    }
    return response

def update_live_odds(
        write: bool = True,
        start_date: str = None,
        end_date: str = None,
) -> dict:
    """updates pregame odds"""
    #get df of games
    df = optic_odds_get_fixtures(include_lineups=True, start_date_before=end_date, start_date_after=start_date)
    #filter to life games
    df = df[df['status'] == 'live']
    #loop through games
    for index, row in df.iterrows():
        df_odds_pinn = optic_odds_get_odds(id = row['id'], sportsbook='Pinnacle')
        df_odds_b365 = optic_odds_get_odds(id = row['id'], sportsbook='bet365')
        df_odds_bmgm = optic_odds_get_odds(id = row['id'], sportsbook='BetMGM')
        df_odds_bova = optic_odds_get_odds(id = row['id'], sportsbook='Bovada')

        df_odds_drki = optic_odds_get_odds(id = row['id'], sportsbook='Draftkings')
        df_odds_cris = optic_odds_get_odds(id = row['id'], sportsbook='Betcris')
        df_odds_briv = optic_odds_get_odds(id = row['id'], sportsbook='BetRivers')
        df_odds_rock = optic_odds_get_odds(id = row['id'], sportsbook='Hard Rock')

        #stack data frames
        combined_df = pd.concat(
            [
                df_odds_pinn,
                df_odds_b365,
                df_odds_bmgm,
                df_odds_bova,
                df_odds_drki,
                df_odds_cris,
                df_odds_briv,
                df_odds_rock,
            ], ignore_index=True)
        record_to_table(combined_df, 'mlb_jalen.mlb_live_odds')
    response = {
        'meta':
            {
                'message':
                    f'Successfully written mlb live odds.',
            },

    }
    return response

