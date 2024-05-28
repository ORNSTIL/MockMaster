from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel
from enum import Enum
import sqlalchemy
from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/players",
    tags=["players"],
    dependencies=[Depends(auth.get_api_key)],
)

class SearchPlayersResponse(BaseModel):
    previous: str
    next: str
    results: list[dict]

class PlayerStatisticsResponse(BaseModel):
    player_id: str
    seasons: list[dict]

class DraftPlayerRequest(BaseModel):
    team_id: int

class search_year_options(str, Enum):
    all = "all"
    y2023 = "2023"
    y2022 = "2022"
    y2021 = "2021"
    y2020 = "2020"
    y2019 = "2019"

class search_position_options(str, Enum):
    all = "all"
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"

class search_sort_options(str, Enum):
    player_name = "player_name"
    year = "year"
    age = "age"
    position = "position"
    team = "team"
    standard_fantasy_points = "standard_fantasy_points"
    ppr_fantasy_points = "ppr_fantasy_points"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/search/", response_model=SearchPlayersResponse)
def search_players(
    player_name: str = "",
    year: search_year_options = search_year_options.all,
    age: str = "",
    position: search_position_options = search_position_options.all,
    team: str = "",
    sort_col: search_sort_options = search_sort_options.ppr_fantasy_points,
    sort_order: search_sort_order = search_sort_order.desc,
    search_page: str = ""
):
    """
    Gets results according to specified search parameters and sort options. 
    Provides player_id, player_name, position, team, age, standard_fantasy_points, and ppr_fantasy_points for each result.
    """

    if search_page == "":
        offset = 0
        prev_token = ""
    else:
        offset = (int(search_page)-1)*10
        if offset == 0:
            prev_token = ""
        else:
            prev_token = str(int(search_page)-1)

    if sort_col is search_sort_options.player_name:
        if sort_order is search_sort_order.asc:
            order_by = db.player_points.c.player_name
        else:
            order_by = sqlalchemy.desc(db.player_points.c.player_name)
    elif sort_col is search_sort_options.year:
        if sort_order is search_sort_order.asc:
            order_by = db.player_points.c.year
        else:
            order_by = sqlalchemy.desc(db.player_points.c.year)
    elif sort_col is search_sort_options.age:
        if sort_order is search_sort_order.asc:
            order_by = db.player_points.c.age
        else:
            order_by = sqlalchemy.desc(db.player_points.c.age)
    elif sort_col is search_sort_options.position:
        if sort_order is search_sort_order.asc:
            order_by = db.player_points.c.position
        else:
            order_by = sqlalchemy.desc(db.player_points.c.position)
    elif sort_col is search_sort_options.team:
        if sort_order is search_sort_order.asc:
            order_by = db.player_points.c.team
        else:
            order_by = sqlalchemy.desc(db.player_points.c.team)
    elif sort_col is search_sort_options.standard_fantasy_points:
        if sort_order is search_sort_order.asc:
            order_by = db.player_points.c.fantasy_points_standard_10
        else:
            order_by = sqlalchemy.desc(db.player_points.c.fantasy_points_standard_10)
    elif sort_col is search_sort_options.ppr_fantasy_points:
        if sort_order is search_sort_order.asc:
            order_by = db.player_points.c.fantasy_points_ppr_10
        else:
            order_by = sqlalchemy.desc(db.player_points.c.fantasy_points_ppr_10)
    else:
        raise HTTPException(status_code=400, detail="Invalid sort column specified")

    stmt = (
        sqlalchemy
        .select(
            db.player_points.c.player_id,
            db.player_points.c.player_name,
            db.player_points.c.year,
            db.player_points.c.position,
            db.player_points.c.team,
            db.player_points.c.age,
            db.player_points.c.fantasy_points_standard_10,
            db.player_points.c.fantasy_points_ppr_10
        )
        .select_from(db.player_points)
        .limit(11)
        .offset(offset)
        .order_by(order_by)
    )

    if player_name != "":
        stmt = stmt.where(db.player_points.c.player_name.ilike(f"%{player_name}%"))
    if year != "all":
        stmt = stmt.where(db.player_points.c.year == year)
    if age != "":
        stmt = stmt.where(db.player_points.c.age == int(age))
    if position != "all":
        stmt = stmt.where(db.player_points.c.position.ilike(position))
    if team != "":
        stmt = stmt.where(db.player_points.c.team.ilike(f"%{team}%"))

    with db.engine.begin() as connection:
        result = connection.execute(stmt).fetchall()
        json = []
        if len(result) > 10:
            result = result[0:10]
            if search_page == "":
                next_token = "2"
            else:
                next_token = str(int(search_page)+1)
        else:
            next_token = ""

        for row in result:
            json.append(
                {
                    "player_id": row.player_id,
                    "player_name": row.player_name,
                    "year": row.year,
                    "age": row.age,
                    "position": row.position,
                    "team": row.team,
                    "standard_fantasy_points": row.fantasy_points_standard_10/10,
                    "ppr_fantasy_points": row.fantasy_points_ppr_10/10
                }
            )

        search_result = {"previous": prev_token, "next": next_token, "results": json}

    print(search_result)

    return search_result


@router.get("/{player_id}/", response_model=PlayerStatisticsResponse)
def get_player_statistics(player_id: str):
    """
    Gets all player statistics for all seasons for the specified player.
    """
    with db.engine.begin() as connection:
        stats = connection.execute(sqlalchemy.text("""
            SELECT player_id, year, age, position, team, games_played, games_started,
                   passing_yards, passing_tds, interceptions, rushing_atts, rushing_yards,
                   targets, receptions, receiving_yards, receiving_tds, fumbles, fumbles_lost,
                   two_point_conversions, fantasy_points_standard_10, fantasy_points_ppr_10,
                   rushing_tds, two_point_conversions_passing
            FROM stats
            WHERE player_id = :player_id"""), {'player_id': player_id}).mappings()

        seasons = []
        for season in stats:
            seasons.append({
                'year': season.year,
                'age': season.age,
                'position': season.position,
                'team': season.team,
                'games_played': season.games_played,
                'games_started': season.games_started,
                'passing_yards': season.passing_yards,
                'passing_tds': season.passing_tds,
                'interceptions': season.interceptions,
                'rushing_atts': season.rushing_atts,
                'rushing_yards': season.rushing_yards,
                'rushing_tds': season.rushing_tds,
                'targets': season.targets,
                'receptions': season.receptions,
                'receiving_yards': season.receiving_yards,
                'receiving_tds': season.receiving_tds,
                'fumbles': season.fumbles,
                'fumbles_lost': season.fumbles_lost,
                'two_point_conversions_passing': season.two_point_conversions_passing,
                'two_point_conversions': season.two_point_conversions,
                'fantasy_points_standard_10': season.fantasy_points_standard_10 / 10,
                'fantasy_points_ppr_10': season.fantasy_points_ppr_10 / 10
            })

        if len(seasons) <= 0:
            raise HTTPException(status_code=404, detail="Player statistics not found")

        player_statistics = {"player_id": player_id, "seasons": seasons}

    print(player_statistics)

    return {"player_id": player_id, "seasons": seasons}


@router.post("/{player_id}/draft")
def draft_player(player_id: str, request: DraftPlayerRequest):
    """
    Drafts a player to a team. The player must be available, it must be the team's pick, and the player pick must not violate minimum and maximum position restraints for a roster.
    """
    with db.engine.begin() as connection:
        draft_info = connection.execute(sqlalchemy.text("""
            SELECT teams.draft_id, drafts.draft_status, teams.draft_position, drafts.roster_size FROM teams
            JOIN drafts ON teams.draft_id = drafts.draft_id
            WHERE teams.team_id = :team_id
        """), {'team_id': request.team_id}).mappings().fetchone()

        if not draft_info:
            raise HTTPException(status_code=404, detail="Team not found")

        if draft_info['draft_status'] != 'active':
            raise HTTPException(status_code=409, detail="Draft not active")
        
        try:
            player_position = connection.execute(sqlalchemy.text("""
                SELECT position FROM stats WHERE player_id = :player_id
            """), {'player_id': player_id}).scalar_one()

        except:
            raise HTTPException(status_code=404, detail="Player not found")

        already_drafted = connection.execute(sqlalchemy.text("""
            SELECT EXISTS (
                SELECT 1 FROM selections
                JOIN teams ON selections.team_id = teams.team_id
                WHERE teams.draft_id = :draft_id AND selections.player_id = :player_id
            )
        """), {'draft_id': draft_info['draft_id'], 'player_id': player_id}).scalar_one()

        if already_drafted:
            raise HTTPException(status_code=409, detail="Player already drafted in this draft")

        previous_picks = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM selections
            JOIN teams ON selections.team_id = teams.team_id
            WHERE teams.draft_id = :draft_id
        """), {'draft_id': draft_info['draft_id']}).scalar_one()

        number_of_teams = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM teams
            WHERE draft_id = :draft_id
        """), {'draft_id': draft_info['draft_id']}).scalar_one()

        last_round = previous_picks // number_of_teams
        if last_round % 2 == 1:
            current_pick = number_of_teams - (previous_picks % number_of_teams)
        else:
            current_pick = (previous_picks % number_of_teams) + 1

        if current_pick != draft_info['draft_position']:
            raise HTTPException(status_code=403, detail="Not your turn to draft")
        
        total_selections = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM selections
            WHERE team_id = :team_id
        """), {'team_id': request.team_id}).scalar_one()
        remaining_picks = draft_info['roster_size'] - total_selections

        positions_needed = {}
        total_needed_picks = 0
        positions = connection.execute(sqlalchemy.text("""
            SELECT position, min FROM position_requirements
            WHERE draft_id = :draft_id
        """), {'draft_id': draft_info['draft_id']}).mappings().fetchall()
        
        for pos in positions:
            count = connection.execute(sqlalchemy.text("""
                SELECT COUNT(*) FROM selections
                JOIN stats ON selections.player_id = stats.player_id
                WHERE selections.team_id = :team_id AND stats.position = :position
            """), {'team_id': request.team_id, 'position': pos['position']}).scalar_one()
 
            needed = max(0, pos['min'] - count)
            positions_needed[pos['position']] = needed
            total_needed_picks += needed

        current_count = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM selections
            JOIN stats ON selections.player_id = stats.player_id
            WHERE selections.team_id = :team_id AND stats.position = :position
        """), {'team_id': request.team_id, 'position': player_position}).scalar_one()

        max_allowed = connection.execute(sqlalchemy.text("""
            SELECT max FROM position_requirements
            WHERE draft_id = :draft_id AND position = :position
        """), {'draft_id': draft_info['draft_id'], 'position': player_position}).scalar_one()

        if total_needed_picks >= remaining_picks and positions_needed[player_position] < 1:
            raise HTTPException(status_code=409, detail="Cannot draft player; minimum positions not met. Current requirements:" + str(positions_needed))
        elif current_count >= max_allowed:
            raise HTTPException(status_code=409, detail=f"Maximum number of {player_position} players reached")
        
        connection.execute(sqlalchemy.text("""
            INSERT INTO selections (team_id, player_id, when_selected)
            VALUES (:team_id, :player_id, :when_selected)
        """), {'team_id': request.team_id, 'player_id': player_id, 'when_selected': previous_picks + 1})

        total_possible_picks = number_of_teams * draft_info['roster_size']
        if previous_picks + 1 == total_possible_picks:
            connection.execute(sqlalchemy.text("""
                UPDATE drafts SET draft_status = 'ended'
                WHERE draft_id = :draft_id
            """), {'draft_id': draft_info['draft_id']})

        return {"message": "Player drafted successfully"}
