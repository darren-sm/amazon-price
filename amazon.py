# Libraries 
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlencode
import argparse


# Create the Spider
class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    # Custom Headers - Manipulate the Request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    }
        
    # Custom Spider Settings - Customize the Spider
    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ROBOTSTXT_OBEY': False
    }

    @staticmethod
    # Modify the URL by custom API Key - avoid getting banned
    def get_url(url):
        API = 'c555fa397d677caa732fbdfac7271c6e'
        payload = {
            'api_key': API, 'url': url
        }
        return 'http://api.scraperapi.com/?' + urlencode(payload)

    # Start The Request
    def start_requests(self):
        """
        Send the request on a base link given
        """
        base_link = f'https://www.amazon.{args.domain.lower()}/s?k={args.item.lower().strip().replace(" ", "+")}&page='
        for i in range(1, args.page + 1):
            yield scrapy.Request(AmazonSpider.get_url(base_link + str(i)), meta = {'link':base_link + str(i)}, headers = self.headers, callback = self.parse)

    # Parse the response
    def parse(self, response):
        """
        Parse the response sent from our request above.
        """
        # Products are listed in a row. 
        product_list = response.xpath('//div[@class="s-main-slot s-result-list s-search-results sg-row"]/child::div[not(@data-asin="") and not(contains(@class, "AdHolder"))]')
        for product in product_list:
            # Get the details of a product
            name = product.xpath('.//h2//span/text()').get()
            price = product.xpath('.//div[@class="a-row a-size-base a-color-base"]/a/child::span[position() = 1]/span/text()').get()
            secondary_price = product.xpath('.//div[@class="a-row a-size-base a-color-base"]/a/child::span[position() = 2]/text()').get()            
            previous_price = product.xpath('.//div[@class="a-row a-size-base a-color-base"]/a/child::span[position() = 3]/span/text()').get()
            discount = product.xpath('.//div[@class="a-row a-size-base a-color-base"]/span/text()').get()
            rating = product.xpath('.//div[@class="a-row a-size-small"]/span/@aria-label').get()
            review_count = product.xpath('.//div[@class="a-row a-size-small"]/span[position() = 2]/@aria-label').get()
            product_link = 'https://www.amazon.in' + product.xpath('.//h2/a/@href').get()
            thumbnail = product.xpath('.//span//a//img/@src').get()
            # Generate a dictionary that contains details of the product. Output will be on CSV
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

if __name__ == '__main__':
    # Get the amazon link based on user options
    parser = argparse.ArgumentParser(description='Amazon search result web scraper')

    parser.add_argument("-i", "--item", help="Target the web scraper to the Amazon search of your product", required=True)
    parser.add_argument("-d", "--domain", help="Assign the domain for your amazon search. Example, `in` for Indian Amazon domain https://www.amazon.in/. Defaults to `com`", default="com")
    parser.add_argument("-p", "--page", help="Assign how many pages of the search result to scrape. Default is 5", default=5, type=int)

    args = parser.parse_args()
    domains = ['eg', 'br', 'ca', 'mx', 'com', 'cn', 'in', 'jp', 'sg', 'ae', 'sa', 'fr', 'de', 'it', 'nl', 'pl', 'es', 'tr', 'uk', 'au']

    if args.page < 1:
        raise Exception("Target pages to scrape must at least be 1.")
    if args.domain.lower() not in domains:
        raise Exception(f"Not a proper domain. The available ones are:\n\t-{', '.join(domains)}\nPlease see https://en.wikipedia.org/wiki/Amazon_(company)#Website for more info")


    # Start the web scraping
    process = CrawlerProcess({
        'FEED_URI': 'products.csv',
        'FEED_FORMAT': 'csv'
    })
    process.crawl(AmazonSpider)
    process.start()