from pathlib import Path
import os
import scrapy
from datetime import datetime

from SiteSpiders.items import NewsItem


class CNNSpider(scrapy.Spider):
    name = "cnn"
    date_curr = datetime.now().date()
    url_visited = set()

    custom_settings = {
        "ITEM_PIPELINES": {"SiteSpiders.pipelines.NewsPipeline": 300,
                           "SiteSpiders.pipelines.NewsSaveToMySQL": 400
                           }
    }

    testing = False

    def start_requests(self):
        if self.testing:
            test_url = "https://cnn.com/"
            urls = [test_url]
        else:
            urls = [

                "https://cnn.com/",
            ]

        allowed_domains = [
            "cnn.com", "www.cnn.com"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # visit the homepage and get the links to articles
    def parse(self, response):

        if self.testing:
            test_url = "https://www.cnn.com/2024/01/17/middleeast/israel-far-right-gaza-settler-movement-cmd-intl/index.html"
            links = [test_url]
            yield from response.follow_all(links, self.parse_link, dont_filter=False)

        else:

            filename = f"{self.date_curr}_{self.name}.log"
            links = response.xpath("//div/a/@href").getall()
            try:
                with open(filename, 'a') as file:
                    for link in links:
                        if link.startswith("/"):
                            file.write((response.urljoin(link) + "\n"))
                self.log(f"Saved file: {self.name} : links : {filename}")
            except Exception as e:
                self.log(f"error: {e} -- saving {self.name} : links : {filename}")

            # adding full url using urljoin
            links = [response.urljoin(link) for link in links if link.startswith("/")]
            yield from response.follow_all(links, self.parse_link, dont_filter=False)

    # visit the article link and get the author link
    def parse_link(self, response):
        """
        @url https://www.cnn.com/2024/01/11/politics/us-strikes-houthis-yemen/index.html
        @scrapes article_url news_site article_title
        :param response:
        :return:
        """
        item = NewsItem()

        item["author_profile_link"] = None
        item["author_twitter_link"] = None
        item["article_url"] = None
        item["article_title"] = None
        item["news_site"] = None

        item["news_site"] = self.name.upper()

        # get the article url and article tile / set item detail
        self.log(f" {response.url}")

        item["article_url"] = response.url

        article_title = response.xpath("//h1/text()").get().strip()
        # response.xpath("//h1/text()").get()

        item["article_title"] = article_title

        # get authors links, maybe multiple authors
        author_link = response.css("div.byline__names").xpath("a/@href").getall()

        # names of all authors w/ link => response.css("div.byline__names").xpath("a/span/text()").getall()
        if os.environ.get("SCRAPY_CHECK"):
            print(" ## The author links")
            print(author_link)

        # author link can be empty
        if len(author_link) < 1:
            self.log(f"No author links on {response.url}")
            pass

            ### fill later
            # get byline text response.css("div.byline__names").xpath("text()").getall()

        else:

            filename = f"{self.date_curr}_{self.name}_authors.log"
            try:
                with open(filename, 'a') as file:
                    for link in author_link:
                        if link.startswith("/"):
                            file.write(("https://cnn.com" + link + "\n"))
                        file.write((link + "\n"))

                self.log(f"Saved file {self.name}  : author links : {filename}")

                for index, link in enumerate(author_link):
                    new_item = item.deepcopy()

                    if link.startswith("/"):
                        link = "https://cnn.com" + link
                    if link not in self.url_visited:
                        self.url_visited.add(link)

                        request = response.follow(link, callback=self.author_link,
                                                  meta={'item': new_item}, dont_filter=False, priority=(index + 1))
                        yield request

                    else:
                        new_item["author_profile_link"] = link
                        self.log(f"### already visited author profile url - will get from database ###")
                        ### need to process these in item pipeline

                        yield new_item

            except Exception as e:
                self.log(f"error {e} -- saving {self.name}  : author links : {filename}")
                yield item

    def author_link(self, response):
        """
        @url https://www.cnn.com/profiles/scott-mclean-profile
        @scrapes author_name
        :param response:
        :return: item
        """
        if os.environ.get("SCRAPY_CHECK"):
            item = {}
        else:
            item = response.meta["item"]

        item["author_profile_link"] = response.url

        author_name = response.css("section.profile__top").xpath("div/div/h1/text()").get().strip()
        item["author_name"] = author_name

        self.log(f"### author profile visiting will get name {item['author_name']} from {response.url}")

        social_links = response.css("section.profile__top").xpath("div/div/ul/li/a/@href").getall()
        if social_links:
            for author_social_link in social_links:
                if "twitter" in author_social_link:
                    item["author_twitter_link"] = author_social_link

        if os.environ.get("SCRAPY_CHECK"):
            print(social_links)
            print(item["author_twitter_link"])

        yield item
