from preprocess import FileReader, FeaturesTransformer
from model import DecisionTreeModel, NaiveBayesModel, LogisticRegressionModel
import pickle
import os


for directory in os.listdir('../dataset'):
    with open(f'../models/{directory}/{directory}_nb.pickle', mode='rb') as f:
        nb_model = pickle.load(f)
        f.close()

    with open(f'../models/{directory}/{directory}_logistic.pickle', mode='rb') as f:
        dtree_model = pickle.load(f)
        f.close()

    X, y = FileReader(f'../dataset/{directory}/test.txt').load_data()

    y_pred_nb = nb_model.clf.predict_proba(X)
    y_pred_dtree = dtree_model.clf.predict_proba(X)

    if not os.path.exists(f'meta_learner_data/{directory}'):
        os.makedirs(f'meta_learner_data/{directory}')

    with open(f'meta_learner_data/{directory}/train_nb_logistic.txt', mode='w', encoding='utf8') as f:
        for i in range(len(y)):
            line = f'{X[i]}\t{y_pred_nb[i][1]}\t{y_pred_dtree[i][1]}\t{y[i]}\n'
            f.write(line)

        f.close()

