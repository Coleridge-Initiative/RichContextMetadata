# Notes


## Datasets

The datasets are one of the "givens" in this system.
We consider their names to be known and invariant.
Nonetheless, there may be edits required.
The following script regenerates `uuid` values for each dataset:

```
./bin/gen_dat_id.py corpus/dataset.json 
```


## RCC publications

The following script runs the OpenAIRE API to lookup the (likely)
publisher name and open access URL for each publication from the RCC
training set:

```
./bin/rcc_openaire.py
```

NB: this script needs updates!!! remove counters, output dicts


## Aligning the publisher names

The names of publishers will be an ongoing hot mess.
While the full name of a publishher may appear on a publication, there
are formal abbreviations used in citations, which we'll use here.
Unfortunatly, these inconsistencies in naming break the `uuid` values
for publications, so we must use a canonical list.

The following script generates a tally of the publisher names used so
far, and helps catch inconsistencies that lead to broken links later:

```
./bin/tally_pubs.py corpus/publication.json
```


## Stitch

NB: needs work!!! pickup with `dat/rcc_out.json` instead of `dat/out`

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
Delete any entry in `publication.json` to cause it to be regenerated.

```
./bin/stitch.py
```


## Generate a corpus to publish

In this final step, the `gen_ttl.py` script reads:

 - `corpus/publication.json`
 - `corpus/dataset.json`
 - `corpus/vocab.json`

Then generates both `tmp.ttl` and `tmp.jsonld` which subsequently must
be renamed and moved into the corpus repo manually.
This step also generates the publication `uuid` values (late binding).

```
./bin/gen_ttl.py
```

