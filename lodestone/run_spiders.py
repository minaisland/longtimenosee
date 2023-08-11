from twisted.internet import reactor, defer
from lodestone.spiders.linkshell_spider import LinkshellSpider
from lodestone.spiders.lsdetail_spider import LsdetailSpider
from lodestone.spiders.crosslinkshell_spider import CrossLinkshellSpider
from lodestone.spiders.cwlsdetail_spider import CwlsdetailSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
configure_logging(settings)
runner = CrawlerRunner(settings)

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(LinkshellSpider)
    yield runner.crawl(LsdetailSpider)
    yield runner.crawl(CrossLinkshellSpider)
    yield runner.crawl(CwlsdetailSpider)
    reactor.stop()

def go():
    crawl()
    reactor.run()  # the script will block here until the last crawl call is finished
