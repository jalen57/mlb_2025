
import asyncio
import json
import subprocess
import time
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

import pandas as pd
import requests
from fastapi import APIRouter
from fastapi import Query

from utils.database_connection import engine
from utils.database_connection import record_to_table
from utils.optic_odds_scrapers import update_live_odds
from utils.optic_odds_scrapers import update_pregame_odds


#ncaamb_player_EV_stats = mapping_league_to_EV_stats['ncaamb']
league = 'mlb'
league_tag = 'MLB'

router = APIRouter(
    prefix=f'/{league}',
    tags=[league_tag],
    responses={
        404: {
            'description': 'MLB Baseball not found'
        }
    },
)


@router.put(
    '/odds/pregame',
    summary='Runs odds scraping through optic odds for pregame status matches'
)
def put_pregame_odds(
    start_date: str = Query(
        None,
        description='When given, only return predictions for specified player(s)'
    ),
    end_date: str = Query(
        None,
        description='When given, only return predictions for specified player(s)'
    ),
):
    
    response = update_pregame_odds(start_date=start_date, end_date=end_date)
    return response
    



@router.put(
    '/odds/live',
    summary='Runs odds scraping through optic odds for pregame status matches'
)
def put_live_odds(
    start_date: str = Query(
        None,
        description='When given, only return predictions for specified player(s)'
    ),
    end_date: str = Query(
        None,
        description='When given, only return predictions for specified player(s)'
    ),
):
    
    response = update_live_odds(start_date=start_date, end_date=end_date)
    return response
    

