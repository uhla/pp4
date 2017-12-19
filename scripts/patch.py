#!/usr/bin/python3

import sys
import argparse
import subprocess
import re

def pp4_patch(patch, checkout=True, checkoutonly=False, postaction=None):
    changed_files = []
    changelist = -1
    patch_result = 0

    if checkout:
        start=0
        end=len(patch)
        last_line = ""
        for i, line in enumerate(patch):
            if re.match("#+ +CHANGE START +#+", line):
                start = i
            if re.match("#+ +CHANGE END +#+", line):
                end = i
            if last_line.startswith("--") and line.startswith("++"):
                file1 = re.search('\-{2,}\s+(\S+)', last_line).group(1)
                file2 = re.search('\+{2,}\s+(\S+)', line).group(1)
                changed_files.append((file1, file2))
            if last_line.startswith("++") and line.startswith("--"):
                file1 = re.search('\-{2,}\s+(\S+)', line).group(1)
                file2 = re.search('\+{2,}\s+(\S+)', last_line).group(1)
                changed_files.append((file1, file2))
            last_line = line

        change = patch[start+1:end]
        change.append("Change: new")

        print("\n".join(change))

        process = subprocess.run('pp4 change -i'.split(), stdout=subprocess.PIPE, input="".join(change),
                                 universal_newlines=True, check=True)
        output = process.stdout.split("\n")

        m = re.search('Change ([0-9]+) created', output[0])
        if not m:
            print("PP4 error: " + output[0])

        changelist = int(m.group(1))
        print("Pending changelist created: " + str(changelist))

        for file_from, file_to in changed_files:
            # File changed (or moved):
            if file_from != "/dev/null" and file_to != "/dev/null":
                subprocess.run(['pp4', 'edit', '-c', str(changelist), file_from], stdout=subprocess.PIPE,
                               universal_newlines=True, check=True)
            # TODO: Move
            # TODO: Delete

    if not checkoutonly:
        process = subprocess.run(["patch", "-r", "-l", "-N", "-p1", "--merge"],
                                 stdout=subprocess.PIPE, input="".join(patch), universal_newlines=True)
        patch_result = process.returncode
        print(process.stdout)


    if checkout:
        for file_from, file_to in changed_files:
            # File added
            if file_from == "/dev/null" and file_to != "/dev/null":
                subprocess.run(['pp4', 'add', '-c', str(changelist), file_to], stdout=subprocess.PIPE,
                               universal_newlines=True, check=True)

    if patch_result != 0:
        print("There were patch errors or warnings. Please review and fix the code and submit/shelve manually",
              file=sys.stderr)
        return patch_result

    if postaction == "shelve":
        subprocess.run(['pp4', 'shelve', '-c', str(changelist)], stdout=subprocess.PIPE,
                       universal_newlines=True, check=True)

    if postaction == "submit":
        subprocess.run(['pp4', 'submit', '-c', str(changelist)], stdout=subprocess.PIPE,
                       universal_newlines=True, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Apply a patch to Perforce files and create a new pending changelist from it.')
    parser.add_argument('--nocheckout', dest='checkout', action="store_false",
                        help='Do not checkout the files, just patch them')
    parser.add_argument('--checkoutonly', dest='checkoutonly', action='store_true',
                        help='Just checkout the files, do not patch them')
    parser.add_argument('--submit', dest='postaction', action='store_const', const='submit',
                        help='If patch is applied without conflicts, submit the changelist')
    parser.add_argument('--shelve', dest='postaction', action='store_const', const='shelve',
                        help='If patch is applied without conflicts, shelve the changelist')
    args = parser.parse_args()

    patch = [x for x in sys.stdin]
    res = pp4_patch(patch, checkout=args.checkout, checkoutonly=args.checkoutonly, postaction=args.postaction)
    exit(res)