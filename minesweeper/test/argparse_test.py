#!/usr/bin/python3.2

import argparse
from argparse import Action
from sys import argv


class FindLongestAction(Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(FindLongestAction, self).__init__(dest, nargs, **kwargs)

    def __call__(self, *args, **kwargs):
        pass


def find_longest_string(strings):
    return max(strings, key=lambda s: len(s))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("-s", "--strings", dest="string_longest", action="store",
                   nargs="+", help="List of strings where the longest is to be found", required=True)
    r = a.parse_args(args=argv[1:])

    print("Longest string: %s" % find_longest_string(r.string_longest))

if __name__ == "__main__":
    main()
