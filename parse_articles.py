from lxml import etree
from datetime import datetime
import csv
import codecs
import ujson
import re

# all of the element types in dblp
all_elements = {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}

all_features = {"address", "author", "booktitle", "cdrom", "chapter", "cite", "crossref", "editor", "ee", "isbn",
                "journal", "month", "note", "number", "pages", "publisher", "school", "series", "title", "url",
                "volume", "year"}

def log_msg(message):
    """Produce a log with current time"""
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)

def context_iter(dblp_path):
    """Create a dblp data iterator of (event, element) pairs for processing"""
    return etree.iterparse(source=dblp_path, dtd_validation=True, load_dtd=True)  # required dtd

def count_pages(pages):
    """Borrowed from: https://github.com/billjh/dblp-iter-parser/blob/master/iter_parser.py
    Parse pages string and count number of pages. There might be multiple pages separated by commas.
    VALID FORMATS:
        51         -> Single number
        23-43      -> Range by two numbers
    NON-DIGITS ARE ALLOWED BUT IGNORED:
        AG83-AG120
        90210H     -> Containing alphabets
        8e:1-8e:4
        11:12-21   -> Containing colons
        P1.35      -> Containing dots
        S2/109     -> Containing slashes
        2-3&4      -> Containing ampersands and more...
    INVALID FORMATS:
        I-XXI      -> Roman numerals are not recognized
        0-         -> Incomplete range
        91A-91A-3  -> More than one dash
        f          -> No digits
    ALGORITHM:
        1) Split the string by comma evaluated each part with (2).
        2) Split the part to subparts by dash. If more than two subparts, evaluate to zero. If have two subparts,
           evaluate by (3). If have one subpart, evaluate by (4).
        3) For both subparts, convert to number by (4). If not successful in either subpart, return zero. Subtract first
           to second, if negative, return zero; else return (second - first + 1) as page count.
        4) Search for number consist of digits. Only take the last one (P17.23 -> 23). Return page count as 1 for (2)
           if find; 0 for (2) if not find. Return the number for (3) if find; -1 for (3) if not find.
    """
    cnt = 0
    for part in re.compile(r",").split(pages):
        subparts = re.compile(r"-").split(part)
        if len(subparts) > 2:
            continue
        else:
            try:
                re_digits = re.compile(r"[\d]+")
                subparts = [int(re_digits.findall(sub)[-1]) for sub in subparts]
            except IndexError:
                continue
            cnt += 1 if len(subparts) == 1 else subparts[1] - subparts[0] + 1
    return "" if cnt == 0 else str(cnt)


def extract_feature(elem, features, include_key=False):
    """Extract the value of each feature"""
    if include_key:
        attribs = {'key': [elem.attrib['key']]}
    else:
        attribs = {}
    for feature in features:
        attribs[feature] = []
    for sub in elem:
        if sub.tag not in features:
            continue
        if sub.tag == 'title':
            text = re.sub("<.*?>", "", etree.tostring(sub).decode('utf-8')) if sub.text is None else sub.text
        elif sub.tag == 'pages':
            if (sub.text ==None):
                pass
                text = None
                # print(attribs['key'])
            else:
                text = count_pages(sub.text)
        else:
            text = sub.text
        if text is not None and len(text) > 0:
            attribs[sub.tag] = attribs.get(sub.tag) + [text]
    return attribs



def clear_element(element):
    """Free up memory for temporary element tree after processing the element"""
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]
cite_dic = {}

def parse_entity(dblp_path, save_path, type_name, features=None, save_to_csv=False, include_key=False):
    global cite_dic
    """Parse specific elements according to the given type name and features"""
    log_msg("PROCESS: Start parsing for {}...".format(str(type_name)))
    i=0
    assert features is not None, "features must be assigned before parsing the dblp dataset"
    results = []
    dic = {}
    attrib_count, full_entity, part_entity = {}, 0, 0
    for _, elem in context_iter(dblp_path):
        if elem.tag in type_name:
            attrib_values = extract_feature(elem, features, include_key)  # extract required features
            results.append(attrib_values)  # add record to results array
            # print(i,attrib_values)
            for key, value in attrib_values.items():
                attrib_count[key] = attrib_count.get(key, 0) + len(value)
            cnt = sum([1 if len(x) > 0 else 0 for x in list(attrib_values.values())])
            if cnt == len(features):
                full_entity += 1
            else:
                part_entity += 1
            i += 1
        elif elem.tag not in all_elements:
            continue
        clear_element(elem)

        if i>2000000:
            # break
            pass
    all_cites=0
    useful_records = []
    useful_dic = {}
    for record in results:
        # print("record",record,"key",record['key'],"cite",record['cite'],'len',len(record['cite']))
        all_cites+=len(record['cite'])
        if len(record['cite'])>0:
            useful_records.append(record)
            useful_dic[record['key'][0]]=record
    countt=0
    print('all_cites', all_cites)
    print('useful_records',len(useful_records),len(useful_dic))
    for record in useful_records:
        cites_in_record = record['cite']
        for cite in cites_in_record:
            for c in useful_dic.keys():
                if cite == c:
                    countt+=1
    print('cites within articles',countt)
    cite_dic = useful_dic
    dfs_helper(useful_dic)
    return full_entity, part_entity, attrib_count
visited = {}
def dfs_helper(useful_dic):
    for u in useful_dic.keys():
        visited[u] = 0
    for u in useful_dic.keys():
        if visited[u]==0:
            record = useful_dic[u]
            cites = record['cite']
            for cite in cites:
                if cite !='...':
                    dfs(cite,0)

maxx = -1
def dfs(cite,n):
    global cite_dic
    global maxx
    global visited
    # print(len(cite_dic),'cite_dic')
    visited[cite]=1
    if n>maxx:
        maxx = n
        print('maxx',maxx)
    if cite != '...':
        try:
            record = cite_dic[cite]
            # print('found')
            cites = record['cites']
            # print(n)
            for cite in cites:
                if visited[cite]==0:
                    dfs(cite,n+1)
        except :
            # print("No cites found in articles")
            pass



def parse_article(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ['article']
    features = ['title', 'author', 'year', 'journal', 'cite']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total articles found: {}, articles contain all features: {}, articles contain part of features: {}'
            .format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))

def main():
    dblp_path = 'dataset/dblp.xml'
    save_path = 'dataset/article.xml'
    try:
        context_iter(dblp_path)
        log_msg("LOG: Successfully loaded \"{}\".".format(dblp_path))
    except IOError:
        log_msg("ERROR: Failed to load file \"{}\". Please check your XML and DTD files.".format(dblp_path))
        exit()
    parse_article(dblp_path,save_path,False,True)

if __name__ == '__main__':
    main()