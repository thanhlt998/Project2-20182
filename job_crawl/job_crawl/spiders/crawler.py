from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from lxml import etree
import json
from pyMicrodata import pyMicrodata
import os
import re
from utils.utils import parse_json
from utils.detect_schema import JobSchemaDetection
from utils.model import NaiveBayesModel, DecisionTreeModel
from utils.preprocess import FeaturesTransformer
from utils.job_normalization import normalize_job
from utils.utils import flatten_dict


class Crawler(Spider):
    name = 'new_crawler'

    MODEL_DIR = 'job_crawl/spiders/models'
    STANDARD_ATTRIBUTES_FN = 'job_crawl/spiders/utils/attributes.json'
    WEIGHT_MODEL_FN = 'job_crawl/spiders/utils/weight.json'
    MAX_NO_SAMPLES = 20

    microdata = pyMicrodata()
    schema = None
    map_schema = None
    standard_sample = None
    domain = ''
    parse_job = None
    get_job_sample = None
    samples = []
    selectors = {

    }
    start_url = None

    def start_requests(self):
        self.get_input_info()

        with open(self.STANDARD_ATTRIBUTES_FN, mode='r', encoding='utf8') as f:
            self.standard_sample = json.load(f)
            f.close()

        yield Request(url=self.start_url, callback=self.get_data_format)

    def get_input_info(self):
        # self.start_url = input('Enter start url: ')
        # self.selectors['next_page'] = input('Enter next_page xpath: ')
        # self.selectors['job_url'] = input('Enter job_url xpath: ')

        # self.start_url = 'https://www.timviecnhanh.com/vieclam/timkiem?tu_khoa=&nganh_nghe%5B%5D=&tinh_thanh%5B%5D='
        # self.selectors['next_page'] = '/html/body/section/div/div[1]/div/div/article[1]/table/tfoot/tr/td/div/a[last()]'
        # self.selectors['job_url'] = '/html/body/section/div/div/div/div/article[1]/table/tbody/tr/td[1]/a[1]'
        #
        self.start_url = 'https://www.topcv.vn/viec-lam/moi-nhat.html?utm_source=click-search-job&utm_medium=page-job&utm_campaign=tracking-job'
        self.selectors['next_page'] = '//*[@id="box-job-result"]/div[2]/ul/li[last()]/a'
        self.selectors['job_url'] = '//*[@id="box-job-result"]/div[1]/div/div/div[2]/h4/a'

        self.domain = re.search(r'(?<=www\.)\w+', self.start_url).group(0)

    def parse(self, response):
        next_page = response.xpath(self.selectors['next_page'] + '/@href').get()
        job_urls = response.xpath(self.selectors['job_url'] + '/@href').getall()

        for job_url in job_urls:
            job_url = response.urljoin(job_url)
            yield Request(url=job_url, callback=self.parse_job)

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(url=next_page, callback=self.parse)

    def get_data_format(self, response):
        sample_job_url = response.xpath(self.selectors['job_url'] + '/@href').get()
        yield Request(url=sample_job_url, callback=self.decide_data_format)

    def decide_data_format(self, response):
        can_crawl = True
        if self.is_data_json_format(response):
            self.parse_job = self.parse_job_json
            self.get_job_sample = self.get_job_sample_json
        elif self.is_data_microdata_format(response):
            self.parse_job = self.parse_job_microdata
            self.get_job_sample = self.get_job_sample_microdata
        else:
            print('Cannot crawl')
            can_crawl = False

        if can_crawl:
            if os.path.exists(f'job_crawl/spiders/schema/{self.domain}.json'):
                with open(f'job_crawl/spiders/schema/{self.domain}.json', mode='r', encoding='utf8') as f:
                    self.schema = json.load(f)
                    f.close()
                self.get_map_schema()
                yield Request(url=self.start_url, callback=self.parse)
            else:
                yield Request(url=self.start_url, callback=self.get_job_samples)

    def get_job_samples(self, response):
        next_page = response.xpath(self.selectors['next_page'] + '/@href').get()
        job_urls = response.xpath(self.selectors['job_url'] + '/@href').getall()

        for job_url in job_urls:
            if not job_url.startswith('http'):
                job_url = response.urljoin(job_url)
            if len(self.samples) >= self.MAX_NO_SAMPLES:
                break
            else:
                yield Request(url=job_url, callback=self.get_job_sample)

        if next_page is not None and len(self.samples) < self.MAX_NO_SAMPLES:
            if not next_page.startswith('http'):
                next_page = response.urljoin(next_page)
            yield Request(url=next_page, callback=self.get_job_samples)
        else:
            self.decide_schema()
            yield Request(url=self.start_url, callback=self.parse)

    def decide_schema(self):
        schema = JobSchemaDetection(self.samples, self.MODEL_DIR, self.STANDARD_ATTRIBUTES_FN,
                                    self.WEIGHT_MODEL_FN).get_mapping_schema()
        with open(f'job_crawl/spiders/schema/{self.domain}.json', mode='w', encoding='utf8') as f:
            json.dump(schema, f)
            f.close()
        self.schema = schema
        self.get_map_schema()

    def get_job_sample_json(self, response):
        self.samples += self.get_json_from_response_json(response)
        print(f'len_samples: {len(self.samples)}')

    def get_job_sample_microdata(self, response):
        self.samples += self.get_json_from_response_microdata(response)
        print(f'len_samples: {len(self.samples)}')

    def parse_job_json(self, response):
        jobs = self.get_json_from_response_json(response)
        for job in jobs:
            yield self.normalize(job)

    def parse_job_microdata(self, response):
        jobs = self.get_json_from_response_microdata(response)
        for job in jobs:
            yield self.normalize(job)

    def is_data_json_format(self, response):
        return len(self.get_json_from_response_json(response)) > 0

    def is_data_microdata_format(self, response):
        return len(self.get_json_from_response_microdata(response)) > 0

    @staticmethod
    def get_json_from_response_json(response):
        result = []
        dom = etree.HTML(response.body.decode("utf8"))
        json_node = dom.xpath("//script[text()]")
        for node in json_node:
            try:
                job = json.loads(node.text, strict=False)
                if job['@type'] == 'JobPosting':
                    result.append(job)

            except (ValueError, TypeError):
                pass
        return result

    def get_json_from_response_microdata(self, response):
        raw_json = json.loads(self.microdata.rdf_from_source(response.body, 'json-ld').decode('utf8'))
        result = parse_json(raw_json)
        return result

    def get_map_schema(self):
        self.map_schema = {key: value.split('_') for key, value in self.schema.items()}

    def normalize(self, job):
        norm_job = self.standard_sample.copy()
        flatten_job = flatten_dict(job)

        for key, value in self.map_schema.items():
            real_value = flatten_job.get(key)
            if real_value is None:
                continue
            else:
                attribute = norm_job
                for attribute_level in value[:-1]:
                    attribute = attribute.get(attribute_level)
                if type(real_value) is str:
                    attribute[value[-1]] = re.sub(r'<[^<>]*>', '', str(real_value))
                else:
                    attribute[value[-1]] = real_value

        return normalize_job(norm_job)


if __name__ == '__main__':
    setting = get_project_settings()
    setting['FEED_FORMAT'] = 'json'
    setting['FEED_URI'] = 'topcv.json'

    process = CrawlerProcess(setting)
    process.crawl(Crawler())
    process.start()
