#!/usr/bin/env python
# encoding: utf-8

from urllib import parse
import csv
import json
import sys
import urllib.request
import xml.etree.ElementTree as et

API_URI = "http://api.openaire.eu/search/publications?title="
DEBUG = False # True

NS = {
    "oaf": "http://namespace.openaire.eu/oaf"
    }


def iter_json_pub (filename):
    with open(filename) as f:
        for elem in json.load(f):
            yield elem["pubs"], elem["doi"], elem["journal"], elem["title"]


def iter_usda_pub (filename):
    with open(filename) as f:
        for row in csv.reader(f, delimiter=","):
            dataset, doi, journal, title = row[:4]
            yield dataset, doi, journal, title


def load_uri (uri):
    with urllib.request.urlopen(uri) as response:
        html = response.read()
        return html.decode("utf-8")


def extract_pub_uri (xml):
    root = et.fromstring(xml)
    result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result", NS)

    if len(result) > 0:
        url_list = result[0].findall("./children/instance/webresource/url")

        if len(url_list) > 0:
            pub_url = url_list[0].text
            return pub_url

    return None


def extract_publisher (xml):
    try:
        root = et.fromstring(xml)
        result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result", NS)

        if len(result) > 0:
            pub_node = result[0].findall("./children/result/publisher")

            if len(pub_node) > 0:
                publisher = pub_node[0].text
                return publisher
    except:
        pass

    return "???"


def lookup_pub_uris (doi, journal, title, debug=False):
    try:
        uri = API_URI + parse.quote(title)
        #print(uri)
        xml = load_uri(uri)

        if debug:
            print(xml)

        pub_url = extract_pub_uri(xml)

        if pub_url:
            ## substitute the extracted journal name here
            journal = extract_publisher(xml)
            #print(journal)

            pub_id = "pub-{}".format(get_hash([doi, journal, title]))
            #print(pub_id)

            return [pub_id, pub_url, journal]
        else:
            return None
    except:    
        print("ERROR: {}".format(sys.exc_info()[0]))
        return None


def run_lookup (elem):
    pub_id = elem["publication_id"]
    doi = elem["unique_identifier"]
    #journal = elem["journal"]
    journal = ""
    title = elem["title"]

    #print(pub_id, doi, journal, title)
    response = lookup_pub_uris(doi, journal, title, debug=DEBUG)

    if response:
        gen_pub_id, pub_url, journal = response
        #print("  !!!", gen_pub_id, pub_id, pub_url, doi, journal, title)
        return [gen_pub_id, pub_id, pub_url, doi, journal, title]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        min_counter = int(sys.argv[1])
    else:
        min_counter = 0

    #filename = "../usda/dyads_for_validation.csv"
    #iter = iter_usda_pub(filename)

    #filename = "publications.json"
    #iter = iter_json_pub(filename)

    if DEBUG:
        iter = [["10.5150/alfred.e.neuman", "Mad Magazine", "Does a Nutritious Diet Cost More in Food Deserts?"]]

    # pull results from the OpenAIRE API
    filename = "phase1-train-test-publications.json"
    counter = 0

    with open(filename) as f:
        for elem in json.load(f):
            if counter >= min_counter:
                results = run_lookup(elem)

                if results:
                    results.append(counter)

                    with open("out", "a+") as o:
                        json.dump(results, o, indent=2)
                        o.write(",\n")

            counter += 1
