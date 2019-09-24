#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
import csv
import requests
import sys
import urllib.parse


def get_ssrn (title):
    """
    lookup the title on SSRN.com
    """
    url = "https://papers.ssrn.com/sol3/results.cfm?txtKey_Words=" + urllib.parse.quote(title)
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")

    for elem in soup.find_all("a", {"class": "optClickTitle", "tabindex": "0"}):
        doc_url = elem["href"]
        doc_title = elem.find("span").get_text()

        if doc_title.lower() == title.lower():
            return doc_url

    return None


def test_url (url, title):
    """
    verify that the URL is a page for this title
    """
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")
    elem = soup.find("meta",  {"name": "citation_title"})

    if elem and elem["content"].lower() == title.lower():
        return True
    else:
        return False


def get_repec_url (title):
    """
    attempt to find a title on ideas.RePEc.org
    """
    enc_title = urllib.parse.quote_plus(title.replace("(", "").replace(")", "").replace(":", ""))
    cgi_url = "https://ideas.repec.org/cgi-bin/htsearch?q={}".format(enc_title)
    response = requests.get(cgi_url).text
    soup = BeautifulSoup(response, "html.parser")
    li = soup.find("li", {"class": "list-group-item"})

    if li:
        elem = li.find("a")
        url = "https://ideas.repec.org" + elem["href"]

        if test_url(url, title):
            return url

    return None


def lookup (title):
    """
    for now, simply lookup on RePEc
    """
    return get_repec_url(title)


if __name__ == "__main__":
    filename = "all_bundesbank_w_datasets_ssrn_links-20190607.csv"

    with open(filename, "r") as in_file, open("out.tsv", "w") as out_file:
        reader = csv.reader(in_file)
        next(reader)

        writer = csv.writer(out_file, delimiter="\t")
        writer.writerow(["title", "dataset", "url"])

        for row in reader:
            title, authors, journal, bbk_dataset, dataset_notes, paper, doi, bbk_url = row
            title = title.strip()
            bbk_dataset = bbk_dataset.strip()

            doc_url = get_ssrn(title)

            if bbk_dataset == "":
                # for now, ignore publications which lack datasets
                pass
            if bbk_url == doc_url:
                url = bbk_url
            elif doc_url:
                # believe the lookup results
                url = doc_url
            elif bbk_url != "":
                if test_url(bbk_url, title):
                    url = bbk_url
                else:
                    url = lookup(title)
            else:
                url = lookup(title)

            writer.writerow([title, bbk_dataset, url])
