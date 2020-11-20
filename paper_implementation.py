from lxml import etree
from io import StringIO, BytesIO
from collections import defaultdict

path = 'dataset/'
file_name = 'new2.xml'
file_path = path + file_name

include_key = True
all_elements = {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}
all_features = {"author", "cite", "journal", "title", "year"}

paper_outlinks = defaultdict(list)
paper_inlinks = defaultdict(list)


def context_iter(dblp_path):
    """Create a dblp data iterator of (event, element) pairs for processing"""
    return etree.iterparse(source=dblp_path, dtd_validation=True, load_dtd=True)  # required dtd


all_nodes = defaultdict(list)
dblp_path = file_path


def iterate_each_node():
    for _, elem in context_iter(dblp_path):
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
                    attribs[sub.tag] = attribs.get(sub.tag) + [sub.text]
            attribs['paper-rank'] = 1.0
            # print(attribs)
            y = attribs
            # print(attribs['key'][0])
            all_nodes[attribs['key'][0]].append(y)
            outlinks = attribs['cite']
            for i in outlinks:
                # print(i,end=' ')
                paper_outlinks[attribs['key'][0]].append(i)
                paper_inlinks[i].append(attribs['key'][0])

    print("-------------------")


theta = 0.85


def iterative_pagerank_time_dependent():
    updated_page_rank = {}
    max_score = 0
    while True:
        flag = True
        for k in all_nodes:
            paper = all_nodes[k]
            current_score = paper[0]['paper-rank']
            if k in paper_inlinks:
                inlinks_list = paper_inlinks[k]
                new_score = 0
                for i in inlinks_list:
                    if i in all_nodes:
                        paper_i = all_nodes[i]
                        new_score += paper_i[0]['paper-rank'] / len(paper_outlinks[i])
                new_score = (1 - theta) + theta * new_score
                if current_score != new_score:
                    flag = False
                updated_page_rank[k] = new_score
        if flag == True:
            break
        max_score = 0
        for key in updated_page_rank:
            all_nodes[key][0]['paper-rank'] = updated_page_rank[key]
            max_score = max(max_score, updated_page_rank[key])
        updated_page_rank.clear()
    # print('max_score', max_score)

    for paper in all_nodes:
        all_nodes[paper][0]['paper-rank'] /= max_score
        print(all_nodes[paper])


year_citation_count = {}
year_paper_count = {}
average_year_citation_count = {}


def iterative_pagerank_time_independent():
    for k in all_nodes:
        year = all_nodes[k][0]['year'][0]
        print(year)
        if year not in year_citation_count.keys():
            year_citation_count[year] = len(paper_outlinks[k])
            year_paper_count[year] = 1
        else:
            curr_value = year_citation_count[year]
            updated_value = curr_value + len(paper_outlinks[k])
            year_citation_count.update({year: updated_value})
            year_paper_count.update({year: year_paper_count[year] + 1})

    for ycc in year_citation_count:
        average_year_citation_count[ycc] = year_citation_count[ycc] / year_paper_count[ycc]
    print(average_year_citation_count)
    print(year_citation_count, year_paper_count)
    updated_page_rank = {}
    max_score = 0
    while True:
        flag = True
        for k in all_nodes:
            paper = all_nodes[k]
            current_score = paper[0]['paper-rank']
            if k in paper_inlinks:
                inlinks_list = paper_inlinks[k]
                new_score = 0
                for i in inlinks_list:
                    if i in all_nodes:
                        paper_i = all_nodes[i]
                        new_score += paper_i[0]['paper-rank'] / len(paper_outlinks[i])
                year = (paper[0]['year'][0])
                print('year0', year)
                new_score = (1 - theta) + theta * new_score / average_year_citation_count[year]
                if current_score != new_score:
                    flag = False
                updated_page_rank[k] = new_score
        if flag == True:
            break
        max_score = 0
        for key in updated_page_rank:
            all_nodes[key][0]['paper-rank'] = updated_page_rank[key]
            max_score = max(max_score, updated_page_rank[key])
        updated_page_rank.clear()
    # print('max_score', max_score)

    for paper in all_nodes:
        all_nodes[paper][0]['paper-rank'] /= max_score
        print(all_nodes[paper])


"""Conference Score CS = Σ(Paper Score PS)/( Number of Papers published in the Conference NPC[C])"""

conference = defaultdict(list)


def ranking_journals():
    conference_score_unit = {'score': 0, 'papers': 0}
    for k in all_nodes:
        conference_t = all_nodes[k][0]['journal'][0]
        print(conference_t)
        paper_score = all_nodes[k][0]['paper-rank']
        if conference_t not in conference:
            conference[conference_t] = {'score': 0, 'papers_count': 0}
        else:
            current_conference = conference[conference_t]
            print(current_conference['score'])
            current_conference.update({'score', current_conference['score'] + paper_score})
            current_conference.update({'papers_count', current_conference['papers_count'] + 1})
    print(conference)


iterate_each_node()
iterative_pagerank_time_dependent()
iterative_pagerank_time_independent()
ranking_journals()
