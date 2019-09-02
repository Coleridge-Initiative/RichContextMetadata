# RePEc Author Confirmation

## Files

  * `ds.txt` -- list of datasets included


## Usage

To pull RePEc handles for matching publications from the Dimensions API:

```
./repec.py 1
```

To access metadata (authors, etc.) from the RePEc API:

```
./repec.py 2
```

To generate the data to send to RePEc for author confirmation:

```
./repec.py 3
```


## Specs

For each of the authors among the USDA and Bundesbank publications, for
which we have matched datasets:


Author 1, article title, journal title, year, (whatever other identifying information we have in the metadata that matches the REPEC API fields), dataset name (with all the possible variants that you have identified)

Author 2 ditto
 
...

That set of fields then need to be matched to the same fields from the
REPEC API to the extent necessary to get the right REPEC handle.
 
Then we send him the REPEC handle with the dataset name (with all
possible variants)
