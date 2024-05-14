# Example workflow

Example Flow 2: Starting, Pausing, Resuming, and Ending a Draft

Scenario: Tyler, a fantasy football guru, has created a draft room. Once 7 other teams join his draft, he starts the draft and every team is assigned their draft pick. However, Tyler realizes that he left his stove on as the draft is beginning, so he quickly pauses the draft. After turning the stove off, Tyler resumes the draft. Once every team has made their selections, the draft is ended.

Tyler calls PUT /drafts/{draft_id}/start to start the draft that he created. This automatically assigns each team in the draft a random number from 1 to the number of teams in the draft (with no duplicates). This number represents that team’s draft pick.
Tyler calls PUT /drafts/{draft_id}/pause to pause the draft. At the current moment, nobody can make a pick and the draft timer for the current pick is halted.
Tyler calls PUT /drafts/{draft_id}/resume once he has turned off the stove to resume the draft.
The draft concludes with a call to PUT /drafts/{draft_id}/end.


# Testing results

Tyler calls PUT /drafts/11/start to start the draft that he created.


1. 

curl -X 'PUT' \
  'http://127.0.0.1:8000/drafts/11/start' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster'


2. 

{
  "success": true,
  "message": "Draft started and draft positions assigned randomly"
}

Tyler calls PUT /drafts/11/pause to pause the draft. At the current moment, nobody can make a pick and the draft timer for the current pick is halted.


1.

curl -X 'PUT' \
  'http://127.0.0.1:8000/drafts/11/pause' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster'

2.

"OK"


Tyler calls PUT /drafts/11/resume once he has turned off the stove to resume the draft.


1.

curl -X 'PUT' \
  'http://127.0.0.1:8000/drafts/11/resume' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster'


2.

{
  "success": true,
  "message": "Draft resumed successfully"
}

The draft concludes with a call to PUT /drafts/{draft_id}/end.

1.

curl -X 'PUT' \
  'http://127.0.0.1:8000/drafts/11/end' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster'

2.

{
  "success": true
}


# Example workflow

Example Flow 3: Accessing Player Statistics During Draft

Scenario: Samantha, a fantasy football analyst and blogger known for her strategic insights, is participating in a live draft broadcast. To provide her followers with real-time advice, she accesses detailed statistics for a sleeper pick that could turn the tide of any fantasy league.

Samantha calls GET /players/ to get a list of all players available in the draft. This includes a player named “DK Metcalf” with a player id of “MetcDK00”, who Samantha believes is a sleeper in the draft.
Samantha calls GET /players/{player_id} to retrieve all of the statistics and history for the player named “DK Metcalf”. She can now see that the player named “DK Metcalf” started 16 games, had 119 targets, 66 receptions, 1114 receiving yards, 8 receiving touchdowns, and 225.4 total PPR fantasy points last season.
Samantha, who has a team with an ID of 18, calls POST /players/{player_id}/draft to draft DK Metcalf to her lineup.


# Testing results

Samantha calls GET /players/ to get a list of all players available in the draft. This includes a player named “DK Metcalf” with a player id of “MetcDK00”, who Samantha believes is a sleeper in the draft.

1. 

2.

Samantha calls GET /players/MetcDK00 to retrieve all of the statistics and history for the player named “DK Metcalf”. She can now see that the player named “DK Metcalf” started 16 games, had 119 targets, 66 receptions, 1114 receiving yards, 8 receiving touchdowns, and 225.4 total PPR fantasy points last season.

1.

curl -X 'GET' \
  'http://127.0.0.1:8000/players/MetcDK00/' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster'

2.

{
  "player_stats": {
    "history": [
      {
        "player_id": "MetcDK00",
        "year": 2023,
        "age": 26,
        "position": "WR",
        "team": "SEA",
        "games_played": 16,
        "games_started": 16,
        "passing_yards": 0,
        "passing_tds": 0,
        "interceptions": 0,
        "rushing_atts": 0,
        "rushing_yards": 0,
        "targets": 119,
        "receptions": 66,
        "receiving_yards": 1114,
        "receiving_tds": 8,
        "fumbles": 0,
        "fumbles_lost": 0,
        "two_point_conversions": 0,
        "fantasy_points_standard_10": 159,
        "fantasy_points_ppr_10": 225.4,
        "rushing_tds": 0,
        "two_point_conversions_passing": 0
      }
    ]
  }
}


Samantha, who has a team with an ID of 18, calls POST /players/{player_id}/draft to draft DK Metcalf to her lineup.

1.

curl -X 'POST' \
  'http://127.0.0.1:8000/players/MetcDK00/draft' \
  -H 'accept: application/json' \
  -H 'access_token: MockMaster' \
  -H 'Content-Type: application/json' \
  -d '{
  "team_id": 18
}'


2.

"OK"

