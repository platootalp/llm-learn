from urllib.parse import urljoin

import scrapy


class JavaBasicSpider(scrapy.Spider):
    name = "java_basic"
    allowed_domains = ["javaguide.cn"]
    start_urls = ["https://javaguide.cn/java/basis/java-basic-questions-01.html"]

    # def parse(self, response):
    #     for h2 in response.css('h2'):
    #         yield {"title": h2.css('::text').get().strip()}
    def parse(self, response):
        # 抓取侧边栏所有链接
        links = response.css("a.vp-sidebar-link::attr(href)").getall()
        for href in links:
            full_url = urljoin(response.url, href)
            yield scrapy.Request(full_url, callback=self.parse_content)

    def parse_content(self, response):
        title = response.css("h1::text").get()
        # content = response.css("main").get()
        yield {
            "url": response.url,
            "title": title
            # "content": content
        }