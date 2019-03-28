import json
from .process import parse_attribute, flatten_dict
import os
import re


class ParserDataset:
    def __init__(self, data_file_name, attributes_file_name, destination_dir, max_no_items):
        self.data_file_name = data_file_name
        self.attributes_file_name = attributes_file_name
        self.destination_dir = destination_dir
        self.max_no_items = max_no_items
        self.raw_data = self.__load_raw_data()
        self.attributes = self.__load_attributes()

    def __load_raw_data(self):
        with open(self.data_file_name, mode='r', encoding='utf8') as f:
            raw_data = json.load(f)[:self.max_no_items]
            f.close()
        return raw_data

    def __load_attributes(self):
        with open(self.attributes_file_name, mode='r', encoding='utf8') as f:
            attributes_format = json.load(f)
            f.close()

        return parse_attribute(attributes_format)

    def make_dataset(self):
        save_file_dir = {}
        for attribute in self.attributes:
            if not os.path.exists(f'{self.destination_dir}/dataset/{attribute}/'):
                os.makedirs(f'{self.destination_dir}/dataset/{attribute}/')

            save_file_dir[attribute] = open(f'{self.destination_dir}/dataset/{attribute}/data.txt', mode='a+', encoding='utf8')
        for item in self.raw_data:
            for job_field, job_value in flatten_dict(item).items():
                if job_field not in self.attributes:
                    continue

                if type(job_value) is list:
                    value_to_write = ' '.join([re.sub('\\s', ' ', str(value)) for value in job_value])
                else:
                    value_to_write = re.sub('\\s', ' ', str(job_value))

                for attribute in self.attributes:
                    if str(job_value).strip() != '':
                        if job_field == attribute:
                            save_file_dir[job_field].write(value_to_write + '\t1' + '\n')
                        else:
                            save_file_dir[attribute].write(value_to_write + '\t0' + '\n')

        for folder in save_file_dir.values():
            folder.close()


