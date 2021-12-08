import re
import sys
from sys import stdin
import os

valid_options = ["-b", "--bytes", "-c", "--characters", "-f", "--fields", "-n", "-z", "--zero-terminated",
                 "--complement", "-s", "--only-delimited", "--output-delimiter", "--help", "--version", "-d",
                 "--delimiter"]

valid_options_range = ["-b", "--bytes", "-c", "--characters", "-f", "--fields"]
valid_options_range_check = [0, 0, 0]

more_info = "Try 'cut --help' for more information."


# there are not -b,-c,-f options
def valid_option_primary_check(options):
    if len(options) == 0:
        return False
    exist = False
    for option in options:
        if option in valid_options_range:
            exist = True
    return exist


# invalid option
def valid_option_check(options):
    for option in options:
        if option not in valid_options:
            return option
    return True


# verify first word "cut"
def cut_first_word(command):
    if command[0] != "cut":
        return command[0]
    return True


# verify that ranges are placed after options
def numbers_after_options(command, options, ranges):
    for option in options:
        if option in valid_options_range:
            position = command.index(option)
            if position + 1 >= len(command) or command[position + 1] not in ranges:
                return False
    return True


# some commands must not appear 2 times
def only_one_range_option(options):
    for option in options:
        if option in valid_options_range:
            valid_options_range_check[int((valid_options_range.index(option)) / 2)] = \
                valid_options_range_check[int((valid_options_range.index(option)) / 2)] + 1
    nr_options = 0
    for val in valid_options_range_check:
        if val > 1:
            return False
        elif val == 1:
            nr_options += 1
    if nr_options > 1:
        return False
    return True


# verify if the files exist
def verify_file_exists(command, files):
    for file in files:
        if os.path.isfile(file) is False:
            return file
    return True


# verify if command is valid
def validate_command(command, options, ranges, files):
    valid = True
    if cut_first_word(command) is not True:
        print(cut_first_word(command), end="")
        print(":command not found")
        valid = False
    elif valid_option_primary_check(options) is False:
        print("cut: you must specify a list of bytes, characters or fields")
        valid = False
    elif valid_option_check(options) is not True:
        print("cut: invalid option -- \'" + valid_option_check(options) + "\'")
        valid = False
    elif numbers_after_options(command, options, ranges) is False:
        print("cut: invalid byte, character or field list")
        valid = False
    elif only_one_range_option(options) is False:
        print("cut: only one type of list may be specified")
        valid = False
    elif verify_file_exists(command, files) is not True:
        print("cut: " + verify_file_exists(command, files) + " : No such file or directory")
        valid = False
    if valid is False:
        print(more_info)
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
def process_command(command, delim, output_delim):
    # separate the command in files, options and ranges
    files = [file for file in command if ".txt" in file]
    # print(files)
    options = [opt for opt in command if len(opt) > 1 and "-" == opt[0] and (opt[1].isdigit() is False)]
    # print(options)
    ranges = [ran for ran in command if ran not in files and any(map(str.isdigit, ran))]
    # print(ranges)

    # verify if the command is valid
    valid = validate_command(command, options, ranges, files)
    if valid is True:
        if "--help" in options:
            help_command()
        elif "--version" in options:
            version_command()

        # if the input is from files
        if len(files) != 0:
            for file in files:
                lines = read_file(file)
                if "-z" in options or "--zero-terminated" in options:
                    z_command(command, lines, options, ranges, delim, output_delim)  # -z option
                elif "-b" in options or "--bytes" in options:
                    bytes_characters_command(command, lines, options, ranges)  # -b option
                elif "-c" in options or "--characters" in options:
                    bytes_characters_command(command, lines, options, ranges)  # -c option
                elif "-f" in options or "--fields" in options:
                    fields_command(command, lines, options, ranges, delim, output_delim)  # -f option
        # standard input
        else:
            nr_line = 0
            zero_terminated = False
            for line in stdin:
                # print(len(line))
                # end the input strings
                if line.rstrip() == '^C':
                    break
                # verify if it's the first line and that -z is an option
                if nr_line == 0 and "-z" in options or "--zero-terminated" in options:
                    z_command_line(command, line, options, ranges, delim, output_delim)  # -z option
                    zero_terminated = True
                # verify that -z is not in options
                if zero_terminated is False:
                    if "-b" in options or "--bytes" in options:
                        bytes_characters_command_line(command, line, options, ranges)  # -b option
                    elif "-c" in options or "--characters" in options:
                        bytes_characters_command_line(command, line, options, ranges)  # -c option
                    elif "-f" in options or "--fields" in options:
                        fields_command_line(command, line, options, ranges, delim, output_delim)  # -f option
                else:
                    # if -z is in options, just the first line will suffer changes and the others will stay the same
                    if nr_line > 0:
                        print(line, end="")
                nr_line += 1


# -b, -c options for files
def bytes_characters_command(command, lines, options, ranges):
    for line in lines:
        if "--complement" in options:
            text = line
        else:
            text = ""
        for r in ranges:
            # r=a-b,-b,a-
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
            # r=nr
            else:
                if "--complement" in options:
                    text = text.replace(line[int(r) - 1][:], '')
                else:
                    text = text + line[int(r) - 1][:]
        print(text)


# -b, -c options for standard input
def bytes_characters_command_line(command, line, options, ranges):
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


# -f,-d options for files
def fields_command(command, lines, options, ranges, delim, output_delim):
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
                    line_delimited_1 = [x + output_delim for x in line_delimited]
                    if "--complement" in options:
                        text = line
                        text = text.replace(delim, output_delim)
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
                                text = text + output_delim.join(line_delimited[a:b][:]) + output_delim
                        else:
                            nr = int(r) - 1
                            if nr < len(line_delimited):
                                if "--complement" in options:
                                    text = text.replace(line_delimited_1[nr][:], '')
                                else:
                                    text = text + line_delimited[nr][:] + output_delim
                    if text[-1] == output_delim:
                        text = text[:-1]
                    print(text)


# -f,-d options line for standard input
def fields_command_line(command, line, options, ranges, delim, output_delim):
    if "-d" not in options and "--delimiter" not in options:
        print(line)
    else:
        print_lines_no_delim = False
        printable = True
        if "-s" in options or "--only-delimited" in options:
            print_lines_no_delim = True
        if print_lines_no_delim is True and line.find(delim) == -1:
            printable = False
        if printable is True:
            if line.find(delim) == -1:
                print(line)
            else:
                line_delimited = line.split(delim)
                line_delimited_1 = [x + output_delim for x in line_delimited]
                if "--complement" in options:
                    text = line
                    text = text.replace(delim, output_delim)
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
                            text = text + output_delim.join(line_delimited[a:b][:])
                    else:
                        nr = int(r) - 1
                        if nr < len(line_delimited):
                            if "--complement" in options:
                                text = text.replace(line_delimited_1[nr][:], '')
                            else:
                                text = text + line_delimited[nr][:] + output_delim
                if text[-1] == output_delim:
                    text = text[:-1]
                print(text)


# -z option for files
def z_command(command, lines, options, ranges, delim, output_delim):
    if "-b" in options or "--bytes" in options:
        bytes_characters_command_line(command, lines[0], options, ranges)  # -b option
    elif "-c" in options or "--characters" in options:
        bytes_characters_command_line(command, lines[0], options, ranges)  # -c option
    elif "-f" in options or "--fields" in options:
        fields_command_line(command, lines[0], options, ranges, delim, output_delim)  # -f option
    for line in lines[1:]:
        print(line)


# -z option for standard input
def z_command_line(command, line, options, ranges, delim, output_delim):
    if "-b" in options or "--bytes" in options:
        bytes_characters_command_line(command, line, options, ranges)  # -b option
    elif "-c" in options or "--characters" in options:
        bytes_characters_command_line(command, line, options, ranges)  # -c option
    elif "-f" in options or "--fields" in options:
        fields_command_line(command, line, options, ranges, delim, output_delim)  # -f option


# --help option
def help_command():
    f = open("help.txt", "r")
    print(f.read())


# --version option
def version_command():
    f = open("version.txt", "r")
    print(f.read())


# read the command as a string
com = " ".join(sys.argv[1:])
# print(com)

delim = ""
output_delim = ""

# if -d option is present, then we will have a delimiter
if com.find("-d") or com.find("--delimiter"):
    index = sys.argv.index('-d') + 1
    delim = sys.argv[index]
    # output_delimiter will be the same as delimiter if the --output-delimiter is not present
    output_delim = delim
    # if --output-delimiter option is present, then we will have an output_delimiter
    if com.find("--output-delimiter") != -1:
        index_1 = sys.argv.index('--output-delimiter') + 1
        output_delim = sys.argv[index_1]

# print("Delimiter:")
# print(delim)
# print("Output delimiter:")
# print(output_delim)

# split the initial command string in substrings
command = re.split(' |,|=', com)
# print(command)
# process the split command
process_command(command, delim, output_delim)
