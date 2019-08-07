import json
import os
import metadata_funs

pub_paths = [os.path.join(os.getcwd(),p) for p in ['manually_curated_pubs.json','stringsearch_pubs.json']]

pub_list = []
for p in pub_paths:
    with open(p) as json_file:
        data = json.load(json_file)
    pub_list.append(data)
    
    
pub_list_flat = metadata_funs.flatten(pub_list)

pub_list_final = []
for p in pub_list_flat:
    try:
        pub_id = "pub-{}".format(metadata_funs.get_hash((p['title'],p['doi'],p['journal']['title'])))
        p.update({'pub_id':pub_id})
        pub_list_final.append(p)
    except:
        pass
    
pub_list_lim = [{'pubs':p['pub_id'],'title':p['title'],'doi':p['doi'],'journal':p['journal']['title']} for p in pub_list_final]
  
json.dump(pub_list_lim, open('./publications_lim.json', 'w'), indent=2)    
json.dump(pub_list_flat, open('./publications.json', 'w'), indent=2)