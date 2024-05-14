-- Part 1: Schema for database initialization
create table
  public.drafts (
    draft_id bigint generated by default as identity,
    created_at timestamp with time zone null default (now() at time zone 'utc'::text),
    draft_name text null,
    draft_type text null,
    roster_size integer null,
    draft_size integer null,
    draft_length integer null,
    flex_spots integer null,
    draft_status text null default 'pending'::text,
    constraint drafts_pkey primary key (draft_id),
    constraint drafts_draft_id_key unique (draft_id)
  ) tablespace pg_default;

create table
  public.position_requirements (
    draft_id bigint generated by default as identity,
    position text not null,
    min integer null,
    max integer null,
    constraint position_requirements_pkey primary key (draft_id, "position"),
    constraint position_requirements_draft_id_fkey foreign key (draft_id) references drafts (draft_id)
  ) tablespace pg_default;

create table
  public.teams (
    team_id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    team_name text null,
    user_name text null,
    draft_position integer null,
    draft_id bigint null,
    constraint teams_pkey primary key (team_id),
    constraint teams_id_key unique (team_id),
    constraint teams_draft_id_fkey foreign key (draft_id) references drafts (draft_id)
  ) tablespace pg_default;

create table
  public.players (
    player_name text null,
    player_id text not null,
    constraint players_pkey primary key (player_id),
    constraint players_player_id2_key unique (player_id)
  ) tablespace pg_default;

create table
  public.stats (
    player_id text not null,
    year integer not null,
    age integer null,
    position text null,
    team text null,
    games_played integer null,
    games_started integer null,
    passing_yards integer null,
    passing_tds integer null,
    interceptions integer null,
    rushing_atts integer null,
    rushing_yards integer null,
    targets integer null,
    receptions integer null,
    receiving_yards integer null,
    receiving_tds integer null,
    fumbles integer null,
    fumbles_lost integer null,
    two_point_conversions integer null,
    fantasy_points_standard_10 integer null,
    fantasy_points_ppr_10 integer null,
    rushing_tds integer null,
    two_point_conversions_passing integer null,
    constraint stats_pkey primary key (player_id, year),
    constraint stats_player_id_fkey foreign key (player_id) references players (player_id)
  ) tablespace pg_default;

create table
  public.selections (
    team_id bigint not null,
    player_id text not null,
    when_selected integer null,
    constraint selections_pkey primary key (team_id, player_id),
    constraint selections_player_id_fkey foreign key (player_id) references players (player_id),
    constraint selections_team_id_fkey foreign key (team_id) references teams (team_id)
  ) tablespace pg_default;

-- Part 2: Populating initial player data in database (if using local database)
-- 1) Navigate to your localhost instance of Supabase 
-- 2) Click on the "players" table
-- 3) Click "Insert" and "Import" data from CSV 
-- 4) Use "2023_players.csv" file from the data folder of the repository
-- 5) Click "Import Data"
-- 6) Click on the "stats" table
-- 7) Click "Insert" and "Import" data from CSV 
-- 8) Use "2023_stats.csv" file from the data folder of the repository
-- 9) Click "Import Data"
-- Now your local database will have all the necassary fantasy football player data for the 2023 season