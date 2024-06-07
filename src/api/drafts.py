from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from pydantic import BaseModel, Field, conint
from typing import Literal
from enum import Enum
from sqlalchemy import exc

router = APIRouter(
    prefix="/drafts",
    tags=["drafts"],
    dependencies=[Depends(auth.get_api_key)],
)

class DraftType(str, Enum):
    PPR = 'PPR'
    Standard = 'Standard'

class DraftRequest(BaseModel):
    draft_type: DraftType
    draft_name: str = Field(..., min_length=3, max_length=30)
    draft_size: conint(ge=2, le=16)
    roster_size: Literal[8, 10, 12]

class JoinDraftRequest(BaseModel):
    team_name: str = Field(..., min_length=3, max_length=14)
    user_name: str = Field(..., min_length=3, max_length=14)

@router.post("/{draft_id}/join")
def join_draft_room(draft_id: int, join_request: JoinDraftRequest):
    """
    Adds a team to a specific draft. Assigns the team's initial name and the name of the user.
    """

    try:
        with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as connection:
            with connection.begin():
                draft = connection.execute(sqlalchemy.text("""                               
                    SELECT draft_size FROM drafts
                    WHERE draft_id = :id AND draft_status = 'pending'
                """), {"id": draft_id}).fetchone()

                if not draft:
                    raise HTTPException(status_code=404, detail="Draft not found or not in a pending state")

                team_count = connection.execute(sqlalchemy.text("""
                    SELECT COUNT(*) FROM teams WHERE draft_id = :id
                """), {"id": draft_id}).scalar_one()

                if team_count >= draft.draft_size:
                    raise HTTPException(status_code=400, detail="Draft is already full")

                team_id = connection.execute(sqlalchemy.text("""
                    INSERT INTO teams (draft_id, team_name, user_name)
                    VALUES (:id, :team, :user)
                    RETURNING team_id
                """), {"id": draft_id, "team": join_request.team_name, "user": join_request.user_name}).scalar_one()
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Failed to Join Draft room with Draft ID {draft_id}. Please try again.")
    
    return {"team_id": team_id}


@router.post("/")
def create_draft_room(draft_request: DraftRequest):
    """
    Creates a draft room. Assigns the draft's type, name, and size. Also sets the positional requirements based on the roster size.
    """

    positional_requirements = {
        8: {'QB': (1, 3), 'RB': (1, 3), 'WR': (1, 3), 'TE': (1, 3)},
        10: {'QB': (1, 4), 'RB': (1, 4), 'WR': (1, 4), 'TE': (1, 4)},
        12: {'QB': (2, 4), 'RB': (2, 4), 'WR': (2, 4), 'TE': (2, 4)}
    }
    requirements = positional_requirements[draft_request.roster_size]

    try:
        with db.engine.begin() as connection:
            id_sql = sqlalchemy.text("""
                INSERT INTO drafts (draft_name, draft_type, roster_size, draft_size)
                VALUES (:name, :type, :rsize, :dsize)
                RETURNING draft_id
                """)
            id_options = {"name": draft_request.draft_name, "type": draft_request.draft_type, "rsize": draft_request.roster_size, "dsize": draft_request.draft_size}
            draft_id = connection.execute(id_sql, id_options).scalar_one()
            
            pos_reqs = [{'draft_id': draft_id, 'position': key, 'min': val[0], 'max': val[1]} for key, val in requirements.items()]
            
            connection.execute(sqlalchemy.text("""
                INSERT INTO position_requirements (draft_id, position, min, max)
                VALUES (:draft_id, :position, :min, :max)"""), pos_reqs)
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Failed to create draft room. Please try again.")

    return {"draft_id": draft_id}


@router.get("/")
def get_draft_rooms():
    """
    Retrieves all available drafts that have not yet been started. Acts as a list of drafts that are able to be joined.
    """

    try: 
        with db.engine.begin() as connection:
            draft_rooms = connection.execute(sqlalchemy.text("""
                SELECT draft_id, draft_name, draft_type, draft_size, roster_size
                FROM drafts
                WHERE draft_status = 'pending'
                """)).mappings().fetchall()
            
            draft_rooms_list = [
                {"draft_id": room['draft_id'],
                "draft_name": room['draft_name'],
                "draft_type": room['draft_type'],
                "draft_size": room['draft_size'],
                "roster_size": room['roster_size']}
                for room in draft_rooms
            ]
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Could not retrieve pending drafts. Please try again.")

    return draft_rooms_list


@router.put("/{draft_id}/start")
def start_draft(draft_id: int):
    """
    Starts the drafting process for a specified draft. This process also randomly assigns the draft order for all users in the draft.
    """

    try: 
        with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as connection:
            with connection.begin():
                draft_lock = connection.execute(sqlalchemy.text("""
                    SELECT draft_status
                    FROM drafts
                    WHERE drafts.draft_id = :draft_id
                """), {'draft_id': draft_id}).fetchone()

                draft_info = connection.execute(sqlalchemy.text("""
                    SELECT COUNT(team_id) as team_count
                    FROM drafts
                    LEFT JOIN teams ON drafts.draft_id = teams.draft_id
                    WHERE drafts.draft_id = :draft_id
                    GROUP BY drafts.draft_status
                """), {'draft_id': draft_id}).fetchone()
                
                if (not draft_lock) or (draft_lock.draft_status != 'pending'):
                    raise HTTPException(status_code=404, detail="Draft not found or not in a pending state")

                if draft_info.team_count == 0:
                    raise HTTPException(status_code=400, detail="Cannot start a draft with no teams")

                connection.execute(sqlalchemy.text("""
                    WITH teams_list AS (
                        SELECT team_id, ROW_NUMBER() OVER (ORDER BY random()) as position_num
                        FROM teams 
                        WHERE draft_id = :draft_id
                    )
                    UPDATE teams SET draft_position = teams_list.position_num
                    FROM teams_list
                    WHERE teams.team_id = teams_list.team_id;
                                                   
                    UPDATE drafts SET draft_status = 'active'
                    WHERE draft_id = :draft_id;
                """), {'draft_id': draft_id})
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Could not start draft with Draft ID ${draft_id}. Please try again.")

    return {"success": True, "message": "Draft started and draft positions assigned randomly"}


@router.put("/{draft_id}/pause")
def pause_draft(draft_id: int):
    """
    Changes the status of a specified draft from active to paused.
    """

    try: 
        with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as connection:
            with connection.begin():
                result = connection.execute(sqlalchemy.text("""                                                    
                    UPDATE drafts SET draft_status = 'paused' 
                    WHERE draft_id = :draft_id AND draft_status = 'active'
                    RETURNING draft_id
                    """), {'draft_id': draft_id})

                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Draft not found or not active")
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Could not pause draft with Draft ID {draft_id}. Please try again.")

    return {"success": True, "message": "Draft paused successfully"}


@router.put("/{draft_id}/resume")
def resume_draft(draft_id: int):
    """
    Changes the status of a specified draft from paused to active.
    """

    try:
        with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as connection:
            with connection.begin():
                result = connection.execute(sqlalchemy.text("""                                                    
                    UPDATE drafts 
                    SET draft_status = 'active' 
                    WHERE draft_id = :draft_id AND draft_status = 'paused'
                    RETURNING draft_id
                """), {'draft_id': draft_id})

                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Draft not found or not in a paused state")
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Could not resume draft with Draft ID {draft_id}. Please try again.")

    return {"success": True, "message": "Draft resumed successfully"}


@router.put("/{draft_id}/end")
def end_draft(draft_id: int):
    """
    Ends the drafting process by changing the status of a specified draft from active to ended. An ended draft cannot be resumed.
    """

    try:
        with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as connection:
            with connection.begin():
                result = connection.execute(sqlalchemy.text("""            
                    UPDATE drafts SET draft_status = 'ended' 
                    WHERE draft_id = :draft_id AND draft_status = 'active'
                    RETURNING draft_id
                """), {'draft_id': draft_id})

                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Draft not found or not in an endable state")
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Could not end draft with Draft ID {draft_id}. Please try again.")

    return {"success": True, "message": "Draft ended successfully"}


@router.get("/{draft_id}/picks")
def get_draft_picks(draft_id: int):
    """
    Returns a list of all selections made in the specified draft.
    """

    try:
        with db.engine.begin() as connection:
            get_draft = connection.execute(sqlalchemy.text("""
                SELECT selections.when_selected, selections.player_id, player_positions.position, teams.team_name, teams.team_id
                FROM selections
                JOIN teams ON selections.team_id = teams.team_id
                JOIN player_positions ON selections.player_id = player_positions.player_id
                WHERE teams.draft_id = :draft_id
                ORDER BY selections.when_selected ASC;
            """), {'draft_id': draft_id}).mappings().fetchall()
            
            if not get_draft:
                raise HTTPException(status_code=404, detail="No picks found for the given draft ID")
            
            picks = [{
                "when_selected": row['when_selected'],
                "player_id": row['player_id'],
                "position": row['position'],
                "team_name": row['team_name'],
                "team_id": row['team_id']
            } for row in get_draft]
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Could not get all draft selections for draft with Draft ID {draft_id}. Please try again.")

    return picks


@router.get("/{draft_id}/order")
def get_draft_order(draft_id: int):
    """
    Returns the order of selections for all teams in the specified draft.
    """

    try:
        with db.engine.begin() as connection:
            draft_order = connection.execute(sqlalchemy.text("""
                SELECT teams.draft_position, teams.team_id, teams.team_name
                FROM teams
                WHERE teams.draft_id = :draft_id
                ORDER BY draft_position ASC;
            """), {'draft_id': draft_id}).mappings().fetchall()
            
            if not draft_order:
                raise HTTPException(status_code=404, detail="Draft not found or draft is empty")
            if draft_order[0]['draft_position'] is None:
                raise HTTPException(status_code=404, detail="Draft order has not yet been assigned")

            order = [{
                "draft_position": row['draft_position'],
                "team_id": row['team_id'],
                "team_name": row['team_name']
            } for row in draft_order]
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Could not get draft order for draft with Draft ID {draft_id}. Please try again.")

    return order


@router.get("/{draft_id}/pick")
def get_current_draft_pick(draft_id: int):
    """
    Returns the team_id of the team in the given draft (via draft_id) who is currently able to draft a player.
    """

    try:
        with db.engine.begin() as connection:
            draft_status = connection.execute(sqlalchemy.text("""
                    SELECT draft_status
                    FROM drafts
                    WHERE draft_id = :draft_id
                """), {'draft_id': draft_id}).scalar_one()
            
            if draft_status != 'active':
                    raise HTTPException(status_code=409, detail="Draft not active")

            previous_picks = connection.execute(sqlalchemy.text("""
                SELECT COUNT(*) FROM selections
                JOIN teams ON selections.team_id = teams.team_id
                WHERE teams.draft_id = :draft_id
            """), {'draft_id': draft_id}).scalar_one()

            number_of_teams = connection.execute(sqlalchemy.text("""
                SELECT COUNT(*) FROM teams
                WHERE draft_id = :draft_id
            """), {'draft_id': draft_id}).scalar_one()

            current_pick = 0
            last_round = previous_picks // number_of_teams
            if last_round % 2 == 1:
                current_pick = number_of_teams - (previous_picks % number_of_teams)
            else:
                current_pick = (previous_picks % number_of_teams) + 1

            team_id = connection.execute(sqlalchemy.text("""
                SELECT team_id
                FROM teams
                WHERE draft_id = :draft_id and draft_position = :current_pick
            """), {'draft_id': draft_id, 'current_pick': current_pick}).scalar_one()
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail=f"Could not get current draft pick for draft with Draft ID {draft_id}. Please try again.")

    return {"team_id": team_id}

