from lxml import etree


with open('html/index.html', encoding='utf8', mode='r') as f:
    tree = etree.HTML(f.read())
    f.close()


def parse(tree):
    tree = html
