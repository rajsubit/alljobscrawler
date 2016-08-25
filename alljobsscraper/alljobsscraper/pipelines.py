import os
import xlwt
import sys
import locale
import codecs
import pymysql
import pandas as pd
from twisted.enterprise import adbapi

from alljobsscraper import settings


pymysql.install_as_MySQLdb()


class AlljobsscraperPipeline(object):

    def __init__(self):
        """ Initial the excel file with headings as the first row. """

        sys.stdout = codecs.getwriter(
            locale.getpreferredencoding())(sys.stdout)
        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.book = xlwt.Workbook(encoding='utf-8')
        self.sheet = self.book.add_sheet('AllJobs')
        self.sheet.write(0, 0, 'Site')
        self.sheet.write(0, 1, 'Company')
        self.sheet.write(0, 2, 'Company_jobs')
        self.sheet.write(0, 3, 'Job_id')
        self.sheet.write(0, 4, 'Job_title')
        self.sheet.write(0, 5, 'Job_Description')
        self.sheet.write(0, 6, 'Job_Post_Date')
        self.sheet.write(0, 7, 'Job_URL')
        self.sheet.write(0, 8, 'Country_Areas')
        self.sheet.write(0, 9, 'Job_categories')
        self.sheet.write(0, 10, 'AllJobs_Job_class')

        self.last_row = self.sheet.last_used_row

    def close_spider(self, spider):
        """
        Read the unsorted excel file
        Sort rows by company and create new excel file with sorted rows
        Remove the unsorted excel file
        """

        unsorted_xls_df = pd.read_excel('unsorted_allJobsList.xls')
        sorted_xls = unsorted_xls_df.sort_values(by='Company')
        sorted_xls.to_excel(
            'AllJobsJobsList.xls', sheet_name='AllJobs', index=False)
        os.remove('unsorted_allJobsList.xls')

    def process_item(self, item, spider):
        """ Add each scraped contents in respective columns. """

        self.last_row += 1
        self.sheet.write(self.last_row, 0, item['alljobs']['Site'])
        self.sheet.write(self.last_row, 1, item['alljobs']['Company'])
        self.sheet.write(self.last_row, 2, item['alljobs']['Company_jobs'])
        self.sheet.write(self.last_row, 3, item['alljobs']['Job_id'])
        self.sheet.write(self.last_row, 4, item['alljobs']['Job_title'])
        self.sheet.write(self.last_row, 5, item['alljobs']['Job_Description'])
        self.sheet.write(self.last_row, 6, item['alljobs']['Job_Post_Date'])
        self.sheet.write(self.last_row, 7, item['alljobs']['Job_URL'])
        self.sheet.write(self.last_row, 8, item['alljobs']['Country_Areas'])
        self.sheet.write(self.last_row, 9, item['alljobs']['Job_categories'])
        self.sheet.write(
            self.last_row, 10, item['alljobs']['AllJobs_Job_class'])

        self.book.save('unsorted_allJobsList.xls')

        return item


class MySQLPipeline(object):

    def __init__(self, dbpool):
        """ Initiate Mysql database """

        self.dbpool = dbpool

    @classmethod
    def from_settings(cls):
        """ Connect to local mysql database """

        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        """ Process the items to insert into database """

        dbpool = self.dbpool.runInteraction(self.insert, item, spider)
        dbpool.addErrback(self.handle_error, item, spider)
        dbpool.addBoth(lambda _: item)
        return dbpool

    def insert(self, conn, item, spider):
        """ Insert items into database """

        conn.execute("""
                INSERT INTO alljobs (
                Site,
                Company,
                Company_jobs,
                Job_id,
                Job_title,
                Job_Description,
                Job_Post_Date,
                Job_URL,
                Country_Areas,
                Job_categories,
                AllJobs_Job_class
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
            """, (
            item['alljobs']['Site'],
            item['alljobs']['Company'],
            item['alljobs']['Company_jobs'],
            item['alljobs']['Job_id'],
            item['alljobs']['Job_title'],
            item['alljobs']['Job_Description'],
            item['alljobs']['Job_Post_Date'],
            item['alljobs']['Job_URL'],
            item['alljobs']['Country_Areas'],
            item['alljobs']['Job_categories'],
            item['alljobs']['AllJobs_Job_class']

        ))
        spider.log(
            "Item stored in dbSchema: %s %r" %
            (item['alljobs']['Job_id'], item))

    def handle_error(self, failure, item, spider):
        """Handle occurred on dbSchema interaction."""

        self.logger.info("DB Schema Handled")
