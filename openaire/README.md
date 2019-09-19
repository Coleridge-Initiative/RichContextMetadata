# Notes


## 1. Datasets

Datasets are one of the "givens" in this system: they represent the
known _labels_ (aka "classes") in the ground truth for this corpus.
In contrast, the set of publications gets expanded later in our
workflow, but the set of known datasets does not.

We consider dataset names to be known and invariant -- 
nonetheless, edits may be required.


## 2. RCC publications

The following script runs the OpenAIRE API to lookup the (likely)
publisher name and open access URL for each publication from the RCC
training set:

```
./bin/rcc_openaire.py
```

Do this once, commit the results as `dat/rcc_out.json` and then
make edits on that file manually.

NB: this script needs updates!!! remove counters, output dicts


## 3. Aligning publisher names

The names of publishers will be an ongoing hot mess.
While the full name of a publishher may appear on a publication, there
are formal abbreviations used in citations, which we'll use here.
Unfortunatly, these inconsistencies in naming break the `uuid` values
for publications, so we must use a canonical list.

The following script generates a tally of the publisher names used so
far, and helps catch inconsistencies that lead to broken links later:

```
./bin/tally_pubs.py
```


## 4. Stitch

The preconditions for including a publication in the corpus are:

 - linked to 1 or more known datasets
 - has a `title`
 - has a `publisher`
 - has a `url`
 - has a URL for an open access `pdf`

Most all of the publications have titles, at a minimum, although some
of those are incorrect and must be modified.
Earlier stages of scripts lookup `publisher` and `url` properties via 
API, then the `pdf` property is added manually.
Optionally, each publication may have a unique `doi` identifier.

This script serializes a collection of entities (dicts in JSON) to add
as another partition in the `corpus/pub/.json` for each publication
for which all of these preconditions have been met.
Delete entries from `corpus/pub/*.json` to cause them to be regenerated.

```
./bin/stitch.py
```


## 5. Generate a corpus to publish

This final step uses the dataset list plus the following files as
input:

 - `corpus/vocab.json`
 - `corpus/pub/*.json`

Then it generates the `uuid` values (late binding) for publications,
and serializes the new corpus update as both `tmp.ttl` (TTL) and 
`tmp.jsonld` (JSON-LD) formats, which must then be renamed and moved
into the corpus repo manually:

```
./bin/gen_ttl.py
```

