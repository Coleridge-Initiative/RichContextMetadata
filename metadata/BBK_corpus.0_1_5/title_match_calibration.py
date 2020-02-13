import re
import sys
import codecs
import json
from collections import defaultdict
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
from datasketch import MinHashLSHEnsemble, MinHash

def title_match(title1, title2):
    pass

def get_set_of_words(text):
    return re.sub("[\W+]", " ", text).lower().split()


def main(corpus_path, search_for_matches_path):

    ## TODO: Load all dataset ids and titles from dataset.json

    ## TODO: Load all dataset adrf_ids and titles from ADRF dump

    ## TODO: Create known true matches and known false matches lists
        # TODO: for 4 true links see https://github.com/NYU-CI/RCCustomers/blob/5e71284c893f39e670a474ec9b7110ec04593e09/customers/USDA/bin/usda_datadump.json

    ## TODO: Create 1 set and 1 MinHash per dataset title

    ## TODO: Loop changing threshold from 0.1 to 0.9
        ## TODO: for each threshold, calculate 'confusion matrix'

    #Load all dataset adrf_ids and titles from ADRF dump
    with codecs.open(search_for_matches_path, "r", encoding="utf8") as f:
        adrf_dataset_list = json.load(f)

    print("loading ADRF dataset corpus...", type(adrf_dataset_list), len(adrf_dataset_list))

    # Load all dataset ids and titles from dataset.json
        #TODO using a temporal copy instead the most updated version˚
    with codecs.open(corpus_path, "r", encoding="utf8") as f:
        rc_dataset_list = json.load(f)

    print("loading RC dataset corpus...",type(rc_dataset_list),len(rc_dataset_list))

    # create a structure to access title and its set of unique words
    rc_corpus = defaultdict()
    for dataset in rc_dataset_list:
        d = dict()
        d["words"] = get_set_of_words(dataset["title"])
        d["title"] = dataset["title"]
        rc_corpus[dataset["id"]] = d

    # create a MinHash for each dataset title
    print("creating MinHash for each RC dataset...")
    for key,values in rc_corpus.items():
        mh = MinHash(num_perm=128)
        for term in values["words"]:
            mh.update(term.encode("utf8"))
        rc_corpus[key]["min_hash"] = mh


    lsh_threshold = 0.85
    print("creating MinHashLSHEnsemble with threshold=%s, num_perm=128, num_part=16..." % lsh_threshold)
    # Create an LSH Ensemble index with threshold and number of partition settings.
    lshensemble = MinHashLSHEnsemble(threshold=lsh_threshold, num_perm=128, num_part=16)

    print("indexing all RC dataset's MinHash...")
    # Index takes an iterable of (key, minhash, size)
    lshensemble.index([(key,values["min_hash"],len(values["words"])) for key, values in rc_corpus.items()])

    # test by querying the LSH Ensemble with each ADRF dataset title to explore potential matches
    for adrf_dataset in adrf_dataset_list:

        set1=get_set_of_words(adrf_dataset["fields"]["title"])
        m1 = MinHash(num_perm=128)
        for term in set1:
            m1.update(term.encode("utf8"))

        print("\nquery for '%s' yields datasets" % adrf_dataset["fields"]["title"])
        matches=False
        for key in lshensemble.query(m1, len(set1)):
            print(key,rc_corpus[key]["title"])
            matches = True
        if not matches:
            print("no matches")


if __name__ == '__main__':

    #Enforcing only 2 parameters.
    # if(len(sys.argv[1:]) != 2):
    #     print("Only 2 parameters allowed")
    #     exit(1)
    # corpus_path = sys.argv[1]
    # search_for_matches_path = sys.argv[2]


    corpus_path= "copy_datasets.json"
    search_for_matches_path = "adrf_data/datasets-02-11-2020.json"

    main(corpus_path,search_for_matches_path)
