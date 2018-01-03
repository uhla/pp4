import re
import subprocess

from scripts.util import parser
from scripts.util.parser import skip_blank_lines, read_tabbed, read_until_blank, parse_files


class Changelist:
    def __init__(self, number, user, workspace, datestr, description="", affected_files=None, shelved_files=None,
                 stream="", pending=None, differences=None):
        if shelved_files is None:
            shelved_files = []
        if affected_files is None:
            affected_files = []

        self.number = number
        self.user = user
        self.workspace = workspace
        self.datestr = datestr
        self.description = description
        self.affected_files = affected_files
        self.shelved_files = shelved_files
        self.stream = stream
        self.pending = pending
        self.differences = differences

    def __repr__(self, *args, **kwargs):
        return repr(self.__dict__)


def pp4_describe_changelist(changelist):
    process = subprocess.run(["pp4", "describe", "-S", "-s", str(changelist)], stdout=subprocess.PIPE,
                             universal_newlines=True, check=True)

    return parse_describe_changelist(process.stdout)


def parse_describe_changelist(text):
    if isinstance(text, str):
        output = text.split("\n")
    else:
        output = text

    first = output.pop(0)
    m = re.search(
        "Change (?P<number>[0-9]+) by (?P<user>[^@]+)@(?P<workspace>[^ ]+) on (?P<datestr>[0-9/]+ [0-9:]+) *(?P<pending>\*pending\*)?",
        first)
    if not m:
        raise Exception("Unable to parse line " + first)

    changelist = Changelist(**m.groupdict())

    output = skip_blank_lines(output)
    #print("\n".join(output))
    description, output = read_tabbed(output)
    changelist.description = "\n".join(description)

    output = skip_blank_lines(output)
    while output:
        title = output.pop(0)
        if "Affected files" in title:
            output = skip_blank_lines(output)
            files, output = read_until_blank(output)
            changelist.affected_files = parse_files(files)
        elif "Shelved files" in title:
            output = skip_blank_lines(output)
            files, output = read_until_blank(output)
            changelist.shelved_files = parse_files(files)
        elif title.startswith("Differences ..."):
            output = skip_blank_lines(output)
            changelist.differences = output
            output = []



    streams = set()
    if changelist.affected_files:
        for f in changelist.affected_files:
            path = f[0].split("/")
            stream_path = "/".join(path[:4])
            streams.add(stream_path)

    if changelist.shelved_files:
        for f in changelist.shelved_files:
            path = f[0].split("/")
            stream_path = "/".join(path[:4])
            streams.add(stream_path)

    changelist.stream = list(streams)

    return changelist


def workspace_from_changelist(changelist):
    return pp4_describe_changelist(changelist).workspace


def stream_from_changelist(changelist):
    return pp4_describe_changelist(changelist).stream


def pp4_describe_client(client=None):
    args = ["pp4", "client", "-o"]
    if client:
        args.append(str(client))
    process = subprocess.run(args, stdout=subprocess.PIPE,
                             universal_newlines=True, check=True)
    output = process.stdout.split("\n")
    result = parser.parse_listing(output)
    return result


def stream_from_workspace(client):
    return pp4_describe_client(client)["Stream"]


def get_current_workspace():
    return pp4_describe_client()["Client"]
