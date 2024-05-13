from fastapi import APIRouter, Depends, HTTPException, Path
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
    draft_length: int
    roster_positions: list[RosterPosition] #Format: [position_name, min, max]
    flex_spots: int
    roster_size: int
    team_name: str
    user_name: str

class JoinDraftRequest(BaseModel):
    team_name: str
    user_name: str

@router.post("/{draft_id}/join")
def join_draft_room(draft_id: int, join_request: JoinDraftRequest):
    with db.engine.begin() as connection:
        # check if draft exists and is not full
        draft = connection.execute(sqlalchemy.text("""SELECT draft_size FROM drafts WHERE draft_id = :id"""),
                                   {"id": draft_id}).mappings().fetchone()
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")

        # count existing teams to ensure the draft is not full
        team_count = connection.execute(sqlalchemy.text("""SELECT COUNT(*) FROM teams WHERE draft_id = :id"""),
                                        {"id": draft_id}).scalar_one()

        # check if there are more teams than allowed
        if team_count >= draft['draft_size']:
            raise HTTPException(status_code=400, detail="Draft is already full")

        # update database
        team_id = connection.execute(sqlalchemy.text("""INSERT INTO teams (draft_id, team_name, user_name)
                                                        VALUES (:id, :team, :user)
                                                        RETURNING team_id"""),
                                     {"id": draft_id, "team": join_request.team_name, "user": join_request.user_name}).scalar_one()

    # print team_id for testing
    print(f"Team ID : {team_id}")

    # return team_id
    return {"team_id": team_id}

@router.post("/")
def create_draft_room(draft_request: DraftRequest):
    with db.engine.begin() as connection:
        # update database
        id = connection.execute(sqlalchemy.text("""INSERT INTO drafts (draft_name, draft_type, roster_size, draft_size, draft_length, flex_spots)
                                                    VALUES (:name, :type, :rsize, :dsize, :dlength, :flex)
                                                    RETURNING draft_id
                                                    """),
                                                    {"name": draft_request.draft_name,
                                                     "type": draft_request.draft_type,
                                                    "rsize": draft_request.roster_size,
                                                    "dsize": draft_request.draft_size,
                                                    "dlength": draft_request.draft_length,
                                                    "flex": draft_request.flex_spots}).scalar_one()
        
        # create roster positions dictionary
        pos_reqs = []
        for pos in draft_request.roster_positions:
            pos_reqs.append({"id": id, "pos": pos.position, "min": pos.min_num, "max": pos.max_num})

        # update database with position requirements
        connection.execute(sqlalchemy.text("""INSERT INTO position_requirements (draft_id, position, min, max)
                                            VALUES (:id, :pos, :min, :max)"""), pos_reqs)
        
        # update database with user
        connection.execute(sqlalchemy.text("""INSERT INTO teams (draft_id, team_name, user_name)
                                            VALUES (:id, :team, :user)"""),
                                            {"id": id, "team": draft_request.team_name, "user": draft_request.user_name})

    # print id for testing
    print(f"Draft ID : {id}")

    # return id
    return {"draft_id" : id}

@router.get("/")
def get_draft_rooms():
    with db.engine.begin() as connection:
        # query database
        draft_rooms = connection.execute(sqlalchemy.text("""SELECT draft_id, draft_name, draft_type, draft_size, roster_size, draft_length, flex_spots
                                                            FROM drafts""")).mappings().fetchall()
        
        # transform result into desired format
        draft_rooms_list = [
            {"draft_id": room['draft_id'],
             "draft_name": room['draft_name'],
             "draft_type": room['draft_type'],
             "draft_size": room['draft_size'],
             "roster_size": room['roster_size'],
             "draft_length": room['draft_length'],
             "flex_spots": room['flex_spots']}
            for room in draft_rooms
        ]

    # print draft_rooms_list for testing
    print(f"Draft Room List : {draft_rooms_list}")

    # return draft_rooms_list
    return draft_rooms_list

@router.put("/{draft_id}/start")
def start_draft(draft_id: int):
    with db.engine.begin() as connection:
        # Ensure the draft is in 'pending' state and count the number of teams
        draft_info = connection.execute(sqlalchemy.text("""
            SELECT draft_status, COUNT(team_id) as team_count
            FROM drafts
            LEFT JOIN teams ON drafts.draft_id = teams.draft_id
            WHERE drafts.draft_id = :draft_id
            GROUP BY drafts.draft_status
        """), {'draft_id': draft_id}).mappings().fetchone()

        if not draft_info or draft_info['draft_status'] != 'pending':
            raise HTTPException(status_code=404, detail="Draft not found or not in a pending state")

        if draft_info['team_count'] == 0:
            raise HTTPException(status_code=400, detail="Cannot start a draft with no teams")

        # Generate random draft positions
        draft_positions = list(range(1, draft_info['team_count'] + 1))
        random.shuffle(draft_positions)

        # Fetch team IDs to update their draft positions
        teams = connection.execute(sqlalchemy.text("""
            SELECT team_id FROM teams WHERE draft_id = :draft_id
        """), {'draft_id': draft_id}).mappings().fetchall()

        # Assign random draft positions to each team
        for team, position in zip(teams, draft_positions):
            connection.execute(sqlalchemy.text("""
                UPDATE teams SET draft_position = :position
                WHERE team_id = :team_id
            """), {'position': position, 'team_id': team['team_id']})

        # Update the draft status to 'active'
        connection.execute(sqlalchemy.text("""
            UPDATE drafts SET draft_status = 'active'
            WHERE draft_id = :draft_id
        """), {'draft_id': draft_id})

    return {"success": True, "message": "Draft started and draft positions assigned randomly"}


@router.put("/{draft_id}/pause")
def pause_draft(draft_id: int):
    with db.engine.begin() as connection:
        # update database
        result = connection.execute(sqlalchemy.text("""
            UPDATE drafts SET draft_status = 'paused' 
            WHERE draft_id = :draft_id AND draft_status = 'active'
            RETURNING draft_id
        """), {'draft_id': draft_id})

        # if there is no corresponding draft
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Draft not found or not active")

    # return status
    return "OK"

@router.put("/{draft_id}/resume")
def resume_draft(draft_id: int):
    with db.engine.begin() as connection:
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

    return {"success": True, "message": "Draft resumed successfully"}


@router.put("/{draft_id}/end")
def end_draft(draft_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            UPDATE drafts SET draft_status = 'ended' 
            WHERE draft_id = :draft_id AND draft_status = 'active'
            RETURNING draft_id
        """), {'draft_id': draft_id})

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Draft not found or not in an endable state")

    return {"success": True}

# For create_draft_room testing
# {
#   "draft_type": "Test 3: Full First Workflow",
#   "draft_name": "The Testers",
#   "draft_size": 10,
#   "draft_length": 60,
#   "roster_positions": [
#     {
#       "position": "QB",
#       "min_num": 1,
#       "max_num": 3
#     },
#     {
#       "position": "RB",
#       "min_num": 2,
#       "max_num": 6
#     },
#     {
#       "position": "WR",
#       "min_num": 2,
#       "max_num": 6
#     },
#     {
#       "position": "TE",
#       "min_num": 1,
#       "max_num": 3
#     }
#   ],
#   "flex_spots": 2,
#   "roster_size": 14,
#   "team_name": "The Coders",
#   "user_name": "elcoder00"
# }
