from fastapi import APIRouter, Depends
from enum import Enum
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
    roster_positions: list[RosterPosition]   # [position_name, min, max]
    flex_spots: int
    roster_size: int
    team_name: str
    user_name: str


@router.post("/")
def post_create_draftroom(draft_request: DraftRequest):
    """ """

    with db.engine.begin() as connection:
        id = connection.execute(sqlalchemy.text("""INSERT INTO drafts (draft_name, draft_type, roster_size, draft_size, draft_length, flex_spots)
                                                    VALUES (:name, :type, :rsize, :dsize, :dlength, :flex)
                                                    RETURNING draft_id
                                                    """),
                                                    {"name": draft_request.draft_name,
                                                     "type": draft_request.draft_type,
                                                    "rsize": draft_request.draft_length,
                                                    "dsize": draft_request.draft_size,
                                                    "dlength": draft_request.flex_spots,
                                                    "flex": draft_request.roster_size}).scalar_one()
        pos_reqs = []
        for pos in draft_request.roster_positions:
            pos_reqs.append({"id": id, "pos": pos.position, "min": pos.min_num, "max": pos.max_num})

        connection.execute(sqlalchemy.text("""INSERT INTO position_requirements (draft_id, position, min, max)
                                            VALUES (:id, :pos, :min, :max)"""), pos_reqs)
        
        connection.execute(sqlalchemy.text("""INSERT INTO teams (draft_id, team_name, user_name)
                                            VALUES (:id, :team, :user)"""),
                                            {"id": id, "team": draft_request.team_name, "user": draft_request.user_name})
        
    print(f"Draft ID : {id}")

    return {"draft_id" : id}

# For testing
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

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": 5,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())