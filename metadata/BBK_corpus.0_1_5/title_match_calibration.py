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


def main(title1, title2):

    ## TODO: Load all dataset ids and titles from dataset.json

    ## TODO: Load all dataset adrf_ids and titles from ADRF dump

    ## TODO: Create known true matches and known false matches lists
        # TODO: for 4 true links see https://github.com/NYU-CI/RCCustomers/blob/5e71284c893f39e670a474ec9b7110ec04593e09/customers/USDA/bin/usda_datadump.json

    ## TODO: Create 1 set and 1 MinHash per dataset title

    ## TODO: Loop changing threshold from 0.1 to 0.9
        ## TODO: for each threshold, calculate 'confusion matrix'


    # Load all dataset ids and titles from dataset.json
        #using a temporal copy
    path= "copy_datasets.json"
    with codecs.open(path, "r", encoding="utf8") as f:
        rc_dataset_list = json.load(f)

    print("loading RC dataset corpus...",type(rc_dataset_list),len(rc_dataset_list))

    rc_corpus = defaultdict()
    for dataset in rc_dataset_list:
        rc_corpus[dataset["id"]]=get_set_of_words(dataset["title"])

    print("creating MinHash for each RC dataset...")
    rc_minhash = defaultdict()
    for id,words in rc_corpus.items():
        mh = MinHash(num_perm=128)
        for term in words:
            mh.update(term.encode("utf8"))
        rc_minhash[id]=mh

    print("creating MinHashLSHEnsemble with threshold=0.9, num_perm=128, num_part=16...")
    # Create an LSH Ensemble index with threshold and number of partition
    # settings.
    lshensemble = MinHashLSHEnsemble(threshold=0.9, num_perm=128, num_part=16)

    print("indexing all RC dataset's MinHash...")
    # Index takes an iterable of (key, minhash, size)
    lshensemble.index([(key,values,len(values)) for key, values in rc_minhash.items()])

    path= "adrf_data/datasets-02-11-2020.json"
    with codecs.open(path, "r", encoding="utf8") as f:
        adrf_dataset_list = json.load(f)

    print("loading ADRF dataset corpus...",type(adrf_dataset_list), len(adrf_dataset_list))

    for adrf_dataset in adrf_dataset_list:
        set1=get_set_of_words(adrf_dataset["fields"]["title"])
        m1 = MinHash(num_perm=128)
        for term in set1:
            m1.update(term.encode("utf8"))

        print("query for",adrf_dataset["fields"]["title"],"yields datasets")
        for key in lshensemble.query(m1, len(set1)):
            print(key,rc_corpus[key])
        break


def test_LSH_ensemble(title1, title2):

    set1 = get_set_of_words(title1)
    set2 = get_set_of_words(title2)

    title3="dummy text about universities and innovation umetrics"
    set3 = get_set_of_words(title3)

    print(set1)
    print(set2)
    print(set3)

    # Create MinHash objects
    m1 = MinHash(num_perm=128)
    m2 = MinHash(num_perm=128)
    for d in set1:
        m1.update(d.encode('utf8'))
    for d in set2:
        m2.update(d.encode('utf8'))


    m3 = MinHash(num_perm=128)
    for d in set3:
        m3.update(d.encode('utf8'))


    # Create an LSH Ensemble index with threshold and number of partition
    # settings.
    lshensemble = MinHashLSHEnsemble(threshold=0.5, num_perm=128,
                                     num_part=16)

    # Index takes an iterable of (key, minhash, size)
    lshensemble.index([("title 2", m2, len(set2)), ("title 1", m1, len(set1))])

    # Using m1 as the query, get an result iterator
    print("matches for title1")
    for key in lshensemble.query(m1, len(set1)):
        print(key)

    print("matches for title2")
    for key in lshensemble.query(m2, len(set2)):
        print(key)


    print("matches for title3")
    for key in lshensemble.query(m3, len(set3)):
        print(key)

    return


    m3 = MinHash(num_perm=128)
    for d in set3:
        m3.update(d.encode('utf8'))



    # Check for membership using the key
    print("m2" in lshensemble)
    print("m3" in lshensemble)
    print("m1" in lshensemble)

    # Using m1 as the query, get an result iterator
    print("Sets with containment > 0.8:")




if __name__ == '__main__':

    #Enforcing only 2 parameters.
    # if(len(sys.argv[1:]) != 2):
    #     print("Only 2 parameters allowed")
    #     exit(1)
    # title1 = sys.argv[1]
    # title2 = sys.argv[2]

    title1= "Universities: Measuring the Impacts of Research on Innovation, Competitiveness, and Science (UMETRICS)"
    title2= "Universities: Measuring the Impacts of Research on Innovation, Competitiveness, and Science"

    #test_LSH_ensemble(title1, title2)

    main(title1,title2)
