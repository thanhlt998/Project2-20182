from model import NaiveBayesModel
from preprocess import FileReader, FeaturesTransformer
import pickle
from sklearn.metrics import accuracy_score
import os


for attribute in os.listdir('../dataset/'):
    data_file_name = f'../dataset/{attribute}/test.txt'

    # Build feature extraction with available dictionary
    X_test, y_test = FileReader(data_file_name).load_data()

    # Load model
    with open(f'../models/{attribute}/{attribute}_nb.pickle', mode='rb') as f:
        model = pickle.load(f)
        f.close()

    # Predict
    y_pred = model.clf.predict(X_test)
    # y_prob = model.clf.predict_proba(X_test)

    # Print accuracy result
    print(f'Accuracy of {attribute}: %.2f' % (accuracy_score(y_test, y_pred)))

