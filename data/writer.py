import pandas
import sys

def main():
    if len(sys.argv) != 6:
        sys.exit("Usage: python script.py file1.csv file2.csv file3.csv file4.csv file5.csv")

    dfs = [pandas.read_csv(file) for file in sys.argv[1:]]

    df = pandas.concat(dfs, ignore_index=True)

    df.drop(columns=['name']).to_csv('stats.csv', index=False)

    unique_players = df[['player_id', 'name']].drop_duplicates()
    unique_players.rename(columns={'name': 'player_name'}, inplace=True)
    unique_players.to_csv('players.csv', index=False)

if __name__ == "__main__":
    main()
