# create 8,696 draft instances
# drafts = 8,696 rows
# position requirements = 34,784 rows
# teams = 86,960 rows
# selections = 869,600
# across all tables = 1,000,040 rows

# import modules
import csv

# generate fake draft data
with open("fake/fake_drafts.csv", mode="w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow(["draft_name","draft_type","roster_size","draft_size","draft_status"])

    i = 1
    while i <= 8696:
        draft_name = f"Fake Draft {i}"
        if i%2 == 0:
            draft_type = "PPR"
        else:
            draft_type = "Standard"
        roster_size = 10
        draft_size = 10
        draft_status = "completed"
        
        writer.writerow([draft_name, draft_type, roster_size, draft_size, draft_status])

        i = i + 1

# generate fake position requirements data
with open("fake/fake_position_requirements.csv", mode="w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow(["draft_id","position","min","max"])

    i = 1
    while i <= 8696:
        for pos in ["QB", "RB", "WR", "TE"]:
            draft_id = i
            position = pos
            min = 1
            max = 4
            
            writer.writerow([draft_id, position, min, max])

        i = i + 1

# generate fake team data
with open("fake/fake_teams.csv", mode="w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow(["team_name","user_name","draft_position","draft_id"])

    i = 1
    while i <= 8696:
        j = 1
        while j <= 10:
            team_id = (i-1)*10 + j
            team_name = f"Fake Team {(i-1)*10 + j}"
            user_name = f"Fake User {(i-1)*10 + j}"
            draft_position = j
            draft_id = i
        
            writer.writerow([team_name, user_name, draft_position, draft_id])

            j = j + 1
        i = i + 1

# ids of players to be drafted (20 QB, 30 RB, 30WR, 20TE)
player_ids = [
    "JackLa00", "PresDa01", "WilsRu00", "WatsDe00", "MahoPa00", "MurrKy00", "RodgAa00", "RyanMa00", "BreeDr00", "TannRy00",
    "WentCa00", "DarnSa00", "CarrDe02", "CousKi00", "AlleJo02", "MayfBa00", "KeenCa00", "RiddDe00", "WalkPh00", "BridTe00",
    "McCaCh01", "HenrDe00", "JoneAa00", "ElliEz00", "CookDa01", "ChubNi00", "IngrMa01", "EkelAu00", "CarsCh00", "BarkSa00",
    "MixoJo00", "GurlTo01", "DrakKe00", "MontDa01", "MichSo00", "FreeDe00", "HydeCa00", "JohnDu00", "MostRa00", "SandEm00",
    "ConnJa00", "ColeTe01", "PerrBr02", "BarbPe01", "HowaJo00", "PennRa00", "KnigZo00", "HuntCa02", "BreiMa00", "JuszKy00",
    "LindPh00", "WallDa01", "KelcTr00", "AndrMa00", "KittGe00", "CookJa02", "HoopAu00", "PruiMy00", "ThomLo00", "GoedDa00",
    "HillTa00", "HigbTy00", "McLaTe00", "EvanMi00", "GesiMi00", "HenrHu00", "TonyRo00", "LikeIs00", "DissWi00", "OttoCa00",
    "CookDa01", "ThomMi05", "GodwCh00", "GollKe00", "KuppCo00", "JoneJu02", "LandJa00", "MoorD.00", "WoodRo02", "BrowAJ00",
    "HopkDe00", "RobiAl02", "CharDJ00", "LockTy00", "BoydTy00", "RidlCa00", "SuttCo00", "DiggSt00", "BeckOd00", "AlleKe00",
    "WillMi07", "SlayDa01", "SamuDe00", "KirkCh01", "HardMe00", "PascZa00", "JameRi00", "ShahRa00", "ZaccOl01", "ReynJo00"
]

# generate fake selection data
with open("fake/fake_selections.csv", mode="w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow(["team_id","player_id","when_selected"])

    i = 1
    while i <= 8696:
        k = 1
        while k <= 10:
            j = 1
            while j <= 10:
                team_id = (i-1)*10 + j
                when_selected = (k-1)*10 + j
                player_id = player_ids[when_selected-1]
            
                writer.writerow([team_id, player_id, when_selected])

                j = j + 1
            k = k + 1
        i = i + 1
