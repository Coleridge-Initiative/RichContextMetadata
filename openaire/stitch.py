#!/usr/bin/env python
# encoding: utf-8

import corpus
import json
import sys


def format_entry (dat_set, url, doi, publisher, title):
    pub_id = corpus.get_hash([publisher, title], prefix="publication-")

    entry = {
        "id": pub_id,
        "doi": doi,
        "publisher": publisher,
        "title": title,
        "url": url
        }

    print(json.dumps(entry, indent=2), ",")

    for dat_id in dat_set:
        id = dat_dict[dat_id]["id"]
        links.append([id, pub_id])


if __name__ == "__main__":
    dat_dict = {}
    pub_dict = {}
    map_dict = {}
    doi_done = set([])
    todo = {}
    links = []

    ## load the "already done" publications
    filename = "corpus/publication.json"

    with open(filename) as f:
        for elem in json.load(f):
            doi = elem["doi"]
            doi_done.add(doi)

    ## load the RCC dataset list
    filename = "dat/rcc_test_dataset.json"
    kill_set = set(["483"])

    with open(filename) as f:
        for elem in json.load(f):
            dat_id = str(elem["data_set_id"])
            pub_id = str(elem["publication_id"])

            if dat_id in kill_set:
                continue
            elif pub_id not in map_dict:
                map_dict[pub_id] = set([dat_id])
            else:
                map_dict[pub_id].add(dat_id)

            if "id" in elem:
                dat_dict[dat_id] = elem

    ## load the open access publications
    filename = "dat/out"

    with open(filename) as f:
        for elem in json.load(f):
            _pub_id, pub_id_num, url, doi, publisher, title, count = elem
            pub_id = str(pub_id_num)

            if doi in doi_done:
                continue
            elif pub_id in map_dict:
                dat_set = map_dict[pub_id]

                for dat_id in dat_set:
                    if dat_id in kill_set:
                        pass
                    elif dat_id in dat_dict:
                        todo[pub_id] = [dat_set, url, doi, publisher, title]


    ## 1. simplest case: known publisher, known datasets
    got_any = False

    for pub_id, (dat_set, url, doi, publisher, title) in todo.items():
        if publisher == "???":
            continue
        else:
            all_known = True

            for dat_id in dat_set:
                if dat_id not in dat_dict:
                    all_known = False

            if all_known:
                format_entry(dat_set, url, doi, publisher, title)
                got_any = True

    if got_any:
        ## print the links, too
        for dat_id, pub_id in sorted(links):
            print("{}\t{}".format(dat_id, pub_id))

        sys.exit(0)


    ## 2. harder case: unknown publisher, all known datasets
    got_any = False

    for pub_id, (dat_set, url, doi, publisher, title) in todo.items():
        all_known = True

        for dat_id in dat_set:
            if dat_id not in dat_dict:
                all_known = False

        if all_known:
            print(pub_id, url, title)
            got_any = True

    if got_any:
        sys.exit(0)


    ## 3. harder case: unknown publisher, any known datasets
    got_any = False

    for pub_id, (dat_set, url, doi, publisher, title) in todo.items():
        any_known = False

        for dat_id in dat_set:
            if dat_id in dat_dict:
                any_known = True

        if any_known:
            print(pub_id, url, title, dat_set)
            got_any = True

    if got_any:
        sys.exit(0)
