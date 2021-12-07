import re


# verify that the command is valid
# TODO: study other cases in which a command is not valid
def validate_command(command):
    options = 0
    if "-b" in command or "--bytes" in command:
        options += 1
    if "-c" in command or "--characters" in command:
        options += 1
    if "-f" in command or "--fields" in command:
        options += 1
    if options != 1:
        return False
    return True


# read file with a given name
def read_file(file_name):
    f = open(file_name, "r")
    lines = f.readlines()
    lines_modified = [line[:-1] for line in lines]
    # print(lines_modified)
    return lines_modified


# execute the command
def process_command(command, delim):
    # validation = validate_command(command)
    files = [file for file in command if ".txt" in file]
    # print(files)
    options = [opt for opt in command if len(opt) > 1 and "-" == opt[0] and (opt[1].isdigit() is False)]
    # print(options)
    ranges = [ran for ran in command if ran not in files and any(map(str.isdigit, ran))]
    # print(ranges)

    if "-b" in options or "--bytes" in options:
        bytes_characters_command(command, files, options, ranges)  # -b option
    elif "-c" in options or "--characters" in options:
        bytes_characters_command(command, files, options, ranges)  # -c option
    elif "-f" in options or "--fields" in options:
        fields_command(command, files, options, ranges, delim)  # -f option
    # TODO:--output-delimiter and -z


# -b, -c options
def bytes_characters_command(command, files, options, ranges):
    for file in files:
        lines = read_file(file)
        for line in lines:
            if "--complement" in options:
                text = line
            else:
                text = ""
            for r in ranges:
                if "-" in r:
                    r_split = r.split("-")
                    a = 0
                    b = len(line)
                    if r_split[0].isnumeric():
                        a = int(r_split[0]) - 1
                    if r_split[1].isnumeric():
                        b = int(r_split[1])
                    if "--complement" in options:
                        text = text.replace(line[a:b][:], '')
                    else:
                        text = text + line[a:b][:]
                else:
                    if "--complement" in options:
                        text = text.replace(line[int(r) - 1][:], '')
                    else:
                        text = text + line[int(r) - 1][:]
            print(text)


# -f,-d options
def fields_command(command, files, options, ranges, delim):
    for file in files:
        lines = read_file(file)
        if "-d" not in options and "--delimiter" not in options:
            print('\n'.join(lines))
        else:
            print_lines_no_delim = False
            printable = True
            for line in lines:
                if "-s" in options or "--only-delimited" in options:
                    print_lines_no_delim = True
                if print_lines_no_delim is True and line.find(delim) == -1:
                    printable = False
                if printable is True:
                    if line.find(delim) == -1:
                        print(line)
                    else:
                        line_delimited = line.split(delim)
                        line_delimited_1 = [x + delim for x in line_delimited]
                        if "--complement" in options:
                            text = line
                        else:
                            text = ""
                        for r in ranges:
                            if "-" in r:
                                r_split = r.split("-")
                                a = 0
                                b = len(line_delimited)
                                if r_split[0].isnumeric():
                                    a = int(r_split[0]) - 1
                                if r_split[1].isnumeric() and int(r_split[1].isnumeric()) < len(line_delimited):
                                    b = int(r_split[1])
                                if "--complement" in options:
                                    text = text.replace("".join(line_delimited_1[a:b][:]), '')
                                else:
                                    text = text + delim.join(line_delimited[a:b][:])
                            else:
                                if (int(r) - 1) < len(line_delimited):
                                    if "--complement" in options:
                                        text = text.replace("".join(line_delimited_1[int(r) - 1][:]), '')
                                    else:
                                        text = text + "".join(line_delimited[int(r) - 1][:]) + delim
                        print(text)


print("Insert command:")
com = str(input())
# print(com)
delim = ""
if com.find("-d") or com.find("--delimiter"):
    index = com.find("\"")
    delim = com[index + 1]
# print(delim)
command = re.split('[ ,]', com)
process_command(command, delim)
