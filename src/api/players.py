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
        draft_info = connection.execute(sqlalchemy.text("""
            SELECT teams.draft_id, drafts.draft_status, teams.draft_position, drafts.roster_size FROM teams
            JOIN drafts ON teams.draft_id = drafts.draft_id
            WHERE teams.team_id = :team_id
        """), {'team_id': request.team_id}).mappings().fetchone()

        if not draft_info:
            raise HTTPException(status_code=404, detail="Team not found")

        if draft_info['draft_status'] != 'active':
            raise HTTPException(status_code=409, detail="Draft not active")
        
        try:
            player_position = connection.execute(sqlalchemy.text("""
                SELECT position FROM stats WHERE player_id = :player_id
            """), {'player_id': player_id}).scalar_one()

        except:
            raise HTTPException(status_code=404, detail="Player not found")

        already_drafted = connection.execute(sqlalchemy.text("""
            SELECT EXISTS (
                SELECT 1 FROM selections
                JOIN teams ON selections.team_id = teams.team_id
                WHERE teams.draft_id = :draft_id AND selections.player_id = :player_id
            )
        """), {'draft_id': draft_info['draft_id'], 'player_id': player_id}).scalar_one()

        if already_drafted:
            raise HTTPException(status_code=409, detail="Player already drafted in this draft")

        previous_picks = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM selections
            JOIN teams ON selections.team_id = teams.team_id
            WHERE teams.draft_id = :draft_id
        """), {'draft_id': draft_info['draft_id']}).scalar_one()

        number_of_teams = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM teams
            WHERE draft_id = :draft_id
        """), {'draft_id': draft_info['draft_id']}).scalar_one()

        last_round = previous_picks // number_of_teams
        if last_round % 2 == 1:
            current_pick = number_of_teams - (previous_picks % number_of_teams)
        else:
            current_pick = (previous_picks % number_of_teams) + 1

        if current_pick != draft_info['draft_position']:
            raise HTTPException(status_code=403, detail="Not your turn to draft")
        
        total_selections = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM selections
            WHERE team_id = :team_id
        """), {'team_id': request.team_id}).scalar_one()
        remaining_picks = draft_info['roster_size'] - total_selections

        positions_needed = {}
        total_needed_picks = 0
        positions = connection.execute(sqlalchemy.text("""
            SELECT position, min FROM position_requirements
            WHERE draft_id = :draft_id
        """), {'draft_id': draft_info['draft_id']}).mappings().fetchall()
        
        for pos in positions:
            count = connection.execute(sqlalchemy.text("""
                SELECT COUNT(*) FROM selections
                JOIN stats ON selections.player_id = stats.player_id
                WHERE selections.team_id = :team_id AND stats.position = :position
            """), {'team_id': request.team_id, 'position': pos['position']}).scalar_one()
 
            needed = max(0, pos['min'] - count)
            positions_needed[pos['position']] = needed
            total_needed_picks += needed

        current_count = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM selections
            JOIN stats ON selections.player_id = stats.player_id
            WHERE selections.team_id = :team_id AND stats.position = :position
        """), {'team_id': request.team_id, 'position': player_position}).scalar_one()

        max_allowed = connection.execute(sqlalchemy.text("""
            SELECT max FROM position_requirements
            WHERE draft_id = :draft_id AND position = :position
        """), {'draft_id': draft_info['draft_id'], 'position': player_position}).scalar_one()

        if total_needed_picks >= remaining_picks and positions_needed[player_position] < 1:
            raise HTTPException(status_code=409, detail="Cannot draft player; minimum positions not met. Current requirements:" + str(positions_needed))
        elif current_count >= max_allowed:
            raise HTTPException(status_code=409, detail=f"Maximum number of {player_position} players reached")
        
        connection.execute(sqlalchemy.text("""
            INSERT INTO selections (team_id, player_id, when_selected)
            VALUES (:team_id, :player_id, :when_selected)
        """), {'team_id': request.team_id, 'player_id': player_id, 'when_selected': previous_picks + 1})

        total_possible_picks = number_of_teams * draft_info['roster_size']
        if previous_picks + 1 == total_possible_picks:
            connection.execute(sqlalchemy.text("""
                UPDATE drafts SET draft_status = 'ended'
                WHERE draft_id = :draft_id
            """), {'draft_id': draft_info['draft_id']})

        return {"message": "Player drafted successfully"}
