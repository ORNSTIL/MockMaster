from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

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
             "flex_spots": room['flex_spots']}  # assuming roster_positions is stored in a suitable format
            for room in draft_rooms
        ]

    # print draft_rooms_list for testing
    print(f"Draft Room List : {draft_rooms_list}")

    # return draft_rooms_list
    return draft_rooms_list

@router.put("/{draft_id}/start")
def start_draft(draft_id: int):
    with db.engine.begin() as connection:
        # query database
        result = connection.execute(sqlalchemy.text("""
            UPDATE drafts SET draft_status = 'active' 
            WHERE draft_id = :draft_id AND draft_status != 'active'
            RETURNING draft_id
        """), {'draft_id': draft_id})

        # if there is no corresponding draft
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Draft not found or already active")

    # return status
    return "OK"

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