import manually_curated_publications
import stringsearch_publications
import getpass
import metadata_funs

print('enter your dimensions api username')
user = input()
print('enter your dimensions api password')
password = getpass.getpass()

api_client = metadata_funs.connect_ds_api(username=user,password=password)

b = manually_curated_publications.main(api_client = api_client)

a = stringsearch_publications.main(api_client = api_client)