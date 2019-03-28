from test_dataset.preprocess.make_dataset import ParserDataset
raw_data_file_name = 'test_dataset/preprocess/raw_data/vieclam24h.json'
attributes_file_name = 'test_dataset/preprocess/attributes.json'
parser = ParserDataset(raw_data_file_name, attributes_file_name)
parser.make_dataset()