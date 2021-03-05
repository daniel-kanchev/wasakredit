import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from wasakredit.items import Article


class WasakreditSpider(scrapy.Spider):
    name = 'wasakredit'
    allowed_domains = ['wasakredit.se']
    start_urls = ['https://www.wasakredit.se/om-oss/nyheter/']

    def parse(self, response):
        articles = response.xpath('//li[@class="list-group-item block-image-left"]')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('.//time/text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//li[@class="page-item"][last()]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="container main-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
