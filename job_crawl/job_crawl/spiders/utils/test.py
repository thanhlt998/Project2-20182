from detect_schema import JobSchemaDetection
from model import DecisionTreeModel, NaiveBayesModel
from preprocess import FeaturesTransformer
import json

with open('test_job.json', mode='r', encoding='utf') as f:
    jobs = json.load(f)
    f.close()

schema = JobSchemaDetection(jobs, '../models', 'attributes.json', 'weight.json').get_mapping_schema()
print(schema)

