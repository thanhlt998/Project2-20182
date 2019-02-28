import scrapy
from scrapy import Request
from job_crawl.items import JobItem


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

    def parse(self, response):
        job_urls = response.xpath(self.selectors['job_url']).getall()
        next_page = response.xpath(self.selectors['next_page']).get()
        for job_url in job_urls:
            yield Request(url=job_url, callback=self.parse_job)

        if next_page is not None:
            yield Request(url=next_page, callback=self.parse)

    def parse_job(self, response):
        self.item = JobItem()
        job_selector = self.selectors['job']
        self.item['url'] = response.request.url

        # Title
        title = response.xpath(job_selector['title']).get()
        self.item['title'] = title
        if title is None:
            return

        # Company
        company = response.xpath(job_selector['company']).get()
        self.item['company'] = company if company is not None else title

        # Salary
        self.item['salary'] = response.xpath(job_selector['salary']).get()

        # Experience
        experience = response.xpath(job_selector['experience']).get()
        self.item['experience'] = experience.strip() if experience is not None else "Không yêu cầu"

        # Career
        careers = response.xpath(job_selector['career']).getall()
        self.item['career'] = ', '.join(careers)

        # Address
        self.item['address'] = response.xpath(job_selector['address']).get()

        # Description
        descriptions = response.xpath(job_selector['description']).getall()
        self.item['description'] = ' '.join([description.replace('-', '').strip() for description in descriptions])

        # Benifits
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
