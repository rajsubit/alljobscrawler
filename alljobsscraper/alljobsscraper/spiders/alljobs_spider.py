import scrapy


class AllJobsSpider(scrapy.Spider):
    """ Spider to scrape job information from site http://www.alljobs.co.il """

    name = "alljobs_spider"
    start_urls = ["http://www.alljobs.co.il/SearchResultsGuest.aspx", ]

    def parse(self, response):
        """ Function to parse the page and extract the required data points."""
        for each_job in response.xpath("//div[@class='open-board']"):
            job_title = 
