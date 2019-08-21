import json
import os
import metadata_funs

search_path = '/Users/sophierand/RichContextMetadata/metadata/'
pub_paths = [search_path+f for f in os.listdir(search_path) if f.endswith("pubs.json")]

def collate_pubs(pub_paths):
    pub_list = []
    for p in pub_paths:
        with open(p) as json_file:
            data = json.load(json_file)
        pub_list.append(data)
    pub_list_flat = metadata_funs.flatten(pub_list)
    return pub_list_flat
    
def add_pub_ids(pub_list_flat):
    pub_list_final = []
    for p in pub_list_flat:
        try:
            pub_id = metadata_funs.get_hash((p['title'],p['journal']['title']),prefix = 'pub-')
#             pub_id = "pub-{}".format(metadata_funs.get_hash((p['title'],p['doi'],p['journal']['title'])))
            p.update({'pub_id':pub_id})
            pub_list_final.append(p)
        except:
            pass
    return pub_list_final


def dedup_pub_list(pub_list_final):
    seen = set()
    dedup_pub_list = []
    for p in pub_list_final:
        id_tup = tuple((p['related_dataset'],p['pub_id']))
        if id_tup not in seen:
            seen.add(id_tup)
            dedup_pub_list.append(p)
    return dedup_pub_list

def gen_publist_lim(pub_list_final):
    pub_list_lim = []
    for p in pub_list_final:
        lim_dict = {'pub_id':p['pub_id'],'title':p['title'],'related_dataset':p['related_dataset']}
        try:
            lim_dict.update({'journal':p['journal']['title']})
        except:
            pass
        try:
            lim_dict.update({'linkage_source':p['linkage_source']})
        except:
            pass
        try:
            lim_dict.update({'doi':p['doi']})
        except:
            pass        
        pub_list_lim.append(lim_dict)
    return pub_list_lim  

search_path = '/Users/sophierand/RichContextMetadata/metadata/'
pub_paths = [search_path+f for f in os.listdir(search_path) if f.endswith("pubs.json")]
pub_list_flat = collate_pubs(pub_paths)
pub_list_final = add_pub_ids(pub_list_flat)
pub_list_final_dedup = dedup_pub_list(pub_list_final)
pub_list_lim = gen_publist_lim(pub_list_final_dedup)
json.dump(pub_list_lim, open('/Users/sophierand/RichContextMetadata/publications_lim.json', 'w'), indent=2)    
json.dump(pub_list_final_dedup, open('/Users/sophierand/RichContextMetadata/publications.json', 'w'), indent=2)