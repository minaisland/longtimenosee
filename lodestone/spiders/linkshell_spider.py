import scrapy
from lodestone.items import LinkshellItem
from lodestone.spiders import BaseSpider

class LinkshellSpider(BaseSpider):
    name = "ls"
    custom_settings = {
        "ITEM_PIPELINES": {
            "lodestone.pipelines.LinkshellPipeline": 300,
            "lodestone.pipelines.GeneratorURLPipeline": 400,
        }
    }

    def start_requests(self):
        super().start_requests()
        urls = [
            "https://jp.finalfantasyxiv.com/lodestone/linkshell/?q=&worldname=Chocobo&character_count=11-30&order=",
            "https://jp.finalfantasyxiv.com/lodestone/linkshell/?q=&worldname=Chocobo&character_count=31-50&order=",
            "https://jp.finalfantasyxiv.com/lodestone/linkshell/?q=&worldname=Chocobo&character_count=51-&order=",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        linkshell_item = LinkshellItem()
        linkshell_item["type_string"] = "linkshell"
        for entry in response.css("div.ldst__window div.entry"):
            linkshell_item["name"] = entry.css("p.entry__name::text").get()
            linkshell_item["world"] = entry.css("p.entry__world::text").re(r"(\w+)\s+")[0]
            linkshell_item["lodestone_id"] = entry.css("a.entry__link--line::attr(href)").re(r"\d+")[0]
            yield linkshell_item

        self.goto_next_page()
