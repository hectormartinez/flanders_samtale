import argparse
import xml.etree.ElementTree as ET
from collections import defaultdict



def read_enriched_taxonomy_from_xml(infile):
    T = defaultdict(list)
    tree = ET.parse('country_data.xml')
    tax = tree.getroot()
    #TODO iterate and retrieve T

    return T

def read_codetable_from_tabseparated(infile):
    return {}



def main():
    parser = argparse.ArgumentParser(description="""Tagger+Parser""")
    parser.add_argument("--taxonomies", nargs='+')
    parser.add_argument("--codetable", help="")
    args = parser.parse_args()

    #TODO read taxonomies and aggregate them
    #TODO read codetable
    #TODO print out expanded

if __name__=="__main__":
    main()

