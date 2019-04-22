import scrapy
from scrapy import Request
from .utils.utils import parse_json
from pyMicrodata import pyMicrodata
import json


class CareerLink(scrapy.Spider):
    name = 'careerlink'

    start_urls = [
        'https://www.careerlink.vn/vieclam/list?keyword_use=A'
    ]

    microdata = pyMicrodata()

    selectors = {
        'job_url': "//div[@class='list-group list-search-result-group tlp headline']/div[contains(@class, 'list-group-item')]/h2[@class='list-group-item-heading']/a/@href",
        'next_page': "//div[contains(@class, 'search-result-paginator')]/nav/ul[@class='pagination']/li[@class='active']/following-sibling::li[1]/a/@href",
        'job': {
            'title': "//div[@class='page-header job-header']//span[@itemprop='title']/text()",
            'company': "//div[@class='job-data']/ul[contains(@class, 'critical-job-data')]/li/a[@class='text-accent']/span[@itemprop='hiringOrganization']/span[@itemprop='name']/text()",
            'salary': {
                'min': "//div[@class='job-data']/ul[contains(@class, 'critical-job-data')]/li[contains(text(), 'Lương:')]/span[@itemprop='baseSalary']/span[@itemprop='minValue']/@content",
                'max': "//div[@class='job-data']/ul[contains(@class, 'critical-job-data')]/li[contains(text(), 'Lương:')]/span[@itemprop='baseSalary']/span[@itemprop='maxValue']/@content",
                'currency': "//div[@class='job-data']/ul[contains(@class, 'critical-job-data')]/li[contains(text(), 'Lương:')]/span[@itemprop='baseSalary']/span[@itemprop='currency']/text()",
                'value': "//div[@class='job-data']/ul[contains(@class, 'critical-job-data')]/li[contains(text(), 'Lương:')]/span[@itemprop='baseSalary']/span[@itemprop='value']/text()"
            },
            'experience': "//span[@itemprop='experienceRequirements']/text()",
            'diploma': "//span[@itemprop='educationRequirements']/text()",
            'amount': "",
            'career': "//span[@itemprop='occupationalCategory']/text()",
            'address': "//ul[@class='list-unstyled']/li[contains(text(), 'Nơi làm việc:')]/ul/li[@itemprop='address']/a[@itemprop='addressRegion']/text()",
            'position': "//span[@itemprop='qualifications']/text()",
            'category': "//span[@itemprop='employmentType']/text()",
            'trial_time': "",
            'sex': "//ul[@class='list-unstyled']/li[contains(text(), 'Giới tính:')]/text()",
            'age': "//ul[@class='list-unstyled']/li[contains(text(), 'Tuổi:')]/text()",
            'description': "//div[@class='job-data']/div[@itemprop='description']/p/text()",
            'benefits': "",
            'require_skill': "//div[@class='job-data']/div[@itemprop='skills']/p/text()",
            'contact': {
                'person': "//div[@class='job-data']/ul[@class='list-unstyled']/li[contains(text(), 'Tên liên hệ:')]/text()",
                'address': "//div[@class='job-data']/ul[@class='list-unstyled']/li/span[@itemprop='jobLocation']//span/text()"
            },
            'expired': "//div[@class='job-data']/dl//span[@itemprop='validThrough']/text()",
            'created': "//div[@class='job-data']/dl//span[@itemprop='datePosted']/text()",
        }
    }

    # address_dict = load_dict('address')
    # career_dict = load_dict('career')
    #
    # mongo_uri = 'mongodb://localhost:27017/'
    # mongo_database = 'recruitment_information'
    # mongo_collection = 'job_information'
    # collection = pymongo.MongoClient(mongo_uri)[mongo_database][mongo_collection]
    # data_reduction = DataReduction(3, [[job['title'], job['company'], ', '.join(job['address'])] for job in list(
    #     collection.find({}, {'title': 1, 'company': 1, 'address': 1, '_id': 0}))])
    # no_duplicated_items = 0

    def parse(self, response):
        job_urls = [response.urljoin(url) for url in response.xpath(self.selectors['job_url']).getall()]
        next_page = response.xpath(self.selectors['next_page']).get()

        for job_url in job_urls:
            yield Request(url=job_url, callback=self.parse_job_json)

        if next_page is not None:
            yield Request(url=response.urljoin(next_page), callback=self.parse)

    # def parse_job(self, response):
    #     self.item = JobItem()
    #     job_selector = self.selectors['job']
    #     self.item['url'] = response.request.url
    #
    #     # Title
    #     title = response.xpath(job_selector['title']).get()
    #     if title is None:
    #         return
    #
    #     self.item['title'] = re.sub('(\\(.+\\)|\\[.+\\]|{.+}|–.+|-.*|,.*|Thu Nhập.*|Khu Vực.*|Làm Việc Tại.*|Lương.*|\d{1,2}[ ]{0,1}-[ ]{0,1}\d{1,2}.*)', '', title).strip()
    #
    #     # Company
    #     company = response.xpath(job_selector['company']).get()
    #     self.item['company'] = re.sub('(\\(.*\\)|\\[.*\\]|{.*})', '', company).strip() if company is not None else ''
    #
    #     # Address
    #     address_list = list(set(address.strip() for address in response.xpath(job_selector['address']).getall()))
    #     addresses = sorted(
    #         [self.address_dict.get(address.replace(',', '').strip(), "Khác") for address in address_list])
    #     self.item['address'] = addresses
    #
    #     # Check duplicate
    #     if self.data_reduction.is_match([title, company, ', '.join(addresses)]):
    #         self.no_duplicated_items += 1
    #         return
    #
    #     # Salary
    #     min_salary = response.xpath(job_selector['salary']['min']).get()
    #     max_salary = response.xpath(job_selector['salary']['max']).get()
    #     currency = response.xpath(job_selector['salary']['currency']).get()
    #     value = response.xpath(job_selector['salary']['value']).get()
    #
    #     self.item['salary'] = self.normalize_salary(min_salary, max_salary, currency, value)
    #
    #     # Experience
    #     experience = response.xpath(job_selector['experience']).get()
    #     self.item['experience'] = experience.strip() if experience is not None else ''
    #
    #     # Career
    #     careers = [career.strip() for career in response.xpath(job_selector['career']).getall()]
    #     self.item['career'] = self.normalize_career(careers)
    #
    #     # Description
    #     descriptions = response.xpath(job_selector['description']).getall()
    #     self.item['description'] = ' '.join([description.replace('-', '').strip() for description in descriptions])
    #
    #     # Benefits
    #     # benefits = response.xpath(job_selector['benefits']).getall()
    #     # self.item['benefits'] = ', '.join(benefits).strip()
    #     self.item['benefits'] = ''
    #
    #     # Require Skills
    #     require_skills = response.xpath(job_selector['require_skill']).getall()
    #     self.item['require_skill'] = " ".join([skill.replace('-', '').strip() for skill in require_skills])
    #
    #     # Contact
    #     contact_person = response.xpath(job_selector['contact']['person']).get()
    #     contact_address = response.xpath(job_selector['contact']['address']).getall()
    #     self.item['contact'] = {
    #         'person': contact_person.split(':')[-1].strip() if contact_person is not None else '',
    #         'address': ' '.join([s.strip() for s in contact_address])
    #     }
    #
    #     # Expired
    #     self.item['expired'] = response.xpath(job_selector['expired']).get().strip()
    #
    #     # Created
    #     self.item['created'] = response.xpath(job_selector['created']).get().strip()
    #
    #     # Age
    #     age = response.xpath(job_selector['age']).get()
    #     self.item['age'] = age.split(":")[-1].strip() if age is not None else ''
    #
    #     # Diploma
    #     diploma = response.xpath(job_selector['diploma']).get()
    #     self.item['diploma'] = diploma.strip() if diploma is not None else ''
    #
    #     # Category
    #     category = response.xpath(job_selector['category']).get()
    #     self.item['category'] = category.strip() if category is not None else ''
    #
    #     # Sex
    #     sex = response.xpath(job_selector['sex']).get()
    #     self.item['sex'] = sex.split(':')[-1].strip() if sex is not None else ''
    #     yield self.item
    #
    # def normalize_salary(self, min_salary, max_salary, currency, value):
    #     salary = {}
    #     if value is None:
    #         salary['min'] = int(min_salary)
    #         salary['max'] = int(max_salary)
    #         salary['currency'] = currency
    #     else:
    #         values = re.compile('\d+').findall(re.sub('[.,]', '', value))
    #         if len(values) == 0:
    #             salary['min'] = salary['max'] = 0
    #             salary['currency'] = ''
    #         elif len(values) >= 1:
    #             salary['min'] = int(values[0])
    #             salary['max'] = int(values[-1])
    #             salary['currency'] = currency
    #     return salary
    #
    # def close(self, spider, reason):
    #     print("Number of duplicated items: ", self.no_duplicated_items)
    #
    # def normalize_career(self, careers):
    #     normalized_career = []
    #     for career in careers:
    #         career_tmp = re.sub("\\s*[-\\/]\\s*", " - ", career)
    #         normalized_career.append(self.career_dict.get(career_tmp, "Khác"))
    #     return normalized_career

    def parse_job_json(self, response):
        raw_json = json.loads(self.microdata.rdf_from_source(response.body, 'json-ld').decode('utf8'))
        format_json = parse_json(raw_json)
        for item in format_json:
            yield item

