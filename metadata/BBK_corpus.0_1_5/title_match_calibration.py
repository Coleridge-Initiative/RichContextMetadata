import re
import sys
import codecs
import json
from difflib import SequenceMatcher
from pprint import pprint
from fuzzywuzzy import fuzz
from datasketch import MinHashLSHEnsemble, MinHash
from sklearn import metrics
from pathlib import Path
import pandas as pd

KNOWN = 1
UNKNOWN = 0
DEBUG = False
CALIBRATE_LSH = True
LSH_THRESHOLD = 0.79 #Required when CALIBRATE_LSH == False
CALIBRATE_SEQUENCEMATCHER = True
SEQUENCEMATCHER_THRESHOLD = 0.55 #Required when CALIBRATE_SEQUENCEMATCHER == False

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

def load_classified_vector(vector_path,adrf_dataset_list):
    vector = list()
    classified = list()

    vectorDF = pd.read_csv(vector_path)

    for adrf_dataset in adrf_dataset_list:
        link = False

        #search the adrf_dataset in the classified vector
        for index, row in vectorDF.iterrows():
            if adrf_dataset["fields"]["dataset_id"] == row["adrf_id"]:
                if row['link'] != "FALSE":
                    vector.append(KNOWN)
                    classified.append(adrf_dataset["fields"]["dataset_id"])
                    break
                else:
                    vector.append(UNKNOWN)
                    classified.append(adrf_dataset["fields"]["dataset_id"])
                    break


    return vector,classified


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
    for step in range(60, 100, 1):

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

    for step in range(50, 100, 1):

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


def record_linking_sm(adrf_dataset_list, rc_corpus, lsh_ensemble, sm_min_score):


    # create a MinHash for each adrf dataset title
    result_list = list()

    for adrf_dataset in adrf_dataset_list:

        matches = False

        adrf_id = adrf_dataset["fields"]["dataset_id"]
        title = adrf_dataset["fields"]["title"]
        words = get_set_of_words(adrf_dataset["fields"]["title"])

        mh = MinHash(num_perm=128)
        for term in words:
            mh.update(term.encode("utf8"))

        max_score = sm_min_score
        for rc_dataset_id in lsh_ensemble.query(mh, len(words)):
            # print(rc_dataset_id, rc_corpus[rc_dataset_id]["title"])
            s = SequenceMatcher(None, rc_corpus[rc_dataset_id]["title"], title)
            # select the best match
            if (s.ratio() >= max_score):
                best_match = rc_dataset_id
                max_score = s.ratio()
                matches = True

        if matches:
            # if DEBUG:
            #     print("Searching for", values["title"])
            #     print("matches with", best_match, rc_corpus[best_match]["title"])
            #     print("with a SequenceMatcher ratio", max_score)
            adrf_match = dict()
            adrf_match["adrf_id"] = adrf_id
            adrf_match["title"] = title
            adrf_match["url"] = adrf_dataset["fields"]["source_url"]
            adrf_match["description"] = adrf_dataset["fields"]["description"]

            rc_match = dict()
            rc_match["dataset_id"] = best_match
            rc_match["title"] = rc_corpus[best_match]["title"]

            if "url" in rc_corpus[best_match]:
                rc_match["url"] = rc_corpus[best_match]["url"]

            if "description" in rc_corpus[best_match]:
                rc_match["description"] = rc_corpus[best_match]["description"]

            result_list.append(adrf_match)
            result_list.append(rc_match)

    # write json file
    out_path = "matched_datasets_SequenceMatcher.json"
    with codecs.open(Path(out_path), "wb", encoding="utf8") as f:
        json.dump(result_list, f, indent=4, sort_keys=True, ensure_ascii=False)

    print(len(result_list)/2,"matched datasets")

## TODO: the main logic in this method is the same as test_sm_threshold. Try to generalize it and deduplicate code.
def test_fuzzy_threshold(adrf_classified_minhash, lsh_ensemble, rc_corpus, fuzzy_threshold):
    print("******** Fuzzy matcher threshold", fuzzy_threshold, "*******")
    # iterate the adrf_dataset_list, but only test the text matcher with the cases present on the test_vector
    results = list()
    for key, values in adrf_classified_minhash.items():

        m1 = values["min_hash"]
        set1 = values["words"]
        matches = False
        # this forces that any match will have at least the SM_threshold
        max_score = fuzzy_threshold

        # search the adrf dataset title in the LSH index and for potential hits
        for rc_dataset_id in lsh_ensemble.query(m1, len(set1)):
            # print(rc_dataset_id, rc_corpus[rc_dataset_id]["title"])
            ratio = fuzz.token_sort_ratio(rc_corpus[rc_dataset_id]["title"], values["title"])
            # select the best match
            if ratio >= max_score:
                best_match = rc_dataset_id
                max_score = ratio
                matches = True

        if matches:
            if DEBUG:
                print("Searching for", values["title"])
                print("matches with", best_match, rc_corpus[best_match]["title"])
                print("with a Fuzzy matcher ratio", max_score)
            results.append(KNOWN)
        else:
            results.append(UNKNOWN)
            # print("no matches")
    return results

## TODO: the logic in this method is the same as calibrate_SequenceMatcher. Try to generalize it and deduplicate code.
def calibrate_FuzzyWuzzy(lsh_ensemble, adrf_classified_minhash, rc_corpus, test_vector):

    max_precision_score = 0
    calibration_metrics = dict()
    selected_fuzzy_threshold = 0

    for step in range(50, 80, 1):

        fuzzy_threshold = step #/ 100 #fuzzy ratio is 1 to 100

        results = test_fuzzy_threshold(adrf_classified_minhash, lsh_ensemble, rc_corpus, fuzzy_threshold)

        scores = get_confusion_matrix_scores(test_vector, results)

        print('confusion matrix for ' + str(fuzzy_threshold))

        pprint(scores["confusion_matrix"])

        calibration_metrics[fuzzy_threshold] = scores

        if scores["precision_score"] > max_precision_score:
            selected_fuzzy_threshold = fuzzy_threshold
            max_precision_score = scores["precision_score"]

    #if DEBUG:
    print("\nshowing all metrics...")
    pprint(calibration_metrics)

    print("Selected threshold:", selected_fuzzy_threshold)
    pprint(calibration_metrics[selected_fuzzy_threshold])

    return selected_fuzzy_threshold

def record_linking_fuzzy(adrf_dataset_list, rc_corpus, lsh_ensemble, fuzzy_min_score):


    # create a MinHash for each adrf dataset title
    result_list = list()

    for adrf_dataset in adrf_dataset_list:

        matches = False

        adrf_id = adrf_dataset["fields"]["dataset_id"]
        title = adrf_dataset["fields"]["title"]
        words = get_set_of_words(adrf_dataset["fields"]["title"])

        mh = MinHash(num_perm=128)
        for term in words:
            mh.update(term.encode("utf8"))

        max_score = fuzzy_min_score
        for rc_dataset_id in lsh_ensemble.query(mh, len(words)):
            # print(rc_dataset_id, rc_corpus[rc_dataset_id]["title"])
            ratio = fuzz.token_sort_ratio(rc_corpus[rc_dataset_id]["title"], title)
            # select the best match
            if ratio >= max_score:
                best_match = rc_dataset_id
                max_score = ratio
                matches = True

        if matches:
            # if DEBUG:
            #     print("Searching for", values["title"])
            #     print("matches with", best_match, rc_corpus[best_match]["title"])
            #     print("with a SequenceMatcher ratio", max_score)
            adrf_match = dict()
            adrf_match["adrf_id"] = adrf_id
            adrf_match["title"] = title
            adrf_match["url"] = adrf_dataset["fields"]["source_url"]
            adrf_match["description"] = adrf_dataset["fields"]["description"]

            rc_match = dict()
            rc_match["dataset_id"] = best_match
            rc_match["title"] = rc_corpus[best_match]["title"]

            if "url" in rc_corpus[best_match]:
                rc_match["url"] = rc_corpus[best_match]["url"]

            if "description" in rc_corpus[best_match]:
                rc_match["description"] = rc_corpus[best_match]["description"]

            result_list.append(adrf_match)
            result_list.append(rc_match)

    # write json file
    out_path = "matched_datasets_fuzzy.json"
    with codecs.open(Path(out_path), "wb", encoding="utf8") as f:
        json.dump(result_list, f, indent=4, sort_keys=True, ensure_ascii=False)

    print(len(result_list)/2,"matched datasets")


def main(corpus_path, search_for_matches_path, classified_vector_path):

    #Load all dataset adrf_ids and titles from ADRF dump
    with codecs.open(search_for_matches_path, "r", encoding="utf8") as f:
        adrf_dataset_list = json.load(f)

    print("loaded ADRF dataset corpus...", type(adrf_dataset_list), len(adrf_dataset_list))

    # Load all dataset ids and titles from dataset.json
    with codecs.open(corpus_path, "r", encoding="utf8") as f:
        rc_dataset_list = json.load(f)

    print("loaded RC dataset corpus...",type(rc_dataset_list),len(rc_dataset_list))

    test_vector,classified_ids = load_classified_vector(classified_vector_path, adrf_dataset_list)
    print("loaded clasiffied data from",classified_vector_path,"|",len(test_vector),"data points")

    print("creating MinHash for each RC dataset...")

    # create a MinHash for each dataset title and a structure to access title and its set of unique words
    rc_corpus = dict()
    for dataset in rc_dataset_list:
        d = dict()
        d["title"] = dataset["title"]
        d["words"] = get_set_of_words(dataset["title"])
        if "url" in dataset:
            d["url"] = dataset["url"]
        if "description" in dataset:
            d["description"] = dataset["description"]

        mh = MinHash(num_perm=128)
        for term in d["words"]:
            mh.update(term.encode("utf8"))
        d["min_hash"] = mh
        rc_corpus[dataset["id"]] = d

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
        print("***starting LSH Ensemble threshold calibration***")
        lsh_threshoild = calibrate_lsh_threshold(adrf_classified_minhash, rc_corpus, test_vector)
    else:
        lsh_threshoild = LSH_THRESHOLD

    lsh_ensemble = create_lsh_ensemble(lsh_threshoild,rc_corpus)

    if CALIBRATE_SEQUENCEMATCHER:
        print("***starting SequenceMatcher threshold calibration***")
        sm_min_score = calibrate_SequenceMatcher(lsh_ensemble, adrf_classified_minhash, rc_corpus, test_vector)
    else:
        sm_min_score = SEQUENCEMATCHER_THRESHOLD

    print("selected threshold for SequenceMatcher:",sm_min_score)

    record_linking_sm(adrf_dataset_list, rc_corpus, lsh_ensemble , sm_min_score)
    #
    # print("***starting FuzzyWuzzy threshold calibration***")
    fuzzy_min_score = calibrate_FuzzyWuzzy(lsh_ensemble, adrf_classified_minhash, rc_corpus, test_vector)
    #
    print("selected threshold for SequenceMatcher:", fuzzy_min_score)

    record_linking_fuzzy(adrf_dataset_list, rc_corpus, lsh_ensemble, fuzzy_min_score)


if __name__ == '__main__':

    #Enforcing only 2 parameters.
    # if(len(sys.argv[1:]) != 2):
    #     print("Only 2 parameters allowed")
    #     exit(1)
    # corpus_path = sys.argv[1]
    # search_for_matches_path = sys.argv[2]

    # TODO using a temporal copy of datsets.json instead the most updated version˚
    corpus_path= "rc_data/copy_datasets.json"
    search_for_matches_path = "adrf_data/datasets-02-11-2020.json"

    # TODO: classified vector is probably biased. It does not cover any edge case.
    classified_vector_path = "training_vector_1.01.csv"

    main(corpus_path,search_for_matches_path,classified_vector_path)
