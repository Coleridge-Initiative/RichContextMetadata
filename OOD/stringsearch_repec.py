import json
import metadata_funs
import time
import os
import datetime
import unicodedata
def read_datasets():
    datasets_json_path = '/Users/sophierand/RichContextMetadata/datasets.json'
    with open(datasets_json_path) as json_file:
        datasets_json = json.load(json_file)
    return datasets_json

def return_string_search_dyads(dataset_string, api_client):
    """
    intake a dataset name
    , identify papers with that term in the full text
    , and return publication metadata
    """
    api_return = metadata_funs.run_exact_string_search(string = dataset_string, api_client = api_client)
    pub_metadata = []
    for i in api_return['publications']:
        time.sleep( 6 )
        pub_id = i['id']
        id_metadata = metadata_funs.run_pub_id_search(dimensions_id = pub_id, api_client = api_client)
        id_metadata.update({'dimensions_id':pub_id,'related_dataset_name':dataset_string})
        pub_metadata.append(id_metadata)
    return pub_metadata


def gen_ss_dyad(dataset_name_dict,api_client):
    """
    intake a dataset dictionary that has a dataset_id and a list of names (name+alias)
    , and each is run through the string_search_dyads function to return publication metadata
    """

    dataset_names_list = dataset_name_dict['title']
    dataset_name_dict['title']= unicodedata.normalize('NFC',dataset_name_dict['title'])
    dataset_id = dataset_name_dict['dataset_id']
    store_dyads = []
#     for ds in dataset_names_list:
    pub_dataset_dyads  = return_string_search_dyads(dataset_string = dataset_names_list, api_client = api_client)
    store_dyads.append(pub_dataset_dyads)
    store_dyads_flat = metadata_funs.flatten(store_dyads)
    for s in store_dyads_flat:
        s.update({'related_dataset':dataset_id,'linkage_source':'dataset_stringsearch'})
    return store_dyads_flat


def gen_dyad_list(ds_names,api_client):
    """
    intake a list of dataset dictionaries
    , where each dict has a dataset_id and a list of names (name+alias)
    , and run through gen_ss_dyad
    """
    big_list = []
    try:
        for d in ds_names:
            print('looking for ',d['title'],d['dataset_id'], ' now')
            # a = 'i would do a string search with {}'.format(d)
            try:
                a = gen_ss_dyad(dataset_name_dict = d,api_client = api_client)
                stringsearch_pubs_path_this = os.path.join(os.getcwd(),'repec/{}stringsearch_dataset{}_pubs.json'.format(metadata_funs.get_hash(str(datetime.datetime.now())),d['title']))
                json.dump(a, open(stringsearch_pubs_path_this, 'w'), indent=2)
                big_list.append(a)
                time.sleep(1)
            except:
                pass
        return big_list
    except KeyboardInterrupt or UnicodeEncodeError:
        return big_list

def get_repec_datasets():
    datasets = read_datasets()
    # owner_list = ['Deutsche Bundesbank',"United States Department of Agriculture (USDA)"]
    bb_usda_datasets = []
    for d in datasets:
        try:
            owner = d['data_steward']
            if 'Deutsche Bundesbank' or 'USDA' in d['data_provider']:
    #         if owner in owner_list:
                bb_usda_datasets.append(d)
        except:
            pass
    return bb_usda_datasets

# def get_repec_datasets():
#     datasets = read_datasets()
#     owner_list = ['Deutsche Bundesbank',"United States Department of Agriculture (USDA)"]
#     bb_usda_datasets = []
#     for d in datasets:
#         try:
#             owner = d['data_steward']
#             if owner in owner_list:
#                 bb_usda_datasets.append(d)
#         except:
#             try:
#                 owner = d['data_provider']
#                 if owner in owner_list:
#                     bb_usda_datasets.append(d)
#             except:
#                 pass
#     return bb_usda_datasets

bb_usda_datasets = get_repec_datasets()
print(bb_usda_datasets)
api_client = metadata_funs.create_api_client()
usda_bb_pubs = gen_dyad_list(bb_usda_datasets,api_client)
final_list = metadata_funs.flatten(usda_bb_pubs)
stringsearch_pubs_path = os.path.join(os.getcwd(),'repec/string_searches/{}stringsearch_pubs.json'.format(metadata_funs.get_hash(str(datetime.datetime.now()))))

json.dump(final_list, open(stringsearch_pubs_path, 'w'), indent=2)
