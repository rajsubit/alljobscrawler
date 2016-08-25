# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AlljobsscraperItem(scrapy.Item):
    """ Data fields to scrape and store from http://www.alljobs.co.il/ """

    site = scrapy.Field()
    company = scrapy.Field()
    company_jobs = scrapy.Field()
    job_id = scrapy.Field()
    job_title = scrapy.Field()
    job_description = scrapy.Field()
    job_post_date = scrapy.Field()
    job_url = scrapy.Field()
    country_areas = scrapy.Field()
    job_categories = scrapy.Field()
    alljobs_job_class = scrapy.Field()
