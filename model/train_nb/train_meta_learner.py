from sklearn.linear_model import LinearRegression


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


