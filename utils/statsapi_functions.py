import requests
import pandas as pd
import statsapi
import json
from database_connection import engine
from database_connection import record_to_table



def stats_api_schedule(
    season: int = 2025,
    start_date: str = None,
    end_date: str = None,
):
    if start_date:
        url = f'https://statsapi.mlb.com/api/v1/schedule?hydrate=team,lineups&sportId=1&startDate={start_date}&endDate={end_date}'
    else:
        url = f'https://statsapi.mlb.com/api/v1/schedule?hydrate=team,lineups&sportId=1&season={season}'

    response = requests.get(url)
    games_data = []
    if response.status_code == 200:
        data = response.json()
        for date in data.get("dates", []):
            for game in date.get("games", []):
                game_id = game.get("gamePk")
                game_datetime = game.get("gameDate")
                game_date = game.get("officialDate")
                home_team = game['teams']['home']['team']['name']
                away_team = game['teams']['away']['team']['name']
                #home_abbr = game['teams']['home']['team']['abbreviation']
                #away_abbr = game['teams']['away']['team']['abbreviation']
                away_id = game['teams']['away']['team']['id']
                home_id = game['teams']['home']['team']['id']
                status = game.get("status", {})
                game_status = status.get("codedGameState")
                game_type = game.get("gameType")
                double_header = game.get("doubleHeader")
                game_num = game.get("gameNumber")




                # Extract player IDs from lineup
                lineups = game.get("lineups", {})
                away_player_ids = [
                    player["id"] for player in lineups.get("awayPlayers", [])
                ]
                home_player_ids = [
                    player["id"] for player in lineups.get("homePlayers", [])
                ]


                games_data.append({
                    "game_id": game_id,
                    "game_datetime": game_datetime,
                    "game_date": game_date,
                    #"home_abbr": home_abbr,
                    #"away_abbr": away_abbr,
                    "home_id": home_id,
                    "away_id": away_id,
                    "status": game_status,
                    "game_type": game_type,
                    "double_header": double_header,
                    "game_num": game_num,
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_lineup": home_player_ids,
                    "away_lineup": away_player_ids,
                })
    df = pd.DataFrame(games_data)
    df["home_lineup"] = df["home_lineup"].apply(json.dumps)
    df["away_lineup"] = df["away_lineup"].apply(json.dumps)
    print(df.head())
    record_to_table(df, 'mlb_jalen.mlb_schedule')
    return 1


def statsapi_scrape_play_by_play(
        start_date: str = None,
        end_date: str = None,
):
    
    query = f"""
    select * from mlb_jalen.mlb_schedule
    where game_date >= '{start_date}'
    and game_date <= '{end_date}'
    and status = 'F'
    and game_type in ('R', 'P')
    order by game_datetime, game_id
    """

    with engine.connect() as con:
        df_sched = pd.read_sql(query, con=con)
    print(df_sched)

    for index, row in df_sched.iterrows():
        game_id = row['game_id']
        # Fetch JSON data
        url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/playByPlay"
        response = requests.get(url)
        data = response.json()
        rows = []

        # Loop through each play
        for play in data["allPlays"]:
            about = play.get("about", {})
            result = play.get("result", {})
            matchup = play.get("matchup", {})
            batter = matchup.get("batter", {})
            pitcher = matchup.get("pitcher", {})
            pitch_hand = matchup.get("pitchHand", {})
            bat_side = matchup.get("batSide", {})
            runners = play.get("runners", [])
            count = play.get("count", {})
            play_events = play.get("playEvents", [])

            # If no runners, still need one row per playEvent
            if not runners:
                runners = [None]

            for event in play_events:
                row = {
                    # Game context
                    "game_id": game_id,
                    "at_bat_index": about.get("atBatIndex"),
                    "ab_start_time": about.get("startTime"),
                    "ab_end_time": about.get("endTime"),
                    "inning": about.get("inning"),
                    "half_inning": about.get("halfInning"),
                    "is_complete": about.get("isComplete"),
                    "event_type": event.get("type"),
                    "play_event_description": event.get("details", {}).get("description"),
                    "batter_id": batter.get("id"),
                    "batter_name": batter.get("fullName"),
                    "pitcher_id": pitcher.get("id"),
                    "pitcher_name": pitcher.get("fullName"),
                    "pitcher_hand": pitch_hand.get("code"),
                    "batter_side": bat_side.get("code"),
                    "result_type": result.get("type"),
                    "play_result_event": result.get("event"),
                    "play_result_description": result.get("description"),
                    "rbi": result.get("rbi"),
                    "home_score": result.get("homeScore"),
                    "away_score": result.get("awayScore"),
                    "is_out": result.get("isOut"),
                    "balls": count.get("balls"),
                    "strikes": count.get("strikes"),
                    "outs": count.get("outs"),
                    "pitch_number": event.get("pitchNumber")
                }
                

                # Event details
                details = event.get("details", {})
                row.update({
                    "call_code": details.get("call", {}).get("code"),
                    "call_description": details.get("description"),
                    "pitch_type": details.get("type", {}).get("description"),
                    "pitch_code": details.get("type", {}).get("code"),
                    "ball_color": details.get("ballColor"),
                    "trail_color": details.get("trailColor"),
                    "is_in_play": details.get("isInPlay"),
                    "is_strike": details.get("isStrike"),
                    "is_ball": details.get("isBall")
                })
                
                #play count
                play_count = event.get("count", {})
                row.update({
                    "play_balls": play_count.get("balls"),
                    "play_strikes": play_count.get("strikes"),
                    "play_outs": play_count.get("outs"),
                })
                
                # Pitch data
                pitch_data = event.get("pitchData", {})
                row.update({
                    "start_speed": pitch_data.get("startSpeed"),
                    "end_speed": pitch_data.get("endSpeed"),
                    "strike_zone_top": pitch_data.get("strikeZoneTop"),
                    "strike_zone_zottom": pitch_data.get("strikeZoneBottom"),
                    "zone": pitch_data.get("zone"),
                    "plate_time": pitch_data.get("plateTime"),
                    "extension": pitch_data.get("extension")
                })
                # Coordinates
                coords = pitch_data.get("coordinates", {})
                for k, v in coords.items():
                    row[f"coordinates_{k.lower()}"] = v

                # Pitch breaks
                breaks = pitch_data.get("breaks", {})
                row.update({
                    "break_angle": breaks.get("breakAngle"),
                    "break_length": breaks.get("breakLength"),
                    "break_vertical": breaks.get("breakVertical"),
                    "break_vertical_induced": breaks.get("breakVerticalInduced"),
                    "break_horizontal": breaks.get("breakHorizontal"),
                    "spin_rate": breaks.get("spinRate"),
                    "spin_direction": breaks.get("spinDirection")
                })

                #hit data
                hit = event.get("hitData", {})
                row.update({
                    "launch_speed": hit.get("launchSpeed"),
                    "launch_angle": hit.get("launchAngle"),
                    "total_distance": hit.get("totalDistance"),
                    "trjaectory": hit.get("trajectory"),
                    "hardness": hit.get("hardness"),
                    "location": hit.get("location"),
                    "hit_x": hit.get("coordinates", {}).get("coordX"),
                    "hit_y": hit.get("coordinates", {}).get("coordY"),
                })
                
                for i, runner in enumerate(runners):
                    prefix = f"runner{i+1}_"

                    # Runner info
                    if runner:
                        row.update({
                            f"{prefix}id": runner.get("movement", {}).get("runner", {}).get("id") or runner.get("details", {}).get("runner", {}).get("id"),
                            f"{prefix}name": runner.get("movement", {}).get("runner", {}).get("fullName") or runner.get("details", {}).get("runner", {}).get("fullName"),
                            f"{prefix}start": runner.get("movement", {}).get("start"),
                            f"{prefix}end": runner.get("movement", {}).get("end"),
                            f"{prefix}out_base": runner.get("movement", {}).get("outBase"),
                            f"{prefix}is_out": runner.get("movement", {}).get("isOut"),
                            f"{prefix}credit_rbi": runner.get("details", {}).get("rbi"),
                            f"{prefix}credit_earned": runner.get("details", {}).get("earned"),
                            f"{prefix}event": runner.get("details", {}).get("event")
                        })
                    else:
                        row.update({
                            f"{prefix}id": None,
                            f"{prefix}name": None,
                            f"{prefix}start": None,
                            f"{prefix}end": None,
                            f"{prefix}out_base": None,
                            f"{prefix}is_out": None,
                            f"{prefix}credit_rbi": None,
                            f"{prefix}credit_earned": None,
                            f"{prefix}event": None
                        })

                    rows.append(row)

        # Convert to DataFrame
        df = pd.DataFrame(rows)
        df = df[df['pitch_number'].notna()]
        df['is_in_play'] = df['is_in_play'].astype(int)
        df['is_strike'] = df['is_strike'].astype(int)
        df['is_ball'] = df['is_ball'].astype(int)

        #df.to_csv('output.csv')
        record_to_table(df, 'mlb_jalen.mlb_pbp')
    return 1

# Helper function to flatten a stats category
def flatten_stats(stats_dict, prefix):
    if not isinstance(stats_dict, dict):
        return {}
    return {f"{prefix}_{k}": v for k, v in stats_dict.items()}

# Extract player stats for a team
def extract_team_players(data, team_side):
    players = data['teams'][team_side]['players']
    team_stats = []

    for player_id, player_data in players.items():
        person = player_data['person']
        stats = player_data.get('stats', {})

        row = {
            'id': person.get('id'),
            'name': person.get('fullName'),
            'position': player_data.get('position', {}).get('abbreviation'),
            'location': team_side,
            'team': data['teams'][team_side]['team']['abbreviation']
        }

        # Expand each stats category
        row.update(flatten_stats(stats.get('batting', {}), 'batting'))
        row.update(flatten_stats(stats.get('pitching', {}), 'pitching'))
        row.update(flatten_stats(stats.get('fielding', {}), 'fielding'))

        team_stats.append(row)

    return team_stats

# Function to pull all teamStats categories
def get_team_stats(data, team_key):
    team_data = data['teams'][team_key]
    team_stats = team_data.get('teamStats', {})
    
    # Flatten all available categories
    batting = team_stats.get('batting', {})
    pitching = team_stats.get('pitching', {})
    fielding = team_stats.get('fielding', {})
    
    # Add team identifiers
    combined = {
        **{f'batting_{k}': v for k, v in batting.items()},
        **{f'pitching_{k}': v for k, v in pitching.items()},
        **{f'fielding_{k}': v for k, v in fielding.items()},
        'team_name': team_data['team']['name'],
        'team_id': team_data['team']['id']
    }
    return combined


def statsapi_scrape_boxscore(
        start_date: str = None,
        end_date: str = None,
):
    
    query = f"""
    select * from mlb_jalen.mlb_schedule
    where game_date >= '{start_date}'
    and game_date <= '{end_date}'
    and status = 'F'
    and game_type in ('R', 'P')
    order by game_datetime, game_id
    """

    with engine.connect() as con:
        df_sched = pd.read_sql(query, con=con)


    for index, row in df_sched.iterrows():
        game_id = row['game_id']
        # Fetch boxscore data
        url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
        response = requests.get(url)
        data = response.json()

        # Combine home and away players
        home_stats = extract_team_players(data, 'home')
        away_stats = extract_team_players(data, 'away')

        # Combine and convert to DataFrame
        df_players = pd.DataFrame(home_stats + away_stats)
        df_batters = df_players.dropna(subset=['batting_atBats'])
        df_pitchers = df_players.dropna(subset=['pitching_inningsPitched'])
        # Drop all columns irrelavant to position group
        df_batters = df_batters.loc[:, ~df_batters.columns.str.startswith('pitching_')]
        df_pitchers = df_pitchers.loc[:, ~df_pitchers.columns.str.startswith('batting_')]
        df_pitchers = df_pitchers.loc[:, ~df_pitchers.columns.str.startswith('fielding_')]

        df_batters.columns = df_batters.columns.str.lower()
        df_pitchers.columns = df_pitchers.columns.str.lower()

        df_batters['game_id'] = game_id
        df_pitchers['game_id'] = game_id

        #now do teams
        # Build DataFrame from both teams
        home_stats = get_team_stats(data, 'home')
        away_stats = get_team_stats(data, 'away')

        df_team_stats = pd.DataFrame([home_stats, away_stats])
        df_team_stats.columns = df_team_stats.columns.str.lower()

        # Show the result
        print(df_team_stats)

        # Optional: make all column names lowercase
        df_team_stats.columns = df_team_stats.columns.str.lower()
        df_team_stats['game_id'] = game_id

        df_pitchers.replace('-.--', 0, inplace=True)
        df_batters.replace('-.--', 0, inplace=True)
        df_team_stats.replace('-.--', 0, inplace=True)

        record_to_table(df_team_stats, 'mlb_jalen.mlb_box_score_team')
        record_to_table(df_batters, 'mlb_jalen.mlb_box_score_batter')
        record_to_table(df_pitchers, 'mlb_jalen.mlb_box_score_pitcher')
    return 1

def statsapi_scrape_event_meta(
    season: int = 2025,
    start_date: str = None,
    end_date: str = None,
):
    if start_date:
        url = f'https://statsapi.mlb.com/api/v1/schedule/?sportId=1&startDate={start_date}&endDate={end_date}&hydrate=weather,weatherForecast,officials'
    else:
        url = f'https://statsapi.mlb.com/api/v1/schedule/?sportId=1&season={season}&hydrate=weather,weatherForecast,officials'
    print(url)
    url = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2025-01-01&endDate=2025-05-18&hydrate=weather,weatherForecast,officials'
    response = requests.get(url)
    games_data = []
    if response.status_code == 200:
        data = response.json()
        for date in data.get("dates", []):
            for game in date.get("games", []):
                game_id = game.get("gamePk")
                game_datetime = game.get("gameDate")
                game_date = game.get("officialDate")
                home_team = game['teams']['home']['team']['name']
                away_team = game['teams']['away']['team']['name']
                #home_abbr = game['teams']['home']['team']['abbreviation']
                #away_abbr = game['teams']['away']['team']['abbreviation']
                away_id = game['teams']['away']['team']['id']
                home_id = game['teams']['home']['team']['id']
                status = game.get("status", {})
                game_status = status.get("codedGameState")
                game_type = game.get("gameType")
                double_header = game.get("doubleHeader")
                game_num = game.get("gameNumber")
                officials = game.get("officials")
                weather = game.get("weather")
                weather_forecast = game.get("weatherForecast")
                #forecast_timestamp = game['weatherForecast']['forecastTimestamp']
                forecast_timestamp = weather_forecast["forecastTimestamp"]
                pop_adjusted = weather_forecast["adjustedPrecipitationProbability"]
                cloud_cover = weather_forecast["cloudCoverPercentage"]
                desc = weather_forecast["description"]
                dewpoint = weather_forecast["dewpoint"]
                temp_feelslike = weather_forecast["temperatureFeelsLike"]
                sky_condition = weather_forecast["skyConditionIconId"]
                precipitation = weather_forecast["precipitationId"]
                pop = weather_forecast["precipitationProbability"]
                precipitation_rate = weather_forecast["precipitationRate"]
                relative_humidity = weather_forecast["relativeHumidity"]
                temperature = weather_forecast["temperature"]
                thunderstorm_prob = weather_forecast["thunderstormProbability"]
                wind_direction = weather_forecast["windDirectionDegrees"]
                wind_speed = weather_forecast["windSpeed"]
                surface_pressure = weather_forecast["surfacePressure"]
                



                games_data.append({
                    "game_id": game_id,
                    "game_datetime": game_datetime,
                    "game_date": game_date,
                    #"home_abbr": home_abbr,
                    #"away_abbr": away_abbr,
                    "home_id": home_id,
                    "away_id": away_id,
                    "status": game_status,
                    "game_type": game_type,
                    "double_header": double_header,
                    "game_num": game_num,
                    "home_team": home_team,
                    "away_team": away_team,
                    "forecast_timestamp": forecast_timestamp,
                    "pop_adjusted": pop_adjusted,
                    "cloud_cover": cloud_cover,
                    "descr": desc,
                    "dewpoint": dewpoint,
                    "temp_feelslike": temp_feelslike,
                    "sky_condition": sky_condition,
                    "precipitation": precipitation,
                    "pop": pop,
                    "precipitation_rate": precipitation_rate,
                    "relative_humidity": relative_humidity,
                    "temperature": temperature,
                    "thunderstorm_prob": thunderstorm_prob,
                    "wind_direction": wind_direction,
                    "wind_speed": wind_speed,
                    "surface_pressure": surface_pressure,
                })
    df = pd.DataFrame(games_data)
    #print(df.head())
    record_to_table(df, 'mlb_jalen.mlb_event_meta')
    return 1


stats_api_schedule(season=2025)
#statsapi_scrape_boxscore(start_date='2017-01-01', end_date='2024-12-31')

#statsapi_scrape_boxscore(start_date='2017-01-01', end_date='2024-12-31')

#statsapi_scrape_event_meta(start_date='2025-01-01', end_date='2025-05-18')
statsapi_scrape_play_by_play(start_date='2025-05-01', end_date='2025-05-18')