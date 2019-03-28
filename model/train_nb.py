from sklearn.naive_bayes import MultinomialNB
from preprocess import FeatureExtraction, FileReader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os


# for directory in os.listdir('dataset1'):
for directory in ['jobLocation_address_addressCountry']:
    # Data path
    path = f'dataset/{directory}/data.txt'

    # Split into train and test data
    data = FileReader(path).load_data()
    train_data, test_data = train_test_split(data, test_size=0.3)

    # Extract features
    X_train, y_train = FeatureExtraction(train_data, f'dictionary/{directory}').get_features_labels()
    X_test, y_test = FeatureExtraction(test_data, f'dictionary/{directory}').get_features_labels()

    # Build model
    model = MultinomialNB()
    model.fit(X_train, y_train)

    # Predict test
    y_pred = model.predict(X_test)
    print(f"Accuracy of {directory} is %.2f" % (accuracy_score(y_test, y_pred) * 100))

    # Save model
    if not os.path.exists(f'../job_crawl/job_crawl/models/{directory}/'):
        os.makedirs(f'../job_crawl/job_crawl/models/{directory}/')
    with open(f'../job_crawl/job_crawl/models/{directory}/{directory}_nb.pickle', mode='wb') as f:
        pickle.dump(model, f)
        f.close()
