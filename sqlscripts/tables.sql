create table mlb_pregame_odds
(

id 					varchar(255),
sportsbook		 	varchar(50),
market				varchar(50),
name				varchar(50),
is_main				varchar(50),
selection			varchar(100),
normalized_selection	varchar(100),
market_id			varchar(100),
selection_line		varchar(50),
player_id			varchar(50),
team_id				varchar(50),
price				float,
timestamp			float,
grouping_key		varchar(50),
points				float,
game_id				varchar(75),
updated_at        timestamp default current_timestamp() on update current_timestamp(),
primary key (game_id, sportsbook, market, name)
)
collate utf8mb3_general_ci
;

create table mlb_live_odds
(

id 					varchar(255),
sportsbook		 	varchar(50),
market				varchar(50),
name				varchar(50),
is_main				varchar(50),
selection			varchar(100),
normalized_selection	varchar(100),
market_id			varchar(100),
selection_line		varchar(50),
player_id			varchar(50),
team_id				varchar(50),
price				float,
timestamp			float,
grouping_key		varchar(50),
points				float,
game_id				varchar(75),
updated_at        timestamp default current_timestamp() on update current_timestamp(),
primary key (game_id, sportsbook, market, name)
)
collate utf8mb3_general_ci
;