from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
import pickle

from preprocess import FileReader, TreeFeatures

for directory in os.listdir('dataset'):
    # Data path
    path = f'dataset/{directory}/data.txt'

    # Split into train and test data
    data = FileReader(path).load_data()
    train_data, test_data = train_test_split(data, test_size=0.3)

    # Get features
    X_train, y_train = TreeFeatures(train_data).get_features_labels()
    X_test, y_test = TreeFeatures(test_data).get_features_labels()

    # Fit the model
    tree = DecisionTreeClassifier(max_depth=10, random_state=0)
    tree.fit(X_train, y_train)

    # Evaluating
    y_pred = tree.predict(X_test)
    print('Accuracy is %.2f' % (accuracy_score(y_test, y_pred)))

    # Save model
    if not os.path.exists(f'../job_crawl/job_crawl/models/{directory}/'):
        os.makedirs(f'../job_crawl/job_crawl/models/{directory}/')
    with open(f'../job_crawl/job_crawl/models/{directory}/{directory}_dstree.pickle', mode='wb') as f:
        pickle.dump(tree, f)
        f.close()


