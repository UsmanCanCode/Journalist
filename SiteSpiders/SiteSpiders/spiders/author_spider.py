import scrapy
from SiteSpiders.items import AuthorItem
import os

# name = scrapy.Field()
# author_url = scrapy.Field()
# birth_date = scrapy.Field()
# quote = scrapy.Field()

class AuthorSpider(scrapy.Spider):
    name = "author"

    custom_settings = {
        "ITEM_PIPELINES": {"SiteSpiders.pipelines.AuthorPipeline": 300,
                           "SiteSpiders.pipelines.AuthorMysqlPipeline": 400
                           }
    }

    url_visited = set()

    def start_requests(self):

        urls = ["https://quotes.toscrape.com/"
                ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):


        quotes_div = response.css(".quote")

        for q in quotes_div:
            author_item = AuthorItem()
            author_item["author_url"] = q.xpath("span[2]/a/@href").get()
            author_item["author_url"] = response.urljoin(author_item["author_url"])
            author_item["name"] = q.xpath("span[2]/small/text()").get()
            author_item["quote"] = q.xpath("span[1]/text()").get()
            author_item["birth_date"] = ''

            if author_item["author_url"] not in self.url_visited:
                self.url_visited.add(author_item["author_url"])

                request = response.follow(author_item["author_url"], callback=self.parse_link,
                                          meta={'item': author_item}, dont_filter=False)
                yield request

            else:

                yield author_item

    def parse_link(self, response):
        """
        @url https://quotes.toscrape.com/author/Albert-Einstein

        @scrapes birth_date profile
        @returns items 1 4
        """
        if os.environ.get("SCRAPY_CHECK"):
            author_item = {"author_url":"Albert-Einstein", "name":"Albert Einsetin", "quote":"test"}
        else:
            author_item = response.meta['item']

        author_item["birth_date"] = response.xpath("//p[1]/span/text()").get()

        return author_item

    # get all authors : response.xpath("//div/span[2]").css(".author::text").getall()

    # get the quotes as list: response.css(".quote")
    # use without get() and getall() to get selectorlist otherwise return string.

    # get all quotes as list a comprehension
    # [quote.xpath("span[1]/text()").get() for quote in response.css(".quote")]

    # get the author url:
    # [quote.xpath("span[2]/a/@href").get() for quote in response.css(".quote")]

    # get author name
    # [quote.xpath("span[2]/small/text()").get() for quote in response.css(".quote")]
