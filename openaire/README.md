# Notes


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