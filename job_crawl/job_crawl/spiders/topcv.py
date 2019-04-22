from scrapy import Request, Spider
from lxml import etree
import json


class TimViecNhanhSpider(Spider):
    name = 'topcv'

    start_urls = [
        'https://www.topcv.vn/viec-lam/moi-nhat.html?utm_source=click-search-job&utm_medium=page-job&utm_campaign=tracking-job'
    ]

    selectors = {
        'url': "//*[@id='box-job-result']/div[1]/div/div/div[2]/h4/a/@href",
        'next_page': "//*[@id='box-job-result']/div[2]/ul/li[last()]/a/@href",
        'job': {
            'occupation_category': '//*[@id="left-content"]/article/div[5]/div[1]/ul/li[5]/a/text()'
        }
    }

    def parse(self, response):
        urls = response.xpath(self.selectors['url']).getall()
        next_page = response.xpath(self.selectors['next_page']).get()

        for url in urls:
            yield Request(url=url, callback=self.parse_job_json)

        if next_page is not None:
            yield Request(url=next_page, callback=self.parse)

    def parse_job_json(self, response):
        dom = etree.HTML(response.body.decode("utf8"))
        json_node = dom.xpath("//script[@type='application/ld+json']")
        for node in json_node:
            try:
                job = json.loads(node.text, strict=False)

                # Schema in vieclam24h doesn't not have occupational Category
                # occupational_category = [category.strip() for category in
                #                          response.xpath(self.selectors['job']['occupation_category']).getall()]
                # job['occupationalCategory'] = occupational_category

                job['url'] = response.request.url

                yield job
            except json.encoder.JSONEncoder:
                pass

