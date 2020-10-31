from lxml import etree
from io import StringIO, BytesIO
path = 'dataset/'
file_name = 'dblp.xml'
file_path = path + file_name
count = 1000
include_key = True
all_elements = {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}
all_features = {"author", "cite",
                "journal", "title",
                "year"}
def context_iter(dblp_path):
    """Create a dblp data iterator of (event, element) pairs for processing"""
    return etree.iterparse(source=dblp_path, dtd_validation=True, load_dtd=True)  # required dtd

dblp_path = file_path
for _, elem in context_iter(dblp_path):
    if count > 0:
        count -= 1
    else:
        break
    # print(elem.tag,elem.text)
    if elem.tag in all_elements:
        if include_key:
            attribs = {'key': [elem.attrib['key']]}
        else:
            attribs = {}
        for feature in all_features:
            attribs[feature] = []
        for sub in elem:
            # print(sub.tag,sub.text)
            if sub.tag in all_features:
                # print("features",sub.tag,sub.text)
                if sub.tag=="cite" and sub.text=="...":
                    continue
                attribs[sub.tag] = attribs.get(sub.tag) + [sub.text]
        # print(attribs)
        print(attribs['cite'])
    # print("-------------------")
