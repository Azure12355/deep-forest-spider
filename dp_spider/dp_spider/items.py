# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DpSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class PestchinaScraperItem(scrapy.Item):
    rowid = scrapy.Field()
    TP_GUID = scrapy.Field()
    SSNameSci = scrapy.Field()
    SSName = scrapy.Field()
    NamedYear = scrapy.Field()
    SCName = scrapy.Field()
    SEName = scrapy.Field()
    SENameAbb = scrapy.Field()
    SClass = scrapy.Field()
    ParentSsName = scrapy.Field()
    SLevel = scrapy.Field()
    SLevel2 = scrapy.Field()
    Source = scrapy.Field()
    Status = scrapy.Field()
    Checker = scrapy.Field()
    CheckTime = scrapy.Field()
    OrgRiskCode = scrapy.Field()
    IsSpecies = scrapy.Field()
    TP_AUTHOR = scrapy.Field()
    TP_CREATED = scrapy.Field()
    TP_EDITOR = scrapy.Field()
    TP_MODIFIED = scrapy.Field()
    Temp_CREATED = scrapy.Field()
    CHECKER_ID = scrapy.Field()
    CHECKER_NAME = scrapy.Field()
    ScType = scrapy.Field()
