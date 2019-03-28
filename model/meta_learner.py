import os
from preprocess import FeatureExtraction, TreeFeatures, FileReader
import pickle


for directory in os.listdir('dataset'):
    data_file_name = f'dataset/{directory}/data1.txt'
    dictionary_dir = f'dictionary/{directory}'

    # Read data
    data = FileReader(data_file_name).load_data()

    # Get features
    X_features_nb, X_labels_nb = FeatureExtraction(data[:50000], dictionary_dir, True).get_features_labels()
    X_features_ds, X_labels_ds = TreeFeatures(data, True).get_features_labels()

    # Load model
    with open(f'../job_crawl/job_crawl/models/{directory}/{directory}_model.pickle', mode='rb') as f:
        model_nb = pickle.load(f)
        f.close()

    with open(f'../job_crawl/job_crawl/models/{directory}/{directory}_dstree.pickle', mode='rb') as f:
        model_ds = pickle.load(f)
        f.close()

    # Predict
    y_prob_nb = [item[0] for item in model_nb.predict_proba(X_features_nb)]
    y_prob_ds = [item[0] for item in model_ds.predict_proba(X_features_ds)]

    # Create dataset1 for meta-learner
    with open(f'dataset/{directory}/meta_learner_data.txt', mode='w', encoding='utf8') as f:
        for i in range(50000):
            f.write('%s\t%f\t%f\t%d\n' % (data[i][0], (y_prob_nb[i]), (y_prob_ds[i]), abs(X_labels_nb[i] - 1)))
        f.close()


