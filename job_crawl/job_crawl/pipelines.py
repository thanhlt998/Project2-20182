# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from job_crawl.items import JobItem
import time

class JobCrawlPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):

    collection_name = 'job_information'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
<<<<<<< HEAD
        self.no_items_added = 0
=======
        # self.jobs_to_add = []
>>>>>>> f38684dd49bf46158a1ee1bc4f10185034cc3b32

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.start_time = time.localtime()
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        # self.db[self.collection_name].insert_many(self.jobs_to_add)
        self.client.close()
        print("Begin time: ", time.strftime("%H:%M:%S", self.start_time))
        print("End time: ", time.strftime("%H:%M:%S", time.localtime()))
<<<<<<< HEAD
        print("Added ", self.no_items_added, 'items')
=======
>>>>>>> f38684dd49bf46158a1ee1bc4f10185034cc3b32

    def process_item(self, item, spider):
        # if isinstance(item, JobItem):
        #     self.jobs_to_add.append(item)
        # if len(self.jobs_to_add) >= 2000:
        #     self.db[self.collection_name].insert_many(self.jobs_to_add)
        #     self.jobs_to_add.clear()
        if isinstance(item, JobItem):
            self.db[self.collection_name].insert_one(dict(item))
<<<<<<< HEAD
            self.no_items_added += 1
=======
>>>>>>> f38684dd49bf46158a1ee1bc4f10185034cc3b32
        return item


