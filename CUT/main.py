import re
from sys import stdin
import numpy as np


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
def process_command(command, delim, output_delim):
    # validation = validate_command(command)
    files = [file for file in command if ".txt" in file]
    # print(files)
    options = [opt for opt in command if len(opt) > 1 and "-" == opt[0] and (opt[1].isdigit() is False)]
    # print(options)
    ranges = [ran for ran in command if ran not in files and any(map(str.isdigit, ran))]
    # print(ranges)

    if "--help" in options:
        help_command()
    elif "--version" in options:
        version_command()

    if len(files) != 0:
        for file in files:
            lines = read_file(file)
            if "-z" in options or "--zero-terminated" in options:
                z_command(command, lines, options, ranges, delim, output_delim)
            elif "-b" in options or "--bytes" in options:
                bytes_characters_command(command, lines, options, ranges)  # -b option
            elif "-c" in options or "--characters" in options:
                bytes_characters_command(command, lines, options, ranges)  # -c option
            elif "-f" in options or "--fields" in options:
                fields_command(command, lines, options, ranges, delim, output_delim)  # -f option
    else:
        nr_line = 0
        zero_terminated = False
        for line in stdin:
            # print(len(line))
            if line.rstrip() == '^C':
                break
            if nr_line == 0 and "-z" in options or "--zero-terminated" in options:
                z_command_line(command, line, options, ranges, delim, output_delim)
                zero_terminated = True
            if zero_terminated is False:
                if "-b" in options or "--bytes" in options:
                    bytes_characters_command_line(command, line, options, ranges)  # -b option
                elif "-c" in options or "--characters" in options:
                    bytes_characters_command_line(command, line, options, ranges)  # -c option
                elif "-f" in options or "--fields" in options:
                    fields_command_line(command, line, options, ranges, delim, output_delim)  # -f option
            else:
                if nr_line > 0:
                    print(line, end="")
            nr_line += 1
    # TODO:-z


# -b, -c options
def bytes_characters_command(command, lines, options, ranges):
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


# -b, -c options
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


# -f,-d options
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


# -f,-d options line
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


def z_command(command, lines, options, ranges, delim, output_delim):
    if "-b" in options or "--bytes" in options:
        bytes_characters_command_line(command, lines[0], options, ranges)  # -b option
    elif "-c" in options or "--characters" in options:
        bytes_characters_command_line(command, lines[0], options, ranges)  # -c option
    elif "-f" in options or "--fields" in options:
        fields_command_line(command, lines[0], options, ranges, delim, output_delim)  # -f option
    for line in lines[1:]:
        print(line)


def z_command_line(command, line, options, ranges, delim, output_delim):
    if "-b" in options or "--bytes" in options:
        bytes_characters_command_line(command, line, options, ranges)  # -b option
    elif "-c" in options or "--characters" in options:
        bytes_characters_command_line(command, line, options, ranges)  # -c option
    elif "-f" in options or "--fields" in options:
        fields_command_line(command, line, options, ranges, delim, output_delim)  # -f option


def help_command():
    f = open("help.txt", "r")
    print(f.read())


def version_command():
    f = open("version.txt", "r")
    print(f.read())


print("Insert command:")
com = str(input())
# print(com)
delim = ""
output_delim = ""
if com.find("-d") or com.find("--delimiter"):
    index = com.find("\"")
    delim = com[index + 1]
    output_delim = delim
    if com.find("--output-delimiter") != -1:
        index_1 = com.find("\"", com.find("--output-delimiter"))
        output_delim = com[index_1 + 1]

# print("Delimiter:")
# print(delim)
# print("Output delimiter:")
# print(output_delim)
command = re.split('[ ,]', com)
process_command(command, delim, output_delim)
