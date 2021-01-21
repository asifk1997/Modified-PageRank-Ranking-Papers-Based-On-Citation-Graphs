import numpy as np
import networkx as nx
from lxml import etree
from io import StringIO, BytesIO
from collections import defaultdict

# G = nx.read_edgelist("test_graph.edgelist")
# textline = "1 2 3,2 3 1"
# fh = open("test.edgelist", "w")
# d = fh.write(textline)
# fh.close()
G = nx.read_edgelist("test.edgelist", nodetype=int, data=(("weight", float),))
print(list(G))

print(list(G.edges(data=True)))

def context_iter(dblp_path):
    """Create a dblp data iterator of (event, element) pairs for processing"""
    return etree.iterparse(source=dblp_path, dtd_validation=True, load_dtd=True)  # required dtd


path = 'our_dataset/'
file_name = 'new2.xml'
file_path = path + file_name
dblp_path = file_path
include_key = True
# all_elements = {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}
all_elements = {"article"}
# all_features = {"author", "cite", "journal", "title", "year"}
all_features = {"author", "cite", "journal", "title", "year"}
all_papers = defaultdict(list)
paper_outlinks = defaultdict(list)
paper_inlinks = defaultdict(list)

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
            all_papers[attribs['key'][0]].append(y)
            outlinks = attribs['cite']
            for i in outlinks:
                print(i,end=' ')
                paper_outlinks[attribs['key'][0]].append(i)
                paper_inlinks[i].append(attribs['key'][0])


    print("-------------------")



def page_rank(G, d=0.85, tol=1e-2, max_iter=100):



    print("Hello")
    nodes = G.nodes()
    matrix = nx.adjacency_matrix(G, nodelist=nodes)
    print(matrix)
    out_degree = matrix.sum(axis=0)
    weight = matrix / out_degree
    N = G.number_of_nodes()
    pr = np.ones(N).reshape(N, 1) * 1./N
    print("Hello")
    # need to repeat the initial step twice
    # for matplotlib animation
    # yield nodes, pr, "init"
    # yield nodes, pr, "init"

    for it in range(max_iter):
        old_pr = pr[:]
        pr = d * weight.dot(pr) + (1-d)/N
        yield nodes, pr, it
        err = np.absolute(pr - old_pr).sum()
        if err < tol:
            return pr

def page_rank_2(G,d=0.85, tol=1e-2,max_iter=100):
    print("Hello")
    nodes = G.nodes()
    matrix = nx.adjacency_matrix(G, nodelist=nodes)
    print(matrix)
    out_degree = matrix.sum(axis=0)
    weight = matrix / out_degree
    N = G.number_of_nodes()
    pr = np.ones(N).reshape(N, 1) * 1. / N
    print(pr)
    for it in range(max_iter):
        old_pr = pr[:]
        pr = d * weight.dot(pr) + (1-d)/N
        # yield nodes, pr, it
        err = np.absolute(pr - old_pr).sum()
        if err < tol:
            print(pr)
            return pr
    print("abcd")
    print(pr)

print("Hi")
page_rank(G)
page_rank_2(G)
print("Bye")