# API Specification

## Drafting

### Search Players - /players/search/ (GET)
Searches for players based on specified query parameters.

Query Parameters:

- `player_name` (optional): The name of the player.
- `position` (optional): The position of the player.
- `team` (optional): The team of the player.
- `search_page` (optional): The page number of the search results.
- `sort_col` (optional): The column to sort the results by. Possible values: `player_name`, `position`, `team`, `age`, `standard_fantasy_points`, `ppr_fantasy_points`. Default: `ppr_fantasy_points`.
- `sort_order` (optional): The sort order of the results. Possible values: `asc` (ascending), `desc` (descending). Default: `desc`.

Response:

The API returns a JSON object with the following structure:

- `previous`: A string that represents the link to the previous page of results. If there is no previous page, this value is an empty string.
- `next`: A string that represents the link to the next page of results. If there is no next page, this value is an empty string.
- `results`: An array of objects, each representing a player. Each player object has the following properties:
    - `player_id`: An string that represents the unique identifier of the player.
    - `player_name`: A string that represents the name of the player.
    - `position`: A string that represents the position of the player.
    - `team`: A string that represents the team of the player.
    - `age`: An integer value that represents the age of the player.
    - `standard_fantasy_points`: An integer value that represents the amount of standard fantasy points the player accrued in the season.
    - `ppr_fantasy_points`: An integer value that represents the amount of ppr fantasy points the player accrued in the season.

### Get Player Statistics - /players/{player_id}/ (GET) - Retrieves detailed statistics for a specified player.

Response:
~~~
{
	“player_stats”: {
		“history”: “array”
	}
}
~~~

### Draft Player - /players/{player_id}/draft (POST) - Draft a player to a team.

Request:
~~~
{
	"team_id": "string"
}
~~~

Response:
~~~
{
	"success”: “boolean”
}
~~~

### Change Team Name - /teams/{team_id}/ (PUT) - Change a specified team’s name.

Request:
~~~
{
	"team_name": "string"
}
~~~

Response:
~~~
{
	"success”: “boolean”
}
~~~

### Get Team - /teams/{team_id}/ (GET) - Get all selections for a team.

Response:
~~~
{
	"team”: {
		"selection": "int",
		"position": "string",
		"player": "string"
	}
}
~~~

## Joining/Creating Drafts

### Create Draft Room - /drafts/ (POST) - Creates a new draft room, joins the draft room, and creates a team for that user

Request:
~~~
{
	"draft_type": "string",
	"draft_name": "string",
	"draft_size": "int",
	"draft_length": "int",
	"roster_positions": "list[RosterPosition]" #Format: [position_name, min, max]
	"flex_spots": "int",
	"roster_size": "int",
	"team_name": "string",
	"user_name": "string"
}
~~~

Response:
~~~
{
 	“team_id": "string"
}
~~~

### Join Draft Room - /drafts/{draft_id}/join (POST) - Joins a draft room and creates a team for that user. 

Request:
~~~
{
	"team_name": "string",
	"user_name": "string"
}
~~~

Response:
~~~
{
	"team_id": "string"
}
~~~

### Get Draft Rooms - /drafts/ (GET) - Returns list of all public drafts that have been created but have not been started.

Response:
~~~
[	// e.g. list of draft room info defined here
	{	
		“draft_id”: “string”
		“draft_name”: “string”,
		“draft_type”: “string”,
		“draft_size”: “integer”,
		“roster_size”: “integer”,
		“draft_length”: “integer”,
		“flex_spots”: “integer”
	}
]
~~~

### Start Draft - /drafts/{draft_id}/start (PUT) - start a pending draft

Response:
~~~
{
	“success”: “boolean”
}
~~~

### Pause Draft - /drafts/{dratf_id}/pause (PUT) - pause a started draft

Response:
~~~
{
	“success”: “boolean”
}
~~~

### Resume Draft - /drafts/{dratf_id}/resume (PUT) - resume a paused draft

Response:
~~~
{
	“success”: “boolean”
}
~~~

### End Draft - /drafts/{dratf_id}/end (PUT) - end a started or resumed draft

Response:
~~~
{
	“success”: “boolean”
}
~~~

### Draft Player - /players/{player_id}/draft (POST) - draft a player to a team if: the draft is active, it is the team's turn to pick, the player is available, and the player selection does not violate maximum and minimum requirements

Response:
~~~
{
	"message": "Player drafted successfully"
}
~~~
