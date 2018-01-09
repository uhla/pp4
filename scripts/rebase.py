#!/usr/bin/python3

import argparse
import os
import re
import subprocess

import sys

from scripts.diff import pp4_diff
from scripts.patch import pp4_patch
from scripts.util.util import pp4_describe_changelist, pp4_describe_client, parse_describe_changelist, Capturing

IN_PROGRESS = "pp4rebase-in-progress"


def apply_line(line, last_changelist=None):
    line = line.split()

    if line[0] == "Change":
        line.pop()

    command, commit = line[0:2]
    if command.isdigit():
        commit, command = command, "apply"
    commit = int(commit)

    if command == "apply" or command == "a":
        diff = Capturing.capture(lambda: pp4_diff(commit))
        diff = [x + "\n" for x in diff]
        return pp4_patch(diff)
    elif command == "squash" or command == "s":
        diff = Capturing.capture(lambda: pp4_diff(commit))
        diff = [x + "\n" for x in diff]
        return pp4_patch(diff, move_from_changelist=last_changelist)

    return last_changelist, 1


def pp4_rebase(file, reverse):
    with open(file) as f:
        content = f.readlines()
    if reverse:
        content.reverse()

    try:
        last_commit = None
        if content and content[0].startswith("!!"):
            line = content.pop(0).strip().split()
            last_commit = int(line[1])

        while content:
            line = content.pop(0)
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            last_commit, patch_result = apply_line(line, last_commit)
            if patch_result != 0:
                print("After you have finished fixing issues, run pp4 rebase --continue. Or run pp4 rebase --abort",
                    file=sys.stderr)
                content.insert(0, "!! " + str(last_commit) + " Application failed: " + line)
                break



    finally:
        if content:
            with open(IN_PROGRESS, "w") as f:
                f.writelines(content)
        else:
            try:
                os.remove(IN_PROGRESS)
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Apply commits from a file')
    parser.add_argument(dest='file', nargs='?', type=str, help='Input file')
    parser.add_argument('-r', dest='reverse', action="store_true")
    parser.add_argument('--continue', dest='cont', action="store_true", help="Continue interrupted rebase")
    args = parser.parse_args()

    if args.cont:
        if args.file:
            raise Exception("--continue cannot be mixed with explicit input")

        args.file = IN_PROGRESS
    elif not args.file:
        raise Exception("Filename or --continue is required")

    res = pp4_rebase(args.file, args.reverse)
    exit(res)
