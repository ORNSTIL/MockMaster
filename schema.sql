-- Part 1: Schema for database initialization
create table
  public.drafts (
    draft_id bigint generated by default as identity,
    created_at timestamp with time zone not null default (now() at time zone 'utc'::text),
    draft_name text not null,
    draft_type text not null,
    roster_size integer not null,
    draft_size integer not null,
    draft_status text not null default 'pending'::text,
    constraint drafts_pkey primary key (draft_id),
    constraint drafts_draft_id_key unique (draft_id)
  ) tablespace pg_default;

create table
  public.position_requirements (
    draft_id bigint not null,
    position text not null,
    min integer not null,
    max integer not null,
    constraint position_requirements_pkey primary key (draft_id, "position"),
    constraint position_requirements_draft_id_fkey foreign key (draft_id) references drafts (draft_id)
  ) tablespace pg_default;

create table
  public.teams (
    team_id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    team_name text not null,
    user_name text not null,
    draft_position integer null,
    draft_id bigint not null,
    constraint teams_pkey primary key (team_id),
    constraint teams_id_key unique (team_id),
    constraint teams_draft_id_fkey foreign key (draft_id) references drafts (draft_id)
  ) tablespace pg_default;

create table
  public.players (
    player_name text not null,
    player_id text not null,
    constraint players_pkey primary key (player_id),
    constraint players_player_id2_key unique (player_id)
  ) tablespace pg_default;

create table
  public.stats (
    player_id text not null,
    year integer not null,
    age integer not null,
    position text not null,
    team text not null,
    games_played integer not null,
    games_started integer not null,
    passing_yards integer not null,
    passing_tds integer not null,
    interceptions integer not null,
    rushing_atts integer not null,
    rushing_yards integer not null,
    rushing_tds integer not null,
    targets integer not null,
    receptions integer not null,
    receiving_yards integer not null,
    receiving_tds integer not null,
    fumbles integer not null,
    fumbles_lost integer not null,
    two_point_conversions integer not null,
    two_point_conversions_passing integer not null,
    fantasy_points_standard_10 integer not null,
    fantasy_points_ppr_10 integer not null,
    constraint stats_pkey primary key (player_id, year),
    constraint stats_player_id_fkey foreign key (player_id) references players (player_id)
  ) tablespace pg_default;

create table
  public.selections (
    team_id bigint not null,
    player_id text not null,
    when_selected integer not null,
    constraint selections_pkey primary key (team_id, player_id),
    constraint selections_player_id_fkey foreign key (player_id) references players (player_id),
    constraint selections_team_id_fkey foreign key (team_id) references teams (team_id)
  ) tablespace pg_default;

-- Part 2: Populating initial player data
-- 1) Navigate to your instance of Supabase 
-- 2) Click on the "players" table
-- 3) Click "Insert" and "Import" data from CSV 
-- 4) Use "players.csv" file from the data folder of the repository
-- 5) Click "Import Data"
-- 6) Click on the "stats" table
-- 7) Click "Insert" and "Import" data from CSV 
-- 8) Use "stats.csv" file from the data folder of the repository
-- 9) Click "Import Data"
-- Now your local database will have all the necassary fantasy football player data for the 2019-2023 seasons

-- Part 3: Creating the materialized views. 

-- Creating the materialized view for search players endpoint. 
-- NOTE: Once the initial data is imported, the materialized view never needs to be updated.
create materialized view
  public.player_points as
select
  players.player_id,
  players.player_name,
  stats.year,
  stats."position",
  stats.team,
  stats.age,
  stats.fantasy_points_standard_10,
  stats.fantasy_points_ppr_10
from
  stats
  join players on stats.player_id = players.player_id;

-- Creating the materialized view for draft players endpoint. 
-- NOTE: Once the initial data is imported, the materialized view never needs to be updated.
create materialized view
  public.player_positions as
select distinct
  stats.player_id,
  stats."position",
  players.player_name
from
  stats
  join players on players.player_id = stats.player_id
where
  stats.year = 2023;