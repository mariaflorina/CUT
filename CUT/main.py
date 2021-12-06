import re


# verify that the command is valid
# TODO: study other casses in which a command is not valid
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
    command = re.split(' |,', str(input()))
    return command


# read file with a given name
def read_file(file_name):
    f = open(file_name, "r")
    lines = f.readlines()
    lines_modified = [line[:-1] for line in lines]
    # print(lines_modified)
    return lines_modified


# execute the command (only -b done)
def process_command(command):
    validation = validate_command(command)
    if validation is True:
        print(command)
    files = [file for file in command if ".txt" in file]
    # print(files)
    options = [opt for opt in command if len(opt) > 1 and "-" == opt[0] and (opt[1].isdigit() is False)]
    # print(options)
    ranges = [ran for ran in command if ran not in files and any(map(str.isdigit, ran))]
    # print(ranges)
    bytes_command(command, files, options, ranges)  # -b option
    # TODO: -c and -f


# read range for -b
def read_range_bytes(command, lines, options, ranges):
    for line in lines:
        text = ""
        for r in ranges:
            if "-" in r:
                a = int(r[0]) - 1
                b = int(r[2])
                text = text + line[a:b][:]
            else:
                text = text + line[int(r[0]) - 1][:]
        print(text)


# -b option
def bytes_command(command, files, options, ranges):
    for file in files:
        lines = read_file(file)
        read_range_bytes(command, lines, options, ranges)


process_command(read_command())
