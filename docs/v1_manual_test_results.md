# Example Flow 1: Participating in a Custom Draft Room and Changing Your Team Name

## Description

Scenario: Alex, a veteran fantasy football player, is gearing up for the annual "Fantastic Footies" league. He wants to do a mock draft with his other league members. Alex decides to create a high-stakes PPR draft room designed for the other players in his league. Once Alex has created and joined the draft room, one of Alex’s friends, Cameron, joins Alex’s draft. After joining the draft room and seeing Alex’s team name, Cameron decides that he wants to change his name into something more unique and fun.

Alex, who has the username “aball17”, calls POST /draft/ with a PPR draft type, draft size of 12 total teams, team roster sizes of 10 players per team, 6 flex spots per team, a team name of “Alex’s Avengers”, and a draft name of “Fantastic Footies”. Alex also calls this endpoint with settings specifying a draft length of 1 minute per pick, roster position limitations of 1-3 QBs, 2-6 RBs, 2-6 WRs, and 1-3 TEs. This returns a new draft with an ID of 8.
Cameron calls GET /drafts to retrieve a list of all available drafts to join. This list includes Alex’s league, which has a draft name of “Fantastic Footies” and a draft ID of 8.
Cameron calls POST/drafts/8/join with a team name of “Cameron’s Team” to join the draft room that Alex created and returns a team ID of 5.
Cameron calls PUT teams/8/ with a team name of “Cameron’s Commanders” to update his team name.


## Testing results

Alex, who has the username “aball17”, calls POST /draft/ with a PPR draft type, draft size of 12 total teams, team roster sizes of 10 players per team, 6 flex spots per team, a team name of “Alex’s Avengers”, and a draft name of “Fantastic Footies”. Alex also calls this endpoint with settings specifying a draft length of 1 minute per pick, roster position limitations of 1-3 QBs, 2-6 RBs, 2-6 WRs, and 1-3 TEs. This returns a new draft with an ID of 8.

1. 

curl -X 'POST' \
  'http://127.0.0.1:8000/drafts/' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster' \
  -H 'Content-Type: application/json' \
  -d '{
  "draft_type": "PPR",
  "draft_name": "Fantastic Footies",
  "draft_size": 12,
  "draft_length": 1,
   "roster_positions": [
     {
       "position": "QB",
       "min_num": 1,
       "max_num": 3
     },
     {
       "position": "RB",
       "min_num": 2,
       "max_num": 6
     },
     {
       "position": "WR",
       "min_num": 2,
       "max_num": 6
     },
     {
       "position": "TE",
       "min_num": 1,
       "max_num": 3
     }
   ],
  "flex_spots": 6,
  "roster_size": 10,
  "team_name": "Alex’s Avengers",
  "user_name": "aball17"
}'


2. 

{
  "draft_id": 8
}



Cameron calls GET /drafts to retrieve a list of all available drafts to join. This list includes Alex’s league, which has a draft name “Fantastic Footies” and a draft ID of 8.

1.

curl -X 'GET' \
  'http://127.0.0.1:8000/drafts/' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster'

2.

[
  {
    "draft_id": 1,
    "draft_name": "Test Numero Uno",
    "draft_type": "PPR",
    "draft_size": 10,
    "roster_size": 15,
    "draft_length": 2,
    "flex_spots": 15
  },
  {
    "draft_id": 2,
    "draft_name": "Test Numero Uno",
    "draft_type": "PPR",
    "draft_size": 10,
    "roster_size": 15,
    "draft_length": 2,
    "flex_spots": 15
  },
  {
    "draft_id": 5,
    "draft_name": "Test 2",
    "draft_type": "PPR",
    "draft_size": 10,
    "roster_size": 60,
    "draft_length": 2,
    "flex_spots": 14
  },
  {
    "draft_id": 6,
    "draft_name": "The Testers",
    "draft_type": "Standard",
    "draft_size": 10,
    "roster_size": 60,
    "draft_length": 2,
    "flex_spots": 14
  },
  {
    "draft_id": 7,
    "draft_name": "The Testers",
    "draft_type": "Test 3: Full First Workflow",
    "draft_size": 10,
    "roster_size": 60,
    "draft_length": 2,
    "flex_spots": 14
  },
  {
    "draft_id": 8,
    "draft_name": "Fantastic Footies",
    "draft_type": "PPR",
    "draft_size": 12,
    "roster_size": 1,
    "draft_length": 6,
    "flex_spots": 10
  }
]


Cameron, whose username is “camdog98”, calls POST/drafts/8/join with a team name of “Cameron’s Team” to join the draft room that Alex created and returns a team ID of 5.

1.

curl -X 'POST' \
  'http://127.0.0.1:8000/drafts/8/join' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster' \
  -H 'Content-Type: application/json' \
  -d '{
  "team_name": "Cameron’s Team",
  "user_name": "camdog98"
}


2.

{
  "team_id": 5
}

Cameron calls PUT teams/8/ with a team name of “Cameron’s Commanders” to update his team name.

1.

curl -X 'PUT' \
  'http://127.0.0.1:8000/teams/5/' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster' \
  -H 'Content-Type: application/json' \
  -d '{
  "team_name": "Cameron’s Commanders"
}'

2.

{
  "success": true,
  "team_id": 5
}


