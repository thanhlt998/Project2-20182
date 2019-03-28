from pyvi import ViTokenizer
from setting import SPECIAL_CHARACTER, STOP_WORDS
from gensim import corpora, matutils
import numpy as np
import re
import os
import re


class FileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self, is_contain_labels=True):
        with open(self.file_path, mode='r', encoding='utf8') as f:
            data = f.readlines()
            f.close()
        if is_contain_labels:
            result = [tuple(statement.split('\t')) for statement in data]
        else:
            result = data
        return result

    def load_dictionary(self):
        return corpora.Dictionary.load_from_text(self.file_path)


class FeatureExtraction:
    def __init__(self, data, dictionary_dir, is_contain_labels=True):
        self.data = []
        self.is_contain_labels = is_contain_labels

        if is_contain_labels:
            self.labels = []
            for line in data:
                self.data.append(self.__normalize(line[0]))
                self.labels.append(int(line[1].strip()))
        else:
            for line in data:
                self.data.append(self.__normalize(line))
        self.dictionary_dir = dictionary_dir

    @staticmethod
    def __tokenize(text):
        return [word.strip().lower() for word in re.sub('[^\\w|\\s]', '', ViTokenizer.tokenize(text)).split() if
                word not in SPECIAL_CHARACTER]

    @staticmethod
    def __remove_stop_words(text):
        return [word for word in text if text not in STOP_WORDS]

    def __normalize(self, text):
        return self.__remove_stop_words(self.__tokenize(text))

    def __build_dictionary(self):
        self.dictionary = corpora.Dictionary(self.data)
        self.dictionary.filter_extremes(no_below=10, no_above=0.3)
        if not os.path.exists(f'{self.dictionary_dir}/'):
            os.makedirs(f'{self.dictionary_dir}/')
        self.dictionary.save_as_text(f'{self.dictionary_dir}/dictionary.txt')

    def __load_dictionary(self):
        if not os.path.exists(f'{self.dictionary_dir}/dictionary.txt'):
            self.__build_dictionary()
        self.dictionary = FileReader(f'{self.dictionary_dir}/dictionary.txt').load_dictionary()

    def get_bow(self, text):
        self.__load_dictionary()
        vector = self.dictionary.doc2bow(text)
        return list(np.column_stack(matutils.sparse2full(doc, len(self.dictionary)) for doc in [vector]).T[0])

    def get_features_labels(self):
        if self.is_contain_labels:
            return [self.get_bow(text) for text in self.data], self.labels
        else:
            return [self.get_bow(text) for text in self.data]


class TreeFeatures:
    def __init__(self, data, is_contain_labels=True):
        self.is_contain_labels = is_contain_labels
        self.data = []

        if is_contain_labels:
            self.labels = []
            for item in data:
                self.data.append(item[0])
                self.labels.append(item[1])
        else:
            for item in data:
                self.data.append(item)

    @staticmethod
    def is_contain_all_digits(text):
        return 1 if re.match('^\d+$', text) is not None else 0

    @staticmethod
    def is_date(text):
        pattern = "^\\d{4}[\\/-]\\d{2}[\\/-]\\d{2}([ T]\\d{2}:\\d{2}:\\d{2}([+-]\\d{2}:\\d{2})?)?$"
        return 1 if re.match(pattern, text) is not None else 0

    @staticmethod
    def is_upper(text):
        return 1 if text.isupper() else 0

    def get_features_labels(self):
        if self.is_contain_labels:
            return [
                [self.is_contain_all_digits(text),
                 self.is_date(text),
                 self.is_upper(text),
                 len(text)/500
                 ]
                for text in self.data
            ], self.labels
        else:
            return [
                [self.is_contain_all_digits(text),
                 self.is_date(text),
                 self.is_upper(text),
                 len(text) / 500
                 ]
                for text in self.data
            ]

