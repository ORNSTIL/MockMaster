from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src import database as db
import sqlalchemy
from src.api import auth
from pydantic import BaseModel, Field
from sqlalchemy import exc

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    dependencies=[Depends(auth.get_api_key)],
)

class TeamUpdateRequest(BaseModel):
    team_name: str = Field(..., min_length=3, max_length=14)

@router.put("/{team_id}/")
def update_team_name(team_id: int, update_request: TeamUpdateRequest):
    """
    Updates the name of a team based on the team_id.
    """

    try:
        with db.engine.begin() as connection:
            update_team = connection.execute(sqlalchemy.text("""
                UPDATE teams SET team_name = :team_name WHERE team_id = :team_id
            """), {"team_name": update_request.team_name, "team_id": team_id})
        
        if update_team.rowcount == 0:
            raise HTTPException(status_code=404, detail="Team not found")
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Could not change name for team with Team ID {team_id}. Please try again.")

    return {"message": "Team name updated successfully"}


@router.get("/{team_id}")
def get_team(team_id: int):
    """
    Retrieves detailed information about a team's selections, including the draft positions, player positions, and names of players selected.
    """

    try:
        with db.engine.begin() as connection:
            team_info = connection.execute(sqlalchemy.text("""
                SELECT when_selected, position, player_name 
                FROM selections
                JOIN player_positions on selections.player_id = player_positions.player_id
                WHERE selections.team_id = :team_id
                ORDER BY when_selected ASC 
                """),{"team_id": team_id})
        
        team = []
        for row in team_info:
            team.append({"selection": row.when_selected, "position": row.position, "player": row.player_name})
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Could not get team with Team ID {team_id}. Please try again.")
        
    return team

