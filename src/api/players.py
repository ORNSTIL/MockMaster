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

@router.get("/search/")
def search_players(
    player_name: str = "",
    position: str = "",
    team: str = "",
    search_page: str = "",
    sort_col: str = "ppr_fantasy_points",
    sort_order: str = "desc"
):
    offset = (int(search_page)-1)*10 if search_page else 0

    # Ensure sort_col is prefixed with the appropriate table name if needed
    if sort_col in ["player_name", "player_id"]:  # Assuming these are from the 'players' table
        order_clause = f"players.{sort_col} {sort_order.upper()}"
    else:  # Assuming other columns are from the 'stats' table
        order_clause = f"stats.{sort_col} {sort_order.upper()}"

    where_clauses = []
    if player_name:
        where_clauses.append("players.player_name ILIKE :player_name")
    if position:
        where_clauses.append("stats.position ILIKE :position")
    if team:
        where_clauses.append("stats.team ILIKE :team")

    where_statement = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    sql = f"""
        SELECT players.player_id, players.player_name, stats.position, stats.team, stats.age, 
               stats.fantasy_points_standard_10, stats.fantasy_points_ppr_10
        FROM players
        JOIN stats ON players.player_id = stats.player_id
        WHERE {where_statement}
        ORDER BY {order_clause}
        LIMIT 11 OFFSET :offset
    """
    
    params = {
        'offset': offset,
        'player_name': f"%{player_name}%" if player_name else None,
        'position': f"%{position}%" if position else None,
        'team': f"%{team}%" if team else None
    }

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql), params).fetchall()
        json = []
        # Handle pagination
        if len(result) > 10:
            result = result[:10]
            next_token = str(int(search_page) + 1 if search_page else 2)
        else:
            next_token = ""
        # Build response
        for row in result:
            json.append({
                "player_id": row.player_id,
                "player_name": row.player_name,
                "position": row.position,
                "team": row.team,
                "age": row.age,
                "standard_fantasy_points": row.fantasy_points_standard_10 / 10,
                "ppr_fantasy_points": row.fantasy_points_ppr_10 / 10
            })

    return {
        "previous": search_page if int(search_page or 0) > 1 else "",
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
