import requests
import pandas as pd
import statsapi
import sys
import os

# Add the path to ml/ so Python can find common/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from common.database_connection import record_to_table
# Fetch JSON data
url = "https://statsapi.mlb.com/api/v1/game/777976/playByPlay"
response = requests.get(url)
data = response.json()
game_id = 9
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

df.to_csv('output.csv')
record_to_table(df, 'mlb_jalen.mlb_pbp')

