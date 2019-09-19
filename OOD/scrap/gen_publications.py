import manually_curated_publications
import stringsearch_publications
import getpass
import metadata_funs
import importlib
importlib.reload(manually_curated_publications)
importlib.reload(stringsearch_publications)

def gen_api_client():
    api_client = metadata_funs.create_api_client()
    return api_client

def gen_manual_pubs(api_client):
    manually_curated_publications.main(api_client = api_client)
    
def gen_ss_pubs(api_client):
    stringsearch_publications.main(api_client = api_client)


