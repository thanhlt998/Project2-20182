# coding: utf-8
import scrapy
from scrapy import Request
from job_crawl.items import JobItem
import pymongo
from ..remove_similar_data.remove_similar_data import DataReduction


class Vieclam24hSpider(scrapy.Spider):
    name = "vieclam24h"
    start_urls = [
        "https://vieclam24h.vn/viec-lam-quan-ly",
        "https://vieclam24h.vn/viec-lam-chuyen-mon",
        "https://vieclam24h.vn/viec-lam-lao-dong-pho-thong",
        "https://vieclam24h.vn/viec-lam-sinh-vien-ban-thoi-gian"
    ]

    selectors = {
        'job_url': 'div.list_item_two div.list-items span.title-blockjob-main a::attr(href)',
        'next_page': 'ul.pagination li.next a::attr(href)',
        'job': {
            'title': 'div.box_chi_tiet_cong_viec h1.title_big::text',
            'company': 'div.box_chi_tiet_cong_viec p.font16 a::text',
            'salary': 'p.line-icon i.icon-money + span span.job_value::text',
            'experience': 'p.line-icon i.icon-exp + span span.job_value::text',
            'diploma': 'p.line-icon i.icon-edu + span span.job_value::text',
            'amount': 'p.line-icon i.icon-quantity + span span.job_value::text',
            'career': 'div.line-icon i.icon-career + h2 .job_value::text',
            'address': 'p.line-icon i.icon-address + span .job_value::text',
            'position': 'p.line-icon i.icon-position + span .job_value::text',
            'category': 'p.line-icon i.icon-job-type + span .job_value::text',
            'trial_time': 'p.line-icon i.icon-countdown + span .job_value::text',
            'sex': 'p.line-icon i.icon-gender + span .job_value::text',
            'age': 'p.line-icon i.icon-age + span .job_value::text',
            'description': '#ttd_detail div.job_description div.pl_24.pr_24 div.item.row:nth-of-type(1) p.word_break::text',
            'benefits': '#ttd_detail div.job_description div.pl_24.pr_24 div.item.row:nth-of-type(2) p.word_break::text',
            'require_skill': '#ttd_detail div.job_description div.pl_24.pr_24 div.item.row:nth-of-type(3) p.word_break::text',
            'contact': '#ttd_detail div.item.row.pt_14.pb_14 > p::text',
            'expired': 'div.box_chi_tiet_cong_viec div.row span.pl_24 span.text_pink::text',
            'created': 'div.box_chi_tiet_cong_viec div.row p.text_grey2.font12 span:last-child::text',
        }
    }

    mongo_uri = 'mongodb://localhost:27017/'
    mongo_database = 'recruitment_information'
    mongo_collection = 'job_information'
    collection = pymongo.MongoClient(mongo_uri)[mongo_database][mongo_collection]
    data_reduction = DataReduction(3, [[job['title'], job['company'], job['address']] for job in list(
        collection.find({}, {'title': 1, 'company': 1, 'address': 1, '_id': 0}))])
    no_added_items = 0

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            yield Request(url=url, meta={'cookiejar': i, 'dont_merge_cookies': True}, callback=self.parse)

    def parse(self, response):
        yield Request(
            url="https://vieclam24h.vn/tim-kiem-viec-lam-nhanh/?hdn_nganh_nghe_cap1=&hdn_dia_diem=&hdn_tu_khoa=&hdn_hinh_thuc=&hdn_cap_bac=",
            meta={'cookiejar': response.meta['cookiejar'], 'dont_merge_cookies': True}, callback=self.parse_job_urls)

    def parse_job_urls(self, response):
        job_urls = [(response.urljoin(job_url), job_url)["vieclam24h" in job_url] for job_url in
                    response.css(self.selectors['job_url']).getall()]
        next_page = response.css(self.selectors['next_page']).get()
        cookiejar = response.meta['cookiejar']

        for job_url in job_urls:
            yield Request(url=job_url, meta={'cookiejar': cookiejar, 'dont_merge_cookies': True},
                          callback=self.parse_job_detail)

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(url=next_page, meta={'cookiejar': cookiejar, 'dont_merge_cookies': True},
                          callback=self.parse_job_urls)

    def parse_job_detail(self, response):
        self.item = JobItem()
        job_selector = self.selectors['job']

        # Url
        self.item['url'] = response.request.url

        # Title
        title = response.css(job_selector['title']).get()
        self.item['title'] = title
        if self.item['title'] is None:
            return

        # Company
        company = response.css(job_selector['company']).get()
        self.item['company'] = company

        # Address
        addresses = response.css(job_selector['address']).getall()
        address = ', '.join(
            [address.replace("Việc làm", "").replace("TP.HCM", "Hồ Chí Minh").strip() for address in addresses])
        self.item['address'] = address

        # Check duplicate
        if self.data_reduction.is_match([title, company, address]):
            return

        self.no_added_items += 1
        print('Added ', self.no_added_items, ' items.')

        # Salary
        self.item['salary'] = response.css(job_selector['salary']).get()

        # Experience
        self.item['experience'] = response.css(job_selector['experience']).get()

        # Diploma
        self.item['diploma'] = response.css(job_selector['diploma']).get()

        # Amount
        self.item['amount'] = int(response.css(job_selector['amount']).get())

        # Career
        self.item['career'] = ', '.join(response.css(job_selector['career']).getall())

        # Position
        self.item['position'] = response.css(job_selector['position']).get()

        # Category
        self.item['category'] = response.css(job_selector['category']).get()

        # Trial Time
        trial_time = response.css(job_selector['trial_time']).get()
        self.item['trial_time'] = trial_time if trial_time is not None else ''

        # Sex
        self.item['sex'] = response.css(job_selector['sex']).get()

        # Age
        self.item['age'] = response.css(job_selector['age']).get()

        # Description
        self.item['description'] = " ".join(
            [description.replace("-", "").strip() for description in
             response.css(job_selector['description']).getall()])

        # Benefits
        self.item['benefits'] = " ".join(
            [benefit.replace("-", "").strip() for benefit in response.css(job_selector['benefits']).getall()])

        # Require Skill
        self.item['require_skill'] = " ".join(
            [line.replace("-", "").strip() for line in response.css(job_selector['require_skill']).getall()]
        )

        # Contact
        contacts = response.css(job_selector['contact']).getall()
        self.item['contact'] = f"Người liên hệ: {contacts[0].strip()}; Địa chỉ liên hệ: {contacts[1].strip()}"

        # Expired
        self.item['expired'] = response.css(job_selector['expired']).get()

        # Created
        self.item['created'] = response.css(job_selector['created']).get().split(':')[1].strip()

        yield self.item
