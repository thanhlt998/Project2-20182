import scrapy
from scrapy import Request
from job_crawl.items import JobItem
import pymongo
import re
from ..remove_similar_data.remove_similar_data import DataReduction
from ..dict.load_dict import load_dict
from lxml import etree
import json


class CareerBuilderSpider(scrapy.Spider):
    name = "careerbuilder"

    start_urls = [
        "https://careerbuilder.vn/viec-lam/tat-ca-viec-lam-vi.html"
    ]

    selectors = {
        'job_url': "//div[contains(@class,'gird_standard')]//dd[contains(@class, 'brief')]/span[@class='jobtitle']/h3[@class='job']/a/@href",
        'next_page': "//div[@class='paginationTwoStatus']/a[@class='right']/@href",
        'job': {
            'title': "//div[@class='MyJobDetail']/div[@class='MyJobLeft']/div[@class='LeftJobCB']/div[@class='top-job']/div[@class='top-job-info']/h1/text()",
            'company': "//div[@class='MyJobDetail']/div[@class='MyJobLeft']/div[@class='LeftJobCB']/div[@class='top-job']/div[@class='top-job-info']/div[@class='tit_company']/text()",
            'salary': "//div[@id='showScroll']/ul/li/p/span[contains(text(), 'Lương')]/following-sibling::label/text()",
            'experience': "//div[@id='showScroll']/ul/li/p/span[contains(text(), 'Kinh nghiệm')]/../text()",
            'diploma': "",
            'amount': "",
            'career': "//div[@id='showScroll']/ul/li/p/span[contains(text(), 'Ngành nghề')]/following-sibling::b/a/text()",
            'address': "//div[@id='showScroll']/ul/li/p/span[contains(text(), 'Nơi làm việc')]/following-sibling::b/a/text()",
            'position': "//div[@id='showScroll']/ul/li/p/span[contains(text(), 'Cấp bậc')]/following-sibling::label/text()",
            'category': "",
            'trial_time': "",
            'sex': "",
            'age': "",
            'description': "//div[@class='MarBot20']/h4[contains(text(),'Mô tả Công việc')]/following-sibling::div[@class='content_fck']//text()",
            'benefits': "//div[@class='MarBot20 benefits-template']/h4[contains(text(),'Phúc lợi')]/following-sibling::ul/li/text()",
            'require_skill': "//div[@class='MarBot20']/h4[contains(text(),'Yêu Cầu Công Việc')]/following-sibling::div[@class='content_fck']//text()",
            'contact': "//div[@class='box1Detail']/p[@class='TitleDetailNew']/label//text()",
            'expired': "//div[@id='showScroll']/ul/li/p/span[contains(text(), 'Hết hạn nộp:')]/../text()",
            'created': "//div[@class='MyJobDetail']/div[@class='MyJobLeft']/div[@class='LeftJobCB']/div[@class='datepost']/span/text()",
            'other': "//div[@class='MarBot20']/h4[contains(text(),'Thông tin khác')]/following-sibling::div[@class='content_fck']/ul/li//text()"
        }
    }

    address_dict = load_dict('address')
    career_dict = load_dict('career')

    mongo_uri = 'mongodb://localhost:27017/'
    mongo_database = 'recruitment_information'
    mongo_collection = 'job_information'
    collection = pymongo.MongoClient(mongo_uri)[mongo_database][mongo_collection]
    data_reduction = DataReduction(3, [[job['title'], job['company'], ', '.join(job['address'])] for job in list(
        collection.find({}, {'title': 1, 'company': 1, 'address': 1, '_id': 0}))])
    no_duplicated_items = 0

    def parse(self, response):
        job_urls = response.xpath(self.selectors['job_url']).getall()
        next_page = response.xpath(self.selectors['next_page']).get()
        for job_url in job_urls:
            # yield Request(url=job_url, callback=self.parse_job)
            yield Request(url=job_url, callback=self.parse_json)

        if next_page is not None:
            yield Request(url=next_page, callback=self.parse)

    def parse_job(self, response):
        self.item = JobItem()
        job_selector = self.selectors['job']
        self.item['url'] = response.request.url

        # Title
        title = response.xpath(job_selector['title']).get()
        if title is None:
            return

        self.item['title'] = re.sub('(\\(.+\\)|\\[.+\\]|{.+}|–.+|-.*|,.*|Thu Nhập.*|Khu Vực.*|Làm Việc Tại.*|Lương.*|\d{1,2}[ ]{0,1}-[ ]{0,1}\d{1,2}.*)', '', title).strip()

        # Company
        company = response.xpath(job_selector['company']).get()
        self.item['company'] = re.sub('(\\(.*\\)|\\[.*\\]|{.*})', '', company).strip() if company is not None else ''

        # Address
        address_list = response.xpath(job_selector['address']).getall()
        addresses = sorted(
            [self.address_dict.get(address.replace(',', '').strip(), "Khác") for address in address_list])
        self.item['address'] = addresses

        # Check duplicate
        if self.data_reduction.is_match([title, company, ', '.join(addresses)]):
            self.no_duplicated_items += 1
            return

        # Salary
        salary = response.xpath(job_selector['salary']).getall()
        self.item['salary'] = self.normalize_salary(salary)

        # Experience
        experience = response.xpath(job_selector['experience']).get()
        self.item['experience'] = experience.strip() if experience is not None else "Không yêu cầu"

        # Career
        careers = [career.strip() for career in response.xpath(job_selector['career']).getall()]
        self.item['career'] = self.normalize_career(careers)

        # Description
        descriptions = response.xpath(job_selector['description']).getall()
        self.item['description'] = ' '.join([description.replace('-', '').strip() for description in descriptions])

        # Benefits
        benefits = response.xpath(job_selector['benefits']).getall()
        self.item['benefits'] = ', '.join(benefits).strip()

        # Require Skills
        require_skills = response.xpath(job_selector['require_skill']).getall()
        self.item['require_skill'] = " ".join([skill.replace('-', '').strip() for skill in require_skills])

        # Contact
        contacts = response.xpath(job_selector['contact']).getall()
        self.item['contact'] = ' '.join([contact.replace('-', '').strip() for contact in contacts])

        # Expired
        self.item['expired'] = response.xpath(job_selector['expired']).get().strip()

        # Created
        self.item['created'] = response.xpath(job_selector['created']).get().strip()

        # Other
        others = response.xpath(job_selector['other']).getall()

        # Age
        ages = [other.strip() for other in others if "tuổi" in other] + [description.strip() for description in
                                                                         descriptions if "tuổi" in description]
        if len(ages) > 0:
            self.item['age'] = ages[0].split(":")[-1].strip()

        # Diploma
        diploma = [other.strip() for other in others if
                   "bằng cấp" in other.lower() or "tốt nghiệp" in other.lower()] + [
                      description.strip() for description
                      in descriptions if "bằng cấp" in description.lower() or "tốt nghiệp" in description.lower()]
        if len(diploma) > 0:
            self.item['diploma'] = diploma[0].split(':')[-1].strip()
        else:
            self.item['diploma'] = ''

        # Category
        category = [other for other in others if "hình thức" in other.lower()]
        if len(category) > 0:
            self.item['category'] = category[0].split(":")[1].strip()
        else:
            self.item['category'] = ''

        # Sex
        sex_male = "Nam" if len([other for other in others if "nam" in other.lower()]) > 0 else ""
        sex_female = "Nữ" if len([other for other in others if "nữ" in other.lower()]) > 0 else ""
        sex = sex_male + ("", "/")[sex_male != "" and sex_female != ""] + sex_female
        if sex == "":
            self.item['sex'] = "Không yêu cầu"
        else:
            self.item['sex'] = sex

        yield self.item

    def close(self, spider, reason):
        print("Number of duplicated items: ", self.no_duplicated_items)

    def normalize_salary(self, salary):
        if len(salary) == 3:
            min_salary = int(re.sub('[,.]', '', salary[0]))
            max_salary = int(re.sub('[,.]', '', salary[1]))
            currency = salary[2]
            return {
                "min": min_salary,
                "max": max_salary,
                "currency": currency
            }
        elif len(salary) == 2:
            min_salary = max_salary = int(re.sub('[.,]', '', salary[0]))
            currency = salary[1]
            return {
                "min": min_salary,
                "max": max_salary,
                "currency": currency
            }
        elif len(salary) == 1:
            return {
                "min": 0,
                "max": 0,
                "currency": ""
            }

    def normalize_career(self, careers):
        normalized_career = []
        for career in careers:
            career_tmp = re.sub("\\s*[-\\/]\\s*", " - ", career)
            normalized_career.append(self.career_dict.get(career_tmp, "Khác"))
        return normalized_career

    def parse_json(self, response):
        dom = etree.HTML(response.body.decode("utf8"))
        json_node = dom.xpath("//script[@type='application/ld+json']")
        for node in json_node:
            try:
                job = json.loads(node.text, strict=False)
                if job['@type'] == 'JobPosting':
                    if job.get('url') is None:
                        job['url'] = response.request.url

                    job['occupationalCategory'] = job['industry']
                    del job['industry']

                    yield job

            except json.encoder.JSONEncoder:
                pass
