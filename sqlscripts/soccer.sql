use ai;


create or replace view ai.soccer_event as
with team as (select team.id,
                     team.league_id,
                     team.conference_id,
                     team.division_id,
                     team.venue_id,
                     team.abbreviation,
                     concat(team.location, ' ', team.nick_name) as full_name,
                     league.abbreviation                        as league_abbr
              from api_european_football.team
                       join api_european_football.league
                            on team.league_id = league.id)
#    , bst as (select event_id,
#                     team_id,
#                     runs,
#                     win,
#                     loss
#              from api_european_football.box_score_team)
   , mo_moneyline as
    (select event_id,
            outcome_type,
            money_line_name,
            avg(if(odds >= 0, 1 + (odds / 100), 1 - (100 / odds))) as odds
     from api_european_football.other_books_moneyline
     where money_line_name regexp 'moneyline'
     group by event_id, outcome_type, money_line_name)
   , mo_spread as
    (select event_id,
            type,
            avg(spread)                                                                    as avg_spread,
            avg(if(odds >= 0, 1 + (odds / 100), 1 - (100 / odds)))                         as avg_odds,
            avg(opening_spread)                                                            as avg_spread_open,
            avg(if(opening_odds >= 0, 1 + (opening_odds / 100), 1 - (100 / opening_odds))) as avg_odds_open
     from api_european_football.other_books_spread
     group by event_id, type)
   , mo_over_under as
    (select event_id,
            type,
            avg(total)                                                                     as avg_total,
            avg(if(odds >= 0, 1 + (odds / 100), 1 - (100 / odds)))                         as avg_odds,
            avg(opening_total)                                                             as avg_total_open,
            avg(if(opening_odds >= 0, 1 + (opening_odds / 100), 1 - (100 / opening_odds))) as avg_odds_open
     from api_european_football.other_books_over_under
     group by event_id, type)
select l.name                                                as event_league_name,
       l.abbreviation                                        as event_league_abbr,
       cast(s.season as integer)                             as season,
       e.start_date                                          as start_datetime,
       e.id                                                  as event_id,
       lower(et.name)                                        as event_type,
       convert((case
                    when e.sr_id regexp '^mock.*' then 'invalid'
                    when
#                         e.sr_status regexp 'closed|complete|ended'
                        e.team_home_score is not null and e.team_away_score is not null
                        then 'closed'
                    when e.sr_status regexp
                         'pre-game|scheduled|created|time-tbd|if-necessary|flex-schedule|delayed|not_started'
                        and e.start_date > utc_timestamp - interval 2 hour
                        then 'pre-game'
                    when e.sr_status regexp 'inprogress|in-progress|halftime'
                        and e.start_date > utc_timestamp - interval 8 hour
                        then 'inprogress'
                    else 'invalid' end) using utf8) collate
       utf8_unicode_ci                                       as classified_event_status,

       home.league_abbr                                      as home_team_league_abbr,
       e.team_home_id                                        as home_team_id,
       home.full_name                                        as home_team_name,

       away.league_abbr                                      as away_team_league_abbr,
       e.team_away_id                                        as away_team_id,
       away.full_name                                        as away_team_name,

       concat(away.abbreviation, ' @ ', home.abbreviation)   as matchup,
#        home_bst.runs                                       as home_team_score,
#        away_bst.runs                                       as away_team_score,
#        home_bst.runs + away_bst.runs                       as total_score,
#        home_bst.runs - away_bst.runs                       as home_lead,
#        home_bst.runs > away_bst.runs                       as home_win,

       e.team_home_score                                     as home_team_score,
       e.team_away_score                                     as away_team_score,
       e.team_home_score + e.team_away_score                 as total_score,
       e.team_home_score - e.team_away_score                 as home_lead,
       e.team_home_score > e.team_away_score                 as home_win,

#        home.conference_id = away.conference_id             as same_conference,
#        home.division_id = away.division_id                 as same_division,
       e.venue_id,
       e.attendance,
       v.timezone,
       v.latitude,
       v.longitude,
       v.elevation,
       e.series_id,
       e.title,
       mo_moneyline_odds.home_odds                           as mo_home_moneyline_odds,
       mo_moneyline_odds.away_odds                           as mo_away_moneyline_odds,
       mo_moneyline_odds.draw_odds                           as mo_draw_moneyline_odds,
       mo_spread_home.avg_spread                             as mo_home_spread,
       mo_spread_home.avg_odds                               as mo_home_spread_odds,
       mo_spread_away.avg_spread                             as mo_away_spread,
       mo_spread_away.avg_odds                               as mo_away_spread_odds,
       mo_total.total                                        as mo_total_score,
       mo_total.odds_over                                    as mo_total_over_odds,
       mo_total.odds_under                                   as mo_total_under_odds,
       e.other_books_data,
       mo_moneyline_odds.home_odds_open                      as mo_home_moneyline_odds_open,
       mo_moneyline_odds.away_odds_open                      as mo_away_moneyline_odds_open,
       mo_moneyline_odds.draw_odds_open                      as mo_draw_moneyline_odds_open,
       mo_spread_home.avg_spread_open                        as mo_home_spread_open,
       mo_spread_home.avg_odds_open                          as mo_home_spread_odds_open,
       mo_spread_away.avg_spread_open                        as mo_away_spread_open,
       mo_spread_away.avg_odds_open                          as mo_away_spread_odds_open,
       mo_total.total_open                                   as mo_total_score_open,
       mo_total.odds_over_open                               as mo_total_over_odds_open,
       mo_total.odds_under_open                              as mo_total_under_odds_open,
       e.sr_uuid,
       convert_tz(e.start_date, 'utc', 'America/Toronto')    as start_datetime_est,
       coalesce(lower(es.name), e.sr_status, e.match_status) as event_status
#        null
from api_european_football.event as e
         join api_european_football.league as l
              on e.league_id = l.id
         left join api_european_football.season as s
                   on e.season_id = s.id
         left join api_european_football.event_type as et
                   on e.type_id = et.id
         left join api_european_football.event_status as es
                   on e.event_status_id = es.id
    #          left join bst as home_bst
#                    on e.id = home_bst.event_id and e.team_home_id = home_bst.team_id
#          left join bst as away_bst
#                    on e.id = away_bst.event_id and e.team_away_id = away_bst.team_id
         left join api_european_football.venue as v
                   on e.venue_id = v.id
         left join team as home
                   on e.team_home_id = home.id
         left join team as away
                   on e.team_away_id = away.id
         left join (select event_id,
                           avg(if(money_line_name = 'moneyline_open' and outcome_type = 'home', odds,
                                  null)) as home_odds_open,
                           avg(if(money_line_name = 'moneyline_current' and outcome_type = 'home', odds,
                                  null)) as home_odds,
                           avg(if(money_line_name = 'moneyline_open' and outcome_type = 'away', odds,
                                  null)) as away_odds_open,
                           avg(if(money_line_name = 'moneyline_current' and outcome_type = 'away', odds,
                                  null)) as away_odds,
                           avg(if(money_line_name = 'moneyline_open' and outcome_type = 'draw', odds,
                                  null)) as draw_odds_open,
                           avg(if(money_line_name = 'moneyline_current' and outcome_type = 'draw', odds,
                                  null)) as draw_odds
                    from mo_moneyline
                    group by event_id) as mo_moneyline_odds
                   on e.id = mo_moneyline_odds.event_id
         left join (select *
                    from mo_spread
                    where type = 'home') as mo_spread_home
                   on e.id = mo_spread_home.event_id
         left join (select *
                    from mo_spread
                    where type = 'away') as mo_spread_away
                   on e.id = mo_spread_away.event_id
         left join (select event_id,
                           avg(avg_total)                                       as total,
                           avg(case when type = 'over' then avg_odds end)       as odds_over,
                           avg(case when type = 'under' then avg_odds end)      as odds_under,
                           avg(avg_total_open)                                  as total_open,
                           avg(case when type = 'over' then avg_odds_open end)  as odds_over_open,
                           avg(case when type = 'under' then avg_odds_open end) as odds_under_open
                    from mo_over_under
                    group by event_id) as mo_total
                   on e.id = mo_total.event_id

# where true
#   and e.start_date > utc_timestamp
# order by e.start_date
;


# select sr_status, count(1) as counts
# from api_european_football.event
# group by sr_status
# ;
#
# select match_status, count(1) as counts
# from api_european_football.event
# group by match_status


create or replace view ai.soccer_bst as
select cast(s.season as integer)                                       as season,
       e.start_date                                                    as start_datetime,
       e.id                                                            as event_id,
       el.abbreviation                                                 as event_league_abbr,
       et.event_type,
       (case
            when bst.team_id = e.team_home_id then e.team_away_id
            when bst.team_id = e.team_away_id then e.team_home_id end) as opp_team_id,
       bst.team_id,
       concat(t.location, ' ', t.nick_name)                            as team_name,
       t.abbreviation                                                  as team_abbr,
       (bst.team_id = e.team_home_id)                                  as is_home,
       bst.goals > opp_bst.goals                                       as win_loss,
       bst.goals - opp_bst.goals                                       as scores_lead,

       bst.goals,
       opp_bst.goals                                                   as goals_conceded,

       bst.involvement_in_attempt_at_goal,
       bst.involvement_in_attempt_at_goal_xg,
       bst.xg_value,

       bst.duels_total,
       bst.duels_complete,
       bst.duels_incomplete,
       bst.duels_offensive,
       bst.duels_offensive_won,
       bst.duels_defensive,
       bst.duels_defensive_won,
       bst.duels_defensive_opponents_half,
       bst.duels_defensive_opponents_half_won,
       bst.duels_defensive_own_box,
       bst.duels_defensive_own_box_won,
       bst.duels_defensive_own_half,
       bst.duels_defensive_own_half_won,
       bst.duels_fifty_fifty,
       bst.duels_sliding,
       bst.ground_duels_defensive,
       bst.ground_duels_defensive_won,
       bst.ground_duels_offensive,
       bst.ground_duels_offensive_won,
       bst.aerial_duels_defensive,
       bst.aerial_duels_defensive_won,
       bst.aerial_duels_offensive,
       bst.aerial_duels_offensive_won,

       bst.events,
       bst.events_successful,
       bst.events_key,
       bst.events_key_corner,
       bst.events_key_freekick,
       bst.events_inside_box,

       bst.fouls,
       bst.fouls_for,
       bst.fouls_against,
       bst.fouls_own_half,

       bst.interceptions_goalkeeper,
       bst.keeper_throws_short,
       bst.keeper_throws_long,

       bst.passes,
       bst.passes_complete,
       bst.passes_incomplete,
       bst.passes_key,
       bst.passes_forward,
       bst.passes_forward_complete,
       bst.passes_backward,
       bst.passes_backward_complete,
       bst.passes_first_in_possession,
       bst.passes_first_in_possession_forward,
       bst.passes_in_final_third,
       bst.passes_in_final_third_complete,
       bst.passes_opponents_half,
       bst.passes_opponents_half_complete,
       bst.passes_own_half,
       bst.passes_short,
       bst.passes_long,
       bst.passes_long_complete,
       bst.passes_long_incomplete,
       bst.passes_switch,
       bst.passes_wide,
       bst.passes_wide_complete,
       bst.passes_between_central_defenders,
       bst.passes_direct,
       bst.passes_into_box,

       bst.ball_possession,
       bst.ball_possession_adv,
       bst.possessions_time,
       bst.possessions_lost,
       bst.possessions_lost_by_passes,
       bst.possessions_lost_by_duel,
       bst.possessions_regained_by_duel,
       bst.possessions_regained_by_interception,
       bst.possessions_regained_in_play,
       bst.possessions_regained_in_play_own_half,
       bst.possessions_regained_in_opponents_half,
       bst.possession_opponents_half,

       bst.speed_of_play,

       bst.throw_ins,
       bst.throw_ins_adv,
       bst.throw_ins_keep_possession,

       bst.attempts_at_goal,
       bst.attempts_at_goal_on_target,
       bst.attempts_at_goal_blocked,
       bst.attempts_at_goal_header,
       bst.attempts_at_goal_inside_the_penalty_area,
       bst.attempts_at_goal_outside_the_penalty_area,
       bst.attempts_at_goal_inside_the_penalty_area_on_target,
       bst.attempts_at_goal_outside_the_penalty_area_on_target,
       bst.attempts_at_goal_inside_the_penalty_area_scored,
       bst.attempts_at_goal_outside_the_penalty_area_scored,
       bst.attempts_on_target_saves,

       bst.ball_progression,
       bst.ball_progression_complete,
       bst.ball_progression_incomplete,

       bst.clearances,

       bst.corners,
       bst.corners_long,
       bst.corners_short,
       bst.corner_kicks,

       bst.crosses,
       bst.crosses_completed,
       bst.crosses_incomplete,
       bst.crosses_early,
       bst.crosses_late,
       bst.crosses_low,
       bst.crosses_high,
       bst.crosses_to_goal,
       bst.crosses_to_attempt_at_goal,

       bst.free_kicks,
       bst.free_kicks_adv,
       bst.free_kicks_on_goal,
       bst.free_kicks_scored,
       bst.free_kicks_missed,

       bst.penalties_faced,
       bst.penalties_missed,

       bst.assists_adv,
       bst.assists_by_free_kick,

       bst.goal_kicks,
       bst.goal_kicks_adv,

       bst.offsides,
       bst.offsides_adv,

       bst.cards_given,
       bst.yellow_cards,
       bst.yellow_cards_adv,
       bst.yellow_red_cards,
       bst.red_cards,
       bst.direct_red_cards,
       bst.red_cards_for_second_caution,

       bst.shots_total,
       bst.shots_off_target,
       bst.shots_on_target,
       bst.shots_saved,
       bst.shots_blocked,

       bst.substitutions,
       bst.injuries,

       bst.period_scores,
       bst.ball_locations

from api_european_football.box_score_team as bst
         join(select id,
                     season_id,
                     type_id,
                     sr_status                           as event_status,
                     start_date,
                     team_home_id,
                     team_away_id,
                     (team_home_score - team_away_score) as home_lead,
                     venue_id,
                     league_id
              from api_european_football.event) as e
             on e.id = bst.event_id
         join (select id, abbreviation
               from api_european_football.league) as el
              on e.league_id = el.id
         join (select id, season
               from api_european_football.season) as s
              on s.id = e.season_id
         join (select id, conference_id, division_id, venue_id, abbreviation, location, nick_name
               from api_european_football.team) as t
              on bst.team_id = t.id
         left join (select id, lower(name) as event_type
                    from api_european_football.event_type) as et
                   on e.type_id = et.id
         join (select event_id, team_id, goals
               from api_european_football.box_score_team) as opp_bst
              on bst.event_id = opp_bst.event_id and bst.team_id != opp_bst.team_id
# where l.abbreviation = 'soccer'
#   and bst.runs is not null
;


create or replace view ai.soccer_bsp as
select cast(s.season as integer)                                       as season,
       e.start_date                                                    as start_datetime,
       e.id                                                            as event_id,
       l.abbreviation                                                  as event_league_abbr,
       lower(et.name)                                                  as event_type,
       (case
            when bsp.team_id = e.team_home_id then e.team_away_id
            when bsp.team_id = e.team_away_id then e.team_home_id end) as opp_team_id,
       bsp.team_id,
       concat(t.location, ' ', t.nick_name)                            as team_name,
       t.abbreviation                                                  as team_abbr,
       (bsp.team_id = e.team_home_id)                                  as is_home,
       bsp.player_id,
       p.full_name                                                     as player_name,
#        pos.name                                                        as starting_position,
       bsp.position_type,
       bsp.position,
       bsp.status,
       dnpt.name                                                       as did_not_play_type,

       bsp.aerial_duels_offensive,
       bsp.aerial_duels_offensive_won,
       bsp.aerial_duels_defensive,
       bsp.aerial_duels_defensive_won,

       bsp.ball_progression,
       bsp.ball_progression_complete,
       bsp.ball_progression_incomplete,

       bsp.corners,
       bsp.corners_long,
       bsp.corners_short,

       bsp.crosses,
       bsp.crosses_completed,
       bsp.crosses_incomplete,
       bsp.crosses_early,
       bsp.crosses_late,
       bsp.crosses_low,
       bsp.crosses_high,
       bsp.crosses_to_goal,
       bsp.crosses_to_attempt_at_goal,

       bsp.duels_total,
       bsp.duels_incomplete,
       bsp.duels_complete,
       bsp.duels_offensive,
       bsp.duels_offensive_won,
       bsp.duels_defensive,
       bsp.duels_defensive_won,
       bsp.duels_defensive_own_box,
       bsp.duels_defensive_own_box_won,
       bsp.duels_defensive_own_half,
       bsp.duels_defensive_own_half_won,
       bsp.duels_defensive_opponents_half,
       bsp.duels_defensive_opponents_half_won,
       bsp.duels_fifty_fifty,
       bsp.duels_sliding,

       bsp.ground_duels_offensive,
       bsp.ground_duels_offensive_won,
       bsp.ground_duels_defensive,
       bsp.ground_duels_defensive_won,

       bsp.events,
       bsp.events_successful,
       bsp.events_key,
       bsp.events_key_freekick,
       bsp.events_key_corner,
       bsp.events_inside_box,

       bsp.fouls_against,
       bsp.fouls_for,
       bsp.fouls_own_half,

       bsp.own_goals,
       bsp.goals,
       bsp.goals_scored,
       bsp.goals_conceded,

       bsp.goals_by_head,
       bsp.goals_by_penalty,
       bsp.goal_kicks_adv,

       bsp.involvement_in_attempt_at_goal,
       bsp.involvement_in_attempt_at_goal_xg,

       bsp.minutes_played,

       bsp.passes,
       bsp.passes_complete,
       bsp.passes_incomplete,
       bsp.passes_backward,
       bsp.passes_backward_complete,
       bsp.passes_forward,
       bsp.passes_forward_complete,
       bsp.passes_own_half,
       bsp.passes_opponents_half,
       bsp.passes_opponents_half_complete,
       bsp.passes_in_final_third,
       bsp.passes_in_final_third_complete,
       bsp.passes_short,
       bsp.passes_long,
       bsp.passes_long_complete,
       bsp.passes_long_incomplete,
       bsp.passes_wide,
       bsp.passes_wide_complete,
       bsp.passes_first_in_possession,
       bsp.passes_first_in_possession_forward,
       bsp.passes_into_box,
       bsp.passes_direct,
       bsp.passes_switch,
       bsp.passes_between_central_defenders,
       bsp.passes_key,

       bsp.offsides,
       bsp.offsides_adv,

       bsp.possessions_time,
       bsp.possessions_lost,
       bsp.possessions_lost_by_passes,
       bsp.possessions_lost_by_duel,
       bsp.possessions_regained_by_duel,
       bsp.possessions_regained_by_interception,
       bsp.possessions_regained_in_opponents_half,
       bsp.possession_opponents_half,

       bsp.attempts_at_goal,
       bsp.attempts_at_goal_on_target,
       bsp.attempts_at_goal_blocked,
       bsp.attempts_at_goal_header,
       bsp.attempts_at_goal_inside_the_penalty_area,
       bsp.attempts_at_goal_outside_the_penalty_area,
       bsp.attempts_at_goal_inside_the_penalty_area_on_target,
       bsp.attempts_at_goal_outside_the_penalty_area_on_target,
       bsp.attempts_at_goal_inside_the_penalty_area_scored,
       bsp.attempts_at_goal_outside_the_penalty_area_scored,

       bsp.attempts_on_target_saves,
       bsp.diving_saves,

       bsp.throw_ins_adv,
       bsp.throw_ins_keep_possession,

       bsp.xg_value,

       bsp.clearances,

       bsp.grade,
       bsp.total_xlocation,
       bsp.total_ylocation,

       bsp.interceptions_goalkeeper,
       bsp.keeper_throws_short,
       bsp.keeper_throws_long,

       bsp.assists,
       bsp.assists_adv,
       bsp.assists_by_free_kick,

       bsp.yellow_cards,
       bsp.yellow_cards_adv,
       bsp.yellow_red_cards,
       bsp.direct_red_cards,
       bsp.red_cards,
       bsp.red_cards_for_second_caution,

       bsp.penalties_faced,
       bsp.penalties_missed,
       bsp.penalties_saved,

       bsp.free_kicks_adv,
       bsp.free_kicks_scored,
       bsp.free_kicks_missed,
       bsp.free_kicks_on_goal,

       bsp.substituted_in,
       bsp.substituted_out,

       bsp.shots_on_target,
       bsp.shots_off_target,

       bsp.shots_blocked,
       bsp.corner_kicks,

       timestampdiff(year, p.birth_date, e.start_date)                 as age,
       p.height_inches,
       p.weight_lbs,
       p.nationality,
       p.preferred_foot

from api_european_football.box_score_player as bsp
         join api_european_football.event as e
              on e.id = bsp.event_id
         join api_european_football.league as l
              on e.league_id = l.id
         left join api_european_football.season as s
                   on s.id = e.season_id
         left join api_european_football.event_type as et
                   on e.type_id = et.id
         left join api_european_football.team as t
                   on bsp.team_id = t.id
         left join api_european_football.player as p
                   on bsp.player_id = p.id
         left join api_european_football.position as pos
                   on bsp.starting_position_id = pos.id
         left join api_european_football.did_not_play_type as dnpt
                   on bsp.did_not_play_type_id = dnpt.id
;


create or replace view soccer_pbpe as
select CAST(`s`.`season` AS SIGNED) AS `season`,
       LCASE(`et`.`name`)           AS `event_type`,
       `e`.`start_date`             AS `start_datetime`,
       `pbpe`.`pbp_event_date`      AS `pbpe_datetime`,
       `ep`.`event_id`              AS `event_id`,
       `ep`.`sequence`              AS `period_sequence`,
       `pbpe`.`period_type`         AS `period_type`,
       `pbpe`.`period_name`         AS `period_name`,
       `pbpe`.`id`                  AS `pbpe_id`,
       `pbpe`.`match_time`          AS `clock_minutes`,
       `pbpe`.`match_clock`         AS `clock_seconds`,
       `pbpe`.`stoppage_time`       AS `stoppage_time_minutes`,
       `pbpe`.`stoppage_time_clock` AS `stoppage_time_seconds`,
       `pbpe`.`attribution_id`      AS `team_id`,
       `pbpe`.`competitor`          AS `is_home`,
       `pbpe`.`home_score`,
       `pbpe`.`away_score`,
       `pbpe`.`description`         AS `description`,
       `pbpe`.`alt_description`     AS `alt_description`,
       `pbpe`.`event_type`          AS `pbpe_type`,
       `pbpe`.`x`                   AS `x_coordinate`,
       `pbpe`.`y`                   AS `y_coordinate`,
       `pbpe`.`outcome`             AS `shot_outcome`,
       `pbpe`.`method`              AS `scoring_method`,

       `pbpe`.`pass_style`          AS `pass_style`,
       `pbpe`.`pass_body`           AS `pass_body`,
       `pbpe`.`pass_outcome`        AS `pass_outcome`,
       `pbpe`.`pass_is_assist`      AS `pass_is_assist`,

       `pbpe`.`cross_style`         AS `cross_style`,
       `pbpe`.`cross_body`          AS `cross_body`,
       `pbpe`.`cross_outcome`       AS `cross_outcome`,
       `pbpe`.`cross_is_assist`     AS `cross_is_assist`,
       `pbpe`.`clearance_body`      AS `clearance_body`,
       `pbpe`.`control_type`        AS `control_type`,

       `pbpe`.`duel_type`           AS `duel_type`,
       `pbpe`.`duel_result`         AS `duel_result`,
       `pbpe`.`card_description`    AS `card_description`

from api_european_football.play_by_play_event as pbpe
         join api_european_football.event_period as ep on ep.id = pbpe.period_id
         join api_european_football.event as e on ep.event_id = e.id
         join api_european_football.season as s on e.season_id = s.id
         join api_european_football.league as l on e.league_id = l.id
         join api_european_football.event_type as et on e.type_id = et.id
;
