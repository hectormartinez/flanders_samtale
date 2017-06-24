import argparse
import xml.etree.ElementTree as ET
from collections import defaultdict
import editdistance #https://pypi.python.org/pypi/editdistance
from collections import Counter


def similarity(a,b):
    denominator = len(a)
    if len(b) > len(a):
        denominator = len(b)
    return 1 - (editdistance.eval(a,b) / denominator)


def invertT(T):
    iT = defaultdict(set)
    for descriptor in T.keys():
        for code in T[descriptor]:
            iT[code].add(descriptor)
    return iT


def output_enriched_taxonomy(code2stringattractor,enriched_synonyms_for_attractor,bare_codetable):
    for code,codeid in bare_codetable.items():
        print(codeid+"\t"+code)
        if code in code2stringattractor:
            attractor = code2stringattractor[code]
            print("-\t"+attractor)
            if attractor in enriched_synonyms_for_attractor:
                for synonym in enriched_synonyms_for_attractor[attractor]:
                    print("-\t" + synonym)


def read_enriched_taxonomy_from_xml(infile,T,):
    tree = ET.parse(infile)
    #We retrieve the second child from
    coderecord_list = tree.getroot().find("CodeRecordList")
    #TODO iterate and retrieve T
    for coderecord in coderecord_list:
        #NB, Coderecords have different fields depending on client
        codeID = coderecord.find("CodeID").text
        synonyms = []
        for instance in coderecord.find("InstanceList"):
            synonyms.append(instance.find("InstanceDescription").text.lower())
        for s in synonyms:
            T[s].add(codeID)
        T[coderecord.find("CodeDescription").text.lower()].add(codeID)




def read_enriched_taxonomy_from_tabseparated(infile,T):
    current_codeid = ""
    for line in open(infile).readlines():
        codeid,description = line.strip().split("\t")
        if current_codeid != "_":
            current_codeid = codeid
        T[description.lower()].add(current_codeid)


def read_bare_codetable_from_tapseparated(infile):
    codetable = dict()
    for line in open(infile).readlines():
        codeid,description = line.strip().split("\t")
        codetable[description]=codeid #No append here, I am assuming code-codeID relation is unique
    return codetable

def assign_descriptors_to_attractors(string_attractors,T,ignore_codeids=set(["OVERIG"]),min_attraction=0.5):
    enriched_synonyms_for_attractor = defaultdict(set)
    #First assign by shared codes
    unassigned_descriptors =  set(T.keys()).difference(set(string_attractors.keys()))

    assigned_descriptors = set()
    for descriptor in unassigned_descriptors:
        if ignore_codeids.intersection(set(T[descriptor])):
            pass #ignore the OVERIG type, which is a rummage box
        else:
            common_codes_scoring = Counter({k:len(set(T[descriptor].intersection(set(T[k])))) for k  in string_attractors.keys() })
            string_sim_scoring = Counter({k:similarity(k,descriptor) for k  in string_attractors.keys() })
            total_score = common_codes_scoring  + string_sim_scoring
            best_attractor,attractor_score = total_score.most_common()[0]
            if attractor_score < min_attraction:
                pass #do not assign
            else:
                enriched_synonyms_for_attractor[best_attractor].add(descriptor)
                assigned_descriptors.add(descriptor)
    return enriched_synonyms_for_attractor,assigned_descriptors


    #print("_______")
    #for attractor in string_attractors:
    #    print(attractor,T[attractor])




def main():
    parser = argparse.ArgumentParser(description="""Textkernel coding exercise""")
    parser.add_argument("--xml_codetables", nargs='+',default=["all.jobtitle_enriched.xml","manpower_experience_enriched.xml"])
    #parser.add_argument("--tabsep_codetables",  nargs='+', default=["experience.normalized4"])
    parser.add_argument("--tabsep_codetables",  nargs='+', default=[])
    parser.add_argument("--bare_codetable", default="experience.normalized4.barecodetable")

    args = parser.parse_args()


    """This is an implementation of the suggested algorithm in the exercise handout"""

    # Build sparse T, size M x N, where M is the size of the synonym list and N is the number of taxonomies
    # Use a defaultdict for the sparse matrix
    T = defaultdict(set)
    inverseT = defaultdict(set)

    # Add all synonyms from all taxonomies in xml files
    for infile in args.xml_codetables:
        read_enriched_taxonomy_from_xml(infile,T)

    # Add all synonyms from all taxonomies in tab separated files
    for infile in args.tabsep_codetables:
        read_enriched_taxonomy_from_tabseparated(infile,T)

    # Read input bare codetable
    bare_codetable = read_bare_codetable_from_tapseparated(args.bare_codetable)

    string_attractor2code = dict()
    code2stringattractor = dict()

    for code_description_d  in bare_codetable.keys():
        levenshtein_similarity_ranker = Counter()
        for synonym_candidate in T.keys():
            levenshtein_similarity_ranker[synonym_candidate] = similarity(code_description_d.lower(),synonym_candidate)
        string_attractor = levenshtein_similarity_ranker.most_common()[0][0]
        string_attractor2code[string_attractor] = code_description_d.lower()
        code2stringattractor[code_description_d] = string_attractor

    enriched_synonyms_for_attractor, assigned_descriptors = assign_descriptors_to_attractors(string_attractor2code,T)
    output_enriched_taxonomy(code2stringattractor, enriched_synonyms_for_attractor,bare_codetable)


if __name__=="__main__":
    main()

