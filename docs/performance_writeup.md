# Performance Writeup

## Fake Data Modeling

Python file for data creation: https://github.com/ORNSTIL/MockMaster/blob/main/data/generator.py

The fake data was generated using the average expected draft size and roster size for a typical mock draft. As a result, we assumed each draft had 10 teams and 10 roster spots per team. Since the players and stats tables are not modified by the user and will not change over time, their size is independent of the scale of the application.

Data Distribution:
- Drafts: 8,696 rows
- Position Requirements: 34,784 rows
- Teams: 86,960 rows
- Selections: 869,600 rows
- Players: 1,200 rows*
- Stats: 3,247 rows*
- Total rows across all tables: 1,004,487 rows

While the number of teams in a draft can range anywhere from 2 to 16 and the number of roster positions from 8 to 12, it is safe to assume that our service will scale in the manner outlined above. In any drafting setting, selections should always be the most common transaction. Additionally, there will always be more selections than teams and teams than drafts. Given our implementation of position requirements, there will always be 4 position requirement entries for every draft. This leads us to the following ratio, which is used for the calculation of rows listed above:

drafts : position_requirements : teams : selections = 1 : 4 : 10 : 100

## Endpoint Performance Results

Drafts Endpoints:
- POST /drafts/draft_id/join = 0.0357ms
- GET /drafts/ = 0.0169ms
- POST /drafts/ = 0.0297ms
- PUT /drafts/draft_id/start = 0.0581ms
- PUT /drafts/draft_id/pause = 0.0173ms
- PUT /drafts/draft_id/resume = 0.0112ms
- PUT /drafts/draft_id/end = 0.0113ms
- GET /drafts/draft_id/picks = 0.0311ms

Players Endpoints:
- GET /players/search/ = 0.0116ms
- GET /players/playerId/ = 0.0129ms
- POST /players/player_id/draft = 0.0704ms

Teams Endpoints:
- PUT /teams/team_id/ = 0.0166ms
- GET /teams/team_id/ = 0.0098ms

Slowest Endpoints:
- POST /players/player_id/draft = 0.0704ms
- PUT /drafts/draft_id/start = 0.0581ms
- POST /drafts/draft_id/join = 0.0357ms

## Endpoint Performance Tuning

### POST /players/player_id/draft

1.

| QUERY PLAN                                                                  	|
| ------------------------------------------------------------------------------- |
| Nested Loop  (cost=0.58..16.61 rows=1 width=26)                             	|
|   ->  Index Scan using teams_pkey on teams  (cost=0.29..8.31 rows=1 width=12)   |
|     	Index Cond: (team_id = 1)                                           	|
|   ->  Index Scan using drafts_pkey on drafts  (cost=0.29..8.30 rows=1 width=22) |
|     	Index Cond: (draft_id = teams.draft_id)                             	|

2. 

| QUERY PLAN                                                                         	|
| -------------------------------------------------------------------------------------- |
| Limit  (cost=0.28..6.30 rows=1 width=7)                                            	|
|   ->  Index Scan Backward using stats_pkey on stats  (cost=0.28..12.31 rows=2 width=7) |
|     	Index Cond: (player_id = 'JeffJu00'::text)                                 	|

3. 

| QUERY PLAN                                                                                      	|
| --------------------------------------------------------------------------------------------------- |
| Result  (cost=2123.47..2123.48 rows=1 width=1)                                                  	|
|   InitPlan 1 (returns $1)                                                                       	|
| 	->  Nested Loop  (cost=0.42..2123.47 rows=1 width=0)                                        	|
|       	->  Seq Scan on teams  (cost=0.00..2075.00 rows=10 width=8)                           	|
|             	Filter: (draft_id = 1)                                                          	|
|       	->  Index Only Scan using selections_pkey on selections  (cost=0.42..4.44 rows=1 width=8) |
|             	Index Cond: ((team_id = teams.team_id) AND (player_id = 'JeffJu00'::text))      	|

4. 

| QUERY PLAN                                                                                     	|
| -------------------------------------------------------------------------------------------------- |
| Aggregate  (cost=2122.25..2122.26 rows=1 width=8)                                              	|
|   ->  Nested Loop  (cost=0.42..2122.00 rows=100 width=0)                                       	|
|     	->  Seq Scan on teams  (cost=0.00..2075.00 rows=10 width=8)                            	|
|           	Filter: (draft_id = 1)                                                           	|
|     	->  Index Only Scan using selections_pkey on selections  (cost=0.42..4.60 rows=10 width=8) |
|           	Index Cond: (team_id = teams.team_id)                                            	|

5. 

| QUERY PLAN                                                	|
| ------------------------------------------------------------- |
| Aggregate  (cost=2075.03..2075.04 rows=1 width=8)         	|
|   ->  Seq Scan on teams  (cost=0.00..2075.00 rows=10 width=0) |
|     	Filter: (draft_id = 1)                            	|

6. 

| QUERY PLAN                                                                               	|
| -------------------------------------------------------------------------------------------- |
| Aggregate  (cost=4.62..4.63 rows=1 width=8)                                              	|
|   ->  Index Only Scan using selections_pkey on selections  (cost=0.42..4.60 rows=10 width=0) |
|     	Index Cond: (team_id = 1)                                                        	|

7. 

| QUERY PLAN                                                                                          	|
| ------------------------------------------------------------------------------------------------------- |
| Index Scan using position_requirements_pkey on position_requirements  (cost=0.29..13.61 rows=4 width=7) |
|   Index Cond: (draft_id = 1)                                                                        	|

8. 

| QUERY PLAN                                                                                           	|
| -------------------------------------------------------------------------------------------------------- |
| Aggregate  (cost=100.38..100.39 rows=1 width=8)                                                      	|
|   ->  Hash Join  (cost=4.72..100.37 rows=4 width=0)                                                  	|
|     	Hash Cond: (stats.player_id = selections.player_id)                                          	|
|     	->  Seq Scan on stats  (cost=0.00..94.59 rows=404 width=9)                                   	|
|           	Filter: ("position" = 'QB'::text)                                                      	|
|     	->  Hash  (cost=4.60..4.60 rows=10 width=9)                                                  	|
|           	->  Index Only Scan using selections_pkey on selections  (cost=0.42..4.60 rows=10 width=9) |
|                 	Index Cond: (team_id = 1)                                                        	|

9. 

| QUERY PLAN                                                                                           	|
| -------------------------------------------------------------------------------------------------------- |
| Aggregate  (cost=100.38..100.39 rows=1 width=8)                                                      	|
|   ->  Hash Join  (cost=4.72..100.37 rows=4 width=0)                                                  	|
|     	Hash Cond: (stats.player_id = selections.player_id)                                          	|
|     	->  Seq Scan on stats  (cost=0.00..94.59 rows=404 width=9)                                   	|
|           	Filter: ("position" = 'QB'::text)                                                      	|
|     	->  Hash  (cost=4.60..4.60 rows=10 width=9)                                                  	|
|           	->  Index Only Scan using selections_pkey on selections  (cost=0.42..4.60 rows=10 width=9) |
|                 	Index Cond: (team_id = 1)                                                        	|

10. 

| QUERY PLAN                                                                                         	|
| ------------------------------------------------------------------------------------------------------ |
| Index Scan using position_requirements_pkey on position_requirements  (cost=0.29..8.31 rows=1 width=4) |
|   Index Cond: ((draft_id = 1) AND ("position" = 'QB'::text))                                       	|

11.

| QUERY PLAN                                         	|
| ------------------------------------------------------ |
| Insert on selections  (cost=0.00..0.01 rows=0 width=0) |
|   ->  Result  (cost=0.00..0.01 rows=1 width=44)    	|

Since this endpoint contains many SQL queries, we are going to focus on optimizing the queries that have the highest cost. These are queries 3, 4, and 5. All of these endpoints do a sequential scan on teams when filtering on the draft_id value. To improve performance, we can add an index to this value using the following code:

CREATE INDEX teams_draft_id_index ON teams (draft_id);

| QUERY PLAN                                                                                            	|
| --------------------------------------------------------------------------------------------------------- |
| Result  (cost=53.16..53.17 rows=1 width=1)                                                            	|
|   InitPlan 1 (returns $1)                                                                             	|
| 	->  Nested Loop  (cost=0.73..53.16 rows=1 width=0)                                                	|
|       	->  Index Scan using teams_draft_id_index on teams  (cost=0.29..8.47 rows=10 width=8)       	|
|             	Index Cond: (draft_id = 1)                                                            	|
|       	->  Memoize  (cost=0.43..4.45 rows=1 width=8)                                               	|
|             	Cache Key: teams.team_id                                                              	|
|             	Cache Mode: logical                                                                   	|
|             	->  Index Only Scan using selections_pkey on selections  (cost=0.42..4.44 rows=1 width=8) |
|                   	Index Cond: ((team_id = teams.team_id) AND (player_id = 'A'::text))             	|

| QUERY PLAN                                                                                     	|
| -------------------------------------------------------------------------------------------------- |
| Aggregate  (cost=55.72..55.73 rows=1 width=8)                                                  	|
|   ->  Nested Loop  (cost=0.72..55.47 rows=100 width=0)                                         	|
|     	->  Index Scan using teams_draft_id_index on teams  (cost=0.29..8.47 rows=10 width=8)  	|
|           	Index Cond: (draft_id = 1)                                                       	|
|     	->  Index Only Scan using selections_pkey on selections  (cost=0.42..4.60 rows=10 width=8) |
|           	Index Cond: (team_id = teams.team_id)                                            	|

| QUERY PLAN                                                                               	|
| -------------------------------------------------------------------------------------------- |
| Aggregate  (cost=4.49..4.50 rows=1 width=8)                                              	|
|   ->  Index Only Scan using teams_draft_id_index on teams  (cost=0.29..4.47 rows=10 width=0) |
|     	Index Cond: (draft_id = 1)                                                       	|

Before adding the index to this endpoint, it took about 0.0704ms to execute. After adding the index on draft_id in the teams table, the execution time was reduced to 0.0322ms. This is a significant improvement on the performance of our endpoint. The cost of the queries was also reduced from around 2000 to around 50 or less for each query.

### PUT /drafts/draft_id/start

1. 

| QUERY PLAN                                                            	|
| ------------------------------------------------------------------------- |
| Index Scan using drafts_pkey on drafts  (cost=0.29..8.30 rows=1 width=10) |
|   Index Cond: (draft_id = 1)                                          	|

2. 

| QUERY PLAN                                                                              	|
| ------------------------------------------------------------------------------------------- |
| GroupAggregate  (cost=2083.44..2083.46 rows=1 width=18)                                 	|
|   Group Key: drafts.draft_status                                                        	|
|   ->  Sort  (cost=2083.44..2083.44 rows=1 width=18)                                     	|
|     	Sort Key: drafts.draft_status                                                   	|
|     	->  Nested Loop Left Join  (cost=0.29..2083.43 rows=1 width=18)                 	|
|           	Join Filter: (drafts.draft_id = teams.draft_id)                           	|
|           	->  Index Scan using drafts_pkey on drafts  (cost=0.29..8.30 rows=1 width=18) |
|                 	Index Cond: (draft_id = 1)                                          	|
|           	->  Seq Scan on teams  (cost=0.00..2075.00 rows=10 width=16)              	|
|                 	Filter: (draft_id = 1)                                              	|

3. 

| QUERY PLAN                                                                       	|
| ------------------------------------------------------------------------------------ |
| Update on teams  (cost=2075.68..2158.72 rows=0 width=0)                          	|
|   CTE teams_list                                                                 	|
| 	->  WindowAgg  (cost=2075.19..2075.39 rows=10 width=24)                      	|
|       	->  Sort  (cost=2075.19..2075.22 rows=10 width=16)                     	|
|             	Sort Key: (random())                                             	|
|             	->  Seq Scan on teams teams_1  (cost=0.00..2075.03 rows=10 width=16) |
|                   	Filter: (draft_id = 1)                                     	|
|   ->  Nested Loop  (cost=0.29..83.33 rows=10 width=50)                           	|
|     	->  CTE Scan on teams_list  (cost=0.00..0.20 rows=10 width=56)           	|
|     	->  Index Scan using teams_pkey on teams  (cost=0.29..8.31 rows=1 width=14)  |
|           	Index Cond: (team_id = teams_list.team_id)                         	|

Similarly to the draft player endpoint, the start draft endpoint also experiences slow performance due to a sequential scan on the draft_id field in the teams endpoint. Queries 2 and 3 are causing the poor performance on this endpoint. The same improvement from the previous endpoint should also improve performance here. Since the index was already created, the code for it does not need to be run again. If it was not implemented previously, you would run:

CREATE INDEX teams_draft_id_index ON teams (draft_id);

| QUERY PLAN                                                                                       	|
| ---------------------------------------------------------------------------------------------------- |
| GroupAggregate  (cost=16.91..16.93 rows=1 width=18)                                              	|
|   Group Key: drafts.draft_status                                                                 	|
|   ->  Sort  (cost=16.91..16.91 rows=1 width=18)                                                  	|
|     	Sort Key: drafts.draft_status                                                            	|
|     	->  Nested Loop Left Join  (cost=0.58..16.90 rows=1 width=18)                            	|
|           	Join Filter: (drafts.draft_id = teams.draft_id)                                    	|
|           	->  Index Scan using drafts_pkey on drafts  (cost=0.29..8.30 rows=1 width=18)      	|
|                 	Index Cond: (draft_id = 1)                                                   	|
|           	->  Index Scan using teams_draft_id_index on teams  (cost=0.29..8.47 rows=10 width=16) |
|                 	Index Cond: (draft_id = 1)                                                   	|

| QUERY PLAN                                                                                                 	|
| -------------------------------------------------------------------------------------------------------------- |
| Update on teams  (cost=9.15..92.18 rows=0 width=0)                                                         	|
|   CTE teams_list                                                                                           	|
| 	->  WindowAgg  (cost=8.66..8.86 rows=10 width=24)                                                      	|
|       	->  Sort  (cost=8.66..8.68 rows=10 width=16)                                                     	|
|             	Sort Key: (random())                                                                       	|
|             	->  Index Scan using teams_draft_id_index on teams teams_1  (cost=0.29..8.49 rows=10 width=16) |
|                   	Index Cond: (draft_id = 1)                                                           	|
|   ->  Nested Loop  (cost=0.29..83.33 rows=10 width=50)                                                     	|
|     	->  CTE Scan on teams_list  (cost=0.00..0.20 rows=10 width=56)                                     	|
|     	->  Index Scan using teams_pkey on teams  (cost=0.29..8.31 rows=1 width=14)                        	|
|           	Index Cond: (team_id = teams_list.team_id)                                                   	|

Before adding the index, this endpoint executed in about 0.0581ms. After adding the index on draft_id in the teams table, execution time was reduced to 0.0363, which is much more in line with other endpoints of a similar type. Additionally, the cost of these queries was reduced from about 2000 to around 15 or less.

### POST /drafts/draft_id/join

1. 

| QUERY PLAN                                                           	|
| ------------------------------------------------------------------------ |
| Index Scan using drafts_pkey on drafts  (cost=0.29..8.30 rows=1 width=4) |
|   Index Cond: (draft_id = 1)                                         	|
|   Filter: (draft_status = 'pending'::text)                           	|

2. 

| QUERY PLAN                                                	|
| ------------------------------------------------------------- |
| Aggregate  (cost=2075.03..2075.04 rows=1 width=8)         	|
|   ->  Seq Scan on teams  (cost=0.00..2075.00 rows=10 width=0) |
|     	Filter: (draft_id = 1)                            	|

3.

| QUERY PLAN                                     	|
| -------------------------------------------------- |
| Insert on teams  (cost=0.00..0.01 rows=1 width=92) |
|   ->  Result  (cost=0.00..0.01 rows=1 width=92)	|

Same as the two previous endpoints, the join draft endpoint also suffered in performance due to a sequential scan on the teams table and the draft_id field. Query 2 was the only query in this endpoint that had a significant cost. Since this index has already been created, no further action is required. However, if the index was not created beforehand, it could be done with the following code: 

CREATE INDEX teams_draft_id_index ON teams (draft_id);

| QUERY PLAN                                                                               	|
| -------------------------------------------------------------------------------------------- |
| Aggregate  (cost=4.49..4.50 rows=1 width=8)                                              	|
|   ->  Index Only Scan using teams_draft_id_index on teams  (cost=0.29..4.47 rows=10 width=0) |
|     	Index Cond: (draft_id = 1)                                                       	|

Before adding the index, this endpoint executed in about 0.0357ms. After adding the index on draft_id in the teams table, execution time was reduced to 0.0162. Additionally, the cost of this query was reduced from about 2000 to around 5 or less.
