#!/usr/bin/env python
# encoding: utf-8

import corpus
import json
import sys


if __name__ == "__main__":
    filename = sys.argv[1]
    pub_set = {}

    with open(filename) as f:
        for elem in json.load(f):
            pub_id = elem["id"]

            if pub_id not in pub_set:
                pub_set[pub_id] = elem

    keys = sorted(pub_set.keys())

    for pub_id in keys:
        print(json.dumps(pub_set[pub_id], indent=2))
        print(",")
