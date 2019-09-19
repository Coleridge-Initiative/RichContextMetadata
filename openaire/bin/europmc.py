#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
import json
import re
import requests
import sys
import traceback
import urllib.parse


def get_europepmc_metadata (url):
    """
    parse metadata from a Europe PMC web page for a publication
    """

    # <meta content="http://europepmc.org/articles/PMC2819787?pdf=render" name="citation_pdf_url"/>
    # <meta content="10.3390/ijerph7010269" name="citation_doi"/>
    # <meta content="Int J Environ Res Public Health" name="citation_journal_abbrev"/>

    response = requests.get(url).text
    #print(BeautifulSoup(response, "html.parser").prettify())

    publisher = None
    doi = None
    pdf = None

    soup = BeautifulSoup(response, "html.parser")

    for x in soup.find_all("span", {"id": "pmcmata"}):
        publisher = x.get_text()

    for x in soup.find_all("meta",  {"name": "citation_doi"}):
        doi = x["content"]

    for x in soup.find_all("meta",  {"name": "citation_pdf_url"}):
        pdf = x["content"]

    if publisher and doi and pdf:
        return [publisher, doi, pdf]
    else:
        return None


def transform_elem (elem, publisher, doi, pdf, dat_set):
    """
    format a publication element
    """
    return {
        "doi": doi,
        "publisher": publisher,
        "title": elem["title"],
        "url": elem["url"].rstrip("/"),
        "pdf": pdf,
        "datasets": list(dat_set)
        }


if __name__ == "__main__":
    ## load the datasets
    filename = "corpus/refs.json"
    known_dat = {}

    with open(filename, "r") as f:
        try:
            for elem in json.load(f):
                for dat_id in elem["rcc_cite"]:
                    known_dat[str(dat_id)] = elem["id"]
        except:
            print(traceback.format_exc())
            print(filename)
            sys.exit(1)


    ## transform just the Europe PMC links
    MISSING_DAT = 4
    pat = r"(http|https)\:\/\/europepmc.org*"
    p = re.compile(pat)

    count = 0
    print("[")

    with open(sys.argv[1], "r") as f:
        for line in f:
            if line.startswith("{"):
                elem = json.loads(line)
                url = elem["url"]

                if MISSING_DAT not in elem["flags"] and p.match(url):
                    results = get_europepmc_metadata(url)

                    if results:
                        publisher, doi, pdf = results
                        dat_set = set([ known_dat[str(d)] for d in elem["rcc_cite"] ])
                        ref = transform_elem(elem, publisher, doi, pdf, dat_set)

                        if count > 0:
                            print(",")

                        print(json.dumps(ref))
                        count += 1

    print("]")
