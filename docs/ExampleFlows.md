## Example Flows

### Example Flow 1: Participating in a Custom Draft Room and Changing Your Team Name

Scenario: Alex, a veteran fantasy football player, is gearing up for the annual "Gridiron Glory" private league. He wants to do a mock draft with his other private league members. Alex decides to create a high-stakes PPR draft room designed for the other experienced players in his league. Once Alex has created and joined the draft room, one of Alex’s friends, Cameron, joins Alex’s draft. After joining the draft room and seeing Alex’s team name, Cameron decides that he wants to change his name into something more unique and fun.

- Alex calls POST /draft/ with advanced experience level, a PPR draft type, private visibility, and a team name of “Alex’s Avengers”. Alex also calls this endpoint with settings specifying a draft length of 60 seconds, roster positions of QB, RB, WR, TE, D/ST, and K, a roster size of 12 players, and a draft size of 10 teams. This returns a new draft with an ID of 1234.
- Cameron calls GET /drafts to retrieve a list of all available drafts to join. This list includes Alex’s league, which has a draft id of 1234.
- Cameron calls POST/drafts/1234/join with a team name of “Cameron’s Team” to join the draft room that Alex created and returns a team id of 65.
- Cameron calls PUT teams/65/ with a team name of “Cameron’s Commanders” to update his team name.


### Example Flow 2: Accessing Player Statistics During Draft

Scenario: Samantha, a fantasy football analyst and blogger known for her strategic insights, is participating in a live draft broadcast. To provide her followers with real-time advice, she accesses detailed statistics for a sleeper pick that could turn the tide of any fantasy league.

- Samantha calls GET /players/ to get a list of all players available in the draft. This includes a player named “Justin Fields” with a player id of 6752, who Samantha believes is a sleeper in the draft.
- Samantha calls GET /players/6752/ to retrieve all of the statistics and history for the player named “Justin Fields”. She can now see that the player named “Justin Fields” started 13 games and threw 16 touchdowns last season.

### Example Flow 3: Automatic Drafting for Distracted Users

Scenario: Jordan, a busy software developer and fantasy football enthusiast, is juggling a major project launch with his mock draft night. Concerned he might miss his pick, he sets up an auto-draft feature to ensure he doesn’t lose out on securing a top running back for his team.

- Jordan calls POST /players/{player_id}/enqueue to add a player to his queue. This includes a team id of “Jordan’s Jesters” to ensure the player is queued to the correct team.
- Jordan misses his draft turn when the draft clock expires.
- The system calls POST /players/{player_id}/draft to draft the first player on Jordan’s queue who is still available. This again includes a team id of “Jordan’s Jesters”, and the player is drafted to Jordan’s team.

Note that a player being available must satisfy 2 conditions:
- The player has not already been drafted
- Drafting the player does not violate the number of positions already filled on the user’s team

