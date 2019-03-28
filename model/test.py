from preprocess import FeatureExtraction, FileReader
import pickle
from sklearn.metrics import accuracy_score
import os

# for attribute in os.listdir('dataset1/'):
for attribute in ['title']:
    data_file_name = f'dataset/{attribute}/data1.txt'
    dict_dir = f'dictionary/{attribute}'

    # Read data
    data = FileReader(data_file_name).load_data()

    # Build feature extraction with available dictionary
    X_test, y_test = FeatureExtraction(data[:10], dict_dir).get_features_labels()

    # Load model
    with open(f'../job_crawl/job_crawl/models/{attribute}/{attribute}_model.pickle', mode='rb') as f:
        model = pickle.load(f)
        f.close()

    # Predict
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    print(data[:10])
    print(y_test)
    print(y_pred)
    print(y_prob)

    # Print accuracy result
    print(f'Accuracy of {attribute}: %.2f' % (accuracy_score(y_test, y_pred)))

