

def main(file_in, file_out):
    fin = open(file_in, "r")
    fout = open(file_out, "w")
    
    line = fin.readline()
    fout.write(line)
    line = line.split(',')
    fan_std_col = fan_ppr_col = 0
    for i in range(len(line)):
        if line[i] == "fantasy_points_standard":
            fan_std_col = i
        if line[i] == "fantasy_points_ppr":
            fan_ppr_col = i
        
    line = fin.readline()
    line = line.split(',')

    player_names = {}
    repeated_players = {}
    
    print(fan_std_col, fan_ppr_col)
    count = 0
    while line != "" or line != None:
        count += 1
        if len(line) > 1:
            name = line[0]
            if len(name) > 2:
                if name[-1] == '+' or name[-1] == '*':
                    name = name[:-1]
                if name[-1] == '+' or name[-1] == '*':
                    name = name[:-1]
            if name not in player_names:
                player_names[name] = 1
            else:
                if name not in repeated_players:
                    repeated_players[name] = 1
                else:
                    repeated_players[name] += 1
            new_line = name
            new_line += ","
            for i in range(1, len(line)):
                if line[i] == "":
                    new_line += "0"
                elif i == fan_ppr_col or i == fan_std_col:
                    new_line += str(int(float(line[i]) * 10))
                else:
                    new_line += line[i]
                new_line += ","
            new_line = new_line[:-1]
            fout.write(new_line)
            line = fin.readline()
            if line == "" or None:
                break
            line = line.split(',')

    for name in repeated_players.keys():
        print(f"{name} repeated {repeated_players[name]} times")

    print("DONE")
    print("number of lines: ", count)

    fout.close()
    fin.close()

if __name__=="__main__":
    main("2022_player_stats_old.txt", "2022_player_stats.csv")