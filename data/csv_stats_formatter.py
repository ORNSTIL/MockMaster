import sys

def main():
    if len(sys.argv) != 3:
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        fin = open(input_file, "r")
        fout = open(output_file, "w")
    except IOError:
        sys.exit(1)
    
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
    
    print(fan_std_col, fan_ppr_col)
    while line != None:
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
                else:
                    new_line += line[i]
                new_line += ","
            new_line = new_line[:-1]
            fout.write(new_line)
            line = fin.readline()
            line = line.split(',')
    fout.close()
    fin.close()

if __name__=="__main__":
    main()