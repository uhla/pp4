#!/usr/bin/python3

import argparse
import re
import subprocess

from scripts.util.util import pp4_describe_changelist, pp4_describe_client, parse_describe_changelist


def diff_added_or_deleted(file_with_revision, stream, is_add=True):
    global file
    pp4 = subprocess.Popen(["pp4", "print", file_with_revision], stdout=subprocess.PIPE)
    tail = subprocess.Popen(["tail", "-n+2"], stdin=pp4.stdout, stdout=subprocess.PIPE)
    diffargs = ["diff", "-u", "/dev/null", "-"] if is_add else \
        ["diff", "-u", "-", "/dev/null"]
    diff = subprocess.run(diffargs, stdin=tail.stdout, stdout=subprocess.PIPE,
                          universal_newlines=True)
    tail.wait()
    file = file_with_revision.split("#")[0]
    file = file.replace(stream, ".")
    out = diff.stdout
    out = out.replace("--- -", "--- " + file)
    out = out.replace("+++ -", "+++ " + file)
    return out


def pp4_diff(changelist):
    cl = pp4_describe_changelist(changelist)
    print("### CHANGE START ###")
    print("Description:")
    for line in cl.description.split("\n"):
        print("\t" + line)
    print("### CHANGE END ###")

    # print(cl)
    stream = cl.stream[0]

    if not cl.pending:
        # Submitted changelist -> create patch against previous revision
        pp4 = ["pp4", "diff2", "-u",
               stream + "/...@" + str(changelist - 1),
               stream + "/...@" + str(changelist)]
        # print(" ".join(args))
        process = subprocess.run(pp4, stdout=subprocess.PIPE,
                                 universal_newlines=True, check=True)

        output = process.stdout
        output = output.replace(stream, ".")
        print(output, end="")

        print("## Added and removed files")

        pp4 = ["pp4", "diff2", "-Od", "-q",
               stream + "/...@" + str(changelist - 1),
               stream + "/...@" + str(changelist)]
        # print(" ".join(args))
        process = subprocess.run(pp4, stdout=subprocess.PIPE,
                                 universal_newlines=True, check=True)

        output = process.stdout
        # output = output.replace(stream, ".")
        for line in output.split("\n"):
            m = re.search("=+ ((?P<oldfile>[^#]+#[0-9]+)|<none>) - ((?P<newfile>[^#]+#[0-9]+)|<none>) =+", line)
            if m:
                new = m.groupdict().get("newfile", None)
                old = m.groupdict().get("oldfile", None)

                if old and not new:
                    print(diff_added_or_deleted(old, stream, is_add=False))
                elif not old and new:
                    print(diff_added_or_deleted(new, stream, is_add=True))

        return 0

    else:  # Pending changelist -> is it in current workspace?
        current_client = pp4_describe_client()
        if current_client["Client"] == cl.workspace:
            # Current workspace -> create patch from the actual files in it
            # 		pp4 opened -c $CL | sed -e 's/#.*//' | pp4 -x - diff -du | sed "s|$DP|.|" | sed "s|$PWD|.|"
            pp4 = ["pp4", "opened", "-c", str(changelist)]
            process = subprocess.run(pp4, stdout=subprocess.PIPE,
                                     universal_newlines=True, check=True)

            files = []
            for line in process.stdout.split("\n"):
                m = re.search("(?P<file>[^#]+)#([0-9]+) - (?P<action>[^ ]+) change .*", line)
                if m:
                    file = m.groupdict()["file"]
                    action = m.groupdict()["action"]

                    files.append(file)

            pp4 = ["pp4", "-x", "-", "diff", "-du"]
            process = subprocess.run(pp4, stdout=subprocess.PIPE, input="\n".join(files),
                                     universal_newlines=True, check=True)

            for line in process.stdout.split("\n"):
                line = line.replace(stream, ".")
                line = line.replace(current_client["Root"], ".")
                print(line)

            return 0
        else:
            # Another workspace -> create patch from shelved files (if any)
            # 		pp4 describe -du4 -S $CL | awk 'p; /Differences .../ {p=1};' | sed 's/^==== \([^#]*\)#.*$/+++ \1\
            # --- \1/' | sed "s|$DP|.|" | sed "s|$PWD|.|"
            pp4 = ["pp4", "describe", "-du4", "-S", str(changelist)]
            process = subprocess.run(pp4, stdout=subprocess.PIPE,
                                     universal_newlines=True, check=True)

            cl = parse_describe_changelist(process.stdout)

            for line in cl.differences:
                m = re.search("=+ (?P<file>[^#]+)#([0-9]+) \(.*\) =+", line)
                if m:
                    file = m[1]
                    file = file.replace(stream, ".")
                    print("+++ " + file)
                    print("--- " + file)
                else:
                    print(line)

            return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create an unified diff from a changelist.')
    parser.add_argument(dest='changelist', type=int, help='Changelist#')
    args = parser.parse_args()

    res = pp4_diff(args.changelist)
    exit(res)
