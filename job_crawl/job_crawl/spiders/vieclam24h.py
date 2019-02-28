# coding: utf-8
import scrapy
from scrapy import Request
from job_crawl.items import JobItem


class VieclLam24hSpider(scrapy.Spider):
    name = "vieclam24h"
    start_urls = [
        "https://vieclam24h.vn"
    ]

    cookies = [
        {
            'gate_nganh': 14,
            '_gid': 'GA1.2.188974254.1551174426',
            '_ga': 'GA1.2.1690984599.1551174426',
            'gate': 'vlql'
        },
        {
            'gate_nganh': 14,
            '_gid': 'GA1.2.188974254.1551174426',
            '_ga': 'GA1.2.1690984599.1551174426',
            'gate': 'vlcm'
        },
        {
            'gate_nganh': 14,
            '_gid': 'GA1.2.188974254.1551174426',
            '_ga': 'GA1.2.1690984599.1551174426',
            'gate': 'ldpt'
        },
        {
            'gate_nganh': 14,
            '_gid': 'GA1.2.188974254.1551174426',
            '_ga': 'GA1.2.1690984599.1551174426',
            'gate': 'sv'
        }

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

    def parse(self, response):
        # for cookie in self.cookies:
        yield Request(
            url="https://vieclam24h.vn/tim-kiem-viec-lam-nhanh/?hdn_nganh_nghe_cap1=&hdn_dia_diem=&hdn_tu_khoa=&hdn_hinh_thuc=&hdn_cap_bac=",
            callback=self.parse_job_urls, cookies=self.cookies[3])

    def parse_job_urls(self, response):
        job_urls = [(response.urljoin(job_url), job_url)["vieclam24h" in job_url] for job_url in
                    response.css(self.selectors['job_url']).getall()]
        next_page = response.css(self.selectors['next_page']).get()

        for job_url in job_urls:
            yield Request(url=job_url, callback=self.parse_job_detail)

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(url=next_page, callback=self.parse_job_urls)

    def parse_job_detail(self, response):
        self.item = JobItem()
        job_selector = self.selectors['job']

        # Url
        self.item['url'] = response.request.url

        # Title
        self.item['title'] = response.css(job_selector['title']).get()
        if self.item['title'] is None:
            return

        # Company
        self.item['company'] = response.css(job_selector['company']).get()

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

        # Address
        self.item['address'] = response.css(job_selector['address']).get()

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
