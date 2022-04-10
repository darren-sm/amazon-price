# Libraries 
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlencode
import scraper_helper as sh 
API = 'c555fa397d677caa732fbdfac7271c6e'

# Modify the URL by custom API Key - avoid getting banned
def get_url(url):
    payload = {
        'api_key': API, 'url': url
    }
    return 'http://api.scraperapi.com/?' + urlencode(payload)

# Create the Spider
class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    # Custom Headers - Manipulate the Request
    headers = sh.get_dict(
        """
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0
        """
    )

    # Custom Spider Settings - Customize the Spider
    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ROBOTSTXT_OBEY': False
    }

    # Start The Request
    def start_requests(self):
        base_link = 'https://www.amazon.in/s?k=ginger+powder&page='
        for i in range(1,8):
            yield scrapy.Request(get_url(base_link + str(i)), meta = {'link':base_link + str(i)}, headers = self.headers, callback = self.parse)

    # Parse the response
    def parse(self, response):
        product_list = response.xpath('//div[@class="s-main-slot s-result-list s-search-results sg-row"]/child::div[not(@data-asin="") and not(contains(@class, "AdHolder"))]')
        for product in product_list:
            name = product.xpath('.//h2//span/text()').get()
            price = product.xpath('.//div[@class="a-row a-size-base a-color-base"]/a/child::span[position() = 1]/span/text()').get()
            secondary_price = product.xpath('.//div[@class="a-row a-size-base a-color-base"]/a/child::span[position() = 2]/text()').get()            
            previous_price = product.xpath('.//div[@class="a-row a-size-base a-color-base"]/a/child::span[position() = 3]/span/text()').get()
            discount = product.xpath('.//div[@class="a-row a-size-base a-color-base"]/span/text()').get()
            rating = product.xpath('.//div[@class="a-row a-size-small"]/span/@aria-label').get()
            review_count = product.xpath('.//div[@class="a-row a-size-small"]/span[position() = 2]/@aria-label').get()
            product_link = 'https://www.amazon.in' + product.xpath('.//h2/a/@href').get()
            thumbnail = product.xpath('.//span//a//img/@src').get()

            yield {
                'name': name,
                'price': price,
                'secondary_price': secondary_price,
                'previous_price': previous_price,
                'discount': discount,
                'rating': rating,
                'review_count': review_count,
                'product_link': product_link,
                'thumbnail': thumbnail
            }

# Run the Spider
if __name__ == '__main__':
    process = CrawlerProcess({
        'FEED_URI': 'products.csv',
        'FEED_FORMAT': 'csv'
    })
    process.crawl(AmazonSpider)
    process.start()