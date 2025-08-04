import scrapy
from parsel import Selector

class CareervietSpider(scrapy.Spider):
    name = "careerviet"
    allowed_domains = ["careerviet.vn"]

    custom_settings = {
        'FEEDS': {
            'careerviet.csv': {
                'format': 'csv',
                'overwrite': True
            }
        },
        'LOG_ENABLED': False
    }

    def __init__(self, start_urls=None, *args, **kwargs):
        super(CareervietSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls or ["https://careerviet.vn/viec-lam/data-scientist-k-vi.html"]
        self.page_count = 1

    def parse(self, response):
        # ... giữ nguyên phần parse
        for job in response.css("div.job-item"):
            job_url = response.urljoin(job.css("div.title a.job_link::attr(href)").get())

            job_info = {
                "title": job.css("div.title a.job_link::text").get(default="").strip(),
                "company": job.css("a.company-name::text").get(default="").strip(),
                "location": ", ".join(job.css("div.location li::text").getall()).strip(),
                "salary": job.css("div.salary p::text").get(default="").replace("Lương: ", "").strip(),
                "job_url": job_url
            }

            yield response.follow(job_url, callback=self.parse_detail, meta={'job_info': job_info})

        if self.page_count < 4:
            next_page = response.css('a[rel=next]::attr(href)').get()
            if next_page:
                self.page_count += 1
                yield response.follow(next_page, callback=self.parse)

    def parse_detail(self, response):
        job_info = response.meta['job_info']
        
        detail_section = response.css("div.detail-row.reset-bullet").get(default="")
        if not detail_section:
            detail_section = response.css("div.detail-title").get(default="")

        selector = Selector(text=detail_section)
        description_text = selector.xpath("string()").get(default="").strip()

        job_info["description"] = description_text
        yield job_info
