# Notes


## Aligning the publisher names

The names of publishers will be an ongoing hot mess.
While the full name of a publishher may appear on a publication, there
are formal abbreviations used in citations, which we'll use here.
Unfortunatly, these inconsistencies in naming break the `uuid` values
for publications, so we must use a canonical list.

The following script generates a tally of the publisher names used so
far, and helps catch inconsistencies that lead to broken links later:

```
./tally_pubs.py corpus/publication.json
```


## Stitch

The preconditions for including a publication in the corpus are:

 - linked to 1 or more known datasets
 - has a `title`
 - has a `publisher`
 - has a `url`
 - has a URL for an open access `pdf`

Optionally, each publication may have a unique `doi` identifier.
Most all of the publications have titles, at a minimum, although some
are incorrect and must be modified.
Earlier stages of scripts lookup `publisher` and `url`, then the `pdf`
step is manual.
Note that if `title` or `publisher` get modified, the generated `uuid`
will change.

After all of these preconditions are met, the `stitch.py` script
generates a JSON entity (hash) to include into the `publication.json`
file -- only if it is not included already.
Delete an entry to regenerate it.


## Generate corpus to publish

In this final step, the `gen_ttl.py` script reads:

 - `corpus/publication.json`
 - `corpus/dataset.json`
 - `vocab.json`

Then generates both `tmp.ttl` and `tmp.jsonld` which need to be
renamed and moved into the corpus repo:

```
gen_ttl.py
```