from scrapy import Request, Spider
# from scrapy_splash import SplashRequest
from lxml import etree
import json


class TimViecNhanhSpider(Spider):
    name = 'mywork'

    start_urls = [
        'https://mywork.com.vn/tuyen-dung'
    ]

    selectors = {
        'url': "//*[@id='idJobNew']/div/div[1]/section/div/div[1]/div/div/p/a/@href",
        'next_page': "//*[@id='idJobNew']/div/div[2]/section/ul/li[last()]/a/@href",
    }

    splash_script = """
    function main(splash)
        splash:init_cookies(splash.args.cookies)
        local url = splash.args.url
        assert(splash:go(url))
        assert(splash:wait(2))
        return {
            cookies = splash:get_cookies(),
            html = splash:html()
        }
    end
    """

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield SplashRequest(url=url, callback=self.parse, endpoint='execute',
    #                             args={'lua_source': self.splash_script})

    def parse(self, response):
        urls = response.xpath(self.selectors['url']).getall()
        next_page = response.xpath(self.selectors['next_page']).get()

        for url in urls:
            yield Request(url=response.urljoin(url), callback=self.parse_job_json)

        if next_page is not None:
            # yield SplashRequest(url=response.urljoin(next_page), callback=self.parse, endpoint='execute',
            #                     args={'lua_source': self.splash_script})
            yield Request(url=response.urljoin(next_page), callback=self.parse)

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

                yield job
            except json.encoder.JSONEncoder:
                pass
