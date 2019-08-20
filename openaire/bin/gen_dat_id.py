#!/usr/bin/env python
# encoding: utf-8

import corpus
import json
import sys


if __name__ == "__main__":
    filename = "corpus/dataset.json"

    with open(filename) as f:
        for elem in json.load(f):
            publisher = elem["publisher"]
            title = elem["title"]

            dat_id = corpus.get_hash([publisher, title])
            print(dat_id, publisher, title)
