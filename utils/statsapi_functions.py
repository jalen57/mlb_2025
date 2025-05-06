import statsapi
import pandas as pd
from database_connection import engine
from database_connection import record_to_table



#box score
bs = statsapi.get('game_playByPlay', {'gamePk': 778563})
df = pd.json_normalize(bs['allPlays'])
#print(bs)
df.to_csv('test.csv')


#finished below

#linescore
#bs = statsapi.get('game_linescore', {'gamePk': 778563})
#df = pd.json_normalize(bs['innings'])