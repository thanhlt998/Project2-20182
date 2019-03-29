from model import DecisionTreeModel
from preprocess import FileReader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import time
import os
import pickle


def main():
    folder = '../dataset'
    for directory in os.listdir(folder):
        print(time.asctime())
        data_fn = f'{folder}/{directory}/data.txt'
        X, y = FileReader(data_fn).load_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

        # Fit model
        model = NaiveBayesModel()
        model.clf.fit(X_train, y_train)

        # Test
        y_pred = model.clf.predict(X_test)
        print("Accuracy of title is %.2f %%" % (accuracy_score(y_test, y_pred) * 100))

        # Saving model
        # with open(f'models/{directory}/{directory}_nb.pickle', mode='wb') as f:
        #     pickle.dump(model, f)
        #     f.close()

        print(time.asctime())


if __name__ == '__main__':
    main()
