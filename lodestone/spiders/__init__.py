# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy
from twisted.internet import reactor

class BaseSpider(scrapy.Spider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def __init__(self, is_next_page=True, *args, **kwargs):
        self.timeout = int(kwargs.pop("timeout", "60"))
        self.is_next_page = is_next_page
        super(BaseSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        reactor.callLater(self.timeout, self.stop)

    def stop(self):
        self.crawler.engine.close_spider(self, "timeout")

    def goto_next_page(self):
        if self.is_next_page:
            next_page = response.css("div.ldst__window ul.btn__pager a.btn__pager__next::attr(href)").get()
            if next_page != "javascript:void(0);":
                yield response.follow(next_page, callback=self.parse)
            else:
                print("it is not nextpage")

    def spider_closed(self, spider):
        spider.logger.info("Spider closed: %s", spider.name)
