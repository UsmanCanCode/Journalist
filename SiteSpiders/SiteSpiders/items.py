# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SitespidersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

# you can clean items as they are being added
# the effect only shows in final output aka csv
def serialize_price(value):
    return f'${str(value)[1:]}'


class BookItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()

class AuthorItem(scrapy.Item):
    name = scrapy.Field()
    author_url = scrapy.Field()
    birth_date = scrapy.Field()
    quote = scrapy.Field()

class NewsItem(scrapy.Item):
    author_name = scrapy.Field()
    author_profile_link = scrapy.Field()
    author_twitter_link = scrapy.Field()
    article_url = scrapy.Field()
    article_title = scrapy.Field()
    news_site = scrapy.Field()