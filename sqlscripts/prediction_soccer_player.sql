use ai;

create table prediction_soccer_player
(
    event_league_abbr varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    starter           bool,
    position          varchar(50),
    shots             float,
    goals             float,
    assists           float,
    shots_params      json check (json_valid(shots_params)),
    shots_bins        json check (json_valid(shots_bins)),
    goals_params      json check (json_valid(goals_params)),
    goals_bins        json check (json_valid(goals_bins)),
    assists_params    json check (json_valid(assists_params)),
    assists_bins      json check (json_valid(assists_bins)),

    updated_at        timestamp default current_timestamp() on update current_timestamp(),

    shots_model_id    varchar(50),
    goals_model_id    varchar(50),
    assists_model_id  varchar(50),
    primary key (event_id, player_id)
)
    collate = utf8mb3_general_ci
;


alter table prediction_soccer_player

    add shots_on_target                               float after assists,
    add shots_off_target                              float after shots_on_target,
    add shots_blocked                                 float after shots_off_target,
    add clearances                                    float after shots_blocked,
    add possessions_regained_by_interception          float after clearances,
    add duels_offensive_won                           float after possessions_regained_by_interception,
    add duels_defensive_won                           float after duels_offensive_won,
    add crosses_to_attempt_at_goal                    float after duels_defensive_won,
    add fouls_for                                     float after crosses_to_attempt_at_goal,
    add fouls_against                                 float after fouls_for,
    add passes_complete                               float after fouls_against,
    add crosses_completed                             float after passes_complete,
    add yellow_cards                                  float after crosses_completed,
    add red_cards                                     float after yellow_cards,
    add own_goals                                     float after red_cards,
    add shots_on_target_params                        json check ( json_valid(shots_on_target_params) ),
    add shots_on_target_bins                          json check ( json_valid(shots_on_target_bins) ),
    add shots_off_target_params                       json check ( json_valid(shots_off_target_params) ),
    add shots_off_target_bins                         json check ( json_valid(shots_off_target_bins) ),
    add shots_blocked_params                          json check ( json_valid(shots_blocked_params) ),
    add shots_blocked_bins                            json check ( json_valid(shots_blocked_bins) ),
    add clearances_params                             json check ( json_valid(clearances_params) ),
    add clearances_bins                               json check ( json_valid(clearances_bins) ),
    add possessions_regained_by_interception_params   json check ( json_valid(possessions_regained_by_interception_params) ),
    add possessions_regained_by_interception_bins     json check ( json_valid(possessions_regained_by_interception_bins) ),
    add duels_offensive_won_params                    json check ( json_valid(duels_offensive_won_params) ),
    add duels_offensive_won_bins                      json check ( json_valid(duels_offensive_won_bins) ),
    add duels_defensive_won_params                    json check ( json_valid(duels_defensive_won_params) ),
    add duels_defensive_won_bins                      json check ( json_valid(duels_defensive_won_bins) ),
    add crosses_to_attempt_at_goal_params             json check ( json_valid(crosses_to_attempt_at_goal_params) ),
    add crosses_to_attempt_at_goal_bins               json check ( json_valid(crosses_to_attempt_at_goal_bins) ),
    add fouls_for_params                              json check ( json_valid(fouls_for_params) ),
    add fouls_for_bins                                json check ( json_valid(fouls_for_bins) ),
    add fouls_against_params                          json check ( json_valid(fouls_against_params) ),
    add fouls_against_bins                            json check ( json_valid(fouls_against_bins) ),
    add passes_complete_params                        json check ( json_valid(passes_complete_params) ),
    add passes_complete_bins                          json check ( json_valid(passes_complete_bins) ),
    add crosses_completed_params                      json check ( json_valid(crosses_completed_params) ),
    add crosses_completed_bins                        json check ( json_valid(crosses_completed_bins) ),
    add yellow_cards_params                           json check ( json_valid(yellow_cards_params) ),
    add yellow_cards_bins                             json check ( json_valid(yellow_cards_bins) ),
    add red_cards_params                              json check ( json_valid(red_cards_params) ),
    add red_cards_bins                                json check ( json_valid(red_cards_bins) ),
    add own_goals_params                              json check ( json_valid(own_goals_params) ),
    add own_goals_bins                                json check ( json_valid(own_goals_bins) ),

    add shots_on_target_model_id                      varchar(50),
    add shots_off_target_model_id                     varchar(50),
    add shots_blocked_model_id                        varchar(50),
    add clearances_model_id                           varchar(50),
    add possessions_regained_by_interception_model_id varchar(50),
    add duels_offensive_won_model_id                  varchar(50),
    add duels_defensive_won_model_id                  varchar(50),
    add crosses_to_attempt_at_goal_model_id           varchar(50),
    add fouls_for_model_id                            varchar(50),
    add fouls_against_model_id                        varchar(50),
    add passes_complete_model_id                      varchar(50),
    add crosses_completed_model_id                    varchar(50),
    add yellow_cards_model_id                         varchar(50),
    add red_cards_model_id                            varchar(50),
    add own_goals_model_id                            varchar(50)
;


alter table prediction_soccer_player

    add goals_by_penalty          float,
    add penalties_saved           float,
    add goals_by_penalty_params   json check ( json_valid(goals_by_penalty_params) ),
    add goals_by_penalty_bins     json check ( json_valid(goals_by_penalty_bins) ),
    add penalties_saved_params    json check ( json_valid(penalties_saved_params) ),
    add penalties_saved_bins      json check ( json_valid(penalties_saved_bins) ),
    add goals_by_penalty_model_id varchar(50),
    add penalties_saved_model_id  varchar(50)
;

alter table prediction_soccer_player
    modify goals_by_penalty float null after own_goals;

alter table prediction_soccer_player
    modify penalties_saved float null after goals_by_penalty;

alter table prediction_soccer_player
    modify goals_by_penalty_params longtext collate utf8mb4_bin null check (json_valid(`goals_by_penalty_params`)) after own_goals_bins;

alter table prediction_soccer_player
    modify goals_by_penalty_bins longtext collate utf8mb4_bin null check (json_valid(`goals_by_penalty_bins`)) after goals_by_penalty_params;

alter table prediction_soccer_player
    modify penalties_saved_params longtext collate utf8mb4_bin null check (json_valid(`penalties_saved_params`)) after goals_by_penalty_bins;

alter table prediction_soccer_player
    modify penalties_saved_bins longtext collate utf8mb4_bin null check (json_valid(`penalties_saved_bins`)) after penalties_saved_params;



create table prediction_soccer_player_candidate_shots
(
    event_league_abbr varchar(50),
    model_id          varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    shots             float,
    shots_params      json check (json_valid(shots_params)),
    updated_at        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;


create table prediction_soccer_player_candidate_goals
(
    event_league_abbr varchar(50),
    model_id          varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    goals             float,
    goals_params      json check (json_valid(goals_params)),
    updated_at        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_assists
(
    event_league_abbr varchar(50),
    model_id          varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    assists           float,
    assists_params    json check (json_valid(assists_params)),
    updated_at        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;


create table prediction_soccer_player_candidate_shots_on_target
(
    event_league_abbr      varchar(50),
    model_id               varchar(50),
    event_id               int,
    team_id                int,
    player_id              int,
    shots_on_target        float,
    shots_on_target_params json check (json_valid(shots_on_target_params)),
    updated_at             timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;


create table prediction_soccer_player_candidate_shots_off_target
(
    event_league_abbr       varchar(50),
    model_id                varchar(50),
    event_id                int,
    team_id                 int,
    player_id               int,
    shots_off_target        float,
    shots_off_target_params json check (json_valid(shots_off_target_params)),
    updated_at              timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_shots_blocked
(
    event_league_abbr    varchar(50),
    model_id             varchar(50),
    event_id             int,
    team_id              int,
    player_id            int,
    shots_blocked        float,
    shots_blocked_params json check (json_valid(shots_blocked_params)),
    updated_at           timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_clearances
(
    event_league_abbr varchar(50),
    model_id          varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    clearances        float,
    clearances_params json check (json_valid(clearances_params)),
    updated_at        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;


# create table prediction_soccer_player_candidate_possessions_regained_by_interception
create table prediction_soccer_player_candidate_possessions_regained_by_int
(
    event_league_abbr                           varchar(50),
    model_id                                    varchar(50),
    event_id                                    int,
    team_id                                     int,
    player_id                                   int,
    possessions_regained_by_interception        float,
    possessions_regained_by_interception_params json check (json_valid(possessions_regained_by_interception_params)),
    updated_at                                  timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_duels_offensive_won
(
    event_league_abbr          varchar(50),
    model_id                   varchar(50),
    event_id                   int,
    team_id                    int,
    player_id                  int,
    duels_offensive_won        float,
    duels_offensive_won_params json check (json_valid(duels_offensive_won_params)),
    updated_at                 timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_duels_defensive_won
(
    event_league_abbr          varchar(50),
    model_id                   varchar(50),
    event_id                   int,
    team_id                    int,
    player_id                  int,
    duels_defensive_won        float,
    duels_defensive_won_params json check (json_valid(duels_defensive_won_params)),
    updated_at                 timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_crosses_to_attempt_at_goal
(
    event_league_abbr                 varchar(50),
    model_id                          varchar(50),
    event_id                          int,
    team_id                           int,
    player_id                         int,
    crosses_to_attempt_at_goal        float,
    crosses_to_attempt_at_goal_params json check (json_valid(crosses_to_attempt_at_goal_params)),
    updated_at                        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_fouls_for
(
    event_league_abbr varchar(50),
    model_id          varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    fouls_for         float,
    fouls_for_params  json check (json_valid(fouls_for_params)),
    updated_at        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_fouls_against
(
    event_league_abbr    varchar(50),
    model_id             varchar(50),
    event_id             int,
    team_id              int,
    player_id            int,
    fouls_against        float,
    fouls_against_params json check (json_valid(fouls_against_params)),
    updated_at           timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_passes_complete
(
    event_league_abbr      varchar(50),
    model_id               varchar(50),
    event_id               int,
    team_id                int,
    player_id              int,
    passes_complete        float,
    passes_complete_params json check (json_valid(passes_complete_params)),
    updated_at             timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_crosses_completed
(
    event_league_abbr        varchar(50),
    model_id                 varchar(50),
    event_id                 int,
    team_id                  int,
    player_id                int,
    crosses_completed        float,
    crosses_completed_params json check (json_valid(crosses_completed_params)),
    updated_at               timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_yellow_cards
(
    event_league_abbr   varchar(50),
    model_id            varchar(50),
    event_id            int,
    team_id             int,
    player_id           int,
    yellow_cards        float,
    yellow_cards_params json check (json_valid(yellow_cards_params)),
    updated_at          timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_red_cards
(
    event_league_abbr varchar(50),
    model_id          varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    red_cards         float,
    red_cards_params  json check (json_valid(red_cards_params)),
    updated_at        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_own_goals
(
    event_league_abbr varchar(50),
    model_id          varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    own_goals         float,
    own_goals_params  json check (json_valid(own_goals_params)),
    updated_at        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_goals_by_penalty
(
    event_league_abbr varchar(50),
    model_id          varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    goals_by_penalty               float,
    goals_by_penalty_params        json check (json_valid(goals_by_penalty_params)),
    updated_at        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;


create table prediction_soccer_player_candidate_penalties_saved
(
    event_league_abbr varchar(50),
    model_id          varchar(50),
    event_id          int,
    team_id           int,
    player_id         int,
    penalties_saved               float,
    penalties_saved_params        json check (json_valid(penalties_saved_params)),
    updated_at        timestamp default current_timestamp() on update current_timestamp(),
    primary key (model_id, event_id, player_id)
)
    collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_first_goalscorer
(
     event_league_abbr varchar(50),
     model_id          varchar(50),
     event_id          int,
     team_id           int,
     player_id         int,
     first_goalscorer               float,
     first_goalscorer_params        json check (json_valid(first_goalscorer_params)),
     updated_at        timestamp default current_timestamp() on update current_timestamp(),
     is_active         tinyint(1) default 1                 null,
     primary key (model_id, event_id, player_id)
)
     collate = utf8mb3_general_ci
;

create table prediction_soccer_player_candidate_last_goalscorer
(
     event_league_abbr varchar(50),
     model_id          varchar(50),
     event_id          int,
     team_id           int,
     player_id         int,
     last_goalscorer               float,
     last_goalscorer_params        json check (json_valid(last_goalscorer_params)),
     updated_at        timestamp default current_timestamp() on update current_timestamp(),
     is_active         tinyint(1) default 1                 null,
     primary key (model_id, event_id, player_id)
)
     collate = utf8mb3_general_ci
;

# create table prediction_soccer_player_candidate_xxx
# (
#     event_league_abbr varchar(50),
#     model_id          varchar(50),
#     event_id          int,
#     team_id           int,
#     player_id         int,
#     xxx               float,
#     xxx_params        json check (json_valid(xxx_params)),
#     updated_at        timestamp default current_timestamp() on update current_timestamp(),
#     primary key (model_id, event_id, player_id)
# )
#     collate = utf8mb3_general_ci
# ;
