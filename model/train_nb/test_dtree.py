from model import DecisionTreeModel
from preprocess import FileReader, FeaturesTransformer
import pickle
from sklearn.metrics import precision_recall_fscore_support
import os


for index, attribute in enumerate(os.listdir('../dataset/')):
    data_file_name = f'../dataset/{attribute}/test.txt'

    # Build feature extraction with available dictionary
    X_test, y_test = FileReader(data_file_name).load_data()

    # Load model
    with open(f'../models/{attribute}/{attribute}_dtree.pickle', mode='rb') as f:
        model = pickle.load(f)
        f.close()

    # Predict
    y_pred = model.clf.predict(X_test)
    # y_prob = model.clf.predict_proba(X_test)

    # Print accuracy result
    if index == 0:
        print('%50s\t%10s\t%10s\t%10s' % ('Attribte', 'precision', 'recall', 'f1-score'))
    precision, recall, fscore, _ = precision_recall_fscore_support(y_test, y_pred, average='micro')

    print('%50s\t%10s\t%10s\t%10s' % (attribute, '%.2f' % (precision * 100), '%.2f' % (recall * 100), '%.2f' % (fscore * 100)))


