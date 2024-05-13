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

class PlayerStatsResponse(BaseModel):
    player_stats: dict

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

@router.get("/search/")
def search_players(
    player_name: str = "",
    position: str = "",
    team: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.ppr_fantasy_points,
    sort_order: search_sort_order = search_sort_order.desc
):
    
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
        assert False

    # set sqlalchemy statement
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

    # filter only if player_name parameter and/or position paramater are passed
    if player_name != "":
        stmt = stmt.where(db.players.c.player_name.ilike(f"%{player_name}%"))
    if position != "":
        stmt = stmt.where(db.stats.c.position.ilike(f"%{position}%"))
    if team != "":
        stmt = stmt.where(db.stats.c.team.ilike(f"%{team}%"))

    # connect to database
    with db.engine.begin() as connection:
        result = connection.execute(stmt).fetchall()
        json = []
        # set next page
        if len(result) > 10:
            result = result[0:10]
            if search_page == "":
                next_token = "2"
            else:
                next_token = str(int(search_page)+1)
        else:
            next_token = ""
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

    # return search object
    return {
        "previous": prev_token,
        "next": next_token,
        "results": json
    }

@router.get("/{player_id}/", response_model=PlayerStatsResponse)
def get_player_statistics(player_id: str):
    with db.engine.begin() as connection:
        # query database
        stats = connection.execute(sqlalchemy.text("""
            SELECT player_id, year, age, position, team, games_played, games_started,
                   passing_yards, passing_tds, interceptions, rushing_atts, rushing_yards,
                   targets, receptions, receiving_yards, receiving_tds, fumbles, fumbles_lost,
                   two_point_conversions, fantasy_points_standard_10, fantasy_points_ppr_10,
                   rushing_tds, two_point_conversions_passing
            FROM stats
            WHERE player_id = :player_id
        """), {'player_id': player_id}).mappings().fetchall()
        
        # if no player statistics are found
        if not stats:
            raise HTTPException(status_code=404, detail="Player statistics not found")

        # format returned stats
        formatted_stats = [{
            'player_id': row['player_id'],
            'year': row['year'],
            'age': row['age'],
            'position': row['position'],
            'team': row['team'],
            'games_played': row['games_played'],
            'games_started': row['games_started'],
            'passing_yards': row['passing_yards'],
            'passing_tds': row['passing_tds'],
            'interceptions': row['interceptions'],
            'rushing_atts': row['rushing_atts'],
            'rushing_yards': row['rushing_yards'],
            'targets': row['targets'],
            'receptions': row['receptions'],
            'receiving_yards': row['receiving_yards'],
            'receiving_tds': row['receiving_tds'],
            'fumbles': row['fumbles'],
            'fumbles_lost': row['fumbles_lost'],
            'two_point_conversions': row['two_point_conversions'],
            'fantasy_points_standard_10': row['fantasy_points_standard_10'] / 10,
            'fantasy_points_ppr_10': row['fantasy_points_ppr_10'] / 10,
            'rushing_tds': row['rushing_tds'],
            'two_point_conversions_passing': row['two_point_conversions_passing']
        } for row in stats]

        # print formatted_stats for testing
        print(f"Statistics : {formatted_stats}")

        # return formatted_stats
        return {"player_stats": {"history": formatted_stats}}

@router.post("/{player_id}/draft")
def draft_player(player_id: str, request: DraftPlayerRequest):
    with db.engine.begin() as connection:
        # update database with draft selection
        try:
            connection.execute(sqlalchemy.text("""
                INSERT INTO selections (team_id, player_id, when_selected)
                VALUES (:team_id, :player_id, EXTRACT(EPOCH FROM NOW()))"""), 
                {'team_id': request.team_id, 'player_id': player_id})

            return "OK"
        # if the player is already drafted or the team is not found
        except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=409, detail="Player already drafted or team not found")
