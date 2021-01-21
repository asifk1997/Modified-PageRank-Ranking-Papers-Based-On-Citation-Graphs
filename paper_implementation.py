from lxml import etree
from io import StringIO, BytesIO
from collections import defaultdict

path = 'dataset/'
file_name = 'dblp.xml'
file_path = path + file_name

include_key = True
# all_elements = {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}
all_elements = {"article"}
# all_features = {"author", "cite", "journal", "title", "year"}
all_features = {"author", "cite", "journal", "title", "year"}

paper_outlinks = defaultdict(list)
paper_inlinks = defaultdict(list)
print_top = 10

def context_iter(dblp_path):
    """Create a dblp data iterator of (event, element) pairs for processing"""
    return etree.iterparse(source=dblp_path, dtd_validation=True, load_dtd=True)  # required dtd


all_papers = defaultdict(list)
dblp_path = file_path


def iterate_each_node(max_limit=300000):
    z = 0
    for _, elem in context_iter(dblp_path):
        if elem.tag in all_elements:
            if "dblpnote" in elem.attrib['key'] or "journals/jbi" in elem.attrib['key']:
                continue
            if include_key:
                attribs = {'key': [elem.attrib['key']]}
            else:
                attribs = {}
            for feature in all_features:
                attribs[feature] = []
            for sub in elem:
                # print(sub.tag,sub.text)
                if sub.tag in all_features:
                    if sub.tag == 'cite' and sub.text == '...':
                        pass
                    else:
                        attribs[sub.tag] = attribs.get(sub.tag) + [sub.text]
            attribs['paper-rank'] = 1.0
            # print(attribs)
            y = attribs
            # print(attribs['key'][0])
            # print(y)
            all_papers[attribs['key'][0]].append(y)
            outlinks = attribs['cite']
            for i in outlinks:
                # print(i, end=' ')
                paper_outlinks[attribs['key'][0]].append(i)
                paper_inlinks[i].append(attribs['key'][0])
            if z > max_limit:
                break
            z += 1
            # print(z)
        # clear_element(elem)

    print("-------------------")


theta = 0.85


def myfunc():
    pass


def iterative_pagerank_time_dependent():
    updated_page_rank = {}
    max_score = 0
    # print(paper_inlinks)
    while True:
        flag = True
        for k in all_papers:

            paper = all_papers[k]
            # print(paper)
            current_score = paper[0]['paper-rank']
            if k in paper_inlinks:
                inlinks_list = paper_inlinks[k]
                new_score = 0
                for i in inlinks_list:
                    if i in all_papers:
                        paper_i = all_papers[i]
                        new_score += paper_i[0]['paper-rank'] / len(paper_outlinks[i])
                new_score = (1 - theta) + theta * new_score
                # print(new_score)
                if current_score != new_score:
                    flag = False
                updated_page_rank[k] = new_score
        if flag == True:
            break
        max_score = 0
        for key in updated_page_rank:
            all_papers[key][0]['paper-rank'] = updated_page_rank[key]
            max_score = max(max_score, updated_page_rank[key])
            # print(updated_page_rank[key])
        updated_page_rank.clear()
    print('max_score', max_score)

    for paper in all_papers:
        if max_score!=0:
            all_papers[paper][0]['paper-rank'] /= max_score
        # print(all_papers[paper])
    # print(all_papers)

    sorted_papers = sorted(all_papers.items(), key=lambda x: x[1][0]['paper-rank'],
                           reverse=True)  # Sort Papers based on scores
    # print("-" * 200)
    # print("Papers in sorted order by ranks")
    cnt=0
    for i in sorted_papers:
        print(i)
        if cnt>=print_top:
            break
        cnt+=1

    print("-" * 200)


year_citation_count = {}
year_paper_count = {}
average_year_citation_count = {}


def iterative_pagerank_time_independent():
    for k in all_papers:
        year = all_papers[k][0]['year'][0]
        # print(year)
        if year not in year_citation_count.keys():
            year_citation_count[year] = len(paper_outlinks[k])
            year_paper_count[year] = 1
        else:
            curr_value = year_citation_count[year]
            updated_value = curr_value + len(paper_outlinks[k])
            year_citation_count.update({year: updated_value})
            year_paper_count.update({year: year_paper_count[year] + 1})
    # print('ypc', year_paper_count)
    # print('ycc', year_citation_count)
    for ycc in year_citation_count:
        average_year_citation_count[ycc] = year_citation_count[ycc] / year_paper_count[ycc]
    # print('aycc', average_year_citation_count)
    # print(year_citation_count, year_paper_count)
    updated_page_rank = {}
    max_score = 0
    while True:
        flag = True
        for k in all_papers:
            paper = all_papers[k]
            current_score = paper[0]['paper-rank']
            if k in paper_inlinks:
                inlinks_list = paper_inlinks[k]
                new_score = 0
                for i in inlinks_list:
                    if i in all_papers:
                        paper_i = all_papers[i]
                        new_score += paper_i[0]['paper-rank'] / len(paper_outlinks[i])
                year = (paper[0]['year'][0])
                # print('year0', year)
                # print(average_year_citation_count[year])
                if average_year_citation_count[year] != 0:
                    new_score = (1 - theta) + theta * new_score / average_year_citation_count[year]
                else:
                    new_score = (1 - theta) + theta * new_score
                if current_score != new_score:
                    flag = False
                updated_page_rank[k] = new_score
        if flag == True:
            break
        max_score = 0
        for key in updated_page_rank:
            all_papers[key][0]['paper-rank'] = updated_page_rank[key]
            max_score = max(max_score, updated_page_rank[key])
        updated_page_rank.clear()
    # print('max_score', max_score)

    for paper in all_papers:
        if max_score!=0:
            all_papers[paper][0]['paper-rank'] /= max_score
        # print(all_papers[paper])
    print("-" * 200)

    sorted_papers = sorted(all_papers.items(), key=lambda x: x[1][0]['paper-rank'],
                           reverse=True)  # Sort Papers based on scores
    print("-" * 200)
    print("Papers in sorted order by ranks")
    cnt=1
    for i in sorted_papers:
        if cnt >= print_top:
            break
        cnt += 1
        print(i)

        pass
    print("-" * 200)


conference = defaultdict(list)
conference_scores = {}


def ranking_journals():
    """Conference Score CS = Σ(Paper Score PS)/( Number of Papers published in the Conference NPC[C])"""
    for k in all_papers:
        # print(k)
        # print(all_papers[k])
        try :
            conference_t = all_papers[k][0]['journal'][0]
            paper_score = all_papers[k][0]['paper-rank']
            if conference_t not in conference:
                conference[conference_t] = {'score': paper_score, 'papers_count': 1}
            else:
                current_conference = conference[conference_t]
                current_conference['score'] += paper_score
                current_conference['papers_count'] += 1
                conference[conference_t] = current_conference
        except Exception as e:
            print(e)
            print(k)
            return

    for k in conference:
        conference_scores[k] = conference[k]['score'] / conference[k]['papers_count']
    # print(conference)
    # print(conference_scores)
    soretd_journals = sorted(conference_scores.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    # print(soretd_journals)
    print("-" * 200)
    print("Print journals ranked")
    cnt = 1
    for i in soretd_journals:
        if cnt >= print_top:
            break
        cnt+=1
        print(i)
        pass
    print("-" * 200)


conference_scores_total_yearly = {}
conference_scores_yearly = {}


def ranking_journals_yearly():
    """Conference Yearwise Score CYS = Σ(Paper Score PS)/( Number of Papers published in the Conference in a given year NPCY[C][Y])"""
    for k in all_papers:
        conference_t = all_papers[k][0]['journal'][0]
        year_t = all_papers[k][0]['year'][0]
        paper_score = all_papers[k][0]['paper-rank']
        key = conference_t + ' - ' + year_t
        if key not in conference_scores_total_yearly.keys():
            conference_scores_total_yearly[key] = {'paper-score': paper_score, 'count-of-papers': 1}
            conference_scores_yearly[key] = paper_score
        else:
            updated_paper_score = conference_scores_total_yearly[key]['paper-score'] + paper_score
            count_of_papers = conference_scores_total_yearly[key]['count-of-papers'] + 1
            conference_scores_total_yearly[key] = {'paper-score': updated_paper_score,
                                                   'count-of-papers': count_of_papers}
            conference_scores_yearly[key] = updated_paper_score / count_of_papers
    # print(conference_scores_total_yearly)
    # print(conference_scores_yearly)
    sorted_conference_scores_yearly = sorted(conference_scores_yearly.items(), key=lambda kv: (kv[1], kv[0]),
                                             reverse=True)
    print("-" * 200)
    print("Print yearly conferences ranked")
    cnt = 0
    for i in sorted_conference_scores_yearly:
        pass
        if cnt > print_top:
            break
        cnt+=1
        print(i)
    print("-" * 200)


authors_score_total = {}
authors_score = {}


def ranking_authors():
    """Author Score = Σ(Paper Score PS * Conference Score CS)/(Number of Papers published by the Author NPA[A])"""
    for k in all_papers:
        authors = all_papers[k][0]['author']
        paper_score = all_papers[k][0]['paper-rank']
        conf = all_papers[k][0]['journal'][0]
        conf_score = conference_scores[conf]
        for author in authors:
            if author not in authors_score_total.keys():
                authors_score_total[author] = {'paper-x-conference-score': paper_score * conf_score,
                                               'count-of-papers': 1}
            else:
                authors_score_total[author]['paper-x-conference-score'] += paper_score * conf_score
                authors_score_total[author]['count-of-papers'] += 1
    for k in authors_score_total:
        authors_score[k] = authors_score_total[k]['paper-x-conference-score'] / authors_score_total[k][
            'count-of-papers']
        # print(k, authors_score[k])

    sorted_author_score = sorted(authors_score.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    print("-" * 200)
    print("Author Ranked")
    cnt = 0
    for i in sorted_author_score:
        pass
        if cnt > print_top:
            break
        cnt += 1
        print(i)
    print("-" * 200)


def clear_element(element):
    """Free up memory for temporary element tree after processing the element"""
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]


iterate_each_node()
iterative_pagerank_time_dependent()
# iterative_pagerank_time_independent()
ranking_journals()
ranking_journals_yearly()
ranking_authors()
