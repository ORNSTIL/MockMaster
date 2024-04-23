MockMaster 
Alex Vasquez 
Xavier Garcia 
Sam Todd 
Luca Ornstil

API Specification

Drafting
Get Players - /players/ (GET) - Retrieves the catalog of all players.
Response:
[
{
	“player_id”: “string”,
	“player_name”: “string”,
	“player_position”: “string”,
	“player_team”: “string”,
	“player_age”: “int”,
	… // other field
}
]
Get Player Statistics - /players/{player_id}/ (GET) - Retrieves detailed statistics for a specified player.
Response:
{
“player_stats”: {
 “history”: “array”
   	}
}
Draft Player - /players/{player_id}/draft (POST) - Draft a player to a team.
Request:
{
"team_id": "string"
}
Response:
{
"success”: “boolean”
}
Add Player to Queue - /players/{player_id}/enqueue (POST) - Add a player to a team’s draft queue.
Request:
{
 	"team_id": "string"
}
Response:
{
"success”: “boolean”
}

Remove Player from Queue - /players/{player_id}/dequeue (DELETE) - Remove a player from a team’s draft queue.
Request:
{
"team_id": "string"
}
Response:
{
"success”: “boolean”
}
Get Queue- /teams/{team_id}/queue (GET) - Retrieves the draft queue for a team.
Response:
[
{
	“player_name”: “string”,
	…
}
			]
Get Players on Team - /teams/{team_id}/players (GET) - Retrieves all drafted players for a specified team.
Response:
[
{
	“player_name”: “string”,
	…
}
]
Change Team Name - /teams/{team_id}/ (PUT) - Change a specified team’s name.
Request:
{
"team_name": "string"
}
Response:
{
 "success”: “boolean”
}








Joining/Creating Drafts
Create Draft Room - /drafts/ (POST) - Creates a new draft room, joins the draft room, and creates a team for that user
Request:
{
"experience_level": "string",
"draft_type": "string", // e.g., PPR, .5 PPR, non-PPR
"visibility": "string", // public or private
"settings": {
"draft_length": "integer", // e.g. time to select a player
"roster_positions": "array",
“roster_size”: “integer”,   // e.g. number of players 
“draft_size”: “integer”   // e.g. number of team
 }
  	“team_name”: “string” // team name for the user creating the draft
  }
Response:
{
 	“team_id": "string"
}
Join Draft Room - /drafts/{draft_id}/join (POST) - Joins a draft room and creates a team for that user. 
Request:
{
"team_name": "string"
}
Response:
{
"team_id": "string"
}
Get Active Draft Rooms - /drafts/ (GET) - Returns list of all public drafts that have been created but have not been started.
Response:
[	// e.g. list of draft room info defined here
	{	
		“draft_id”: “string”
		“draft_name”: “string”,
		“experience_level”: “string”,
		“draft_type”: “string”,
		“draft_size”: “integer”,
		“roster_size”: “integer”,
		“roster_positions”: “array”
	}
]
Start Draft - /drafts/{draft_id}/start (PUT) - start a draft
Response:
{
	“success”: “boolean”
}
Pause Draft - /drafts/{dratf_id}/pause (PUT) - pause a draft
Response:
{
	“success”: “boolean”
}
