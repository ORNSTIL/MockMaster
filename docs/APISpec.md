# API Specification

## Drafting

### Search Players - /players/search/ (GET)
Gets results according to specified search parameters and sort options. Provides player_id, player_name, position, team, age, standard_fantasy_points, and ppr_fantasy_points for each result.

Query Parameters:

- `player_name` (optional): The name of the player.
- `year`: (optional): The year of the player season. Possible Values: `all`, `2023`, `2022`, `2021`, `2020`, `2019`. Default: `all`.
- `age`: (optional): The age of the player during a given player season.
- `position` (optional): The position of the player.
- `team` (optional): The team of the player.
- `sort_col` (optional): The column to sort the results by. Possible values: `player_name`, `year`, `age`, `position`, `team`, `standard_fantasy_points`, `ppr_fantasy_points`. Default: `ppr_fantasy_points`.
- `sort_order` (optional): The sort order of the results. Possible values: `asc` (ascending), `desc` (descending). Default: `desc`.
- `search_page` (optional): The page number of the search results.

Response:

The API returns a JSON object with the following structure:

- `previous`: A string that represents the link to the previous page of results. If there is no previous page, this value is an empty string.
- `next`: A string that represents the link to the next page of results. If there is no next page, this value is an empty string.
- `results`: An array of objects, each representing a player. Each player object has the following properties:
    - `player_id`: A string that represents the unique identifier of the player.
    - `player_name`: A string that represents the name of the player.
    - `year`: An integer value that represents the year of the player season.
    - `age`: An integer value that represents the age of the player.
    - `position`: A string that represents the position of the player.
    - `team`: A string that represents the team of the player.
    - `standard_fantasy_points`: A float value that represents the amount of standard fantasy points the player accrued in the season.
    - `ppr_fantasy_points`: A float value that represents the amount of PPR fantasy points the player accrued in the season.

### Get Player Statistics - /players/{player_id}/ (GET)
Gets all player statistics for all seasons for the specified player.

Response:
~~~
{
	"player_id": "string",
	"seasons": [
		{
			"year": "integer",
			"age": "integer",
			"position": "string",
			"team": "string",
			"games_played": "integer",
			"games_started": "integer",
			"passing_yards": "integer",
			"passing_tds": "integer",
			"interceptions": "integer",
			"rushing_atts": "integer",
			"rushing_yards": "integer",
			"rushing_tds": "integer",
			"targets": "integer",
			"receptions": "integer",
			"receiving_yards": "integer",
			"receiving_tds": "integer",
			"fumbles": "integer",
			"fumbles_lost": "integer",
			"two_point_conversions_passing": "integer",
			"two_point_conversions": "integer",
			"fantasy_points_standard_10": "float",
			"fantasy_points_ppr_10": "float"
		}
	]
}
~~~

### Draft Player - /players/{player_id}/draft (POST)
Drafts a player to a team. The player must be available, it must be the team's pick, and the player pick must not violate minimum and maximum position restraints for a roster.

Request:
~~~
{
	"team_id": "integer"
}
~~~

Response:
~~~
{
	"message": "string"
}
~~~

### Update Team Name - /teams/{team_id}/ (PUT)
Updates the name of a team based on the team_id.

Request:
~~~
{
	"team_name": "string"
}
~~~

Response:
~~~
{
	"message": "string"
}
~~~

### Get Team - /teams/{team_id}/ (GET)
Retrieves detailed information about a team's selections, including the draft positions, player positions, and names of players selected.

Response:
~~~
[
	{
		"selection": "integer",
		"position": "string",
		"player": "string"
	}
]
~~~

## Joining/Creating Drafts

### Create Draft Room - /drafts/ (POST)
Creates a draft room. Assigns the draft's type, name, and size. Also sets the positional requirements based on the roster size.

Request:
~~~
{
	"draft_type": "string",
	"draft_name": "string",
	"draft_size": "integer",
	"roster_size": "integer"
}
~~~

Response:
~~~
{
	"draft_id": "integer"
}
~~~

### Join Draft Room - /drafts/{draft_id}/join (POST)
Adds a team to a specific draft. Assigns the team's initial name and the name of the user.

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
	"team_id": "integer"
}
~~~

### Get Draft Rooms - /drafts/ (GET)
Retrieves all available drafts that have not yet been started. Acts as a list of drafts that are able to be joined.

Response:
~~~
[
	{	
		"draft_id": "integer",
		"draft_name": "string",
		"draft_type": "string",
		"draft_size": "integer",
		"roster_size": "integer"
	}
]
~~~

### Start Draft - /drafts/{draft_id}/start (PUT)
Starts the drafting process for a specified draft. This process also randomly assigns the draft order for all users in the draft.

Response:
~~~
{
	"success": "boolean",
	"message": "string"
}
~~~

### Pause Draft - /drafts/{draft_id}/pause (PUT)
Changes the status of a specified draft from active to paused.

Response:
~~~
{
	"success": "boolean",
	"message": "string"
}
~~~

### Resume Draft - /drafts/{draft_id}/resume (PUT)
Changes the status of a specified draft from paused to active.

Response:
~~~
{
	"success": "boolean",
	"message": "string"
}
~~~

### End Draft - /drafts/{draft_id}/end (PUT)
Ends the drafting process by changing the status of a specified draft from active to ended. An ended draft cannot be resumed.

Response:
~~~
{
	"success": "boolean",
	"message": "string"
}
~~~

### Get Draft Picks - /drafts/{draft_id}/picks (GET)
Returns a list of all selections made in the specified draft.

Response:
~~~
[
	{
		"when_selected": "integer",
		"player_id": "string",
		"position": "string",
		"team_name": "string",
		"team_id": "integer"
	}
]
~~~

### Get Draft Order - /drafts/{draft_id}/order (GET)
Returns the order of selections for all teams in the specified draft.

Response:
~~~
[
	{
		"draft_position": "integer",
        "team_id": "integer",
        "team_name": "string"
	}
]
~~~

### Get Current Draft Pick - /drafts/{draft_id}/pick (GET)
Returns the team_id of the team in the given draft (via draft_id) who is currently able to draft a player.

Response:
~~~
{
	"team_id": "integer"
}
~~~
