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


# read command from console
def read_command():
    print("Insert command:")
    return str(input())


# read file with a given name
def read_file(file_name):
    f = open(file_name, "r")
    lines = f.readlines()
    lines_modified = [line[:-1] for line in lines]
    # print(lines_modified)
    return lines_modified


# execute the command (only -b done)
def process_command(command, delim):
    validation = validate_command(command)
    if validation is True:
        print(command)
    files = [file for file in command if ".txt" in file]
    print(files)
    options = [opt for opt in command if len(opt) > 1 and "-" == opt[0] and (opt[1].isdigit() is False)]
    print(options)
    ranges = [ran for ran in command if ran not in files and any(map(str.isdigit, ran))]
    print(ranges)

    if "-b" in options or "--bytes" in options:
        bytes_characters_command(command, files, options, ranges)  # -b option
    elif "-c" in options or "--characters" in options:
        bytes_characters_command(command, files, options, ranges)  # -c option
    elif "-f" in options or "--fields" in options:
        fields_command(command, files, options, ranges, delim)  # -f option
    # TODO: --complement and -s


# read range for -b, -c
def read_range_bytes_characters(command, lines, options, ranges):
    for line in lines:
        text = ""
        for r in ranges:
            if "-" in r:
                a = 0
                b = len(line)
                if r[0].isdigit():
                    a = int(r[0]) - 1
                if len(r) > 2 and r[2].isdigit():
                    b = int(r[2])
                elif len(r) > 1 and r[1].isdigit():
                    b = int(r[1])
                text = text + line[a:b][:]
            else:
                text = text + line[int(r[0]) - 1][:]
        print(text)


# -b, -c option
def bytes_characters_command(command, files, options, ranges):
    for file in files:
        lines = read_file(file)
        read_range_bytes_characters(command, lines, options, ranges)


def read_delimiter_fields(command, lines, options, ranges, delim):
    for line in lines:
        line_delimited = line.split(delim)
        text = ""
        for r in ranges:
            if "-" in r:
                a = 0
                b = len(line_delimited)
                if r[0].isdigit():
                    a = int(r[0]) - 1
                if len(r) > 2 and r[2].isdigit():
                    b = int(r[2])
                elif len(r) > 1 and r[1].isdigit():
                    b = int(r[1])
                text = text + " ".join(line_delimited[a:b][:])
            else:
                text = text + " ".join(line_delimited[int(r[0]) - 1][:])
        print(text)


def fields_command(command, files, options, ranges, delim):
    for file in files:
        lines = read_file(file)
        if "-d" not in options and "--delimiter" not in options:
            print('\n'.join(lines))
        else:
            read_delimiter_fields(command, lines, options, ranges, delim)


com = read_command()
print(com)
delim = ""
if com.find("-d") or com.find("--delimiter"):
    index = com.find("\"")
    delim = com[index + 1]
print(delim)
command = re.split(' |,', com)
process_command(command, delim)
