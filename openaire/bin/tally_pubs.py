#!/usr/bin/env python
# encoding: utf-8

import glob
import json
import sys


if __name__ == "__main__":
    ## load metadata from JSON
    tally = {}

    for filename in glob.glob("corpus/pub/*.json"):
        with open(filename) as f:
            for elem in json.load(f):
                publisher = elem["publisher"].strip().lower()

                if publisher not in tally:
                    tally[publisher] = 1
                else:
                    tally[publisher] += 1

    ## output tallies
    for publisher, count in sorted(tally.items()):
        print("{}\t{}".format(count, publisher))
