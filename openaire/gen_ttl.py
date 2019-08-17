#!/usr/bin/env python
# encoding: utf-8

from rdflib.serializer import Serializer
import csv
import json
import rdflib
import sys


PREAMBLE = """
@base <https://github.com/Coleridge-Initiative/adrf-onto/wiki/Vocabulary> .

@prefix cito:	<http://purl.org/spar/cito/> .
@prefix dct:	<http://purl.org/dc/terms/> .
@prefix foaf:	<http://xmlns.com/foaf/0.1/> .
@prefix rdf:	<http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd:	<http://www.w3.org/2001/XMLSchema#> .
"""

TEMPLATE_DATASET = """
:{}
  rdf:type :Dataset ;
  foaf:page "{}"^^xsd:anyURI ;
  dct:publisher "{}" ;
  dct:title "{}" ;
"""

TEMPLATE_PUBLICATION = """
:{}
  rdf:type :ResearchPublication ;
  foaf:page "{}"^^xsd:anyURI ;
  dct:publisher "{}" ;
  dct:title "{}" ;
  dct:identifier "{}" ;
"""


if __name__ == "__main__":
    out_buf = [ PREAMBLE.lstrip() ]

    ## load the links
    filename = "corpus/links.tsv"
    linked_pubs = set([])
    link_map = {}

    with open(filename) as f:
        for row in csv.reader(f, delimiter="\t"):
            dat_id, pub_id = row[:2]
            linked_pubs.add(pub_id)

            if pub_id not in link_map:
                link_map[pub_id] = set([dat_id])
            else:
                link_map[pub_id].add(dat_id)

    ## load the datasets
    filename = "corpus/dataset.json"
    known_datasets = set([])

    with open(filename) as f:
        for elem in json.load(f):
            dat_id = elem["id"]
            known_datasets.add(dat_id)

            out_buf.append(
                TEMPLATE_DATASET.format(
                    dat_id,
                    elem["url"],
                    elem["publisher"],
                    elem["title"]
                    ).strip()
                )

            if "alt_title" in elem:
                out_buf.append("  dct:alternative \"{}\" ;".format(elem["alt_title"]))

            out_buf.append(".\n")

    ## load the publications
    filename = "corpus/publication.json"

    with open(filename) as f:
        for elem in json.load(f):
            pub_id = elem["id"]

            if pub_id in linked_pubs:
                out_buf.append(
                    TEMPLATE_PUBLICATION.format(
                        pub_id,
                        elem["url"],
                        elem["publisher"],
                        elem["title"],
                        elem["doi"]
                        ).strip()
                    )

                if "pdf" in elem:
                    out_buf.append("  :openAccess \"{}\"^^xsd:anyURI ;".format(elem["pdf"]))

                dat_list = [ ":{}".format(dat_id) for dat_id in link_map[pub_id] ]
                out_buf.append("  cito:citesAsDataSource {} ;".format(", ".join(dat_list)))
                out_buf.append(".\n")

            # {'id': 'publication-ea02695293f2279e9bba', 'doi': '10.1136/jech.46.3.191', 'publisher': 'J Epidemiol Community Health', 'title': 'Gender and race differences in the correlation between body mass and education in the 1971-1975 NHANES I', 'url': 'https://europepmc.org/articles/PMC1059548/', 'pdf': 'https://europepmc.org/articles/PMC1059548?pdf=render'}


    ## write the TTL output
    filename = "tmp.ttl"

    with open(filename, "w") as f:
        for text in out_buf:
            f.write(text)
            f.write("\n")

    ## load the TTL output as a graph
    graph = rdflib.Graph()
    graph.parse(filename, format="n3")

    ## transform graph into JSON-LD
    with open("corpus/vocab.json", "r") as f:
        context = json.load(f)

    with open("tmp.jsonld", "wb") as f:
        f.write(graph.serialize(format="json-ld", context=context, indent=2))

    ## read back
    graph = rdflib.Graph()
    graph.parse("tmp.jsonld", format="json-ld")
