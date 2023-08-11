import scrapy
import re
from scrapy import signals
from lodestone.items import CharacterItem

class CwlsdetailSpider(scrapy.Spider):
    name = "cwlsd"
    custom_settings = {
        "ITEM_PIPELINES": {
            "lodestone.pipelines.CrossLinkshellCharacterPipeline": 300,
        }
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CwlsdetailSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def start_requests(self):
        with open("ls.txt", "rt") as f:
            urls = [url.strip() for url in f.readlines()]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        character_item = CharacterItem()
        ls_lodestone_id = re.search(r"[a-z0-9]{16,}", response.url).group()
        for entry in response.css("div.ls__member div.entry"):
            character_item["lodestone_id"] = entry.css("a.entry__link::attr(href)").re(r"\d+")[0]
            character_item["name"] = entry.css("p.entry__name::text").get()
            character_item["world"] = entry.css("p.entry__world::text").re(r"(\w+)\s+")[0]
            character_item["avatar_url"] = entry.css("div.entry__chara__face img::attr(src)").get()
            character_item["cwls_lodestone_id"] = ls_lodestone_id
            character_item["is_owner"] = len(entry.css("div.entry__chara_info__linkshell")) > 0
            yield character_item

        next_page = response.css("div.ldst__window ul.btn__pager a.btn__pager__next::attr(href)").get()
        if next_page != "javascript:void(0);":
            yield response.follow(next_page, callback=self.parse)
        else:
            print("it is not nextpage")

    def spider_closed(self, spider):
        if os.path.isfile("ls.txt"):
            os.remove("ls.txt")
        spider.logger.info("Spider closed: %s", spider.name)
