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

class RosterPositions(BaseModel):
    QB: list[int]
    RB: list[int]
    WR: list[int]
    TE: list[int]


class DraftRequest(BaseModel):
    draft_type: str
    draft_name: str
    draft_size: int
    draft_length: int
    roster_positions: list[RosterPositions]
    flex_spots: int
    roster_size: int


@router.post("/drafts/")
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
        
    print(f"Draft ID : {id}")

    return {"draft_id" : id}

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