#!/usr/bin/env python
# encoding: utf-8

from rdflib.serializer import Serializer
import corpus
import csv
import glob
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
  :openAccess "{}"^^xsd:anyURI ;
"""


if __name__ == "__main__":
    out_buf = [ PREAMBLE.lstrip() ]

    ## load the datasets
    filename = "corpus/dataset.json"
    known_datasets = set([])

    with open(filename) as f:
        for elem in json.load(f):
            dat_id = elem["uuid"]
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
                for alt_title in elem["alt_title"]:
                    out_buf.append("  dct:alternative \"{}\" ;".format(alt_title))

            out_buf.append(".\n")

    ## load the publications
    for filename in glob.glob("corpus/pub/*.json"):
        with open(filename) as f:
            for elem in json.load(f):
                link_map = elem["datasets"]

                if len(link_map) > 0:
                    id_list = [elem["publisher"], elem["title"]]
                    pub_id = corpus.get_hash(id_list, prefix="publication-")

                    out_buf.append(
                        TEMPLATE_PUBLICATION.format(
                            pub_id,
                            elem["url"],
                            elem["publisher"],
                            elem["title"],
                            elem["doi"],
                            elem["pdf"]
                            ).strip()
                        )

                    dat_list = [ ":{}".format(dat_id) for dat_id in link_map ]
                    out_buf.append("  cito:citesAsDataSource {} ;".format(", ".join(dat_list)))
                    out_buf.append(".\n")

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
