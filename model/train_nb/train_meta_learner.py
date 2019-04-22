from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import os
import json


def load_data(fn):
    with open(fn, mode='r', encoding='utf8') as f:
        lines = f.readlines()
        f.close()

    X = []
    y = []

    for line in lines:
        line = line.strip().split('\t')
        X.append([float(line[1]), float(line[2])])
        y.append(int(line[-1]))

    return X, y


folder = 'meta_learner_data'
weight = {}
for directory in os.listdir(folder):
    data_file_name = f'{folder}/{directory}/train_nb_logistic.txt'
    X, y = load_data(data_file_name)

    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    model = LinearRegression()
    model.fit(X, y)

    print(f"Weights of {directory} ", model.coef_)
    weight[directory] = list(model.coef_)

with open('weight_nb_logistic.json', mode='w', encoding='utf8') as f:
    json.dump(weight, f)
    f.close()
