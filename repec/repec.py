#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
import configparser
import copy
import glob
import json
import requests
import sys
import traceback
import urllib.parse


CONFIG = configparser.ConfigParser()
CONFIG.read("repec.cfg")


def extract_view (elem, count):
    view = {}

    try:
        view["dimensions_id"] = elem["dimensions_id"]
        view["doi"] = elem["doi"]
        view["title"] = elem["title"]
        view["related_dataset_name"] = elem["related_dataset_name"]

        view["authors"] = []

        if "authors" in elem:
            for a in elem["authors"]:
                view["authors"].append({
                        "first_name": a["first_name"],
                        "last_name": a["last_name"],
                        })
    
        if "journal" in elem:
            view["journal"] = elem["journal"]
        else:
            view["journal"] = None

        return view

    except:
        print(traceback.format_exc())
        print(count, elem)
        sys.exit(1)


def get_repec_handle (title):
    enc_title = urllib.parse.quote_plus(title.replace("(", "").replace(")", "").replace(":", ""))

    cgi_url = "https://ideas.repec.org/cgi-bin/htsearch?q={}".format(enc_title)
    response = requests.get(cgi_url).text
    #print(BeautifulSoup(response, "html.parser").prettify())

    soup = BeautifulSoup(response, "html.parser")
    ol = soup.find("ol", {"class": "list-group"})
    results = ol.findChildren()

    if len(results) > 0:
        li = results[0]
        handle = li.find("i").get_text()
        return handle
    else:
        return None


def get_repec_meta (token, handle):
    try:
        api_url = "https://api.repec.org/call.cgi?code={}&getref={}".format(token, handle)
        response = requests.get(api_url).text

        meta = json.loads(response)
        return meta

    except:
        print(traceback.format_exc())
        print("ERROR: {}".format(handle))
        return None


def get_repec_authors (token, handle):
    try:
        api_url = "https://api.repec.org/call.cgi?code={}&getauthorsforitem={}".format(token, handle)

        response = requests.get(api_url).text

        authors = json.loads(response)
        return authors

    except:
        print(traceback.format_exc())
        print("ERROR: {}".format(handle))
        return None


if __name__ == "__main__":
    mode = sys.argv[1]

    if mode == "1":
        pubs = []

        ## load the Dimensions API results
        for filename in glob.glob("string_searches/*.json"):
            with open(filename) as f:
                count = 0

                for elem in json.load(f):
                    #print(elem)
                    view = extract_view(elem, count)
                    view["repec_handle"] = get_repec_handle(view["title"])

                    pubs.append(view)
                    count += 1

        ## persist the results to a file
        with open("pub_handles.json", "w") as f:
            json.dump(pubs, f, indent=2, sort_keys=True)


    elif mode == "2":
        repec_token = CONFIG["DEFAULT"]["repec_token"]
        pubs = []

        ## call RePEc API to get author metadata        
        with open("pub_handles.json", "r") as f:
            for view in json.load(f):
                if view["repec_handle"]:
                    #print(view)
                    results = get_repec_meta(repec_token, view["repec_handle"])
                    authors = get_repec_authors(repec_token, view["repec_handle"])

                    if results and len(results) > 0:
                        meta = results[0]

                        if view["title"].lower() == meta["bibliographic"]["name"].lower():
                            view["repec_biblio"] = meta["bibliographic"]
                            view["repec_authors_fallback"] = meta["author"].split(" & ")

                            if authors:
                                view["repec_authors"] = authors

                            pubs.append(view)

        ## persist the results to a file
        with open("pub_authors.json", "w") as f:
            json.dump(pubs, f, indent=2, sort_keys=True)


    elif mode == "3":
        ## prepare the data to send to RePEc for author confirmation
        pubs = []

        with open("pub_authors.json", "r") as f:
            for view in json.load(f):
                meta = {}
                meta["repec_handle"] = view["repec_handle"]
                meta["related_dataset_name"] = view["related_dataset_name"]
                meta["title"] = view["title"]

                if view["journal"]:
                    meta["journal"] = view["journal"]["title"]
                else:
                    meta["journal"] = ""

                ## enumerate the authors and align their metadata
                if "repec_authors" not in view:
                    print(view)
                    print("ERROR: MISSING AUTHORS")
                elif "error" in view["repec_authors"][0]:
                    ## this case had `"error": 44`
                    for author in set(view["repec_authors_fallback"]):
                        auth_meta = copy.deepcopy(meta)
                        auth_meta["shortid"] = None
                        auth_meta["author"] = author
                        pubs.append(auth_meta)
                else:
                    for author in view["repec_authors"]:
                        auth_meta = copy.deepcopy(meta)
                        auth_meta["shortid"] = author["shortid"]
                        del author["shortid"]
                        auth_meta["author"] = author
                        pubs.append(auth_meta)

        ## persist the results to a file
        with open("send_repec.json", "w", encoding="utf8") as f:
            json.dump(pubs, f, indent=2, sort_keys=True, ensure_ascii=False)

        print("processed {} author records".format(len(pubs)))

