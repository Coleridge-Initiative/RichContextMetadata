import re
import sys
import codecs
import json
from difflib import SequenceMatcher
from pprint import pprint
from fuzzywuzzy import fuzz
from datasketch import MinHashLSHEnsemble, MinHash
from sklearn import metrics

KNOWN = 1
UNKNOWN = 0
DEBUG = False
CALIBRATE_LSH = False
LSH_THRESHOLD = 0.88

def get_set_of_words(text):
    return re.sub("[\W+]", " ", text).lower().split()


def create_lsh_ensemble(lsh_threshold, rc_corpus):
    print("creating MinHashLSHEnsemble with threshold=%s, num_perm=128, num_part=16..." % lsh_threshold)
    # Create an LSH Ensemble index with threshold and number of partition settings.
    lshensemble = MinHashLSHEnsemble(threshold=lsh_threshold, num_perm=128, num_part=16)
    print("indexing all RC dataset's MinHash...")
    # Index takes an iterable of (key, minhash, size)
    lshensemble.index([(key, values["min_hash"], len(values["words"])) for key, values in rc_corpus.items()])
    return lshensemble


def test_lsh_threshold(adrf_classified_minhash, rc_corpus, lsh_threshold):

    lshensemble = create_lsh_ensemble(lsh_threshold, rc_corpus)

    # test by querying the LSH Ensemble with each ADRF dataset title to explore potential matches
    results = list()
    for adrf_id, values in adrf_classified_minhash.items():
        m1 = values["min_hash"]
        set1 = values["words"]
        #print("\nquery for '%s' yields datasets" % adrf_dataset["fields"]["title"])
        matches = False
        for key in lshensemble.query(m1, len(set1)):
            #print(key, rc_corpus[key]["title"])
            matches = True
            break
        if matches:
            results.append(KNOWN)
        else:
            results.append(UNKNOWN)
            #print("no matches")

    return results


def load_test_vector(adrf_dataset_list,true_links, true_not_links): ## TODO: this is partially built

    vector = list()
    classified = list()
    if DEBUG: print("creating classified_ids_list...using the list below to compare adrf walk through order to future walk throughs")
    for adrf_dataset in adrf_dataset_list:
        if DEBUG: print(adrf_dataset["fields"]["dataset_id"])
        if adrf_dataset["fields"]["dataset_id"] in true_links:
            vector.append(KNOWN)
            classified.append(adrf_dataset["fields"]["dataset_id"])
        elif adrf_dataset["fields"]["dataset_id"] in true_not_links:
            vector.append(UNKNOWN)
            classified.append(adrf_dataset["fields"]["dataset_id"])

    return vector,classified


def create_test_vector(rc_dataset_list,adrf_dataset_list):

    true_links = set()
    true_not_links = set()

    for adrf_dataset in adrf_dataset_list:
        title = adrf_dataset["fields"]["title"]
        url = adrf_dataset["fields"]["source_url"]
        adrf_id = adrf_dataset["fields"]["dataset_id"]

        # Excluding by provider (manual search) ## TODO: subject to change!
        if adrf_dataset["fields"]["data_provider"] in [6,7,12,14,17,48,44,40]: #other providers ID would be 30, 29, 26, 23,22,19,18,17,15
            true_not_links.add(adrf_id)
            continue

        # TODO: check manually from https://github.com/NYU-CI/RCCustomers/blob/5e71284c893f39e670a474ec9b7110ec04593e09/customers/USDA/bin/usda_datadump.json
        if title in [
            "Information Resources, Inc. (IRI) Consumer Network household-based scanner data",
            "Information Resources, Inc. (IRI) InfoScan retail-based scanner data",
            "FoodAPS National Household Food Acquisition and Purchase Survey",
            "Supplemental Nutrition Assistance Program (SNAP) Administrative Data"
                    ]:
            true_links.add(adrf_id)
            continue

        for rc_dataset in rc_dataset_list:
            if "adrf_id" in rc_dataset and adrf_id == rc_dataset["adrf_id"]:
                true_links.add(adrf_id)
                continue

            if "title" in rc_dataset and title == rc_dataset["title"]:
                true_links.add(adrf_id)
                continue

            if "url" in rc_dataset and url == rc_dataset["url"]:
                true_links.add(adrf_id)
                if DEBUG:
                    print("matched by url", "\n\tADRF",title , "\n\tRC" ,rc_dataset["title"])
                    print("\tADRF",url,"\n\tRC" ,rc_dataset["url"])
                    print("\tADRF",adrf_id,"\n\tRC" ,rc_dataset["id"])
                continue

    return true_links, true_not_links


def get_confusion_matrix_scores(test_vector, result):
    tn, fp, fn, tp = metrics.confusion_matrix(test_vector, result).ravel()

    scores = dict()
    confusion_matrix = dict()
    confusion_matrix["TN"] = tn
    confusion_matrix["FP"] = fp
    confusion_matrix["FN"] = fn
    confusion_matrix["TP"] = tp
    scores["confusion_matrix"] = confusion_matrix
    scores["accuracy_score"] = metrics.accuracy_score(test_vector, result)
    scores["recall_score"] = metrics.recall_score(test_vector, result)
    scores["precision_score"] = metrics.precision_score(test_vector,result)
    scores["f1_score"] = metrics.f1_score(test_vector, result) # harmonic mean of Precision and Recall
    scores["specificity_score"] = tn / (tn + fp)
    scores["False Positive Rate or Type I Error"] = fp / (fp + tn)
    scores["False Negative Rate or Type II Error"] = fn / (fn + tp)
    return scores


def calibrate_lsh_threshold(adrf_classified_minhash, rc_corpus, test_vector):
    calibration_metrics = dict()
    max_f1_score = 0
    selected_lsh_threshold = 0
    for step in range(80, 100, 1):

        lsh_threshold = step / 100
        print(lsh_threshold)

        result = test_lsh_threshold(adrf_classified_minhash, rc_corpus, lsh_threshold)

        scores = get_confusion_matrix_scores(test_vector, result)

        print('confusion matrix for ' + str(lsh_threshold))
        # print("\tTP: " + str(tp) + "\tFP: " + str(fp))
        # print("\tFN: " + str(fn) + "\tTN: " + str(tn))
        pprint(scores["confusion_matrix"])

        calibration_metrics[lsh_threshold] = scores

        if scores["f1_score"] > max_f1_score:
            selected_lsh_threshold = lsh_threshold
            max_f1_score = scores["f1_score"]
    if DEBUG:
        print("\nshowing all metrics...")
        pprint(calibration_metrics)
    print("Selected threshold:", selected_lsh_threshold)
    pprint(calibration_metrics[selected_lsh_threshold])

    return selected_lsh_threshold

def test_sm_threshold(adrf_classified_minhash, lsh_ensemble, rc_corpus, sequenceMatcher_threshold):
    print("******** SequenceMatcher threshold", sequenceMatcher_threshold, "*******")
    # iterate the adrf_dataset_list, but only test the text matcher with the cases present on the test_vector
    results = list()
    for key, values in adrf_classified_minhash.items():

        m1 = values["min_hash"]
        set1 = values["words"]
        matches = False
        # this forces that any match will have at least the SM_threshold
        max_score = sequenceMatcher_threshold

        # search the adrf dataset title in the LSH index and for potential hits
        for rc_dataset_id in lsh_ensemble.query(m1, len(set1)):
            # print(rc_dataset_id, rc_corpus[rc_dataset_id]["title"])
            s = SequenceMatcher(None, rc_corpus[rc_dataset_id]["title"], values["title"])
            # select the best match
            if (s.ratio() >= max_score):
                best_match = rc_dataset_id
                max_score = s.ratio()
                matches = True

        if matches:
            if DEBUG:
                print("Searching for", values["title"])
                print("matches with", best_match, rc_corpus[best_match]["title"])
                print("with a SequenceMatcher ratio", max_score)
            results.append(KNOWN)
        else:
            results.append(UNKNOWN)
            # print("no matches")
    return results


def calibrate_SequenceMatcher(lsh_ensemble, adrf_classified_minhash, rc_corpus, test_vector):

    max_precision_score = 0
    calibration_metrics = dict()
    selected_sm_threshold = 0

    for step in range(80, 100, 1):

        sequenceMatcher_threshold = step / 100

        results = test_sm_threshold(adrf_classified_minhash, lsh_ensemble, rc_corpus, sequenceMatcher_threshold)

        scores = get_confusion_matrix_scores(test_vector, results)

        print('confusion matrix for ' + str(sequenceMatcher_threshold))
        # print("\tTP: " + str(tp) + "\tFP: " + str(fp))
        # print("\tFN: " + str(fn) + "\tTN: " + str(tn))
        pprint(scores["confusion_matrix"])

        calibration_metrics[sequenceMatcher_threshold] = scores

        if scores["precision_score"] > max_precision_score:
            selected_sm_threshold = sequenceMatcher_threshold
            max_precision_score = scores["precision_score"]

    #if DEBUG:
    print("\nshowing all metrics...")
    pprint(calibration_metrics)

    print("Selected threshold:", selected_sm_threshold)
    pprint(calibration_metrics[selected_sm_threshold])

    return selected_sm_threshold


def main(corpus_path, search_for_matches_path):

    ## TODO: Create known true matches and known false matches lists
        # TODO: for 4 true links see https://github.com/NYU-CI/RCCustomers/blob/5e71284c893f39e670a474ec9b7110ec04593e09/customers/USDA/bin/usda_datadump.json

    #Load all dataset adrf_ids and titles from ADRF dump
    with codecs.open(search_for_matches_path, "r", encoding="utf8") as f:
        adrf_dataset_list = json.load(f)

    print("loading ADRF dataset corpus...", type(adrf_dataset_list), len(adrf_dataset_list))

    # Load all dataset ids and titles from dataset.json
        #TODO using a temporal copy instead the most updated version˚
    with codecs.open(corpus_path, "r", encoding="utf8") as f:
        rc_dataset_list = json.load(f)

    print("loading RC dataset corpus...",type(rc_dataset_list),len(rc_dataset_list))


    print("creating MinHash for each RC dataset...")

    # create a MinHash for each dataset title and a structure to access title and its set of unique words
    rc_corpus = dict()
    for dataset in rc_dataset_list:
        d = dict()
        d["title"] = dataset["title"]
        d["words"] = get_set_of_words(dataset["title"])

        mh = MinHash(num_perm=128)
        for term in d["words"]:
            mh.update(term.encode("utf8"))
        d["min_hash"] = mh
        rc_corpus[dataset["id"]] = d


    # TODO: true links were made programatically and true not-links were made manually. A better quality test_vector is needed for end version
    true_links, true_not_links = create_test_vector(rc_dataset_list, adrf_dataset_list)

    #classified_ids is used to run the model only with the adrf_dataset subset that are classified (i.e. exists in test_vector)
    test_vector,classified_ids = load_test_vector(adrf_dataset_list,true_links, true_not_links)

    # create a MinHash for each classified adrf dataset title
    adrf_classified_minhash = dict()
    for adrf_dataset in adrf_dataset_list:

        adrf_id = adrf_dataset["fields"]["dataset_id"]
        if adrf_id not in classified_ids:
            continue #skip the datasets not used in the test_vector
        d = dict()
        d["title"] = adrf_dataset["fields"]["title"]
        d["words"] = get_set_of_words(adrf_dataset["fields"]["title"])

        mh = MinHash(num_perm=128)
        for term in d["words"]:
            mh.update(term.encode("utf8"))

        d["min_hash"] = mh
        adrf_classified_minhash[adrf_id] = d

    if CALIBRATE_LSH:
        lsh_threshoild = calibrate_lsh_threshold(adrf_classified_minhash, rc_corpus, test_vector)
    else:
        lsh_threshoild = LSH_THRESHOLD

    lsh_ensemble = create_lsh_ensemble(lsh_threshoild,rc_corpus)

    sm_min_score = calibrate_SequenceMatcher(lsh_ensemble, adrf_classified_minhash, rc_corpus, test_vector)

    print("selected threshold for SequenceMatcher:",sm_min_score)



if __name__ == '__main__':

    #Enforcing only 2 parameters.
    # if(len(sys.argv[1:]) != 2):
    #     print("Only 2 parameters allowed")
    #     exit(1)
    # corpus_path = sys.argv[1]
    # search_for_matches_path = sys.argv[2]


    corpus_path= "rc_data/copy_datasets.json"
    search_for_matches_path = "adrf_data/datasets-02-11-2020.json"

    main(corpus_path,search_for_matches_path)
