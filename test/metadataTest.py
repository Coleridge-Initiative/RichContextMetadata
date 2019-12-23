import unittest
import sys
from glob import glob
from pathlib import Path
import codecs
import csv 
import os 

csv_paths = []
bad_unicodes = ["â€™", "‚Äô", "‚Äò", "‚Äú", "‚Äù", "‚Äì"]

metadata_path = "/../metadata"

class TestSample(unittest.TestCase):

    def test_contains_unicode(self):
        badlyEncodedFiles = {}
        for csvpath in csv_paths:
            try: 
                with codecs.open(csvpath, encoding="utf-8") as f:
                    csv_reader = csv.reader(f, delimiter=",")

                    for row in csv_reader:
                        for badUnicode in bad_unicodes: 
                            if any(badUnicode in field for field in row):
                                path, filename = os.path.split(csvpath)
                                badlyEncodedFiles.setdefault(filename,set()).add(badUnicode)
            except: 
                print("Issue opening: " + csvpath)   
        
        for key in badlyEncodedFiles:
            print(key, badlyEncodedFiles[key])

        self.assertTrue(len(badlyEncodedFiles) == 0), "Files are not properly encoded"

if __name__ == '__main__':

    if len(sys.argv) > 1:
        csv_paths.append(sys.argv.pop())
    else:
        csv_wild_path = "/*/*.csv"
        dir_path = os.path.dirname(__file__)
        print(__file__)
        print(dir_path + metadata_path + csv_wild_path)
        for csvpath in glob(dir_path + metadata_path + csv_wild_path):
            csv_paths.append(csvpath)

    print("Files to check: {}".format(len(csv_paths)))
    unittest.main()