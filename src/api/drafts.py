from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import random

router = APIRouter(
    prefix="/drafts",
    tags=["drafts"],
    dependencies=[Depends(auth.get_api_key)],
)

class RosterPosition(BaseModel):
    position: str
    min_num: int
    max_num: int

class DraftRequest(BaseModel):
    draft_type: str
    draft_name: str
    draft_size: int
    roster_positions: list[RosterPosition]
    roster_size: int

class JoinDraftRequest(BaseModel):
    team_name: str
    user_name: str

@router.post("/{draft_id}/join")
def join_draft_room(draft_id: int, join_request: JoinDraftRequest):
    """
    Adds a team to a specific draft. Assigns the team's initial name and the name of the user.
    """
    try:
        with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as connection:
            with connection.begin():
                # Check if draft exists, is not full, and is in a 'pending' status
                draft = connection.execute(sqlalchemy.text("""                               
                    SELECT draft_size FROM drafts
                    WHERE draft_id = :id AND draft_status = 'pending'
                """), {"id": draft_id}).fetchone()

                if not draft:
                    raise HTTPException(status_code=404, detail="Draft not found or not in a pending state")

                # Count existing teams to ensure the draft is not full
                team_count = connection.execute(sqlalchemy.text("""
                    SELECT COUNT(*) FROM teams WHERE draft_id = :id
                """), {"id": draft_id}).scalar_one()

                if team_count >= draft.draft_size:
                    raise HTTPException(status_code=400, detail="Draft is already full")

                # Insert the new team into the draft
                team_id = connection.execute(sqlalchemy.text("""
                    INSERT INTO teams (draft_id, team_name, user_name)
                    VALUES (:id, :team, :user)
                    RETURNING team_id
                """), {"id": draft_id, "team": join_request.team_name, "user": join_request.user_name}).scalar_one()
    except:
        raise HTTPException(status_code=400, detail=f"Failed to Join Draft room with Draft ID: ${draft_id}. Please try again.")
    
    return {"team_id": team_id}


@router.post("/")
def create_draft_room(draft_request: DraftRequest):
    """
    Creates a draft room. Assigns the draft's type, name, and size. Also sets the positional requirements and overall number of roster positions.
    """
    try:
        with db.engine.begin() as connection:
            id_sql = sqlalchemy.text("""
                INSERT INTO drafts (draft_name, draft_type, roster_size, draft_size)
                VALUES (:name, :type, :rsize, :dsize)
                RETURNING draft_id
                """)
            id_options = {"name": draft_request.draft_name,
                        "type": draft_request.draft_type,
                        "rsize": draft_request.roster_size,
                        "dsize": draft_request.draft_size}
            id = connection.execute(id_sql, id_options).scalar_one()
            
            # create roster positions dictionary
            pos_reqs = []
            for pos in draft_request.roster_positions:
                pos_reqs.append({"id": id, "pos": pos.position, "min": pos.min_num, "max": pos.max_num})

            # update database with position requirements
            connection.execute(sqlalchemy.text("""
                INSERT INTO position_requirements (draft_id, position, min, max)
                VALUES (:id, :pos, :min, :max)"""), pos_reqs)
    except:
        raise HTTPException(status_code=400, detail="Failed to create draft room. Please try again.")
    
    return {"draft_id" : id}


@router.get("/")
def get_draft_rooms():
    """
    Retrieves all available drafts that have not yet been started. Acts as a list of drafts that are able to be joined.
    """
    try: 
        with db.engine.begin() as connection:
            draft_rooms = connection.execute(sqlalchemy.text("""
                SELECT draft_id, draft_name, draft_type, draft_size, roster_size, draft_length
                FROM drafts
                WHERE draft_status = 'pending'
                """)).mappings().fetchall()
            
            draft_rooms_list = [
                {"draft_id": room['draft_id'],
                "draft_name": room['draft_name'],
                "draft_type": room['draft_type'],
                "draft_size": room['draft_size'],
                "roster_size": room['roster_size'],
                "draft_length": room['draft_length']}
                for room in draft_rooms
            ]
    except:
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
                # Ensure the draft is in 'pending' state and count the number of teams
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

                # Assign random draft position to each team in draft, update respectively in teams db
                # Update the draft status to 'active'
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
    except:
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

                # if there is no corresponding draft
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Draft not found or not active")
    except:
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
                # Update draft status to 'active' only if it is currently 'paused'
                result = connection.execute(sqlalchemy.text("""                                                    
                    UPDATE drafts 
                    SET draft_status = 'active' 
                    WHERE draft_id = :draft_id AND draft_status = 'paused'
                    RETURNING draft_id
                """), {'draft_id': draft_id})

                # If no draft is found or the draft is not in a paused state
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Draft not found or not in a paused state")
    except:
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
    except:
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
                SELECT selections.when_selected, selections.player_id, stats.position, teams.team_name, teams.team_id
                FROM selections
                JOIN teams ON selections.team_id = teams.team_id
                JOIN players ON selections.player_id = players.player_id
                JOIN stats ON players.player_id = stats.player_id
                WHERE teams.draft_id = :draft_id
                ORDER BY selections.when_selected ASC
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
    except:
        raise HTTPException(status_code=400, detail=f"Could not get all draft selections for draft with Draft ID {draft_id}. Please try again.")

    return picks

