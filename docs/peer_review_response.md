# Peer Review Feedback
## Code Review Comments (Ethan Vosburg)
### 1. Readability in SQL commands
Changes: implemented the suggested SQL statements to improve readability
id_sql = sqlalchemy.text("""INSERT INTO drafts (draft_name, draft_type, roster_size, draft_size, draft_length, flex_spots)
                                                VALUES (:name, :type, :rsize, :dsize, :dlength, :flex)
                                                RETURNING draft_id
                                                """)
id_options = {"name": draft_request.draft_name,
                                                     "type": draft_request.draft_type,
                                                    "rsize": draft_request.roster_size,
                                                    "dsize": draft_request.draft_size,
                                                    "dlength": draft_request.draft_length,
                                                    "flex": draft_request.flex_spots}
id = connection.execute(id_sql, id_options).scalar_one()
### 2. Ambiguous “if” statement
Changes: added parenthesis to “if” statement to make it less ambiguous 
if (not draft_info) or (draft_info['draft_status'] != 'pending'):
### 3. Inconsistent SQL statements
No changes made here
The suggestion was to change our use of Query builder notation to .text notation to maintain consistency, but we are sticking with Query builder notation because it was recommended in class for search endpoints
### 4. Cursor Object Instead of fetchall() in players.py
No changes made here
We are continuing to use fetchall instead of a CursorResult object because we get the length of the resulting rows before we iterate through them.
### 5. Raise an Exception in players.py
Replaced statement with “raise HTTPException(status_code=400, detail="Invalid sort column specified")”
### 6. Unnecessary Mappings in drafts.py
Removed unnecessary mappings() from all but get_draft_rooms() because mappings() makes it simpler
### 7. Returning in a With Statement in drafts.py (join_draft_room)
Change: modified code so the return is outside of the with statement. It now follows a common format across all files.
### 8. Identical Error Statements in drafts.py
Didn’t change anything because while there are duplicate error/exception messages across all endpoints in drafts.py, each endpoint contains only unique messages
### 9. Cleaning Up Teams
Change: implemented the suggested change of not reassigning result and instead assigning the updated_team_id variable to the connection result directly
### 10. Better Naming (for result variable in teams.py)
Change: implemented the suggested improvement of updating the “result” variable in the get_team endpoint to “team_info”
### 11. Cursor Result (in players.py)
Change: Replaced all instances of indexing with dot notation to access data from mappings.
### 12. Better Error Language (in players.py)
Change: more descriptive error codes and messages were added throughout the draft player endpoint.

## Code Review Comments (Jonathan DeBarro)
### 1. Define variable outside execution in drafts.py
I can’t find where this occurs, so no changes
### 2. Remove generic comments 
Changes: removed generic comments within functions in teams.py, drafts.py, and players.py
### 3. Add long comments to beginning of function 
Changes: added comment to describe functions in teams.py, drafts.py, and players.py
### 4. Add helper functions (suggested for start_draft and get_player_statistics)
No changes made to get_player_statistics
Since this function simply returns the data from one table in the database, a helper function is not needed.
No changes made to start_draft
Helper function not necessary for any of the operations in this function.
### 5. Two blank lines after a function
Changes: ensured two line spacing between functions in teams.py, drafts.py, and players.py
### 6. Add view for player stats
Changes: Following recommendation, a materialized view was created in order to prevent using joins in the search function.
create materialized view
  public.player_points as
select
  players.player_id,
  players.player_name,
  stats.year,
  stats."position",
  stats.team,
  stats.age,
  stats.fantasy_points_standard_10,
  stats.fantasy_points_ppr_10
from
  stats
  join players on stats.player_id = players.player_id;
### 7. Change search endpoint name
No changes made here
For specificity and clarity, the more descriptive /players/search/ endpoint name is kept instead of reducing the endpoint to just /players/.
### 8. Add generic get/{team_id} endpoint
No changes made here
This improvement suggests changing this endpoint to be able to return many teams; however, we want this endpoint to only return one team at a time to keep the functionality of viewing one’s own team or a specific team simple
### 9. No review comment
### 10. Add verbs to draft start/pause/end endpoints
I’m confused because “start,” “pause,” “end” are the verbs; no changes
### 11. Move commented out draft testing code to separate file
Created “comments_for_testing.txt” in root directory to hold shortcuts for testing endpoints
### 12. Delete files irrelevant to project

## Code Review Comments (Baylor Pond)
### 1. Inconsistent SQL Alchemy Queries in drafts.py
SQL Alchemy Queries were standardized and they all follow a common format throughout all endpoints across all files. The only exception is the search function which uses the query builder which was a recommended implementation from class.
### 2. Query Builder vs. SQLAlchemy.text 
Completed already (see Ethan Vosburg Code Review Comments #3)
### 3. Assert false instead of exception (line 85 players.py)
Completed already (see Ethan Vosburg Code Review Comments #5)
### 4. Mappings on a query returning one row (drafts.py)
Completed already (see Ethan Vosburg Code Review Comments #6)
### 5. Add larger comments for each function
Duplicate; in progress (see Jonathan DeBarro Code Review Comments #3)
### 6. Make “get_player_statistics()” more readable (players.py)
No changes made here
Since the variable assignment is the only significant operation in the function, we decided that a helper function is unnecessary.
### 7. Use more try-except blocks
Try-except blocks were added throughout the files to provide more relevant messages to users. In general, all connections to the database are wrapped in a try-except block.
### 8. Repurpose commented-out code → perhaps for testing in another file
Completed already (see Jonathon DeBarro Code Review Comments #11)
### 9. Unnecessary files 
Completed already (see Jonathan DeBarro Code Review Comments #12)

## Code Review Comments (Muzart Truman)
### 1. Remove unnecessary comments in drafts.py
Completed already (see Jonathon DeBarro Code Review Comments #11)
### 2. Wrap SQL queries in try-except blocks
Completed already (see Baylor Pond Code Review Comments #7)
### 3. Use Pydantic in drafts.py
Pydantic is used, so no changes
### 4. More descriptive comments at top of functions
Duplicate; in progress (see Jonathan DeBarro Code Review Comments #3)
### 5. Define variables outside of SQL statements
No changes made here
We purposely defined variables used in SQL statements within the SQL statements to improve readability in being clear where those variables are used
### 6. Add validation constraints to models like RosterPosition
The way in which input validation for draft creation was significantly changed. Now, pydantic is used to ensure that values are valid.
### 7. Use transactions in drafts.py file
The format of the position requirement was changed so that the numbers are changed according to the number of roster positions that were selected. The endpoint then inserts the rows directly so that validation errors will not occur.
### 8. Add logging to track errors
No changes made here
Instead of error logging, more robust exceptions were added throughout the endpoints to ensure that sufficient information is available for the user and for testing.
### 9. Delete Central Coast Cauldron files
Completed already (see Jonathan DeBarro Code Review Comments #12)
### 10. Implement asynchronous functions as well as asynchronous SQL queries
No changes made here
Given the scale of our project, this implementation would add too much complexity and challenges when debugging. Additionally, there are very few endpoints that would require this functionality.
### 11. Implement a limit for user requests
No changes made here
Similar to the previous endpoint, given the scale of our project, we decided not to implement this feature.
### 12. Make sure the first shuffle does not match the second shuffle 
No changes made here
The random.shuffle function is already used as intended
This function randomizes draft pick order given the number of teams in a draft, and each pick is unique

## Schema/API Design Comments (Jonathan DeBarro)
### 1. Create a view for the stats and players table
Completed already (see Jonathan DeBarro Code Review Comments #6)
### 2. draft_id and draft_position should not be nullable
While draft_id has been set to not null, draft_position remains nullable. The reason for this is that the team’s draft position is not assigned until the draft status is changed from pending to started. This is because the draft position is randomly assigned and the range of possible values depends on how many teams there are when a draft is started.
### 3. Cascade teams when draft is deleted
No changes made here
Drafts cannot and should not be deleted
### 4. Cascade selections when team is deleted
No changes made here
Teams cannot and should not be deleted
### 5. Force draft type to only take specific forms in drafts
Pydantic was used to ensure that draft type and other inputs only takes on specific forms or exist within certain ranges:
class DraftType(str, Enum):
	PPR = 'PPR'
	Standard = 'Standard'

class DraftRequest(BaseModel):
	draft_type: DraftType
	draft_name: str = Field(..., min_length=3, max_length=30)
	draft_size: conint(ge=2, le=16)
	roster_size: Literal[8, 10, 12]
### 6. Force max/mins for size, flex_spots, etc.
Completed already (see Jonathan DeBarro Schema/API Design Comments #6)
### 7. Add endpoint to remove team from draft
No changes made here
Drafts cannot and should not be deleted

## Schema/API Design Comments (Ethan Vorsburg)
### 1. Return Team ID when draft is created
The team creation functionality has now been moved to a separate endpoint so this is no longer an issue.
### 2. Separate team creation from draft creation
Draft creation no longer includes team creation. They are now entirely separate endpoints as recommended.
### 3. Players should have unique ID numbers aside from alphanumeric strings
No changes made here
Since all of our player data comes from an outside resource which comes with a specified ID, we decided to keep the single id value. This allows us to expand the amount of player data we have for past seasons more easily, making this portion of the project more scalable.
### 4. Add endpoint to get all player data
No changes made here
Due to the amount of player data that is being stored, this endpoint would return more data than would realistically be useful. As a result, all player data access goes through the search endpoint.
### 5. Add get draft rooms endpoint
A full get drafts endpoint was created:
@router.get("/")
def get_draft_rooms():
…
### 6. Add consistent feedback messages for draft control endpoints
Feedback messages were added for all time control endpoints. For example:
Ex: return {"success": True, "message": "Draft paused successfully"}
### 7. Add CRON job to SQL database
CRON job was created using
create extension pg_cron with schema extensions;
create extension pg_net;
grant usage on schema cron to postgres;
grant all privileges on all tables in schema cron to postgres;

SELECT cron.schedule('keep alive job', '*/10 * * * *', $$
    select
      net.http_get(
          url:='https://mockmaster.onrender.com/?ping=true'
      );
;$$);
### 8. Position requirements table not in use
The draft functionality has been updated so that the table and feature is now in use. The draft player endpoint now checks to make sure that position requirements are satisfied when selecting a player.
### 9. Redundant table values
Tables were modified and certain unused values were removed. For example, the flex_spots and draft_visibility fields are not longer in use.
### 10. Add visibility flag from documented flows
The visibility flag functionalist has been removed from the API and all references to this value were removed.
### 11. Add roster_table to link players to teams
The selections table achieves this functionality.
### 12. No way to add players to teams
The draft player endpoint achieves this functionality.

## Schema/API Design Comments (Muzart Tuman)
### 1. Consistent data types for ids
No changes made here, already addressed
(see Ethan Vosburg Schema/API Design Comments #3)
### 2. Implement authentication for user privacy
No changes made here
While this was a feature we wanted to implement in a more complete manner, we did not have enough time to fully complete it.
### 3. Add not null to draft name
The schema has been updated to reflect this recommendation. Draft name is no longer nullable.
### 4. Use VARCHAR instead of TEXT
No changes made here
Due to recommendations made in lecture, we decided to continue to use TEXT instead of VARCHAR
### 5. User SERIAL instead of bigint
No changes made here
Due to recommendations made in lecture, we decided to continue to use bigint instead of SERIAL
### 6. Index player_name to make search quicker
No changes made here
Adding indexes and improving performance will be addressed later in V5.
### 7. Implement constraints for roster size
Roster size and roster positions have been changed so that only certain values are possible as constraints have been implemented.
(see Jonathan DeBarro Schema/API Design Comments #3)
### 8. Add remove player
No changes made here
Players should not be able to be removed from mock drafts.
### 9. Add draft history to see previous drafts
No changes made here
While this was a feature we wanted to implement in a more complete manner, we did not have enough time to fully complete it. However, since drafts are not deleted when their status is changed to complete, these draft are always viewable as long as you have the draft_id.
### 10. Add security so not anyone can update team names
No changes made here
While this was a feature we wanted to implement in a more complete manner, we did not have enough time to fully complete it.
### 11. If any delete endpoints are implemented, make sure there is security
No changes made here
No delete endpoints were added since they are not used in mockdrafts.
### 12. Index draft rooms to make lookup faster
No changes made here

## Schema/API Design Comments (Baylor Pond)
### 1. Make player_id int instead of string
No changes made here, already addressed
(see Ethan Vosburg Schema/API Design Comments #3)
### 2. Auto generate all IDs
No changes made here, already addressed
(see Ethan Vosburg Schema/API Design Comments #3)
### 3. Add remove player
No changes made here, already addressed
(see Muzart Tuman Schema/API Design Comments #8)
### 4. Add remove team
No changes made here, already addressed
(see Jonathan DeBarro Schema/API Design Comments #7)
### 5. Add security for delete and remove endpoints
No changes made here, already addressed
(see Muzart Tuman Schema/API Design Comments #10)
### 6. Add not null constraints
Not null constraints have been added throughout the schema to ensure all values are appropriately set.
### 7. Some IDs do not have unique constraint
No changes made here
All IDs are either randomly generated or taken directly from Sports Referene’s database. In the case of the stats table, player_id is not unique because the table’s primary key is a composite key of player_id and year. This is because each row represents a player season, not just a player. As a result, the composite key is what is unique, not the individual id.
### 8. Some tables not in use
Already completed (see Ethan Vosburg Schema/API Design Comments #8)
### 9. Prevent race conditions when drafting players
The draft player endpoint has been significantly changed so that race conditions are handled. Now, it uses the last pick made in the draft to check and see which team_id should be selecting. If the team_id passed by the endpoint is not the same as the team_id who is selecting, are exception will be raised. Additionally, the transaction isolation levels for draft player have been set to serializable to prevent multiple selections being made at the same time.
### 10. Look at all players in draft and see their stats
No changes made here
 (see Ethan Vosburg Schema/API Design Comments #8)
### 11. Cascade deletions
No changes made here
 (see Jonathan DeBarro Schema/API Design Comments #3)
### 12. Specify draft type instead of open text field
Already completed (see Jonathan DeBarro Schema/API Design Comments #5)

## Example Flow Comments

It should be noted for the example flows that our implementation has since been updated from the version being reviewed. We have altered or removed several attributes used for creating a draft room. For example, we have removed fields deemed unnecessary including “draft_length” and “flex_spots”, as well as removed the functionality of adding a team to a draft while also creating that draft. Now, a draft can only be joined via the join draft endpoint instead of both the create draft endpoint and the join draft endpoint. Additionally, we have altered the rules regarding inputs for creating a draft. The “roster_size” field input has been limited to entries of 8, 10, or 12 to align with fantasy football conventions. Also, the attribute “roster_positions”, which sets the maximum and minimum position constraints on drafting players, is no longer passed in by the user but rather automatically generated based on the “roster_size” field. Further, positions for the “roster_positions” field are limited to QB, WR, RB, and TE (unlike some example flows which included D/ST and K). 

We also updated the functionality of our endpoints to ensure valid input by using Pydantic. There are now constraints on draft creation parameters and inputting team name and user name to ensure reasonably sized inputs. For example, the “draft_size” attribute is limited to between 2 and 16, “draft_type” must be either “PPR” or “Standard”, and “team_name” must be between 3 and 14 characters in length.

On another note, we added an endpoint to get a list of all players who have been drafted in the draft, addressing the example flow which wanted an endpoint to see which players were available to draft.

To address the comments that a user should not be able to start and end a draft if they are not the creator of the draft, we purposely allow anyone to start, pause, resume, or end the draft to allow for mock drafting flexibility between users.

An important note is that at the time of testing, our update team name endpoint was resulting in an internal server error. However, we found the bug in our code and ensured that a user can successfully update their team name.

In another example flow, the user attempted to search for a player by using a numeric player ID. However, player ID is an alphanumeric value dependent on the player’s name. For example, the player CeeDee Lamb has player ID LambCe00, and these player IDs can be retrieved with our get players endpoint.

It should be noted that some example flow authors left additional example flows that they wanted us to test, and these endpoints were all tested and verified (such as trying to add a team to a draft when the draft has already started).

## Product Ideas (Baylor Pond)
### 1. Endpoint to display all players with their stats
We decided not to create this endpoint because there are many players and each player can have up to five seasons worth of stats, which we believe is too much for our use case. We will use the search endpoint instead.
### 2. Add training capabilities
We decided not to implement this because trades during fantasy drafts are rare, let alone mock fantasy drafts. If we were implementing a real site where people could host their fantasy leagues, then maybe we would add it.

## Product Ideas (Muzart Tuman)
### 1. History endpoints that display users’ past drafts
Our vision for our site is for users to play one-time mock drafts that serve the sole purpose of getting practice for their real fantasy football draft. As such, we did not intend for users to create accounts, and we opted to focus our efforts on improving the draft functionality rather than properly handling accounts and passwords.
### 2. Leaderboard system / Friends
Like our response to the suggestion above, we did not intend to implement user accounts. Additionally, mock drafts and fantasy drafts as a whole are not something that you can decide or quantify as a winner. So, there would be no metric for which a leaderboard would make sense, other than perhaps displaying who has conducted the most mock drafts.

## Product Ideas (Ethan Vosburg)
### 1. Display player stats for your team when getting your team
We found inspiration for our project from well-known fantasy football sites, which typically display players’ names, positions, and pick number when displaying a team. To get more information or stats about the player, the user would need to click on the player, which we figured would launch a specific search for that player’s stats and information.
### 2. Add a real-time clock to track latency in server-client connection
We did not find that this added functionality would provide much to the core of our project and ideas, so we opted to not spend our efforts looking into it.

## Product Ideas (Jonathan DeBarro)
### 1. Trading endpoint
As stated above for the same suggestion, we do not believe a mock draft site should have the ability to trade picks or players as that is typically not the norm for fantasy sites, and it isn’t really practical. 
### 2. Punishment Voting Endpoint for the team that performs the worst
As stated above, mock drafts are not something in which a winner or loser can be decided. Mock draft sites are meant to be supplemental practice for drafting only– not for maintaining a team through the season. I believe this suggestion would be really fun to see in action for an entire fantasy football site, but it does not have a place in a mock draft site.
