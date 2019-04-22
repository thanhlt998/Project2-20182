from lxml import etree
import pickle
from model import *


with open('../html/test_vietnamworks.html', mode='r', encoding='utf8') as f:
    tree = etree.HTML(f.read())
    f.close()

with open('occupationalCategory_nb1.pickle', mode='rb') as f:
    model_nb = pickle.load(f)
    f.close()

# with open('occupationalCategory_dtree.pickle', mode='rb') as f:
#     model_dtree = pickle.load(f)
#     f.close()

occupational_nodes = []
for node in tree.xpath('//a[text()]'):
    if node.text is not None:
        if model_nb.clf.predict_proba([node.text.strip()])[0][1] > 0.2:
            print(node.getroottree().getpath(node), node.text.strip())

print(model_nb.clf.predict_proba(['Hàng không/Du lịch'])[0][1])
