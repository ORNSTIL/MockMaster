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
            SELECT * FROM stats WHERE player_id = :player_id
        """), {'player_id': player_id}).fetchall()
        
        if not stats:
            raise HTTPException(status_code=404, detail="Player statistics not found")

        # Assuming the database returns a list of dictionaries
        return {"player_stats": {"history": [dict(row) for row in stats]}}

class DraftPlayerRequest(BaseModel):
    team_id: str

@router.post("/{player_id}/draft")
def draft_player(player_id: str, request: DraftPlayerRequest):
    with db.engine.begin() as connection:
        # Attempt to insert the player into the selections table
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

