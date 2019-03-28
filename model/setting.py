def load_stop_words(file_name):
    with open(file_name, mode='r', encoding='utf8') as f:
        stop_words = f.readlines()
        f.close()
    return stop_words


STOP_WORDS_FILE_NAME = 'vietnamese-stopwords/vietnamese-stopwords-dash.txt'
SPECIAL_CHARACTER = '0123456789%@$.,=+-!;/()*"&^:#|\n\t\''
STOP_WORDS = load_stop_words(STOP_WORDS_FILE_NAME)
