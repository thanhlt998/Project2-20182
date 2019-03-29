from scrapy import Request, Spider
from lxml import etree
import json


class TimViecNhanhSpider(Spider):
    name = 'timviecnhanh'

    start_urls = [
        'https://www.timviecnhanh.com/vieclam/timkiem?tu_khoa=&nganh_nghe%5B%5D=&tinh_thanh%5B%5D='
    ]

    selectors = {
        'url': "/html/body/section/div/div/div/div/article[1]/table/tbody/tr/td[1]/a[1]/@href",
        'next_page': "/html/body/section/div/div[1]/div/div/article[1]/table/tfoot/tr/td/div/a[last()]/@href",
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
                occupational_category = [category.strip() for category in
                                         response.xpath(self.selectors['job']['occupation_category']).getall()]
                job['occupationalCategory'] = occupational_category

                job['url'] = response.request.url

                yield job
            except json.encoder.JSONEncoder:
                pass

