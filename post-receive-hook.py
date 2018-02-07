#! /usr/bin/env python

import sys
import os
import subprocess


def main():
    (oldrev, newrev, branch) = sys.stdin.read().split()
    print("Old Revision "+oldrev)
    print("New Revision "+newrev)
    print("Branch "+branch)

if __name__ == '__main__':
    main()


