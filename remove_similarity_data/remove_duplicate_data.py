from pyvi import ViTokenizer
import re
from py_stringmatching.similarity_measure.soft_tfidf import SoftTfIdf
from py_stringmatching.similarity_measure.cosine import Cosine
import json
import time
import os


# Split string to tokens
def word_split(text):
    return re.split("[^\w_]+", ViTokenizer.tokenize(text))


# Normalize tokens
def word_nomalize(text):
    return [word.lower() for word in text]


# Build inverted index
def invert_index(str_list):
    inverted = {}
    for i, s in enumerate(str_list):
        for word in s:
            locations = inverted.setdefault(word, [])
            locations.append(i)
    return inverted


def size_filtering(x, Y, JACCARD_MEASURE):
    up_bound = len(x) / JACCARD_MEASURE
    down_bound = len(x) * JACCARD_MEASURE
    return [y for y in Y if down_bound <= len(y) <= up_bound]


def prefix_filtering(inverted_index, x, Y, PREFIX_FILTERING):
    if len(x) >= PREFIX_FILTERING:
        # Sort x, y in Y
        x_ = sort_by_frequency(inverted_index, x)
        Y_ = [sort_by_frequency(inverted_index, y)[:len(y) - PREFIX_FILTERING + 1] for y in Y if
              len(y) >= PREFIX_FILTERING]
        Y_inverted_index = invert_index(Y_)
        Y_filtered_id = []
        for x_j in x_[:len(x) - PREFIX_FILTERING + 1]:
            Y_filtered_id += Y_inverted_index.get(x_j) if Y_inverted_index.get(x_j) is not None else []
        Y_filtered_id = set(Y_filtered_id)
        return [Y[i] for i in Y_filtered_id]
    else:
        return []


def sort_by_frequency(inverted_index, arr):
    return sorted(arr,
                  key=lambda arr_i: len(inverted_index.get(arr_i) if inverted_index.get(arr_i) is not None else []))


with open('job_crawl/data.json', encoding='utf-8-sig') as f1:
    X = json.loads(f1.read())
    f1.close()

with open('job_crawl/careerbuilder.json', encoding='utf-8-sig') as f2:
    Y = json.loads(f2.read())
    f2.close()

# Const
JACCARD_MEASURE = 0.7
PREFIX_FILTERING = 2
SIMILARITY_THRESHOLD = 0.75

# Time start
print(time.strftime("%H:%M:%S", time.localtime()))

# Split
X_title_split = [word_split(x.get('title')) for x in X]
Y_title_split = [word_split(y.get('title')) for y in Y]

# Normalize
X_title_normalize = [word_nomalize(X_title) for X_title in X_title_split]
Y_title_normalize = [word_nomalize(Y_title) for Y_title in Y_title_split]

# Inverted index of Y
Y_inverted_index = invert_index(Y_title_normalize)

# Similarity score with SoftTfIdf
softTfIdf = SoftTfIdf(X_title_normalize + Y_title_normalize)

X_ = []

for x in X_title_normalize:
    Y_size_filtering = size_filtering(x, Y_title_normalize, JACCARD_MEASURE)
    Y_candidates = prefix_filtering(Y_inverted_index, x, Y_size_filtering, PREFIX_FILTERING)
    flag = False
    for y in Y_candidates:
        if softTfIdf.get_raw_score(x, y) > SIMILARITY_THRESHOLD:
            flag = True
            break
    if not flag:
        X_.append(x)

print(len(X_))

# Time end
print(time.strftime("%H:%M:%S", time.localtime()))
