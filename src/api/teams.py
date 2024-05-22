from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel
from src import database as db
import sqlalchemy
from src.api import auth

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    dependencies=[Depends(auth.get_api_key)],
)

class TeamUpdateRequest(BaseModel):
    team_name: str

@router.put("/{team_id}/")
def update_team_name(team_id: int, update_request: TeamUpdateRequest):
    with db.engine.begin() as connection:
        updated_team_id = connection.execute(sqlalchemy.text("""UPDATE teams
                                                       SET team_name = :team_name
                                                       WHERE team_id = :team_id"""),
                                    {"team_name": update_request.team_name, "team_id": team_id}).scalar_one_or_none()
        if not updated_team_id:
            raise HTTPException(status_code=404, detail="Team not found")

    return "OK"


@router.get("/{team_id}")
def get_team(team_id: int):
    with db.engine.begin() as connection:
        team_info = connection.execute(sqlalchemy.text(""" SELECT when_selected, position, player_name 
                                                        FROM selections
                                                        JOIN players on selections.player_id = players.player_id
                                                        JOIN stats on players.player_id = stats.player_id
                                                        WHERE selections.team_id = :team_id
                                                        ORDER BY when_selected asc 
                                                       """),
                                                    {"team_id": team_id})
    team = []
    for row in team_info:
        team.append({"selection": row.when_selected, "position": row.position, "player": row.player_name})
        
    return team
