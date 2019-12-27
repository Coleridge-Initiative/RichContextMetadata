import json
from datetime import datetime
from urllib.parse import urlparse
from collections import OrderedDict


def get_setup_info():
    """generate pathname for new partition"""
    partition_location = input("path to your local partition subfolder:  ")
    now = datetime.now()
    date_time = now.strftime("%Y%m%d")

    path_name = partition_location + "/" + date_time + "_" + str(hash(now)) + "_pub.json"
    
    return path_name

def get_req_info():
    """get basic required metadata on the publication"""
    title = input("Publication title: ")
    dataset = input("Which dataset does it use? Enter a dataset-id or dataset name")
    return {"title":title,"datasets": dataset}


def url_validator (url):
    """validate the format of a URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

def get_pub_md():
    """generate non-required metadata"""
    pub_md = {}
    url = input("Enter a url for the publication: ")
    if url_validator(url):
        pub_md["url"] = url
    if not url_validator(url):
        print('That url is invalid')
    pdf = input("Enter a pdf for the publication: ")
    journal = input("Enter a journal for the publication: ")
    doi = input("Enter a doi for the publication: ")
    pub_md["pdf"] = pdf
    pub_md["journal"] = journal
    pub_md["doi"] = doi
    orig = {"original":pub_md}
    return orig


def check_dataset(dataset):
    """make sure dataset exists"""
    with open('/Users/sophierand/RCDatasets/datasets.json') as json_file:
        data_list = json.load(json_file)
    if "dataset" in dataset:
        check_ds = [d for d in data_list if d['id'] == dataset]
    elif "dataset" not in dataset:
        check_ds = [d for d in data_list if d['title'] == dataset]
    if len(check_ds) > 0:
        return True
    elif len(check_ds) == 0:
        print('dataset "{}" is not in datasets.json.'.format(dataset))
        return False

def write_partition(md):
    """write partition to folder"""
    path_name = get_setup_info()
    print("Writing {} to a partition: {} ".format(md,path_name))
    with open(path_name, 'w') as outfile:
        json.dump(md, outfile,indent = 2)


def check_addition():
    req = get_req_info()
    title = req['title']
    dataset = req['datasets']
    if title and dataset:
        if check_dataset(dataset):
            orig = get_pub_md()
            req.update(orig)
            if len(req) > 0:
                write_partition([req])


if __name__ == "__main__":
    check_addition()
