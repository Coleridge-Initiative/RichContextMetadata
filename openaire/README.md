# Generating a public corpus for the leaderboard competition


## 1. Managing the dataset metadata

Datasets are one of the "givens" in this system: they represent the
known _labels_ (aka "classes") in the ground truth for this corpus.
In contrast, the set of publications gets expanded later in our
workflow, but the set of known datasets does not.

We consider dataset names to be known and invariant -- 
nonetheless, edits may be required.


## 2. Importing linked data from the first RCC competition

The following script runs the OpenAIRE API to lookup the (likely)
publisher name and open access URL for each publication from the
corpus used in the first RCC competition:

```
./bin/rcc_openaire.py
```

NB: this script needs updates!!! remove counters, output dicts

Do this step once, committing the results as `dat/rcc_out.json` and
then making edits on that file manually based on use of the scripts
descibed below.


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


## 4. Stitch: identify manual work to be performed

The preconditions for including a publication in the corpus are:

 - linked to 1 or more known datasets
 - has a `title`
 - has a `publisher`
 - has a `url`
 - has a URL for an open access `pdf`

Most all of the publications have titles, at a minimum, although some
of those are incorrect and must be modified. Earlier stages of
scripts lookup `publisher` and `url` properties via API, then the
`pdf` property is added manually. Optionally, each publication may
have a unique `doi` identifier.

This script has two output modes:

  * JSON to use for publications
  * a "todo" list of lookups/edits required for next steps

In the first mode, it serializes a collection of entities (dicts in
JSON about metadata per publication) to be added as another partition
in the `corpus/pub/.json` directory. These only get generated when
all of these preconditions listed above have been met for a given
publication.

```
./bin/stitch.py
```

Sometimes no open access PDF will be available for a publication.
For those cases, set the property `"pdf": null` and move them into 
the file `corpus/rejects.json` for managing dead ends, i.e., to 
avoid this script getting stuck.

In the second mode, this script generates a list of items to be looked
up, which will be manual work. Then edit the `dat/rcc_out.json` with
those changes and run the script again so it will shift into the first
mode.

Iterate on this step to generate more entries for the corpus. Again,
most of this will require manual work, although the script helps
identify the next set of entries that require the least changes to
be usable. The scripts described in the next section may help 
automate lookups in some common cases.


## 5. Parse metadata from known sites

Some sites, such as _Europe PMC_, use consistent formats for metadata
embedded in HTML. So we can parse the HTML from a publication's web
page to extract needed properties:

```
./bin/stitch.py > todo
./bin/europmc.py todo
```


## 6. Generate a corpus to publish

This final step uses the dataset list plus the following files as
input:

 - `corpus/vocab.json`
 - `corpus/pub/*.json`

For the partitioned files within the `corpus/pub` directory, we expect
the following format:

```
    {
        "doi": "10.1000/XYZ.0123456789",
        "publisher": "J Egreg Mansplain",
        "title": "Market share dominance among Samoan-owned coconut tree services in Oahu",
        "url": "https://example.com/article/5150",
        "pdf": "https://example.com/article/5150?render=pdf",
        "datasets": [
            "dataset-000",
            "dataset-123"
        ]
    },

```

Then the following script generates `uuid` values (late binding) for
both publications and datasets, serializing the full output as TTL in
`tmp.ttl` and as JSON-LD in `tmp.jsonld` for a corpus update:

```
./bin/gen_ttl.py
```

Then move and commit these manually into the corpus repo as a
new release: https://github.com/Coleridge-Initiative/rclc
