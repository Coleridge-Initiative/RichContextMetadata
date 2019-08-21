import dimensions_search_api_client as dscli
import time
import getpass
import hashlib
import os
import json
import hashlib
import json
import rdflib
import sys
import unicodedata

def scrub_unicode (text):
    """
    try to handle the unicode edge cases encountered in source text,
    as best as possible
    """
    x = " ".join(map(lambda s: s.strip(), text.split("\n"))).strip()

    x = x.replace('“', '"').replace('”', '"')
    x = x.replace("‘", "'").replace("’", "'").replace("`", "'")
    x = x.replace("`` ", '"').replace("''", '"')
    x = x.replace('…', '...').replace("\\u2026", "...")
    x = x.replace("\\u00ae", "").replace("\\u2122", "")
    x = x.replace("\\u00a0", " ").replace("\\u2022", "*").replace("\\u00b7", "*")
    x = x.replace("\\u2018", "'").replace("\\u2019", "'").replace("\\u201a", "'")
    x = x.replace("\\u201c", '"').replace("\\u201d", '"')

    x = x.replace("\\u20ac", "€")
    x = x.replace("\\u2212", " - ") # minus sign

    x = x.replace("\\u00e9", "é")
    x = x.replace("\\u017c", "ż").replace("\\u015b", "ś").replace("\\u0142", "ł")    
    x = x.replace("\\u0105", "ą").replace("\\u0119", "ę").replace("\\u017a", "ź").replace("\\u00f3", "ó")

    x = x.replace("\\u2014", " - ").replace('–', '-').replace('—', ' - ')
    x = x.replace("\\u2013", " - ").replace("\\u00ad", " - ")

    x = str(unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("utf-8"))

    # some content returns text in bytes rather than as a str ?
    try:
        assert type(x).__name__ == "str"
    except AssertionError:
        print("not a string?", type(x), x)

    return x


def get_hash (strings, prefix=None, digest_size=10):
    """
    construct a unique identifier from a collection of strings
    """
    m = hashlib.blake2b(digest_size=digest_size)
    
    for elem in sorted(map(lambda x: x.encode("utf-8").lower().strip(), strings)):
        m.update(elem)

    if prefix:
        id = prefix + m.hexdigest()
    else:
        id = m.hexdigest()

    return id


def create_api_client():
    print('enter your dimensions api username')
    user = input()
    print('enter your dimensions api password')
    pw = getpass.getpass()
    api_client = connect_ds_api(username = user, password = pw)
    return api_client

def connect_ds_api(username,password):
    api_client = dscli.DimensionsSearchAPIClient()
    api_client.set_max_in_items( 100 )
    api_client.set_max_return( 1000 )
    api_client.set_max_overall_returns( 50000 )
    api_client.set_username( username )
    api_client.set_password( password )
    return api_client

def run_string_search(string,api_client):
    search_string = 'search publications in full_data for "{}" return publications'.format(string)
    api_response = api_client.execute_query(query_string_IN = search_string )
    return api_response


def run_exact_string_search(string,api_client):
    search_string = 'search publications in full_data for "\\"{}\\"" return publications'.format(string)
    api_response = api_client.execute_query(query_string_IN = search_string )
    return api_response

def run_doi_search(doi_id,api_client):
    doi_search_string = 'search publications where doi = "{}" return publications[all] limit 1'.format(doi_id)
    doi_response = api_client.execute_query( query_string_IN=doi_search_string )
    publication_metadata_full = doi_response['publications']
    if publication_metadata_full:
        publication_metadata = publication_metadata_full[0]
        return publication_metadata


def run_pub_id_search(dimensions_id,api_client):
    id_search_string = 'search publications where id = "{}" return publications[all] limit 1'.format(dimensions_id)
    id_response = api_client.execute_query( query_string_IN=id_search_string )
    publication_metadata = id_response['publications'][0]
    return publication_metadata



def flatten(l):
    flat_list = [item for sublist in l for item in sublist]
    return flat_list


def run_author_search(author_dimensions_id, api_client):
    auth_query = 'search researchers where id = "{}" return researchers[all]'.format(author_dimensions_id)
    author_return = api_client.execute_query( query_string_IN=auth_query )
    author_metadata = author_return['researchers']
    return author_metadata

def read_datasets():
    dataset_json_path = os.path.join(os.getcwd(),'datasets.json')
    with open(dataset_json_path) as json_file:
        dataset_json = json.load(json_file)
#     dataset_names =[{'dataset_name':d['title'],'dataset_id':d['dataset_id']} for d in dataset_json]
    return dataset_json

def read_publications():
    publication_json_path = '/Users/sophierand/RichContextMetadata/publications_lim.json'
    with open(publication_json_path) as json_file:
        publications_json = json.load(json_file)
    return publications_json