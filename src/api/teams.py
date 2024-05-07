from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel
from src import database as db
import sqlalchemy

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
        # Update the team's name
        result = connection.execute(sqlalchemy.text("""UPDATE teams
                                                       SET team_name = :team_name
                                                       WHERE team_id = :team_id
                                                       RETURNING team_id"""),
                                    {"team_name": update_request.team_name, "team_id": team_id})
        
        updated_team_id = result.scalar_one_or_none()
        if not updated_team_id:
            raise HTTPException(status_code=404, detail="Team not found")

    return {"success": True, "team_id": updated_team_id}

