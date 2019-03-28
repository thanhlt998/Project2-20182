from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np


def load_data(file_name):
    with open(file_name, mode='r', encoding='utf8') as f:
        lines = f.readlines()
        f.close()

    X = []
    y = []

    for line in lines:
        s = line.strip().split('\t')
        X.append([float(s[1]), float(s[2])])
        y.append(int(s[3]))

    return X, y


# split train and test data
X, y = load_data('dataset/title/meta_learner_data.txt')
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4)

# fit regression model
model = LinearRegression()
model.fit(X_train, y_train)

print(model.intercept_)
print(model.coef_)

res = np.concatenate(([model.predict(X_test)], [y_test])).T
print(res)
np.savetxt('result.txt', res, delimiter=',')


