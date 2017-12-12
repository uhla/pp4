import re


def __strip(line):
    return line.strip(" \t\n\r")


def skip_blank_lines(text):
    start = -1
    for i, line in enumerate(text):
        line = __strip(line)
        if not line or line.startswith("#"):
            start = i
        else:
            break
    return text[start + 1:]


def read_tabbed(text):
    rest = -1
    result = []
    for i, line in enumerate(text):
        if line.startswith("\t"):
            result.append(__strip(line))
            rest = i
        else:
            break

    return result, text[rest + 1:]


def read_until_blank(text):
    rest = -1
    result = []
    for i, line in enumerate(text):
        if __strip(line):
            result.append(line)
            rest = i
        else:
            break
    return result, text[rest + 1:]


def parse_files(files):
    parsed = []
    for f in files:
        m = re.search('\.\.\. ([^#]+)#([0-9a-z]+) ([^ ]*)', f)
        if m:
            parsed.append((m[1], m[2], m[3]))

    return parsed


def parse_listing(lines):
    result = {}
    lines = skip_blank_lines(lines)
    while lines:
        line = lines.pop(0)
        if ":" in line:
            line = line.split(":", maxsplit=1)
            key, value = line
            value = __strip(value)
            if not value:
                value, lines = read_tabbed(lines)
                value = "\n".join(value)
            result[key] = value
        lines = skip_blank_lines(lines)

    return result
