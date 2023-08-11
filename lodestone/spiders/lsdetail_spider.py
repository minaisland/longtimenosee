import scrapy
import re
import os
from lodestone.items import CharacterItem
from lodestone.spiders import BaseSpider

class LsdetailSpider(BaseSpider):
    name = "lsd"
    custom_settings = {
        "ITEM_PIPELINES": {
            "lodestone.pipelines.LinkshellCharacterPipeline": 300,
        }
    }

    def start_requests(self):
        super().start_requests()
        with open("ls.txt", "rt") as f:
            urls = [url.strip() for url in f.readlines()]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        character_item = CharacterItem()
        ls_lodestone_id = re.search(r"\d+", response.url).group()
        for entry in response.css("div.ls__member div.entry"):
            character_item["lodestone_id"] = entry.css("a.entry__link::attr(href)").re(r"\d+")[0]
            character_item["name"] = entry.css("p.entry__name::text").get()
            character_item["world"] = entry.css("p.entry__world::text").re(r"(\w+)\s+")[0]
            character_item["avatar_url"] = entry.css("div.entry__chara__face img::attr(src)").get()
            character_item["ls_lodestone_id"] = ls_lodestone_id
            character_item["is_owner"] = len(entry.css("div.entry__chara_info__linkshell")) > 0
            yield character_item

        self.goto_next_page()

    def spider_closed(self, spider):
        if os.path.isfile("ls.txt"):
            os.remove("ls.txt")
        super().spider_closed(spider)
