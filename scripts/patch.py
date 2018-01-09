#!/usr/bin/python3

import sys
import argparse
import subprocess
import re

from scripts.util.util import pp4_describe_changelist, pp4_delete


def pp4_patch(patch, checkout=True, checkoutonly=False, changelist=None, postaction=None, move_from_changelist=None):
    changed_files = []
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

#        print(change)
        print("\n".join(change))

        if not changelist:
            process = subprocess.run('pp4 change -i'.split(), stdout=subprocess.PIPE, input="".join(change),
                                     universal_newlines=True, check=True)
            output = process.stdout.split("\n")

            m = re.search('Change ([0-9]+) created', output[0])
            if not m:
                print("PP4 error: " + output[0])
                raise Exception()

            changelist = int(m.group(1))
            print("Pending changelist created: " + str(changelist))
        else:
            # TODO: Add description to existing change
            pass

        if move_from_changelist:
            old_changelist = pp4_describe_changelist(move_from_changelist)
            #print(old_changelist)
            subprocess.run(['pp4', 'shelve', '-c', str(move_from_changelist)], stdout=subprocess.PIPE,
                           universal_newlines=True, check=True)

            print ("Moving files to new changelist:")
            files = [f[0] for f in old_changelist.affected_files]

            process = subprocess.run(['pp4', 'reopen', '-c', str(changelist)] + files, stdout=subprocess.PIPE,
                           universal_newlines=True, check=True)
            print(process.stdout)

        for file_from, file_to in changed_files:
            # File changed (or moved):
            if file_from != "/dev/null" and file_to != "/dev/null":
                subprocess.run(['pp4', 'edit', '-c', str(changelist), file_from], stdout=subprocess.PIPE,
                               universal_newlines=True, check=True)
            # TODO: Move

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
            # File deleted
            elif file_from != "/dev/null" and file_to == "/dev/null":
                pp4_delete(changelist, file_from)

    if patch_result != 0:
        print("There were patch errors or warnings. Please review and fix the code and submit/shelve manually",
              file=sys.stderr)
        return changelist, patch_result

    if postaction == "shelve":
        process = subprocess.run(['pp4', 'shelve', '-c', str(changelist)], stdout=subprocess.PIPE,
                       universal_newlines=True, check=True)


    if postaction == "submit":
        subprocess.run(['pp4', 'submit', '-c', str(changelist)], stdout=subprocess.PIPE,
                       universal_newlines=True, check=True)

    return changelist, patch_result

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
    changelist, res = pp4_patch(patch, checkout=args.checkout, checkoutonly=args.checkoutonly, postaction=args.postaction)
    exit(res)