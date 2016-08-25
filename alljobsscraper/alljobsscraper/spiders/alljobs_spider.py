import re
import sys
import codecs
import scrapy
import locale

from alljobsscraper.items import AlljobsscraperItem


class AllJobsSpider(scrapy.Spider):
    """ Spider to scrape job information from site http://www.alljobs.co.il """

    name = "alljobs_spider"
    allowed_domains = ["http://www.alljobs.co.il"]
    start_urls = [
        "http://www.alljobs.co.il/SearchResultsGuest.aspx?" +
        "page=1&position=&type=&freetxt=&city=&region=", ]

    def __init__(self):

        sys.stdout = codecs.getwriter(
            locale.getpreferredencoding())(sys.stdout)
        reload(sys)
        sys.setdefaultencoding('utf-8')

    def parse(self, response):
        """ Parse Each location Link and Extract Each job in this location"""

        container_id_list = response.xpath(
            "//div[@class='open-board']/@id").extract()

        id_list = [re.findall(r'[\d]+', x.strip()) for x in container_id_list]

        id_list = [x[0] for x in id_list if x]

        if id_list:
            for job_id in id_list:
                job_link = \
                    "http://www.alljobs.co.il/Search/UploadSingle.aspx?JobID={}".format(job_id)
                yield scrapy.Request(
                    job_link, self.parse_each_job,
                    dont_filter=True,
                    meta={'job_id': job_id})

        pagi_link_list = response.xpath(
            "//div[@class='T13 MT5']//div[@class='jobs-paging-nactive']")

        for pagi_link in pagi_link_list:
            nextpagi_text = pagi_link.xpath("./a/text()").extract_first()
            if nextpagi_text == u'\u05d4\u05d1\u05d0 \xbb':
                yield scrapy.Request(
                    response.urljoin(
                        pagi_link.xpath("./a/@href").extract_first()),
                    self.parse, dont_filter=True)

    def parse_each_job(self, response):
        """ Parse Each job and extract the data points"""

        # job_id = response.meta['job_id']
        job_item_sel = response.xpath("//div[@class='open-board']")

        try:
            job_date = job_item_sel.xpath(
                './/div[@class="job-content-top-date"]/text()').extract_first()
            date = job_date.split(' ')[-1]
        except:
            date = ""

        try:
            job_class = job_item_sel.xpath(
                './/div[@class="job-content-top-status-text"]/text()'
            ).extract_first()
        except:
            job_class = ""

        try:

            job_title = job_item_sel.xpath(
                './/div[contains(@class, "job-content-top-title")]//div/a/h2/text()').extract_first()
        except:
            job_title = ""

        try:
            company = job_item_sel.xpath(
                './/div[@class="T14"]/a/text()').extract_first()
        except:
            company = ""

        try:
            company_jobs = job_item_sel.xpath(
                './/div[@class="job-company-details"]//a[@class="L_Blue gad"]/@href').extract_first()
            company_jobs = response.urljoin(company_jobs)
        except:
            company_jobs = ""

        try:
            country_areas = job_item_sel.xpath(
                './/div[@class="job-content-top-location"]/a/text()'
            ).extract_first()
        except:
            country_areas = ""

        job_description = ""
        try:
            description_div_id = "job-body-content" + \
                str(response.meta['job_id'])
            description_div = job_item_sel.xpath(
                './/div[@id="' + description_div_id + '"]/*')
            for dv in description_div:
                description_text = dv.xpath(
                    "normalize-space(string())").extract_first()
                if description_text:
                    job_description += description_text
                    job_description += "\n"

        except:
            job_description = ""

        item = AlljobsscraperItem()

        item['alljobs'] = {
            'Site': 'AllJobs',
            'Company': company,
            'Company_jobs': company_jobs,
            'Job_id': response.meta['job_id'],
            'Job_title': job_title,
            'Job_Description': job_description,
            'Job_Post_Date': date,
            'Job_URL': response.url,
            'Country_Areas': country_areas,
            'Job_categories': '',
            'AllJobs_Job_class': job_class,
        }

        yield item
