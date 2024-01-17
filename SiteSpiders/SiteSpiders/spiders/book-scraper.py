import scrapy
from SiteSpiders.items import BookItem


class BookSpider(scrapy.Spider):
    name = "book"


    custom_settings = {
        "ITEM_PIPELINES": {
            "SiteSpiders.pipelines.SitespidersPipeline": 300,
            "SiteSpiders.pipelines.SaveToMysqlPipeline": 400}
    }

    def start_requests(self):
        urls = ["https://books.toscrape.com/"
                ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links = response.xpath("//h3/a/@href")
        title_links = response.xpath("//h3/a/text()")

        yield from response.follow_all(links, self.parse_link)

    def parse_link(self, response):
        book_item = BookItem()
        book_item['url'] = response.url
        book_item['price'] = response.xpath("//article/div[1]/div[2]/p[1]/text()").get()
        book_item['description'] = response.xpath("//article/p/text()").get()
        book_item['title'] = response.xpath("//article/div[1]/div[2]/h1/text()").get()
        yield book_item
