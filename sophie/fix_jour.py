import json
import ast
import sys

# partition = "/Users/sophierand/RCPublications/partitions/20191119_WomensEmploymentStudy_publications.json"


def read_partition(partition):
    with open(partition, "r") as f:
        part = json.load(f)
    with open(partition, "r") as f:
        new_p = json.load(f)
    return part, new_p

def check_results(part,new_p):
    if not len(set([p['title'] for p in new_p])) == len(set([p['title'] for p in part])):
        print('something went wrong')

    if not len(part)==len(new_p):
        print('something went wrong')


def replace_jour(p):
    for pub in p:
        if "original" in pub.keys():
            orig = pub["original"] 
            try:
                j = orig["journal"]
                try:                           
                    eval_orig = ast.literal_eval(j)
                except:
                    eval_orig = j
                if isinstance(eval_orig,dict):
                    journal_title = eval_orig["title"]
                    orig["journal"] = journal_title

            except:
                pass
    return p


def main(partition):
    part, new_p = read_partition(partition)
    check_results(part,new_p)
    new = replace_jour(new_p)
    with open(partition, 'w') as outfile:
        json.dump(new_p, outfile,indent = 2)

if __name__ == "__main__":
    partition = "/Users/sophierand/RCPublications/partitions/" + sys.argv[1]
    print("Reading from path: {}".format(partition))
    main(partition)
    