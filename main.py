import xml.etree.ElementTree as ET
from dblplib import test
path = '/media/asif/Data/study/sem1/algo/project/'
file_name = 'dblp.xml'
file_path = path+file_name

def print_hi(name):
    print(file_path)
    tree = ET.parse(file_path)
    print (tree)
    # getting the parent tag of
    # the xml document
    root = tree.getroot()

    # printing the root (parent) tag
    # of the xml document, along with
    # its memory location
    print(root)

    # printing the attributes of the
    # first tag from the parent
    print(root[0].attrib)

    # printing the text contained within
    # first subtag of the 5th tag from
    # the parent
    print(root[5][0].text)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print_hi('PyCharm')
    tes
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
