#!/usr/bin/env python
# encoding: utf-8

import configparser
import corpus
import csv
import glob
import json
import sys
import traceback


CONFIG = configparser.ConfigParser()
CONFIG.read("rc.cfg")


def format_entity (elem):
    """
    format one publication as JSON
    """
    try:
        dat_set = set([ known_dat[str(d)] for d in elem["rcc_cite"] ])

        entity = {
            "doi": elem["doi"],
            "publisher": elem["publisher"],
            "title": elem["title"],
            "url": elem["url"],
            "pdf": elem["pdf"],
            "datasets": list(dat_set)
            }

        print(json.dumps(entity, indent=2))
    except:
        print(traceback.format_exc())
        print(elem)
        sys.exit(1)


def suggest_work (todo, criteria, descript):
    """
    suggest the next batch of manual lookups
    """
    suggested = []

    for elem in todo:        
        if elem["flags"] == criteria:
            suggested.append(elem)

    if len(suggested) > 0:
        print(descript)

        for elem in suggested:
            print(elem)

        sys.exit(0)


if __name__ == "__main__":
    known_dat = {}
    done_pubs = set([])
    todo = []
    complete = []

    MISSING_PDF = 1
    MISSING_PUB = 2
    MISSING_URL = 3
    MISSING_DAT = 4
    NO_DAT = 5


    ## load the datasets
    filename = "corpus/refs.json"

    with open(filename, "r") as f:
        try:
            for elem in json.load(f):
                for dat_id in elem["rcc_cite"]:
                    known_dat[str(dat_id)] = elem["id"]
        except:
            print(traceback.format_exc())
            print(filename)
            sys.exit(1)


    ## track titles for publications already included in the corpus
    for filename in glob.glob("corpus/pub/*.json"):
        with open(filename) as f:
            for elem in json.load(f):
                _title = elem["title"].strip().lower()
                done_pubs.add(_title)


    ## load the RCC publications
    filename = "dat/rcc_out.json"

    try:
        with open(filename) as f:
            for elem in json.load(f):
                elem["flags"] = set([])
                _title = elem["title"].strip().lower()

                if _title in done_pubs:
                    # ignore publications already in the corpus
                    continue

                if elem["publisher"] == "???":
                    elem["flags"].add(MISSING_PUB)

                if "url" not in elem:
                    elem["flags"].add(MISSING_URL)

                if "pdf" not in elem:
                    elem["flags"].add(MISSING_PDF)

                if "rcc_cite" not in elem:
                    elem["rcc_cite"] = []
                    elem["flags"].add(NO_DAT)
                else:
                    for dat_id in elem["rcc_cite"]:
                        dat_id = str(dat_id)

                        if dat_id not in known_dat:
                            elem["flags"].add(MISSING_DAT)

                todo.append(elem)

                if len(elem["flags"]) == 0:
                    complete.append(elem)
    except:
        print(traceback.format_exc())
        print(filename)
        sys.exit(1)


    ## 1. output the complete cases
    if len(complete) > 0:
        count = 0
        print("[")

        for elem in complete:
            if count > 0:
                print(",")

            format_entity(elem)
            count += 1

        print("]")
        sys.exit(0)


    ## other suggestions for what to repair manually next
    suggest_work(todo, set([MISSING_PDF]), "only the PDF is missing")
    suggest_work(todo, set([MISSING_URL]), "only the URL is missing")
    suggest_work(todo, set([MISSING_PUB]), "only the publisher is unknown")
    suggest_work(todo, set([MISSING_PDF, MISSING_PUB]), "missing PDF and publisher")

    for elem in todo:
        if len(elem["flags"]) <= 1:
            print(elem)
