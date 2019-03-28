from preprocess import FeatureExtraction, FileReader
import pickle

path = "data.txt"
with open(path, mode='r', encoding='utf8') as f:
    data = f.readlines()
    f.close()

link_text = [item.strip().split('\t')[1] for item in data]
dictionary_dir = 'dictionary/title'

features = FeatureExtraction(data=link_text, dictionary_dir=dictionary_dir, is_contain_labels=False).get_features_labels()

with open('../job_crawl/job_crawl/models1/title/title_model.pickle', mode='rb') as f:
    model = pickle.load(f)
    f.close()

y_pred = model.predict(features)
for i, item in enumerate(y_pred):
    if item == 0:
        print(data[i].strip())


