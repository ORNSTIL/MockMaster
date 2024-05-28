from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel
from enum import Enum
import sqlalchemy
from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/players",
    tags=["players"],
    dependencies=[Depends(auth.get_api_key)],
)

class SearchPlayersResponse(BaseModel):
    previous: str
    next: str
    results: list[dict]

class PlayerStatisticsResponse(BaseModel):
    player_id: str
    seasons: list[dict]

class DraftPlayerRequest(BaseModel):
    team_id: int

class search_sort_options(str, Enum):
    player_name = "player_name"
    position = "position"
    team = "team"
    age = "age"
    standard_fantasy_points = "standard_fantasy_points"
    ppr_fantasy_points = "ppr_fantasy_points"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/search/", response_model=SearchPlayersResponse)
def search_players(
    player_name: str = "",
    position: str = "",
    team: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.ppr_fantasy_points,
    sort_order: search_sort_order = search_sort_order.desc
):
    """
    Gets results according to specified search parameters and sort options. 
    Provides player_id, player_name, position, team, age, standard_fantasy_points, and ppr_fantasy_points for each result.
    """
    # set which page of results to get
    if search_page == "":
        offset = 0
        prev_token = ""
    else:
        offset = (int(search_page)-1)*10
        if offset == 0:
            prev_token = ""
        else:
            prev_token = str(int(search_page)-1)

    # set sort order
    if sort_col is search_sort_options.player_name:
        if sort_order is search_sort_order.asc:
            order_by = db.players.c.player_name
        else:
            order_by = sqlalchemy.desc(db.players.c.player_name)
    elif sort_col is search_sort_options.position:
        if sort_order is search_sort_order.asc:
            order_by = db.stats.c.position
        else:
            order_by = sqlalchemy.desc(db.stats.c.position)
    elif sort_col is search_sort_options.team:
        if sort_order is search_sort_order.asc:
            order_by = db.stats.c.team
        else:
            order_by = sqlalchemy.desc(db.stats.c.team)
    elif sort_col is search_sort_options.age:
        if sort_order is search_sort_order.asc:
            order_by = db.stats.c.age
        else:
            order_by = sqlalchemy.desc(db.stats.c.age)
    elif sort_col is search_sort_options.standard_fantasy_points:
        if sort_order is search_sort_order.asc:
            order_by = db.stats.c.fantasy_points_standard_10
        else:
            order_by = sqlalchemy.desc(db.stats.c.fantasy_points_standard_10)
    elif sort_col is search_sort_options.ppr_fantasy_points:
        if sort_order is search_sort_order.asc:
            order_by = db.stats.c.fantasy_points_ppr_10
        else:
            order_by = sqlalchemy.desc(db.stats.c.fantasy_points_ppr_10)
    else:
        raise HTTPException(status_code=400, detail="Invalid sort column specified")

    # set sqlalchemy statement using query builder
    stmt = (
        sqlalchemy
        .select(
            db.players.c.player_id,
            db.players.c.player_name,
            db.stats.c.position,
            db.stats.c.team,
            db.stats.c.age,
            db.stats.c.fantasy_points_standard_10,
            db.stats.c.fantasy_points_ppr_10
        )
        .select_from(
            db.players
            .join(db.stats, db.players.c.player_id == db.stats.c.player_id)
        )
        .limit(11)
        .offset(offset)
        .order_by(order_by)
    )

    # add filter if strings were specified
    if player_name != "":
        stmt = stmt.where(db.players.c.player_name.ilike(f"%{player_name}%"))
    if position != "":
        stmt = stmt.where(db.stats.c.position.ilike(f"%{position}%"))
    if team != "":
        stmt = stmt.where(db.stats.c.team.ilike(f"%{team}%"))

    with db.engine.begin() as connection:
        result = connection.execute(stmt).fetchall()
        json = []
        # set next page token
        if len(result) > 10:
            result = result[0:10]
            if search_page == "":
                next_token = "2"
            else:
                next_token = str(int(search_page)+1)
        else:
            next_token = ""
        # create search result entries for page
        for row in result:
            json.append(
                {
                    "player_id": row.player_id,
                    "player_name": row.player_name,
                    "position": row.position,
                    "team": row.team,
                    "age": row.age,
                    "standard_fantasy_points": row.fantasy_points_standard_10/10,
                    "ppr_fantasy_points": row.fantasy_points_ppr_10/10
                }
            )

        search_result = {"previous": prev_token, "next": next_token, "results": json}

    print(search_result)

    return search_result


@router.get("/{player_id}/", response_model=PlayerStatisticsResponse)
def get_player_statistics(player_id: str):
    """
    Gets all player statistics for all seasons for the specified player.
    """
    with db.engine.begin() as connection:
        stats = connection.execute(sqlalchemy.text("""
            SELECT player_id, year, age, position, team, games_played, games_started,
                   passing_yards, passing_tds, interceptions, rushing_atts, rushing_yards,
                   targets, receptions, receiving_yards, receiving_tds, fumbles, fumbles_lost,
                   two_point_conversions, fantasy_points_standard_10, fantasy_points_ppr_10,
                   rushing_tds, two_point_conversions_passing
            FROM stats
            WHERE player_id = :player_id"""), {'player_id': player_id}).mappings()

        # create list of season statistics
        seasons = []
        for season in stats:
            seasons.append({
                'year': season.year,
                'age': season.age,
                'position': season.position,
                'team': season.team,
                'games_played': season.games_played,
                'games_started': season.games_started,
                'passing_yards': season.passing_yards,
                'passing_tds': season.passing_tds,
                'interceptions': season.interceptions,
                'rushing_atts': season.rushing_atts,
                'rushing_yards': season.rushing_yards,
                'rushing_tds': season.rushing_tds,
                'targets': season.targets,
                'receptions': season.receptions,
                'receiving_yards': season.receiving_yards,
                'receiving_tds': season.receiving_tds,
                'fumbles': season.fumbles,
                'fumbles_lost': season.fumbles_lost,
                'two_point_conversions_passing': season.two_point_conversions_passing,
                'two_point_conversions': season.two_point_conversions,
                'fantasy_points_standard_10': season.fantasy_points_standard_10 / 10,
                'fantasy_points_ppr_10': season.fantasy_points_ppr_10 / 10
            })

        # if no player statistics are found
        if len(seasons) <= 0:
            raise HTTPException(status_code=404, detail="Player statistics not found")

        player_statistics = {"player_id": player_id, "seasons": seasons}

    print(player_statistics)

    return {"player_id": player_id, "seasons": seasons}


@router.post("/{player_id}/draft")
def draft_player(player_id: str, request: DraftPlayerRequest):
    with db.engine.begin() as connection:
        # update database with draft selection
        try:
            connection.execute(sqlalchemy.text("""
                WITH previousPicks AS (
                SELECT COUNT(*) AS picks
                FROM selections
                JOIN teams ON selections.team_id = teams.team_id
                JOIN drafts ON teams.draft_id = drafts.draft_id
                WHERE teams.draft_id = (
                    SELECT teams.draft_id
                    FROM teams
                    WHERE teams.team_id = :team_id
                )
                )
                INSERT INTO selections (team_id, player_id, when_selected)
                SELECT :team_id, :player_id, picks+1
                FROM previousPicks;"""), 
                {'team_id': request.team_id, 'player_id': player_id})

            return "OK"
        # if the player is already drafted or the team is not found
        except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=409, detail="Player already drafted or team not found")
