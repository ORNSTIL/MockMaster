import sys

def main():
    if len(sys.argv) != 4:
        sys.exit("Usage: python script.py input.csv output.csv year")

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    year = sys.argv[3]

    try:
        fin = open(input_file, "r")
        fout = open(output_file, "w")
    except IOError:
        sys.exit(1)
    
    header = fin.readline().strip()
    columns = header.split(',')
    fan_std_col = fan_ppr_col = 0
    for i in range(len(columns)):
        if columns[i] == "fantasy_points_standard":
            fan_std_col = i
            columns[i] = "fantasy_points_standard_10"
        if columns[i] == "fantasy_points_ppr":
            fan_ppr_col = i
            columns[i] = "fantasy_points_ppr_10"
    header = ",".join(columns) + ",year\n"
    fout.write(header)

    line = fin.readline()
    while line:
        line = line.strip().split(',')
        if len(line) > 1:
            name = line[0]
            if len(name) > 2:
                if name[-1] == '+' or name[-1] == '*':
                    name = name[:-1]
                if name[-1] == '+' or name[-1] == '*':
                    name = name[:-1]
            new_line = name
            new_line += ","
            for i in range(1, len(line)):
                if line[i] == "":
                    new_line += "0"
                elif i == fan_ppr_col or i == fan_std_col:
                    new_line += str(int(float(line[i]) * 10))
                elif i == 2:
                    if line[i] == "FB":
                        new_line += "RB"
                    else:
                        new_line += line[i]
                else:
                    new_line += line[i]
                new_line += ","
            new_line += year
            fout.write(new_line + "\n")
        line = fin.readline()
    
    fout.close()
    fin.close()

if __name__ == "__main__":
    main()
