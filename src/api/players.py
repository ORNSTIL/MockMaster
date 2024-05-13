from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel
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

@router.get("/{player_id}/", response_model=PlayerStatsResponse)
def get_player_statistics(player_id: str):
    with db.engine.begin() as connection:
        stats = connection.execute(sqlalchemy.text("""
            SELECT player_id, year, age, position, team, games_played, games_started,
                   passing_yards, passing_tds, interceptions, rushing_atts, rushing_yards,
                   targets, receptions, receiving_yards, receiving_tds, fumbles, fumbles_lost,
                   two_point_conversions, fantasy_points_standard_10, fantasy_points_ppr_10,
                   rushing_tds, two_point_conversions_passing
            FROM stats
            WHERE player_id = :player_id
        """), {'player_id': player_id}).mappings().fetchall()
        
        if not stats:
            raise HTTPException(status_code=404, detail="Player statistics not found")

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

        return {"player_stats": {"history": formatted_stats}}


class DraftPlayerRequest(BaseModel):
    team_id: int

@router.post("/{player_id}/draft")
def draft_player(player_id: str, request: DraftPlayerRequest):
    with db.engine.begin() as connection:
        try:
            result = connection.execute(sqlalchemy.text("""
                INSERT INTO selections (team_id, player_id, when_selected)
                VALUES (:team_id, :player_id, EXTRACT(EPOCH FROM NOW()))
                RETURNING team_id
            """), {'team_id': request.team_id, 'player_id': player_id})

            drafted_team_id = result.scalar_one()
            return {"success": True}
        except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=409, detail="Player already drafted or team not found")

