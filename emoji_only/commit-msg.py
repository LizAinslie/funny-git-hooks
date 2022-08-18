#!/usr/bin/env python3

"""
Git commit hook
Only allow emoji in commits
"""

import sys, os, re
from subprocess import call
import emoji

is_piped = True if len(sys.argv) == 1 else False
editor = os.environ.get('EDITOR', 'nvim')
sys.stdin = open("/dev/tty", "r")


def emoji_only(string):
    for char in string:
        if not emoji.is_emoji(char):
            return False
    return True


def bad_commit(errmsg, line=""):
    sys.stderr.write("\nThe following line does not follow our "
                     "guidelines:\n%s\n" % line)
    sys.stderr.write("\n%s\n" % errmsg)
    if is_piped:
        sys.exit(1)
    raise SyntaxError(errmsg)


while True:
    commit = sys.stdin if is_piped else open(sys.argv[1], 'r')
    try:
        lines = commit.read().splitlines()
        # abracadabra: remove all comments from the list of lines ;)
        lines = [l for l in lines if not l.startswith("#")]

        if len(lines) == 0:
            bad_commit(commit, "Empty commit message")

        # first line
        line = lines[0]

        # ignore any Merge
        if line.startswith("Merge"):
            sys.exit(0)

        for l in lines:
            if not emoji_only(l):
                bad_commit("Commits are only allowed to contain emoji", l)

    # We catch that an error has happened and react accordingly
    except SyntaxError as err:
        if input("Do you want to edit it? (Your commit will "
                 "be rejected otherwise) [y/N] ").lower() == 'y':
            if not is_piped:
                commit.close()
                commit = open(sys.argv[1], 'a')
            # commit.write("#\n# %s\n#\n" % err)
            sys.stderr.write('\n')
            commit.close()
            call('%s %s' % (editor, sys.argv[1]), shell=True)
            continue
        else:
            sys.stderr.write("Exiting without committing\n")
            sys.exit(1)
    break
sys.exit(0)
