from random import random
import scrapy

from bookscraper.items import BookItem

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    custom_settings = {
        'FEEDS': {
            'booksdata_ws.csv': {'format': 'csv', 'overwrite': True}
        }
    }#this FEEDS overwrite the one in settings.py

    # user_agent_list = [
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    #     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    #     'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    #     'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',]
    # This list contains different user agents to avoid getting blocked by the website
    #but when scraping large amounts of data it is not sufficient. so we use fake user agent api to call and loop through thousands of fake user agents


    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            # yield {
                # "name": book.css("h3 a::attr(title)").get(),
                # "price": book.css("p.price_color::text").get(),
                # "url": book.css("h3 a::attr(href)").get(),
                # "image_url": book.css("img.thumbnail::attr(src)").get(),
                # "availability": book.css("p.availability::text").re_first(r"\d+"),
            relative_url = book.css("h3 a::attr(href)").get()
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            yield response.follow(book_url, callback = self.parse_book_page) # type: ignore
            # } # here we create a new func to parse the book page, and here in the parse func we just keep url

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            yield response.follow(next_page_url, callback = self.parse)
# This spider scrapes book information from the website "books.toscrape.com".
# It extracts the book name, price, URL, image URL, and availability.
    def parse_book_page(self, response):
        table_rows = response.css("table tr")
        book_item = BookItem()
        
        book_item['url'] = response.url,
        book_item['title'] = response.css(".product_main h1::text").get(),
        book_item['upc'] = table_rows[0].css("td::text").get(),
        book_item['product_type'] = table_rows[1].css("td::text").get(),
        book_item['price_excl_tax'] = table_rows[2].css("td::text").get(),
        book_item['price_incl_tax'] = table_rows[3].css("td::text").get(),
        book_item['tax'] = table_rows[4].css("td::text").get(),
        book_item['availability'] = table_rows[5].css("td::text").get(),
        book_item['num_reviews'] = table_rows[6].css("td::text").get(),
        book_item['stars' ] = response.css("p.star-rating").attrib["class"],
        book_item['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
        book_item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
        book_item['price'] = response.css("p.price_color::text").get(),
        yield book_item